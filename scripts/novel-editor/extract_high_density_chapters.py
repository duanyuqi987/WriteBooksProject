# -*- coding: utf-8 -*-
"""提取密度>5的章节全文，用于创建v3替换"""
import re

B2 = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2, 'r', encoding='utf-8') as f:
    html = f.read()

# ch024 (8.7), ch025 (7.9), ch023 (6.2), ch013 (5.6)
targets = [24, 25, 23, 13]

out_path = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_high_density.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_num in targets:
        ch_id = 'ch%d' % ch_num
        pos = html.find('<h2 id="%s">' % ch_id)
        if pos < 0:
            continue
        next_pos = html.find('<h2 id="ch', pos + 20)
        if next_pos < 0:
            next_pos = html.find('<footer', pos)
        if next_pos < 0:
            next_pos = len(html)
        content = html[pos:next_pos]
        clean = re.sub(r'<[^>]+>', '', content)
        cjk = len(re.findall(r'[一-鿿]', clean))
        dashes = clean.count('——')
        density = dashes / cjk * 100 if cjk > 0 else 0

        out.write('\n' + '=' * 70 + '\n')
        out.write('%s [%dCJK] %d dashes density=%.1f/100字\n' % (ch_id, cjk, dashes, density))
        out.write('=' * 70 + '\n')
        out.write(clean)
        out.write('\n\n')

print('Done: ' + out_path)
