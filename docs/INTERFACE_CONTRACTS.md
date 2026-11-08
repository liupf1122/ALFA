# 接口约定

| 接口 | 输入 | 输出/约定 |
|---|---|---|
| 清单 | CSV：id、eid、image_path、配置中的条件列 | 每行一次扫描，绝对影像路径；同 eid 为同一人 |
| MRIDataset | 清单、完整配置、训练 normalizer | t1 `[D,H,W]`、conditions `[C]`、local_id、id、eid |
| LatentManager | local_id `[B]` | `[B,L,Dz,Hy,Wx]`；同人跨扫描共用 |
| sample_voxels | `[B,D,H,W]`、采样点数 N | 坐标 `[B,N,3]`、真值 `[B,N,1]` |
| ConditionalSIREN | coords `[B,N,3]`、latent `[B,L,Dz,Hy,Wx]`、conditions `[B,N,C]` | 强度 `[B,N,1]` |
| fit_latent | 冻结网络、单卷真值及条件 | 新 latent `[1,L,Dz,Hy,Wx]`；只更新此 latent |
| predict_volume | 网络、latent、shape、条件、chunk size | float32 数组 `[D,H,W]`，归一化强度 |
| export_volume | 预测数组、参考 NIfTI | 乘以参考扫描 p99.9 scale 的 NIfTI，保留物理几何 |

磁盘 p99.9 缓存数组为 x,y,z，加载时先转为 z,y,x；不得重复归一化。
坐标内部为 z,y,x，范围 [-1,1]；grid_sample 前翻转为 x,y,z，align_corners=True。
原始源 CSV 精确保留 IID、instance、mri_path、age、sex 五列；prepare 转换为上述内部清单，不向源表添加内部字段。
默认 L=128、C=2；无条件消融 C=0，其余接口保持成立。
条件归一化只在训练集 fit，统计量随 checkpoint 保存；中点填充缺失值，不裁剪超范围条件。

检查点格式版本为 1。包含 model、latent、latent_keys、optimizer、scheduler、scaler、rng、
config、normalizer、split_sha256、epoch、best_epoch、best_validation_mae 和早停状态。
只加载可信检查点。旧版没有这些自描述信息，入口会拒绝直接加载。
当前检查点必须声明 `data.normalization=p999` 和 `data.cache_mode=adjacent`。
固定尺度或缺少归一化声明的旧检查点不再支持；`norm_shift`、`norm_scale` 已从配置入口移除。

恢复训练核对划分哈希及 latent 顺序；需要同目录匹配的 best.pt 以保留历史最佳状态。
只保存完整 epoch；epoch 中途终止会标记 interrupted 并保留之前的完整检查点。
评估输出不会写入输入 checkpoint，单独建立运行目录记录检查点哈希及预算。

指标 data_range 默认固定 1.0（归一化单位），用于 PSNR 和 SSIM，不逐卷重新估计范围；
前景为真值 >0.05。预测不裁剪。MSE 为 0 时 PSNR 写 null 表示理论无限，空前景 MAE 写 null。

训练入口默认自动准备缺失的完整划分；部分划分缺失和恢复时划分缺失均报错，不重新分配受试者。
自动选卡尊重 CUDA_VISIBLE_DEVICES，按空闲显存选一张可见 GPU；恢复时也重新选择。无 GPU 的自动训练报错，CPU 必须显式选择。
`train --check-only` 完成数据检查及设备选择后返回，不构建模型、不创建运行目录、不训练。

混合精度梯度非有限时，不做裁剪或 Adam 更新，由 GradScaler 自动降低 loss scale；正常梯度仍严格检查裁剪范数。
非有限前向 loss、全精度非有限梯度、连续 16 次 AMP 溢出或整个 epoch 没有成功更新均报错。
`logs/amp_overflows.jsonl` 记录每次溢出的 epoch/batch、缩放系数和连续次数。
`logs/metrics.jsonl` 新增 optimizer_steps、amp_skipped_steps、loss_scale；train_mae 仅统计成功更新批次。
检查点新增 consecutive_amp_overflows，旧格式版本 1 检查点缺少该字段时按 0 恢复。

新划分配置 data.train_ratio/val_ratio/test_ratio 均相对于全体受试者，要求正数且和为 1；默认 0.8/0.1/0.1。以 seed 打乱排序后的唯一 IID，val/test 人数取 round(N×ratio)，train 接收余数；同人全部扫描归属一致。已有划分不自动覆盖。旧检查点的历史比例配置仅用于保留和恢复原有快照，不用于新建划分。
