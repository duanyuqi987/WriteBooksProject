# -*- coding: utf-8 -*-
"""提取《清音寺居》叙事优化需要修改的关键章节文本"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 计划中涉及的所有章节
target_chapters = [
    # 组A
    ('ch34', '收蜜'), ('ch39', '晒药'), ('ch40', '捣药'), ('ch52', '画壁'),
    ('ch53', '制香'), ('ch61', '播种'), ('ch71', '寻泉'), ('ch91', '迎夏'),
    ('ch108', '煨芋'), ('ch149', '换衣'),
    ('ch58', '望山'), ('ch64', '午憩'), ('ch70', '封笔'),
    ('ch43', '夜读'), ('ch103', '寄远'),
    # 组B
    ('ch1', '磨墨'), ('ch25', '补经'), ('ch57', '独处'), ('ch67', '临帖'),
    ('ch74', '辞行'), ('ch75', '归途'), ('ch119', '忍寒'),
    ('ch49', '论道'), ('ch77', '叙旧'), ('ch107', '话旧'),
    ('ch80', '迎春'), ('ch145', '晚钟'),
    # 组C
    ('ch42', '煎药'), ('ch50', '送别'), ('ch51', '盼信'), ('ch76', '重逢'),
    ('ch147', '送春'),
    # 组D
    ('ch2', '裁纸'), ('ch142', '种瓜'), ('ch150', '闻蝉'), ('ch152', '无尽'),
    # 组E (不特定章节，在脚本中动态查找)
]

out_path = 'd:/ProgramWork/WriteBookProject/tmp_b2_target_chapters.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_num_str, ch_title_hint in target_chapters:
        # 在HTML中找这个章节
        ch_id = ch_num_str
        pos = html.find('<h2 id="%s">' % ch_id)
        if pos < 0:
            out.write('\n=== %s NOT FOUND ===\n\n' % ch_id)
            continue

        next_pos = html.find('<h2 id="ch', pos + 20)
        if next_pos < 0:
            next_pos = html.find('<footer', pos)
        if next_pos < 0:
            next_pos = len(html)

        ch_html = html[pos:next_pos]
        clean = re.sub(r'<[^>]+>', '', ch_html)
        cjk = len(re.findall(r'[一-鿿]', clean))

        out.write('\n' + '=' * 60 + '\n')
        out.write('%s %s [%dCJK]\n' % (ch_id, ch_title_hint, cjk))
        out.write('=' * 60 + '\n')
        out.write(clean[:800])  # first 800 chars
        out.write('\n...\n\n')

print('Done: ' + out_path)
print('Extracted %d chapters' % len(target_chapters))
