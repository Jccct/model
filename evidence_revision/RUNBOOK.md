# 运行手册

在现有隔离环境 `/workspace/model/evidence_revision` 工作；不创建 worktree，不修改源 Word。Python 3.12 标准库已具备；没有依赖安装命令或后台服务需要重启。

离线从零运行顺序见 README。附加检查：

```bash
python3 src/cli.py run-eval --strong --run runs/mock-strong.jsonl
python3 src/cli.py run-eval --backend mock-faulty --run runs/mock-faulty.jsonl
python3 src/cli.py score --run runs/mock-faulty.jsonl
python3 src/cli.py report --run runs/mock-faulty.jsonl
```

同一 run 命令再次执行不新增结果。数据、提示、代码或解码配置变化时拒绝混写，使用新路径。所有日志可重新 score/report；不覆盖用户已有结果。有限重试策略为 0 次，网络失败和格式失败原样保存；要复测用新 run，保留旧结果。不会自动清除失败或只保留较好答案。

真实模型命令（尚未执行）：先配置支持 OpenAI Chat Completions 请求结构的 HTTPS 服务，将密钥安全注入 `MODEL_API_KEY`，模型 ID、精确 revision 和完整 endpoint 由所选服务提供。不要在聊天或命令字面量填密钥。平台注入的代理凭据可照常使用；unset 不能单独证明没有授权。目前配置元数据确实没有绑定，亦没有服务/预算。

```bash
cd /workspace/model/evidence_revision
# 非秘密选择器：先设置 MODEL_ID、MODEL_REVISION、MODEL_ENDPOINT
python3 src/cli.py run-eval --backend api --model "$MODEL_ID" --revision "$MODEL_REVISION" --endpoint "$MODEL_ENDPOINT" --dry-run
# 只有获得该服务对应请求/token预算后运行；以下上限须在授权范围内。
python3 src/cli.py run-eval --backend api --model "$MODEL_ID" --revision "$MODEL_REVISION" --endpoint "$MODEL_ENDPOINT" --max-requests 72 --max-tokens 2000000 --run runs/real-ordinary-001.jsonl
python3 src/cli.py report --run runs/real-ordinary-001.jsonl
python3 src/cli.py run-eval --backend api --model "$MODEL_ID" --revision "$MODEL_REVISION" --endpoint "$MODEL_ENDPOINT" --strong --max-requests 72 --max-tokens 2000000 --run runs/real-strong-001.jsonl
python3 src/cli.py report --run runs/real-strong-001.jsonl
```

预算是每个 run 的上限，不代表已经批准。dry-run 不读取密钥、不调用模型；UTF-8 字节数加每请求 256 输出 allowance 是保守估计，不是实测 tokens。真实 usage 以服务返回为准；没有 usage 记 null。服务返回的精确 model/revision 在 raw_response 中可核对；调用前应确认 MODEL_REVISION 对应不可变版本而不是擅填字符串。当前适配器不实现本地 transformers/vLLM、计费货币限额、tokenizer 长度实测或模型自生成历史。若服务不兼容 seed/temperature/max_tokens，先记录适配版本，不能偷偷改已冻结配置。遇到上下文超限不截断样本，应记录失败。

网络需要保留 HTTPS 代理和 TLS 校验，按服务域名增加环境设置，不绕过策略。文献访问可额外需要 aclanthology.org、arxiv.org、doi.org、dekleer.org、openreview.net、研究稿托管站；先核验实际需求，不替换未知 allowlist。

训练未实现也未启动。M4 证据与资源确认前，没有可以执行的训练命令；不提供伪训练入口。

## 本轮新增：4090本地推理与连续轨迹（不训练）

`src/gpu_eval.py` 支持已有本地模型目录，要求CUDA，禁用隐式下载、远程自定义代码、输入截断和CPU回退。记录模型文件SHA256清单、GPU型号/显存、实际token与峰值显存。旧版API入口仍保留。本地后端尚未在CUDA设备实测，不能宣称4090兼容性已验证。

在实验室机器已安装兼容的 PyTorch/CUDA 和 Transformers、且已有模型后，从整个 evidence_revision 目录运行：

```bash
nvidia-smi
python3 -c 'import torch, transformers; print(torch.__version__, transformers.__version__); print(torch.cuda.is_available())'
# MODEL_DIR为已有instruct模型目录，MODEL_REVISION为其精确来源版本，不是密钥。
python3 src/gpu_eval.py --model-path "$MODEL_DIR" --revision "$MODEL_REVISION" --max-calls 100 --out runs/lab4090-ordinary-001.jsonl
python3 src/gpu_eval.py --model-path "$MODEL_DIR" --revision "$MODEL_REVISION" --strong --max-calls 100 --out runs/lab4090-strong-001.jsonl
```

每种提示含72终点逻辑单元和2条×4轮连续查询，共80逻辑单元；重复请求缓存后，本轮mock实际43次/提示。真实计数取决于模型自己的轨迹回答，不预先写成测量值。生成逐轮保留原始输出及gold评分；下一轮只带自己的输出，不注入gold。每run上限100次前向生成；不代表GPU耗时预算已实测。程序只推理，没有训练入口。

本地依赖安装与CUDA/模型加载步骤未在当前无GPU环境测试，不提供伪称验证过的pip版本组合。连接实验室机器后先检查现有依赖/模型和24GB显存的实际可用量，再决定是否需安装或量化。

离线验证新增入口：

```bash
python3 src/gpu_eval.py --mock --out runs/continuation-v2-ordinary.jsonl
python3 src/gpu_eval.py --mock --strong --out runs/continuation-v2-strong.jsonl
python3 src/m3_candidates.py
python3 src/cli.py validate
```

M3候选输出位于data/m3-candidates-v1，独立于原六例与旧结果；尚未接入旧版cli的generate/export，因此不要用旧版generate声称重新生成该候选集。30家族审核清单已随机固定，审核状态pending。
