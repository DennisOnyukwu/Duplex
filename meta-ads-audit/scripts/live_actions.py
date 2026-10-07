#!/usr/bin/env python3
"""
Meta Ads Audit - one row per live ad set with a verdict, for the action tab.

Verdict rules (fixed, so the next audit applies the same ones):
    Non-Sales objective              -> "Review: Reach objective" (or "Check targeting" when the
                                        campaign name names a different market than its targeting)
    First spend within the last 7 days -> "Too early: review on <first spend + 7 days>"
    ROAS >= 1.5 x account ROAS        -> "Scale: winner (Z12)"
    ROAS >= account ROAS               -> "Keep"
    ROAS <  account ROAS               -> "Watch: below account ROAS"
    Nigeria ad sets older than 7 days additionally carry "fold into NG consolidation".
Flags appended: Z7 fatigued ads in the ad set; under ₦50,000 spent in the last 7 days.

Usage:
    python live_actions.py <fact.csv> <ad_meta.csv> <live_ids.txt> <zingers_live.csv> <out.csv>
"""
import sys
import csv
from collections import defaultdict
from datetime import date, timedelta


def main():
    fact_p, meta_p, ids_p, z_p, out_p = sys.argv[1:6]
    live = {l.strip() for l in open(ids_p) if l.strip()}
    meta = {r['Ad ID']: r for r in csv.DictReader(open(meta_p, encoding='utf-8'))}
    fact_all = list(csv.DictReader(open(fact_p, encoding='utf-8')))
    tot_s = sum(float(r['Amount spent']) for r in fact_all)
    tot_v = sum(float(r['Purchase value']) for r in fact_all)
    acct_roas = tot_v / tot_s
    dmax = max(r['Date'] for r in fact_all)
    cut7 = (date.fromisoformat(dmax) - timedelta(days=6)).isoformat()
    fatigued = defaultdict(int)
    for z in csv.DictReader(open(z_p, encoding='utf-8')):
        if z['Zinger'] == 'Z7':
            ad = z['Entity'].rsplit('(', 1)[-1].rstrip(')')
            for r in fact_all:
                if r['Ad ID'] == ad:
                    fatigued[r['Ad Set ID']] += 1
                    break

    A = defaultdict(lambda: {'sp': 0.0, 'p': 0.0, 'v': 0.0, 'sp7': 0.0, 'p7': 0.0, 'first': '9999',
                             'ads': set(), 'fmt': set()})
    for r in fact_all:
        if r['Ad ID'] not in live:
            continue
        a = A[r['Ad Set ID']]
        sp = float(r['Amount spent'])
        a['sp'] += sp
        a['p'] += float(r['Purchases'])
        a['v'] += float(r['Purchase value'])
        if r['Date'] >= cut7:
            a['sp7'] += sp
            a['p7'] += float(r['Purchases'])
        if sp > 0:
            a['first'] = min(a['first'], r['Date'])
        a['ads'].add(r['Ad ID'])
        a['fmt'].add(r['Ad Format'])
        m = meta[r['Ad ID']]
        a.update({'name': r['Ad Set Name'], 'camp': r['Campaign Name'], 'mkt': r['Market'],
                  'aud': r['Audience'], 'obj': r['Objective'], 'goal': m['Optimisation goal'],
                  'lp': m['Learning phase'] or 'Not reported',
                  'bud': (float(m['Campaign daily budget'] or m['Ad set daily budget'] or 0) / 100) or None})

    rows = []
    for k, a in A.items():
        roas = a['v'] / a['sp'] if a['sp'] else None
        new = a['first'] >= cut7
        names_mkt = [t for t in ('CA', 'UK', 'US', 'USA', 'NG') if f' {t} ' in f" {a['camp']} ".replace('|', ' ')
                     or a['camp'].startswith(t + ' ')]
        if a['obj'] != 'OUTCOME_SALES':
            named = names_mkt[0].replace('USA', 'US') if names_mkt else None
            if named and named != a['mkt']:
                verdict = f"Check targeting: campaign named {named}, targets {a['mkt']}"
            else:
                verdict = 'Review: Reach objective, no purchase goal'
        elif new:
            review = (date.fromisoformat(a['first']) + timedelta(days=7)).isoformat()
            verdict = f"Too early: review on {review}"
        elif roas is not None and roas >= 1.5 * acct_roas:
            verdict = 'Scale: winner (Z12)'
        elif roas is not None and roas >= acct_roas:
            verdict = 'Keep'
        else:
            verdict = 'Watch: below account ROAS'
        if a['obj'] == 'OUTCOME_SALES' and a['mkt'] == 'NG' and not new:
            verdict += '; fold into NG consolidation'
        flags = []
        if fatigued.get(k):
            flags.append(f"{fatigued[k]} fatigued ad(s) (Z7): refresh creative")
        if not new and a['sp7'] < 50000:
            flags.append('barely delivering: under ₦50,000 in the last 7 days')
        rows.append({
            'Verdict': verdict, 'Flags': '; '.join(flags),
            'Campaign Name': a['camp'], 'Ad Set Name': a['name'], 'Ad Set ID': k,
            'Market': a['mkt'], 'Audience': a['aud'], 'Ad Format(s)': '/'.join(sorted(a['fmt'])),
            'Objective': a['obj'], 'Optimisation goal': a['goal'], 'Learning phase': a['lp'],
            'Daily budget (₦)': a['bud'], 'First spend date': a['first'], 'Live ads': len(a['ads']),
            'Amount spent (12m)': round(a['sp'], 2), 'Purchases (12m)': a['p'],
            'ROAS (12m)': round(roas, 2) if roas is not None else None,
            'CPA (12m)': round(a['sp'] / a['p'], 2) if a['p'] else None,
            'Amount spent (last 7d)': round(a['sp7'], 2), 'Purchases (last 7d)': a['p7'],
        })
    order = ['Check', 'Scale', 'Keep', 'Watch', 'Review', 'Too early']
    rows.sort(key=lambda r: (next(i for i, o in enumerate(order) if r['Verdict'].startswith(o)),
                             -r['Amount spent (12m)']))
    with open(out_p, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(Counter(r['Verdict'].split(':')[0].split(';')[0] for r in rows))
    for r in rows[:14]:
        print(f"  {r['Verdict'][:60]:<60} | {r['Campaign Name'][:32]:<32} {r['Market']} roas={r['ROAS (12m)']} sp7={r['Amount spent (last 7d)']:,.0f} {r['Flags']}")
    print(f"Wrote {out_p} ({len(rows)} ad sets)")


if __name__ == '__main__':
    main()
