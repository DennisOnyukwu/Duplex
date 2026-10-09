"""Klaviyo Reviews: all reviews from pages 1-6 (newest first; page 6 reaches Nov 2025, so 2026 is complete). Count by month, status, verified. Review-request flow went live 2026-05-08."""
from common import *
import collections, glob, json
R=[]
for f in sorted(glob.glob(D+'/klaviyo_reviews_p*.json')): R+=json.load(open(f))['result']['data']
print('reviews loaded', len(R), 'oldest', min(r['attributes']['created'] for r in R))
M=collections.defaultdict(lambda: collections.Counter())
for r in R:
    a=r['attributes']; ym=a['created'][:7]
    M[ym]['all']+=1; M[ym][a['status']['value']]+=1; M[ym]['verified' if a['verified'] else 'unverified']+=1
    if a['rating']: M[ym]['rating_sum']+=a['rating']; M[ym]['rated']+=1
out={}
print('month | all | published | rejected | pending | verified | avg rating')
for ym in sorted(M):
    c=M[ym]; out[ym]=dict(c)
    print(f"{ym} {c['all']:4d} {c['published']:4d} {c['rejected']:4d} {c.get('pending',0):4d} {c['verified']:4d} {c['rating_sum']/c['rated'] if c['rated'] else 0:4.2f}")
pre=sum(M[m]['all'] for m in M if '2026-01'<=m<='2026-04'); post=sum(M[m]['all'] for m in M if '2026-05'<=m<='2026-09')
print('Jan-Apr 2026 reviews', pre, '(%.0f/month)'%(pre/4), '| May-Sep 2026', post, '(%.0f/month)'%(post/5))
pub=sum(M[m]['published'] for m in M if m.startswith('2026')); print('published 2026:', pub)
dump('reviews.json', out)
