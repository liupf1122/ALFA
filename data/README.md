# 当前数据

`recommended_core4_i2_i3.csv` 从用户指定的
`/mnt/sda/liupeifu/WorkSpace/Codes/datas/recommended_core4_i2_with_i3_T1_rigid.csv`
提取，精确保留 `IID,instance,mri_path,age,sex` 五列，顺序和扫描行均不变。
共 1143 人、2286 扫描，每人 instance=2、3 各一条。33 个 age 缺失值原样保留，没有跨访视填充。
`IID` 是个人标识，`instance` 是扫描访视，二者不作为数值条件；网络条件顺序为 `[age,sex]`。

旧 data/ 内容已删除，删除清单和上游来源指纹记录在 `docs/data_change_20261105.json`。
新数据不沿用 bridge QC 或旧 train/val/test 成员。固定划分在 `splits/`，按 IID 保证同人不跨集合；
采用全体受试者 train 80%、val 10%、test 10%，seed=42。先对排序后的 IID 随机打乱，验证和测试人数取 round(N×0.1)，训练接收余数：
训练 915 人/1830 扫描、验证 114 人/228 扫描、测试 114 人/228 扫描。
旧划分保存在 `splits_history/20261105_155721/`；记录见 `../docs/split_change_801010.json`。源 CSV、影像及缓存未修改。

## 缓存位置与行为

原始 MRI：

```text
/mnt/sda/public/00_Datasets/public/MRI/UKbiobank/UKB_84436/T1_rigid/{IID}/instance_{instance}/T1/reg_T1_rigid_MNI.nii.gz
```

缓存就在同一目录，按完整影像路径追加后缀：

- `<mri_path>.alfa-p999.npy`：float32 三维强度，轴序 x,y,z。
- `<mri_path>.alfa-p999.json`：来源大小、mtime、归一化 scale 和空间信息。
- `<mri_path>.alfa-p999-foreground.npy`：在 x,y,z 数组展平后的前景索引；当前训练仍均匀采样。

实际核查 2286 组缓存均存在，来源元数据与影像一致，shape 均为 `[193,229,193]`。
缓存加载先核对源文件大小、mtime、路径、归一化规则、shape、dtype、有限值及数值范围。
元数据中的旧 cache_path/foreground_path 可能指向已迁移的目录，代码只按当前 MRI 路径找缓存。
首次读取无有效缓存时，自动在 MRI 所在目录加锁并生成缓存和元数据；有效缓存直接复用且不改写。
不在 prepare 阶段批量创建缓存；原始 MRI 从不写入。

归一化为 `clip(raw / percentile(raw[raw>0],99.9),0,1)`，不能再除以 1500。
加载时由磁盘 x,y,z 转成模型 z,y,x。PSNR/SSIM 固定 data_range=1.0；前景阈值为归一化强度 >0.05。
导出乘参考扫描的 scale，保留 affine、qform/sform 及单位；裁剪损失的信息不能恢复。

条件归一化 min/max 仅从训练集计算；缺失 age 在模型条件中映射为 0，源表仍保持 NaN。
纵向评估需要真实 i2/i3 age，因此跳过并记录年龄缺失配对，不能把这种中点编码解释为观测年龄。
