#!/usr/bin/env python3
"""
Meta Ads Audit - assemble the audit workbook.

Tab order (Part 2, section 4), plus an action tab at the end:
    Read Me | Data | Lookup | Monthly | Weekly | Zingers | Tracking | Findings | Live Ad Sets

Built to be read, not just stored:
    Read Me     opens with the executive summary and the prioritised actions, then the
                account facts, how to use the tabs and the data-quality summary.
    Findings    the narrative rendered as headings, wrapped paragraphs and real tables.
    Zingers     one summary row per zinger and scope first, then every fired instance.
    Tracking    the measurement table from the findings, one row per item.
    Data tabs   typed values (dates as dates, numbers as numbers, IDs as text so 18-digit
                Meta IDs are not rounded), currency / percentage formats, frozen headers,
                autofilter. No formulas.

Usage:
    python build_workbook.py <output_dir> <findings.md> --out audit.xlsx
        [--zingers z1.csv,z2.csv,...] [--live live_adsets.csv] [--meta-json account.json]
"""
import sys
import os
import re
import csv
import json
from datetime import date

TAB_ORDER = ['Read Me', 'Data', 'Lookup', 'Monthly', 'Weekly', 'Zingers', 'Tracking', 'Findings',
             'Live Ad Sets']
MAX_ROWS = 200000

NAVY = '1F3864'
LIGHT = 'D9E1F2'
PALE = 'F2F2F2'
AMBER = 'FFF2CC'
RED = 'F8CBAD'
GREEN = 'E2EFDA'

MONEY = '"₦"#,##0.00'
MONEY0 = '"₦"#,##0'
INT = '#,##0'
RATIO = '0.00'
PCT = '0.00%'

ZINGER_TEXT = {
    'Z1': ('Spend producing no purchases',
           'Ad sets that spent at least 1.5x the account CPA and bought nothing measurable.',
           'Check objective first (Reach/Traffic ad sets are not meant to buy). For Sales ad sets, '
           'stop launching new ad sets abroad on ₦10-15k/day budgets; see recommendation 2.'),
    'Z2': ('Learning-limited ad sets',
           'Active ad sets under 50 purchases in the last 7 days while spending more than one CPA.',
           'Consolidate into fewer ad sets with enough budget to clear 50 a week (recommendation 1).'),
    'Z3': ('Retargeting starved of budget', 'Retargeting under 10% of spend while returning 2x prospecting.', '—'),
    'Z4': ('Prospecting inefficiency', 'Prospecting over 80% of spend at ROAS below 1.0.', '—'),
    'Z5': ('Fragmentation',
           'Over 40% of ad sets below the 50-conversion line and the top 5 hold under 40% of spend.',
           'Same root cause as Z2: too many small, short-lived ad sets. Consolidate.'),
    'Z6': ('Format funded without justification', 'A format with 15%+ of spend at under half the account ROAS.', '—'),
    'Z7': ('Creative fatigue',
           'Ads whose ROAS in their last 30 days is 40%+ below their first 30 days.',
           'Refresh creative inside the same ad set rather than pausing it (recommendation 3).'),
    'Z8': ('Zombie ads', 'Ads active 30+ days with zero purchases.', 'All are already paused; no action beyond not repeating it.'),
    'Z9': ('Concentration risk', 'One ad set or ad over 50% of account spend.', '—'),
    'Z10': ('Audience overlap risk',
            'Broad, Interest and Lookalike ad sets running on the same days on the same objective.',
            'Hypothesis only: confirm with an audience-overlap check in Ads Manager before acting.'),
    'Z11': ('Cost trend against you', 'CPM or CPA up 25%+ between the prior and recent 90 days at stable spend.', '—'),
    'Z12': ('Underfunded winner',
            'Ad sets returning 1.5x the account ROAS on under 5% of spend.',
            'Live: give these budget inside the consolidated NG campaign. Paused: reuse their creative.'),
}
SEV_ORDER = ['Highest', 'High', 'Medium', 'Watch']


def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.reader(f))


def num(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == '':
        return None
    try:
        x = float(s)
    except ValueError:
        return s
    return int(x) if x.is_integer() and 'e' not in s.lower() else x


def col_kind(header):
    h = header.lower()
    if h.endswith(' id') or h in ('ad id', 'ad set id', 'campaign id'):
        return 'text'
    if h in ('date', 'first date active', 'last date active', 'first spend date') or \
            (h == 'period' and False):
        return 'date'
    if h in ('ctr', 'cvr', 'share', 'spend %'):
        return 'pct'
    if h in ('roas', 'blended roas', 'roas (12m)'):
        return 'ratio'
    if any(k in h for k in ('amount spent', 'purchase value', 'total spend', 'cpm', 'cpc', 'cpa',
                            'spend involved', 'daily budget')):
        return 'money'
    if any(k in h for k in ('impressions', 'clicks', 'purchases', 'days active', 'adds to cart',
                            'checkouts', 'content views', 'live ads', 'total purchases')):
        return 'int'
    return 'auto'


def typed(v, kind):
    if v is None or v == '':
        return None
    if kind == 'text':
        return str(v)
    if kind == 'auto' and re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(v)):
        return date.fromisoformat(str(v))
    if kind == 'date':
        try:
            return date.fromisoformat(str(v)[:10])
        except ValueError:
            return str(v)
    if kind in ('pct', 'ratio', 'money', 'int'):
        return num(v)
    return num(v)


FMT = {'pct': PCT, 'ratio': RATIO, 'money': MONEY, 'int': INT, 'date': 'yyyy-mm-dd'}


def est_lines(text, width_chars):
    lines = 0
    for part in str(text).split('\n'):
        lines += max(1, -(-len(part) // max(width_chars, 1)))
    return lines


# ---------------------------------------------------------------- markdown helpers

def strip_md(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\1', s)
    s = s.replace('\\|', '|').replace('`', '')
    return s.strip()


def md_sections(md):
    """Split findings markdown into {heading: [lines]} at ## / ### level (and # parts)."""
    out, cur = {}, None
    for line in md.split('\n'):
        m = re.match(r'^(#{1,3}) (.*)', line)
        if m:
            cur = m.group(2).strip()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def md_table(lines):
    rows = []
    for l in lines:
        if l.startswith('|'):
            cells = [c.strip() for c in re.split(r'(?<!\\)\|', l.strip())[1:-1]]
            if all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
                continue
            rows.append([strip_md(c) for c in cells])
    return rows


# ---------------------------------------------------------------- workbook

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
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    outdir, findings_path = args[0], args[1]
    out_path = opts.get('--out', 'meta-ads-audit.xlsx')
    acct = json.load(open(opts['--meta-json'])) if '--meta-json' in opts else {}

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("Error: openpyxl required. pip install openpyxl")
        sys.exit(1)

    md = open(findings_path, encoding='utf-8').read()
    sections = md_sections(md)

    wb = Workbook()
    wb.remove(wb.active)
    hfont = Font(bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor=NAVY)
    wrap_top = Alignment(wrap_text=True, vertical='top')
    thin = Side(style='thin', color='BFBFBF')
    box = Border(left=thin, right=thin, top=thin, bottom=thin)

    def fill(c):
        return PatternFill('solid', fgColor=c)

    def header_row(ws, row, headers, col0=1):
        for j, h in enumerate(headers):
            c = ws.cell(row=row, column=col0 + j, value=h)
            c.font = hfont
            c.fill = hfill
            c.alignment = Alignment(wrap_text=True, vertical='center')
            c.border = box

    # ---- data tabs -----------------------------------------------------------------
    def data_tab(name, path, widths=None, freeze_cols=0):
        if not os.path.exists(path):
            print(f"Note: {path} not found, skipping {name}.")
            return None
        rows = read_csv(path)
        if len(rows) - 1 > MAX_ROWS:
            print(f"Note: {name} has {len(rows) - 1} rows, above {MAX_ROWS}; split by year or quarter.")
        ws = wb.create_sheet(name)
        hdr = rows[0]
        kinds = [col_kind(h) for h in hdr]
        ws.append(hdr)
        for r in rows[1:]:
            ws.append([typed(v, kinds[j]) for j, v in enumerate(r)])
        header_row(ws, 1, hdr)
        for j, k in enumerate(kinds):
            if k in FMT:
                letter = get_column_letter(j + 1)
                for cell in ws[letter][1:]:
                    cell.number_format = FMT[k]
            elif k == 'auto' and len(rows) > 1 and re.fullmatch(r'\d{4}-\d{2}-\d{2}', rows[1][j] or ''):
                for cell in ws[get_column_letter(j + 1)][1:]:
                    cell.number_format = 'yyyy-mm-dd'
            elif k == 'text':
                for cell in ws[get_column_letter(j + 1)][1:]:
                    cell.number_format = '@'
        for j, h in enumerate(hdr):
            longest = max([len(h)] + [len(str(r[j])) for r in rows[1:300] if j < len(r)])
            ws.column_dimensions[get_column_letter(j + 1)].width = min(max(10, longest + 2), 45)
        ws.row_dimensions[1].height = 30
        ws.freeze_panes = ws.cell(row=2, column=freeze_cols + 1)
        ws.auto_filter.ref = ws.dimensions
        return ws

    # ---- Read Me ---------------------------------------------------------------------
    ws = wb.create_sheet('Read Me')
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 60
    ws.column_dimensions['C'].width = 55
    ws.column_dimensions['D'].width = 18
    r = 1
    ws.cell(row=r, column=1, value=acct.get('title', 'Meta Ads Audit')).font = Font(bold=True, size=16, color=NAVY)
    r += 2
    for k, v in acct.get('facts', []):
        ws.cell(row=r, column=1, value=k).font = Font(bold=True)
        c = ws.cell(row=r, column=2, value=v)
        c.alignment = wrap_top
        if k.lower().startswith('partial'):
            c.fill = fill(GREEN if v.lower().startswith('no') else RED)
        r += 1
    r += 1

    ws.cell(row=r, column=1, value='Start here — what the audit found').font = Font(bold=True, size=13, color=NAVY)
    r += 1
    for line in sections.get('Executive Summary', []):
        t = strip_md(line)
        if not t or t == '---':
            continue
        if t.startswith('- '):
            t = '• ' + t[2:]
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        c = ws.cell(row=r, column=1, value=t)
        c.alignment = wrap_top
        ws.row_dimensions[r].height = 15 * est_lines(t, 175) + 4
        r += 1
    r += 1

    ws.cell(row=r, column=1, value='Prioritised actions (detail in Findings, section 9)').font = Font(bold=True, size=13, color=NAVY)
    r += 1
    header_row(ws, r, ['Priority', 'Action', 'Worth', 'Where to look'])
    r += 1
    for head, body in sections.items():
        m = re.match(r'^\[(.+?)\]\s*(.*)', head)
        if not m:
            continue
        worth = next((strip_md(l)[len('- Worth:'):].strip() if strip_md(l).startswith('- Worth:') else
                      strip_md(l).split('Worth:', 1)[1].strip()
                      for l in body if 'Worth:' in l), '')
        worth = worth[:1].upper() + worth[1:]
        vals = [m.group(1), m.group(2), worth,
                'Live Ad Sets tab' if 'Nigeria' in head or 'winners' in head or 'Awareness' in head
                else 'Findings §9']
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.alignment = wrap_top
            c.border = box
            if j == 0:
                c.fill = fill(RED if 'High' in v else AMBER if 'Medium' in v else LIGHT)
        ws.row_dimensions[r].height = 15 * max(est_lines(vals[1], 60), est_lines(vals[2], 55)) + 4
        r += 1
    note = 'Nothing in the ad account has been changed. Every action above is a recommendation to test.'
    ws.cell(row=r, column=1, value=note).font = Font(italic=True, color='7F7F7F')
    r += 2

    ws.cell(row=r, column=1, value='How to use this workbook').font = Font(bold=True, size=13, color=NAVY)
    r += 1
    guide = [
        ('Read Me', 'This page: the answer, the actions and the data quality.'),
        ('Data', 'Fact table: one row per ad per day. Everything pivots from here. Values only, no formulas.'),
        ('Lookup', 'One row per ad with its attributes and totals. VLOOKUP or join on Ad ID.'),
        ('Monthly / Weekly', 'Pre-built rollups by Funnel Stage, Audience, Ad Format and Market (weeks start Monday).'),
        ('Zingers', 'Waste found by fixed thresholds. Summary first, then every instance with its spend.'),
        ('Tracking', 'Can the account measure itself? Read before trusting any ROAS figure.'),
        ('Findings', 'The full narrative: live ads first (Part A), then other ads and the 12-month view (Part B).'),
        ('Live Ad Sets', 'Action list: one row per live ad set with a verdict, the reason and the figures.'),
    ]
    for k, v in guide:
        ws.cell(row=r, column=1, value=k).font = Font(bold=True)
        ws.cell(row=r, column=2, value=v).alignment = wrap_top
        r += 1
    r += 1
    ws.cell(row=r, column=1, value='Categories and definitions').font = Font(bold=True, size=13, color=NAVY)
    r += 1
    for k, v in acct.get('definitions', []):
        ws.cell(row=r, column=1, value=k).font = Font(bold=True)
        c = ws.cell(row=r, column=2, value=v)
        c.alignment = wrap_top
        ws.row_dimensions[r].height = 15 * est_lines(v, 70) + 4
        r += 1
    r += 1
    ws.cell(row=r, column=1, value='Data quality').font = Font(bold=True, size=13, color=NAVY)
    r += 1
    dqp = os.path.join(outdir, 'dq_report.txt')
    if os.path.exists(dqp):
        for line in open(dqp, encoding='utf-8'):
            line = line.rstrip()
            if not line or line.startswith('=') or line.startswith('Meta Ads Audit') or \
                    line.startswith('Currency: confirm') or line.startswith('Category columns'):
                continue
            k, _, v = line.partition(':')
            ws.cell(row=r, column=1, value=k.strip()).font = Font(bold=True)
            ws.cell(row=r, column=2, value=v.strip()).alignment = wrap_top
            r += 1
    for k, v in acct.get('dq_extra', []):
        ws.cell(row=r, column=1, value=k).font = Font(bold=True)
        c = ws.cell(row=r, column=2, value=v)
        c.alignment = wrap_top
        ws.row_dimensions[r].height = 15 * est_lines(v, 70) + 4
        r += 1

    # ---- data tabs, in order ---------------------------------------------------------
    data_tab('Data', os.path.join(outdir, 'fact.csv'), freeze_cols=1)
    data_tab('Lookup', os.path.join(outdir, 'lookup.csv'), freeze_cols=2)
    data_tab('Monthly', os.path.join(outdir, 'monthly.csv'))
    data_tab('Weekly', os.path.join(outdir, 'weekly.csv'))

    # ---- Zingers -----------------------------------------------------------------------
    ws = wb.create_sheet('Zingers')
    zrows = []
    for p in (opts.get('--zingers') or '').split(','):
        if p and os.path.exists(p):
            zrows += list(csv.DictReader(open(p, encoding='utf-8')))
    widths = {'A': 22, 'B': 8, 'C': 10, 'D': 30, 'E': 9, 'F': 18, 'G': 50, 'H': 60}
    for k, v in widths.items():
        ws.column_dimensions[k].width = v
    ws.cell(row=1, column=1, value='Zingers — summary').font = Font(bold=True, size=13, color=NAVY)
    ws.cell(row=2, column=1, value='Fixed thresholds from Part 5; none were changed. Account averages: '
            + acct.get('averages', '')).font = Font(italic=True, color='7F7F7F')
    header_row(ws, 3, ['Scope', 'Zinger', 'Severity', 'Finding', 'Fired', 'Spend involved', 'What it means',
                       'What to do'])
    r = 4
    scopes = []
    for z in zrows:
        if z['Scope'] not in scopes:
            scopes.append(z['Scope'])
    for sc in scopes:
        group = [z for z in zrows if z['Scope'] == sc]
        ids = sorted({z['Zinger'] for z in group},
                     key=lambda zid: (SEV_ORDER.index(group[[g['Zinger'] for g in group].index(zid)]['Severity']),
                                      int(zid[1:])))
        for zid in ids:
            zs = [z for z in group if z['Zinger'] == zid]
            title, meaning, todo = ZINGER_TEXT[zid]
            vals = [sc, zid, zs[0]['Severity'], title, len(zs), sum(float(z['Spend involved']) for z in zs),
                    meaning, todo]
            for j, v in enumerate(vals):
                c = ws.cell(row=r, column=j + 1, value=v)
                c.alignment = wrap_top
                c.border = box
            ws.cell(row=r, column=6).number_format = MONEY0
            sev = zs[0]['Severity']
            ws.cell(row=r, column=3).fill = fill(RED if sev == 'Highest' else AMBER if sev == 'High'
                                                 else LIGHT if sev == 'Medium' else PALE)
            ws.row_dimensions[r].height = 15 * max(est_lines(meaning, 48), est_lines(todo, 58)) + 4
            r += 1
        fired = {z['Zinger'] for z in group}
        nf = [k for k in ZINGER_TEXT if k not in fired]
        c = ws.cell(row=r, column=1, value=f"{sc} — did not fire: {', '.join(nf) or 'none'}")
        c.font = Font(italic=True, color='7F7F7F')
        r += 2
    r += 1
    ws.cell(row=r, column=1, value='Zingers — every fired instance (filter by Scope or Zinger)').font = Font(bold=True, size=13, color=NAVY)
    r += 1
    det_hdr = ['Scope', 'Zinger', 'Severity', 'Finding', 'Basis', 'Spend involved', 'Entity', 'Detail']
    header_row(ws, r, det_hdr)
    top = r
    r += 1
    for z in zrows:
        vals = [z['Scope'], z['Zinger'], z['Severity'], z['Finding'], z.get('Basis', ''),
                float(z['Spend involved']), z['Entity'], z['Detail']]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.alignment = wrap_top
        ws.cell(row=r, column=6).number_format = MONEY
        ws.row_dimensions[r].height = 15 * max(est_lines(z['Entity'], 48), est_lines(z['Detail'], 58)) + 2
        r += 1
    ws.auto_filter.ref = f"A{top}:H{r - 1}"
    ws.freeze_panes = 'A4'

    # ---- Tracking ------------------------------------------------------------------------
    ws = wb.create_sheet('Tracking')
    trk = next((v for k, v in sections.items() if k.startswith('8.')), [])
    t = md_table(trk)
    ws.column_dimensions['A'].width = 32
    ws.column_dimensions['B'].width = 60
    ws.column_dimensions['C'].width = 60
    if t:
        header_row(ws, 1, t[0])
        for i2, row in enumerate(t[1:], start=2):
            for j, v in enumerate(row):
                c = ws.cell(row=i2, column=j + 1, value=v)
                c.alignment = wrap_top
                c.border = box
            st = row[1].lower()
            ws.cell(row=i2, column=2).fill = fill(
                PALE if st.startswith('data not available') else
                RED if any(w in st for w in ('107', 'not parseable', 'higher than', 'overstated', 'fallen')) else
                GREEN if st.startswith('yes') or st.startswith('passed') or st.startswith('purchase') else AMBER)
            ws.row_dimensions[i2].height = 15 * max(est_lines(row[1], 58), est_lines(row[2], 58)) + 4
        r = len(t) + 2
        ws.cell(row=r, column=1, value='Effect on this audit').font = Font(bold=True, size=12, color=NAVY)
        r += 1
        effect = [strip_md(l) for l in trk[trk.index(next(l for l in trk if l.startswith('**Effect'))) + 1:]
                  if strip_md(l) and strip_md(l) != '---'] if any(l.startswith('**Effect') for l in trk) else []
        for e in effect:
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
            c = ws.cell(row=r, column=1, value=e)
            c.alignment = wrap_top
            ws.row_dimensions[r].height = 15 * est_lines(e, 150) + 4
            r += 1
        ws.freeze_panes = 'A2'

    # ---- Findings --------------------------------------------------------------------------
    ws = wb.create_sheet('Findings')
    ncol = 8
    colw = [34, 20, 16, 16, 16, 16, 16, 16]
    for j, w in enumerate(colw):
        ws.column_dimensions[get_column_letter(j + 1)].width = w
    total_w = sum(colw)
    r = 1
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
            header_row(ws, r, t[0])
            r += 1
            for row in t[1:]:
                bold = row[0].lower().startswith('total')
                h = 1
                for j, v in enumerate(row):
                    c = ws.cell(row=r, column=j + 1, value=v)
                    c.alignment = wrap_top
                    c.border = box
                    if bold:
                        c.font = Font(bold=True)
                    h = max(h, est_lines(v, int((colw[j] if j < ncol else 16) * 1.1)))
                ws.row_dimensions[r].height = 15 * h + 3
                r += 1
            r += 1
            continue
        k += 1
        s = line.rstrip()
        if not s.strip():
            continue
        if s.strip() == '---':
            r += 1
            continue
        m = re.match(r'^(#{1,3}) (.*)', s)
        if m:
            level = len(m.group(1))
            size = {1: 15, 2: 13, 3: 11}[level]
            if level == 1 and r > 1:
                r += 1
            c = ws.cell(row=r, column=1, value=strip_md(m.group(2)))
            c.font = Font(bold=True, size=size, color=NAVY if level < 3 else '000000')
            if level == 1:
                for j in range(1, ncol + 1):
                    ws.cell(row=r, column=j).fill = fill(LIGHT)
            ws.row_dimensions[r].height = size + 10
            r += 1
            continue
        indent = len(s) - len(s.lstrip(' '))
        text = strip_md(s)
        if text.startswith('- '):
            text = ('    ' * (indent // 2)) + ('• ' if indent == 0 else '– ') + text[2:]
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
        c = ws.cell(row=r, column=1, value=text)
        c.alignment = wrap_top
        if s.lstrip().startswith('**') and s.rstrip().endswith('**'):
            c.font = Font(bold=True)
        ws.row_dimensions[r].height = 15 * est_lines(text, int(total_w * 1.05)) + 3
        r += 1
    ws.sheet_view.showGridLines = False

    # ---- Live Ad Sets ------------------------------------------------------------------------
    if '--live' in opts and os.path.exists(opts['--live']):
        ws = data_tab('Live Ad Sets', opts['--live'], freeze_cols=2)
        ws.column_dimensions['A'].width = 44
        ws.column_dimensions['B'].width = 40
        for row in ws.iter_rows(min_row=2):
            v = str(row[0].value or '')
            row[0].fill = fill(RED if v.startswith('Check') else GREEN if v.startswith('Scale') else
                               LIGHT if v.startswith('Keep') else AMBER if v.startswith('Watch') else PALE)
            row[0].alignment = wrap_top
            row[1].alignment = wrap_top

    wb._sheets = [wb[n] for n in TAB_ORDER if n in wb.sheetnames]
    wb.active = 0
    wb.save(out_path)

    print("=== Tabs assembled ===")
    for n in wb.sheetnames:
        print(f"  {n:<13} {wb[n].max_row} rows x {wb[n].max_column} cols")
    print(f"\nWrote {out_path}")
    print("Import to Google Sheets: Drive > New > File upload, then Open with Google Sheets "
          "(or File > Import in an existing sheet). All tabs and formats carry over.")


if __name__ == '__main__':
    main()
