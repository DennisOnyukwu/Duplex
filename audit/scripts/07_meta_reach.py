"""Meta reach & frequency by month and country, 2026 (monthly reach is de-duplicated within month only; 'unknown' country rows of <₦20 dropped)."""
from common import *
rows=[r for r in load('meta_reach_2026.json') if r['country']!='unknown']
out={}
for c in ['Nigeria','United Kingdom','Canada','United States']:
    rs=sorted([r for r in rows if r['country']==c], key=lambda r:int(r['year_month'].split('|')[1]))
    fr=[r['frequency'] for r in rs]
    out[cc(c)]={r['year_month']:dict(reach=r['reach'],freq=r['frequency'],cpm_reach=r['spend']/r['reach']*1000) for r in rs}
    print(cc(c), 'freq by month', [round(f,1) for f in fr], '| months freq>=5:', sum(f>=5 for f in fr), 'of', len(fr), '| median', sorted(fr)[len(fr)//2])
    print('   reach', [r['reach'] for r in rs])
dump('meta_reach.json', out)
