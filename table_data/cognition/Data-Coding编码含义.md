# cognition 字段 Data-Coding 编码含义

> 数据来源：UK Biobank Data-Coding 页面（`https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=<编码>`）。
> 仅带类别编码的字段（多为 Categorical，少数 Integer/Text 含特殊值编码）在此列出；纯连续/整数测量字段归入末尾「无 Data-Coding」小节。
> 使用相同 Data-Coding 的字段合并在同一小节。负值（如 -1/-3/-818 等）通常为「不知道/不愿回答/跳过/缺失」等特殊值；当取值本身即数字编号（如卡片/图片索引）时，中文列与原值相同。

## Data-Coding 92

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=92

适用字段：
- `401` 本轮卡片A的索引（Index for card A in round）
- `402` 本轮卡片B的索引（Index for card B in round）
- `10139` 本轮卡片A的索引（试点）（Index for card A in round (pilot)）
- `10140` 本轮卡片B的索引（试点）（Index for card B in round (pilot)）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | Solid circle | 实心圆 |
| 1 | Hollow circle | 空心圆 |
| 2 | Vertical/horizontal cross "+" | 正十字"+" |
| 3 | Equals-sign "=" | 等号"=" |
| 4 | Rugby-post "H" | 橄榄球门柱"H" |
| 5 | Solid square | 实心方块 |
| 6 | Hollow square | 空心方块 |
| 7 | Triangle | 三角形 |
| 8 | Smiley face | 笑脸 |
| 9 | Fir-tree (3 overlapping triangles) | 杉树(3个叠加三角形) |
| 10 | Heart | 心形 |
| 11 | Diamond | 菱形 |
| 12 | Four squares | 四个方块 |
| 13 | Lightning bolt | 闪电 |
| 14 | Top-hat | 礼帽 |
| 15 | Linked squares | 相连方块 |
| 16 | Diagonal cross | 斜十字(×) |
| 17 | Crescent | 新月形 |
| 18 | Sitting cat | 坐着的猫 |
| 19 | Bow tie | 领结 |
| 20 | House | 房子 |
| 21 | Horse-shoe "U" | 马蹄形"U" |
| 22 | Star | 星形 |
| 23 | Person | 人(person) |
| 24 | Knife and fork | 刀叉 |

## Data-Coding 100696

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100696

适用字段：
- `4282` 正确记住的最大位数（Maximum digits remembered correctly）
- `4283` 完成的数字记忆测试轮数（Number of rounds of numeric memory test performed）
- `10612` 以'S'开头的词数（试点）（Number of words beginning with 'S' (pilot)）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -1 | Abandoned | 已放弃 |

## Data-Coding 16

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=16

适用字段：
- `4292` 前瞻记忆：初次回答（PM: initial answer）
- `4293` 前瞻记忆：最终回答（PM: final answer）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -1 | Participant skipped/abandonded | 参与者跳过/放弃 |
| 0 | Blue square | 蓝色方块 |
| 1 | Pink star | 粉色星形 |
| 2 | Grey cross | 灰色十字 |
| 3 | Orange circle | 橙色圆 |

## Data-Coding 29

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=29

适用字段：
- `4259` 数字是否输入正确（Digits entered correctly）
- `4294` 最终尝试是否正确（Final attempt correct）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | no | 否 |
| 1 | yes | 是 |
| 9 | abandon | 放弃 |

## Data-Coding 402

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=402

适用字段：
- `400` 完成本轮用时（Time to complete round）
- `10138` 完成本轮用时（试点）（Time to complete round (pilot)）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | Test not completed | 测试未完成 |

## Data-Coding 1990

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=1990

适用字段：
- `6348` 完成数字路径用时（连线测试#1）（Duration to complete numeric path (trail #1)）
- `6350` 完成字母数字路径用时（连线#2）（Duration to complete alphanumeric path (trail #2)）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | Trail not completed | 连线未完成 |

## Data-Coding 2536

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=2536

适用字段：
- `20016` 流体智力得分（Fluid intelligence score）
- `20128` 限时内尝试的流体智力题数（Number of fluid intelligence questions attempted within time limit）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -1 | Not calculable due to unclean data | 因数据不洁无法计算 |

## Data-Coding 9

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=9

适用字段：
- `31` 性别（Sex）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | Female | 女性 |
| 1 | Male | 男性 |

## Data-Coding 18

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=18

适用字段：
- `20018` 前瞻记忆结果（Prospective memory result）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | Instruction not recalled, either skipped or incorrect | 未回忆起指令(跳过或错误) |
| 1 | Correct recall on first attempt | 第一次尝试即正确回忆 |
| 2 | Correct recall on second attempt | 第二次尝试正确回忆 |

## Data-Coding 31

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=31

适用字段：
- `4281` 数字记忆测试完成状态（Completion status of numeric memory test）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 2 | stopped | 已停止 |
| 3 | complete | 完成 |
| 9 | abandoned | 已放弃 |

## Data-Coding 32

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=32

适用字段：
- `4287` 测试完成状态（Test completion status）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 3 | complete | 完成 |
| 9 | abandoned | 已放弃 |

## Data-Coding 3050

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=3050

适用字段：
- `7677` 测试结束原因（Reason test concluded）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 1 | All rounds completed without reaching error threshold | 完成所有轮次且未达错误阈值 |
| 2 | Error threshold reached | 达到错误阈值 |
| 3 | Time limit reached during round of letters | 在一组字母环节达到时限 |
| 4 | Time limit reached during individual letter | 在单个字母环节达到时限 |

## Data-Coding 6312

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6312

适用字段：
- `6312` 输入的数值（符号数字替换）（Value entered）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 1 | 1 move | 1步 |
| 2 | 2 moves | 2步 |
| 3 | 3 moves | 3步 |
| 4 | 4 moves | 4步 |
| 5 | 5 moves | 5步 |
| 6 | 6 moves | 6步 |

## Data-Coding 6314

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6314

适用字段：
- `6314` 每轮使用的词/图组（Word/picture group used for each round）

该编码为大型/层级编码，共 **340** 个条目，不在此逐条列出，请通过上方链接查询。

## Data-Coding 6315

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6315

适用字段：
- `6315` 每轮所选图片（Picture selected for each round）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 1 | Dummy #1 | 占位项#1 |
| 2 | Dummy #2 | 占位项#2 |
| 3 | Dummy #3 | 占位项#3 |
| 9 | Correct | 正确 |

## Data-Coding 6332

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6332

适用字段：
- `6332` 每道题所选项（Item selected for each puzzle）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | 0 top-left | 0 左上 |
| 1 | 1 | 1 |
| 2 | 2 | 2 |
| 3 | 3 | 3 |
| 4 | 4 | 4 |
| 5 | 5 | 5 |
| 6 | 6 | 6 |
| 7 | 7 | 7 |

## Data-Coding 6448

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6448

适用字段：
- `6448` 与"huge(巨大)"关联的词（Word associated with "huge"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | car | 汽车 |
| 2 | plant | 植物 |
| 3 | house | 房子 |
| 4 | trousers | 裤子 |

## Data-Coding 6459

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6459

适用字段：
- `6459` 与"happy(高兴)"关联的词（Word associated with "happy"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | dog | 狗 |
| 2 | elephant | 大象 |
| 3 | cat | 猫 |
| 4 | clown | 小丑 |

## Data-Coding 6470

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6470

适用字段：
- `6470` 与"tattered(破烂)"关联的词（Word associated with "tattered"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | dress | 连衣裙 |
| 2 | house | 房子 |
| 3 | plant | 植物 |
| 4 | curtains | 窗帘 |

## Data-Coding 6481

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6481

适用字段：
- `6481` 与"old(旧)"关联的词（Word associated with "old"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | car | 汽车 |
| 2 | cat | 猫 |
| 3 | house | 房子 |
| 4 | elephant | 大象 |

## Data-Coding 6492

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6492

适用字段：
- `6492` 与"long(长)"关联的词（Word associated with "long"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | dress | 连衣裙 |
| 2 | curtains | 窗帘 |
| 3 | car | 汽车 |
| 4 | trousers | 裤子 |

## Data-Coding 6503

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6503

适用字段：
- `6503` 与"red(红)"关联的词（Word associated with "red"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | dish | 盘子 |
| 2 | curtains | 窗帘 |
| 3 | plant | 植物 |
| 4 | car | 汽车 |

## Data-Coding 6514

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6514

适用字段：
- `6514` 与"sulking(生闷气)"关联的词（Word associated with "sulking"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | dog | 狗 |
| 2 | elephant | 大象 |
| 3 | clown | 小丑 |
| 4 | cat | 猫 |

## Data-Coding 6525

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6525

适用字段：
- `6525` 与"pretty(漂亮)"关联的词（Word associated with "pretty"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | cat | 猫 |
| 2 | dress | 连衣裙 |
| 3 | dish | 盘子 |
| 4 | plant | 植物 |

## Data-Coding 6536

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6536

适用字段：
- `6536` 与"tiny(微小)"关联的词（Word associated with "tiny"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | dress | 连衣裙 |
| 2 | house | 房子 |
| 3 | dog | 狗 |
| 4 | cat | 猫 |

## Data-Coding 6547

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=6547

适用字段：
- `6547` 与"new(新)"关联的词（Word associated with "new"）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| 1 | plant | 植物 |
| 2 | curtains | 窗帘 |
| 3 | house | 房子 |
| 4 | dress | 连衣裙 |

## Data-Coding 100280

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100280

适用字段：
- `10610` 词语计数（试点）（Word count (pilot)）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 0 | No | 否 |
| 1 | Yes | 是 |
| 2 | Yes (first language not English) | 是(母语非英语) |

## Data-Coding 100642

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100642

适用字段：
- `4924` 是否尝试流体智力(FI)测试（Attempted fluid intelligence (FI) test.）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| 1 | Begin puzzles | 开始题目 |
| 2 | I am unable to try this | 我无法尝试此项 |

## Data-Coding 100643

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100643

适用字段：
- `4935` FI1：数字加法（FI1 : numeric addition test）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 13 | 13 | 13 |
| 14 | 14 | 14 |
| 15 | 15 | 15 |
| 16 | 16 | 16 |
| 17 | 17 | 17 |

## Data-Coding 100644

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100644

适用字段：
- `4946` FI2：识别最大数字（FI2 : identify largest number）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 253 | 253 | 253 |
| 308 | 308 | 308 |
| 642 | 642 | 642 |
| 714 | 714 | 714 |
| 987 | 987 | 987 |

## Data-Coding 100645

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100645

适用字段：
- `4957` FI3：词语插补（FI3 : word interpolation）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 1 | Grow | 生长(grow) |
| 2 | Develop | 发展(develop) |
| 3 | Improve | 改善(improve) |
| 4 | Adult | 成人 |
| 5 | Old | 旧/老(old) |

## Data-Coding 100646

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100646

适用字段：
- `4968` FI4：位置算术（FI4 : positional arithmetic）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 5 | 5 | 5 |
| 6 | 6 | 6 |
| 7 | 7 | 7 |
| 8 | 8 | 8 |

## Data-Coding 100647

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100647

适用字段：
- `4979` FI5：亲属关系计算（FI5 : family relationship calculation）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 1 | Aunt | 姨/姑(aunt) |
| 2 | Sister | 姐妹(sister) |
| 3 | Niece | 侄女/外甥女(niece) |
| 4 | Cousin | 堂/表亲(cousin) |
| 5 | No relation | 无亲属关系 |

## Data-Coding 100648

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100648

适用字段：
- `4990` FI6：条件算术（FI6 : conditional arithmetic）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 68 | 68 | 68 |
| 69 | 69 | 69 |
| 70 | 70 | 70 |
| 71 | 71 | 71 |
| 72 | 72 | 72 |

## Data-Coding 100649

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100649

适用字段：
- `5001` FI7：同义词（FI7 : synonym）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 1 | Pause | 暂停 |
| 2 | Close | 近/关闭(close) |
| 3 | Cease | 停止(cease) |
| 4 | Break | 打破/折断(break) |
| 5 | Rest | 休息(rest) |

## Data-Coding 100650

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100650

适用字段：
- `5012` FI8：连锁算术（FI8 : chained arithmetic）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 25 | 25 | 25 |
| 26 | 26 | 26 |
| 27 | 27 | 27 |
| 28 | 28 | 28 |
| 29 | 29 | 29 |

## Data-Coding 100651

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100651

适用字段：
- `5556` FI9：概念插补（FI9 : concept interpolation）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 1 | Long | 长(long) |
| 2 | Deep | 深(deep) |
| 3 | Top | 顶部/上(top) |
| 4 | Metres | 米 |
| 5 | Tall | 高(tall) |

## Data-Coding 100652

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100652

适用字段：
- `5699` FI10：算术数列识别（FI10 : arithmetic sequence recognition）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 92 | 92 | 92 |
| 93 | 93 | 93 |
| 94 | 94 | 94 |
| 95 | 95 | 95 |
| 96 | 96 | 96 |

## Data-Coding 100653

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100653

适用字段：
- `5779` FI11：反义词（FI11 : antonym）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 1 | Calm | 平静 |
| 2 | Anxious | 焦虑 |
| 3 | Cool | 凉/酷(cool) |
| 4 | Worried | 担忧 |
| 5 | Tense | 紧张 |

## Data-Coding 100654

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100654

适用字段：
- `5790` FI12：平方数列识别（FI12 : square sequence recognition）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 45 | 45 | 45 |
| 46 | 46 | 46 |
| 47 | 47 | 47 |
| 48 | 48 | 48 |
| 49 | 49 | 49 |
| 50 | 50 | 50 |

## Data-Coding 100655

链接：https://biobank.ndph.ox.ac.uk/ukb/coding.cgi?id=100655

适用字段：
- `5866` FI13：子集包含逻辑（FI13 : subset inclusion logic）

| Coding | Meaning | 中文 |
| --- | --- | --- |
| -5 | Not sure | 不确定 |
| -3 | Prefer not to answer | 不愿回答 |
| -1 | Do not know | 不知道 |
| 1 | False | 假/错误(False) |
| 2 | True | 真/正确(True) |
| 3 | Neither true nor false | 既非真也非假 |

## 无 Data-Coding（连续/整数/日期等数值型字段）

以下字段无类别编码，直接以数值/日期/文本记录：

- `7669` 显示的图像（Image displayed） — Text
- `7670` 向参与者显示的字母（Letter displayed to participant） — Text
- `7671` 参与者选择的字母（Letter selected by participant） — Text
- `7672` 操作历史（History of actions performed） — Text
- `7673` 从显示图像到参与者作出选择的时长（Duration between presenting an image and participant making selection） — Integer
- `7674` 从显示图像到参与者按"下一步"的时长（Duration between presenting an image and participant pressing Next button） — Integer
- `7676` 显示的字母数（Number of letters displayed） — Integer
- `7678` 测试总时长（Total duration of test） — Integer
- `20139` 正确识别的字母数（Number of letters correctly identified） — Integer
- `20141` 首个未识别字母的位置（Position of first letter not identified） — Integer
- `4936` FI1：查看时长（FI1 : duration viewed） — Integer
- `4947` FI2：查看时长（FI2 : duration viewed） — Integer
- `4958` FI3：查看时长（FI3 : duration viewed） — Integer
- `4969` FI4：查看时长（FI4 : duration viewed） — Integer
- `4980` FI5：查看时长（FI5 : duration viewed） — Integer
- `4991` FI6：查看时长（FI6 : duration viewed） — Integer
- `5002` FI7：查看时长（FI7 : duration viewed） — Integer
- `5013` FI8：查看时长（FI8 : duration viewed） — Integer
- `5557` FI9：查看时长（FI9 : duration viewed） — Integer
- `5700` FI10：查看时长（FI10 : duration viewed） — Integer
- `5780` FI11：查看时长（FI11 : duration viewed） — Integer
- `5791` FI12：查看时长（FI12 : duration viewed） — Integer
- `5867` FI13：查看时长（FI13 : duration viewed） — Integer
- `10142` 显示的列数（试点）（Number of columns displayed (pilot)） — Integer
- `10143` 显示的行数（试点）（Number of rows displayed (pilot)） — Integer
- `10144` 完成灯光记忆测试用时（试点）（Time taken to complete lights test (pilot)） — Integer
- `10145` 显示的灯光图案（试点）（Pattern of lights displayed (pilot)） — Text
- `10146` 记忆中的灯光图案（试点）（Pattern of lights as remembered (pilot)） — Text
- `6333` 每道题作答用时（Duration spent answering each puzzle） — Integer
- `6373` 正确解出的题目数（Number of puzzles correctly solved） — Integer
- `6374` 查看的题目数（Number of puzzles viewed） — Integer
- `4250` 需记忆/回忆的数字位数（Number of digits to be memorised/recalled） — Integer
- `4251` 待记忆的目标数字（Target number to be memorised） — Text
- `4252` 待输入的目标数字（Target number to be entered） — Text
- `4253` 数字显示时长（Time number displayed for） — Integer
- `4254` 首次触键时间（Time first key touched） — Integer
- `4255` 最后触键时间（Time last key touched） — Integer
- `4256` 已用时间（Time elapsed） — Integer
- `4257` 按键历史（Keystroke history） — Text
- `4258` 参与者输入的数字（Number entered by participant） — Text
- `4260` 数字记忆测试的轮次（Round of numeric memory test） — Integer
- `4285` 完成测试用时（Time to complete test） — Integer
- `20197` 正确联想的词对数（Number of word pairs correctly associated） — Integer
- `396` 本轮显示的列数（Number of columns displayed in round） — Integer
- `397` 本轮显示的行数（Number of rows displayed in round） — Integer
- `398` 本轮正确匹配数（Number of correct matches in round） — Integer
- `399` 本轮错误匹配数（Number of incorrect matches in round） — Integer
- `6334` 屏幕布局（Screen layout） — Text
- `10133` 本轮显示的列数（试点）（Number of columns displayed in round (pilot)） — Integer
- `10134` 本轮显示的行数（试点）（Number of rows displayed in round (pilot)） — Integer
- `10136` 本轮正确匹配数（试点）（Number of correct matches in round (pilot)） — Integer
- `10137` 本轮错误匹配数（试点）（Number of incorrect matches in round (pilot)） — Integer
- `6317` 每轮选择用时（Duration of selection in each round） — Integer
- `6364` 词汇水平（Vocabulary level） — Continuous
- `6365` 词汇水平的不确定度（Uncertainty in vocabulary level） — Continuous
- `26302` 特定认知能力(AS)（Specific cognitive ability (AS)） — Continuous
- `26306` 反应延迟间隔（Response delay interval） — Integer
- `4286` 初始屏幕显示时间（Time when initial screen shown） — Time
- `4288` 回答用时（Time to answer） — Integer
- `4289` 退出屏幕时间（Time screen exited） — Time
- `4290` 屏幕显示时长（Duration screen displayed） — Integer
- `4291` 尝试次数（Number of attempts） — Integer
- `4295` 尝试历史（History of attempts） — Text
- `403` 按下匹配(snap)按钮的次数（Number of times snap-button pressed） — Integer
- `404` 每轮首次按下匹配按钮的时长（Duration to first press of snap-button in each round） — Integer
- `10141` 按下匹配按钮的次数（试点）（Number of times snap-button pressed (pilot)） — Integer
- `10147` 每轮首次按匹配按钮的时长（试点）（Duration to first press of snap-button in each round (pilot)） — Integer
- `20023` 正确识别匹配的平均用时（Mean time to correctly identify matches） — Integer
- `6313` 输入选择用时（Duration to entering selection） — Integer
- `6383` 尝试的题目数（Number of puzzles attempted） — Integer
- `21004` 正确解出的题目数（Number of puzzles correct） — Integer
- `6349` 遍历数字路径的总错误数（连线#1）（Total errors traversing numeric path (trail #1)） — Integer
- `6351` 遍历字母数字路径的总错误数（连线#2）（Total errors traversing alphanumeric path (trail #2)） — Integer
- `6770` 数字路径中选对前的错误数（连线#1）（Errors before selecting correct item in numeric path (trail #1)） — Integer
- `6771` 字母数字路径中选对前的错误数（连线#2）（Errors before selecting correct item in alphanumeric path (trail #2)） — Integer
- `6772` 数字路径中相邻两点的间隔（连线#1）（Interval between previous point and current one in numeric path (trail #1)） — Integer
- `6773` 字母数字路径中相邻两点的间隔（连线#2）（Interval between previous point and current one in alphanumeric path (trail #2)） — Integer
- `10609` 词语作答数组（试点）（Words answer array (pilot)） — Integer
