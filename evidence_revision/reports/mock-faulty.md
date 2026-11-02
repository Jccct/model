# 自动报告 mock-faulty

后端：mock-faulty
逻辑单元 72；实际请求 35；缓存 37

|条件|状态正确|Macro F1|配对全对|格式错误|
|---|---|---|---|---|
|A|4/24|0.0714|2/12|0/24|
|B|4/24|0.0714|2/12|0/24|
|C|0/24|0.0000|0/12|24/24|

全部错误（不挑选）：
```json
[
  {
    "sample_id": "S01/legal_path/supported/C",
    "gold": "unknown",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S01/legal_path/refuted/C",
    "gold": "unknown",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S01/assistant_only/supported/C",
    "gold": "unknown",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S01/assistant_only/refuted/C",
    "gold": "unknown",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S02/legal_path/supported/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S02/legal_path/supported/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S02/legal_path/supported/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S02/legal_path/refuted/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S02/legal_path/refuted/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S02/legal_path/refuted/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S02/assistant_only/supported/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S02/assistant_only/supported/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S02/assistant_only/supported/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S02/assistant_only/refuted/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S02/assistant_only/refuted/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S02/assistant_only/refuted/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S03/legal_path/supported/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S03/legal_path/supported/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S03/legal_path/supported/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S03/legal_path/refuted/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S03/legal_path/refuted/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S03/legal_path/refuted/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S03/assistant_only/supported/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S03/assistant_only/supported/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S03/assistant_only/supported/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S03/assistant_only/refuted/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S03/assistant_only/refuted/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S03/assistant_only/refuted/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S04/legal_path/supported/A",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S04/legal_path/supported/B",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S04/legal_path/supported/C",
    "gold": "refuted",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S04/legal_path/refuted/A",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S04/legal_path/refuted/B",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S04/legal_path/refuted/C",
    "gold": "refuted",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S04/assistant_only/supported/A",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S04/assistant_only/supported/B",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S04/assistant_only/supported/C",
    "gold": "refuted",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S04/assistant_only/refuted/A",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S04/assistant_only/refuted/B",
    "gold": "refuted",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S04/assistant_only/refuted/C",
    "gold": "refuted",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S05/legal_path/supported/A",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S05/legal_path/supported/B",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "conflict_missed"
  },
  {
    "sample_id": "S05/legal_path/supported/C",
    "gold": "conflict",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S05/legal_path/refuted/A",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S05/legal_path/refuted/B",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "conflict_missed"
  },
  {
    "sample_id": "S05/legal_path/refuted/C",
    "gold": "conflict",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S05/assistant_only/supported/A",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S05/assistant_only/supported/B",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "conflict_missed"
  },
  {
    "sample_id": "S05/assistant_only/supported/C",
    "gold": "conflict",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S05/assistant_only/refuted/A",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S05/assistant_only/refuted/B",
    "gold": "conflict",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "conflict_missed"
  },
  {
    "sample_id": "S05/assistant_only/refuted/C",
    "gold": "conflict",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S06/legal_path/supported/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S06/legal_path/supported/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S06/legal_path/supported/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S06/legal_path/refuted/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S06/legal_path/refuted/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S06/legal_path/refuted/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S06/assistant_only/supported/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S06/assistant_only/supported/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S06/assistant_only/supported/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  },
  {
    "sample_id": "S06/assistant_only/refuted/A",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "current_evidence_failure"
  },
  {
    "sample_id": "S06/assistant_only/refuted/B",
    "gold": "supported",
    "prediction": {
      "action": "seek_evidence",
      "negative_evidence": [],
      "positive_evidence": [],
      "rule_ids": [],
      "state": "unknown"
    },
    "category": "over_unknown"
  },
  {
    "sample_id": "S06/assistant_only/refuted/C",
    "gold": "supported",
    "prediction": null,
    "category": "invalid_output"
  }
]
```
完整轨迹未运行；模型实验与 H1/H2/H3 结论 TBD。
