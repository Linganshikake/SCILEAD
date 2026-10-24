# 阶段 0：环境预检查

状态：**已有环境可复用；P0 等待确认**。当前只进行元数据、文件哈希、依赖和资源只读检查，没有运行 P1 服务回归、批量解析、模型抽取或 API。

已显式读取 Administrator 的 SSH 配置：`scilead-aliyun → root@123.56.138.148:22`，StrictHostKeyChecking=true。实际认证复用此前指定的凭据加载器，先核对已确认的 Ed25519 主机指纹，再认证；未读取或展示私钥，未在新文件保存密码/Token。隔离终端默认账户不同，已使用显式用户配置处理；没有修改 SSH config 或全局 Git 配置。

AxCell 固定提交 `f4648d8fee1aa8482d007a38828da9dc06630f0e`，本地 82 个源文件和远端对应文件全部哈希匹配。SCILEAD Git HEAD 为 `8bf74b0a830feb7035c6166dce3394dc344ae532`，21 个跟踪文件与 Git blob 一致（核对 Windows checkout CRLF）；官方源码/Prompt/Gold 均未修改。

| 依赖 | 当前版本 |
| --- | --- |
| Python | 3.7.1 |
| torch | 1.3.1+cpu |
| torchvision | 0.4.2+cpu |
| numpy | 1.18.1 |
| pandas | 0.25.3 |
| fastai | 1.0.55 |
| fastprogress | 0.1.21 |
| spacy | 2.2.3 |
| scispacy | 0.2.4 |
| docker | 4.1.0 |
| docker-compose | 1.25.5 |
| elasticsearch | 6.3.1 |
| elasticsearch-dsl | 6.3.1 |

环境位于 `/root/scilead/axcell/envs/axcell-original`，包版本清单与成功单篇结束时完全一致；`pip check` 返回 0：`No broken requirements found.`。无重新安装或升级；此前 7 个未固定传递依赖兼容版本继续保留，CPU wheel 例外不变。P0 不导入模型权重。

| 镜像 | 实际 digest |
| --- | --- |
| arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6 | sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e |
| docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1 | sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b |

Docker Engine 29.9.2 正常运行，两个固定镜像已存在。任务容器均停止。Elasticsearch 6.7.1 镜像、停止容器、3 GiB 限额及 127.0.0.1:9200 绑定保留；9200 当前未监听，与上轮正常停止状态一致。**本轮没有启动它，因此不能声称已重新验证服务就绪**；必要服务回归属于获批后的 P1。

模型、taxonomy、metrics、abbreviations 和 SentencePiece 词表共 7 个文件，本地与远端 SHA256 匹配既有清单；总文件字节数 322,457,425。这表示与已下载冻结文件相同，不把本地计算的 SHA256 冒充作者发布的校验值。官方 taxonomy 未替换为 SciLead Gold。

单篇成功输出和日志的 192 个冻结文件保持一致；此前脚本与解析产物的 46 个远端哈希也一致。`single_paper_error_baseline.json` 固定了两处原始错误：91.85 为 Recall 列却预测为 F1；4696 为实体数量却预测为分数。没有重新推理或人工修正。本阶段的只读复核不等于已经完成 P1。

未来沿用原版 `PaperExtractor`、`ResultsExtractor`，type threshold=0.5，结构过滤→confidence 0.8→paper BestResult→confidence 0.85，use_crf=False；只复用已验证的 Docker API 协商、资源封装和空进度条显示适配。

本阶段未发现需要修改系统配置、重新下载模型或增购云资源的依据。云实例原有运行费用继续存在；本阶段新增 GPT/API 费用为 0。详细证据：`remote_preflight.json`、`local_asset_checks.json`、`scilead_code_checks.json`、`dependency_snapshot.json`。
