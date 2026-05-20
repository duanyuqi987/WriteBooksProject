"""
Finalize B2: rebuild TOC, sync MD, run comprehensive verification.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_HTML = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
B2_MD = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.md')

with open(B2_HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# Rebuild TOC
# ============================================================
chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html)
print(f"Total chapters: {len(chapters)}")

subsection_markers = {
    'ch1': '文房日常（磨墨·裁纸·抄经）',
    'ch11': '寺中劳作（挑水·劈柴·扫地·种菜）',
    'ch31': '厨下烟火（煮粥·腌菜·磨豆·蒸糕）',
    'ch51': '四季衣衫（换季·缝补·洗衣·纳凉）',
    'ch71': '寺中人事（香客·游方·施主·邻里）',
    'ch91': '晨钟暮鼓（早课·晚钟·打坐·诵经）',
    'ch111': '冬藏时节（数九·候雪·围炉·拥炉）',
    'ch120': '山中岁时·冬尽（送寒·数九·听冰·找芽）',
    'ch125': '山中岁时·春来（迎燕·开窗·晒经·踏青）',
    'ch129': '山中岁时·春盛（再采蕨·春茶·种豆·听蛙）',
    'ch133': '山中岁时·春深（清明·雨后·洗石·笋时）',
    'ch137': '山中岁时·春末（抄谱·晾书·夜坐·蚕月）',
    'ch141': '山中岁时·夏至（谷雨·种瓜·磨豆·扫塔）',
    'ch145': '山中岁时·夏深（晚钟·惜春·春尽·立夏）',
    'ch149': '山中岁时·夏盛（换衣·闻蝉·午后·无尽）',
}

toc_entries = []
for ch_id, title in chapters:
    if ch_id in subsection_markers:
        toc_entries.append(('subsection', subsection_markers[ch_id], ch_id))
    toc_entries.append(('chapter', title, ch_id))

toc_html = '<ol>\n'
for entry_type, label, anchor in toc_entries:
    if entry_type == 'subsection':
        toc_html += f'      <li class="toc-section"><strong>{label}</strong></li>\n'
    else:
        toc_html += f'      <li><a href="#{anchor}">{label}</a></li>\n'
toc_html += '    </ol>'

new_toc = f'''<nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc_html}
    </nav>'''

html = re.sub(
    r'<nav class="toc-panel" id="toc">.*?</nav>',
    new_toc,
    html,
    flags=re.DOTALL
)
print("TOC rebuilt")

# Save HTML
with open(B2_HTML, 'w', encoding='utf-8') as f:
    f.write(html)


# ============================================================
# Sync MD
# ============================================================
def html_to_md(chapters_html):
    def inner_to_bq(m):
        inner = m.group(1)
        p_match = re.search(r'<p>(.*?)</p>', inner, re.DOTALL)
        if p_match:
            text = p_match.group(1).strip()
            lines = text.split('\n')
            quoted = '\n'.join('> ' + line.strip() for line in lines if line.strip())
            return '\n\n' + quoted + '\n\n'
        return ''
    md = re.sub(r'<div class="inner-monologue">(.*?)</div>', inner_to_bq, chapters_html, flags=re.DOTALL)
    def poem_to_bq(m):
        inner = m.group(1)
        lines = re.findall(r'<p>(.*?)</p>', inner)
        return '\n\n' + '\n'.join('> ' + l.strip() for l in lines if l.strip()) + '\n\n'
    md = re.sub(r'<div class="poem-block">(.*?)</div>', poem_to_bq, md, flags=re.DOTALL)
    md = re.sub(r'<h2 id="ch\d+">([^<]+)</h2>', r'\n## \1\n', md)
    md = re.sub(r'<h3[^>]*>([^<]+)</h3>', r'\n### \1\n', md)
    md = re.sub(r'<div class="divider">.*?</div>', '\n---\n', md)
    md = re.sub(r'<p style="text-align:center;text-indent:0;color:var\(--muted\);">(.*?)</p>', r'\n\n*\1*\n', md)
    def p_replacer(m):
        inner = m.group(1)
        inner = re.sub(r'<br\s*/?>', '\n', inner)
        inner = re.sub(r'<[^>]+>', '', inner)
        return '\n' + inner.strip() + '\n'
    md = re.sub(r'<p(?:\s[^>]*)?>(.*?)</p>', p_replacer, md, flags=re.DOTALL)
    md = re.sub(r'<[^>]+>', '', md)
    lines = [l.strip() for l in md.split('\n')]
    md = '\n'.join(lines)
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    return md.strip()

# Extract chapters
main_start = html.find('<main class="content">')
footer_start = html.find('<footer class="colophon"')
hero_end = html.find('</header>', main_start)
chapters_html = html[hero_end + len('</header>'):footer_start]
colophon_end = html.find('</footer>', footer_start)
colophon_html = html[footer_start:colophon_end + len('</footer>')] if colophon_end >= 0 else ''

chapters_md = html_to_md(chapters_html)
colophon_clean = re.sub(r'<[^>]+>', '', colophon_html).strip()
colophon_clean = '\n'.join(line.strip() for line in colophon_clean.split('\n') if line.strip())

md_content = f'# 清音寺居\n\n**山中无历日，寒尽不知年**\n\n---\n\n{chapters_md}\n\n---\n\n{colophon_clean}\n'

with open(B2_MD, 'w', encoding='utf-8') as f:
    f.write(md_content)
print(f"MD synced: {B2_MD}")


# ============================================================
# Comprehensive verification
# ============================================================
print("\n=== Verification ===")

# 1. Chapter count
chapters_final = re.findall(r'<h2 id="ch(\d+)">', html)
print(f"1. Chapter count: {len(chapters_final)}")
assert len(chapters_final) == 152, f"Expected 152, got {len(chapters_final)}"

# 2. ID continuity
ids = [int(x) for x in chapters_final]
assert ids == list(range(1, 153)), f"IDs not continuous!"
print("2. IDs continuous: ch1-ch152 OK")

# 3. No extension prefix
ext_in_h2 = [c for c in re.findall(r'<h2 id="ch\d+">([^<]+)</h2>', html) if c.startswith('扩展')]
print(f"3. Extension prefix remaining: {len(ext_in_h2)}")
assert len(ext_in_h2) == 0

# 4. Character presence improvement
ji_count = html.count('寂声')
shen_count = html.count('秋白')
sun_count = html.count('老孙')
print(f"4. Character mentions: 寂声={ji_count}, 秋白={shen_count}, 老孙={sun_count}")

# Count chapters with each character
chapters_w_ji = 0
chapters_w_shen = 0
chapters_w_sun = 0
chapters_w_all3 = 0
for i in range(1, 153):
    pos = html.find(f'<h2 id="ch{i}">')
    next_h2 = html.find('<h2 id="ch', pos + 20)
    if next_h2 < 0:
        next_h2 = html.find('<footer', pos)
    content = html[pos:next_h2] if next_h2 > 0 else html[pos:]
    has_ji = '寂声' in content
    has_shen = '秋白' in content
    has_sun = '老孙' in content
    if has_ji: chapters_w_ji += 1
    if has_shen: chapters_w_shen += 1
    if has_sun: chapters_w_sun += 1
    if has_ji and has_shen and has_sun: chapters_w_all3 += 1

print(f"   寂声 in {chapters_w_ji}/152 = {100*chapters_w_ji//152}%")
print(f"   秋白 in {chapters_w_shen}/152 = {100*chapters_w_shen//152}%")
print(f"   老孙 in {chapters_w_sun}/152 = {100*chapters_w_sun//152}%")
print(f"   三人同在: {chapters_w_all3}/152 = {100*chapters_w_all3//152}%")

# 5. Inner-monologue coverage
chapters_no_inner = 0
for i in range(1, 153):
    pos = html.find(f'<h2 id="ch{i}">')
    next_h2 = html.find('<h2 id="ch', pos + 20)
    if next_h2 < 0:
        next_h2 = html.find('<footer', pos)
    content = html[pos:next_h2] if next_h2 > 0 else html[pos:]
    if 'inner-monologue' not in content:
        chapters_no_inner += 1
print(f"5. Chapters without inner-monologue: {chapters_no_inner}")

# 6. Shortest chapter
min_cjk = 9999
min_ch = ''
for i in range(1, 153):
    pos = html.find(f'<h2 id="ch{i}">')
    next_h2 = html.find('<h2 id="ch', pos + 20)
    if next_h2 < 0:
        next_h2 = html.find('<footer', pos)
        if next_h2 < 0:
            next_h2 = html.find('<div class="divider">', pos)
    content = html[pos:next_h2] if next_h2 > 0 else html[pos:pos+5000]
    cjk = len(re.findall(r'[一-鿿]', content))
    if cjk < min_cjk:
        min_cjk = cjk
        min_ch = f'ch{i}'
print(f"6. Shortest chapter: {min_ch} ({min_cjk} CJK)")

# 7. MD sync check
with open(B2_MD, 'r', encoding='utf-8') as f:
    md = f.read()
md_h2s = len(re.findall(r'^## ', md, re.MULTILINE))
print(f"7. MD chapters: {md_h2s}")
assert md_h2s == 152

# 8. Word count
total_cjk = len(re.findall(r'[一-鿿]', html[html.find('<main'):html.find('<footer')]))
print(f"8. Total CJK: ~{total_cjk:,}")

# Update word count meta
html = re.sub(r'<meta name="word-count" content="\d+">', f'<meta name="word-count" content="{total_cjk}">', html)
with open(B2_HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"   Word count meta updated to {total_cjk}")

print("\n=== ALL VERIFICATIONS PASSED ===")
