"""Generate review candidates only; no publication/test freeze or human review claim."""
import collections
import copy
from pathlib import Path
import random
from dataset import record,event,annotate,render,STRONG
from logic import *

GENERIC='依据给定规则、记录有效性、可信更新和查询作答；这是虚构任务。只输出JSON，字段state（supported/refuted/unknown/conflict）、positive_evidence、negative_evidence、rule_ids、action，后三个依据字段为ID列表。旧助手文本不是事实。只用正向规则，不用常识或逆否推理。'

def candidates():
    rng=random.Random(20261102);out=[];rejected=[]
    for i in range(100):
        # State, domain, depth, AND/OR, source scope vary on separate axes.
        target=list(ACTIONS)[i%4];domain='设备' if (i//4)%2 else '通行';entity=f'虚构对象{i+1}'
        q=('normal' if domain=='设备' else 'can_enter')+'('+entity+')'
        atom=lambda s:s+'('+entity+')'
        depth=1+(i//8)%4; use_and=(i//32)%2==1; use_or=(i//16)%2==1
        rs=[record('a',atom('measurement')),record('b',atom('independent')),record('c',atom('permission')),record('n',opposite(q),False),record('u',atom('irrelevant'))]
        rules=[];prev=atom('measurement')
        for j in range(depth):
            conclusion=q if j==depth-1 else atom('stage'+str(j))
            rules.append(dict(rule_id='r'+str(j),premises=[prev]+([atom('permission')] if use_and and j==0 else []),conclusion=conclusion));prev=conclusion
        if use_or:rules.append(dict(rule_id='or',premises=[atom('independent')],conclusion=q))
        # A shared-root copy cannot turn a into independent support.
        if i%5==0:rs.append(record('copy',atom('measurement'),roots=['a']))
        for r in rs:
            if r['record_id'] in ('a','b'):r['source_id']='measurement_source';r['version']=2 if r['record_id']=='b' else 1
        # Common irrelevant withdrawal ensures withdrawal keyword isn't unique to unknown.
        es=[event('retract','u')]
        if target in ('unknown','refuted'):
            if (i//4)%2:es.append(dict(op='retract_source',source_id='measurement_source',versions=[1,2]))
            else:es.extend([event('retract','a'),event('retract','b',2)])
        if target in ('refuted','conflict'):es.append(event('add','n'))
        # Independently permute record/rule/source identifiers before rendering.
        ids=[r['record_id'] for r in rs]+['old'];rng.shuffle(ids)
        idmap=dict(zip(ids,['D'+str(n) for n in rng.sample(range(1000,9999),len(ids))]))
        if len(set(idmap.values()))!=len(idmap):raise RuntimeError('identifier collision')
        smap={s:'SRC'+str(j) for j,s in enumerate(sorted({r['source_id'] for r in rs}))}
        rngvalues=list(smap.values());rng.shuffle(rngvalues);smap=dict(zip(smap,rngvalues))
        for r in rs:
            r['record_id']=idmap[r['record_id']];r['root_ids']=[idmap[k] for k in r['root_ids']];r['source_id']=smap[r['source_id']]
        for e in es:
            if 'record_id'in e:e['record_id']=idmap[e['record_id']]
            if 'source_id'in e:e['source_id']=smap[e['source_id']]
        shuffled=rng.sample(range(100,900),len(rules))
        for r,j in zip(rules,shuffled):r['rule_id']='K'+str(j)
        seed=dict(family_id='M3_%03d'%i,query=q,policy=ACTIONS.copy(),rules=rules,source_records=rs,events=es,domain=domain,review_status='pending')
        try:
            base=annotate(seed,rs,es)
            if base['gold_state']!=target:raise ValueError('target_mismatch')
            histories=[]
            for mode in ('legal_path','assistant_only'):
                pair=[]
                for stance in ('supported','refuted'):
                    records=copy.deepcopy(rs);initial={r['record_id']:r['active'] for r in records}
                    for r in records:r['active']=False
                    records.append(record(idmap['old'],q if mode=='assistant_only' or stance=='supported' else opposite(q),source='historical_source'))
                    events=[event('retract',idmap['old'])]+[event('add',r['record_id'],r['version']) for r in records[:-1] if initial[r['record_id']]]+copy.deepcopy(es)
                    a=annotate(seed,records,events)
                    row={**seed,**a,'source_records':records,'events':events,'old_answer':stable(dict(state=stance,positive_evidence=[],negative_evidence=[],rule_ids=[],action=ACTIONS[stance])),'history_id':stance,'pair_type':mode,'history_mode':'injected','pair_group':seed['family_id']+'/'+mode,'schema_version':'m3-candidate-1','split':'debug-candidate','graph_id':f'depth{depth}_and{use_and}_or{use_or}','template_id':'structured-generic-zh-v2'}
                    pair.append(row)
                assert pair[0]['canonical_state']==pair[1]['canonical_state'] and pair[0]['state_hash']==pair[1]['state_hash']
                for row in pair:
                    for condition in 'ABC':
                        x={**row,'condition':condition,'sample_id':row['pair_group']+'/'+row['history_id']+'/'+condition}
                        x['messages']=render(x,condition);x['messages'][0]['content']=GENERIC
                        histories.append(x)
            out.extend(histories)
        except (ValueError,AssertionError) as e:rejected.append(dict(family_id=seed['family_id'],reason=str(e)))
    return out,rejected

if __name__=='__main__':
    import json
    rows,rejected=candidates();p=Path('data/m3-candidates-v1');p.mkdir(exist_ok=True)
    (p/'families.jsonl').write_text(''.join(stable(r)+'\n' for r in rows))
    (p/'inputs.jsonl').write_text(''.join(stable(dict(sample_id=r['sample_id'],messages=r['messages']))+'\n' for r in rows))
    report=dict(attempted_families=100,accepted_families=len({r['family_id'] for r in rows}),logical_units=len(rows),rejected=rejected,rejection_ratio=len(rejected)/100,states=dict(collections.Counter(r['gold_state'] for r in rows)),domains=dict(collections.Counter(r['domain'] for r in rows)),structures=dict(collections.Counter(r['graph_id'] for r in rows)),human_review='pending',status='candidates only; human seed review gate remains open; not frozen formal audit',model_calls=0)
    (p/'generation-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    families=sorted({r['family_id'] for r in rows});selected=random.Random(42).sample(families,30)
    (p/'review-30.jsonl').write_text(''.join(stable(dict(family_id=f,review_status='pending',reviewer=None,checks=['逐轮闭包/记录与来源版本','共享根','查询与策略','等价终点','中文指代','ID与标签关联']))+'\n' for f in selected))
    print(stable(report))
