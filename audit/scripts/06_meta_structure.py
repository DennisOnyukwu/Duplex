"""Campaign structure by month (all countries): campaigns with spend, average daily spend per campaign, share of spend in campaigns with <7 Meta-reported purchases that month.
Then cost per Meta-reported purchase by creative type and by product, within each country, Jan-Sep 2026 (20+ purchases needed to recommend)."""
from common import *
from meta_class import *
import collections, calendar
rows = load('meta_cmp_*.json')
P='actions_offsite_conversion_fb_pixel_purchase'; V='action_values_offsite_conversion_fb_pixel_purchase'
for r in rows: y,m = r['year_month'].split('|'); r['ym']=f'{y}-{int(m):02d}'; r['date']=r['ym']+'-01'
C = collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    k=(r['ym'], r['campaign_id']); C[k]['spend']+=r.get('spend') or 0; C[k]['purch']+=r.get(P) or 0; C[k]['name']=r['campaign']
print('month   camps  avg daily ₦/camp  spend ₦m  %spend in camps <7 purch')
struct={}
for m in sorted({k[0] for k in C}):
    cs=[v for k,v in C.items() if k[0]==m and v['spend']>0]
    days=calendar.monthrange(int(m[:4]),int(m[5:]))[1]
    sp=sum(v['spend'] for v in cs); low=sum(v['spend'] for v in cs if v['purch']<7)
    struct[m]=dict(camps=len(cs), avg_daily=sp/len(cs)/days, spend=sp, low_share=low/sp)
    print(f"{m}  {len(cs):4d}  {sp/len(cs)/days:12,.0f}  {sp/1e6:7.1f}  {100*low/sp:5.0f}%")
dump('meta_structure.json', struct)
for w in ['JanSep26','JanSep25']:
    ms=[m for m in struct if w in window(m+'-01')]
    sp=sum(struct[m]['spend'] for m in ms); low=sum(struct[m]['spend']*struct[m]['low_share'] for m in ms)
    print(w, 'avg camps/month', sum(struct[m]['camps'] for m in ms)/len(ms), 'low-purchase share', low/sp)
ms=[m for m in struct if 'AprJun26' in window(m+'-01')]; print('AprJun26 low share', sum(struct[m]['spend']*struct[m]['low_share'] for m in ms)/sum(struct[m]['spend'] for m in ms), 'camps', sum(struct[m]['camps'] for m in ms)/3)
ms=[m for m in struct if 'JulSep26' in window(m+'-01')]; print('JulSep26 low share', sum(struct[m]['spend']*struct[m]['low_share'] for m in ms)/sum(struct[m]['spend'] for m in ms), 'camps', sum(struct[m]['camps'] for m in ms)/3)

def table(keyfn, label):
    T=collections.defaultdict(lambda: collections.defaultdict(float))
    for r in rows:
        if 'JanSep26' not in window(r['date']): continue
        c=cc(r['country']);
        if c=='Other': continue
        k=(c, keyfn(r['campaign'])); T[k]['spend']+=r.get('spend') or 0; T[k]['purch']+=r.get(P) or 0; T[k]['value']+=r.get(V) or 0
    out={}
    for c in ['NG','UK','CA','US']:
        tot=sum(v['spend'] for k,v in T.items() if k[0]==c)
        print(f'\n== {label} | {c} (Jan-Sep 2026, Meta-reported)')
        for k,v in sorted([(k,v) for k,v in T.items() if k[0]==c], key=lambda kv:-kv[1]['spend']):
            cpp = v['spend']/v['purch'] if v['purch'] else None
            ok = 'OK' if v['purch']>=20 else 'insufficient data'
            out[f'{c}|{k[1]}']=dict(v, cpp=cpp, share=v['spend']/tot, ok=ok)
            print(f"{k[1]:24} spend {v['spend']/1e6:6.2f}m ({100*v['spend']/tot:3.0f}%) purch {v['purch']:5.0f} cost/purch {cpp or 0:9,.0f} sales/₦1 {v['value']/v['spend'] if v['spend'] else 0:5.2f} {ok}")
    return out
dump('meta_creative.json', table(creative, 'CREATIVE TYPE'))
dump('meta_product.json', table(product, 'PRODUCT'))
# heritage-named campaigns share of export-market spend
H=collections.defaultdict(lambda: [0,0])
for r in rows:
    for w in window(r['date']):
        c=cc(r['country']);
        if c in ('UK','CA','US'): H[(w,c)][1]+=r.get('spend') or 0; H[(w,c)][0]+= (r.get('spend') or 0) if heritage(r['campaign']) else 0
print('\nHeritage-named campaign share of spend:', {f'{k[0]}|{k[1]}': f'{100*v[0]/v[1]:.1f}% ({v[0]/1e6:.2f}m)' for k,v in H.items() if v[1]})
dump('meta_heritage.json', {f'{k[0]}|{k[1]}': v for k,v in H.items()})
