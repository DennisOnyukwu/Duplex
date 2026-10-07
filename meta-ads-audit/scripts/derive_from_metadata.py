#!/usr/bin/env python3
"""
Meta Ads Audit - derive Funnel Stage, Audience, Ad Format and Market per ad
from Meta's own creative and targeting metadata, for accounts whose names
cannot be parsed (Part 3, section 1: "an account that cannot be parsed").

Inputs are Windsor.ai get_data JSON pulls (facebook connector):
    meta.json      ad_id, object_type, adset_targeting, adset_promoted_object,
                   adsset_optimization_goal, adset_learning_stage_info,
                   campaign_bid_strategy, campaign_daily_budget, adset_daily_budget
    status.json    ad_id, effective_status, adset_effective_status, campaign_effective_status
    carousel.json  ad_id, carousel_card_media_urls            (optional)

Rules (every one is a mapping from a Meta field, not from a name):
    Ad Format    object_type VIDEO -> Video; promoted_object.product_set_id -> Catalogue;
                 SHARE with carousel cards -> Carousel; other SHARE -> Static.
    Audience     custom audience named "Lookalike..." -> LAL; "WEB..." -> WebVisitors;
                 "IG..."/engagement custom audience -> Engagers; interests or behaviours
                 in flexible_spec -> Interest; none of these -> Broad.
    Funnel Stage a non-lookalike custom audience (site visitors, engagers) -> RTG;
                 everything else -> Prospecting.
    Market       countries in geo_locations, including those of targeted cities and regions
                 (GB shown as UK); none found -> Unspecified.

Usage:
    python derive_from_metadata.py <meta.json> <status.json> <out_meta.csv> [<carousel.json>]
"""
import sys
import csv
import json
from collections import Counter

MARKET = {'GB': 'UK', 'NG': 'NG', 'CA': 'CA', 'US': 'US'}


def load(path):
    payload = json.load(open(path, encoding='utf-8'))
    if payload.get('status') != 'done':
        print(f"Error: {path} status {payload.get('status')}")
        sys.exit(1)
    return payload['data']


def jload(v):
    if not v or v == 'None':
        return {}
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return {}


def main():
    if len(sys.argv) not in (4, 5):
        print(__doc__)
        sys.exit(1)
    meta = load(sys.argv[1])
    status = {r['ad_id']: r for r in load(sys.argv[2])}
    out = sys.argv[3]
    carousel = {}
    if len(sys.argv) == 5:
        carousel = {r['ad_id']: r.get('carousel_card_media_urls') for r in load(sys.argv[4])}

    rows = []
    for m in meta:
        t = jload(m.get('adset_targeting'))
        po = jload(m.get('adset_promoted_object'))
        cas = [str(c.get('name') or '') for c in t.get('custom_audiences', [])]
        lal = [c for c in cas if c.lower().startswith('lookalike')]
        warm = [c for c in cas if not c.lower().startswith('lookalike')]
        flex = t.get('flexible_spec') or []
        has_interest = any(s.get('interests') or s.get('behaviors') for s in flex)

        if lal:
            audience = 'LAL'
        elif any(c.upper().startswith('WEB') for c in warm):
            audience = 'WebVisitors'
        elif warm:
            audience = 'Engagers'
        elif has_interest:
            audience = 'Interest'
        else:
            audience = 'Broad'
        funnel = 'RTG' if warm else 'Prospecting'

        ot = m.get('object_type')
        cards = carousel.get(m['ad_id'])
        if po.get('product_set_id'):
            fmt = 'Catalogue'
        elif ot == 'VIDEO':
            fmt = 'Video'
        elif ot == 'SHARE' and cards and cards != 'None' and ';' in str(cards):
            fmt = 'Carousel'
        elif ot == 'SHARE':
            fmt = 'Static'
        else:
            fmt = 'Uncategorized'

        geo = t.get('geo_locations') or {}
        countries = list(geo.get('countries') or [])
        # City, region and zip targeting carries the country on each location.
        for k in ('regions', 'cities', 'zips', 'places', 'custom_locations'):
            for loc in geo.get(k) or []:
                if isinstance(loc, dict) and loc.get('country') and loc['country'] not in countries:
                    countries.append(loc['country'])
        market = '+'.join(MARKET.get(c, c) for c in sorted(countries)) if countries else 'Unspecified'

        st = status.get(m['ad_id'], {})
        live = (st.get('effective_status') == 'ACTIVE')
        rows.append({
            'Ad ID': m['ad_id'],
            'Funnel Stage': funnel,
            'Audience': audience,
            'Ad Format': fmt,
            'Market': market,
            'Custom audiences': '; '.join(cas),
            'Interest targeting': '; '.join(
                i.get('name', '') for s in flex for i in (s.get('interests') or []) + (s.get('behaviors') or [])),
            'Advantage+ audience': (t.get('targeting_automation') or {}).get('advantage_audience', ''),
            'Creative object type': ot or '',
            'Optimisation goal': m.get('adsset_optimization_goal') or '',
            'Optimisation event': po.get('custom_event_type', ''),
            'Pixel ID': po.get('pixel_id', ''),
            'Learning phase': m.get('adset_learning_stage_info') or '',
            'Bid strategy': m.get('campaign_bid_strategy') or '',
            'Campaign daily budget': (float(m['campaign_daily_budget']) if m.get('campaign_daily_budget') not in (None, 'None') else ''),
            'Ad set daily budget': (float(m['adset_daily_budget']) if m.get('adset_daily_budget') not in (None, 'None') else ''),
            'Delivery status': st.get('effective_status', 'Data not available'),
            'Ad set delivery status': st.get('adset_effective_status', 'Data not available'),
            'Campaign delivery status': st.get('campaign_effective_status', 'Data not available'),
            'Live': 'Yes' if live else 'No',
        })

    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"=== Metadata derivation ({len(rows)} ads) ===")
    for k in ('Funnel Stage', 'Audience', 'Ad Format', 'Market', 'Optimisation event',
              'Optimisation goal', 'Learning phase', 'Delivery status', 'Live'):
        print(f"  {k:<20} {dict(Counter(r[k] for r in rows).most_common())}")
    print(f"  Carousel metadata: {'used' if carousel else 'not supplied - SHARE ads counted as Static'}")
    print(f"\nWrote {out}")


if __name__ == '__main__':
    main()
