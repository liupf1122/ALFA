本项目使用 conda 下的 `aging` 环境。

图像数据优先使用缓存。缓存目录为每条 `mri_path` 对应影像的所在目录，即 `/mnt/sda/public/00_Datasets/public/MRI/UKbiobank/UKB_84436/T1_rigid/{IID}/instance_{instance}/T1/`；缓存文件为 `<mri_path>.alfa-p999.npy`、`<mri_path>.alfa-p999.json` 和 `<mri_path>.alfa-p999-foreground.npy`。缓存缺失时，在首次运行代码读取该影像时创建；失效缓存校验后重建，使用文件锁和原子写入，原始 MRI 保持只读。现有缓存采用 `clip(raw / percentile(raw[raw>0],99.9),0,1)`，数组轴序为 x,y,z，读取后转为模型使用的 z,y,x；不得再次除以 1500，也不得使用元数据中已失效的旧缓存路径。
