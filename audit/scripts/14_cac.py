"""Cost of a new customer: Meta spend in the country ÷ Shopify first-time-customer orders shipped to that country (same window). Also Meta-reported cost per purchase for comparison. Plus repeat behaviour: share of 2026 orders from returning customers."""
from common import *
import json
S=json.load(open(OUT+'/shopify_win_country.json')); M=json.load(open(OUT+'/meta_win_country.json'))
print('window country | Meta spend ₦m | Shopify orders | new-customer orders | cost per new customer ₦ | cost per order (all) ₦ | Meta cost/purchase ₦ | AOV ₦')
out={}
for c in ['NG','UK','CA','US','ALL']:
    for w in WINS:
        s=S.get(str((w,c))); m=M.get(f'{w}|{c}')
        if not s or not m or not s.get('orders'): continue
        new=s.get('new',0); sp=m['spend']
        out[f'{w}|{c}']=dict(spend=sp, orders=s['orders'], new=new, cpnc=sp/new if new else None, cpo=sp/s['orders'], meta_cpp=m['cpp'], aov=s['aov'])
        print(f"{w:9}{c:4} {sp/1e6:7.1f} {s['orders']:6.0f} {new:6.0f} {sp/new if new else 0:9,.0f} {sp/s['orders']:9,.0f} {m['cpp'] or 0:9,.0f} {s['aov']:9,.0f}")
dump('cac.json', out)
