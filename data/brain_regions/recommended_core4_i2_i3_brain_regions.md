# UKB84436 双访视脑区指标：数据与列名说明

- 主表：`recommended_core4_i2_i3_brain_regions.csv`；UTF-8 BOM 编码，逗号分隔，空单元格表示缺失。
- 名单：`/mnt/sda/liupeifu/WorkSpace/Codes/datas/recommended_core4_i2_with_i3_T1_rigid.csv`；只按 `(IID, instance)` 匹配，严格保留名单行顺序。
- 分割根目录：`/mnt/sda/public/00_Datasets/public/MRI/UKbiobank/UKB_84436/T1_seg`；只读已有统计，没有重跑或修改影像。
- 提取开始：2026-11-08T19:45:08.690341+08:00；结束：2026-11-08T19:45:10.205459+08:00。
- 共 **1,143 人、2,286 行、120 列**；其中元数据 11 列，数值指标 109 列。
- 分割统计成功提取 2,286 次访视；两次访视都成功的受试者 1,143 人。
- 本表仅提取 `aseg+DKT.VINN.withCC.stats`；100 个区域体积加 9 个全脑汇总体积，共 109 个指标。提取异常 0 条。

## 1. 来源、命名与使用边界

1. 所有数值指标均来自每次访视的 `stats/aseg+DKT.VINN.withCC.stats`。`seg__*` 为区域体积，`seg_global__*` 为文件头中的全脑汇总体积。保留原始数值及精度，单位均为 mm³。
2. 区域指标包含双侧 DKT 皮层分区、皮层下结构、白质、脑室和胼胝体分区等。按源文件的 StructName 和 SegId 匹配；体积直接读取 Volume_mm3。
3. 本次提取范围为分割体积。皮层重建统计、厚度、面积、eTIV 和重建处理状态均不纳入。提取脚本仅读取分割状态、输入溯源和指定统计文件。
4. 0 保留为源统计明确报告的 0；空白表示缺失。源名单的年龄缺失保持为空，不插补。WM-hypointensities 是 T1 分割标签，不等价于 FLAIR 白质高信号负荷。
5. 所有体积为原始绝对值，未进行颅内容积归一化或年龄/性别校正，未计算访视差值。MaskVol 是脑掩膜体积，不是 eTIV。
6. 名单中的 rigid MRI 路径用于匹配溯源；实际分割输入见 segmentation_input_path。工程处理完成不代表人工解剖 QC 通过；原始影像和统计文件保持只读。

## 2. 元数据列

| 列名 | 单位/类型 | 含义 | 缺失行数 |
|---|---|---|---:|
| `IID` | 文本 | 原始名单的受试者 ID；必须作为字符串读取 | 0 |
| `instance` | 访视编码 | 2=首次影像访视，3=重复影像访视；同一 IID 两行 | 0 |
| `age` | 年 | 名单中的访视年龄，逐行原样保留；空值不插补 | 33 |
| `sex` | 编码 | 名单中的 sex，0=女性、1=男性；原样保留 | 0 |
| `cohort_mri_path` | 路径 | 名单中的 T1_rigid 路径，仅用于匹配溯源，不是本次统计输入 | 0 |
| `segmentation_input_path` | 路径 | _pipeline/provenance.json 记录的实际分割输入路径 | 0 |
| `stats_dir` | 路径 | 本访视 T1_seg 下的 stats 目录 | 0 |
| `segmentation_status` | 文本 | 提取快照中 segmentation.json 的 status；缺少状态文件为 missing | 0 |
| `segmentation_anatomical_qc` | 文本 | 分割阶段的人工解剖质控记录；not_reviewed=尚未人工审核 | 0 |
| `segmentation_stats_extracted` | 0/1 | 1=完成状态且分割统计通过解析检查并成功提取 | 0 |
| `extraction_note` | 文本 | 分割统计未提取原因；空值表示成功提取 | 2286 |

## 3. 每个数值列的定义

下列顺序与 CSV 数值列一致。脑区中文译名用于阅读，英文原始标签和 SegId 是精确匹配依据。所有数值指标单位均为 mm³（立方毫米）。

### 来源：`aseg+DKT.VINN.withCC.stats`

| 列名 | 中文含义 | 单位 | 源字段/标签 | 缺失行数 |
|---|---|---|---|---:|
| `seg__left_cerebral_white_matter__volume_mm3` | 左侧大脑白质体积 | mm^3 | `SegId=2; Left-Cerebral-White-Matter / Volume_mm3` | 0 |
| `seg__left_lateral_ventricle__volume_mm3` | 左侧侧脑室体积 | mm^3 | `SegId=4; Left-Lateral-Ventricle / Volume_mm3` | 0 |
| `seg__left_inf_lat_vent__volume_mm3` | 左侧侧脑室下角体积 | mm^3 | `SegId=5; Left-Inf-Lat-Vent / Volume_mm3` | 0 |
| `seg__left_cerebellum_white_matter__volume_mm3` | 左侧小脑白质体积 | mm^3 | `SegId=7; Left-Cerebellum-White-Matter / Volume_mm3` | 0 |
| `seg__left_cerebellum_cortex__volume_mm3` | 左侧小脑皮层体积 | mm^3 | `SegId=8; Left-Cerebellum-Cortex / Volume_mm3` | 0 |
| `seg__left_thalamus__volume_mm3` | 左侧丘脑体积 | mm^3 | `SegId=10; Left-Thalamus / Volume_mm3` | 0 |
| `seg__left_caudate__volume_mm3` | 左侧尾状核体积 | mm^3 | `SegId=11; Left-Caudate / Volume_mm3` | 0 |
| `seg__left_putamen__volume_mm3` | 左侧壳核体积 | mm^3 | `SegId=12; Left-Putamen / Volume_mm3` | 0 |
| `seg__left_pallidum__volume_mm3` | 左侧苍白球体积 | mm^3 | `SegId=13; Left-Pallidum / Volume_mm3` | 0 |
| `seg__3rd_ventricle__volume_mm3` | 第三脑室体积 | mm^3 | `SegId=14; 3rd-Ventricle / Volume_mm3` | 0 |
| `seg__4th_ventricle__volume_mm3` | 第四脑室体积 | mm^3 | `SegId=15; 4th-Ventricle / Volume_mm3` | 0 |
| `seg__brain_stem__volume_mm3` | 脑干体积 | mm^3 | `SegId=16; Brain-Stem / Volume_mm3` | 0 |
| `seg__left_hippocampus__volume_mm3` | 左侧海马体积 | mm^3 | `SegId=17; Left-Hippocampus / Volume_mm3` | 0 |
| `seg__left_amygdala__volume_mm3` | 左侧杏仁核体积 | mm^3 | `SegId=18; Left-Amygdala / Volume_mm3` | 0 |
| `seg__csf__volume_mm3` | 脑脊液标签区（非全颅脑脊液总量）体积 | mm^3 | `SegId=24; CSF / Volume_mm3` | 0 |
| `seg__left_accumbens_area__volume_mm3` | 左侧伏隔核区体积 | mm^3 | `SegId=26; Left-Accumbens-area / Volume_mm3` | 0 |
| `seg__left_ventraldc__volume_mm3` | 左侧腹侧间脑复合区体积 | mm^3 | `SegId=28; Left-VentralDC / Volume_mm3` | 0 |
| `seg__left_choroid_plexus__volume_mm3` | 左侧脉络丛体积 | mm^3 | `SegId=31; Left-choroid-plexus / Volume_mm3` | 0 |
| `seg__right_cerebral_white_matter__volume_mm3` | 右侧大脑白质体积 | mm^3 | `SegId=41; Right-Cerebral-White-Matter / Volume_mm3` | 0 |
| `seg__right_lateral_ventricle__volume_mm3` | 右侧侧脑室体积 | mm^3 | `SegId=43; Right-Lateral-Ventricle / Volume_mm3` | 0 |
| `seg__right_inf_lat_vent__volume_mm3` | 右侧侧脑室下角体积 | mm^3 | `SegId=44; Right-Inf-Lat-Vent / Volume_mm3` | 0 |
| `seg__right_cerebellum_white_matter__volume_mm3` | 右侧小脑白质体积 | mm^3 | `SegId=46; Right-Cerebellum-White-Matter / Volume_mm3` | 0 |
| `seg__right_cerebellum_cortex__volume_mm3` | 右侧小脑皮层体积 | mm^3 | `SegId=47; Right-Cerebellum-Cortex / Volume_mm3` | 0 |
| `seg__right_thalamus__volume_mm3` | 右侧丘脑体积 | mm^3 | `SegId=49; Right-Thalamus / Volume_mm3` | 0 |
| `seg__right_caudate__volume_mm3` | 右侧尾状核体积 | mm^3 | `SegId=50; Right-Caudate / Volume_mm3` | 0 |
| `seg__right_putamen__volume_mm3` | 右侧壳核体积 | mm^3 | `SegId=51; Right-Putamen / Volume_mm3` | 0 |
| `seg__right_pallidum__volume_mm3` | 右侧苍白球体积 | mm^3 | `SegId=52; Right-Pallidum / Volume_mm3` | 0 |
| `seg__right_hippocampus__volume_mm3` | 右侧海马体积 | mm^3 | `SegId=53; Right-Hippocampus / Volume_mm3` | 0 |
| `seg__right_amygdala__volume_mm3` | 右侧杏仁核体积 | mm^3 | `SegId=54; Right-Amygdala / Volume_mm3` | 0 |
| `seg__right_accumbens_area__volume_mm3` | 右侧伏隔核区体积 | mm^3 | `SegId=58; Right-Accumbens-area / Volume_mm3` | 0 |
| `seg__right_ventraldc__volume_mm3` | 右侧腹侧间脑复合区体积 | mm^3 | `SegId=60; Right-VentralDC / Volume_mm3` | 0 |
| `seg__right_choroid_plexus__volume_mm3` | 右侧脉络丛体积 | mm^3 | `SegId=63; Right-choroid-plexus / Volume_mm3` | 0 |
| `seg__wm_hypointensities__volume_mm3` | 白质低信号标签区体积 | mm^3 | `SegId=77; WM-hypointensities / Volume_mm3` | 0 |
| `seg__cc_posterior__volume_mm3` | 胼胝体后部体积 | mm^3 | `SegId=251; CC_Posterior / Volume_mm3` | 0 |
| `seg__cc_mid_posterior__volume_mm3` | 胼胝体中后部体积 | mm^3 | `SegId=252; CC_Mid_Posterior / Volume_mm3` | 0 |
| `seg__cc_central__volume_mm3` | 胼胝体中央部体积 | mm^3 | `SegId=253; CC_Central / Volume_mm3` | 0 |
| `seg__cc_mid_anterior__volume_mm3` | 胼胝体中前部体积 | mm^3 | `SegId=254; CC_Mid_Anterior / Volume_mm3` | 0 |
| `seg__cc_anterior__volume_mm3` | 胼胝体前部体积 | mm^3 | `SegId=255; CC_Anterior / Volume_mm3` | 0 |
| `seg__ctx_lh_caudalanteriorcingulate__volume_mm3` | 左侧尾侧前扣带皮层（皮层）体积 | mm^3 | `SegId=1002; ctx-lh-caudalanteriorcingulate / Volume_mm3` | 0 |
| `seg__ctx_lh_caudalmiddlefrontal__volume_mm3` | 左侧尾侧额中回（皮层）体积 | mm^3 | `SegId=1003; ctx-lh-caudalmiddlefrontal / Volume_mm3` | 0 |
| `seg__ctx_lh_cuneus__volume_mm3` | 左侧楔叶（皮层）体积 | mm^3 | `SegId=1005; ctx-lh-cuneus / Volume_mm3` | 0 |
| `seg__ctx_lh_entorhinal__volume_mm3` | 左侧内嗅皮层（皮层）体积 | mm^3 | `SegId=1006; ctx-lh-entorhinal / Volume_mm3` | 0 |
| `seg__ctx_lh_fusiform__volume_mm3` | 左侧梭状回（皮层）体积 | mm^3 | `SegId=1007; ctx-lh-fusiform / Volume_mm3` | 0 |
| `seg__ctx_lh_inferiorparietal__volume_mm3` | 左侧顶下小叶（皮层）体积 | mm^3 | `SegId=1008; ctx-lh-inferiorparietal / Volume_mm3` | 0 |
| `seg__ctx_lh_inferiortemporal__volume_mm3` | 左侧颞下回（皮层）体积 | mm^3 | `SegId=1009; ctx-lh-inferiortemporal / Volume_mm3` | 0 |
| `seg__ctx_lh_isthmuscingulate__volume_mm3` | 左侧扣带峡部（皮层）体积 | mm^3 | `SegId=1010; ctx-lh-isthmuscingulate / Volume_mm3` | 0 |
| `seg__ctx_lh_lateraloccipital__volume_mm3` | 左侧外侧枕叶皮层（皮层）体积 | mm^3 | `SegId=1011; ctx-lh-lateraloccipital / Volume_mm3` | 0 |
| `seg__ctx_lh_lateralorbitofrontal__volume_mm3` | 左侧外侧眶额皮层（皮层）体积 | mm^3 | `SegId=1012; ctx-lh-lateralorbitofrontal / Volume_mm3` | 0 |
| `seg__ctx_lh_lingual__volume_mm3` | 左侧舌回（皮层）体积 | mm^3 | `SegId=1013; ctx-lh-lingual / Volume_mm3` | 0 |
| `seg__ctx_lh_medialorbitofrontal__volume_mm3` | 左侧内侧眶额皮层（皮层）体积 | mm^3 | `SegId=1014; ctx-lh-medialorbitofrontal / Volume_mm3` | 0 |
| `seg__ctx_lh_middletemporal__volume_mm3` | 左侧颞中回（皮层）体积 | mm^3 | `SegId=1015; ctx-lh-middletemporal / Volume_mm3` | 0 |
| `seg__ctx_lh_parahippocampal__volume_mm3` | 左侧海马旁回（皮层）体积 | mm^3 | `SegId=1016; ctx-lh-parahippocampal / Volume_mm3` | 0 |
| `seg__ctx_lh_paracentral__volume_mm3` | 左侧中央旁小叶（皮层）体积 | mm^3 | `SegId=1017; ctx-lh-paracentral / Volume_mm3` | 0 |
| `seg__ctx_lh_parsopercularis__volume_mm3` | 左侧额下回盖部（皮层）体积 | mm^3 | `SegId=1018; ctx-lh-parsopercularis / Volume_mm3` | 0 |
| `seg__ctx_lh_parsorbitalis__volume_mm3` | 左侧额下回眶部（皮层）体积 | mm^3 | `SegId=1019; ctx-lh-parsorbitalis / Volume_mm3` | 0 |
| `seg__ctx_lh_parstriangularis__volume_mm3` | 左侧额下回三角部（皮层）体积 | mm^3 | `SegId=1020; ctx-lh-parstriangularis / Volume_mm3` | 0 |
| `seg__ctx_lh_pericalcarine__volume_mm3` | 左侧距状沟周围皮层（皮层）体积 | mm^3 | `SegId=1021; ctx-lh-pericalcarine / Volume_mm3` | 0 |
| `seg__ctx_lh_postcentral__volume_mm3` | 左侧中央后回（皮层）体积 | mm^3 | `SegId=1022; ctx-lh-postcentral / Volume_mm3` | 0 |
| `seg__ctx_lh_posteriorcingulate__volume_mm3` | 左侧后扣带皮层（皮层）体积 | mm^3 | `SegId=1023; ctx-lh-posteriorcingulate / Volume_mm3` | 0 |
| `seg__ctx_lh_precentral__volume_mm3` | 左侧中央前回（皮层）体积 | mm^3 | `SegId=1024; ctx-lh-precentral / Volume_mm3` | 0 |
| `seg__ctx_lh_precuneus__volume_mm3` | 左侧楔前叶（皮层）体积 | mm^3 | `SegId=1025; ctx-lh-precuneus / Volume_mm3` | 0 |
| `seg__ctx_lh_rostralanteriorcingulate__volume_mm3` | 左侧吻侧前扣带皮层（皮层）体积 | mm^3 | `SegId=1026; ctx-lh-rostralanteriorcingulate / Volume_mm3` | 0 |
| `seg__ctx_lh_rostralmiddlefrontal__volume_mm3` | 左侧吻侧额中回（皮层）体积 | mm^3 | `SegId=1027; ctx-lh-rostralmiddlefrontal / Volume_mm3` | 0 |
| `seg__ctx_lh_superiorfrontal__volume_mm3` | 左侧额上回（皮层）体积 | mm^3 | `SegId=1028; ctx-lh-superiorfrontal / Volume_mm3` | 0 |
| `seg__ctx_lh_superiorparietal__volume_mm3` | 左侧顶上小叶（皮层）体积 | mm^3 | `SegId=1029; ctx-lh-superiorparietal / Volume_mm3` | 0 |
| `seg__ctx_lh_superiortemporal__volume_mm3` | 左侧颞上回（皮层）体积 | mm^3 | `SegId=1030; ctx-lh-superiortemporal / Volume_mm3` | 0 |
| `seg__ctx_lh_supramarginal__volume_mm3` | 左侧缘上回（皮层）体积 | mm^3 | `SegId=1031; ctx-lh-supramarginal / Volume_mm3` | 0 |
| `seg__ctx_lh_transversetemporal__volume_mm3` | 左侧横颞回（皮层）体积 | mm^3 | `SegId=1034; ctx-lh-transversetemporal / Volume_mm3` | 0 |
| `seg__ctx_lh_insula__volume_mm3` | 左侧岛叶（皮层）体积 | mm^3 | `SegId=1035; ctx-lh-insula / Volume_mm3` | 0 |
| `seg__ctx_rh_caudalanteriorcingulate__volume_mm3` | 右侧尾侧前扣带皮层（皮层）体积 | mm^3 | `SegId=2002; ctx-rh-caudalanteriorcingulate / Volume_mm3` | 0 |
| `seg__ctx_rh_caudalmiddlefrontal__volume_mm3` | 右侧尾侧额中回（皮层）体积 | mm^3 | `SegId=2003; ctx-rh-caudalmiddlefrontal / Volume_mm3` | 0 |
| `seg__ctx_rh_cuneus__volume_mm3` | 右侧楔叶（皮层）体积 | mm^3 | `SegId=2005; ctx-rh-cuneus / Volume_mm3` | 0 |
| `seg__ctx_rh_entorhinal__volume_mm3` | 右侧内嗅皮层（皮层）体积 | mm^3 | `SegId=2006; ctx-rh-entorhinal / Volume_mm3` | 0 |
| `seg__ctx_rh_fusiform__volume_mm3` | 右侧梭状回（皮层）体积 | mm^3 | `SegId=2007; ctx-rh-fusiform / Volume_mm3` | 0 |
| `seg__ctx_rh_inferiorparietal__volume_mm3` | 右侧顶下小叶（皮层）体积 | mm^3 | `SegId=2008; ctx-rh-inferiorparietal / Volume_mm3` | 0 |
| `seg__ctx_rh_inferiortemporal__volume_mm3` | 右侧颞下回（皮层）体积 | mm^3 | `SegId=2009; ctx-rh-inferiortemporal / Volume_mm3` | 0 |
| `seg__ctx_rh_isthmuscingulate__volume_mm3` | 右侧扣带峡部（皮层）体积 | mm^3 | `SegId=2010; ctx-rh-isthmuscingulate / Volume_mm3` | 0 |
| `seg__ctx_rh_lateraloccipital__volume_mm3` | 右侧外侧枕叶皮层（皮层）体积 | mm^3 | `SegId=2011; ctx-rh-lateraloccipital / Volume_mm3` | 0 |
| `seg__ctx_rh_lateralorbitofrontal__volume_mm3` | 右侧外侧眶额皮层（皮层）体积 | mm^3 | `SegId=2012; ctx-rh-lateralorbitofrontal / Volume_mm3` | 0 |
| `seg__ctx_rh_lingual__volume_mm3` | 右侧舌回（皮层）体积 | mm^3 | `SegId=2013; ctx-rh-lingual / Volume_mm3` | 0 |
| `seg__ctx_rh_medialorbitofrontal__volume_mm3` | 右侧内侧眶额皮层（皮层）体积 | mm^3 | `SegId=2014; ctx-rh-medialorbitofrontal / Volume_mm3` | 0 |
| `seg__ctx_rh_middletemporal__volume_mm3` | 右侧颞中回（皮层）体积 | mm^3 | `SegId=2015; ctx-rh-middletemporal / Volume_mm3` | 0 |
| `seg__ctx_rh_parahippocampal__volume_mm3` | 右侧海马旁回（皮层）体积 | mm^3 | `SegId=2016; ctx-rh-parahippocampal / Volume_mm3` | 0 |
| `seg__ctx_rh_paracentral__volume_mm3` | 右侧中央旁小叶（皮层）体积 | mm^3 | `SegId=2017; ctx-rh-paracentral / Volume_mm3` | 0 |
| `seg__ctx_rh_parsopercularis__volume_mm3` | 右侧额下回盖部（皮层）体积 | mm^3 | `SegId=2018; ctx-rh-parsopercularis / Volume_mm3` | 0 |
| `seg__ctx_rh_parsorbitalis__volume_mm3` | 右侧额下回眶部（皮层）体积 | mm^3 | `SegId=2019; ctx-rh-parsorbitalis / Volume_mm3` | 0 |
| `seg__ctx_rh_parstriangularis__volume_mm3` | 右侧额下回三角部（皮层）体积 | mm^3 | `SegId=2020; ctx-rh-parstriangularis / Volume_mm3` | 0 |
| `seg__ctx_rh_pericalcarine__volume_mm3` | 右侧距状沟周围皮层（皮层）体积 | mm^3 | `SegId=2021; ctx-rh-pericalcarine / Volume_mm3` | 0 |
| `seg__ctx_rh_postcentral__volume_mm3` | 右侧中央后回（皮层）体积 | mm^3 | `SegId=2022; ctx-rh-postcentral / Volume_mm3` | 0 |
| `seg__ctx_rh_posteriorcingulate__volume_mm3` | 右侧后扣带皮层（皮层）体积 | mm^3 | `SegId=2023; ctx-rh-posteriorcingulate / Volume_mm3` | 0 |
| `seg__ctx_rh_precentral__volume_mm3` | 右侧中央前回（皮层）体积 | mm^3 | `SegId=2024; ctx-rh-precentral / Volume_mm3` | 0 |
| `seg__ctx_rh_precuneus__volume_mm3` | 右侧楔前叶（皮层）体积 | mm^3 | `SegId=2025; ctx-rh-precuneus / Volume_mm3` | 0 |
| `seg__ctx_rh_rostralanteriorcingulate__volume_mm3` | 右侧吻侧前扣带皮层（皮层）体积 | mm^3 | `SegId=2026; ctx-rh-rostralanteriorcingulate / Volume_mm3` | 0 |
| `seg__ctx_rh_rostralmiddlefrontal__volume_mm3` | 右侧吻侧额中回（皮层）体积 | mm^3 | `SegId=2027; ctx-rh-rostralmiddlefrontal / Volume_mm3` | 0 |
| `seg__ctx_rh_superiorfrontal__volume_mm3` | 右侧额上回（皮层）体积 | mm^3 | `SegId=2028; ctx-rh-superiorfrontal / Volume_mm3` | 0 |
| `seg__ctx_rh_superiorparietal__volume_mm3` | 右侧顶上小叶（皮层）体积 | mm^3 | `SegId=2029; ctx-rh-superiorparietal / Volume_mm3` | 0 |
| `seg__ctx_rh_superiortemporal__volume_mm3` | 右侧颞上回（皮层）体积 | mm^3 | `SegId=2030; ctx-rh-superiortemporal / Volume_mm3` | 0 |
| `seg__ctx_rh_supramarginal__volume_mm3` | 右侧缘上回（皮层）体积 | mm^3 | `SegId=2031; ctx-rh-supramarginal / Volume_mm3` | 0 |
| `seg__ctx_rh_transversetemporal__volume_mm3` | 右侧横颞回（皮层）体积 | mm^3 | `SegId=2034; ctx-rh-transversetemporal / Volume_mm3` | 0 |
| `seg__ctx_rh_insula__volume_mm3` | 右侧岛叶（皮层）体积 | mm^3 | `SegId=2035; ctx-rh-insula / Volume_mm3` | 0 |
| `seg_global__subcortgrayvol_mm3` | 皮层下灰质总体积 | mm^3 | `# Measure SubCortGrayVol` | 0 |
| `seg_global__maskvol_mm3` | 脑掩膜体积（不是颅内容积） | mm^3 | `# Measure MaskVol` | 0 |
| `seg_global__brainsegvol_mm3` | 脑分割总体积 | mm^3 | `# Measure BrainSegVol` | 0 |
| `seg_global__brainsegvolnotvent_mm3` | 排除脑室后的脑分割体积 | mm^3 | `# Measure BrainSegVolNotVent` | 0 |
| `seg_global__supratentorialvol_mm3` | 幕上总体积 | mm^3 | `# Measure SupraTentorialVol` | 0 |
| `seg_global__supratentorialvolnotvent_mm3` | 排除脑室后的幕上体积 | mm^3 | `# Measure SupraTentorialVolNotVent` | 0 |
| `seg_global__rhcerebralwhitemattervol_mm3` | 右侧大脑白质总体积 | mm^3 | `# Measure rhCerebralWhiteMatterVol` | 0 |
| `seg_global__lhcerebralwhitemattervol_mm3` | 左侧大脑白质总体积 | mm^3 | `# Measure lhCerebralWhiteMatterVol` | 0 |
| `seg_global__cerebralwhitemattervol_mm3` | 双侧大脑白质总体积 | mm^3 | `# Measure CerebralWhiteMatterVol` | 0 |

## 4. 校验与复现

- 主表 SHA-256：`08fe464a3f6bb4b1f775fadfd6ffe665ba5ef733242c4bc3cf5a23d438c535a1`。
- 源名单 SHA-256：`435267dc3f3acec86201fdb94b173993fc1d7739e669003a39a61431eabb6f07`。
- `recommended_core4_i2_i3_brain_regions_sources.csv`：逐个已读取文件的路径、大小、修改时间和 SHA-256，包含状态快照及实际统计来源。
- `recommended_core4_i2_i3_brain_regions_audit.json`：访视覆盖、配对数、各列缺失/零值计数及提取异常。
- 已验证 ID/访视唯一、每人同时有 i2/i3、行序不变、原名单哈希不变、字段定义一致、数值有限且非负，以及全部 CSV 单元格写入后回读一致。
- 每个文件读取前后检查大小和修改时间；每个完成阶段读取后核对状态快照未改变。状态树仍在更新，本表是本次快照；若需核对原始文件是否后来变化，可使用来源清单中的 SHA-256。
- 重新提取只读取已有结果，默认覆盖本脚本生成的主表、MD、audit 和 sources 文件；不会启动任何重建进程。若需保留此次快照，用 `--output-dir` 指定新目录。

```bash
python /mnt/sda/liupeifu/WorkSpace/Codes/datas/extract_core4_brain_regions.py
```

## 5. 官方指标说明

- [FastSurfer 输出文件](https://deep-mi.org/FastSurfer/stable/overview/OUTPUT_FILES.html)：分割与表面重建输出文件说明；本表实际来源以本机统计文件头为准。
- [FreeSurfer MorphometryStats](https://freesurfer.net/fswiki/MorphometryStats)：全脑汇总指标的含义（本表无 eTIV）。
