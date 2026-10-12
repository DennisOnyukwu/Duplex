"""Line items by product. Titles merged case-insensitively (e.g. 'MYSTIQUE' and 'Mystique' are one product; 'Golden Kiss - 10ML'/'- 10ml' merged).
Net = sum line_item__net_sales over rows; units = quantity on first occurrence of each line item. Cancelled orders and 'Delivery fee' excluded."""
from common import *
import collections, re
rows = [r for r in load('li_*.json') if str(r['order_test'])=='False']
dups = collections.Counter(r['line_item__id'] for r in rows)
print('line rows', len(rows), 'distinct line items', len(dups), 'repeated', sum(1 for v in dups.values() if v>1))
def norm(t):
    t = re.sub(r'\s+',' ', (t or '').strip().upper())
    t = t.replace('3ML SAMPLE','3ML SAMPLE')
    return t
titles = collections.defaultdict(set)
for r in rows: titles[norm(r['line_item__title'])].add(r['line_item__title'])
merged = {k:v for k,v in titles.items() if len(v)>1}
print('merged spellings:', merged)
seen=set(); A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in sorted(rows, key=lambda r:r['date']):
    if r.get('order_cancelled_at') or norm(r['line_item__title'])=='DELIVERY FEE': continue
    p = norm(r['line_item__title'])
    for w in window(r['date']):
        for c in (cc(r['order_shipping_address_country']),'ALL'):
            a=A[(w,c,p)]
            if r['line_item__id'] not in seen: a['units'] += r['line_item__quantity'] or 0; a['lines']+=1
            a['net'] += r['line_item__net_sales'] or 0
    seen.add(r['line_item__id'])
out = {str(k):dict(v) for k,v in A.items()}; dump('shopify_products.json', out)
for c in ['ALL','NG','UK','CA','US']:
    print('\n==', c)
    tot = {w: sum(v['net'] for k,v in A.items() if k[0]==w and k[1]==c) for w in WINS}
    prods = sorted({k[2] for k in A if k[1]==c and k[0]=='JanSep26'}, key=lambda p:-A[('JanSep26',c,p)]['net'])
    print(f"{'product':28}" + ''.join(f'{w:>22}' for w in WINS))
    for p in prods:
        print(f'{p:28}' + ''.join(f"{A[(w,c,p)]['units']:6.0f}u {A[(w,c,p)]['net']/1e6:6.1f}m {100*A[(w,c,p)]['net']/tot[w] if tot[w] else 0:4.0f}%" for w in WINS))
