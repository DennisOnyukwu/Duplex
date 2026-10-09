"""Klaviyo flows (conversion metric Placed Order WtBUYg, Klaviyo attribution) rebuilt from monthly pulls; campaigns from campaign reports. Windows: Jan-Sep26 (sum of 9 monthly pulls), AprJun26, JulSep26, JanSep25 (= 2025 Q3; Q1/Q2 returned no flows)."""
from common import *
import collections, json
A=json.load(open(D+'/klaviyo_flow_agg.json'))
months=[f'2026-{m:02d}' for m in range(1,10)]
def agg(keys):
    T=collections.defaultdict(lambda:[0,0,0,0,0.0])
    for k in keys:
        for f,v in A.get(k,{}).items():
            if f.startswith('_'): continue
            for i in range(5): T[f][i]+=v[i]
    return T
W={'JanSep26':agg(months),'AprJun26':agg(months[3:6]),'JulSep26':agg(months[6:9]),'JanSep25':agg(['2025Q3']),'JanApr26 (old flows)':agg(months[:4]),'MaySep26 (rebuilt flows)':agg(months[4:9])}
out={}
for w,T in W.items():
    print(f'\n== {w}: flow | recipients | opens | clicks | orders | revenue ₦ | rev/recipient')
    tot=[0,0,0,0,0.0]
    for f,v in sorted(T.items(), key=lambda kv:-kv[1][4]):
        print(f"{f.split('|')[1]:52} {v[0]:6.0f} {v[1]:6.0f} {v[2]:5.0f} {v[3]:4.0f} {v[4]/1e6:6.2f}m {v[4]/v[0] if v[0] else 0:6.0f}")
        for i in range(5): tot[i]+=v[i]
        out[f'{w}|{f}']=v
    print(f"{'TOTAL':52} {tot[0]:6.0f} {tot[1]:6.0f} {tot[2]:5.0f} {tot[3]:4.0f} {tot[4]/1e6:6.2f}m {tot[4]/tot[0] if tot[0] else 0:6.0f}")
    out[f'{w}|TOTAL']=tot
# abandoned checkout coverage: flow recipients vs GA4 begin_checkout by month
ga=json.load(open(OUT+'/ga4_month.json'))
print('\nmonth | abandoned-checkout emails (recipients, all AC flows) | GA4 checkouts started | coverage')
cov={}
for m in months:
    rec=sum(v[0] for f,v in A.get(m,{}).items() if 'Abandoned Checkout' in f)
    chk=ga.get(f'{m}|ALL',{}).get('checkouts',0)
    cov[m]=(rec,chk,rec/chk if chk else None); print(f"{m} {rec:6.0f} {chk:6.0f} {100*rec/chk if chk else 0:5.1f}%")
out['coverage']=cov
# campaigns
def camp(file):
    d=json.load(open(D+'/'+file))['data']['attributes']['results']
    T=[0,0,0,0,0.0]; n=0
    for r in d:
        s=r['statistics']; n+=1
        for i,k in enumerate(['recipients','opens_unique','clicks_unique','conversions','conversion_value']): T[i]+=s.get(k) or 0
    return n,T
n,T=camp('klaviyo_campaigns_2026.json'); print(f'\nCAMPAIGNS JanSep26: {n} sends | recipients {T[0]:.0f} opens {T[1]:.0f} clicks {T[2]:.0f} orders {T[3]:.0f} revenue {T[4]/1e6:.2f}m rev/recipient {T[4]/T[0]:.0f}'); out['campaigns|JanSep26']=[n]+T
rows=json.load(open(D+'/klaviyo_campaigns_2025_compact.json'))['rows']; T=[sum(r[i] for r in rows) for i in range(1,6)]
print(f'CAMPAIGNS JanSep25: {len(rows)} sends | recipients {T[0]:.0f} opens {T[1]:.0f} clicks {T[2]:.0f} orders {T[3]:.0f} revenue {T[4]/1e6:.2f}m rev/recipient {T[4]/T[0]:.0f}'); out['campaigns|JanSep25']=[len(rows)]+T
# campaigns by window 2026 using send_time
import datetime
d=json.load(open(D+'/klaviyo_campaigns_2026.json'))['data']['attributes']['results']
for w,(a,b) in {'AprJun26':('2026-04-01','2026-06-30'),'JulSep26':('2026-07-01','2026-09-30')}.items():
    T=[0,0,0,0,0.0]; n=0
    for r in d:
        st=r['campaign_details']['attributes']['scheduled_at'][:10]
        if a<=st<=b:
            n+=1; s=r['statistics']
            for i,k in enumerate(['recipients','opens_unique','clicks_unique','conversions','conversion_value']): T[i]+=s.get(k) or 0
    print(f'CAMPAIGNS {w}: {n} sends | recipients {T[0]:.0f} orders {T[3]:.0f} revenue {T[4]/1e6:.2f}m rev/recipient {T[4]/T[0] if T[0] else 0:.0f}'); out[f'campaigns|{w}']=[n]+T
W=json.load(open(D+'/klaviyo_widget_metrics.json')); print('reviews widget impressions by month Jan-Sep26:', W['impression_reviewsWidget_count'], '| review submissions:', W['submitted_review_count'])
dump('email.json', out)
