"""GA4 funnel by country, Jan-Sep 2026 (property 518041609; data begins Dec 2025). sessions -> items viewed -> add to cart -> checkouts (begin_checkout) -> purchases."""
from common import *
import collections
rows=load('ga4_country_funnel.json')
A=collections.defaultdict(lambda: collections.defaultdict(float)); M=collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    ym=r['year_month']; d=f'{ym[:4]}-{ym[4:]}-01'
    for w in window(d):
        for c in (cc(r['country']),'ALL'):
            for k in ['sessions','totalusers','items_viewed','add_to_carts','checkouts','ecommerce_purchases','purchase_revenue']: A[(w,c)][k]+=r.get(k) or 0
    for c in (cc(r['country']),'ALL'):
        for k in ['sessions','checkouts','ecommerce_purchases']: M[(f'{ym[:4]}-{ym[4:]}',c)][k]+=r.get(k) or 0
print('window country sessions views ATC checkouts purch | view/sess ATC/sess chk/ATC purch/chk purch/sess')
out={}
for c in ['ALL','NG','UK','CA','US']:
    for w in ['JanSep26','AprJun26','JulSep26']:
        a=A[(w,c)]; s=a['sessions']
        out[f'{w}|{c}']=dict(a)
        print(f"{w:9}{c:4} {s:8.0f} {a['items_viewed']:8.0f} {a['add_to_carts']:7.0f} {a['checkouts']:7.0f} {a['ecommerce_purchases']:6.0f} | {100*a['items_viewed']/s:5.1f}% {100*a['add_to_carts']/s:5.1f}% {100*a['checkouts']/a['add_to_carts'] if a['add_to_carts'] else 0:5.1f}% {100*a['ecommerce_purchases']/a['checkouts'] if a['checkouts'] else 0:5.1f}% {100*a['ecommerce_purchases']/s:5.2f}%")
dump('ga4_funnel.json', out); dump('ga4_month.json', {f'{k[0]}|{k[1]}':dict(v) for k,v in M.items()})
print('\nmonthly checkouts (ALL):', {k[0]:int(v['checkouts']) for k,v in sorted(M.items()) if k[1]=='ALL'})
print('monthly GA4 purchases ALL:', {k[0]:int(v['ecommerce_purchases']) for k,v in sorted(M.items()) if k[1]=='ALL'})
