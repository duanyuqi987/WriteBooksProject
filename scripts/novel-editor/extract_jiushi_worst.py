"""提取高密度章节全文用于分析"""
import re

B2_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 提取最需要优化的章: ch29, ch3, ch27, ch14, ch30, ch24, ch21
targets = [29, 3, 27, 14, 30, 24, 21]

out_path = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_worst_chapters.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    for ch_num in targets:
        pos = html.find(f'<h2 id="ch{ch_num}">')
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

        out.write(f'{"="*60}\n')
        out.write(f'ch{ch_num:03d} [{cjk}CJK] {dashes}个破折号 密度={density:.1f}/100字\n')
        out.write(f'{"="*60}\n')
        out.write(clean)
        out.write('\n\n')

print(f'Done: {out_path}')
