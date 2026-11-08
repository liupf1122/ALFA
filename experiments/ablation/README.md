# 无条件消融

`no_conditions.yaml` 将条件输入设为空，保留坐标、个体 latent、数据划分和其他训练参数。
条件消融会减少首层参数数目；报告时应明确这一差异。

```bash
bash scripts/train.sh --config experiments/ablation/no_conditions.yaml
```

CPU 合成流程已验证无条件配置可训练和重建评估。该配置不支持 age 条件编辑或年龄修改的纵向模式；
不能把无条件重建与条件模型的 i3 预测混为同一个任务。
