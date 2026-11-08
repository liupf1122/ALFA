# ALFA2 v1

可独立运行的条件 MRI auto-decoder 项目。沿用 `ALFA/ALFAv1` 的条件 SIREN、
三维个体 latent 网格和 L1 目标，按 `Notes/AI辅助代码.md` 组织代码、文档及运行记录。
每个人一个 latent，多次扫描共享；输入坐标、表型条件和个体 latent，输出 T1 强度。

本目录原先为空。初建时复用旧版模型实现；当前数据已切换为 UKB84436 core4 i2/i3 配对表，只使用 age、sex 条件。
原目录保持不变，未搬入旧权重、历史日志和图像。旧版检查点不能直接用于新入口。

## 环境

```bash
conda activate aging
cd /mnt/sda/liupeifu/WorkSpace/Codes/ALFA/ALFA2/v1
```

现有 `aging` 已包含所需依赖；无需重新安装 PyTorch。`requirements.txt` 给出兼容范围。
实际验证环境版本及证据见 [运行验证](docs/VERIFICATION.md)。

## 运行

一键训练（可以在任意目录执行，无须先激活 aging）：

```bash
bash /mnt/sda/liupeifu/WorkSpace/Codes/ALFA/ALFA2/v1/scripts/train.sh
```

脚本自动使用 conda aging，核查已有固定划分；缺少全部划分时生成一次，部分缺失时报错。
默认在 PyTorch 可见的 GPU 中选择当前空闲显存最多的一张，打印设备、显存情况和运行目录。
已设置 `CUDA_VISIBLE_DEVICES` 时仅在该集合内选择，不修改可见范围；这是单 GPU 训练。
自动模式下没有可用 GPU 会报错，明确需要 CPU 时传 `--device cpu`。
选卡依据是启动时的显存快照，不预留 GPU，也不依据计算利用率排名。

只检查准备状态和自动选卡，不训练：

```bash
bash /mnt/sda/liupeifu/WorkSpace/Codes/ALFA/ALFA2/v1/scripts/train.sh --check-only
```

`--check-only` 不创建训练运行目录或模型；若尚无划分，会先生成固定划分。
下列其他命令在项目根目录、aging 环境中执行：

```bash
# 检查固定划分、文件可用性及空间几何；不训练
python scripts/run.py prepare --headers

# 小型 CPU 合成数据全流程检查，数秒级，不使用真实 MRI 训练
python scripts/run.py smoke

# 正式训练；自动准备并选 GPU，每次建立独立运行目录
bash scripts/train.sh --config experiments/baseline/config.yaml

# 可指定可见 GPU；cuda:0 指可见集合中的第一张
CUDA_VISIBLE_DEVICES=0 bash scripts/train.sh --device cuda:0

# 从最近完整 epoch 恢复；重新自动选卡，epochs 是总 epoch 上限
bash scripts/train.sh --resume outputs/<运行名>/checkpoints/last.pt --epochs 1000

# 测试重建：冻结网络，用被测影像优化新 latent，再与该影像比较
python scripts/run.py evaluate --checkpoint outputs/<运行名>/checkpoints/best.pt

# 纵向：只在 i2 拟合 z，固定 z 和非 age 条件，改为 i3 年龄；与真实 i3 比较
python scripts/run.py evaluate --checkpoint outputs/<运行名>/checkpoints/best.pt --mode longitudinal

# 先重建，再固定同一个 z 修改 age；scan-id 从 test.csv 的 id 列选取
python scripts/run.py infer --checkpoint outputs/<运行名>/checkpoints/best.pt \
  --scan-id <扫描ID> --set age=70

# 关闭条件输入的消融；同一套固定划分
bash scripts/train.sh --config experiments/ablation/no_conditions.yaml

python -m unittest discover -s tests -v
```

`evaluate` 支持 `--max-samples N`、`--fit-steps N`、`--device cpu`；
`infer` 支持多次 `--set 条件=数值`。评估与推理默认从检查点恢复模型配置、训练归一化参数和划分快照，
不依赖重新读取原训练表型表。`--manifest` 可指定同格式外部清单；评估拒绝训练受试者。

## 配置与数据

`configs/default.yaml` 是默认配置，`experiments/*/*.yaml` 仅写差异。
相对配置中的数据/输出路径均相对于项目根目录，命令行 `--config` 路径相对于当前工作目录。
未知配置键会报错。恢复训练使用检查点配置，只允许通过入口调整总 epoch 上限和设备。
恢复时默认重新自动选 GPU，可用 `--device` 指定；恢复使用原运行划分快照，不会自动重新划分数据。

当前数据为 1143 人 / 2286 扫描，每人 i2、i3 各一条；训练 915 人 / 1830 扫描，验证 114 人 / 228 扫描，测试 114 人 / 228 扫描。
按全部受试者划分 train 80%、val 10%、test 10%，seed=42；验证/测试人数四舍五入，训练接收余数，同人两次扫描不跨集合。新训练使用这套划分；恢复旧检查点仍使用其原划分快照。
默认每次验证使用验证表中前 8 名不同受试者的首个扫描，每个 latent 拟合 100 步，按完整体积 MAE 选优。
这是运行成本有限的开发配置；正式研究可在启动前将 `validation.max_samples` 设为 `null` 使用全部验证受试者。

MRI 保持只读。优先使用每条 mri_path 同目录的 `.alfa-p999.npy` 缓存；缺失或失效时首次读取自动创建/重建，配有文件锁和原子写入。
强度沿用缓存的 p99.9 归一化，范围 [0,1]，不再除以 1500。新源表保留 33 个缺失年龄；纵向评估跳过并记录年龄缺失的配对，不用 i2 年龄填补 i3。
当前代码仅支持逐扫描 p99.9 归一化，已移除固定尺度配置与旧缓存分支；加载旧固定尺度检查点会明确报错，不会按新尺度静默解释旧模型。
数据路径、归一化与划分细节见 [数据说明](data/README.md)。

## 目录与产物

| 目录/文件 | 职责 |
|---|---|
| `AGENTS.md` | 指定 conda `aging` 环境 |
| `docs/` | 科学目标、实现约定、实验计划、当前进展与证据 |
| `src/` | 数据、模型、损失、训练、评估、推理及运行工具 |
| `scripts/` | CLI 与训练启动脚本 |
| `data/splits/` | 固定 train/val/test 清单；含本地受限数据，不默认入 Git |
| `experiments/` | baseline、消融和 smoke 的人工配置 |
| `analysis/` | 可重复执行的指标汇总脚本 |
| `tests/` | 坐标、个体映射、数据隔离与模型接口检查 |
| `outputs/` | 每次独立运行的配置、日志、检查点、评估结果与推理影像 |

训练输出包含完整 `config.yaml`、`run_info.json`、`data/splits/` 快照、
`checkpoints/best.pt`、`checkpoints/last.pt`、`logs/metrics.jsonl` 和 `summary.json`。
检查点保存模型、latent、受试者映射、优化器、调度器、AMP scaler、随机状态、归一化与早停状态。
`best.pt` 按验证重建 MAE 选择；`last.pt` 是最近完成的 epoch。恢复会建立新运行目录并关联来源。
验证耐心计数按验证次数计算。中断发生在 epoch 内时，从上一个完整 epoch 恢复。

评估输出 `metrics.csv` 和 `summary.json`；推理输出 `latent.pt`、`reconstruction.nii.gz`，
修改条件时另有 `edited.nii.gz`。导出乘以参考扫描的 p99.9 scale 返回原始强度单位，保留参考影像的物理空间几何；预处理裁剪掉的信息不能逆向恢复。

本次验证证明流程可执行。真实队列尚未训练，不能据此判断重建质量、年龄效应、个体保持或纵向预测有效性。
从 [项目上下文](docs/PROJECT_CONTEXT.md) 查看下一步。

混合精度训练偶尔打印 `AMP overflow ... update skipped, scale=...` 表示该批梯度溢出，已安全跳过参数更新并自动降低缩放系数。
连续 16 次溢出、整轮无有效更新或前向 loss 非有限会停止并记录失败；每次溢出见运行目录 `logs/amp_overflows.jsonl`，每轮计数见 `logs/metrics.jsonl`。

训练时显示每轮批次进度、平均 MAE（成功更新批次）、AMP 跳过次数、速度和该轮预计剩余时间；验证阶段另显示已完成扫描数与累计 MAE。AMP 提示兼容进度条显示。已启动进程不会热加载代码，进度条从下一次启动生效。
