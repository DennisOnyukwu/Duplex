#!/usr/bin/env python3
"""
Meta Ads Audit - stage 3 analysis tables (Part 4), per scope.

Computes, for a scope of ads (or the whole account):
    funnel, audience, ad format, market and objective breakdowns;
    learning phase and weekly conversion volume; spend concentration;
    monthly trend; Z10 overlap re-tested within each market;
    status of the ad sets behind Z1 / Z12.

Usage:
    python analyse.py <fact.csv> <ad_meta.csv> <out.json> [--scope ids.txt] [--zingers z.csv]
"""
import sys
import csv
import json
from collections import defaultdict
from datetime import date, timedelta


def f(v):
    try:
        return float(v or 0)
    except ValueError:
        return 0.0


def main():
    argv = sys.argv[1:]
    opts, args, i = {}, [], 0
    while i < len(argv):
        if argv[i].startswith('--'):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            args.append(argv[i])
            i += 1
    fact_all = list(csv.DictReader(open(args[0], encoding='utf-8')))
    meta = {r['Ad ID']: r for r in csv.DictReader(open(args[1], encoding='utf-8'))}
    out = args[2]
    if '--scope' in opts:
        ids = {l.strip() for l in open(opts['--scope']) if l.strip()}
        fact = [r for r in fact_all if r['Ad ID'] in ids]
    else:
        fact = fact_all

    acct_spend = sum(f(r['Amount spent']) for r in fact_all)
    acct_value = sum(f(r['Purchase value']) for r in fact_all)
    acct_purch = sum(f(r['Purchases']) for r in fact_all)
    spend = sum(f(r['Amount spent']) for r in fact)
    dmax = max(date.fromisoformat(r['Date']) for r in fact_all)

    def agg(keyfn, rows=fact):
        a = defaultdict(lambda: {'spend': 0.0, 'impr': 0.0, 'lc': 0.0, 'purch': 0.0, 'value': 0.0,
                                 'ads': set(), 'adsets': set()})
        for r in rows:
            x = a[keyfn(r)]
            x['spend'] += f(r['Amount spent'])
            x['impr'] += f(r['Impressions'])
            x['lc'] += f(r['Link clicks'])
            x['purch'] += f(r['Purchases'])
            x['value'] += f(r['Purchase value'])
            x['ads'].add(r['Ad ID'])
            x['adsets'].add(r['Ad Set ID'])
        tot = sum(x['spend'] for x in a.values()) or 1
        res = []
        for k, x in sorted(a.items(), key=lambda kv: -kv[1]['spend']):
            res.append({
                'key': k, 'spend': round(x['spend'], 2), 'share': round(x['spend'] / tot, 4),
                'purchases': x['purch'], 'value': round(x['value'], 2),
                'roas': round(x['value'] / x['spend'], 2) if x['spend'] else None,
                'cpa': round(x['spend'] / x['purch'], 2) if x['purch'] else None,
                'cpm': round(x['spend'] / x['impr'] * 1000, 2) if x['impr'] else None,
                'ctr': round(x['lc'] / x['impr'], 4) if x['impr'] else None,
                'cvr': round(x['purch'] / x['lc'], 4) if x['lc'] else None,
                'ads': len(x['ads']), 'adsets': len(x['adsets']),
            })
        return res

    R = {
        'scope_spend': round(spend, 2), 'account_spend': round(acct_spend, 2),
        'account_roas': round(acct_value / acct_spend, 2), 'account_cpa': round(acct_spend / acct_purch, 2),
        'rows': len(fact), 'ads': len({r['Ad ID'] for r in fact}),
        'adsets': len({r['Ad Set ID'] for r in fact}), 'campaigns': len({r['Campaign ID'] for r in fact}),
        'totals': agg(lambda r: 'Total')[0],
        'funnel': agg(lambda r: r['Funnel Stage']),
        'audience': agg(lambda r: r['Audience']),
        'format': agg(lambda r: r['Ad Format']),
        'market': agg(lambda r: r.get('Market', '')),
        'objective': agg(lambda r: r['Objective'] or '(none)'),
        'monthly': sorted(agg(lambda r: r['Date'][:7]), key=lambda x: x['key']),
        'market_format': agg(lambda r: f"{r.get('Market', '')} | {r['Ad Format']}"),
        'market_audience': agg(lambda r: f"{r.get('Market', '')} | {r['Audience']}"),
        'opt_goal': agg(lambda r: meta.get(r['Ad ID'], {}).get('Optimisation goal', 'Data not available')),
        'learning': agg(lambda r: meta.get(r['Ad ID'], {}).get('Learning phase') or '(not reported)'),
        'status': agg(lambda r: meta.get(r['Ad ID'], {}).get('Delivery status', 'Data not available')),
    }

    # Weekly conversion volume per active ad set (last 7 days).
    cut = (dmax - timedelta(days=6)).isoformat()
    wk = defaultdict(lambda: {'spend': 0.0, 'purch': 0.0, 'name': '', 'campaign': ''})
    for r in fact:
        if r['Date'] >= cut:
            x = wk[r['Ad Set ID']]
            x['spend'] += f(r['Amount spent'])
            x['purch'] += f(r['Purchases'])
            x['name'], x['campaign'] = r['Ad Set Name'], r['Campaign Name']
    active = {k: v for k, v in wk.items() if v['spend'] > 0}
    below = {k: v for k, v in active.items() if v['purch'] < 50}
    R['learning_phase'] = {
        'window': f"{cut} to {dmax.isoformat()}",
        'active_adsets': len(active), 'below_50': len(below),
        'share_below': round(len(below) / len(active), 4) if active else None,
        'spend_below': round(sum(v['spend'] for v in below.values()), 2),
        'week_spend': round(sum(v['spend'] for v in active.values()), 2),
        'week_purchases': sum(v['purch'] for v in active.values()),
        'max_weekly_purchases': max((v['purch'] for v in active.values()), default=0),
        'top_weekly': sorted(([v['campaign'], round(v['spend'], 2), v['purch']] for v in active.values()),
                             key=lambda x: -x[1])[:15],
    }
    # Weekly purchases per ad set across the whole window (how many ad-set-weeks ever clear 50).
    wkly = defaultdict(float)
    for r in fact:
        d = date.fromisoformat(r['Date'])
        wkly[(r['Ad Set ID'], (d - timedelta(days=d.weekday())).isoformat())] += f(r['Purchases'])
    R['learning_phase']['adset_weeks'] = len(wkly)
    R['learning_phase']['adset_weeks_50plus'] = sum(1 for v in wkly.values() if v >= 50)

    # Spend concentration (ad set level, share of scope spend).
    ads_ = agg(lambda r: r['Ad Set ID'])
    names = {}
    for r in fact:
        names[r['Ad Set ID']] = f"{r['Ad Set Name']} [{r['Campaign Name']}]"
    R['concentration'] = {
        'adsets': len(ads_),
        'top5_share': round(sum(x['share'] for x in ads_[:5]), 4),
        'top10_share': round(sum(x['share'] for x in ads_[:10]), 4),
        'under_1pct': sum(1 for x in ads_ if x['share'] < 0.01),
        'largest': [names[ads_[0]['key']], ads_[0]['spend'], ads_[0]['share']] if ads_ else None,
        'top10': [[names[x['key']], x['spend'], x['share'], x['purchases'], x['roas']] for x in ads_[:10]],
    }
    R['campaign_concentration'] = agg(lambda r: r['Campaign Name'])[:25]

    # Campaign lifecycle: how long campaigns live, how many launched per month.
    life = defaultdict(set)
    for r in fact:
        if f(r['Amount spent']) > 0:
            life[r['Campaign ID']].add(r['Date'])
    days = sorted(len(v) for v in life.values())
    launches = defaultdict(int)
    for v in life.values():
        launches[min(v)[:7]] += 1
    R['campaign_life'] = {
        'campaigns': len(days), 'median_days': days[len(days) // 2] if days else None,
        'under_14_days': sum(1 for d in days if d < 14), 'over_90_days': sum(1 for d in days if d > 90),
        'launches_by_month': dict(sorted(launches.items())),
    }

    # Z10 re-tested within each market: all three audience types on the same day, same market.
    by = defaultdict(lambda: defaultdict(set))
    for r in fact:
        if r['Audience'] in ('Broad', 'Interest', 'LAL') and f(r['Amount spent']) > 0:
            by[(r.get('Market', ''), r['Objective'])][r['Date']].add(r['Audience'])
    R['z10_by_market'] = []
    for (mkt, obj), dd in by.items():
        od = {d for d, s in dd.items() if {'Broad', 'Interest', 'LAL'} <= s}
        if od:
            rows = [r for r in fact if r['Date'] in od and r.get('Market', '') == mkt
                    and r['Objective'] == obj and r['Audience'] in ('Broad', 'Interest', 'LAL')]
            sp = sum(f(r['Amount spent']) for r in rows)
            im = sum(f(r['Impressions']) for r in rows)
            mk_rows = [r for r in fact if r.get('Market', '') == mkt]
            mk_sp = sum(f(r['Amount spent']) for r in mk_rows)
            mk_im = sum(f(r['Impressions']) for r in mk_rows)
            R['z10_by_market'].append({
                'market': mkt, 'objective': obj, 'days': len(od), 'spend': round(sp, 2),
                'cpm': round(sp / im * 1000, 2) if im else None,
                'market_cpm': round(mk_sp / mk_im * 1000, 2) if mk_im else None,
                'adsets': sorted({f"{r['Ad Set Name']} [{r['Campaign Name']}] ({r['Audience']})" for r in rows})[:20],
            })

    # Status and objective of the ad sets behind each zinger.
    if '--zingers' in opts:
        zs = list(csv.DictReader(open(opts['--zingers'], encoding='utf-8')))
        adset_status = {}
        adset_obj = {}
        for r in fact_all:
            m = meta.get(r['Ad ID'], {})
            adset_status.setdefault(r['Ad Set ID'], set()).add(m.get('Delivery status', 'n/a'))
            adset_obj[r['Ad Set ID']] = r['Objective']
        z_summary = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
        for z in zs:
            if z['Zinger'] in ('Z1', 'Z12'):
                aid = z['Entity'].rsplit('(', 1)[-1].rstrip(')')
                live = 'live' if 'ACTIVE' in adset_status.get(aid, set()) else 'not live'
                obj = adset_obj.get(aid, '')
                key = f"{live} | {obj}"
                z_summary[z['Zinger']][key][0] += 1
                z_summary[z['Zinger']][key][1] += float(z['Spend involved'])
        R['zinger_status'] = {k: {kk: [vv[0], round(vv[1], 2)] for kk, vv in v.items()}
                              for k, v in z_summary.items()}

    json.dump(R, open(out, 'w'), indent=1, default=str)
    print(f"Wrote {out}")


if __name__ == '__main__':
    main()
