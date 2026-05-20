# -*- coding: utf-8 -*-
"""从HTML生成附录卷MD文件"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-ci-fulujuan-appendix-2026-05-15.html'
md_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-ci-fulujuan-appendix-2026-05-15.md'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

title_m = re.search(r'<title>(.*?)</title>', html)
book_title = title_m.group(1) if title_m else '银杏辞附录卷'

chapters = []
h2_re = re.compile(r'<h2 id="(ch\d+)">([^<]+)</h2>')
pos = 0
while True:
    m = h2_re.search(html, pos)
    if not m:
        break
    ch_id = m.group(1)
    ch_title = m.group(2)
    ch_start = m.end()

    next_h2_re = re.compile(r'<h2 id="ch\d+">')
    next_m = next_h2_re.search(html, ch_start)
    footer_m = re.compile(r'<footer').search(html, ch_start)
    end_offset = len(html) - ch_start
    if next_m:
        end_offset = next_m.start() - ch_start
    if footer_m:
        footer_rel = footer_m.start() - ch_start
        if footer_rel < end_offset:
            end_offset = footer_rel

    ch_html = html[ch_start:ch_start + end_offset]
    md_lines = []
    ch_html = ch_html.strip()

    blocks = re.findall(r'(<(?:p|blockquote|div)[^>]*>.*?</(?:p|blockquote|div)>)', ch_html, re.DOTALL)
    if not blocks:
        blocks = [ch_html]

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if block.startswith('<blockquote'):
            inner = re.sub(r'</?blockquote[^>]*>', '', block).strip()
            inner = re.sub(r'<br\s*/?>', '\n> ', inner)
            inner = re.sub(r'<p[^>]*>', '', inner)
            inner = re.sub(r'</p>', '', inner)
            for line in inner.split('\n'):
                line = line.strip()
                if line:
                    md_lines.append('> ' + line)
        elif block.startswith('<div'):
            inner = re.sub(r'</?div[^>]*>', '', block).strip()
            if inner:
                md_lines.append('*' + inner + '*')
        elif block.startswith('<p'):
            inner = re.sub(r'<p[^>]*>', '', block, count=1)
            inner = re.sub(r'</p>$', '', inner)
            inner = re.sub(r'<br\s*/?>', '\n', inner)
            inner = re.sub(r'<em>', '*', inner)
            inner = re.sub(r'</em>', '*', inner)
            inner = re.sub(r'<strong>', '**', inner)
            inner = re.sub(r'</strong>', '**', inner)
            inner = re.sub(r'<[^>]+>', '', inner)
            inner = inner.strip()
            if inner == '（完）':
                inner = '*（完）*'
            if inner:
                md_lines.append(inner)

    chapters.append((ch_id, ch_title, md_lines))
    pos = ch_start + end_offset

md_content = []
md_content.append('# ' + book_title)
md_content.append('')
md_content.append('**银杏辞系列附录卷 · 资料编**')
md_content.append('')
md_content.append('---')
md_content.append('')

for ch_id, ch_title, md_lines in chapters:
    md_content.append('## ' + ch_title)
    md_content.append('')
    for line in md_lines:
        md_content.append(line)
        md_content.append('')
    md_content.append('')

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_content))

print('MD written: %s' % md_path)
print('Chapters: %d' % len(chapters))
