"""Shopify orders: source of truth. Input: data/shop_orders_*.json (Windsor shopify, order rows incl. refund-adjustment rows).
Definitions:
 - Net sales = sum of order_net_sales over all rows dated in the window (refund rows carry negative net on refund date) — matches Shopify's net-sales-by-date.
 - Orders = distinct orders placed in the window (row with earliest date per order_id), excluding cancelled orders. Test orders filtered (none found).
 - Country = shipping country of the order.
"""
from common import *
import collections
rows = [r for r in load('shop_orders_*.json') if r['order_test'] == 'False']
first = {}
for r in rows:
    k = r['order_id']
    if k not in first or r['date'] < first[k]['date']: first[k] = r
cancelled = sum(1 for r in first.values() if r.get('order_cancelled_at'))
orders = [r for r in first.values() if not r.get('order_cancelled_at')]
print('rows', len(rows), 'orders', len(first), 'cancelled', cancelled)

def agg(keyfn):
    A = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in rows:
        for k in keyfn(r): A[k]['net'] += r['order_net_sales'] or 0
    for r in orders:
        for k in keyfn(r):
            a = A[k]; a['orders'] += 1
            a['gross'] += r.get('order_gross_sales') or 0
            a['disc'] += r.get('order_total_discounts') or 0
            if r.get('order_discount_code'): a['orders_with_code'] += 1
            a['units'] += r.get('order_quantity') or 0
            if r.get('order_new_or_returning_customer') == 'new': a['new'] += 1
            elif r.get('order_new_or_returning_customer') == 'returning': a['ret'] += 1
            a['first_net'] += r['order_net_sales'] or 0  # net at placement, for AOV
    for k, a in A.items():
        a['aov'] = a['first_net'] / a['orders'] if a['orders'] else None
        a['disc_rate'] = a['disc'] / a['gross'] if a['gross'] else None
        a['new_share'] = a['new'] / a['orders'] if a['orders'] else None
    return {str(k): dict(v) for k, v in A.items()}

byWinCountry = agg(lambda r: [(w, c) for w in window(r['date']) for c in (cc(r['order_shipping_address_country']), 'ALL')])
byMonthCountry = agg(lambda r: [(ym(r['date']), c) for c in (cc(r['order_shipping_address_country']), 'ALL')])
dump('shopify_win_country.json', byWinCountry); dump('shopify_month_country.json', byMonthCountry)

def f(x): return '-' if x is None else (f'{x/1e6:,.1f}m' if abs(x) >= 1e5 else f'{x:,.0f}')
print('\nWINDOW x COUNTRY: orders | net ₦ | AOV ₦ | new% | discount% of gross | %orders w code')
for c in ['ALL','NG','UK','CA','US','Other']:
    for w in WINS:
        a = byWinCountry.get(str((w, c)))
        if a: print(f"{c:5} {w:9} {a['orders']:6.0f} {f(a['net']):>9} {a['aov'] or 0:9,.0f} {100*(a['new_share'] or 0):5.1f}% {100*(a['disc_rate'] or 0):5.1f}% {100*a.get('orders_with_code',0)/a['orders']:5.1f}%")
print('\nMONTH x COUNTRY: orders / net ₦m')
months = sorted({eval(k)[0] for k in byMonthCountry})
print('month   ' + ''.join(f'{c:>16}' for c in ['ALL','NG','UK','CA','US']))
for m in months:
    line = m + ' '
    for c in ['ALL','NG','UK','CA','US']:
        a = byMonthCountry.get(str((m, c)))
        line += f"{(a or {}).get('orders',0):7.0f}/{(a or {}).get('net',0)/1e6:7.1f}m "
    print(line)
