"""Meta Ads (account 480225648142941) campaign x country x month, Jan 2025-Sep 2026. Purchases = pixel website purchases as reported by Meta.
Country = Meta delivery country. Reconciled against Shopify orders/net by shipping country (out/shopify_win_country.json)."""
from common import *
from meta_class import *
import collections, calendar
rows = load('meta_cmp_*.json')
for r in rows: r['ym'] = '%s-%02d' % (r['year_month'].split('|')[0], int(r['year_month'].split('|')[1])); r['date'] = r['ym'] + '-01'
P='actions_offsite_conversion_fb_pixel_purchase'; V='action_values_offsite_conversion_fb_pixel_purchase'
diff = sum(abs((r.get(P) or 0)-(r.get('actions_purchase') or 0)) for r in rows); print('pixel vs all purchase action diff:', diff)
def num(r,k): return r.get(k) or 0
A = collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    for w in window(r['date']) + [r['ym']]:
        for c in (cc(r['country']), 'ALL'):
            a = A[(w,c)]
            for k,n in (('spend','spend'),('impr','impressions'),('clicks','link_clicks'),('purch',P),('value',V)): a[k] += num(r,n)
shop = json.load(open(OUT+'/shopify_win_country.json')); shopm = json.load(open(OUT+'/shopify_month_country.json'))
print('country breakdown of all Meta spend Jan-Sep26:', {k[1]: round(v['spend']/1e6,1) for k,v in A.items() if k[0]=='JanSep26'})
res = {}
print('\nWINDOW x COUNTRY | spend | impr | clicks | cost/click | Meta purch | Meta value | cost/purch (Meta) | sales per ₦1 (Meta) | Shopify orders | Shopify net | Meta purch as % of Shopify orders | Shopify net per ₦1 of Meta')
for c in ['ALL','NG','UK','CA','US','Other']:
    for w in WINS:
        a = A.get((w,c));
        if not a: continue
        s = shop.get(str((w,c)), {})
        o = s.get('orders',0); n = s.get('net',0)
        row = dict(a, cpc=a['spend']/a['clicks'] if a['clicks'] else None, cpp=a['spend']/a['purch'] if a['purch'] else None,
                   roas=a['value']/a['spend'] if a['spend'] else None, shop_orders=o, shop_net=n,
                   claim=a['purch']/o if o else None, mer=n/a['spend'] if a['spend'] else None)
        res[f'{w}|{c}'] = row
        print(f"{c:5}{w:9} {a['spend']/1e6:7.1f}m {a['impr']/1e6:6.1f}m {a['clicks']:8.0f} {row['cpc'] or 0:6.0f} {a['purch']:6.0f} {a['value']/1e6:7.1f}m {row['cpp'] or 0:8,.0f} {row['roas'] or 0:5.2f} {o:6.0f} {n/1e6:7.1f}m {100*(row['claim'] or 0):5.0f}% {row['mer'] or 0:5.2f}")
dump('meta_win_country.json', res)
print('\nMONTHLY by country: spend ₦m / Meta purchases / Shopify orders / Shopify net per ₦1 Meta')
months = sorted({k[0] for k in A if len(k[0])==7})
for m in months:
    line = m
    for c in ['ALL','NG','UK','CA','US']:
        a = A.get((m,c), {}); s = shopm.get(str((m,c)), {})
        sp = a.get('spend',0)
        line += f" | {c} {sp/1e6:5.1f}m {a.get('purch',0):4.0f}p {s.get('orders',0):5.0f}o {(s.get('net',0)/sp if sp else 0):5.1f}x"
    print(line)
dump('meta_month_country.json', {f'{k[0]}|{k[1]}': dict(v) for k,v in A.items()})
