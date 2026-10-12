"""Nigeria by state and by Lagos zone. Source: data/shop_ng_city_2025.json, shop_ng_city_2026.json
(Shopify orders shipped to Nigeria, first row per order, cancelled excluded)."""
import json, collections, re, os
from common import OUT, dump
D=os.path.join(os.path.dirname(__file__),'..','data')
def load(p):
    raw=open(os.path.join(D,p)).read(); return json.loads(raw[raw.find('{'):raw.rfind('}')+1])['result']
rows=load('shop_ng_city_2026.json')+load('shop_ng_city_2025.json')
orders={}
for r in rows:
    if r.get('order_cancelled_at'): continue
    oid=r['order_id']; net=float(r.get('order_net_sales') or 0)
    if oid in orders: orders[oid]['net']+=net; continue
    orders[oid]=dict(date=r['date'],city=(r.get('order_shipping_address_city') or '').strip().lower(),
                     prov=(r.get('order_shipping_address_province') or '').strip(),net=net,new=(r.get('order_new_or_returning_customer')=='new'))
PROV={'Abuja Federal Capital Territory':'Abuja (FCT)'}
def state(o): return PROV.get(o['prov'],o['prov'] or 'Unknown')
ISLAND=r'lekki|victoria island|\bvi\b|ikoyi|ajah|sangotedo|ikota|ikate|eti.?osa|lagos island|oniru|chevron|osapa|agungi|jakande|abraham adesanya|awoyaya|lakowe|ibeju|epe|banana|ologolo|igbo efon|elegushi|orchid|vgc|ikota'
MAINLAND=r'ikeja|surulere|yaba|gbagada|ogba|shomolu|somolu|maryland|magodo|ketu|ilupeju|ojodu|mushin|isolo|okota|festac|amuwo|ogudu|kosofe|lagos mainland|anthony|ojota|oshodi|ajao|apapa|ebute|palmgrove|bariga|ikosi|ojuelegba|ogunlana|mende|opebi|allen|oregun|omole|alausa|gra ikeja|berger|agidingbi|akoka|ilasamaja|ago palace|ejigbo|satellite|orile|iganmu|mile 2|ijesha|aguda|iwaya|obanikoro|ilaje|akowonjo'
OUTER=r'ikorodu|alimosho|agege|egbeda|ipaja|ikotun|igando|abule egba|iyana|ojo|badagry|sango|ifako|ayobo|command|meiran|ojokoro|dopemu|idimu|isheri|lasu|okokomaiko|alakuko|ikola|mowe|ibafo|arepo|magboro|ota|akute|alagbado|abule ado|agbara'
def zone(o):
    if state(o)!='Lagos': return None
    c=o['city']
    if re.search(ISLAND,c): return 'Lagos Island side'
    if re.search(MAINLAND,c): return 'Lagos Mainland'
    if re.search(OUTER,c): return 'Lagos outer suburbs'
    return 'Lagos (no area given)'
def win(d):
    y,m=int(d[:4]),int(d[5:7]); w=[]
    if y==2025 and m<=9: w.append('JanSep25')
    if y==2026 and m<=9: w.append('JanSep26')
    if y==2025 and m>=10: w.append('OctDec25')
    if y==2026 and 4<=m<=6: w.append('AprJun26')
    if y==2026 and 7<=m<=9: w.append('JulSep26')
    return w
def agg(keyf):
    t=collections.defaultdict(lambda: collections.defaultdict(lambda: dict(orders=0,net=0.0,new=0)))
    for o in orders.values():
        k=keyf(o)
        if k is None: continue
        for w in win(o['date']):
            a=t[w][k]; a['orders']+=1; a['net']+=o['net']; a['new']+=o['new']
    out={}
    for w,d in t.items():
        tot=sum(v['net'] for v in d.values())
        out[w]={k:dict(v,share=round(v['net']/tot*100,1),aov=round(v['net']/v['orders']) if v['orders'] else 0) for k,v in sorted(d.items(),key=lambda kv:-kv[1]['net'])}
    return out
by_state=agg(state); by_zone=agg(zone)
# monthly for top states
mon=collections.defaultdict(lambda: collections.defaultdict(lambda: dict(orders=0,net=0.0,new=0)))
for o in orders.values():
    a=mon[o['date'][:7]][state(o)]; a['orders']+=1; a['net']+=o['net']; a['new']+=o['new']
dump('ng_cities.json',dict(by_state=by_state,by_zone=by_zone,monthly={m:dict(d) for m,d in sorted(mon.items())}))
def show(title,t,top=12):
    print('\n==',title)
    ws=['JanSep25','JanSep26','OctDec25','AprJun26','JulSep26']
    print(f"{'':28}"+''.join(f"{w:>22}" for w in ws))
    keys=list(t['JanSep26'].keys())[:top]
    for k in keys:
        print(f"{k[:28]:28}"+''.join(f"{t[w].get(k,{}).get('net',0)/1e6:8.1f}m {t[w].get(k,{}).get('orders',0):5d} {t[w].get(k,{}).get('share',0):5.1f}%" for w in ws))
    print(f"{'new-customer share JanSep26':28}"+' '.join(f"{k[:10]}:{round(t['JanSep26'][k]['new']/t['JanSep26'][k]['orders']*100)}%" for k in keys))
    print(f"{'AOV JanSep26':28}"+' '.join(f"{k[:10]}:{t['JanSep26'][k]['aov']:,}" for k in keys))
show('BY STATE (net ₦m, orders, share of NG)',by_state)
show('LAGOS BY ZONE',by_zone,6)
print('\nunclassified Lagos cities (JanSep26 top):')
c=collections.Counter(o['city'] for o in orders.values() if zone(o)=='Lagos (no area given)' and 'JanSep26' in win(o['date']))
print(c.most_common(40))
print('\nMONTHLY net ₦m: Lagos / Abuja / Rivers / rest')
for m,d in sorted(mon.items()):
    L=d.get('Lagos',{}).get('net',0);A=d.get('Abuja (FCT)',{}).get('net',0);R=d.get('Rivers',{}).get('net',0);T=sum(v['net'] for v in d.values())
    print(m,f"{L/1e6:6.1f} {A/1e6:6.1f} {R/1e6:6.1f} {(T-L-A-R)/1e6:6.1f}  total {T/1e6:6.1f}  new: L {d.get('Lagos',{}).get('new',0)} A {d.get('Abuja (FCT)',{}).get('new',0)} R {d.get('Rivers',{}).get('new',0)}")
