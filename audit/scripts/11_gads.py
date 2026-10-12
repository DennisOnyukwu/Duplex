"""Google Ads account 173-070-6186 (USD). Campaign x month from Mar 2026 (no rows before). Search terms Jan-Sep 2026: brand share of cost/clicks."""
from common import *
import collections,re
BRAND=re.compile(r'beguile|begiule|beguil|shopbeguile|mystique|golden kiss|goddess|sweet oud|blush bloom|omaa|\boma\b',re.I)
rows=load('gads_campaign_month.json')
print('month      campaign          cost$  clicks  conv  value$  value/cost')
tot=collections.defaultdict(float)
for r in sorted(rows,key=lambda r:(r['year_month'],r['campaign'])):
    print(f"{r['year_month']:8} {r['campaign']:16} {r['cost']:7.0f} {r['clicks']:6.0f} {r['conversions']:6.1f} {r['conversions_value']:7.0f} {r['conversions_value']/r['cost']:5.1f}")
    for k in ['cost','clicks','conversions','conversions_value']: tot[k]+=r[k]
    y,m=r['year_month'].split('|'); 
    for w in window(f'{y}-{int(m):02d}-01'): 
        for k in ['cost','clicks','conversions','conversions_value']: tot[(w,r['campaign'],k)]+=r[k]
print('Jan-Sep26 total', dict((k,round(v,1)) for k,v in tot.items() if isinstance(k,str)))
for w in ['JanSep26','AprJun26','JulSep26']:
    for c in ['NGN PMAX','CA PMAX','Website traffic']:
        if tot[(w,c,'cost')]: print(w,c,'cost$',round(tot[(w,c,'cost')]),'conv',round(tot[(w,c,'conversions')],1),'value$',round(tot[(w,c,'conversions_value')]),'cost/conv$',round(tot[(w,c,'cost')]/tot[(w,c,'conversions')],1))
st=load('gads_search_terms_2026.json')
B=collections.defaultdict(float)
for r in st:
    b='brand' if BRAND.search(r['search_term'] or '') else 'nonbrand'
    for k in ['cost','clicks','conversions','conversions_value']: B[(b,k)]+=r[k] or 0
print('search terms Jan-Sep26:', {f'{k[0]}|{k[1]}':round(v,1) for k,v in B.items()})
top=sorted(st,key=lambda r:-(r['cost'] or 0))[:15]; print([(r['search_term'],round(r['cost'],1),r['conversions']) for r in top])
dump('gads.json', {'tot':{str(k):v for k,v in tot.items()}, 'terms':{str(k):v for k,v in B.items()}})
