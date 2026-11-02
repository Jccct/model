import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from gpu_eval import MockEngine,mock_or_local
from m3_candidates import candidates
from logic import stable

class Continuation(unittest.TestCase):
    def test_own_answers_resume_and_trajectory_denominator(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'run.jsonl';r=mock_or_local(MockEngine(),p)
            self.assertEqual(r['logical_units'],80)
            self.assertEqual(r['trajectory_success'],dict(numerator=0,denominator=2))
            before=p.read_bytes();mock_or_local(MockEngine(),p);self.assertEqual(p.read_bytes(),before)
            logs=[json.loads(l) for l in p.read_text().splitlines()]
            for tid in ('independent_then_restore','counterevidence_then_conflict'):
                turns=[l for l in logs if l.get('trajectory_id')==tid]
                self.assertEqual(len(turns),4)
                for i,l in enumerate(turns):
                    answers=[m['content'] for m in l['raw_request']['messages'] if m['role']=='assistant']
                    self.assertEqual(answers,[x['raw_output'] for x in turns[:i]])
                    self.assertNotIn('gold_state',stable(l['raw_request']))
                    self.assertNotIn('queried_states',stable(l['raw_request']))
    def test_candidates_balanced_pairs_and_identifiers(self):
        rows,rejected=candidates();self.assertEqual(rejected,[]);self.assertEqual(len(rows),1200)
        from collections import Counter,defaultdict
        self.assertEqual(set(Counter(r['gold_state'] for r in rows).values()),{300})
        groups=defaultdict(list)
        for r in rows:
            groups[(r['pair_group'],r['condition'])].append(r)
            text=stable(r['messages'])
            for forbidden in ('M3_','gold_state','canonical_state','state_hash','can_enter(小林)'):self.assertNotIn(forbidden,text)
        for pair in groups.values():self.assertEqual(pair[0]['canonical_state'],pair[1]['canonical_state'])
        # Record/source withdrawal occurs in both unknown and refuted, not tied to label.
        for s in ('unknown','refuted'):
            chosen=[r for r in rows if r['gold_state']==s]
            self.assertTrue(any(e['op']=='retract_source' for r in chosen for e in r['events']))
            self.assertTrue(any(not any(e['op']=='retract_source' for e in r['events']) for r in chosen))
if __name__=='__main__':unittest.main()
