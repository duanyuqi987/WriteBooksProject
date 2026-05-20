"""检查所有章开头是否已有桥接语句"""
import re

with open('docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html', 'r', encoding='utf-8') as f:
    html = f.read()

chapters = re.findall(r'<h2 id="ch(\d+)">([^<]+)</h2>', html)
bridge_kw = ['之后', '完了', '过后', '第二天', '次日', '接着', '继续', '接下来', '下来', '从那', '从此', '回来', '归来', '上次', '上一', '那天', '当晚', '前', '这']

results = []
for ch_id, title in chapters:
    ch_num = int(ch_id)
    pos = html.find(f'<h2 id="ch{ch_num}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+5000]
    clean = re.sub(r'<[^>]+>', '', c)
    lines = clean.strip().split('\n')
    first_text = ''
    for l in lines:
        l = l.strip()
        if l and l != title and len(l) > 10:
            first_text = l[:150]
            break
    has_bridge = any(kw in first_text for kw in bridge_kw)
    results.append((ch_num, has_bridge, title, first_text))

no_bridge = [r for r in results if not r[1]]
has_bridge = [r for r in results if r[1]]

out_path = 'd:/ProgramWork/WriteBookProject/tmp_bridge_check.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'有桥接: {len(has_bridge)}章\n')
    f.write(f'无桥接: {len(no_bridge)}章\n\n')
    f.write('=== 无桥接章节 ===\n')
    for ch_num, _, title, first_text in no_bridge:
        f.write(f'ch{ch_num:03d} {title}: {first_text[:120]}\n')
    f.write('\n=== 有桥接章节 ===\n')
    for ch_num, _, title, first_text in has_bridge:
        f.write(f'ch{ch_num:03d} {title}: {first_text[:120]}\n')

print(f'Done: {out_path}')
print(f'Bridge: {len(has_bridge)}, No bridge: {len(no_bridge)}')
