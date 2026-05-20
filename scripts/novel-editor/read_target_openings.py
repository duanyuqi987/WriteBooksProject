# -*- coding: utf-8 -*-
"""读取目标章节的真实开头和关键段落，用于撰写精准锚点"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 需要查看的章节 (ch_name -> title)
targets = [
    # 组D
    'ch2', 'ch142', 'ch149', 'ch91', 'ch150', 'ch145', 'ch152',
    # 组E 季节
    'ch80', 'ch90', 'ch110', 'ch130',
    # 组A samples
    'ch34', 'ch39', 'ch40', 'ch52', 'ch53', 'ch61', 'ch71', 'ch108',
    'ch58', 'ch64', 'ch70', 'ch43', 'ch103',
    # 组B
    'ch1', 'ch25', 'ch57', 'ch67', 'ch74', 'ch75', 'ch119',
    'ch49', 'ch77', 'ch107',
    # 组C
    'ch42', 'ch50', 'ch51', 'ch76', 'ch147',
]

h2_re = re.compile(r'<h2 id="(ch\d+)">([^<]+)</h2>')

out_path = 'd:/ProgramWork/WriteBookProject/tmp_b2_openings.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_id in targets:
        pos = html.find('<h2 id="%s">' % ch_id)
        if pos < 0:
            out.write('\n=== %s NOT FOUND ===\n\n' % ch_id)
            continue

        # 找章节标题
        title_m = h2_re.search(html, pos)
        title = title_m.group(2) if title_m else '?'

        h2_end = html.find('</h2>', pos) + len('</h2>')
        next_ch = html.find('<h2 id="ch', h2_end)
        if next_ch < 0:
            next_ch = html.find('<footer', h2_end)
        if next_ch < 0:
            next_ch = len(html)

        ch_html = html[h2_end:next_ch]

        # 提取所有<p>文本
        ps = re.findall(r'<p[^>]*>(.*?)</p>', ch_html, re.DOTALL)
        clean_ps = []
        for p in ps:
            clean = re.sub(r'<[^>]+>', '', p).strip()
            if clean:
                clean_ps.append(clean)

        cjk = len(re.findall(r'[一-鿿]', ch_html))

        out.write('\n' + '=' * 60 + '\n')
        out.write('%s %s [%dCJK] %d段落\n' % (ch_id, title, cjk, len(clean_ps)))
        out.write('=' * 60 + '\n')

        # 写前3段
        for i, p in enumerate(clean_ps[:5]):
            out.write('[P%d] %s\n\n' % (i+1, p[:200]))

print('Done: ' + out_path)
print('Processed %d chapters' % len(targets))
