"""Derived comparisons used in the document: year and momentum changes, country shares, scenario arithmetic, scorecard values."""
from common import *
import json
S=json.load(open(OUT+'/shopify_win_country.json')); SM=json.load(open(OUT+'/shopify_month_country.json')); M=json.load(open(OUT+'/meta_win_country.json')); MM=json.load(open(OUT+'/meta_month_country.json'))
C=json.load(open(OUT+'/cac.json')); G=json.load(open(OUT+'/ga4_funnel.json')); E=json.load(open(OUT+'/email.json')); ST=json.load(open(OUT+'/meta_structure.json'))
def pct(a,b): return (a/b-1)*100 if b else None
print('== Shopify changes')
for c in ['ALL','NG','UK','CA','US']:
    a=S[str(('JanSep26',c))]; y=S.get(str(('JanSep25',c))); q2=S[str(('AprJun26',c))]; q3=S[str(('JulSep26',c))]
    print(f"{c}: net Jan-Sep26 ₦{a['net']/1e6:.1f}m ({pct(a['net'],y['net']) if y else None} % vs 25) orders {a['orders']:.0f} ({pct(a['orders'],y['orders']) if y else None}%) AOV ₦{a['aov']:,.0f} ({pct(a['aov'],y['aov']) if y else None}%) | Q3 vs Q2: net {pct(q3['net'],q2['net']):.0f}% orders {pct(q3['orders'],q2['orders']):.0f}% | share of Jan-Sep26 net {100*a['net']/S[str(('JanSep26','ALL'))]['net']:.1f}% | Q3 monthly avg ₦{q3['net']/3/1e6:.1f}m")
print('== Meta changes')
for c in ['ALL','NG','UK','CA','US']:
    a=M[f'JanSep26|{c}']; y=M.get(f'JanSep25|{c}'); q2=M[f'AprJun26|{c}']; q3=M[f'JulSep26|{c}']
    print(f"{c}: spend ₦{a['spend']/1e6:.1f}m ({pct(a['spend'],y['spend']) if y and y['spend'] else None}% vs 25) share {100*a['spend']/M['JanSep26|ALL']['spend']:.0f}% | Shopify net per ₦1: {a['mer']:.2f} (25: {y['mer'] if y else None}) Q2 {q2['mer']:.2f} Q3 {q3['mer']:.2f} | Meta cost/purchase ₦{a['cpp']:,.0f} Q3 ₦{q3['cpp']:,.0f} | claim {100*a['claim']:.0f}% Q3 {100*q3['claim']:.0f}%")
print('Sep 2026 Meta purchases vs Shopify orders:', MM['2026-09|ALL']['purch'], SM[str(('2026-09','ALL'))]['orders'], '| NG', MM['2026-09|NG']['purch'], SM[str(('2026-09','NG'))]['orders'], '| UK', MM['2026-09|UK']['purch'], SM[str(('2026-09','UK'))]['orders'],'| CA', MM['2026-09|CA']['purch'], SM[str(('2026-09','CA'))]['orders'])
print('Meta spend Jan-Sep26 export share:', 100*(M['JanSep26|UK']['spend']+M['JanSep26|CA']['spend']+M['JanSep26|US']['spend'])/M['JanSep26|ALL']['spend'], '| export share of Shopify net:', 100*(S[str(('JanSep26','UK'))]['net']+S[str(('JanSep26','CA'))]['net']+S[str(('JanSep26','US'))]['net'])/S[str(('JanSep26','ALL'))]['net'])
print('== cost per new customer vs AOV')
for c in ['NG','UK','CA','US']:
    for w in ['JanSep26','JulSep26','JanSep25']:
        x=C.get(f'{w}|{c}')
        if x: print(f"{c} {w}: ₦{x['cpnc']:,.0f} per new customer = {100*x['cpnc']/x['aov']:.0f}% of AOV ₦{x['aov']:,.0f}; new customers {x['new']}")
print('== seasonality & scenarios')
q3_25=sum(SM[str((m,'ALL'))]['net'] for m in ['2025-07','2025-08','2025-09']); q4_25=sum(SM[str((m,'ALL'))]['net'] for m in ['2025-10','2025-11','2025-12'])
q3_26=S[str(('JulSep26','ALL'))]['net']; q3_26o=S[str(('JulSep26','ALL'))]['orders']
r=q4_25/q3_25; print(f"Q4/Q3 ratio 2025: {r:.3f} (Q3 25 ₦{q3_25/1e6:.1f}m, Q4 25 ₦{q4_25/1e6:.1f}m)")
base=q3_26*r; print(f"BASE: Q3 26 ₦{q3_26/1e6:.1f}m x {r:.2f} = ₦{base/1e6:.0f}m, orders {q3_26o*r:.0f} ({q3_26o*r/92:.0f}/day), Meta spend flat at Q3 ₦{M['JulSep26|ALL']['spend']/1e6:.1f}m")
# stretch: NG spend +50% at Q3 NG return, export flat; email/CRO uplifts not assumed
ng3=M['JulSep26|NG']; add=ng3['spend']*0.5; stretch=base+add*ng3['mer']
print(f"STRETCH: + ₦{add/1e6:.1f}m extra Nigeria spend at Q3 Nigeria return {ng3['mer']:.2f} = +₦{add*ng3['mer']/1e6:.0f}m -> ₦{stretch/1e6:.0f}m; total Meta spend ₦{(M['JulSep26|ALL']['spend']+add)/1e6:.1f}m; orders at Q3 AOV {stretch/S[str(('JulSep26','ALL'))]['aov']:.0f}")
print(f"AMBITION ₦1bn: gap vs stretch ₦{(1e9-stretch)/1e6:.0f}m; at Q3 blended return {M['JulSep26|ALL']['mer']:.2f} needs further ₦{(1e9-stretch)/M['JulSep26|ALL']['mer']/1e6:.0f}m spend; total ₦{((1e9-stretch)/M['JulSep26|ALL']['mer']+M['JulSep26|ALL']['spend']+add)/1e6:.0f}m")
print('best month orders/day Oct 2025:', SM[str(('2025-10','ALL'))]['orders']/31, 'Oct 2025 Meta spend', MM['2025-10|ALL']['spend']/1e6, 'net per ₦1', SM[str(('2025-10','ALL'))]['net']/MM['2025-10|ALL']['spend'])
print('== scorecard today (Q3 2026 unless stated)')
print('monthly net Sep 2026', SM[str(('2026-09','ALL'))]['net']/1e6, '| orders/day Q3', q3_26o/92, '| Shopify net per ₦1 Meta Q3', M['JulSep26|ALL']['mer'], '| NG cost per new customer Q3', C['JulSep26|NG']['cpnc'], '| export cost per new customer Q3 (UK/CA/US)', (M['JulSep26|UK']['spend']+M['JulSep26|CA']['spend']+M['JulSep26|US']['spend'])/(C['JulSep26|UK']['new']+C['JulSep26|CA']['new']+C['JulSep26|US']['new']))
print('low-purchase spend share Jul-Sep', 'see 06 output 36%', '| email share of orders Q3 (Shopify last visit)', 52/2185*100, '| checkout->purchase Q3', 100*G['JulSep26|ALL']['ecommerce_purchases']/G['JulSep26|ALL']['checkouts'], '| AC coverage Sep 42.5%', '| reviews/month May-Sep 11')
print('returning share Q3 ALL', 100*(1-S[str(('JulSep26','ALL'))]['new_share']), 'Jan-Sep', 100*(1-S[str(('JanSep26','ALL'))]['new_share']), '2025', 100*(1-S[str(('JanSep25','ALL'))]['new_share']))
