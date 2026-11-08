# 可重复分析

从评估生成的逐扫描/逐配对 CSV 重算描述统计：

```bash
python analysis/summarize.py outputs/<评估运行名>/metrics.csv --output outputs/<评估运行名>/statistics.csv
```

输出 count/mean/std/min/max；只做描述汇总，不将每个扫描当成独立受试者做显著性检验。
本次未生成科研比较图。后续绘图应区分原始输入与重建，固定显示窗和切片，并标明 PSNR 的比较对象。
