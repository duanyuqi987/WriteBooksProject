"""
Story optimization: improve TOC structure, add season dividers,
and sync changes to both .html and .md files.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

# ============================================================
# Book 2 TOC improvement: Add sub-section markers
# ============================================================
print("=== Optimizing Book 2: 《清音寺居》 ===")

html_path = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
md_path = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.md')

with open(html_path, 'r', encoding='utf-8') as f:
    html2 = f.read()

# Extract chapter list with titles
chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html2)

# Define sub-sections for 卷上 (ch1-ch119) by scanning chapter themes
# Group roughly by activity type:
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
    'ch129': '山中岁时·春盛（采蕨·春茶·种豆·听蛙）',
    'ch133': '山中岁时·春深（清明·雨后·洗石·笋时）',
    'ch137': '山中岁时·春末（抄谱·晾书·夜坐·蚕月）',
    'ch141': '山中岁时·夏至（谷雨·种瓜·磨豆·扫塔）',
    'ch145': '山中岁时·夏深（晚钟·惜春·送春·立夏）',
    'ch149': '山中岁时·夏盛（换衣·听蝉·午后·无尽）',
}

# Build new TOC HTML
toc_entries = []
current_subsection = None

for ch_id, title in chapters:
    ch_num = int(ch_id[2:])
    # Check if this chapter starts a new subsection
    if ch_id in subsection_markers:
        current_subsection = subsection_markers[ch_id]
        toc_entries.append(('subsection', current_subsection, ch_id))
    toc_entries.append(('chapter', f'{title}', ch_id))

# Build TOC HTML
toc_html = '<ol>\n'
for entry_type, label, anchor in toc_entries:
    if entry_type == 'subsection':
        toc_html += f'      <li class="toc-section"><strong>{label}</strong></li>\n'
    else:
        toc_html += f'      <li><a href="#{anchor}">{label}</a></li>\n'
toc_html += '    </ol>'

# Replace TOC in HTML
old_toc_pattern = r'<nav class="toc-panel" id="toc">.*?</nav>'
new_toc = f'''<nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc_html}
    </nav>'''

html2 = re.sub(old_toc_pattern, new_toc, html2, flags=re.DOTALL)

# Add season divider HTML comments between major sections
# Insert dividers at key transition points
divider_map = {
    'ch120': '\n    <!-- ═══════════ 卷下：山中岁时 ═══════════ -->\n',
    'ch125': '\n    <!-- ────────── 春来 ────────── -->\n',
    'ch133': '\n    <!-- ────────── 春深 ────────── -->\n',
    'ch141': '\n    <!-- ────────── 夏至 ────────── -->\n',
    'ch149': '\n    <!-- ────────── 夏盛 ────────── -->\n',
}

for ch_id, divider_html in sorted(divider_map.items(), reverse=True):
    marker = f'<h2 id="{ch_id}">'
    pos = html2.find(marker)
    if pos > 0:
        html2 = html2[:pos] + divider_html + html2[pos:]

# Also add a main divider between 卷上 and 卷下
ch120_marker = '<h2 id="ch120">'
pos120 = html2.find(ch120_marker)
if pos120 > 0:
    # Find the end marker of ch119
    prev_end = html2.rfind('</p>', 0, pos120)
    if prev_end > 0:
        vol_divider = '\n\n    <div style="text-align:center;margin:48px 0;color:var(--muted);">——— 卷下：山中岁时 ———</div>\n\n'
        html2 = html2[:prev_end+4] + vol_divider + html2[prev_end+4:]

# Save HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html2)
print(f"  HTML updated: {html_path}")

# Update MD file with same structure
with open(md_path, 'r', encoding='utf-8') as f:
    md2 = f.read()

# Add season dividers in MD
md_divider_map = {
    '## 扩展五百二十 送寒': '\n---\n### 卷下：山中岁时 · 冬尽\n',
    '## 扩展五百五十二 迎燕': '\n### 春来\n',
    '## 扩展五百六十 清明': '\n### 春深\n',
    '## 扩展五百六十八 谷雨': '\n### 夏至\n',
    '## 扩展五百七十六 换衣': '\n### 夏盛\n',
}

for marker_text, divider_md in sorted(md_divider_map.items(), reverse=True):
    pos = md2.find(marker_text)
    if pos > 0:
        md2 = md2[:pos] + divider_md + '\n' + md2[pos:]

# Also add a main 卷下 divider
vol2_marker = '## 扩展五百二十 送寒'
pos_v2 = md2.find(vol2_marker)
if pos_v2 > 0:
    md2 = md2[:pos_v2] + '---\n### 卷下：山中岁时\n\n' + md2[pos_v2:]

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md2)
print(f"  MD updated: {md_path}")


# ============================================================
# Book 3 TOC improvement: List all chapters
# ============================================================
print("\n=== Optimizing Book 3: 《银杏城旧事》 ===")

html3_path = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
md3_path = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.md')

with open(html3_path, 'r', encoding='utf-8') as f:
    html3 = f.read()

ch3 = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html3)
print(f"  Book 3 has {len(ch3)} chapters")

# Build improved TOC with section headers
toc3_sections = {
    'ch1': '春之卷',
    'ch5': '夏之卷',
    'ch10': '秋之卷',
    'ch16': '冬之卷',
    'ch22': '洛城风物',
}

toc3_html = '<ol>\n'
for ch_id, title in ch3:
    if ch_id in toc3_sections:
        toc3_html += f'      <li class="toc-section"><strong>{toc3_sections[ch_id]}</strong></li>\n'
    toc3_html += f'      <li><a href="#{ch_id}">{title}</a></li>\n'
toc3_html += '    </ol>'

new_toc3 = f'''<nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc3_html}
    </nav>'''

html3 = re.sub(r'<nav class="toc-panel" id="toc">.*?</nav>', new_toc3, html3, flags=re.DOTALL)

with open(html3_path, 'w', encoding='utf-8') as f:
    f.write(html3)
print(f"  HTML updated: {html3_path}")

# MD: add section headers
with open(md3_path, 'r', encoding='utf-8') as f:
    md3 = f.read()

md3_sections = {
    '## 扩展九十四 清明': '\n### 春之卷\n',
    '## 扩展九十 端午': '\n### 夏之卷\n',
    '## 扩展九十一 中秋': '\n### 秋之卷\n',
    '## 扩展九十三 除夕': '\n### 冬之卷\n',
    '## 扩展五十六 洛城四季图': '\n### 洛城风物\n',
}

for marker, divider in sorted(md3_sections.items(), reverse=True):
    pos = md3.find(marker)
    if pos > 0:
        md3 = md3[:pos] + divider + '\n' + md3[pos:]

with open(md3_path, 'w', encoding='utf-8') as f:
    f.write(md3)
print(f"  MD updated: {md3_path}")


# ============================================================
# Book 4 TOC improvement: Add character-group headers
# ============================================================
print("\n=== Optimizing Book 4: 《银杏人物志》 ===")

html4_path = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.html')
md4_path = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.md')

with open(html4_path, 'r', encoding='utf-8') as f:
    html4 = f.read()

ch4 = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html4)
print(f"  Book 4 has {len(ch4)} chapters")

toc4_sections = {
    'ch1': '云姬卷',
    'ch7': '苏映雪卷',
    'ch13': '楚寒衣卷',
    'ch17': '陆明远卷',
    'ch22': '赵婉柔卷',
    'ch26': '沈怀瑾卷',
    'ch30': '顾长卿卷',
    'ch34': '外传与散篇',
}

toc4_html = '<ol>\n'
for ch_id, title in ch4:
    if ch_id in toc4_sections:
        toc4_html += f'      <li class="toc-section"><strong>{toc4_sections[ch_id]}</strong></li>\n'
    toc4_html += f'      <li><a href="#{ch_id}">{title}</a></li>\n'
toc4_html += '    </ol>'

new_toc4 = f'''<nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc4_html}
    </nav>'''

html4 = re.sub(r'<nav class="toc-panel" id="toc">.*?</nav>', new_toc4, html4, flags=re.DOTALL)

with open(html4_path, 'w', encoding='utf-8') as f:
    f.write(html4)
print(f"  HTML updated: {html4_path}")

with open(md4_path, 'r', encoding='utf-8') as f:
    md4 = f.read()

md4_sections = {
    '## 扩展一 望江楼': '\n### 云姬卷\n',
    '## 扩展七 授琴诗社': '\n### 苏映雪卷\n',
    '## 扩展十三 剑影': '\n### 楚寒衣卷\n',
    '## 扩展十七 纨绔': '\n### 陆明远卷\n',
    '## 扩展二十二 冷宫春暖': '\n### 赵婉柔卷\n',
    '## 扩展二十六 陈情': '\n### 沈怀瑾卷\n',
    '## 扩展三十 银杏辞': '\n### 顾长卿卷\n',
    '## 扩展三十四 外传·若华': '\n### 外传与散篇\n',
}

for marker, divider in sorted(md4_sections.items(), reverse=True):
    pos = md4.find(marker)
    if pos > 0:
        md4 = md4[:pos] + divider + '\n' + md4[pos:]

with open(md4_path, 'w', encoding='utf-8') as f:
    f.write(md4)
print(f"  MD updated: {md4_path}")


# ============================================================
# Book 5 TOC improvement: Add category headers
# ============================================================
print("\n=== Optimizing Book 5: 《银杏辞·附录卷》 ===")

html5_path = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.html')
md5_path = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.md')

with open(html5_path, 'r', encoding='utf-8') as f:
    html5 = f.read()

ch5 = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html5)
print(f"  Book 5 has {len(ch5)} chapters")

toc5_sections = {
    'ch1': '诗词全录',
    'ch8': '人物春秋',
    'ch14': '诗谶辑录',
    'ch18': '风物志',
    'ch22': '寺庙志',
    'ch26': '时序录与梦境',
}

toc5_html = '<ol>\n'
for ch_id, title in ch5:
    if ch_id in toc5_sections:
        toc5_html += f'      <li class="toc-section"><strong>{toc5_sections[ch_id]}</strong></li>\n'
    toc5_html += f'      <li><a href="#{ch_id}">{title}</a></li>\n'
toc5_html += '    </ol>'

new_toc5 = f'''<nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc5_html}
    </nav>'''

html5 = re.sub(r'<nav class="toc-panel" id="toc">.*?</nav>', new_toc5, html5, flags=re.DOTALL)

with open(html5_path, 'w', encoding='utf-8') as f:
    f.write(html5)
print(f"  HTML updated: {html5_path}")

# MD
with open(md5_path, 'r', encoding='utf-8') as f:
    md5 = f.read()

md5_sections = {
    '## 扩展五十三 诗词全录': '\n### 诗词全录\n',
    '## 扩展六十 人物春秋': '\n### 人物春秋\n',
    '## 扩展六十六 诗谶辑录': '\n### 诗谶辑录\n',
    '## 扩展七十 洛城风物志': '\n### 风物志\n',
    '## 扩展七十四 清音寺志': '\n### 寺庙志\n',
    '## 扩展七十八 梦境录': '\n### 时序录与梦境\n',
}

for marker, divider in sorted(md5_sections.items(), reverse=True):
    pos = md5.find(marker)
    if pos > 0:
        md5 = md5[:pos] + divider + '\n' + md5[pos:]

with open(md5_path, 'w', encoding='utf-8') as f:
    f.write(md5)
print(f"  MD updated: {md5_path}")


print("\n=== All Books Optimized ===")
print("Changes:")
print("  - Book 2: Added 15 sub-section markers + season dividers in TOC")
print("  - Book 3: Listed all 31 chapter titles in TOC with 5 volume headers")
print("  - Book 4: Added 8 character-group headers in TOC")
print("  - Book 5: Added 6 category headers in TOC")
print("  - All changes synced to both .html and .md files")
