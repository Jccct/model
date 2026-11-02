import copy
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from logic import *
from dataset import *
from evaluation import parse,score,run,certificate

class Semantics(unittest.TestCase):
    def test_six_trajectories(self):
        expected=[['supported','unknown'],['supported','supported'],['supported','supported'],['supported','unknown','refuted'],['supported','conflict'],['supported','unknown','supported']]
        for seed,want in zip(seeds(),expected):self.assertEqual([r['gold_state'] for r in annotate(seed,seed['source_records'],seed['events'])['rounds']],want)
    def test_shared_root_withdrawal(self):
        rs=[record('root','raw'),record('copy1','p',roots=['root']),record('copy2','p',roots=['root'])]
        self.assertEqual({tuple(p['roots']) for p in independent_proofs(rs,[],'p')},{('root',)})
        self.assertEqual(state(closure(replay(rs,[event('retract','root')]),[]),'p'),'unknown')
        self.assertEqual(state(closure(replay(rs,[event('retract','copy1')]),[]),'p'),'supported')
    def test_source_scope_and_version_restore(self):
        rs=[record('v1','p',source='s',version=1),record('v2','not_p',source='s',version=2)]
        es=[dict(op='retract_source',source_id='s',versions=[1,2]),event('restore','v1')]
        self.assertEqual([r['record_id'] for r in replay(rs,es)],['v1'])
        with self.assertRaises(ValueError):replay(rs,[event('restore','v2',1)])
        with self.assertRaises(ValueError):replay(rs,[dict(op='retract_source',source_id='s')])
    def test_and_or_and_independent_oracle_exhaustive(self):
        rs=[record('a','a'),record('b','b'),record('c','c'),record('n','not_p')]
        rules=[dict(rule_id='r1',premises=['a','b'],conclusion='p'),dict(rule_id='r2',premises=['c'],conclusion='p')]
        for bits in itertools.product([False,True],repeat=4):
            for r,on in zip(rs,bits):r['active']=on
            active=replay(rs,[])
            s,_=oracle_state(active,rules,'p');self.assertEqual(s,state(closure(active,rules),'p'))
        self.assertNotIn('p',closure([record('a','a')],rules))
        self.assertNotIn('a',closure([record('p','p')],rules))
        self.assertNotIn('anything',closure([record('p','p'),record('n','not_p')],[]))
    def test_limits(self):
        with self.assertRaises(ValueError):validate([record(str(i),str(i)) for i in range(13)],[])
        with self.assertRaises(ValueError):validate([], [dict(rule_id='r',premises=['p'],conclusion='p')])
        with self.assertRaises(ValueError):validate([], [dict(rule_id=str(i),premises=[str(i)],conclusion=str(i+1)) for i in range(5)])
    def test_same_label_not_equivalence(self):
        s=seeds()[1];a=annotate(s,s['source_records'],s['events']);b=copy.deepcopy(a['canonical_state']);b['policy']['supported']='review'
        self.assertNotEqual(a['canonical_state'],b);self.assertNotEqual(a['state_hash'],digest(b))

class Pipeline(unittest.TestCase):
    def test_pairs_and_leakage(self):
        rows=generate();self.assertEqual(len(rows),72)
        grouped={}
        for row,inp in zip(rows,export(rows)):
            text=stable(inp['messages'])
            for field in ('gold_state','gold_action','valid_proofs','state_hash','canonical_state','family_id','S01','S02','S03','S04','S05','S06'):
                self.assertNotIn(field,text)
            self.assertEqual(set(inp),{'sample_id','messages'})
            grouped.setdefault((row['pair_group'],row['condition']),[]).append(row)
        for (group,c),rs in grouped.items():
            self.assertEqual(rs[0]['canonical_state'],rs[1]['canonical_state'])
            self.assertEqual(rs[0]['state_hash'],rs[1]['state_hash'])
            if 'assistant_only' in group:
                for field in ('events','source_records'):self.assertEqual(rs[0][field],rs[1][field])
                b0=[m for m in rs[0]['messages'] if m['role']!='assistant'];b1=[m for m in rs[1]['messages'] if m['role']!='assistant'];self.assertEqual(b0,b1)
            if c=='A':self.assertEqual(rs[0]['messages'],rs[1]['messages'])
    def test_parse_rejects_malformed_and_duplicate(self):
        for raw in ['supported','{"state":["supported","unknown"]}','{"state":"unknown","state":"supported"}','null']:
            self.assertEqual(parse(raw),(None,'invalid_output'))
    def test_mock_resume_metrics_and_faults(self):
        rows=generate()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'mock.jsonl'
            result=run(rows,p);before=p.read_bytes();run(rows,p);self.assertEqual(before,p.read_bytes())
            self.assertLess(result['actual_requests'],72)
            logs=[json.loads(x) for x in p.read_text().splitlines()];m=score(rows,logs)
            self.assertEqual(m['overall']['accuracy']['value'],1)
            self.assertEqual(m['overall']['certificate_validity']['value'],1)
            p2=Path(tmp)/'bad.jsonl';run(rows,p2,'mock-faulty');bad=score(rows,[json.loads(x) for x in p2.read_text().splitlines()])
            self.assertEqual(bad['overall']['invalid_output']['numerator'],24)
            self.assertEqual(bad['overall']['accuracy']['numerator'],8)
            self.assertEqual(bad['overall']['accuracy']['denominator'],72)
            self.assertTrue(bad['errors'])
            with self.assertRaises(ValueError):score(rows,logs+[logs[0]])
    def test_certificate_alternative_and_stale(self):
        row=next(r for r in generate() if r['family_id']=='S02')
        p=dict(state='supported',action='proceed',positive_evidence=['E2'],negative_evidence=[],rule_ids=['R2'])
        self.assertEqual(certificate(row,p),(True,False))
        p['positive_evidence']=['E1'];self.assertEqual(certificate(row,p),(False,True))
    def test_preflight_budget(self):
        with self.assertRaises(ValueError):run(generate(),'/tmp/not-created.jsonl',backend='api',model='test-model',revision='test-revision',endpoint='https://example.com',max_requests=1,max_tokens=1)

if __name__=='__main__':unittest.main()
