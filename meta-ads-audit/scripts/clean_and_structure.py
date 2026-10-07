#!/usr/bin/env python3
"""
Meta Ads Audit - clean and structure a raw export into pivot-ready tables.

Reads a raw Meta Ads export at ad level (CSV, or XLSX if openpyxl is present)
and writes:
    fact.csv      one row per ad per day, typed, with derived metrics
    lookup.csv    one row per ad, with attributes and totals
    monthly.csv   monthly rollup by funnel stage, audience, format (and market when present)
    weekly.csv    weekly rollup (ISO weeks, labelled by the Monday)
    dq_report.txt data-quality report

When the input already carries Funnel Stage / Audience / Ad Format (i.e. it is
the output of categorize_data.py), those columns are carried into every table.
Run it once on the raw export (stage 2) and again on the categorised fact
table (after stage 3) so Lookup and the rollups carry the categories.

Usage:
    python clean_and_structure.py <input.csv|input.xlsx> <output_dir>
"""
import sys
import os
import csv
import re
from collections import defaultdict
from datetime import datetime, date, timedelta


CANON = {
    'date': ['date', 'day', 'reporting starts', 'reporting start'],
    'campaign_id': ['campaign id', 'campaign_id'],
    'campaign_name': ['campaign name', 'campaign_name', 'campaign'],
    'adset_id': ['ad set id', 'adset id', 'ad_set_id', 'adset_id'],
    'adset_name': ['ad set name', 'adset name', 'ad_set_name', 'adset_name', 'ad set'],
    'ad_id': ['ad id', 'ad_id'],
    'ad_name': ['ad name', 'ad_name', 'ad'],
    'objective': ['objective'],
    'status': ['delivery status', 'status', 'ad set delivery', 'campaign delivery'],
    'spend': ['amount spent', 'amount_spent', 'spend', 'cost', 'amount spent (usd)'],
    'impressions': ['impressions'],
    'clicks_all': ['clicks (all)', 'clicks_all', 'clicks all', 'clicks'],
    'link_clicks': ['link clicks', 'link_clicks', 'clicks (link)'],
    'purchases': ['purchases', 'website purchases', 'results', 'conversions'],
    'purchase_value': ['purchase conversion value', 'purchase value', 'website purchase roas',
                       'conversion value', 'revenue'],
    'reach': ['reach'],
    'frequency': ['frequency'],
    'roas_reported': ['purchase roas', 'website purchase roas', 'roas'],
    # Upper-funnel events, carried through when present (used by the tracking check).
    'adds_to_cart': ['adds to cart', 'actions_add_to_cart'],
    'checkouts': ['checkouts initiated', 'actions_initiate_checkout'],
    'content_views': ['content views', 'actions_view_content'],
}

# Category columns produced by categorize_data.py, carried through when present.
CATEGORY_COLS = ['Funnel Stage', 'Audience', 'Ad Format',
                 'Funnel Stage tier', 'Audience tier', 'Ad Format tier', 'Market']


def build_lookup_map(fieldnames):
    lower = {f.lower().strip(): f for f in fieldnames}
    out = {}
    for canon, alts in CANON.items():
        for a in alts:
            if a in lower:
                out[canon] = lower[a]
                break
    return out


def to_float(v):
    if v is None:
        return None
    s = str(v).strip().replace(',', '').replace('$', '').replace('£', '').replace('₦', '')
    if s in ('', '-', 'N/A', 'n/a', 'null', 'None', '--'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_date(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d',
                '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d %b %Y', '%b %d, %Y'):
        try:
            return datetime.strptime(s[:len(fmt) + 4].strip(), fmt).date()
        except ValueError:
            continue
    return None


def clean_label(v):
    """Trim and collapse internal runs of whitespace. Case is left as displayed."""
    return re.sub(r'\s+', ' ', str(v or '')).strip()


def div(a, b):
    """Guarded division. Returns None where the denominator is zero or missing."""
    if a is None or b in (None, 0):
        return None
    return a / b


def r2(v):
    return None if v is None else round(v, 2)


def r4(v):
    # Ratios (CTR, CVR) are kept to 4dp: at 2dp a 1.3% CTR rounds to 0.01.
    return None if v is None else round(v, 4)


def load_rows(path):
    if path.lower().endswith(('.xlsx', '.xlsm')):
        try:
            from openpyxl import load_workbook
        except ImportError:
            print("Error: openpyxl required for XLSX input. pip install openpyxl")
            sys.exit(1)
        wb = load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        it = ws.iter_rows(values_only=True)
        header = [str(h) if h is not None else '' for h in next(it)]
        rows = [dict(zip(header, r)) for r in it]
        return header, rows
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    inp, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)

    fieldnames, rows = load_rows(inp)
    if not rows:
        print("Error: no data rows found.")
        sys.exit(1)

    cmap = build_lookup_map(fieldnames)
    required = ['date', 'campaign_name', 'adset_name', 'ad_name', 'spend', 'purchases']
    missing = [c for c in required if c not in cmap]
    if missing:
        print(f"Error: missing required fields: {missing}")
        print(f"Available columns: {fieldnames}")
        sys.exit(1)
    cats = [c for c in CATEGORY_COLS if c in fieldnames]

    dq = []

    clean, seen = [], set()
    dupes = 0
    bad_dates = 0
    null_metrics = {}
    zero_spend = 0
    negatives = 0
    relabelled = 0
    dates = []

    metric_keys = ['spend', 'impressions', 'clicks_all', 'link_clicks', 'purchases', 'purchase_value']

    for r in rows:
        d = to_date(r.get(cmap['date']))
        if d is None:
            bad_dates += 1
            continue

        ad_id = str(r.get(cmap.get('ad_id', ''), '') or r.get(cmap['ad_name'], '')).strip()
        key = (d.isoformat(), ad_id)
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        dates.append(d)

        def g(k):
            return r.get(cmap[k]) if k in cmap else None

        def lbl(k):
            raw = str(g(k) or '')
            out = clean_label(raw)
            return out, out != raw

        vals = {k: to_float(g(k)) for k in metric_keys}
        for k in metric_keys:
            if k in cmap and vals[k] is None:
                null_metrics[k] = null_metrics.get(k, 0) + 1
        spend = vals['spend']
        impressions = vals['impressions']
        clicks_all = vals['clicks_all']
        link_clicks = vals['link_clicks']
        purchases = vals['purchases']
        value = vals['purchase_value']

        if spend is not None and spend < 0:
            negatives += 1
        if spend == 0:
            zero_spend += 1

        names = {}
        for k in ('campaign_name', 'adset_name', 'ad_name'):
            names[k], changed = lbl(k)
            relabelled += changed

        cpm = div(spend, impressions)
        rec = {
            'Date': d.isoformat(),
            'Campaign ID': str(g('campaign_id') or '').strip(),
            'Campaign Name': names['campaign_name'],
            'Ad Set ID': str(g('adset_id') or '').strip(),
            'Ad Set Name': names['adset_name'],
            'Ad ID': ad_id,
            'Ad Name': names['ad_name'],
            'Objective': str(g('objective') or '').strip(),
            'Amount spent': r2(spend),
            'Impressions': impressions,
            'Clicks (all)': clicks_all,
            'Link clicks': link_clicks,
            'Purchases': purchases,
            'Purchase value': r2(value),
            'CPM': r2(cpm * 1000 if cpm is not None else None),
            'CPC': r2(div(spend, link_clicks)),
            'CTR': r4(div(link_clicks, impressions)),
            'CVR': r4(div(purchases, link_clicks)),
            'CPA': r2(div(spend, purchases)),
            'ROAS': r2(div(value, spend)),
        }
        for k, col in (('adds_to_cart', 'Adds to cart'), ('checkouts', 'Checkouts initiated'),
                       ('content_views', 'Content views')):
            if k in cmap:
                rec[col] = to_float(g(k))
        for c in cats:
            rec[c] = clean_label(r.get(c))
        clean.append(rec)

    if not clean:
        print("Error: no rows survived cleaning.")
        sys.exit(1)

    dq.append(f"Rows read: {len(rows)}")
    dq.append(f"Rows written: {len(clean)}")
    dq.append(f"Duplicate rows removed (Date + Ad ID): {dupes}")
    dq.append(f"Rows dropped for unparseable dates: {bad_dates}")
    for k in metric_keys:
        if k in cmap:
            dq.append(f"Rows with null {k}: {null_metrics.get(k, 0)}")
        else:
            dq.append(f"Field {k}: not present in export")
    dq.append(f"Rows with zero spend (kept; excluded from efficiency pivots): {zero_spend}")
    dq.append(f"Rows with negative spend: {negatives}")
    dq.append(f"Labels with whitespace trimmed or collapsed: {relabelled}")

    dmin, dmax = min(dates), max(dates)
    dq.append(f"Date range: {dmin.isoformat()} to {dmax.isoformat()}")
    span = (dmax - dmin).days + 1
    present = set(dates)
    dq.append(f"Days in range: {span} | days with data: {len(present)} | missing days: {span - len(present)}")
    gaps = [dmin + timedelta(days=i) for i in range(span) if dmin + timedelta(days=i) not in present]
    if gaps:
        dq.append(f"Missing dates (not zero-spend days): {', '.join(g.isoformat() for g in gaps[:30])}")
    dq.append(f"Span in months: {span / 30.44:.1f}")
    if span < 300:
        dq.append("NOTE: window is shorter than 12 months. Creative fatigue and cost-trend findings are limited.")

    today = date.today()
    if dmax >= today:
        dq.append("PARTIAL PERIOD: the range includes today. Figures are partial and subject to change.")
    else:
        dq.append(f"Partial period: no (range ends {dmax.isoformat()}, before {today.isoformat()})")

    total_spend = sum(x['Amount spent'] or 0 for x in clean)
    dq.append(f"Total amount spent: {total_spend:,.2f}")
    dq.append("Currency: confirm from the account, not inferred from the export")
    if cats:
        dq.append(f"Category columns carried through: {', '.join(cats)}")

    fact_fields = list(clean[0].keys())
    with open(os.path.join(outdir, 'fact.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fact_fields)
        w.writeheader()
        w.writerows(clean)

    ads = defaultdict(lambda: {'spend': 0.0, 'purchases': 0.0, 'value': 0.0,
                               'dates': [], 'impressions': 0.0, 'link_clicks': 0.0})
    for x in clean:
        a = ads[x['Ad ID']]
        a.update({
            'Ad ID': x['Ad ID'], 'Ad Name': x['Ad Name'],
            'Ad Set ID': x['Ad Set ID'], 'Ad Set Name': x['Ad Set Name'],
            'Campaign ID': x['Campaign ID'], 'Campaign Name': x['Campaign Name'],
            'Objective': x['Objective'],
        })
        for c in cats:
            a[c] = x.get(c, '')
        a['spend'] += x['Amount spent'] or 0
        a['purchases'] += x['Purchases'] or 0
        a['value'] += x['Purchase value'] or 0
        a['impressions'] += x['Impressions'] or 0
        a['link_clicks'] += x['Link clicks'] or 0
        # Days active counts days with delivery, not rows that merely exist.
        if (x['Amount spent'] or 0) > 0 or (x['Impressions'] or 0) > 0:
            a['dates'].append(x['Date'])

    lookup_fields = ['Ad ID', 'Ad Name', 'Ad Set ID', 'Ad Set Name', 'Campaign ID',
                     'Campaign Name', 'Objective', 'Funnel Stage', 'Audience', 'Ad Format',
                     'First date active', 'Last date active', 'Days active',
                     'Total spend', 'Total purchases', 'Blended ROAS']
    extra = [c for c in cats if c not in lookup_fields]
    lookup_fields = lookup_fields[:10] + extra + lookup_fields[10:]
    lookup = []
    for a in ads.values():
        rec = {
            'Ad ID': a['Ad ID'], 'Ad Name': a['Ad Name'],
            'Ad Set ID': a['Ad Set ID'], 'Ad Set Name': a['Ad Set Name'],
            'Campaign ID': a['Campaign ID'], 'Campaign Name': a['Campaign Name'],
            'Objective': a['Objective'],
            'Funnel Stage': a.get('Funnel Stage', ''), 'Audience': a.get('Audience', ''),
            'Ad Format': a.get('Ad Format', ''),
            'First date active': min(a['dates']) if a['dates'] else '',
            'Last date active': max(a['dates']) if a['dates'] else '',
            'Days active': len(set(a['dates'])),
            'Total spend': r2(a['spend']),
            'Total purchases': a['purchases'],
            'Blended ROAS': r2(div(a['value'], a['spend'])),
        }
        for c in extra:
            rec[c] = a.get(c, '')
        lookup.append(rec)
    lookup.sort(key=lambda x: -(x['Total spend'] or 0))
    with open(os.path.join(outdir, 'lookup.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=lookup_fields)
        w.writeheader()
        w.writerows(lookup)

    def rollup(keyfn, filename):
        agg = defaultdict(lambda: {'spend': 0.0, 'impr': 0.0, 'lc': 0.0,
                                   'purch': 0.0, 'value': 0.0, 'rows': 0})
        for x in clean:
            k = keyfn(x)
            a = agg[k]
            a['spend'] += x['Amount spent'] or 0
            a['impr'] += x['Impressions'] or 0
            a['lc'] += x['Link clicks'] or 0
            a['purch'] += x['Purchases'] or 0
            a['value'] += x['Purchase value'] or 0
            a['rows'] += 1
        fields = ['Period', 'Funnel Stage', 'Audience', 'Ad Format', 'Market', 'Amount spent',
                  'Impressions', 'Link clicks', 'Purchases', 'Purchase value', 'ROAS', 'CPA']
        if 'Market' not in cats:
            fields.remove('Market')
        out = []
        for k, a in sorted(agg.items(), key=lambda kv: str(kv[0])):
            period, fs, aud, fmt, mkt = (list(k) + ['', '', '', ''])[:5]
            out.append({
                'Period': period, 'Funnel Stage': fs, 'Audience': aud, 'Ad Format': fmt,
                **({'Market': mkt} if 'Market' in cats else {}),
                'Amount spent': r2(a['spend']), 'Impressions': a['impr'],
                'Link clicks': a['lc'], 'Purchases': a['purch'],
                'Purchase value': r2(a['value']),
                'ROAS': r2(div(a['value'], a['spend'])),
                'CPA': r2(div(a['spend'], a['purch'])),
            })
        with open(os.path.join(outdir, filename), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(out)

    def week_start(iso):
        d = date.fromisoformat(iso)
        return (d - timedelta(days=d.weekday())).isoformat()

    def dims(x):
        return (x.get('Funnel Stage', ''), x.get('Audience', ''), x.get('Ad Format', ''), x.get('Market', ''))

    rollup(lambda x: (x['Date'][:7],) + dims(x), 'monthly.csv')
    # Weekly rollup keyed by the Monday of the ISO week (the original keyed by the raw date, which is daily).
    rollup(lambda x: (week_start(x['Date']),) + dims(x), 'weekly.csv')

    with open(os.path.join(outdir, 'dq_report.txt'), 'w', encoding='utf-8') as f:
        f.write("Meta Ads Audit - data quality report\n")
        f.write("=" * 44 + "\n")
        for line in dq:
            f.write(line + "\n")

    print("=== Data quality ===")
    for line in dq:
        print("  " + line)
    print(f"\nWrote fact.csv ({len(clean)} rows), lookup.csv ({len(lookup)} ads), "
          f"monthly.csv, weekly.csv, dq_report.txt to {outdir}")

    if dupes or bad_dates or negatives:
        print("\nWarning: cleaning removed or flagged rows. Report these in the audit.")
        sys.exit(2)


if __name__ == '__main__':
    main()
