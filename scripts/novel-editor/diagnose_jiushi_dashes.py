"""
《银杏城旧事》破折号密度诊断
"""
import re

B2_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Find all chapters
chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html)
print(f'总章节数: {len(chapters)}')

total_cjk = 0
total_dashes = 0
chapter_stats = []

for ch_id, title in chapters:
    ch_num = int(ch_id[2:])
    pos = html.find(f'<h2 id="{ch_id}">')
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
    total_cjk += cjk
    total_dashes += dashes
    chapter_stats.append((ch_num, title, cjk, dashes, density))

avg_density = total_dashes / total_cjk * 100 if total_cjk > 0 else 0

out_path = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_dash_diag.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'《银杏城旧事》破折号诊断\n')
    f.write(f'=' * 60 + '\n\n')
    f.write(f'总章节数: {len(chapters)}\n')
    f.write(f'总CJK字数: {total_cjk}\n')
    f.write(f'总破折号数: {total_dashes}\n')
    f.write(f'平均每100 CJK字的破折号数: {avg_density:.1f}\n\n')

    # Sort by density desc
    sorted_chapters = sorted(chapter_stats, key=lambda x: x[4], reverse=True)

    f.write(f'破折号密度最高的20章 (最需要优化):\n')
    f.write('-' * 60 + '\n')
    for ch_num, title, cjk, dashes, density in sorted_chapters[:20]:
        f.write(f'ch{ch_num:03d} [{cjk:5d}CJK] {title}: {dashes}个破折号, 密度={density:.1f}/100字\n')

    f.write(f'\n破折号密度最低的10章 (最自然的):\n')
    f.write('-' * 60 + '\n')
    for ch_num, title, cjk, dashes, density in sorted_chapters[-10:]:
        f.write(f'ch{ch_num:03d} [{cjk:5d}CJK] {title}: {dashes}个破折号, 密度={density:.1f}/100字\n')

    f.write(f'\n\n密度分布:\n')
    f.write(f'  密度>12: {sum(1 for s in chapter_stats if s[4] > 12)}章\n')
    f.write(f'  密度>10: {sum(1 for s in chapter_stats if s[4] > 10)}章\n')
    f.write(f'  密度>8:  {sum(1 for s in chapter_stats if s[4] > 8)}章\n')
    f.write(f'  密度>6:  {sum(1 for s in chapter_stats if s[4] > 6)}章\n')
    f.write(f'  密度>4:  {sum(1 for s in chapter_stats if s[4] > 4)}章\n')
    f.write(f'  密度<3:  {sum(1 for s in chapter_stats if s[4] < 3)}章\n')
    f.write(f'  密度<2:  {sum(1 for s in chapter_stats if s[4] < 2)}章\n')

print(f'Done: {out_path}')
print(f'Total chapters: {len(chapters)}, Total dashes: {total_dashes}, Avg density: {avg_density:.1f}')
print(f'Density >12: {sum(1 for s in chapter_stats if s[4] > 12)}')
print(f'Density >10: {sum(1 for s in chapter_stats if s[4] > 10)}')
print(f'Density >8: {sum(1 for s in chapter_stats if s[4] > 8)}')
