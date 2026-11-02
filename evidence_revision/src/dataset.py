import copy
from logic import *

BASE = '你在虚构实验中判断 can_enter(小林)。只按给定正向规则推理，不使用常识。输出且仅输出 JSON，字段 state（supported/refuted/unknown/conflict）、positive_evidence（记录ID列表）、negative_evidence（记录ID列表）、rule_ids（规则ID列表）、action。无需长推理。旧助手回答不是证据。'
STRONG = '撤回不推出否定；未知与反证不同。检查所有独立支持，撤回一条不删除另一条。正反同时有效必须报 conflict，不从冲突推出其他结论。AND 要求全部前提，多个规则可替代。恢复仅作用于指定版本。'
QUERY = 'can_enter(小林)'
def record(i, lit, active=True, source=None, version=1, roots=None):
    return dict(record_id=i,source_id=source or 'source_'+i,version=version,literal=lit,root_ids=roots or [i],active=active)
def event(op, i, version=1): return dict(op=op,record_id=i,version=version)
def seeds():
    rules=[dict(rule_id='R1',premises=['valid_pass(小林)'],conclusion=QUERY),dict(rule_id='R2',premises=['authorized(小林)'],conclusion=QUERY)]
    out=[]
    for i in range(1,7):
        rs=[record('E1','valid_pass(小林)')]
        es=[event('retract','E1')]
        if i==2: rs.append(record('E2','authorized(小林)'))
        if i==3:
            rs.append(record('E3','blue_lamp(虚构设备)')); es=[event('retract','E3')]
        if i in (4,5):
            rs.append(record('E4',opposite(QUERY),False)); es=([event('retract','E1')] if i==4 else [])+[event('add','E4')]
        if i==6: es += [event('restore','E1')]
        out.append(dict(family_id=f'S{i:02}',rules=copy.deepcopy(rules),source_records=rs,events=es,query=QUERY,policy=ACTIONS.copy(),review_status='pending'))
    return out

def annotate(seed, records, events):
    validate(records,seed['rules'])
    rounds=[]
    for n in range(len(events)+1):
        active=replay(records,events[:n]); facts=closure(active,seed['rules']); s,p=oracle_state(active,seed['rules'],seed['query'])
        assert s==state(facts,seed['query']), 'independent label disagreement'
        rounds.append(dict(active_records=active,closure=sorted(facts),gold_state=s,gold_action=seed['policy'][s],valid_proofs=p))
    end=rounds[-1]
    canon=canonical(end['active_records'],seed['rules'],seed['query'],seed['policy'])
    return dict(rounds=rounds,gold_state=end['gold_state'],gold_action=end['gold_action'],valid_proofs=end['valid_proofs'],canonical_state=canon,state_hash=digest(canon))

def render(sample, condition, strong=False):
    header=dict(rules=sample['rules'],query=sample['query'],policy=sample['policy'])
    messages=[dict(role='system',content=BASE+('\n'+STRONG if strong else ''))]
    if condition=='A':
        messages.append(dict(role='user',content=stable({**header,'current_records':sample['rounds'][-1]['active_records']})))
    else:
        messages.append(dict(role='user',content=stable({**header,'initial_records':sample['source_records']})))
        if condition=='C': messages.append(dict(role='assistant',content=sample['old_answer']))
        messages.append(dict(role='user',content=stable(dict(events=sample['events'],question='请依据更新后的有效记录重新判断。'))))
    # deterministic merge for APIs forbidding adjacent user messages
    merged=[]
    for m in messages:
        if merged and m['role']==merged[-1]['role']=='user': merged[-1]['content']+='\n<USER_TURN_BOUNDARY>\n'+m['content']
        else: merged.append(m.copy())
    return merged

def generate():
    rows=[]
    for seed in seeds():
        for mode in ('legal_path','assistant_only'):
            pairs=[]
            for stance in ('supported','refuted'):
                rs=copy.deepcopy(seed['source_records'])
                # Start with old-only evidence, then retire it and replay the seed from scratch.
                initial={r['record_id']:r['active'] for r in rs}
                for r in rs:r['active']=False
                oldlit=QUERY if (mode=='assistant_only' or stance=='supported') else opposite(QUERY)
                rs.append(record('OLD',oldlit))
                es=[event('retract','OLD')]+[event('add',i) for i,on in initial.items() if on]+copy.deepcopy(seed['events'])
                ans=stable(dict(state=stance,positive_evidence=[],negative_evidence=[],rule_ids=[],action=ACTIONS[stance]))
                sample={**copy.deepcopy(seed),**annotate(seed,rs,es), 'source_records':rs,'events':es,'old_answer':ans,'old_answer_lengths':dict(characters=len(ans),utf8_bytes=len(ans.encode()),tokens=None),'history_id':stance,'pair_group':seed['family_id']+'/'+mode,'pair_type':mode,'history_mode':'injected','graph_id':'entry_or_v1','domain':'fictional_access','template_id':'structured_zh_v1','scenario_type':seed['family_id'],'split':'debug','schema_version':'1.0'}
                pairs.append(sample)
            assert pairs[0]['canonical_state']==pairs[1]['canonical_state']
            assert pairs[0]['state_hash']==pairs[1]['state_hash']
            if mode=='assistant_only':
                assert pairs[0]['source_records']==pairs[1]['source_records'] and pairs[0]['events']==pairs[1]['events']
            for sample in pairs:
                for condition in 'ABC':
                    rows.append({**sample,'condition':condition,'sample_id':sample['pair_group']+'/'+sample['history_id']+'/'+condition,'messages':render(sample,condition)})
    return rows

def export(rows,strong=False):
    # Only whitelist ID and messages; never serialize the annotated row into a prompt.
    return [dict(sample_id=r['sample_id'],messages=render(r,r['condition'],strong)) for r in rows]
