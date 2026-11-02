import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
from logic import *
from dataset import export

STATES=list(ACTIONS)
def parse(raw):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError('duplicate key')
            d[k]=v
        return d
    try:
        p=json.loads(raw,object_pairs_hook=unique)
        if not isinstance(p,dict) or set(p)!= {'state','positive_evidence','negative_evidence','rule_ids','action'}: raise ValueError('schema')
        if p['state'] not in STATES or p['action'] not in ACTIONS.values(): raise ValueError('enum')
        for k in ('positive_evidence','negative_evidence','rule_ids'):
            if not isinstance(p[k],list) or not all(isinstance(i,str) for i in p[k]): raise ValueError('evidence list')
        return p,None
    except (ValueError,TypeError): return None,'invalid_output'

def certificate(row,p):
    if not p:return False,False
    active=row['rounds'][-1]['active_records']; ids={r['record_id'] for r in active}
    cited=set(p['positive_evidence']+p['negative_evidence'])
    stale=bool(cited-ids)
    rules={r['rule_id'] for r in row['rules']}
    if stale or not set(p['rule_ids'])<=rules:return False,stale
    # Verify arbitrary complete certificates, not exact equality with one chosen proof.
    if p['state']!=row['gold_state']:return False,stale
    for field,lit,required in [('positive_evidence',row['query'],p['state'] in ('supported','conflict')),('negative_evidence',opposite(row['query']),p['state'] in ('refuted','conflict'))]:
        facts=closure([r for r in active if r['record_id'] in p[field]],[r for r in row['rules'] if r['rule_id'] in p['rule_ids']])
        if required and lit not in facts:return False,stale
        if not required and p[field]:return False,stale
    return True,stale

def fingerprint():
    root=Path(__file__).parent
    return digest({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('*.py'))})

def run(rows,path,backend='mock-oracle',strong=False,model='mock-v1',revision='not-applicable',endpoint=None,max_requests=0,max_tokens=0,dry=False):
    inputs=export(rows,strong)
    cfg=dict(backend=backend,model=model,revision=revision,tokenizer='provider-reported' if backend=='api' else 'none',temperature=0,seed=42,max_output_tokens=256,prompt='strong' if strong else 'ordinary',code_hash=fingerprint(),data_hash=digest(rows),endpoint=endpoint)
    requests=[dict(model=model,messages=x['messages'],temperature=0,seed=42,max_tokens=256) for x in inputs]
    keys=[digest(dict(config=cfg,request=q)) for q in requests]
    unique=len(set(keys))
    # UTF-8 byte count is a conservative planning proxy, not measured tokenizer tokens.
    estimate=sum(len(stable(q).encode())+256 for q in {k:q for k,q in zip(keys,requests)}.values())
    if dry:return dict(logical_units=len(rows),unique_requests=unique,input_plus_output_token_upper_estimate=estimate,token_estimate_method='UTF8 bytes + 256 output allowance per unique request; tokenizer not loaded',config=cfg)
    if backend=='api':
        if model=='mock-v1' or revision=='not-applicable':raise ValueError('explicit model ID and revision required')
        if not endpoint or not endpoint.startswith('https://'):raise ValueError('API endpoint must be HTTPS')
        if max_requests<=0 or max_tokens<=0:raise ValueError('explicit request/token budget required')
        if unique>max_requests or estimate>max_tokens:raise ValueError('preflight exceeds authorized cap')
        if not os.environ.get('MODEL_API_KEY'):raise ValueError('MODEL_API_KEY missing')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    prior=[json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []
    if any(r['config']!=cfg for r in prior):raise ValueError('run config changed: use a new output path')
    done={r['sample_id'] for r in prior}; cache={r['cache_key']:r for r in prior if r['failure_type']!='network_error'}
    calls=sum(r['actual_call'] for r in prior); used=sum(r.get('reserved_tokens',0) for r in prior)
    try:
        commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):
        commit=None  # exported bundle: source fingerprint remains recorded
    with path.open('a') as f:
        for row,request,key in zip(rows,requests,keys):
            if row['sample_id'] in done:continue
            started=time.monotonic();cached=cache.get(key); actual=not bool(cached)
            raw=None;response=None;failure=None;usage=None;reserved=0
            if cached:
                raw=cached['raw_output'];response=cached['raw_response'];failure=cached['failure_type'];usage=cached['usage']
            elif backend.startswith('mock'):
                p=dict(state=row['gold_state'],action=row['gold_action'],positive_evidence=[],negative_evidence=[],rule_ids=[])
                for side,field in [('positive','positive_evidence'),('negative','negative_evidence')]:
                    proofs=row['valid_proofs'][side]
                    if proofs:
                        p[field]=proofs[0]['records'];p['rule_ids']+=proofs[0]['rules']
                p['rule_ids']=sorted(set(p['rule_ids']))
                raw=stable(p)
                if backend=='mock-faulty':raw=stable(dict(state='unknown',action='seek_evidence',positive_evidence=[],negative_evidence=[],rule_ids=[])) if row['condition']!='C' else 'this is not JSON'
                response={'mock':True,'text':raw};usage={'input_tokens':None,'output_tokens':None}
            else:
                reserved=len(stable(request).encode())+256
                if calls>=max_requests or used+reserved>max_tokens:break
                used+=reserved
                req=urllib.request.Request(endpoint,data=stable(request).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+os.environ['MODEL_API_KEY']})
                try:
                    with urllib.request.urlopen(req,timeout=90) as r:response=json.load(r)
                    raw=response['choices'][0]['message']['content'];usage=response.get('usage')
                except (OSError,ValueError,KeyError,IndexError):
                    # Never log request headers or exception bodies that may contain credentials.
                    failure='network_error'
            if actual:calls+=1
            parsed,err=parse(raw) if raw is not None else (None,None)
            failure=failure or err
            log=dict(run_id=path.stem,sample_id=row['sample_id'],cache_key=key,config=cfg,code_commit=commit,raw_request=request,raw_response=response,raw_output=raw,parsed=parsed,failure_type=failure,retries=0,usage=usage,latency_seconds=time.monotonic()-started,actual_call=actual,cache_hit=bool(cached),reserved_tokens=reserved)
            f.write(stable(log)+'\n');f.flush();done.add(row['sample_id'])
            if failure!='network_error':cache[key]=log
    return dict(logical_units=len(rows),logged=len(done),actual_requests=calls,backend=backend)

def ratio(n,d):return dict(numerator=n,denominator=d,value=n/d if d else None)
def score(rows,logs):
    by={r['sample_id']:r for r in rows}; entries={}
    for log in logs:
        if log['sample_id'] in entries:raise ValueError('duplicate sample result')
        if log['sample_id'] not in by:raise ValueError('unknown sample')
        entries[log['sample_id']]=log
    outputs=[]
    for row in rows:
        l=entries.get(row['sample_id']);p=l['parsed'] if l else None
        correct=bool(p and p['state']==row['gold_state'])
        cert,stale=certificate(row,p)
        outputs.append(dict(row=row,log=l,p=p,correct=correct,certificate=cert,stale=stale))
    def metrics(xs):
        n=len(xs); valid=sum(bool(x['p']) for x in xs); correct=sum(x['correct'] for x in xs)
        f1=[];classes={}
        for s in STATES:
            tp=sum(x['correct'] and x['row']['gold_state']==s for x in xs)
            gold=sum(x['row']['gold_state']==s for x in xs);pred=sum(bool(x['p']) and x['p']['state']==s for x in xs)
            f1.append(2*tp/(gold+pred) if gold+pred else 0)
            classes[s]=dict(recall=ratio(tp,gold),precision=ratio(tp,pred))
        groups=collections.defaultdict(list)
        for x in xs:groups[(x['row']['pair_group'],x['row']['condition'])].append(x)
        pairs=[g for g in groups.values() if len(g)==2]
        parsed=[g for g in pairs if all(x['p'] for x in g)]
        subset=lambda case:[x for x in xs if x['row']['family_id']==case]
        rate=lambda group,test:ratio(sum(test(x) for x in group),len(group))
        return dict(accuracy=ratio(correct,n),macro_f1=sum(f1)/4,classes=classes,parse_coverage=ratio(valid,n),invalid_output=ratio(sum(bool(x['log']) and x['log']['failure_type']=='invalid_output' for x in xs),n),network_error=sum(bool(x['log']) and x['log']['failure_type']=='network_error' for x in xs),unrun=sum(x['log'] is None for x in xs),action_accuracy=rate(xs,lambda x:bool(x['p']) and x['p']['action']==x['row']['gold_action']),pair_joint=ratio(sum(all(x['correct'] for x in g) for g in pairs),len(pairs)),pair_difference=ratio(sum(g[0]['p']['state']!=g[1]['p']['state'] for g in parsed),len(parsed)),pair_coverage=ratio(len(parsed),len(pairs)),pair_decomposition=dict(both_correct=sum(all(x['correct'] for x in g) for g in parsed),both_wrong=sum(not any(x['correct'] for x in g) for g in parsed),one_correct=sum(sum(x['correct'] for x in g)==1 for g in parsed),invalid_or_unrun=len(pairs)-len(parsed)),withdrawal=rate(subset('S01'),lambda x:x['correct']),unsupported_reversal=rate(subset('S01'),lambda x:bool(x['p']) and x['p']['state']=='refuted'),independent_retention=rate(subset('S02'),lambda x:x['correct']),irrelevant_retention=rate(subset('S03'),lambda x:x['correct'] and x['p']['action']==x['row']['gold_action']),conflict_recognition=rate([x for x in xs if x['row']['gold_state']=='conflict'],lambda x:x['correct']),restoration=rate(subset('S06'),lambda x:x['correct'] and x['p']['action']==x['row']['gold_action']),certificate_validity=rate(xs,lambda x:x['certificate']),stale_evidence=rate([x for x in xs if x['p']],lambda x:x['stale']),full_trajectory_success=None,families=len({x['row']['family_id'] for x in xs}))
    errors=[]
    for x in outputs:
        if x['correct'] and x['p']['action']==x['row']['gold_action']:continue
        r=x['row'];p=x['p'];kind=x['log']['failure_type'] if x['log'] else 'unrun'
        if p:
            kind='action_error' if x['correct'] else 'state_error'
            if r['condition']=='A' and not x['correct']:kind='current_evidence_failure'
            elif r['gold_state']=='conflict' and p['state']!='conflict':kind='conflict_missed'
            elif r['family_id']=='S01' and p['state']=='refuted':kind='unsupported_negation'
            elif r['gold_state']!='unknown' and p['state']=='unknown':kind='over_unknown'
        errors.append(dict(sample_id=r['sample_id'],gold=r['gold_state'],prediction=p,category=kind))
    return dict(overall=metrics(outputs),by_condition={c:metrics([x for x in outputs if x['row']['condition']==c]) for c in 'ABC'},by_case={c:metrics([x for x in outputs if x['row']['family_id']==c]) for c in sorted({r['family_id'] for r in rows})},by_pair_type={t:metrics([x for x in outputs if x['row']['pair_type']==t]) for t in ('legal_path','assistant_only')},errors=errors,notes=['mock is engineering validation only','trajectory not evaluated: endpoint-only run','withdrawal scope errors need manual review; state alone does not identify mechanism','M2 descriptive only; no significance claims'])
