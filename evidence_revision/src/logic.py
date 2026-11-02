"""Finite signed Horn logic. No negation-as-failure or explosion."""
import copy
import hashlib
import itertools
import json

ACTIONS = dict(supported='proceed', refuted='stop', unknown='seek_evidence', conflict='review')
def stable(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def digest(x):
    return hashlib.sha256(stable(x).encode()).hexdigest()
def opposite(q):
    return q[4:] if q.startswith('not_') else 'not_' + q

def validate(records, rules):
    ids = [r['record_id'] for r in records]
    if len(ids) != len(set(ids)): raise ValueError('duplicate record_id; use distinct IDs for versions')
    roots = {i for r in records for i in r['root_ids']}
    if len(roots) > 12 or len(rules) > 16: raise ValueError('size_limit')
    if len({r['rule_id'] for r in rules}) != len(rules): raise ValueError('duplicate rule_id')
    for r in records:
        if not r['root_ids'] or not all(k in r for k in ('source_id','version','literal','active')):
            raise ValueError('invalid record')
        if not set(r['root_ids']) <= set(ids): raise ValueError('missing root')
    edges = {}
    for r in rules:
        if not r['premises']: raise ValueError('empty premises')
        edges.setdefault(r['conclusion'], []).extend(r['premises'])
    def depth(x, path):
        if x in path: raise ValueError('cyclic rules')
        return max([0] + [1 + depth(y, path | {x}) for y in edges.get(x, [])])
    if max([0] + [depth(x, set()) for x in edges]) > 4: raise ValueError('depth_limit')

def replay(records, events):
    rs = copy.deepcopy(records)
    by = {r['record_id']: r for r in rs}
    for e in events:
        op = e['op']
        if op == 'retract_source':
            if 'versions' not in e: raise ValueError('source scope requires explicit versions')
            targets = [r for r in rs if r['source_id'] == e['source_id'] and r['version'] in e['versions']]
            if not targets: raise ValueError('empty source scope')
        elif op in ('add','retract','restore'):
            r = by[e['record_id']]
            if r['version'] != e['version']: raise ValueError('version mismatch')
            targets = [r]
        else: raise ValueError('unknown operation')
        for r in targets: r['active'] = op in ('add','restore')
    # root withdrawal also invalidates copied reports; restore never revives other flags.
    return [r for r in rs if r['active'] and all(by[x]['active'] for x in r['root_ids'])]

def closure(records, rules):
    facts = {r['literal'] for r in records}
    while True:
        new = facts | {r['conclusion'] for r in rules if set(r['premises']) <= facts}
        if new == facts: return facts
        facts = new

def state(facts, q):
    return {(True,False):'supported',(False,True):'refuted',(False,False):'unknown',(True,True):'conflict'}[(q in facts, opposite(q) in facts)]

def independent_proofs(records, rules, target):
    """Backward proof search; deliberately does not call forward closure."""
    def search(lit, path):
        if lit in path: raise ValueError('cycle')
        out = [(frozenset([r['record_id']]), frozenset(), frozenset(r['root_ids'])) for r in records if r['literal'] == lit]
        for rule in rules:
            if rule['conclusion'] != lit: continue
            choices = [search(p, path | {lit}) for p in rule['premises']]
            for branch in itertools.product(*choices):
                out.append((frozenset().union(*(b[0] for b in branch)), frozenset([rule['rule_id']]).union(*(b[1] for b in branch)), frozenset().union(*(b[2] for b in branch))))
        return list(set(out))
    raw = search(target, set())
    return [dict(records=sorted(a), rules=sorted(b), roots=sorted(c)) for a,b,c in sorted(raw, key=lambda x: str(tuple(sorted(s) for s in x))) if not any(d < c for _,_,d in raw)]

def oracle_state(records, rules, q):
    pos = independent_proofs(records, rules, q)
    neg = independent_proofs(records, rules, opposite(q))
    return {(True,False):'supported',(False,True):'refuted',(False,False):'unknown',(True,True):'conflict'}[(bool(pos),bool(neg))], {'positive':pos,'negative':neg}

def canonical(records, rules, query, policy, context=None):
    return dict(records=sorted([{**r,'root_ids':sorted(r['root_ids'])} for r in records],key=lambda r:r['record_id']), rules=sorted([{**r,'premises':sorted(r['premises'])} for r in rules],key=lambda r:r['rule_id']),query=query,policy=policy,context=context or {})
