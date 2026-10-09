"""Classify Meta campaigns from their names. Rules are keyword-based and listed here so they can be audited."""
import re
def creative(n):
    s = n.lower()
    if 'iswis' in s: return 'Podcast (ISWIS)'
    if re.search(r'amy okoli|dimma|woomie|scentsationelle|shades of mae|^shades |ph and co|influencer', s): return 'Named creators'
    if 'ceo' in s: return 'CEO'
    if 'ugc' in s: return 'UGC'
    if 'street interview' in s or 'interviews' in s: return 'Street Interview'
    if 'carousel' in s: return 'Carousel'
    if re.search(r'\bdt\b|-dt\b|dt-|dynamic|/dt', s): return 'DT/Dynamic'
    if re.search(r'catalogue|\bcat\b', s): return 'Catalogue'
    if re.search(r'image|flier', s): return 'Image'
    if re.search(r'\bvid\b|video|reels|ig content', s): return 'Video (unspecified)'
    return 'Not stated in name'
PRODUCTS = [('Mystique', r'myst|mytique|msytique|\bmys\b|mys-|mys\+'), ('Goddess', r'godd?d?ess|goddes'),
            ('Golden Kiss', r'golden kiss'), ('Sweet Oud', r'oud|\bso\b'), ('Blush Bloom', r'blush|\bbb\b|bloom'),
            ('Mini Set', r'mini set'), ('Passion', r'passion'), ('Seduction', r'seduction'), ('Oils', r'\boils?\b'),
            ('Vanilla Sugar', r'vanilla'), ('White Florals', r'white-florals|white florals')]
def product(n):
    s = n.lower()
    if re.search(r'\bmgg\b|g&m', s): return 'Multiple products'
    hits = [p for p, rx in PRODUCTS if re.search(rx, s)]
    if len(hits) == 1: return hits[0]
    if len(hits) > 1: return 'Multiple products'
    return 'Range / not stated'
def heritage(n):
    """Campaign name states a Nigerian/African-heritage audience."""
    return bool(re.search(r'nigerians|/nig\b|\bnig\b|africans', n.lower()))
