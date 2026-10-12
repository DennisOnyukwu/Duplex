"""Last-visit source of each order (Shopify order_customer_last_visit_source), by window and country. Orders = first row per order, not cancelled."""
from common import *
import collections
rows = [r for r in load('shop_orders_202[56]*.json') if r['order_test']=='False' and 'order_customer_last_visit_source' in r]
first = {}
for r in rows:
    if r['order_id'] not in first or r['date'] < first[r['order_id']]['date']: first[r['order_id']] = r
orders = [r for r in first.values() if not r.get('order_cancelled_at')]
def norm(s):
    s = (s or 'none recorded').strip()
    return s
res = {}
for c in ['ALL','NG','UK','CA','US']:
    for w in ['JanSep26','JanSep25','AprJun26','JulSep26']:
        C = collections.Counter(); N = collections.Counter()
        for r in orders:
            if w in window(r['date']) and (c=='ALL' or cc(r['order_shipping_address_country'])==c):
                k = norm(r['order_customer_last_visit_source']); C[k]+=1; N[k]+=r['order_net_sales'] or 0
        tot = sum(C.values())
        res[f'{c}|{w}'] = {k:[C[k], N[k]] for k in C}
        if w in ('JanSep26','JanSep25'):
            print(c, w, tot, ' | '.join(f'{k} {C[k]} ({100*C[k]/tot:.0f}%)' for k,_ in C.most_common(9)))
dump('shopify_source.json', res)
# utm source/medium for Jan-Sep 26
C = collections.Counter((r.get('order_customer_last_visit_utm_source'), r.get('order_customer_last_visit_utm_medium')) for r in orders if 'JanSep26' in window(r['date']))
print(C.most_common(20))
