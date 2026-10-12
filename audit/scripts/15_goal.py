"""Test ₦1bn Q4 against Shopify actuals. Q3 2026 = Jul-Sep; best month on record = max monthly net since Jun 2024."""
from common import *
import json
S=json.load(open(OUT+'/shopify_win_country.json')); SM=json.load(open(OUT+'/shopify_month_country.json')); M=json.load(open(OUT+'/meta_win_country.json')); MM=json.load(open(OUT+'/meta_month_country.json'))
m24={r['year_month']:r['order_net_sales'] for r in load('shop_2024_monthly.json')}
months={k.split("'")[1]:v['net'] for k,v in SM.items() if "'ALL'" in k}
best=max(months.items(), key=lambda kv:kv[1]); print('best month on record (2025-26):', best, '| 2024 max:', max(m24.items(), key=lambda kv:kv[1]))
q3=S[str(('JulSep26','ALL'))]; q3m=M['JulSep26|ALL']; q4_25=sum(months[m] for m in ['2025-10','2025-11','2025-12']); q4_25o=sum(SM[str((m,'ALL'))]['orders'] for m in ['2025-10','2025-11','2025-12'])
days=92; target=1e9
print(f"Q3 2026: net ₦{q3['net']/1e6:.1f}m, orders {q3['orders']:.0f} ({q3['orders']/92:.1f}/day), AOV ₦{q3['aov']:,.0f}, Meta spend ₦{q3m['spend']/1e6:.1f}m, Shopify net per ₦1 Meta {q3m['mer']:.2f}")
print(f"Q4 2025 actual: net ₦{q4_25/1e6:.1f}m, orders {q4_25o:.0f}; Q4 2025 vs Q3 2025 ratio: {q4_25/S[str(('JanSep25','ALL'))]['net']*0+q4_25/sum(months[m] for m in ['2025-07','2025-08','2025-09']):.2f}")
need_orders=target/q3['aov']; print(f"₦1bn needs {need_orders:,.0f} orders at Q3 AOV = {need_orders/days:.0f}/day vs Q3 {q3['orders']/92:.1f}/day and best month {SM[str((best[0],'ALL'))]['orders']/31:.1f}/day")
print(f"Spend needed at Q3 return (₦{q3m['mer']:.2f} net per ₦1): ₦{target/q3m['mer']/1e6:.0f}m for the quarter = ₦{target/q3m['mer']/days/1e6:.2f}m/day vs Q3 ₦{q3m['spend']/92/1e6:.2f}m/day; at Jan-Sep return ({M['JanSep26|ALL']['mer']:.2f}): ₦{target/M['JanSep26|ALL']['mer']/1e6:.0f}m")
print(f"Multiple of Q3: {target/q3['net']:.2f}x; multiple of best quarter (Q4 2025 ₦{q4_25/1e6:.0f}m): {target/q4_25:.2f}x; multiple of best month x3: {target/(best[1]*3):.2f}x")
# stock: units sold in Q3 and Jan-Sep by product vs on hand
P=json.load(open(OUT+'/shopify_products.json')); I=json.load(open(OUT+'/inventory.json'))
onhand={}
for k,v in I.items():
    t=eval(k)[0]; onhand[t]=onhand.get(t,0)+sum(x for x in v.values() if isinstance(x,(int,float)))
print('\nproduct | units Q3 | units Jan-Sep | units/day Q3 | on hand (all warehouses) | days of cover at Q3 rate | units needed at 3.7x Q3')
mult=target/q3['net']
for p in ['MYSTIQUE','GOLDEN KISS','GODDESS','SWEET OUD','MINI SET','BLUSH BLOOM','THE OIL TRIO','PASSION','SEDUCTION','GOLDEN KISS - 10ML']:
    u3=P.get(str(('JulSep26','ALL',p)),{}).get('units',0); u9=P.get(str(('JanSep26','ALL',p)),{}).get('units',0); oh=onhand.get(p,0)
    print(f"{p:20} {u3:6.0f} {u9:6.0f} {u3/92:6.1f} {oh:6.0f} {oh/(u3/92) if u3 else 0:6.0f} {u3*mult:7.0f}")
