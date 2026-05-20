# -*- coding: utf-8 -*-
"""Extract dash context around each —— in high-density chapters for creating v3"""
import re

B2 = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2, 'r', encoding='utf-8') as f:
    html = f.read()

targets = [24, 25, 23, 13]

out_path = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_dash_context.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_num in targets:
        ch_id = 'ch%d' % ch_num
        pos = html.find('<h2 id="%s">' % ch_id)
        if pos < 0:
            continue
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0:
            np = html.find('<footer', pos)
        if np < 0:
            np = len(html)
        ch_html = html[pos:np]
        # Remove HTML tags to get clean text
        clean = re.sub(r'<[^>]+>', '', ch_html)
        cjk = len(re.findall(r'[一-鿿]', clean))
        dashes = clean.count('——')

        out.write('\n' + '=' * 70 + '\n')
        out.write('%s [%dCJK] %d dashes density=%.1f\n' % (ch_id, cjk, dashes, dashes/cjk*100 if cjk>0 else 0))
        out.write('=' * 70 + '\n')

        # Show context around each ——
        # Use a simple approach: split by paragraphs, show each paragraph with dashes
        # But better: show content around each ——

        # Find all positions of ——
        dash_positions = [m.start() for m in re.finditer('——', clean)]

        for i, dp in enumerate(dash_positions):
            start = max(0, dp - 30)
            end = min(len(clean), dp + 30)
            ctx = clean[start:end]
            ctx = ctx.replace('\n', ' ')
            out.write('[#%d] ...%s...\n' % (i+1, ctx))

print('Done: ' + out_path)
