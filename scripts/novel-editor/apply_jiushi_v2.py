# -*- coding: utf-8 -*-
"""Apply v2 dash replacements from JSON file"""
import json

B2 = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2, 'r', encoding='utf-8') as f:
    html = f.read()

with open('d:/ProgramWork/WriteBookProject/scripts/jiushi_v2_pairs.json', 'r', encoding='utf-8') as f:
    all_pairs = json.load(f)

def repl_in_ch(html, ch_id, pairs):
    """在指定章节内执行(old, new)替换对"""
    pos = html.find('<h2 id="%s">' % ch_id)
    if pos < 0:
        print('  ERR: cannot find %s' % ch_id)
        return html, 0
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0:
        np = html.find('<footer', pos)
    if np < 0:
        np = len(html)
    ch = html[pos:np]
    hit = 0
    for old, new in pairs:
        if old in ch:
            ch = ch.replace(old, new)
            hit += 1
        else:
            print('  MISS: %s...' % old[:40])
    html = html[:pos] + ch + html[np:]
    return html, hit

total = 0
for ch_id, pairs in all_pairs.items():
    print('Processing %s (%d pairs)...' % (ch_id, len(pairs)))
    html, hits = repl_in_ch(html, ch_id, pairs)
    print('  Hits: %d/%d' % (hits, len(pairs)))
    total += hits

with open(B2, 'w', encoding='utf-8') as f:
    f.write(html)

print('\nTotal applied: %d' % total)
print('Done: ' + B2)
