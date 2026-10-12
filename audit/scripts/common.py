import json, glob, os
D = os.path.join(os.path.dirname(__file__), '..', 'data')
OUT = os.path.join(os.path.dirname(__file__), '..', 'out')
def load(pattern):
    rows = []
    for f in sorted(glob.glob(os.path.join(D, pattern))):
        rows += json.load(open(f))['result']
    return rows
CMAP = {'Nigeria':'NG','United Kingdom':'UK','Canada':'CA','United States':'US'}
def cc(name): return CMAP.get(name, 'Other')
def window(date):
    """Return list of windows a YYYY-MM-DD date falls in."""
    y, m = int(date[:4]), int(date[5:7])
    w = []
    if y == 2026 and m <= 9: w.append('JanSep26')
    if y == 2025 and m <= 9: w.append('JanSep25')
    if y == 2026 and 4 <= m <= 6: w.append('AprJun26')
    if y == 2026 and 7 <= m <= 9: w.append('JulSep26')
    return w
WINS = ['JanSep26','JanSep25','AprJun26','JulSep26']
def ym(date): return date[:7]
def dump(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), 'w'), indent=1, default=str)
