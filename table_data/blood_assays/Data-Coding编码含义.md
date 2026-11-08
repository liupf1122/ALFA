# blood_assays 字段 Data-Coding 编码含义

> 数据来源：UK Biobank Data-Coding 页面（`https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=<编码>`）。
> 仅带类别编码的字段（多为 Categorical，少数 Integer/Text 含特殊值编码）在此列出；纯连续/整数测量字段归入末尾「无 Data-Coding」小节。
> 使用相同 Data-Coding 的字段合并在同一小节。负值（如 -1/-3/-818 等）通常为「不知道/不愿回答/跳过/缺失」等特殊值；当取值本身即数字编号（如卡片/图片索引）时，中文列与原值相同。

## Data-Coding 9

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=9

适用字段：
- `31` 性别（Sex）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | Female | 女性 |
| 1 | Male | 男性 |

## 无 Data-Coding（连续/整数/日期等数值型字段）

以下字段无类别编码，直接以数值/日期/文本记录：

- `30000` 白细胞计数（White blood cell (leukocyte) count） — Continuous, 10^9 cells/Litre
- `30010` 红细胞计数（Red blood cell (erythrocyte) count） — Continuous, 10^12 cells/Litre
- `30020` 血红蛋白浓度（Haemoglobin concentration） — Continuous, grams/decilitre
- `30030` 红细胞压积百分比（Haematocrit percentage） — Continuous, percent
- `30040` 平均红细胞体积（Mean corpuscular volume） — Continuous, femtolitres
- `30050` 平均红细胞血红蛋白含量（Mean corpuscular haemoglobin） — Continuous, picograms
- `30060` 平均红细胞血红蛋白浓度（Mean corpuscular haemoglobin concentration） — Continuous, grams/decilitre
- `30070` 红细胞分布宽度（Red blood cell (erythrocyte) distribution width） — Continuous, percent
- `30080` 血小板计数（Platelet count） — Continuous, 10^9 cells/Litre
- `30090` 血小板压积（Platelet crit） — Continuous, percent
- `30100` 平均血小板体积（Mean platelet (thrombocyte) volume） — Continuous, femtolitres
- `30110` 血小板分布宽度（Platelet distribution width） — Continuous, percent
- `30120` 淋巴细胞计数（Lymphocyte count） — Continuous, 10^9 cells/Litre
- `30130` 单核细胞计数（Monocyte count） — Continuous, 10^9 cells/Litre
- `30140` 中性粒细胞计数（Neutrophill count） — Continuous, 10^9 cells/Litre
- `30150` 嗜酸性粒细胞计数（Eosinophill count） — Continuous, 10^9 cells/Litre
- `30160` 嗜碱性粒细胞计数（Basophill count） — Continuous, 10^9 cells/Litre
- `30170` 有核红细胞计数（Nucleated red blood cell count） — Continuous, 10^9 cells/Litre
- `30180` 淋巴细胞百分比（Lymphocyte percentage） — Continuous, percent
- `30190` 单核细胞百分比（Monocyte percentage） — Continuous, percent
- `30200` 中性粒细胞百分比（Neutrophill percentage） — Continuous, percent
- `30210` 嗜酸性粒细胞百分比（Eosinophill percentage） — Continuous, percent
- `30220` 嗜碱性粒细胞百分比（Basophill percentage） — Continuous, percent
- `30230` 有核红细胞百分比（Nucleated red blood cell percentage） — Continuous, percent
- `30240` 网织红细胞百分比（Reticulocyte percentage） — Continuous, percent
- `30250` 网织红细胞计数（Reticulocyte count） — Continuous, 10^12 cells/Litre
- `30260` 平均网织红细胞体积（Mean reticulocyte volume） — Continuous, femtolitres
- `30270` 平均球形红细胞体积（Mean sphered cell volume） — Continuous, femtolitres
- `30280` 未成熟网织红细胞比例（Immature reticulocyte fraction） — Continuous, ratio
- `30290` 高光散射网织红细胞百分比（High light scatter reticulocyte percentage） — Continuous, percent
- `30300` 高光散射网织红细胞计数（High light scatter reticulocyte count） — Continuous, 10^12 cells/Litre
