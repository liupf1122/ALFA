# Baseline

目的：联合优化个体 latent 与 age、sex 两条件 SIREN，建立独立人群的拟合后重建与 i2-only 纵向基线。
`config.yaml` 合并到默认配置后运行：

```bash
bash scripts/train.sh --config experiments/baseline/config.yaml
```

默认验证最多 8 位独立验证受试者；正式启动前确定此预算是否足够。
未在本次任务中启动真实数据训练。结果需与原始 i2 persistence 和无条件消融比较。
