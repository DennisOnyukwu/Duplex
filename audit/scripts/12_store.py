"""Store checks from Shopify data (storefront fetch blocked by network policy). Description completeness, sold-out tags per market, shipping lines and presentment prices per market (Jul-Sep 2026 orders)."""
from common import *
import re, collections, json
P=load('shop_products_desc.json')
print('product | status | words | notes listed | sold-out tags')
for p in P:
    txt=re.sub('<[^>]+>',' ',p['product_description']); w=len(txt.split()); notes=bool(re.search(r'notes',txt,re.I))
    so=re.findall(r'soldout:(\w+)', p['product_tags'])
    print(f"{p['product_title']:26} {p['product_status']:8} {w:4d} {'yes' if notes else 'no ':3} {','.join(so)}")
rows=[r for r in load('shop_orders_2026Q3_presentment.json') if str(r['order_test'])=='False']
first={}
for r in rows:
    if r['order_id'] not in first: first[r['order_id']]=r
O=list(first.values()); print('\norders Jul-Sep26', len(O))
for c in ['NG','UK','CA','US']:
    os_=[r for r in O if cc(r['order_shipping_address_country'])==c]
    cur=collections.Counter(r['order_presentment_currency'] for r in os_)
    ship=collections.Counter((r['order_shipping_line_title'], r['order_total_shipping_price_presentment']) for r in os_)
    free=sum(1 for r in os_ if (r['order_total_shipping_price_presentment'] or 0)==0)
    sub=[r['order_subtotal_price_presentment'] for r in os_ if r['order_subtotal_price_presentment']]
    # min subtotal with free shipping, max subtotal with paid shipping
    fs=[r['order_subtotal_price_presentment'] for r in os_ if (r['order_total_shipping_price_presentment'] or 0)==0 and r['order_subtotal_price_presentment']]
    ps=[r['order_subtotal_price_presentment'] for r in os_ if (r['order_total_shipping_price_presentment'] or 0)>0 and r['order_subtotal_price_presentment']]
    print(f"\n{c}: n={len(os_)} currency={dict(cur)} free-shipping orders={free} ({100*free/len(os_) if os_ else 0:.0f}%) min subtotal w/ free ship={min(fs) if fs else None} max subtotal w/ paid ship={max(ps) if ps else None}")
    print('  shipping lines:', ship.most_common(8))
    fx=[r['order_subtotal_price']/r['order_subtotal_price_presentment'] for r in os_ if r['order_subtotal_price_presentment'] and r['order_subtotal_price']]
    if fx: fx.sort(); print('  implied NGN per presentment unit (median):', round(fx[len(fx)//2],1))
