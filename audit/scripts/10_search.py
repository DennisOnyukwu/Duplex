"""Search Console (sc-domain:beguile.com). Query-level rows Jun 2025-Sep 2026 (16-month API limit: no Jan-May 2025). Branded = query contains a brand term."""
from common import *
import collections,re
BRAND=re.compile(r'beguile|begiule|beguil|shopbeguile|mystique|golden kiss|goddess|sweet oud|blush bloom|omaa|\boma\b',re.I)
rows=load('sc_queries_2026.json')+load('sc_queries_2025H2.json')
M=collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    y,m=r['year_month'].split('|'); ym=f'{y}-{int(m):02d}'; b='brand' if BRAND.search(r['query'] or '') else 'nonbrand'
    M[(ym,b)]['clicks']+=r['clicks'] or 0; M[(ym,b)]['impr']+=r['impressions'] or 0
    M[(ym,b)]['pos_w']+=(r['position'] or 0)*(r['impressions'] or 0)
print('month   brand clicks/impr | nonbrand clicks/impr | nonbrand share of clicks | wtd position (all)')
out={}
for ym in sorted({k[0] for k in M}):
    b=M[(ym,'brand')]; n=M[(ym,'nonbrand')]; tc=b['clicks']+n['clicks']; ti=b['impr']+n['impr']
    out[ym]=dict(brand_clicks=b['clicks'],brand_impr=b['impr'],nonbrand_clicks=n['clicks'],nonbrand_impr=n['impr'],pos=(b['pos_w']+n['pos_w'])/ti if ti else None)
    print(f"{ym} {b['clicks']:6.0f}/{b['impr']:7.0f} | {n['clicks']:6.0f}/{n['impr']:7.0f} | {100*n['clicks']/tc if tc else 0:5.1f}% | {out[ym]['pos']:.1f}")
dump('search_month.json', out)
for w,ms in [('JanSep26',[m for m in out if m.startswith('2026')]),('AprJun26',['2026-04','2026-05','2026-06']),('JulSep26',['2026-07','2026-08','2026-09']),('JulSep25',['2025-07','2025-08','2025-09'])]:
    bc=sum(out[m]['brand_clicks'] for m in ms if m in out); nc=sum(out[m]['nonbrand_clicks'] for m in ms if m in out)
    print(w, 'brand clicks', bc, 'nonbrand clicks', nc, 'nonbrand share', round(100*nc/(bc+nc),1) if bc+nc else None)
# top non-brand queries Jan-Sep 2026
Q=collections.Counter()
for r in load('sc_queries_2026.json'):
    if not BRAND.search(r['query'] or ''): Q[r['query']]+=r['clicks'] or 0
print('top nonbrand 2026:', Q.most_common(15))
# country split
C=collections.defaultdict(lambda: collections.defaultdict(float))
for r in load('sc_country.json'):
    y,m=r['year_month'].split('|'); d=f'{y}-{int(m):02d}-01'
    for w in window(d): C[(w,cc(r['country']))]['clicks']+=r['clicks'] or 0; C[(w,cc(r['country']))]['impr']+=r['impressions'] or 0
print({f'{k[0]}|{k[1]}':(int(v['clicks']),int(v['impr'])) for k,v in sorted(C.items()) if k[1]!='Other'})
dump('search_country.json', {f'{k[0]}|{k[1]}':dict(v) for k,v in C.items()})
