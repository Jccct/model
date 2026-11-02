import argparse
import json
from pathlib import Path
import subprocess
from dataset import *
from evaluation import run,score

def save(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def jsonl(path,rows):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(stable(r)+'\n' for r in rows))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['validate','generate','export-inputs','run-eval','score','report'])
    ap.add_argument('--strong',action='store_true');ap.add_argument('--backend',choices=['mock-oracle','mock-faulty','api'],default='mock-oracle');ap.add_argument('--model',default='mock-v1');ap.add_argument('--revision',default='not-applicable');ap.add_argument('--endpoint');ap.add_argument('--max-requests',type=int,default=0);ap.add_argument('--max-tokens',type=int,default=0);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--run',default='runs/mock-ordinary.jsonl');ap.add_argument('--out');args=ap.parse_args()
    rows=generate()
    if args.command=='validate':
        subprocess.run(['python3','-m','unittest','discover','-s','tests','-v'],check=True)
        print(stable(dict(samples=len(rows),histories=24,pair_groups=12,condition_pair_comparisons=36,independent_labels='all rounds agree')))
    elif args.command=='generate':
        jsonl('data/seeds.jsonl',seeds());jsonl('data/paired_histories.jsonl',rows);save('data/splits.json',dict(debug=[s['family_id'] for s in seeds()],human_review='pending',train=[],test=[]))
        readable=['# 六例逐轮核验（人工审核 pending）']
        for s in seeds():
            a=annotate(s,s['source_records'],s['events']);readable+=['\n## '+s['family_id'],'```json',json.dumps(s,ensure_ascii=False,indent=2),'```']
            for i,r in enumerate(a['rounds']):readable+=['第 %d 轮：%s；动作 %s；有效记录 %s；证明 %s'%(i,r['gold_state'],r['gold_action'],','.join(x['record_id'] for x in r['active_records']),stable(r['valid_proofs']))]
        Path('reports/six_cases.md').write_text('\n'.join(readable)+'\n')
    elif args.command=='export-inputs':jsonl(args.out or ('data/inputs-strong.jsonl' if args.strong else 'data/inputs-ordinary.jsonl'),export(rows,args.strong))
    elif args.command=='run-eval':print(stable(run(rows,args.run,args.backend,args.strong,args.model,args.revision,args.endpoint,args.max_requests,args.max_tokens,args.dry_run)))
    elif args.command in ('score','report'):
        logs=[json.loads(x) for x in Path(args.run).read_text().splitlines()];result=score(rows,logs)
        save(args.out or 'reports/'+Path(args.run).stem+'-scores.json',result)
        if args.command=='report':
            lines=['# 自动报告 '+Path(args.run).stem,'','后端：'+logs[0]['config']['backend'],'逻辑单元 %d；实际请求 %d；缓存 %d'%(len(logs),sum(x['actual_call'] for x in logs),sum(x['cache_hit'] for x in logs)),'','|条件|状态正确|Macro F1|配对全对|格式错误|','|---|---|---|---|---|']
            for c,m in result['by_condition'].items():lines.append('|%s|%s/%s|%.4f|%s/%s|%s/%s|'%(c,m['accuracy']['numerator'],m['accuracy']['denominator'],m['macro_f1'],m['pair_joint']['numerator'],m['pair_joint']['denominator'],m['invalid_output']['numerator'],m['invalid_output']['denominator']))
            lines+=['','全部错误（不挑选）：','```json',json.dumps(result['errors'],ensure_ascii=False,indent=2),'```','完整轨迹未运行；模型实验与 H1/H2/H3 结论 TBD。']
            Path('reports/'+Path(args.run).stem+'.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
