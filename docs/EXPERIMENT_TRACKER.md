# 当前数据版本实验台账

| 工作 | 状态 | 证据/产物 |
|---|---|---|
| core4 五列 CSV | 已建立 | `data/recommended_core4_i2_i3.csv`，1143 人/2286 行 |
| 按人 80/10/10 划分 | 915/114/114 人；同人不跨集合，全扫描保留；既有全队列几何检查未重跑 | `data/splits/manifest.json`、`docs/split_change_801010.json` |
| MRI 同目录缓存普查 | 2286 组可用 | `docs/cache_audit_20261105.json` |
| 缓存/接口单元测试 | 30 项通过 | `tests/test_cache.py`、`tests/test_contracts.py`、`tests/test_training_entry.py`、`tests/test_amp.py` |
| 新 CSV 与缓存的完整合成流程 | 通过 | `outputs/smoke_suite_seed42_20261105_155732_303036/verification.json` |
| age、sex baseline 真实训练 | 用户启动后因 AMP 溢出失败，原记录保留；已修复入口，尚未重新正式训练 | `outputs/baseline_seed42_20261105_154317_995602/run_info.json` |
| GPU AMP 有界验证 | 6 批中 1 次溢出安全跳过，5 次成功更新 | `docs/amp_verification.json` |
| 无条件真实 MRI 消融 | 未启动 | `experiments/ablation/no_conditions.yaml` |

旧 bridge 划分已删除，旧 outputs 保留为历史产物，不能用于描述当前 core4 数据效果。
新运行以 `run_info.json` 为依据，best.pt 按验证 MAE 选择，last.pt 为最近完整 epoch。
