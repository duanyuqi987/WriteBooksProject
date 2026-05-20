# -*- coding: utf-8 -*-
"""同步清音寺居 HTML → Markdown (简化版)"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
md_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.md'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 提取body
body_m = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
body = body_m.group(1) if body_m else html

# 分割章节: 在<h2 id="chN">处分割
h2_pat = re.compile(r'<h2 id="(ch\d+)">([^<]+)</h2>')
h3_pat = re.compile(r'<h3 id="vol-(\d+)">([^<]+)</h3>')

# 找到所有h2位置
h2_matches = list(h2_pat.finditer(body))
print(f'Found {len(h2_matches)} h2 tags')

# 找到所有h3位置
h3_matches = list(h3_pat.finditer(body))
print(f'Found {len(h3_matches)} h3 tags')

# 构建所有标记点的有序列表
all_marks = []
for m in h3_matches:
    all_marks.append((m.start(), 'h3', m.group(1), m.group(2)))
for m in h2_matches:
    all_marks.append((m.start(), 'h2', m.group(1), m.group(2)))
all_marks.sort(key=lambda x: x[0])

# 处理
toc_lines = ['# 清音寺居\n']
md_lines = []
chapters = []
chapter_num = 0

for i, (start, typ, id_str, title) in enumerate(all_marks):
    # 获取这个section的内容
    end = all_marks[i+1][0] if i+1 < len(all_marks) else len(body)
    section_html = body[start:end]

    if typ == 'h3':
        md_lines.append(f'\n## 卷{id_str}：{title}\n')
    elif typ == 'h2':
        chapter_num += 1
        # 提取段落
        ps = re.findall(r'<p[^>]*>(.*?)</p>', section_html, re.DOTALL)
        clean_ps = []
        for p_text in ps:
            clean = re.sub(r'<[^>]+>', '', p_text).strip()
            if clean:
                clean_ps.append(clean)

        cjk = len(re.findall(r'[一-鿿]', section_html))

        chapters.append((id_str, title, cjk, len(clean_ps)))
        toc_lines.append(f'- [{title}](#{id_str}) — {cjk}字')

        md_lines.append(f'\n### {title}\n')
        for p_text in clean_ps:
            md_lines.append(f'\n{p_text}\n')

# 写入MD
toc_text = '\n'.join(toc_lines)
md_text = toc_text + '\n\n' + '\n'.join(md_lines)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_text)

print(f'Written: {md_path}')
print(f'Chapters: {len(chapters)}')

# 统计
sorted_by_size = sorted(chapters, key=lambda x: x[2])
print('\n最短5章:')
for ch_id, title, cjk, pc in sorted_by_size[:5]:
    print(f'  {ch_id} {title}: {cjk}CJK, {pc}段')
print('\n最长5章:')
for ch_id, title, cjk, pc in sorted_by_size[-5:]:
    print(f'  {ch_id} {title}: {cjk}CJK, {pc}段')

weak = [(ch_id, title, cjk) for ch_id, title, cjk, _ in chapters if cjk < 550]
print(f'\n<550 CJK章节: {len(weak)}')
for ch_id, title, cjk in weak:
    print(f'  {ch_id} {title}: {cjk}CJK')
