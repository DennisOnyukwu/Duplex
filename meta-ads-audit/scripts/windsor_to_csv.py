#!/usr/bin/env python3
"""
Meta Ads Audit - convert Windsor.ai get_data JSON pulls (facebook connector,
ad level, daily) into a raw CSV carrying Meta's own column names.

Usage:
    python windsor_to_csv.py <out.csv> <pull1.json> [<pull2.json> ...]
"""
import sys
import csv
import json

COLS = [
    ('date', 'Date'),
    ('campaign_id', 'Campaign ID'),
    ('campaign', 'Campaign Name'),
    ('campaign_objective', 'Objective'),
    ('adset_id', 'Ad Set ID'),
    ('adset_name', 'Ad Set Name'),
    ('ad_id', 'Ad ID'),
    ('ad_name', 'Ad Name'),
    ('spend', 'Amount spent'),
    ('impressions', 'Impressions'),
    ('clicks', 'Clicks (all)'),
    ('link_clicks', 'Link clicks'),
    ('actions_purchase', 'Purchases'),
    ('action_values_purchase', 'Purchase value'),
    ('actions_add_to_cart', 'Adds to cart'),
    ('actions_initiate_checkout', 'Checkouts initiated'),
    ('actions_view_content', 'Content views'),
]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out, pulls = sys.argv[1], sys.argv[2:]
    n = 0
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow([c for _, c in COLS])
        for p in pulls:
            payload = json.load(open(p, encoding='utf-8'))
            if payload.get('status') != 'done':
                print(f"Error: {p} has status {payload.get('status')}")
                sys.exit(1)
            rows = payload['data']
            if len(rows) != payload.get('total_rows', len(rows)):
                print(f"Error: {p} returned {len(rows)} of {payload['total_rows']} rows")
                sys.exit(1)
            for r in rows:
                # None stays blank: a null is not a zero.
                w.writerow(['' if r.get(k) is None else r.get(k) for k, _ in COLS])
                n += 1
            print(f"  {p}: {len(rows)} rows")
    print(f"Wrote {out} ({n} rows)")


if __name__ == '__main__':
    main()
