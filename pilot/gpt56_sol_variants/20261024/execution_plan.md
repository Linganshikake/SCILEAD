# GPT-5.6 Sol 原版标准化扩展

授权：用户要求执行 GPT-5.6 Sol Partially、Cold Start，并补充 Fully + CS。复用43篇335条已完成抽取；不重新Extraction、不重做RAG、不启动Mixtral。

1. 核对冻结输入、源码、Gold、历史论文顺序和接口配置。
2. CS使用原版模型/阈值离线执行；Partially使用官方两阶段main；Cold Start使用官方两阶段main和三种历史论文顺序。
3. 仅独立接口适配层改用A2已验证的gpt-5.6-sol参数：reasoning_effort=medium,max_completion_tokens=32768,stream=false；不添加temperature/seed/tools等字段。方法内部masking_seed=0/PYTHONHASHSEED=0。
4. 请求前完成离线语义/断点恢复/失败不重发测试；实际逐字段串行，无跨位置缓存。失败状态持久化后暂停对应运行，不自动重试。
5. 原版tuple/leaderboard评价与辅助指标分开，报告全部IIM、ETM、PC/RC/RBO/LR/AO；Cold Start三轮均值及标准差。
6. 核对冻结文件不变，保存本轮实际请求数与Token用量，停止于本任务。

Ruling: 在独立实验目录执行，不改官方git仓库或发布仓库；无需创建源码worktree。
Ruling: GPT56恢复版合并JSON将两篇恢复论文放在末尾。为保持此前Partially/Cold Start比较的论文顺序，新建输入副本按冻结GPT4.1原始论文顺序排列；每篇记录、字段顺序、证据和内容完全不变。原合并文件保持不变。
Ruling: 原版gpt4-turbo-128k仅作为官方消息/比较分支标识保留，实际HTTP模型只能为gpt-5.6-sol。

进度：输入43/335已核实；CS独立执行；Partially/ColdStart适配准备中。正式API尚未启动。
