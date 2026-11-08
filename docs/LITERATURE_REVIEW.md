# 文献与实现来源

本次是代码组织与运行流程建设，没有开展文献检索，也没有核验新颖性。
当前实现依据是旁边旧项目的 `ALFA/ALFAv1/s3_model.py`，
当前输入已改为 age、sex，不能直接沿用旧参数量和输入维数；当前实现与验证以 ARCHITECTURE.md 和 verification.json 为准。

使用的技术概念为 auto-decoder、个体三维 latent 网格三线性插值、SIREN 周期激活、
条件拼接及冻结网络的测试 latent 优化。实现与 scientific claims 分开记录。

正式论文阶段需要另行核验：SIREN 和 auto-decoder 的原始文献；条件 MRI/年龄建模工作的数据划分、
测试 latent 拟合协议及纵向基线；本方法相对于已有工作的增量。
核验前不将旧注释中的论文表述或效果描述当作已验证文献结论。
