"""Meta spend/reach by Nigerian region (no purchase breakdown available by region) and GA4 by city & channel, Jan-Sep 2026."""
import json,collections,os
from common import OUT,dump
D=os.path.join(os.path.dirname(__file__),'..','data')
def load(p):
    raw=open(os.path.join(D,p)).read(); return json.loads(raw[raw.find('{'):raw.rfind('}')+1])['result']
m=load('meta_ng_region_2026.json')
agg=collections.defaultdict(lambda: dict(spend=0.0,imp=0,reach=0))
q3=collections.defaultdict(float)
for r in m:
    a=agg[r['region']]; a['spend']+=float(r['spend'] or 0); a['imp']+=int(r['impressions'] or 0); a['reach']+=int(r['reach'] or 0)
    if r['year_month'] in ('2026|7','2026|8','2026|9'): q3[r['region']]+=float(r['spend'] or 0)
tot=sum(a['spend'] for a in agg.values()); tq=sum(q3.values())
print(f"META NG Jan-Sep26 spend {tot/1e6:.1f}m")
print(f"{'region':28}{'spend ₦m':>9}{'share':>7}{'Q3 share':>9}{'reach k':>8}{'freq':>6}{'₦/reach':>8}")
meta={}
for k,a in sorted(agg.items(),key=lambda kv:-kv[1]['spend'])[:14]:
    meta[k]=dict(spend=a['spend'],share=a['spend']/tot,q3share=q3[k]/tq,reach=a['reach'],freq=a['imp']/a['reach'] if a['reach'] else 0)
    print(f"{k[:28]:28}{a['spend']/1e6:9.2f}{a['spend']/tot*100:6.1f}%{q3[k]/tq*100:8.1f}%{a['reach']/1e3:8.0f}{a['imp']/a['reach'] if a['reach'] else 0:6.1f}{a['spend']/a['reach'] if a['reach'] else 0:8.0f}")
g=load('ga4_ng_city_channel_2026.json')
city=collections.defaultdict(lambda: collections.defaultdict(lambda: dict(s=0,p=0)))
for r in g:
    a=city[r['city']][r['session_default_channel_group']]; a['s']+=int(r['sessions'] or 0); a['p']+=int(r['ecommerce_purchases'] or 0)
def tot_c(c): return sum(v['s'] for v in city[c].values()), sum(v['p'] for v in city[c].values())
TS=sum(tot_c(c)[0] for c in city); TP=sum(tot_c(c)[1] for c in city)
print(f"\nGA4 NG Jan-Sep26 sessions {TS} purchases {TP}")
print(f"{'city':16}{'sess':>8}{'share':>7}{'purch':>6}{'share':>7}{'conv%':>6} | paid soc conv% | org soc conv% | org soc % of purch | paid % of sess")
ga={}
for c in sorted(city,key=lambda c:-tot_c(c)[0])[:16]:
    s,p=tot_c(c); ps=city[c].get('Paid Social',{'s':0,'p':0}); os_=city[c].get('Organic Social',{'s':0,'p':0})
    ga[c]=dict(sessions=s,purchases=p,conv=p/s if s else 0,paid_conv=ps['p']/ps['s'] if ps['s'] else 0,org_conv=os_['p']/os_['s'] if os_['s'] else 0,org_share_p=os_['p']/p if p else 0,paid_share_s=ps['s']/s if s else 0)
    print(f"{str(c)[:16]:16}{s:8d}{s/TS*100:6.1f}%{p:6d}{p/TP*100:6.1f}%{p/s*100 if s else 0:6.2f} | {ps['p']/ps['s']*100 if ps['s'] else 0:13.2f} | {os_['p']/os_['s']*100 if os_['s'] else 0:12.2f} | {os_['p']/p*100 if p else 0:17.0f}% | {ps['s']/s*100 if s else 0:13.0f}%")
dump('ng_region_meta_ga4.json',dict(meta=meta,ga4=ga))
