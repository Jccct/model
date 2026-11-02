"""Local CUDA inference; no training. Mock mode exercises the same orchestration."""
import argparse
import json
from pathlib import Path
import time
from dataset import BASE, STRONG, generate, export
from evaluation import parse, certificate, score, fingerprint
from logic import stable, digest

INTERFACE = '输出约束：action必须是非空字符串，且只能取proceed、stop、seek_evidence、review。固定映射：supported→proceed，refuted→stop，unknown→seek_evidence，conflict→review。positive_evidence、negative_evidence、rule_ids必须为字符串ID列表。只输出一个JSON对象，不加Markdown围栏或解释。'

class LocalCUDA:
    def __init__(self, model_path, revision, max_context=4096):
        import torch
        import transformers
        import platform
        from transformers import AutoTokenizer, AutoModelForCausalLM
        if not torch.cuda.is_available(): raise RuntimeError('CUDA GPU unavailable; do not silently use CPU')
        if not Path(model_path).is_dir():raise ValueError('existing local model directory required; no implicit downloads')
        torch.manual_seed(42)
        self.torch=torch;self.limit=max_context
        self.tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True,trust_remote_code=False)
        self.model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16).to('cuda').eval()
        self.metadata=dict(model_path=str(Path(model_path).resolve()),declared_revision=revision,config_commit=getattr(self.model.config,'_commit_hash',None),gpu=torch.cuda.get_device_name(),gpu_total_bytes=torch.cuda.get_device_properties(0).total_memory,torch=torch.__version__,transformers=transformers.__version__,python=platform.python_version(),tokenizer_class=type(self.tokenizer).__name__)
        # Hash model and tokenizer files; no inference about revision from directory name.
        import hashlib
        manifest={}
        for p in sorted(Path(model_path).rglob('*')):
            if not p.is_file() or p.name.startswith('.'):continue
            if p.suffix not in ('.safetensors','.bin','.json','.model','.txt','.jinja'):continue
            h=hashlib.sha256()
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
            manifest[str(p.relative_to(model_path))]=h.hexdigest()
        self.metadata['artifact_manifest']=manifest
    def __call__(self,messages):
        t=self.tokenizer;torch=self.torch
        rendered=t.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        encoded=t(rendered,return_tensors='pt',add_special_tokens=False).to('cuda');n=encoded['input_ids'].shape[-1]
        if n+256>min(self.limit,getattr(self.model.config,'max_position_embeddings',self.limit)):raise ValueError('context_limit; no truncation')
        torch.cuda.reset_peak_memory_stats();started=time.monotonic()
        with torch.inference_mode():out=self.model.generate(**encoded,max_new_tokens=256,do_sample=False,pad_token_id=t.eos_token_id)
        torch.cuda.synchronize()
        answer=out[0,n:];raw=t.decode(answer,skip_special_tokens=True)
        return raw,dict(input_tokens=n,output_tokens=len(answer),latency_seconds=time.monotonic()-started,peak_allocated_bytes=torch.cuda.max_memory_allocated())

class MockEngine:
    metadata={'backend':'mock-constant-unknown','model':'none'}
    def __call__(self,messages):
        return stable(dict(state='unknown',positive_evidence=[],negative_evidence=[],rule_ids=[],action='seek_evidence')),dict(input_tokens=None,output_tokens=None)

def mock_or_local(engine, output, strong=False, max_calls=100, explicit_interface=False):
    """Every trajectory retains its own actual raw answers, including malformed ones."""
    rows=generate();inputs=export(rows,strong)
    if explicit_interface:
        for x in inputs:x["messages"][0]["content"] += "\n"+INTERFACE
    trajectories=[json.loads(l) for l in Path('data/fixed_trajectories.jsonl').read_text().splitlines()]
    cfg=dict(engine=engine.metadata,strong=strong,explicit_interface=explicit_interface,code_hash=fingerprint(),data_hash=digest(rows),trajectory_hash=digest(trajectories),max_new_tokens=256,do_sample=False,seed=42)
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    logs=[json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    if any(l['config']!=cfg for l in logs):raise ValueError('config changed; use new output path')
    done={l['sample_id']:l for l in logs};cache={l['cache_key']:l for l in logs if l['failure_type'] not in ('runtime_error',)}
    calls=sum(l['actual_call'] for l in logs)
    def ask(sid,messages,kind,extra):
        nonlocal calls
        if sid in done:return done[sid]
        key=digest(dict(config=cfg,messages=messages));cached=cache.get(key)
        if not cached and calls>=max_calls:raise RuntimeError('call_cap_reached')
        usage=None;failure=None;raw=None
        if cached:raw=cached['raw_output'];usage=cached['usage'];failure=cached['failure_type']
        else:
            calls+=1
            try:raw,usage=engine(messages)
            except (RuntimeError,ValueError):failure='runtime_error'
        parsed,err=parse(raw) if raw is not None else (None,None)
        log=dict(config=cfg,sample_id=sid,kind=kind,cache_key=key,raw_request={'messages':[dict(m) for m in messages]},raw_response={'text':raw},raw_output=raw,usage=usage,parsed=parsed,failure_type=failure or err,actual_call=not bool(cached),cache_hit=bool(cached),retries=0,**extra)
        with p.open('a') as f:f.write(stable(log)+'\n')
        logs.append(log);done[sid]=log
        if failure is None:cache[key]=log
        return log
    for row,inp in zip(rows,inputs):ask(row['sample_id'],inp['messages'],'endpoint',{})
    for tr in trajectories:
        messages=[dict(role='system',content=BASE+('\n'+STRONG if strong else '')+('\n'+INTERFACE if explicit_interface else ''))]
        previous=0
        for turn,index in enumerate(tr['queried_round_indices']):
            if turn==0:
                user=stable({k:tr[k] for k in ('rules','query','policy','source_records')})
            else:user=stable(dict(events=tr['events'][previous:index],question='应用这些可信更新后重新判断。'))
            messages.append(dict(role='user',content=user))
            # No gold, oracle or queried_states is passed to engine.
            result=ask('trajectory/'+tr['trajectory_id']+'/'+str(turn),messages,'trajectory',dict(trajectory_id=tr['trajectory_id'],turn=turn))
            if result['raw_output'] is None:break
            messages.append(dict(role='assistant',content=result['raw_output']))
            previous=index
    endpoint=[l for l in logs if l['kind']=='endpoint']
    report=score(rows,endpoint)
    trajectory_details=[]
    for tr in trajectories:
        rounds=[]
        for turn,index in enumerate(tr['queried_round_indices']):
            l=done.get('trajectory/'+tr['trajectory_id']+'/'+str(turn));pred=l['parsed'] if l else None;gold=tr['oracle']['rounds'][index]
            rounds.append(dict(turn=turn,gold=gold['gold_state'],prediction=pred,correct=bool(pred and pred['state']==gold['gold_state'] and pred['action']==gold['gold_action'])))
        trajectory_details.append(dict(trajectory_id=tr['trajectory_id'],rounds=rounds,success=all(r['correct'] for r in rounds)))
    report['trajectory_details']=trajectory_details
    report['trajectory_success']=dict(numerator=sum(t['success'] for t in trajectory_details),denominator=len(trajectories))
    report['engine']=engine.metadata;report['actual_calls']=calls;report['logical_units']=len(logs)
    report['notes']=['This run explicitly includes own-answer fixed trajectories.','Mock engine results are engineering checks only; real CUDA inference requires lab access.']
    Path(str(p)+'.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--model-path');a.add_argument('--revision');a.add_argument('--mock',action='store_true');a.add_argument('--strong',action='store_true');a.add_argument('--explicit-interface',action='store_true');a.add_argument('--max-calls',type=int,default=100);a.add_argument('--out',required=True);args=a.parse_args()
    if not args.mock and (not args.model_path or not args.revision):a.error('local model path and exact revision required')
    engine=MockEngine() if args.mock else LocalCUDA(args.model_path,args.revision)
    r=mock_or_local(engine,args.out,args.strong,args.max_calls,args.explicit_interface)
    print(stable(dict(engine=r['engine'] if args.mock else 'CUDA (metadata in report)',logical_units=r['logical_units'],actual_calls=r['actual_calls'],trajectory_success=r['trajectory_success'])))
