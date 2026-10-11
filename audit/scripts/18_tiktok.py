"""TikTok organic (account BEGUILE, Windsor tiktok_organic), video-level, pulled 2026-10-11. Videos by month; totals; top videos; what the best ones have in common (duration, founder/creator captions)."""
from common import *
import collections, re
V=load('tiktok_organic_videos.json')
def n(x): return x or 0
M=collections.defaultdict(lambda: collections.defaultdict(float))
for v in V:
    m=v['video_create_datetime'][:7]; a=M[m]; a['videos']+=1
    for k in ['video_views_count','video_reach','video_likes','video_shares','video_comments','video_new_followers','video_profile_views','video_website_clicks']: a[k]+=n(v.get(k))
print('month | videos | views | reach | likes | shares | new followers | profile views | site clicks')
for m in sorted(M):
    a=M[m]; print(f"{m} {a['videos']:3.0f} {a['video_views_count']:8.0f} {a['video_reach']:8.0f} {a['video_likes']:6.0f} {a['video_shares']:5.0f} {a['video_new_followers']:5.0f} {a['video_profile_views']:6.0f} {a['video_website_clicks']:4.0f}")
tot={k:sum(n(v.get(k)) for v in V) for k in ['video_views_count','video_reach','video_likes','video_shares','video_new_followers','video_profile_views','video_website_clicks']}
print('TOTAL', len(V), 'videos', tot)
views=sorted([n(v['video_views_count']) for v in V]); print('median views', views[len(views)//2], '| videos over 10k views:', sum(1 for x in views if x>10000), '| share of all views from top 5:', round(100*sum(views[-5:])/sum(views),1))
print('\nTop 10 by views: views | reach | full-watch% | avg sec | new followers | site clicks | date | caption')
for v in sorted(V, key=lambda v:-n(v['video_views_count']))[:10]:
    print(f"{n(v['video_views_count']):7.0f} {n(v['video_reach']):7.0f} {100*n(v['video_full_watched_rate']):5.1f}% {n(v['video_average_time_watched']):4.1f}s {n(v['video_new_followers']):4.0f} {n(v['video_website_clicks']):3.0f} {v['video_create_datetime'][:10]} {(v['video_caption'] or '')[:90]!r}")
# founder / creator / review / notes-essay signal in captions
def tag(c):
    c=(c or '').lower()
    if re.search(r'founder|ihuoma|ceo|queenet', c): return 'founder'
    if re.search(r'review|honest|tried|customer', c): return 'review'
    if re.search(r'notes|top notes|opens with|bergamot|vanilla|oud', c): return 'notes-led caption'
    return 'other'
T=collections.defaultdict(lambda:[0,0,0])
for v in V: t=tag(v['video_caption']); T[t][0]+=1; T[t][1]+=n(v['video_views_count']); T[t][2]+=n(v['video_new_followers'])
print('\ncaption type | videos | views/video | new followers/video'); [print(f"{k:18} {a[0]:3d} {a[1]/a[0]:8.0f} {a[2]/a[0]:5.1f}") for k,a in T.items()]
dur=[(n(v['video_duration']),n(v['video_views_count'])) for v in V if n(v['video_duration'])>0]
for lo,hi in [(0,15),(15,30),(30,60),(60,999)]:
    s=[x for d,x in dur if lo<=d<hi]; print(f'duration {lo}-{hi}s: {len(s)} videos, {sum(s)/len(s) if s else 0:.0f} views each')
dump('tiktok.json', {'month':{k:dict(v) for k,v in M.items()}, 'total':tot})
