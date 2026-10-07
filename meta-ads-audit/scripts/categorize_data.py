#!/usr/bin/env python3
"""
Meta Ads Audit - categorisation with automatic pattern adaptation.

Adds three columns to an ad-level dataset:
    Funnel Stage : Prospecting | RTG | Uncategorized
    Audience     : LAL | Interest | Broad | WebVisitors | ATC | Engagers | Uncategorized
    Ad Format    : Video | Static | GIF | Carousel | Catalogue | Uncategorized

Samples the account's naming first (highest-spend values first), measures the
match rate against the default patterns, and falls back to an extended synonym
set when the match rate is poor. Reports which tier produced each match in a
"<level> tier" column (default | extended | metadata | none).

Optional --meta <file.csv>: a per-ad file keyed on "Ad ID" carrying Funnel Stage,
Audience and/or Ad Format derived from Meta's own creative and targeting
metadata. It is used only for rows the names could not categorise, and every
such row is marked tier=metadata so the source is never hidden.

Usage:
    python categorize_data.py <input.csv> <output.csv> [--threshold 0.85] [--meta meta.csv]
                              [--prefer-meta] [--quiet]
"""
import sys
import re
import csv
from collections import Counter, defaultdict

DEFAULT_THRESHOLD = 0.85

# Token boundary: \b treats "_" as a word character, so \bPRSP\b would miss
# "PRSP_LAL". These lookarounds treat anything that is not a letter or digit
# as a separator, while still stopping CAR matching inside CARDIGAN.
L = r'(?<![A-Za-z0-9])'
R = r'(?![A-Za-z0-9])'


def tok(body):
    return L + body + R


DEFAULT_PATTERNS = {
    'Funnel Stage': [
        ('Prospecting', tok(r'PRSP')),
        ('RTG', tok(r'RMK')),
    ],
    'Audience': [
        ('LAL', tok(r'LAL')),
        ('Interest', tok(r'Interest')),
        ('Broad', tok(r'broad')),
        ('WebVisitors', tok(r'Visitors')),
        ('ATC', tok(r'ATC')),
        ('Engagers', tok(r'Engagers')),
    ],
    'Ad Format': [
        ('Video', tok(r'VID')),
        ('Static', tok(r'IMG')),
        ('GIF', tok(r'GIF')),
        ('Carousel', tok(r'CAR')),
        ('Catalogue', tok(r'DPA')),
    ],
}

EXTENDED_PATTERNS = {
    'Funnel Stage': [
        ('Prospecting', tok(r'(PRSP|PROSP|PROS|PRO|ACQ|TOF|COLD|NEWCUST|NEW)')),
        ('RTG', tok(r'(RMKT|RMK|RETARGET|RETG|RET|RT|BOF|WARM|REM)')),
    ],
    'Audience': [
        ('LAL', tok(r'(LAL\d*|LLA|LOOKALIKE)')),
        ('Interest', tok(r'(INTEREST|INT)')),
        ('Broad', tok(r'(BROAD|BRO|OPEN|GENERAL)')),
        ('WebVisitors', tok(r'(VISITORS|VISITOR|SITEVIS|ALLVISITORS|WV|WEB|SITE)')),
        ('ATC', tok(r'(ADDTOCART|ATC|CART)')),
        ('Engagers', tok(r'(ENGAGERS|ENGAGER|IGENG|FBENG|ENGAGEMENT|ENG)')),
    ],
    'Ad Format': [
        ('Video', tok(r'(VIDEO|VID|REELS|REEL|V)')),
        ('Static', tok(r'(STATIC|STAT|IMAGE|IMG|PHOTO|S)')),
        ('GIF', tok(r'GIF')),
        ('Carousel', tok(r'(CAROUSEL|CAROUS|CARO|CAR)')),
        ('Catalogue', tok(r'(CATALOGUE|CATALOG|DABA|DPA|ASC|ADVANTAGE|CAT)')),
    ],
}

LEVELS = [
    ('Funnel Stage', ['Campaign Name', 'campaign_name', 'Campaign']),
    ('Audience', ['Ad Set Name', 'adset_name', 'Ad Set']),
    ('Ad Format', ['Ad Name', 'ad_name', 'Ad']),
]


def find_column(fieldnames, candidates):
    lower = {f.lower().strip(): f for f in fieldnames}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    for c in candidates:
        for f in fieldnames:
            if c.lower().replace(' ', '') in f.lower().replace(' ', ''):
                return f
    return None


def match(text, patterns):
    if text is None:
        return None
    for label, pat in patterns:
        if re.search(pat, str(text), re.IGNORECASE):
            return label
    return None


def match_rate(values, patterns):
    if not values:
        return 0.0
    hit = sum(1 for v in values if match(v, patterns))
    return hit / len(values)


def unmatched_tokens(values, patterns, limit=25):
    counter = Counter()
    for v in values:
        if match(v, patterns):
            continue
        for t in re.split(r'[\s_\-\|/\.\[\]\(\)]+', str(v)):
            t = t.strip()
            if len(t) > 1 and not t.isdigit():
                counter[t] += 1
    return counter.most_common(limit)


def choose_patterns(level, values, threshold):
    rate_default = match_rate(values, DEFAULT_PATTERNS[level])
    if rate_default >= threshold:
        return DEFAULT_PATTERNS[level], 'default', rate_default, rate_default
    rate_ext = match_rate(values, EXTENDED_PATTERNS[level])
    if rate_ext > rate_default:
        return EXTENDED_PATTERNS[level], 'extended', rate_ext, rate_default
    return DEFAULT_PATTERNS[level], 'default', rate_default, rate_default


def to_spend(v):
    try:
        return float(str(v or 0).replace(',', '').replace('$', '') or 0)
    except ValueError:
        return 0.0


def main():
    argv = sys.argv[1:]
    opts = {}
    args = []
    i = 0
    while i < len(argv):
        if argv[i] in ('--threshold', '--meta'):
            opts[argv[i]] = argv[i + 1]
            i += 2
        elif argv[i].startswith('--'):
            opts[argv[i]] = True
            i += 1
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 2:
        print(__doc__)
        sys.exit(1)

    threshold = float(opts.get('--threshold', DEFAULT_THRESHOLD))
    quiet = '--quiet' in opts
    # --prefer-meta: use the metadata labels for every ad that has them, and names
    # only where metadata is missing. For accounts where the name tiers produce
    # false positives (e.g. "NEW" in "New Launch" read as Prospecting).
    prefer_meta = '--prefer-meta' in opts
    inp, outp = args[0], args[1]

    with open(inp, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        print("Error: input has no rows.")
        sys.exit(1)

    resolved = {}
    for level, candidates in LEVELS:
        col = find_column(fieldnames, candidates)
        if not col:
            print(f"Error: could not find a column for {level}. Looked for: {candidates}")
            print(f"Available columns: {fieldnames}")
            sys.exit(1)
        resolved[level] = col

    spend_col = find_column(fieldnames, ['Amount spent', 'Amount Spent', 'Spend', 'amount_spent'])
    adid_col = find_column(fieldnames, ['Ad ID', 'ad_id'])

    meta = {}
    if '--meta' in opts:
        with open(opts['--meta'], newline='', encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                meta[r['Ad ID']] = r

    # Sample up to 50 distinct values per level, highest spend first.
    sample = {}
    for level, col in resolved.items():
        by_spend = defaultdict(float)
        for r in rows:
            v = r.get(col)
            if v:
                by_spend[v] += to_spend(r.get(spend_col)) if spend_col else 0
        sample[level] = [v for v, _ in sorted(by_spend.items(), key=lambda kv: -kv[1])[:50]]

    chosen, tiers = {}, {}
    if not quiet:
        print("=== Naming convention detection (top-50 by spend) ===")
    for level in resolved:
        patterns, tier, rate, rate_default = choose_patterns(level, sample[level], threshold)
        chosen[level] = patterns
        tiers[level] = tier
        if not quiet:
            print(f"  {level:<14} default match rate={rate_default:.1%} | chosen tier={tier:<9} "
                  f"match rate={rate:.1%} (sample of {len(sample[level])})")
            if rate < threshold:
                toks = unmatched_tokens(sample[level], patterns)
                if toks:
                    print(f"    unmatched tokens to consider: {', '.join(t for t, _ in toks[:15])}")

    out_fields = list(fieldnames)
    for level in resolved:
        for c in (level, f'{level} tier'):
            if c not in out_fields:
                out_fields.append(c)
    # Market is not one of the three audit levels; it is carried from the
    # metadata file when supplied, because this account's names key on it.
    carry_market = bool(meta) and 'Market' in next(iter(meta.values()))
    if carry_market and 'Market' not in out_fields:
        out_fields.append('Market')

    counts = {level: Counter() for level in resolved}
    tier_counts = {level: Counter() for level in resolved}
    spend_by = {level: defaultdict(float) for level in resolved}
    tier_spend = {level: defaultdict(float) for level in resolved}

    for r in rows:
        sp = to_spend(r.get(spend_col)) if spend_col else 0.0
        if carry_market:
            r['Market'] = meta.get(r.get(adid_col), {}).get('Market') or 'Data not available'
        for level, col in resolved.items():
            label = match(r.get(col), chosen[level])
            tier = tiers[level] if label else 'none'
            if prefer_meta:
                label, tier = None, 'none'
            if not label and meta:
                m = meta.get(r.get(adid_col), {}).get(level)
                if m and m != 'Uncategorized':
                    label, tier = m, 'metadata'
            if not label and prefer_meta:
                label = match(r.get(col), chosen[level])
                tier = tiers[level] if label else 'none'
            label = label or 'Uncategorized'
            r[level] = label
            r[f'{level} tier'] = tier
            counts[level][label] += 1
            tier_counts[level][tier] += 1
            spend_by[level][label] += sp
            tier_spend[level][tier] += sp

    total_spend = sum(spend_by['Funnel Stage'].values()) if spend_col else 0.0

    with open(outp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(rows)

    if not quiet:
        print(f"\n=== Categorisation result ({len(rows)} rows) ===")
        for level in resolved:
            n = len(rows)
            unc = counts[level]['Uncategorized']
            line = f"  {level:<14} uncategorized {unc}/{n} ({unc / n:.1%})"
            if spend_col and total_spend:
                us = spend_by[level]['Uncategorized']
                line += f"  | by spend {us / total_spend:.1%}"
            print(line)
            for t, c in tier_counts[level].most_common():
                ts = tier_spend[level][t] / total_spend if total_spend else 0
                print(f"      tier {t:<10} rows {c:>7}  spend {ts:.1%}")
            for label, c in counts[level].most_common():
                ls = spend_by[level][label] / total_spend if total_spend else 0
                print(f"      {label:<14} rows {c:>7}  spend {ls:.1%}")
        if spend_col and total_spend:
            print(f"\n  Total spend parsed: {total_spend:,.2f}")

    print(f"\nWrote {outp}")

    flagged = False
    for level in resolved:
        share = (spend_by[level]['Uncategorized'] / total_spend) if total_spend else \
            counts[level]['Uncategorized'] / len(rows)
        if share > 0.15:
            print(f"Warning: {level} uncategorized share by spend is {share:.1%}, above 15%. "
                  f"Report this as a data-quality finding.")
            flagged = True
    if flagged:
        sys.exit(2)


if __name__ == '__main__':
    main()
