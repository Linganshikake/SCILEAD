# Cold Start 三轮实验与恢复

官方仓库只读。当前目录是唯一新实验写入区。输入为 full43_uncapped/merged/output.json；每轮独立从三个空集合开始。排序种子是 None、字符串 "0"、字符串 "42"；模型 seed 是整数 0。

执行：PowerShell 中设置 `$env:PYTHONHASHSEED='0'`，使用 `D:\miniconda3\envs\scilead\python.exe -B -X utf8 D:\C++\SCILEAD\pilot\full43_cold_start\launch.py`。

launch.py 顺序运行三轮，每轮两个官方标准化 main、评测及离线重放验证。完成的阶段直接跳过。未完成阶段从头重放已保存的**相同位置**响应，核对原始 Prompt、候选集合及事件后才继续；不是按名称缓存，不跨轮复用回答。

每个真实请求在 stage1/api_calls 或 stage2/api_calls 中保存 expected、attempt、实际 request、原始 response、state。成功响应先落盘，再更新候选及 checkpoint。SDK max_retries=0；有 attempt 但状态非 COMPLETE 时禁止自动补发。失败/超时/截断必须人工排查，不得当作 null 后继续。有限的 Windows 文件写入重试只重写同一 payload，不重试 API。

`status.py` 是只读进度查询。全部三轮完成且验证通过后运行 `finalize.py` 生成报告和三轮均值/标准差，不允许使用缺失轮的 0 分或仅成功轮平均代替三轮结果。

evaluation/all27 与 evaluation/masked10 使用同一已审计的评测代码。Masked 10 来自 Partially 的原文件，不使用 Cold Start 自动生成的 27 榜文件。ETM/IIM 仅是辅助诊断。主要结果对每轮榜单 Macro 分数再取三轮均值；主标准差 ddof=1，另保存 ddof=0，作者 ddof 尚未确认。

请求不传入客户端输出 Token 上限，与作者两个阶段的默认上限 15/100 有差异。密钥仅由适配器从已授权配置加载，不保存或输出。实际账单以中转站为准。

不要再次运行 bootstrap.py、prepare.py 或向历史实验目录写入。测试和 replay_validation 的请求文件是模拟/复放记录，不计入真实调用统计。
