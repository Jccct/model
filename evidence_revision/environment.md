# M0 环境审计

2026-11-02（用户时区 Asia/Shanghai）。仓库初始本地 a5489b6，仅 README；远程已更新为 2738be91a7b3ce93163e1e556b797bcd16ad2de3，干净工作区后采用 ff-only 同步两份 Word。没有 AGENTS.md 或既有源码/结果。改动仅在新 evidence_revision 子目录。

实测 Python 3.12.14、Git 2.52.0、Node v24.19.0；本实现仅用 Python 标准库。内存 33GiB、磁盘可用约60GiB；不据此推定GPU资源。没有 nvidia-smi、/dev/nvidia*；torch、transformers、vllm、pytest未安装；/opt、/workspace 无 safetensors，默认HF缓存不存在。未发现可直接使用的模型。

平台当前元数据：running/connected，HTTP restricted/enforced，package_managers preset，无 secret/runtime_variable/outbound_identity 绑定。检查常用模型变量仅记录存在状态；OPENAI_API_KEY/ANTHROPIC_API_KEY/HF_TOKEN/MODEL_PATH 均 unset。没有API endpoint或已授权付费预算。未尝试交互式登录，也未索取GitHub token；原生 Git 经平台代理读取与 fetch 已成功。

普通沙箱下代理连接失败；为 Git 只读读取使用受支持的沙箱执行权限后成功，不能把最初错误写为GitHub认证缺失。三个文献公开页（Belief-R、Grounded Continuation、NAQD）实际访问均 network unavailable；根因未获足够证据，不声称全文不存在。

无需依赖安装/后台服务，未写环境安装或启动草稿。本轮无模型下载、无付费调用、无训练。未来真实运行需服务、精确模型版本、凭据绑定和明确预算；未来本地运行需另配置模型工具链和设备并实测。
