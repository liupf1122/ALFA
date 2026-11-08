# 系统与模型架构

`scripts/run.py` 解析命令，`src/config.py` 合并默认配置与实验差异。
`prepare.py` 建立/核查划分；`dataset.py` 读取影像和表型；`sampler.py` 在体素索引中均匀采样。
`train.py` 编排优化及保存；`evaluator.py` 组织验证与测试；`inference.py` 加载、拟合 latent、重建和导出。
`volume_cache.py` 负责 p99.9 缓存的校验、锁和原子写入。通用运行 provenance 在 `src/utils/runtime.py`。

默认每人 latent 为 `[128,3,3,3]`。从归一化坐标 z,y,x 对 latent 网格三线性插值，
获得 128 维局部 latent。与 3 维坐标及 2 维条件（age、sex）拼接，首层输入 133 维。
SIREN backbone 为 5 个 256 宽 sine 层，输出头为 6 个 256 宽 sine 层加 1 维线性输出。
backbone 首层/隐藏 omega 均 15，head omega 45；可选残差分支默认关闭。
坐标对应的首层权重仍采用旧版单独的 U(-1/3,1/3) 初始化。
默认共享网络参数共 692481 个，个体 latent 参数另按人数计算。

默认训练网络 lr=1e-4、latent lr=1e-3、batch=8、每扫描 51200 个采样点、上限 1000 epoch。
StepLR 每 20 epoch 乘 0.5；梯度裁剪 1；AMP 仅在 CUDA 启用。
以验证拟合后的全卷 MAE 最小值保存 best.pt，耐心 80 次验证、有效改善阈值 1e-4。
best 的严格最小值选择与耐心阈值分别处理。

推理坐标按 chunk 构造，避免在 GPU 上一次分配完整坐标网格。
验证使用独立固定随机序列并恢复训练随机状态；不改变训练的采样序列。
checkpoint 内持有归一化、模型配置与个人映射，无需依赖旧代码 import 或当时的全局常量。

与旧版差异：配置驱动、独立验证选优、完整 RNG/scaler/早停恢复、统一运行记录、MRI 邻接 p99.9 缓存优先读取与缺失时创建。
没有迁移旧版 PCA 视频和历史专用分析脚本，也未添加未经实现的模块占位符。
