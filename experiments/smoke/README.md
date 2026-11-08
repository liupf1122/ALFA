# 工程 smoke

```bash
python scripts/run.py smoke
```

生成 12 人、每人 2 次扫描的 8×9×10 合成 NIfTI，使用缩小网络、CPU 和少量步数。
检查完整训练/验证、检查点恢复一致性、重建/纵向评估、固定 latent 年龄修改、导出几何及无条件消融。
每次数据和运行全部放入新的 `outputs/smoke_suite_*`，不接触真实 MRI。
`config.yaml` 是 smoke 工具的参数模板，由工具覆盖合成数据路径；不要直接把它用于真实队列训练。
