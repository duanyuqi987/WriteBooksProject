# -*- coding: utf-8 -*-
"""Debug misses from v2 — find why 10 pairs didn't match"""
import json

B2 = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2, 'r', encoding='utf-8') as f:
    html = f.read()

with open('d:/ProgramWork/WriteBookProject/scripts/jiushi_v2_pairs.json', 'r', encoding='utf-8') as f:
    all_pairs = json.load(f)

def get_chapter_text(html, ch_id):
    pos = html.find('<h2 id="%s">' % ch_id)
    if pos < 0:
        return ''
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0:
        np = html.find('<footer', pos)
    if np < 0:
        np = len(html)
    return html[pos:np]

out_path = 'd:/ProgramWork/WriteBookProject/tmp_v2_misses.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_id, pairs in all_pairs.items():
        ch_text = get_chapter_text(html, ch_id)
        for i, (old, new) in enumerate(pairs):
            if old not in ch_text:
                out.write('=' * 60 + '\n')
                out.write('MISS: %s pair #%d\n' % (ch_id, i))
                out.write('OLD (first 100 chars): %s\n' % old[:100])
                out.write('---\n')
                # Try to find similar text in chapter
                # Search for a short unique substring from old
                # Find first 20 chars that don't contain quotes
                search = old[:60].replace("'", "").replace('"', '')
                if len(search) > 15:
                    # Find in chapter
                    idx = ch_text.find(search)
                    if idx >= 0:
                        out.write('Found similar at offset %d:\n' % idx)
                        out.write(repr(ch_text[max(0,idx-10):idx+len(search)+50]) + '\n')
                    else:
                        out.write('NOT FOUND in chapter\n')
                out.write('\n')

print('Done: ' + out_path)
