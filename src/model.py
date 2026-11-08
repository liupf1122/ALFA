"""Conditional SIREN adapted from ALFA/ALFAv1/s3_model.py; see docs/ARCHITECTURE.md."""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F



class LatentManager(nn.Module):
    """存放"每个受试者一个 latent 张量"的容器，本质是一张可学习的查找表。

    latent_vector 的 shape 是 [num_subjects, C, D, H, W]，一个人一份（多次随访共享）；
    训练时用人的 local_id 去索引，取出的那一份连同网络一起参与反向传播——这就是所谓
    auto-decoder / GLO：latent 不是编码器算出来的，是"梯度回传直接优化出来的"。
    """

    def __init__(self, num_subjects: int, latent_shape=(128, *(3, 3, 3))):
        super().__init__()
        self.latent_shape = latent_shape
        self.latent_vector = nn.Parameter(torch.empty(num_subjects, *latent_shape))
        nn.init.normal_(self.latent_vector, mean=0.0, std=0.01)

    def forward(self, local_ids: torch.Tensor) -> torch.Tensor:
        """local_ids: [B, 1] 或 [B] 的整数下标 -> [B, C, D, H, W] 对应的 latent 网格。"""
        return self.latent_vector[local_ids.reshape(-1)]


class SineLayer(nn.Module):
    """SIREN 的基本构件：Linear 层 + sin 激活，配套论文里的特殊初始化。

    普通 ReLU/Sigmoid 网络很难学出高频细节（脑组织边界这种锐利结构），
    SIREN（arXiv 2006.09661）用 sin(omega_0 * Wx + b) 作为激活函数，
    配合下面这种按 1/in_features 缩放的初始化，能让每一层的输出方差保持稳定，
    从而支持更深的网络学习高频信号。omega_0 越大，这一层能表达的"频率"越高。
    """

    def __init__(self, in_features: int, out_features: int, is_first: bool = False, omega_0: float = 30.0):
        super().__init__()
        self.omega_0 = omega_0
        self.is_first = is_first
        self.in_features = in_features
        self.linear = nn.Linear(in_features, out_features)
        self._init_weights()

    def _init_weights(self):
        with torch.no_grad():
            if self.is_first:
                bound = 1.0 / self.in_features
            else:
                bound = np.sqrt(6.0 / self.in_features) / self.omega_0
            self.linear.weight.uniform_(-bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sin(self.omega_0 * self.linear(x))


def _make_sine_stack(in_features: int, hidden_features: int, num_hidden_layers: int, omega_0: float) -> nn.ModuleList:
    """搭一串"第一层 is_first=True + 若干隐藏层"的 SineLayer，供 backbone / head / residual 复用。"""
    layers = nn.ModuleList([SineLayer(in_features, hidden_features, is_first=True, omega_0=omega_0)])
    for _ in range(num_hidden_layers - 1):
        layers.append(SineLayer(hidden_features, hidden_features, is_first=False, omega_0=omega_0))
    return layers


def _linear_output_layer(hidden_features: int, out_features: int, omega_0: float) -> nn.Linear:
    """SIREN 最后一层通常用普通线性层（不再过 sin），初始化范围仍按 omega_0 缩放以衔接前面层的量级。"""
    layer = nn.Linear(hidden_features, out_features)
    bound = np.sqrt(6.0 / hidden_features) / omega_0
    with torch.no_grad():
        layer.weight.uniform_(-bound, bound)
    return layer


class ConditionalSIREN(nn.Module):
    """共享解码器：(坐标, 条件, 局部 latent) -> 单通道 T1 强度预测值。

    结构 = SIREN 主干（把 [坐标+条件+latent] 映射到隐藏特征） + SIREN 输出头
    （把隐藏特征映射到 1 维强度值），中间可选一个低频残差分支。之所以主干和
    输出头分开两段 SineLayer 堆叠，是延续原项目"主干可以给多个输出头共享"的
    设计——本项目虽然只用一个头，但保留这个两段式结构，方便以后如果要加分割
    等第二个输出头时，只需再接一个头，不用改主干。
    """

    def __init__(
        self,
        condition_size: int = 2,
        latent_channels: int = 128,
        backbone_hidden_features: int = 256,
        backbone_hidden_layers: int = 5,
        backbone_first_omega: float = 15.0,
        backbone_hidden_omega: float = 15.0,
        head_hidden_features: int = 256,
        head_num_layers: int = 6,
        head_omega: float = 45.0,
        head_out_size: int = 1,
        residual_enabled: bool = False,
        residual_layers: int = 3,
        residual_omega: float = 50.0,
    ):
        super().__init__()
        self.condition_size = condition_size
        self.latent_channels = latent_channels
        self.residual_enabled = residual_enabled

        coord_size = 3  # (z, y, x)
        total_in_features = coord_size + condition_size + latent_channels

        self.backbone = _make_sine_stack(
            total_in_features, backbone_hidden_features, backbone_hidden_layers, backbone_hidden_omega
        )
        self.backbone[0] = SineLayer(total_in_features, backbone_hidden_features, is_first=True, omega_0=backbone_first_omega)

        if residual_enabled:
            self.residual_net = _make_sine_stack(
                total_in_features, backbone_hidden_features, residual_layers, residual_omega
            )
        else:
            self.residual_net = None

        first_layers = [self.backbone[0]] + ([self.residual_net[0]] if residual_enabled else [])
        with torch.no_grad():
            for layer in first_layers:
                layer.linear.weight[:, :coord_size].uniform_(-1.0 / coord_size, 1.0 / coord_size)

        self.head_layers = _make_sine_stack(
            backbone_hidden_features, head_hidden_features, head_num_layers, head_omega
        )
        self.head_out = _linear_output_layer(head_hidden_features, head_out_size, head_omega)

    @staticmethod
    def sample_latent_at_coords(coords: torch.Tensor, latent_grid: torch.Tensor) -> torch.Tensor:
        """用三线性插值，从体素化的 latent 网格里取出每个坐标点对应的局部 latent 向量。

        Args:
            coords: [B, N, 3]，坐标顺序 (z, y, x)，取值范围 [-1, 1]
            latent_grid: [B, C, D, H, W]

        Returns:
            [B, N, C]
        """
        grid = coords[..., [2, 1, 0]].view(coords.shape[0], -1, 1, 1, 3)
        sampled = F.grid_sample(latent_grid, grid, mode="bilinear", padding_mode="border", align_corners=True)
        sampled = sampled.squeeze(-1).squeeze(-1)  # [B, C, N]
        return sampled.permute(0, 2, 1)  # [B, N, C]

    def forward(self, coords: torch.Tensor, latent_grid: torch.Tensor, conditions: torch.Tensor) -> torch.Tensor:
        """
        Args:
            coords: [B, N, 3] 归一化坐标
            latent_grid: [B, C, D, H, W] 该 batch 每个人的个体 latent 网格
            conditions: [B, N, condition_size] 条件向量（同一个人所有采样点相同）

        Returns:
            [B, N, head_out_size] 预测的 T1 强度值
        """
        local_latent = self.sample_latent_at_coords(coords, latent_grid)  # [B, N, C]
        x = torch.cat([coords, conditions, local_latent], dim=-1)

        features = x
        for layer in self.backbone:
            features = layer(features)

        if self.residual_enabled:
            residual = x
            for layer in self.residual_net:
                residual = layer(residual)
            features = features + residual

        for layer in self.head_layers:
            features = layer(features)
        return self.head_out(features)


def build_model(cfg):
    options = dict(cfg["model"])
    options.pop("latent_spatial")
    return ConditionalSIREN(condition_size=len(cfg["data"]["conditions"]), **options)
