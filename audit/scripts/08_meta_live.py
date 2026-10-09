"""Campaigns live on 2026-10-08 (effective status ACTIVE) from the 1-8 Oct pull. Daily budget is in minor units (kobo): ₦ = value/100 (consistent with spend ≈ budget x days)."""
from common import *
import re, collections
rows=load('meta_live_oct.json')
act=[r for r in rows if r['status']=='ACTIVE']
def mk(n):
    s=n.lower()
    for k,p in [('NG',r'\bng\b|ng-|/ng|lagos'),('UK',r'\buk\b'),('CA',r'\bca\b'),('US',r'usa|\bus\b')]:
        if re.search(p,s): return k
    return '?'
C=collections.Counter(mk(r['campaign']) for r in act)
B=collections.defaultdict(float)
for r in act: B[mk(r['campaign'])]+= float(r['daily_budget'])/100 if r['daily_budget'] else 0
print('campaigns with spend 1-8 Oct:', len(rows), '| ACTIVE:', len(act), dict(C))
print('active daily budget ₦ (campaign-level budgets only):', {k: round(v) for k,v in B.items()}, 'total', round(sum(B.values())))
print('ACTIVE with no campaign budget:', [r['campaign'] for r in act if not r['daily_budget']])
print('spend 1-8 Oct total ₦m', sum(float(r['spend']) for r in rows)/1e6)
dump('meta_live.json', dict(n_rows=len(rows), n_active=len(act), by_market=C, budget=B))
