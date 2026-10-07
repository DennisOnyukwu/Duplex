#!/usr/bin/env python3
"""
Meta Ads Audit - build Google Sheets connector payloads (values + formatting requests)
for the reader-facing tabs, straight from the audit outputs, so nothing is retyped.

Tabs (sheetIds fixed here so formatting can be built without a metadata read):
    0 Read Me · 1 Monthly · 2 Zingers · 3 Tracking · 4 Findings · 5 Live Ad Sets

The Data, Lookup and Weekly tabs are too large to send cell by cell through the
connector; they ship in the .xlsx export of the same audit.

Usage:
    python gsheet_payload.py <out_dir> <findings.md> <account.json> <live_adsets.csv>
                             <zingers_live.csv> <zingers_nonlive.csv> <zingers_all.csv> <payload_dir>
Writes one JSON per tab: {"range": ..., "values": [...], "requests": [...]}.
"""
import sys
import os
import re
import csv
import json

sys.path.insert(0, os.path.dirname(__file__))
from build_workbook import md_sections, md_table, strip_md, ZINGER_TEXT, SEV_ORDER  # noqa: E402

TABS = {'Read Me': 0, 'Monthly': 1, 'Zingers': 2, 'Tracking': 3, 'Findings': 4, 'Live Ad Sets': 5}


def rgb(h):
    h = h.lstrip('#')
    return {'red': int(h[0:2], 16) / 255, 'green': int(h[2:4], 16) / 255, 'blue': int(h[4:6], 16) / 255}


NAVY, LIGHT, PALE, AMBER, RED, GREEN, GREY = '#1F3864', '#D9E1F2', '#F2F2F2', '#FFF2CC', '#F8CBAD', '#E2EFDA', '#7F7F7F'


def T(s):
    """Text cell: apostrophe so Sheets never reparses it as a number, date or formula."""
    return None if s is None else "'" + str(s)


def grid(sid, r0, r1, c0, c1):
    return {'sheetId': sid, 'startRowIndex': r0, 'endRowIndex': r1, 'startColumnIndex': c0, 'endColumnIndex': c1}


def fmt(sid, r0, r1, c0, c1, **k):
    f, fields = {}, []
    tf = {}
    if k.get('bold'):
        tf['bold'] = True
    if k.get('italic'):
        tf['italic'] = True
    if k.get('size'):
        tf['fontSize'] = k['size']
    if k.get('fg'):
        tf['foregroundColorStyle'] = {'rgbColor': rgb(k['fg'])}
    if tf:
        f['textFormat'] = tf
        fields += [f'userEnteredFormat.textFormat.{x}' for x in tf]
    if k.get('bg'):
        f['backgroundColorStyle'] = {'rgbColor': rgb(k['bg'])}
        fields.append('userEnteredFormat.backgroundColorStyle')
    if k.get('wrap'):
        f['wrapStrategy'] = 'WRAP'
        fields.append('userEnteredFormat.wrapStrategy')
    if k.get('valign'):
        f['verticalAlignment'] = k['valign']
        fields.append('userEnteredFormat.verticalAlignment')
    if k.get('number'):
        t, p = k['number']
        f['numberFormat'] = {'type': t, 'pattern': p}
        fields.append('userEnteredFormat.numberFormat')
    return {'repeatCell': {'range': grid(sid, r0, r1, c0, c1), 'cell': {'userEnteredFormat': f},
                           'fields': ','.join(fields)}}


def widths(sid, ws):
    return [{'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': i,
                                                     'endIndex': i + 1},
                                           'properties': {'pixelSize': w}, 'fields': 'pixelSize'}}
            for i, w in enumerate(ws)]


def freeze(sid, rows, cols=0):
    return {'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {
        'frozenRowCount': rows, 'frozenColumnCount': cols}},
        'fields': 'gridProperties.frozenRowCount,gridProperties.frozenColumnCount'}}


def merge(sid, r, c0, c1):
    return {'mergeCells': {'range': grid(sid, r, r + 1, c0, c1), 'mergeType': 'MERGE_ALL'}}


def border(sid, r0, r1, c0, c1):
    s = {'style': 'SOLID', 'colorStyle': {'rgbColor': rgb('#BFBFBF')}}
    return {'updateBorders': {'range': grid(sid, r0, r1, c0, c1), 'top': s, 'bottom': s, 'left': s, 'right': s,
                              'innerHorizontal': s, 'innerVertical': s}}


def header(sid, r, c0, c1):
    return fmt(sid, r, r + 1, c0, c1, bold=True, bg=NAVY, fg='#FFFFFF', wrap=True, valign='MIDDLE')


MONEY = ('CURRENCY', '"₦"#,##0')
MONEY2 = ('CURRENCY', '"₦"#,##0.00')
INT = ('NUMBER', '#,##0')
RATIO = ('NUMBER', '0.00')
DATE = ('DATE', 'yyyy-mm-dd')


def main():
    (outdir, findings_p, acct_p, live_p, zl_p, zn_p, za_p, pdir) = sys.argv[1:9]
    os.makedirs(pdir, exist_ok=True)
    md = open(findings_p, encoding='utf-8').read()
    sec = md_sections(md)
    acct = json.load(open(acct_p, encoding='utf-8'))
    payload = {}

    # ---------------- Monthly (data + ROAS/CPA formulas) ----------------
    sid = TABS['Monthly']
    rows = list(csv.reader(open(os.path.join(outdir, 'monthly.csv'), encoding='utf-8')))
    hdr = rows[0]
    vals = [hdr]
    for i, r in enumerate(rows[1:], start=2):
        def n(x):
            return float(x) if x not in ('', None) else None
        vals.append([T(r[0]), T(r[1]), T(r[2]), T(r[3]), T(r[4]), n(r[5]), n(r[6]), n(r[7]), n(r[8]), n(r[9]),
                     f'=IF(F{i}=0,"",J{i}/F{i})', f'=IF(I{i}=0,"",F{i}/I{i})'])
    nrow = len(vals)
    req = [header(sid, 0, 0, len(hdr)), freeze(sid, 1),
           fmt(sid, 1, nrow, 5, 6, number=MONEY2), fmt(sid, 1, nrow, 6, 9, number=INT),
           fmt(sid, 1, nrow, 9, 10, number=MONEY2), fmt(sid, 1, nrow, 10, 11, number=RATIO),
           fmt(sid, 1, nrow, 11, 12, number=MONEY2),
           {'setBasicFilter': {'filter': {'range': grid(sid, 0, nrow, 0, len(hdr))}}},
           {'updateCells': {'rows': [{'values': [{'note': (
               'Source: Meta Ads (Beguile, act 480225648142941) via Windsor.ai connector, ad level, daily, '
               f'pulled 2026-10-07 by Claude. {nrow - 1} rows: monthly rollup of 26,584 ad-day rows by Funnel Stage, '
               'Audience, Ad Format and Market. ROAS and CPA are formulas.')}]}],
               'fields': 'note', 'start': {'sheetId': sid, 'rowIndex': 0, 'columnIndex': 0}}}]
    req += widths(sid, [80, 100, 100, 100, 70, 130, 110, 90, 90, 140, 70, 110])
    payload['Monthly'] = {'range': f"Monthly!A1:L{nrow}", 'values': vals, 'requests': req}

    # ---------------- Read Me ----------------
    sid = TABS['Read Me']
    V, R = [], []

    def row(*cells):
        V.append(list(cells) + [None] * (4 - len(cells)))
        return len(V) - 1

    r = row(T(acct['title']))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=16, fg=NAVY))
    row()
    f0 = len(V)
    for k, v in acct['facts']:
        r = row(T(k), T(v))
        if k.lower().startswith('partial'):
            R.append(fmt(sid, r, r + 1, 1, 2, bg=GREEN))
    R.append(fmt(sid, f0, len(V), 0, 1, bold=True))
    R.append(fmt(sid, f0, len(V), 1, 2, wrap=True))
    row()
    r = row(T('Start here: what the audit found'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    for line in sec.get('Executive Summary', []):
        t = strip_md(line)
        if not t or t == '---':
            continue
        if t.startswith('- '):
            t = '• ' + t[2:]
        r = row(T(t))
        R.append(merge(sid, r, 0, 4))
        R.append(fmt(sid, r, r + 1, 0, 4, wrap=True, valign='TOP'))
    row()
    r = row(T('Headline figures (formulas over the Monthly tab)'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    h0 = len(V)
    row(T('Amount spent'), '=SUM(Monthly!F2:F)')
    row(T('Purchases (Meta-attributed)'), '=SUM(Monthly!I2:I)')
    row(T('Purchase value (Meta-attributed)'), '=SUM(Monthly!J2:J)')
    row(T('ROAS'), f'=IF(B{h0 + 1}=0,"",B{h0 + 3}/B{h0 + 1})')
    row(T('CPA'), f'=IF(B{h0 + 2}=0,"",B{h0 + 1}/B{h0 + 2})')
    R += [fmt(sid, h0, h0 + 5, 0, 1, bold=True),
          fmt(sid, h0, h0 + 1, 1, 2, number=MONEY2), fmt(sid, h0 + 1, h0 + 2, 1, 2, number=INT),
          fmt(sid, h0 + 2, h0 + 3, 1, 2, number=MONEY2), fmt(sid, h0 + 3, h0 + 4, 1, 2, number=RATIO),
          fmt(sid, h0 + 4, h0 + 5, 1, 2, number=MONEY2)]
    row()
    r = row(T('By market, 12 months (formulas over the Monthly tab)'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    mh = row(T('Market'), T('Amount spent'), T('ROAS'), T('CPA'))
    R.append(header(sid, mh, 0, 4))
    m0 = len(V)
    for m in ('NG', 'CA', 'UK', 'US'):
        i = len(V) + 1
        row(T(m), f'=SUMIFS(Monthly!$F:$F,Monthly!$E:$E,A{i})',
            f'=IF(B{i}=0,"",SUMIFS(Monthly!$J:$J,Monthly!$E:$E,A{i})/B{i})',
            f'=IF(SUMIFS(Monthly!$I:$I,Monthly!$E:$E,A{i})=0,"",B{i}/SUMIFS(Monthly!$I:$I,Monthly!$E:$E,A{i}))')
    R += [fmt(sid, m0, len(V), 1, 2, number=MONEY), fmt(sid, m0, len(V), 2, 3, number=RATIO),
          fmt(sid, m0, len(V), 3, 4, number=MONEY), border(sid, mh, len(V), 0, 4)]
    r = row(T('Markets with under ₦100,000 of spend (UK+NG) are left out of this table.'))
    R.append(fmt(sid, r, r + 1, 0, 1, italic=True, fg=GREY))
    row()
    r = row(T('Prioritised actions (detail in Findings, section 9)'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    ah = row(T('Priority'), T('Action'), T('Worth'), T('Where to look'))
    R.append(header(sid, ah, 0, 4))
    for head, body in sec.items():
        m = re.match(r'^\[(.+?)\]\s*(.*)', head)
        if not m:
            continue
        worth = next((strip_md(l).split('Worth:', 1)[1].strip() for l in body if 'Worth:' in l), '')
        worth = worth[:1].upper() + worth[1:]
        where = 'Live Ad Sets tab' if any(w in head for w in ('Nigeria', 'winners', 'Awareness')) else 'Findings, section 9'
        r = row(T(m.group(1)), T(m.group(2)), T(worth), T(where))
        pr = m.group(1)
        R.append(fmt(sid, r, r + 1, 0, 1, bg=RED if 'High' in pr else AMBER if 'Medium' in pr else LIGHT))
    R += [fmt(sid, ah + 1, len(V), 0, 4, wrap=True, valign='TOP'), border(sid, ah, len(V), 0, 4)]
    r = row(T('Nothing in the ad account has been changed. Every action is a recommendation to test.'))
    R.append(fmt(sid, r, r + 1, 0, 1, italic=True, fg=GREY))
    row()
    r = row(T('Tabs in this sheet'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    g0 = len(V)
    for k, v in [
        ('Monthly', 'Monthly rollup by Funnel Stage, Audience, Ad Format and Market. ROAS and CPA are formulas.'),
        ('Zingers', 'Waste found by fixed thresholds: one summary row per zinger and scope, then every live-ad instance.'),
        ('Tracking', 'Whether the account can measure itself. Read before trusting any ROAS figure.'),
        ('Findings', 'The full report: live ads first (Part A), then other ads and the 12-month view (Part B).'),
        ('Live Ad Sets', 'One row per live ad set with a verdict, the reason and the figures.'),
        ('Data, Lookup, Weekly', 'The ad-by-day fact table (26,584 rows), the per-ad lookup (1,413 rows) and the weekly '
                                 'rollup are in the .xlsx export of this audit. In Google Sheets: File > Import > Upload, '
                                 'choose "Insert new sheet(s)".'),
    ]:
        row(T(k), T(v))
    R += [fmt(sid, g0, len(V), 0, 1, bold=True), fmt(sid, g0, len(V), 1, 2, wrap=True)]
    row()
    r = row(T('Definitions'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    d0 = len(V)
    for k, v in acct['definitions']:
        row(T(k), T(v))
    R += [fmt(sid, d0, len(V), 0, 1, bold=True, wrap=True, valign='TOP'), fmt(sid, d0, len(V), 1, 2, wrap=True)]
    row()
    r = row(T('Data quality'))
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    q0 = len(V)
    for line in open(os.path.join(outdir, 'dq_report.txt'), encoding='utf-8'):
        line = line.rstrip()
        if not line or line.startswith(('=', 'Meta Ads Audit', 'Currency: confirm', 'Category columns')):
            continue
        k, _, v = line.partition(':')
        row(T(k.strip()), T(v.strip()))
    for k, v in acct['dq_extra']:
        row(T(k), T(v))
    R += [fmt(sid, q0, len(V), 0, 1, bold=True, wrap=True, valign='TOP'), fmt(sid, q0, len(V), 1, 2, wrap=True)]
    R += widths(sid, [230, 430, 380, 140])
    R.append({'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'hideGridlines': True}},
                                        'fields': 'gridProperties.hideGridlines'}})
    payload['Read Me'] = {'range': f"'Read Me'!A1:D{len(V)}", 'values': V, 'requests': R}

    # ---------------- Zingers ----------------
    sid = TABS['Zingers']
    V, R = [], []
    zl = list(csv.DictReader(open(zl_p, encoding='utf-8')))
    zn = list(csv.DictReader(open(zn_p, encoding='utf-8')))
    za = list(csv.DictReader(open(za_p, encoding='utf-8')))
    V.append([T('Zingers: summary')] + [None] * 7)
    R.append(fmt(sid, 0, 1, 0, 1, bold=True, size=13, fg=NAVY))
    V.append([T('Fixed thresholds from Part 5; none were changed. Account averages: ' + acct['averages'])] + [None] * 7)
    R.append(fmt(sid, 1, 2, 0, 1, italic=True, fg=GREY))
    V.append([T(h) for h in ['Scope', 'Zinger', 'Severity', 'Finding', 'Fired', 'Spend involved', 'What it means',
                             'What to do']])
    R.append(header(sid, 2, 0, 8))
    s0 = len(V)
    for group in (zl, zn, za):
        sc = group[0]['Scope']
        ids = sorted({z['Zinger'] for z in group},
                     key=lambda i: (SEV_ORDER.index(next(z['Severity'] for z in group if z['Zinger'] == i)),
                                    int(i[1:])))
        for zid in ids:
            zs = [z for z in group if z['Zinger'] == zid]
            title, meaning, todo = ZINGER_TEXT[zid]
            sev = zs[0]['Severity']
            r = len(V)
            V.append([T(sc), T(zid), T(sev), T(title), len(zs), round(sum(float(z['Spend involved']) for z in zs), 2),
                      T(meaning), T(todo)])
            R.append(fmt(sid, r, r + 1, 2, 3, bg=RED if sev == 'Highest' else AMBER if sev == 'High'
                         else LIGHT if sev == 'Medium' else PALE))
        nf = [k for k in ZINGER_TEXT if k not in {z['Zinger'] for z in group}]
        r = len(V)
        V.append([T(f"{sc}: did not fire: {', '.join(nf) or 'none'}")] + [None] * 7)
        R.append(fmt(sid, r, r + 1, 0, 1, italic=True, fg=GREY))
    R += [fmt(sid, s0, len(V), 0, 8, wrap=True, valign='TOP'), fmt(sid, s0, len(V), 5, 6, number=MONEY)]
    V.append([None] * 8)
    r = len(V)
    V.append([T('Every fired instance: live ads')] + [None] * 7)
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=13, fg=NAVY))
    r = len(V)
    V.append([T('The 235 instances for other (not live) ads and the 265 account-wide ones are on the Zingers tab '
                'of the .xlsx export.')] + [None] * 7)
    R.append(fmt(sid, r, r + 1, 0, 1, italic=True, fg=GREY))
    dh = len(V)
    V.append([T(h) for h in ['Scope', 'Zinger', 'Severity', 'Finding', 'Basis', 'Spend involved', 'Entity', 'Detail']])
    R.append(header(sid, dh, 0, 8))
    for z in zl:
        V.append([T(z['Scope']), T(z['Zinger']), T(z['Severity']), T(z['Finding']), T(z['Basis']),
                  float(z['Spend involved']), T(z['Entity']), T(z['Detail'])])
    R += [fmt(sid, dh + 1, len(V), 0, 8, wrap=True, valign='TOP'), fmt(sid, dh + 1, len(V), 5, 6, number=MONEY2),
          border(sid, 2, s0 + 0, 0, 8)]
    R += widths(sid, [150, 55, 75, 190, 60, 120, 330, 380])
    R.append(freeze(sid, 3))
    payload['Zingers'] = {'range': f"Zingers!A1:H{len(V)}", 'values': V, 'requests': R}

    # ---------------- Tracking ----------------
    sid = TABS['Tracking']
    trk = next(v for k, v in sec.items() if k.startswith('8.'))
    t = md_table(trk)
    V = [[T(c) for c in row_] for row_ in t]
    R = [header(sid, 0, 0, 3), freeze(sid, 1), fmt(sid, 1, len(V), 0, 3, wrap=True, valign='TOP'),
         fmt(sid, 1, len(V), 0, 1, bold=True), border(sid, 0, len(V), 0, 3)]
    for i, row_ in enumerate(t[1:], start=1):
        st = row_[1].lower()
        c = (PALE if st.startswith('data not available') else
             RED if any(w in st for w in ('107', 'not parseable', 'higher than', 'fallen')) else
             GREEN if st.startswith(('yes', 'passed', 'purchase')) else AMBER)
        R.append(fmt(sid, i, i + 1, 1, 2, bg=c))
    effect_i = next(i for i, l in enumerate(trk) if l.startswith('**Effect'))
    V.append([None] * 3)
    r = len(V)
    V.append([T('Effect on this audit'), None, None])
    R.append(fmt(sid, r, r + 1, 0, 1, bold=True, size=12, fg=NAVY))
    for l in trk[effect_i + 1:]:
        s = strip_md(l)
        if not s or s == '---':
            continue
        indent = len(l) - len(l.lstrip(' '))
        if s.startswith('- '):
            s = ('    – ' if indent else '• ') + s[2:]
        r = len(V)
        V.append([T(s), None, None])
        R += [merge(sid, r, 0, 3), fmt(sid, r, r + 1, 0, 3, wrap=True, valign='TOP')]
    R += widths(sid, [230, 420, 460])
    payload['Tracking'] = {'range': f"Tracking!A1:C{len(V)}", 'values': V, 'requests': R}

    # ---------------- Findings ----------------
    sid = TABS['Findings']
    NC = 7
    V, R = [], []
    para_rows = []
    lines = md.split('\n')
    k = 0
    while k < len(lines):
        line = lines[k]
        if line.startswith('|'):
            block = []
            while k < len(lines) and lines[k].startswith('|'):
                block.append(lines[k])
                k += 1
            t = md_table(block)
            top = len(V)
            for row_ in t:
                V.append([T(c) for c in row_] + [None] * (NC - len(row_)))
            ncols = len(t[0])
            R += [header(sid, top, 0, ncols), border(sid, top, len(V), 0, ncols)]
            last = t[-1][0].lower()
            if last.startswith('total') or last.startswith('**total'):
                R.append(fmt(sid, len(V) - 1, len(V), 0, ncols, bold=True))
            V.append([None] * NC)
            continue
        k += 1
        s = line.rstrip()
        if not s.strip() or s.strip() == '---':
            continue
        m = re.match(r'^(#{1,3}) (.*)', s)
        r = len(V)
        if m:
            level = len(m.group(1))
            if level == 1 and r > 0:
                V.append([None] * NC)
                r = len(V)
            V.append([T(strip_md(m.group(2)))] + [None] * (NC - 1))
            R.append(fmt(sid, r, r + 1, 0, NC if level == 1 else 1, bold=True, size={1: 15, 2: 13, 3: 11}[level],
                         fg=NAVY if level < 3 else '#000000', bg=LIGHT if level == 1 else None))
            continue
        indent = len(s) - len(s.lstrip(' '))
        text = strip_md(s)
        if text.startswith('- '):
            text = ('    – ' if indent else '• ') + text[2:]
        V.append([T(text)] + [None] * (NC - 1))
        para_rows.append(r)
        if s.lstrip().startswith('**') and s.rstrip().endswith('**'):
            R.append(fmt(sid, r, r + 1, 0, 1, bold=True))
    # Paragraph rows: one MERGE_ROWS request per contiguous run instead of one merge per row.
    runs, start = [], None
    for i, rr in enumerate(para_rows):
        if start is None:
            start = rr
        if i + 1 == len(para_rows) or para_rows[i + 1] != rr + 1:
            runs.append((start, rr + 1))
            start = None
    R += [{'mergeCells': {'range': grid(sid, a, b, 0, NC), 'mergeType': 'MERGE_ROWS'}} for a, b in runs]
    # One wrap/top rule for the whole tab, placed first so header and heading formats sit on top of it.
    R.insert(0, fmt(sid, 0, len(V), 0, NC, wrap=True, valign='TOP'))
    R += widths(sid, [260, 190, 120, 120, 120, 120, 120])
    R.append({'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'hideGridlines': True}},
                                        'fields': 'gridProperties.hideGridlines'}})
    payload['Findings'] = {'range': f"Findings!A1:G{len(V)}", 'values': V, 'requests': R}

    # ---------------- Live Ad Sets ----------------
    sid = TABS['Live Ad Sets']
    rows = list(csv.DictReader(open(live_p, encoding='utf-8')))
    hdr = list(rows[0].keys())
    V = [[T(h) for h in hdr]]
    numeric = {'Daily budget (₦)', 'Live ads', 'Amount spent (12m)', 'Purchases (12m)', 'ROAS (12m)', 'CPA (12m)',
               'Amount spent (last 7d)', 'Purchases (last 7d)'}
    for rr in rows:
        out = []
        for h in hdr:
            v = rr[h]
            if h in numeric:
                out.append(float(v) if v not in ('', None) else '')
            elif h == 'First spend date':
                out.append(v)
            else:
                out.append(T(v))
        V.append(out)
    n = len(V)
    col = {h: i for i, h in enumerate(hdr)}
    R = [header(sid, 0, 0, len(hdr)), freeze(sid, 1, 3),
         fmt(sid, 1, n, 0, 2, wrap=True, valign='TOP'),
         fmt(sid, 1, n, col['Daily budget (₦)'], col['Daily budget (₦)'] + 1, number=MONEY),
         fmt(sid, 1, n, col['First spend date'], col['First spend date'] + 1, number=DATE),
         fmt(sid, 1, n, col['Live ads'], col['Live ads'] + 1, number=INT),
         fmt(sid, 1, n, col['Amount spent (12m)'], col['Amount spent (12m)'] + 1, number=MONEY),
         fmt(sid, 1, n, col['Purchases (12m)'], col['Purchases (12m)'] + 1, number=INT),
         fmt(sid, 1, n, col['ROAS (12m)'], col['ROAS (12m)'] + 1, number=RATIO),
         fmt(sid, 1, n, col['CPA (12m)'], col['CPA (12m)'] + 1, number=MONEY),
         fmt(sid, 1, n, col['Amount spent (last 7d)'], col['Amount spent (last 7d)'] + 1, number=MONEY),
         fmt(sid, 1, n, col['Purchases (last 7d)'], col['Purchases (last 7d)'] + 1, number=INT),
         {'setBasicFilter': {'filter': {'range': grid(sid, 0, n, 0, len(hdr))}}},
         {'updateCells': {'rows': [{'values': [{'note': (
             'Source: Meta Ads (Beguile, act 480225648142941) via Windsor.ai connector, pulled 2026-10-07 by Claude. '
             f'{n - 1} rows: live ad sets (effective status ACTIVE). Verdicts follow fixed rules: Scale if ROAS is at '
             'least 1.5x the account ROAS (6.28); Keep if at least 1x; Watch if below; Too early if first spend was '
             'in the last 7 days; Check targeting where the campaign name and targeted market differ.')}]}],
             'fields': 'note', 'start': {'sheetId': sid, 'rowIndex': 0, 'columnIndex': 0}}}]
    for i, rr in enumerate(rows, start=1):
        v = rr['Verdict']
        R.append(fmt(sid, i, i + 1, 0, 1, bg=RED if v.startswith('Check') else GREEN if v.startswith('Scale') else
                     LIGHT if v.startswith('Keep') else AMBER if v.startswith('Watch') else PALE))
    R += widths(sid, [300, 260, 230, 200, 150, 60, 80, 120, 130, 140, 100, 110, 110, 70, 130, 100, 80, 110, 140, 110])
    payload['Live Ad Sets'] = {'range': f"'Live Ad Sets'!A1:T{n}", 'values': V, 'requests': R}

    for name, p in payload.items():
        fn = os.path.join(pdir, f"{TABS[name]}_{name.replace(' ', '_')}.json")
        json.dump(p, open(fn, 'w', encoding='utf-8'), ensure_ascii=False)
        print(f"{name:<13} rows={len(p['values']):>4} values={len(json.dumps(p['values'], ensure_ascii=False)):>7} chars "
              f"requests={len(p['requests'])}")


if __name__ == '__main__':
    main()
