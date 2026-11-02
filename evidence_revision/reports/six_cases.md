# 六例逐轮核验（人工审核 pending）

## S01
```json
{
  "family_id": "S01",
  "rules": [
    {
      "rule_id": "R1",
      "premises": [
        "valid_pass(小林)"
      ],
      "conclusion": "can_enter(小林)"
    },
    {
      "rule_id": "R2",
      "premises": [
        "authorized(小林)"
      ],
      "conclusion": "can_enter(小林)"
    }
  ],
  "source_records": [
    {
      "record_id": "E1",
      "source_id": "source_E1",
      "version": 1,
      "literal": "valid_pass(小林)",
      "root_ids": [
        "E1"
      ],
      "active": true
    }
  ],
  "events": [
    {
      "op": "retract",
      "record_id": "E1",
      "version": 1
    }
  ],
  "query": "can_enter(小林)",
  "policy": {
    "supported": "proceed",
    "refuted": "stop",
    "unknown": "seek_evidence",
    "conflict": "review"
  },
  "review_status": "pending"
}
```
第 0 轮：supported；动作 proceed；有效记录 E1；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}
第 1 轮：unknown；动作 seek_evidence；有效记录 ；证明 {"negative":[],"positive":[]}

## S02
```json
{
  "family_id": "S02",
  "rules": [
    {
      "rule_id": "R1",
      "premises": [
        "valid_pass(小林)"
      ],
      "conclusion": "can_enter(小林)"
    },
    {
      "rule_id": "R2",
      "premises": [
        "authorized(小林)"
      ],
      "conclusion": "can_enter(小林)"
    }
  ],
  "source_records": [
    {
      "record_id": "E1",
      "source_id": "source_E1",
      "version": 1,
      "literal": "valid_pass(小林)",
      "root_ids": [
        "E1"
      ],
      "active": true
    },
    {
      "record_id": "E2",
      "source_id": "source_E2",
      "version": 1,
      "literal": "authorized(小林)",
      "root_ids": [
        "E2"
      ],
      "active": true
    }
  ],
  "events": [
    {
      "op": "retract",
      "record_id": "E1",
      "version": 1
    }
  ],
  "query": "can_enter(小林)",
  "policy": {
    "supported": "proceed",
    "refuted": "stop",
    "unknown": "seek_evidence",
    "conflict": "review"
  },
  "review_status": "pending"
}
```
第 0 轮：supported；动作 proceed；有效记录 E1,E2；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]},{"records":["E2"],"roots":["E2"],"rules":["R2"]}]}
第 1 轮：supported；动作 proceed；有效记录 E2；证明 {"negative":[],"positive":[{"records":["E2"],"roots":["E2"],"rules":["R2"]}]}

## S03
```json
{
  "family_id": "S03",
  "rules": [
    {
      "rule_id": "R1",
      "premises": [
        "valid_pass(小林)"
      ],
      "conclusion": "can_enter(小林)"
    },
    {
      "rule_id": "R2",
      "premises": [
        "authorized(小林)"
      ],
      "conclusion": "can_enter(小林)"
    }
  ],
  "source_records": [
    {
      "record_id": "E1",
      "source_id": "source_E1",
      "version": 1,
      "literal": "valid_pass(小林)",
      "root_ids": [
        "E1"
      ],
      "active": true
    },
    {
      "record_id": "E3",
      "source_id": "source_E3",
      "version": 1,
      "literal": "blue_lamp(虚构设备)",
      "root_ids": [
        "E3"
      ],
      "active": true
    }
  ],
  "events": [
    {
      "op": "retract",
      "record_id": "E3",
      "version": 1
    }
  ],
  "query": "can_enter(小林)",
  "policy": {
    "supported": "proceed",
    "refuted": "stop",
    "unknown": "seek_evidence",
    "conflict": "review"
  },
  "review_status": "pending"
}
```
第 0 轮：supported；动作 proceed；有效记录 E1,E3；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}
第 1 轮：supported；动作 proceed；有效记录 E1；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}

## S04
```json
{
  "family_id": "S04",
  "rules": [
    {
      "rule_id": "R1",
      "premises": [
        "valid_pass(小林)"
      ],
      "conclusion": "can_enter(小林)"
    },
    {
      "rule_id": "R2",
      "premises": [
        "authorized(小林)"
      ],
      "conclusion": "can_enter(小林)"
    }
  ],
  "source_records": [
    {
      "record_id": "E1",
      "source_id": "source_E1",
      "version": 1,
      "literal": "valid_pass(小林)",
      "root_ids": [
        "E1"
      ],
      "active": true
    },
    {
      "record_id": "E4",
      "source_id": "source_E4",
      "version": 1,
      "literal": "not_can_enter(小林)",
      "root_ids": [
        "E4"
      ],
      "active": false
    }
  ],
  "events": [
    {
      "op": "retract",
      "record_id": "E1",
      "version": 1
    },
    {
      "op": "add",
      "record_id": "E4",
      "version": 1
    }
  ],
  "query": "can_enter(小林)",
  "policy": {
    "supported": "proceed",
    "refuted": "stop",
    "unknown": "seek_evidence",
    "conflict": "review"
  },
  "review_status": "pending"
}
```
第 0 轮：supported；动作 proceed；有效记录 E1；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}
第 1 轮：unknown；动作 seek_evidence；有效记录 ；证明 {"negative":[],"positive":[]}
第 2 轮：refuted；动作 stop；有效记录 E4；证明 {"negative":[{"records":["E4"],"roots":["E4"],"rules":[]}],"positive":[]}

## S05
```json
{
  "family_id": "S05",
  "rules": [
    {
      "rule_id": "R1",
      "premises": [
        "valid_pass(小林)"
      ],
      "conclusion": "can_enter(小林)"
    },
    {
      "rule_id": "R2",
      "premises": [
        "authorized(小林)"
      ],
      "conclusion": "can_enter(小林)"
    }
  ],
  "source_records": [
    {
      "record_id": "E1",
      "source_id": "source_E1",
      "version": 1,
      "literal": "valid_pass(小林)",
      "root_ids": [
        "E1"
      ],
      "active": true
    },
    {
      "record_id": "E4",
      "source_id": "source_E4",
      "version": 1,
      "literal": "not_can_enter(小林)",
      "root_ids": [
        "E4"
      ],
      "active": false
    }
  ],
  "events": [
    {
      "op": "add",
      "record_id": "E4",
      "version": 1
    }
  ],
  "query": "can_enter(小林)",
  "policy": {
    "supported": "proceed",
    "refuted": "stop",
    "unknown": "seek_evidence",
    "conflict": "review"
  },
  "review_status": "pending"
}
```
第 0 轮：supported；动作 proceed；有效记录 E1；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}
第 1 轮：conflict；动作 review；有效记录 E1,E4；证明 {"negative":[{"records":["E4"],"roots":["E4"],"rules":[]}],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}

## S06
```json
{
  "family_id": "S06",
  "rules": [
    {
      "rule_id": "R1",
      "premises": [
        "valid_pass(小林)"
      ],
      "conclusion": "can_enter(小林)"
    },
    {
      "rule_id": "R2",
      "premises": [
        "authorized(小林)"
      ],
      "conclusion": "can_enter(小林)"
    }
  ],
  "source_records": [
    {
      "record_id": "E1",
      "source_id": "source_E1",
      "version": 1,
      "literal": "valid_pass(小林)",
      "root_ids": [
        "E1"
      ],
      "active": true
    }
  ],
  "events": [
    {
      "op": "retract",
      "record_id": "E1",
      "version": 1
    },
    {
      "op": "restore",
      "record_id": "E1",
      "version": 1
    }
  ],
  "query": "can_enter(小林)",
  "policy": {
    "supported": "proceed",
    "refuted": "stop",
    "unknown": "seek_evidence",
    "conflict": "review"
  },
  "review_status": "pending"
}
```
第 0 轮：supported；动作 proceed；有效记录 E1；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}
第 1 轮：unknown；动作 seek_evidence；有效记录 ；证明 {"negative":[],"positive":[]}
第 2 轮：supported；动作 proceed；有效记录 E1；证明 {"negative":[],"positive":[{"records":["E1"],"roots":["E1"],"rules":["R1"]}]}
