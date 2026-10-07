#!/usr/bin/env python3
"""
Meta Ads Audit - detect zingers by fixed threshold.

Usage:
    python detect_zingers.py <fact_categorized.csv> <lookup.csv> <out_zingers.csv>
                             [--scope <ad_ids.txt>] [--scope-name "Live ads"]

Account averages (CPA, ROAS) are always computed across the whole fact table,
as the definitions in Part 5 require. With --scope, the entities tested
(ad sets, ads, funnel stages, formats, windows) are restricted to the Ad IDs
listed in the file, one per line, so live ads can be audited on their own.
"""
import sys
import csv
from collections import defaultdict
from datetime import date, timedelta

SEVERITY = {
    'Z1': 'Highest', 'Z4': 'Highest', 'Z12': 'Highest',
    'Z2': 'High', 'Z5': 'High', 'Z6': 'High',
    'Z7': 'Medium', 'Z8': 'Medium', 'Z11': 'Medium',
    'Z3': 'Watch', 'Z9': 'Watch', 'Z10': 'Watch',
}
SEV_ORDER = ['Highest', 'High', 'Medium', 'Watch']

TITLES = {
    'Z1': 'Spend producing no purchases',
    'Z2': 'Learning-limited ad sets',
    'Z3': 'Retargeting starved of budget',
    'Z4': 'Prospecting inefficiency',
    'Z5': 'Fragmentation',
    'Z6': 'Format funded without justification',
    'Z7': 'Creative fatigue',
    'Z8': 'Zombie ads',
    'Z9': 'Concentration risk',
    'Z10': 'Audience overlap risk',
    'Z11': 'Cost trend against you',
    'Z12': 'Underfunded winner',
}


def f(v):
    try:
        return float(str(v).replace(',', '').replace('$', '') or 0)
    except (ValueError, TypeError):
        return 0.0


def load(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def main():
    argv = sys.argv[1:]
    opts, args, i = {}, [], 0
    while i < len(argv):
        if argv[i] in ('--scope', '--scope-name'):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 3:
        print(__doc__)
        sys.exit(1)

    fact_all = load(args[0])
    lookup = load(args[1])
    out_path = args[2]
    scope_name = opts.get('--scope-name', 'All ads')

    if not fact_all:
        print("Error: fact table is empty.")
        sys.exit(1)

    # Account averages: always the whole account, whole window.
    total_spend_acct = sum(f(r.get('Amount spent')) for r in fact_all)
    total_purch = sum(f(r.get('Purchases')) for r in fact_all)
    total_value = sum(f(r.get('Purchase value')) for r in fact_all)
    acct_cpa = (total_spend_acct / total_purch) if total_purch else None
    acct_roas = (total_value / total_spend_acct) if total_spend_acct else None

    all_dates = sorted({r['Date'] for r in fact_all if r.get('Date')})
    dmax = date.fromisoformat(all_dates[-1])
    recent_cut = dmax - timedelta(days=90)
    prior_cut = recent_cut - timedelta(days=90)
    last7_cut = dmax - timedelta(days=6)   # seven days inclusive of dmax

    if '--scope' in opts:
        ids = {l.strip() for l in open(opts['--scope'], encoding='utf-8') if l.strip()}
        fact = [r for r in fact_all if r.get('Ad ID') in ids]
        print(f"Scope: {scope_name} - {len(ids)} ads, {len(fact)} rows")
    else:
        fact = fact_all
    if not fact:
        print("Error: no rows in scope.")
        sys.exit(1)

    total_spend = sum(f(r.get('Amount spent')) for r in fact)

    if acct_cpa is None:
        print("Warning: no purchases in the window. Zingers relying on account CPA cannot fire.")

    def adset_label(r):
        return f"{r.get('Ad Set Name', '')} [{r.get('Campaign Name', '')}] ({r.get('Ad Set ID', '')})"

    def ad_label(r):
        return f"{r.get('Ad Name', '')} [{r.get('Campaign Name', '')}] ({r.get('Ad ID', '')})"

    adsets = defaultdict(lambda: {'spend': 0.0, 'purch': 0.0, 'value': 0.0, 'impr': 0.0,
                                  'dates': set(), 'name': '', 'objective': '', 'audience': ''})
    ads = defaultdict(lambda: {'spend': 0.0, 'purch': 0.0, 'value': 0.0,
                               'dates': set(), 'name': '', 'rows': []})
    for r in fact:
        sp = f(r.get('Amount spent'))
        k = r.get('Ad Set ID') or r.get('Ad Set Name')
        a = adsets[k]
        a['spend'] += sp
        a['purch'] += f(r.get('Purchases'))
        a['value'] += f(r.get('Purchase value'))
        a['impr'] += f(r.get('Impressions'))
        if sp > 0:
            a['dates'].add(r['Date'])
        a['name'] = adset_label(r)
        a['objective'] = r.get('Objective', '')
        a['audience'] = r.get('Audience', '')

        k = r.get('Ad ID') or r.get('Ad Name')
        a = ads[k]
        a['spend'] += sp
        a['purch'] += f(r.get('Purchases'))
        a['value'] += f(r.get('Purchase value'))
        if sp > 0:
            a['dates'].add(r['Date'])
        a['name'] = ad_label(r)
        a['rows'].append(r)

    fired = []

    def add(zid, entity, detail, spend, basis='measured'):
        fired.append({
            'Scope': scope_name, 'Zinger': zid, 'Severity': SEVERITY[zid], 'Finding': TITLES[zid],
            'Entity': entity, 'Detail': detail, 'Spend involved': round(spend, 2), 'Basis': basis,
        })

    # Z1 - ad set spend >= 1.5x account CPA with zero purchases across the window.
    if acct_cpa:
        for k, a in sorted(adsets.items(), key=lambda kv: -kv[1]['spend']):
            if a['spend'] >= 1.5 * acct_cpa and a['purch'] == 0:
                add('Z1', a['name'],
                    f"{len(a['dates'])} days with spend, 0 purchases; "
                    f"{a['spend'] / total_spend_acct:.2%} of account spend "
                    f"(threshold 1.5 x CPA = {1.5 * acct_cpa:,.2f})", a['spend'])

    # Z2 - active ad sets (spend in the last 7 days) below 50 purchases with weekly spend > CPA.
    weekly = defaultdict(lambda: {'spend': 0.0, 'purch': 0.0})
    for r in fact:
        if r['Date'] >= last7_cut.isoformat():
            k = r.get('Ad Set ID') or r.get('Ad Set Name')
            weekly[k]['spend'] += f(r.get('Amount spent'))
            weekly[k]['purch'] += f(r.get('Purchases'))
    active = {k: v for k, v in weekly.items() if v['spend'] > 0}
    below_line = {k: v for k, v in active.items() if v['purch'] < 50}
    limited = []
    if acct_cpa:
        limited = [(k, v) for k, v in active.items() if v['purch'] < 50 and v['spend'] > acct_cpa]
        if limited:
            share = len(limited) / len(active) if active else 0
            add('Z2', f"{len(limited)} ad sets",
                f"{share:.0%} of {len(active)} active ad sets are learning-limited in the last 7 days "
                f"({last7_cut.isoformat()} to {dmax.isoformat()}); "
                f"{sum(v['purch'] for _, v in limited):.0f} purchases between them",
                sum(v['spend'] for _, v in limited))

    # Z3 / Z4 - funnel split.
    fs = defaultdict(lambda: {'spend': 0.0, 'value': 0.0})
    for r in fact:
        lvl = r.get('Funnel Stage', 'Uncategorized')
        fs[lvl]['spend'] += f(r.get('Amount spent'))
        fs[lvl]['value'] += f(r.get('Purchase value'))
    p_s, r_s = fs['Prospecting']['spend'], fs['RTG']['spend']
    p_roas = fs['Prospecting']['value'] / p_s if p_s else 0
    r_roas = fs['RTG']['value'] / r_s if r_s else 0
    if total_spend and p_s and r_s:
        if r_s / total_spend < 0.10 and p_roas and r_roas >= 2 * p_roas:
            opp = 0.10 * total_spend * r_roas
            add('Z3', 'Retargeting',
                f"holds {r_s / total_spend:.1%} of spend at ROAS {r_roas:.2f} vs Prospecting {p_roas:.2f}; "
                f"shifting 10pp of spend would return ~{opp:,.0f} at the observed rate", r_s)
    if total_spend and p_s / total_spend > 0.80 and p_roas < 1.0:
        add('Z4', 'Prospecting',
            f"holds {p_s / total_spend:.1%} of spend at ROAS {p_roas:.2f}", p_s)

    # Z5 - fragmentation.
    if active:
        sub_share = len(below_line) / len(active)
        ranked = sorted((a['spend'] for a in adsets.values()), reverse=True)
        top5 = sum(ranked[:5])
        top10 = sum(ranked[:10])
        if sub_share > 0.40 and total_spend and top5 / total_spend < 0.40:
            add('Z5', f"{len(adsets)} ad sets ({len(active)} active)",
                f"{sub_share:.0%} of active ad sets below the 50-conversion weekly line; "
                f"top 5 ad sets hold {top5 / total_spend:.1%} and top 10 hold {top10 / total_spend:.1%} of spend",
                total_spend)

    # Z6 - format funded without justification.
    fmt = defaultdict(lambda: {'spend': 0.0, 'value': 0.0})
    for r in fact:
        k = r.get('Ad Format', 'Uncategorized')
        fmt[k]['spend'] += f(r.get('Amount spent'))
        fmt[k]['value'] += f(r.get('Purchase value'))
    if total_spend and acct_roas:
        for k, v in fmt.items():
            if k in ('Uncategorized', '') or not v['spend']:
                continue
            share = v['spend'] / total_spend
            roas = v['value'] / v['spend']
            if share >= 0.15 and roas < 0.5 * acct_roas:
                add('Z6', k, f"{share:.1%} of spend at ROAS {roas:.2f} against account average {acct_roas:.2f}",
                    v['spend'])

    # Z7 - creative fatigue: >= 60 days active, ROAS last 30d >= 40% below first 30d.
    for k, a in ads.items():
        ds = sorted(a['dates'])
        if len(ds) < 60:
            continue
        first_end = (date.fromisoformat(ds[0]) + timedelta(days=29)).isoformat()
        last_start = (date.fromisoformat(ds[-1]) - timedelta(days=29)).isoformat()
        first = [r for r in a['rows'] if ds[0] <= r['Date'] <= first_end]
        last = [r for r in a['rows'] if last_start <= r['Date'] <= ds[-1]]
        fs_ = sum(f(r.get('Amount spent')) for r in first)
        ls_ = sum(f(r.get('Amount spent')) for r in last)
        if fs_ <= 0 or ls_ <= 0:
            continue
        fr = sum(f(r.get('Purchase value')) for r in first) / fs_
        lr = sum(f(r.get('Purchase value')) for r in last) / ls_
        if fr > 0 and lr <= 0.6 * fr:
            add('Z7', a['name'],
                f"ROAS fell from {fr:.2f} to {lr:.2f} ({(lr - fr) / fr:.0%}) between first and last 30 days "
                f"of its run; last-30-day spend {ls_:,.2f}", ls_)

    # Z8 - zombie ads.
    zombies = [(k, a) for k, a in ads.items() if len(a['dates']) >= 30 and a['purch'] == 0 and a['spend'] > 0]
    if zombies:
        oldest = max(zombies, key=lambda kv: len(kv[1]['dates']))
        add('Z8', f"{len(zombies)} ads",
            f"active 30+ days with zero purchases; combined spend "
            f"{sum(a['spend'] for _, a in zombies):,.2f}; oldest: {oldest[1]['name']} "
            f"({len(oldest[1]['dates'])} days)",
            sum(a['spend'] for _, a in zombies))

    # Z9 - concentration risk (share of total account spend).
    for k, a in adsets.items():
        if a['spend'] / total_spend_acct > 0.50:
            add('Z9', a['name'], f"ad set holds {a['spend'] / total_spend_acct:.1%} of total account spend",
                a['spend'])
    for k, a in ads.items():
        if a['spend'] / total_spend_acct > 0.50:
            add('Z9', a['name'], f"ad holds {a['spend'] / total_spend_acct:.1%} of total account spend",
                a['spend'])

    # Z10 - Broad, Interest and LAL running simultaneously on the same objective.
    # Tested within each market when a Market column exists: audiences in different
    # countries cannot overlap, so an account-wide test would overstate the risk.
    by_obj = defaultdict(lambda: defaultdict(set))
    for r in fact:
        if r.get('Audience') in ('Broad', 'Interest', 'LAL') and f(r.get('Amount spent')) > 0:
            by_obj[(r.get('Market', ''), r.get('Objective', ''))][r['Date']].add(r['Audience'])
    for (mkt, obj), days in by_obj.items():
        overlap_days = {d for d, s in days.items() if {'Broad', 'Interest', 'LAL'}.issubset(s)}
        if not overlap_days:
            continue
        rows = [r for r in fact if r['Date'] in overlap_days and r.get('Objective', '') == obj
                and r.get('Market', '') == mkt and r.get('Audience') in ('Broad', 'Interest', 'LAL')]
        sp = sum(f(r.get('Amount spent')) for r in rows)
        im = sum(f(r.get('Impressions')) for r in rows)
        base = [r for r in fact_all if r.get('Market', '') == mkt]
        b_sp = sum(f(r.get('Amount spent')) for r in base)
        b_im = sum(f(r.get('Impressions')) for r in base)
        cpm = sp / im * 1000 if im else None
        b_cpm = b_sp / b_im * 1000 if b_im else None
        where = f"{mkt} " if mkt else ''
        detail = (f"all three ran on {len(overlap_days)} common days across "
                  f"{len({r.get('Ad Set ID') for r in rows})} ad sets; combined spend {sp:,.2f}")
        if cpm and b_cpm:
            detail += f"; CPM {cpm:,.2f} vs {where or 'account '}average {b_cpm:,.2f}"
        add('Z10', f"Broad + Interest + LAL, {where}{obj or 'unknown objective'}", detail,
            sp, basis='hypothesis - confirm with an audience-segment breakdown')

    # Z11 - cost trend at stable spend.
    recent = [r for r in fact if r['Date'] > recent_cut.isoformat()]
    prior = [r for r in fact if prior_cut.isoformat() < r['Date'] <= recent_cut.isoformat()]
    trend = {}
    if recent and prior:
        rs = sum(f(r.get('Amount spent')) for r in recent)
        ps = sum(f(r.get('Amount spent')) for r in prior)
        ri = sum(f(r.get('Impressions')) for r in recent)
        pi = sum(f(r.get('Impressions')) for r in prior)
        rp = sum(f(r.get('Purchases')) for r in recent)
        pp = sum(f(r.get('Purchases')) for r in prior)
        stable = ps > 0 and abs(rs - ps) / ps <= 0.20
        trend = {'recent_spend': rs, 'prior_spend': ps, 'stable': stable,
                 'recent_cpm': rs / ri * 1000 if ri else None, 'prior_cpm': ps / pi * 1000 if pi else None,
                 'recent_cpa': rs / rp if rp else None, 'prior_cpa': ps / pp if pp else None}
        if stable and trend['recent_cpm'] and trend['prior_cpm']:
            rc, pc = trend['recent_cpm'], trend['prior_cpm']
            if (rc - pc) / pc >= 0.25:
                add('Z11', 'CPM', f"rose {(rc - pc) / pc:.0%} ({pc:,.2f} to {rc:,.2f}) at stable spend "
                                  f"({ps:,.0f} to {rs:,.0f})", rs)
        if stable and trend['recent_cpa'] and trend['prior_cpa']:
            rc, pc = trend['recent_cpa'], trend['prior_cpa']
            if (rc - pc) / pc >= 0.25:
                add('Z11', 'CPA', f"rose {(rc - pc) / pc:.0%} ({pc:,.2f} to {rc:,.2f}) at stable spend "
                                  f"({ps:,.0f} to {rs:,.0f})", rs)

    # Z12 - underfunded winner.
    if acct_roas:
        for k, a in sorted(adsets.items(), key=lambda kv: -kv[1]['spend']):
            if not a['spend']:
                continue
            roas = a['value'] / a['spend']
            share = a['spend'] / total_spend_acct
            if roas >= 1.5 * acct_roas and share < 0.05:
                add('Z12', a['name'],
                    f"ROAS {roas:.2f} against account average {acct_roas:.2f} on {share:.2%} of spend "
                    f"({a['purch']:.0f} purchases); an extra {a['spend']:,.0f} at the observed rate would "
                    f"return ~{a['spend'] * roas:,.0f} (upper bound: marginal ROAS falls as budget rises)",
                    a['spend'])

    fields = ['Scope', 'Zinger', 'Severity', 'Finding', 'Entity', 'Detail', 'Spend involved', 'Basis']
    fired.sort(key=lambda z: (SEV_ORDER.index(z['Severity']), int(z['Zinger'][1:]), -z['Spend involved']))
    with open(out_path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(fired)

    print(f"=== Zingers fired - {scope_name} ===")
    if not fired:
        print("  None. The scope shows no threshold-level waste.")
        print("  Report the concentration and trend observations that the thresholds do not cover.")
    else:
        for sev in SEV_ORDER:
            group = [z for z in fired if z['Severity'] == sev]
            if not group:
                continue
            print(f"\n  [{sev}]")
            for zid in sorted({z['Zinger'] for z in group}, key=lambda s: int(s[1:])):
                zs = [z for z in group if z['Zinger'] == zid]
                print(f"    {zid} {TITLES[zid]} - {len(zs)} fired, spend involved "
                      f"{sum(z['Spend involved'] for z in zs):,.2f}")
                for z in zs[:5]:
                    print(f"        {z['Entity']}: {z['Detail']}")
                if len(zs) > 5:
                    print(f"        ... and {len(zs) - 5} more (see {out_path})")
    not_fired = [z for z in TITLES if z not in {x['Zinger'] for x in fired}]
    print(f"\n  Did not fire: {', '.join(not_fired) or 'none'}")

    print(f"\nAccount average CPA: {acct_cpa:,.2f}" if acct_cpa else "\nAccount average CPA: not computable")
    print(f"Account average ROAS: {acct_roas:.2f}" if acct_roas else "Account average ROAS: not computable")
    print(f"Scope spend analysed: {total_spend:,.2f} of account {total_spend_acct:,.2f} "
          f"over {len(all_dates)} days")
    print(f"Active ad sets (spend in last 7 days): {len(active)}; below 50 purchases: {len(below_line)}")
    if trend:
        def fm(v):
            return f"{v:,.2f}" if v is not None else "n/a"
        print(f"Recent vs prior 90 days: spend {trend['prior_spend']:,.0f} -> {trend['recent_spend']:,.0f} "
              f"(stable={trend['stable']}); CPM {fm(trend['prior_cpm'])} -> {fm(trend['recent_cpm'])}; "
              f"CPA {fm(trend['prior_cpa'])} -> {fm(trend['recent_cpa'])}")
    print(f"\nWrote {out_path} ({len(fired)} fired)")


if __name__ == '__main__':
    main()
