# 指标定义与源码审计

输入：`D:\C++\SCILEAD\pilot\full43_uncapped\merged\normalized_output.json`；Gold：`C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\leaderboards.json`。官方 Commit：`8bf74b0a830feb7035c6166dce3394dc344ae532`。论文第 5.2 节及公式 (1) 已与 PDF 第 6 页图像核对，Table 5 已与第 8 页核对。

## 未修改的官方实现

通过 SimpleNamespace 提供 gold_leaderboards_file、masked_leaderboards_file=""、normalized_output_file、eval_results_file、eval_values_file，直接调用 leaderboard_eval.main(args)。argparse 定义 normalized_tdm_output_path，而 main 访问 normalized_output_file；README 的多个 *_path 参数还与 argparse 的 *_file 不同。独立入口只桥接参数，未替换数学函数。

构建函数先创建全部 Gold TDM 的空字典，再精确匹配标准化的 Task/Dataset/Metric。未匹配 27 榜的 TDM 不入榜；没有按预测榜至少 3 篇再过滤。每个 (TDM, paper) 只保留输入顺序中最后一条可转换的 Result，不取最大值或最优值；后来的不可转换值跳过，不抹去先前有效值。

PC = Gold 论文 ID 与预测论文 ID 交集大小 / Gold 论文数；明确要求论文 ID 命中。RC = 预测榜中数值属于任意 Gold 数值集合的条数 / Gold 记录数，使用 float 精确相等，不要求命中的数值属于同一论文，不是 TDMR 脚本中的字符串包含规则。重复预测数值按预测论文逐个计数，理论上 RC 可超过 1；本批实际所有官方分数均在 [0,1]，没有裁剪。

本批数值命中但对应论文结果不匹配的项为 0；额外诊断的同论文同数值覆盖率为 31.7989%，恰好等于本批官方 RC，但不据此混淆二者定义。

## 官方数值转换（未扩充规则）

Gold：所有小于 1 的值直接乘 100，不区分 Metric，转换发生在内存副本，磁盘 Gold 不变。预测：先截掉第一个 ± 及其后内容，再截掉第一个 % 及其后内容，再尝试 float；失败即跳过。对于源码枚举的 25 种指标，数值 <1 再乘 100，包括 AVG、Accuracy、BLEU、F1、ROGUE-*、TER 等；Perplexity 不在该缩放名单。条件是 <1，数值 1 不缩放，也没有显式非负下界检查。全部清洗与缩放实际调用原始构建函数，没有另写数值纠正规则。

例如 0.81 ± 0.02 → 81，82% → 82；87.95 (± 0.13) 被截为 87.95 (，无法 float；21.4 (0.5)、44.16/21.56/41.30 也无法转换。不会主动剥括号、拆复合结果、补数值或校正百分数。实际遇到的不可转换、覆盖记录见 tuple_conversion_audit.json。

## 官方 RBO 与论文 AO 的区别

当前 rbo 包版本 0.1.3，签名 `(self, k: Optional[float] = None, p: float = 1.0, ext: bool = False) -> float`。官方先对结果数值去重并排序，再调用 rbo()；默认 p=1 表示均匀平均重叠。论文公式同样均匀平均，但元素是论文 ID，而非数值，所以不能把原始 RBO 重命名为论文 AO。安装库方法源码已保存于 reference/installed_rbo_method.py.txt。

## LR 两种公开口径

精确标准 TDM 出现在模型标准化行中：22/27 = 81.4815%，不要求数值可用。精确标准 TDM 且原始转换后包含至少一条有限数值结果：20/27 = 74.0741%。不能用预建字典键数 27/27。前者更直接对应“识别 TDM”，后者明确衡量可排序的非空榜；论文对此不够具体，因此不隐去任一口径。

## AO 新增只读实现

`A_d = |set(G[:d]) ∩ set(M[:d])| / d`；`AO = sum(A_d) / k`，`k=min(len(G),len(M))`。G/M 元素均为论文 ID，使用官方转换后的结果排序；Perplexity、TER 升序，其余降序。本批 27 榜没有 Perplexity 或 TER，但方向分支已有独立测试。

同分按论文 ID Unicode 字典序升序，排名采用连续序号；不去重同分论文，不填补缺失 Gold 论文，不丢弃预测中的额外论文。k=0 时 AO=0；Macro 包括全部 27 个 Gold 榜。双方空榜的辅助函数也返回 0，但本批 Gold 均非空。所有值必须有限，否则暂停 AO 而不静默过滤。

只对非空榜平均的 AO=62.4375% 仅作诊断，不作为主分数。主 Macro AO=46.2500%。每层前缀、交集、A_d 保存在 gold_vs_predicted.json。

公式有手算相同榜、逆序、短榜、不相交和空榜测试，另验证并列规则、升降序、官方清洗、无效字符串不覆盖旧值、RC 不要求论文 ID。实际 27 榜 AO 还与 rbo(p=1) 在论文 ID 列表上的计算交叉核验；这是公式验证，不是用数值版官方 RBO 代替 AO。

## 数据版本与边界

Gold Leaderboard 的 27 个唯一键、140 条记录与 Gold TDMR 完全一致，无重复 JSON 论文键，无缺失输入论文。每榜 3–14 篇。完整 TDMR 有 43 篇 / 295 条 / 141 唯一 TDM，33 个至少三篇分组；不等于论文中的 138 / 27。沿用提供的 27 榜，保留额外 6 个分组清单，不根据模型分数筛选或修改。

## 工程问题

首次两次导入被只读边界阻止：filelock 尝试写系统临时目录，随后 Windows platform 探测打开 NUL 设备。已把临时目录定向到本次独立目录，并允许无文件产出的 NUL 设备；原始两份堆栈保留在 official/evaluation_failed_import_*.txt。没有修改依赖或官方源码，数学函数随后实际执行成功。所有评价进程禁用网络、拒绝读取敏感配置、禁止向独立目录外写文件。仅为查阅来源下载一次公开 ACL 论文 PDF，不涉及 LLM API。