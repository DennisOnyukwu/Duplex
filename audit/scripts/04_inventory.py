"""Inventory on hand by product x location (Shopify products table, current snapshot pulled 2026-10-08). Cost per item field also checked."""
from common import *
import collections
rows = load('shop_inventory.json')
print(len(rows), 'rows; locations:', collections.Counter(r['product_variant_inventory_location_name'] for r in rows))
print('tracked flag:', collections.Counter((r['product_title'], r['product_variant_inventory_item_province_tracked']) for r in rows if r['product_variant_inventory_item_province_tracked']!='True'))
print('item cost non-zero:', sum(1 for r in rows if (r.get('product_variant_inventory_item_cost') or 0)>0))
seen=set(); T={}
for r in rows:
    k=(r['product_title'].upper(), r['product_variant_title'], r['product_variant_sku'], r['product_variant_inventory_location_name'])
    if k in seen: continue
    seen.add(k)
    T.setdefault((r['product_title'].upper(), r['product_variant_title'], r['product_variant_sku'], r['product_status'], r['product_variant_price'], r['product_variant_inventory_policy'], r['product_variant_inventory_item_province_tracked']), {})[r['product_variant_inventory_location_name']] = r['product_variant_inventory_available_quantity']
locs = sorted({k[3] for k in seen}, key=str)
print(f"{'product':26}{'variant':12}{'sku':14}{'status':9}{'price':>8} {'policy':6}{'trk':5}" + ''.join(f'{str(l)[:14]:>15}' for l in locs))
for k,v in sorted(T.items()):
    print(f'{k[0][:25]:26}{str(k[1])[:11]:12}{str(k[2])[:13]:14}{k[3][:8]:9}{k[4]:8,.0f} {str(k[5])[:6]:6}{str(k[6])[:4]:5}' + ''.join(f'{str(v.get(l,"")):>15}' for l in locs))
dump('inventory.json', {str(k):v for k,v in T.items()})
