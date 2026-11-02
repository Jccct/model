# 证据撤回 M0–M2 离线复现包

本目录独立于原始 Word 文件。Python 3.12 标准库即可运行，无须安装包。只做离线语义与工程验证，未训练、未调用真实模型。先阅读 [阶段报告](reports/M0-M2.md)、[六例核验表](reports/six_cases.md)、[运行手册](RUNBOOK.md)。

```bash
cd /workspace/model/evidence_revision
python3 src/cli.py validate
python3 src/cli.py generate
python3 src/cli.py export-inputs
python3 src/cli.py export-inputs --strong
python3 src/cli.py run-eval --dry-run
python3 src/cli.py run-eval --run runs/mock-ordinary.jsonl
python3 src/cli.py report --run runs/mock-ordinary.jsonl
```

实现：`src/logic.py` 记录重放、前向闭包、独立后向证明、规范化；`src/dataset.py` 六例、两种配对、A/B/C 白名单输入；`src/evaluation.py` mock/HTTPS API、预算、日志与评分；`src/cli.py` 六个入口；`tests/test_system.py` 语义与端到端验收。

每提示设置：6 家族 × 2 配对类型 × 2 历史 × 3 条件 = 72 逻辑单元。每个配对类型独立有 36 单元，不能当作 12 个独立家族。所有样本是 debug split，人工审核 pending；没有训练集或正式测试集。当前历史均为 injected；legal_path 的旧判断与早期证据一致，但也不是模型自生成旧判断。

mock-oracle 直接使用隐藏标签构造输出，只验证管线；mock-faulty 故意输出错误。真实 API 仅接收导出的 messages，收不到隐藏标签。日志记录完整请求、响应、缓存键、配置与代码/数据 hash；不记录鉴权头。API 格式失败与网络失败分别统计。不重试挑答案；失败行保留，重跑配置需要新日志名。完全相同配置的重启跳过已有 sample_id。

当前只做终点模型评测；`data/fixed_trajectories.jsonl` 是独立核验过的轨迹标准答案，不是模型连续交互结果。完整轨迹成功率 N/A。数据是六个人工起草种子，不能据此估计泛化或标签平衡；四状态分布不均，Macro F1 与逐类召回同时看。结构化中文输入尚非自然语言泛化集。

两份源文档版权与许可未另行授予，不发布数据或文档。没有下载外部模型/数据；将来必须记录相应许可、模型精确 revision、tokenizer 与资源实测。没有引用外部工作来宣称创新。
