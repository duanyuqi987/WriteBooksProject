"""
诊断《清音寺居》续修五后状态
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

print("=" * 60)
print("1. 基础结构")
print("=" * 60)
chapters = re.findall(r'<h2 id="ch(\d+)">([^<]+)</h2>', html)
ids = [int(x[0]) for x in chapters]
print(f"章数: {len(chapters)}")
print(f"ID范围: ch{ids[0]}-ch{ids[-1]}")
print(f"ID连续: {ids == list(range(ids[0], ids[-1]+1))}")

# Check for prefix残留
prefix_h2 = [t for _, t in chapters if t.startswith('扩展')]
print(f"'扩展'前缀残留: {len(prefix_h2)}")

# Check for TOC
toc_count = html.count('<nav class="toc-panel"')
print(f"TOC: {toc_count}个")

print("\n" + "=" * 60)
print("2. 每章CJK字数（找最弱章）")
print("=" * 60)

min_cjk = 99999
min_chs = []
weak_chs = []  # <600 CJK
for i, (ch_id, title) in enumerate(chapters):
    ch_num = int(ch_id)
    pos = html.find(f'<h2 id="ch{ch_num}">')
    next_pos = html.find('<h2 id="ch', pos + 20)
    if next_pos < 0:
        next_pos = html.find('<footer', pos)
    content = html[pos:next_pos] if next_pos > 0 else html[pos:pos+10000]
    cjk = len(re.findall(r'[一-鿿]', content))
    if cjk < min_cjk:
        min_cjk = cjk
        min_chs = [(ch_num, title, cjk)]
    elif cjk == min_cjk:
        min_chs.append((ch_num, title, cjk))
    if cjk < 600:
        weak_chs.append((ch_num, title, cjk))

print(f"最短章: {min_chs}")
print(f"<600 CJK的章 ({len(weak_chs)}章):")
for ch_num, title, cjk in sorted(weak_chs, key=lambda x: x[2]):
    print(f"  ch{ch_num} {title}: {cjk} CJK")

print("\n" + "=" * 60)
print("3. 人物出现分布（逐章）")
print("=" * 60)

ji_absent = []
shen_absent = []
sun_absent = []
ji_only = []
sun_only = []

for i, (ch_id, title) in enumerate(chapters):
    ch_num = int(ch_id)
    pos = html.find(f'<h2 id="ch{ch_num}">')
    next_pos = html.find('<h2 id="ch', pos + 20)
    if next_pos < 0:
        next_pos = html.find('<footer', pos)
    if next_pos < 0:
        next_pos = len(html)
    content = html[pos:next_pos]

    has_ji = '寂声' in content
    has_shen = '秋白' in content
    has_sun = '老孙' in content

    if not has_ji: ji_absent.append(ch_num)
    if not has_shen: shen_absent.append(ch_num)
    if not has_sun: sun_absent.append(ch_num)
    if has_ji and not has_shen and not has_sun:
        ji_only.append(ch_num)
    if has_sun and not has_ji and not has_shen:
        sun_only.append(ch_num)

print(f"寂声缺席({len(ji_absent)}章): {ji_absent}")
print(f"沈秋白缺席({len(shen_absent)}章): {shen_absent}")
print(f"老孙缺席({len(sun_absent)}章): {sun_absent}")
print(f"仅寂声({len(ji_only)}章): {ji_only}")
print(f"仅老孙({len(sun_only)}章): {sun_only}")

# Shen absence breakdown
print(f"\n沈秋白缺席章节分布:")
shen_absent_sorted = sorted(shen_absent)
# Group consecutive
groups = []
if shen_absent_sorted:
    group_start = shen_absent_sorted[0]
    group_end = shen_absent_sorted[0]
    for n in shen_absent_sorted[1:]:
        if n == group_end + 1:
            group_end = n
        else:
            groups.append((group_start, group_end))
            group_start = n
            group_end = n
    groups.append((group_start, group_end))
for s, e in groups:
    title_s = dict(chapters).get(f'ch{s}', '?')
    title_e = dict(chapters).get(f'ch{e}', '?')
    print(f"  ch{s}({title_s}) - ch{e}({title_e}): {e-s+1}章")

print("\n" + "=" * 60)
print("4. inner-monologue 分布")
print("=" * 60)
no_inner = []
for i, (ch_id, title) in enumerate(chapters):
    ch_num = int(ch_id)
    pos = html.find(f'<h2 id="ch{ch_num}">')
    next_pos = html.find('<h2 id="ch', pos + 20)
    if next_pos < 0:
        next_pos = html.find('<footer', pos)
    if next_pos < 0:
        next_pos = len(html)
    content = html[pos:next_pos]
    if 'inner-monologue' not in content:
        no_inner.append(ch_num)

print(f"无inner-monologue章: {len(no_inner)}章 → {no_inner}")

# Count inner-monologue instances
total_inner = html.count('inner-monologue')
print(f"inner-monologue总数: {total_inner}")

print("\n" + "=" * 60)
print("5. 检查续修五修改完整性")
print("=" * 60)

# Check ch149 body expansion
ch149_pos = html.find('<h2 id="ch149">')
ch150_pos = html.find('<h2 id="ch150">', ch149_pos)
ch149_content = html[ch149_pos:ch150_pos]
if '重新谈判距离' in ch149_content:
    print("ch149换衣 body expansion: ✓")
else:
    print("ch149换衣 body expansion: ✗ (可能未生效)")

# Check ch91 expansion
ch91_pos = html.find('<h2 id="ch91">')
ch92_pos = html.find('<h2 id="ch92">', ch91_pos)
ch91_content = html[ch91_pos:ch92_pos]
if '火舌舔着锅底' in ch91_content:
    print("ch91迎夏 sensory expansion: ✓")
else:
    print("ch91迎夏 sensory expansion: ✗ (可能未生效)")

# Check ch152 bridge
ch152_pos = html.find('<h2 id="ch152">')
footer_pos = html.find('<footer', ch152_pos)
ch152_content = html[ch152_pos:footer_pos]
if '瓜叶大得像一把一把的蒲扇' in ch152_content:
    print("ch152无尽 bridge paragraph: ✓")
else:
    print("ch152无尽 bridge paragraph: ✗ (可能未生效)")
if '找到属于你自己的' in ch152_content:
    print("ch152无尽 blessing line: ✓")
else:
    print("ch152无尽 blessing line: ✗")

# Check ch49 duplicate edit
ch49_count = html.count('在朝堂上站久了')
print(f"ch49 court reflection 出现次数: {ch49_count} (应为1)")

# Check ch76 reunion detail
if '穿着一件洗旧了的灰布衫' in html:
    print("ch76 reunion detail: ✓")
else:
    print("ch76 reunion detail: ✗")

print("\n" + "=" * 60)
print("6. 内容质量抽样检查")
print("=" * 60)

# Check for potential double-insertion or other artifacts
artifacts = [
    ('重复inner-monologue', r'<div class="inner-monologue">.*?<div class="inner-monologue">'),
    ('空inner-monologue', r'<div class="inner-monologue">\s*<p>\s*</p>\s*</div>'),
    ('连续多个（完）', r'（完）\s*（完）'),
    ('broken HTML tags', r'<(?!\w|/|!--)[^>]*>'),  # Only check for clearly broken
]
for label, pattern in artifacts:
    matches = re.findall(pattern, html, re.DOTALL)
    print(f"{label}: {len(matches)}处")

# Check MD sync
B2_MD = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.md')
with open(B2_MD, 'r', encoding='utf-8') as f:
    md = f.read()
md_h2 = len(re.findall(r'^## ', md, re.MULTILINE))
print(f"\nMD ## 数: {md_h2} (应为152)")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
