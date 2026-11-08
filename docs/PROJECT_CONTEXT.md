# 当前项目上下文

更新：2026-11-05。目标是把原为空目录的 ALFA2/v1 建成符合 `Notes/AI辅助代码.md` 的可运行项目。
用户指定使用 conda `aging`；AGENTS.md 同时约定优先使用 MRI 同目录缓存，缺失时首次读取创建。

已实现独立 YAML 配置、MRI 只读、缓存优先加载和缺失缓存创建、按人固定划分、个体 latent 条件 SIREN、
L1 训练、独立验证选优、完整检查点恢复、重建评估、i2-only 纵向评估及固定 latent 条件推理。
合成数据 CPU 全流程和默认模型接口已验证。用户启动真实训练后遇到 AMP 梯度溢出，现已修复；默认规模真实 MRI GPU 探针完成 5 次更新，尚未重启正式长训练。

模型骨干来源为旁边 `ALFA/ALFAv1`。当前只用 age、sex 两条件。
原 data/ 内容已按用户要求清空，换为 recommended_core4 配对表及重新生成的划分，不沿用 bridge QC 或名单。
新表保留 1143 人的 2286 次扫描及 33 个缺失年龄；缓存均位于 MRI 所在目录。
旧输出保持原状，仅作为历史证据，不能代表当前队列。

下一步：先审阅 [研究规范](RESEARCH_SPEC.md) 和 [实验计划](EXPERIMENT_PLAN.md)，
确定正式训练预算、验证受试者范围和 GPU 后启动 README 中的训练命令。
本次未自动启动正式训练。

关键入口：[架构](ARCHITECTURE.md)、[接口](INTERFACE_CONTRACTS.md)、
[实验台账](EXPERIMENT_TRACKER.md)、[结果解释](RESULTS_ANALYSIS.md)、[验证](VERIFICATION.md)。

当前归一化入口已统一为逐扫描 p99.9，旧固定尺度兼容分支已移除。最新清理和 30 项测试结果见 VERIFICATION.md。

直接运行 `bash scripts/train.sh` 即可使用 aging、自动核查/准备数据并按空闲显存选择一张可见 GPU；`--check-only` 可先检查且不启动训练。

AMP 溢出现在安全跳过更新并降低缩放系数；持续异常明确报错，日志记录跳过次数。验证证据见 docs/amp_verification.json 和 VERIFICATION.md。

当前新训练采用按人 80/10/10 划分：train 915、val 114、test 114 人，seed=42；源数据保持不变，旧划分归档至 data/splits_history/20261105_155721。旧检查点恢复仍用原划分。
