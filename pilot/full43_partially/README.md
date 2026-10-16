# 复现和断点恢复

工作目录为本文件所在 full43_partially；使用既有 scilead Python，不安装依赖。prepare.py 是一次性准备，已有冻结清单时拒绝覆盖。

```powershell
$env:PYTHONHASHSEED='0'
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\run_partially.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\evaluate.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\verify_run.py
& 'D:\miniconda3\envs\scilead\python.exe' -B -X utf8 .\write_report.py
```

成功阶段直接跳过。中断阶段从原始输入重新按序执行官方 main，在同一位置重放 COMPLETE 响应，并核对原始 Prompt、候选序列化和全部状态事件；不会把相同名称在不同位置当作缓存。已尝试但未COMPLETE的请求禁止自动重发，需要明确人工处理/授权，不可删掉失败记录冒充未调用。

实际HTTP请求由ChatOpenAI/OpenAI SDK完成，沿用已验证的参数与脱敏日志机制，SDK max_retries=0，连接20秒、读取180秒。只读取此前用户指定的实验凭证，绝不打印密钥或Header。

阶段一原版 main 直接运行，sys.settrace只观察并记录每个字段完成后的实际状态，不修改locals或候选；阶段二同样执行原版 main并重新读取阶段一文件。仅模型初始化桥接固定GPT-4.1及无输出上限参数；官方算法与Prompt没有修改。

verify_run.py仅重放已保存响应，不读取凭证、不调用网络；evaluate.py复用官方TDMR脚本和上一阶段审计后的排行榜入口，两个Gold范围独立评价。

report.md：总报告；comparison_with_fully.md：三分支及表格阶段歧义；masking/：原版掩蔽；stage1/与stage2/：独立输出、请求和checkpoint；evaluation/：逐篇指标和配对记录；leaderboard_evaluation/：全27及Masked榜；freeze_before.json和verification.json：冻结核验。
