# -*- coding: utf-8 -*-
"""为需要桥接的章节提取前章结尾和本章开头"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 需要桥接的章节（去掉ch1）
need_bridge = ['ch5', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11', 'ch12',
               'ch14', 'ch16', 'ch17', 'ch22', 'ch23', 'ch24', 'ch26',
               'ch27', 'ch29', 'ch31']

# 提取所有章节
h2_re = re.compile(r'<h2 id="(ch\d+)">([^<]+)</h2>')
all_chapters = []
pos = 0
while True:
    m = h2_re.search(html, pos)
    if not m:
        break
    ch_id = m.group(1)
    ch_title = m.group(2)
    ch_start = m.end()
    next_h2 = h2_re.search(html, ch_start)
    footer_m = re.compile(r'<footer').search(html, ch_start)
    end_pos = len(html)
    if next_h2:
        end_pos = next_h2.start()
    if footer_m and footer_m.start() < end_pos:
        end_pos = footer_m.start()
    ch_html = html[ch_start:end_pos]
    all_chapters.append((ch_id, ch_title, ch_html))
    pos = end_pos

# 建立章节号到索引的映射
ch_index = {ch[0]: i for i, ch in enumerate(all_chapters)}

out_path = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_bridge_prep.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_id in need_bridge:
        idx = ch_index.get(ch_id)
        if idx is None or idx == 0:
            continue

        # 前章
        prev_id, prev_title, prev_html = all_chapters[idx - 1]

        # 提取前章最后一段的纯文本
        prev_ps = re.findall(r'<p[^>]*>(.*?)</p>', prev_html, re.DOTALL)
        prev_last_para = ''
        for p_text in reversed(prev_ps):
            clean = re.sub(r'<[^>]+>', '', p_text).strip()
            if clean and clean != '（完）':
                prev_last_para = clean
                break

        # 本章开头
        cur_id, cur_title, cur_html = all_chapters[idx]

        # 提取本章第一段纯文本
        cur_ps = re.findall(r'<p[^>]*>(.*?)</p>', cur_html, re.DOTALL)
        cur_first_para = ''
        for p_text in cur_ps:
            clean = re.sub(r'<[^>]+>', '', p_text).strip()
            if clean and clean != '（完）':
                cur_first_para = clean
                break

        out.write('=' * 60 + '\n')
        out.write('过渡: %s(%s) → %s(%s)\n' % (prev_id, prev_title, cur_id, cur_title))
        out.write('=' * 60 + '\n')
        out.write('前章结尾: %s...\n\n' % prev_last_para[-150:])
        out.write('本章开头: %s...\n\n' % cur_first_para[:200])
        out.write('\n')

print('Done: ' + out_path)
print('Prepared %d transitions' % len(need_bridge))
