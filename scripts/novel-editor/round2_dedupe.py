"""
Round 2: Book 2 internal deduplication.
Rename 3 duplicate titles + add 晒书/晒经/晾书 note in 卷首.
Sync changes to both .html and .md files.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

# ============================================================
# Book 2: 清音寺居 - Rename 3 titles + add 卷首 note
# ============================================================
print("=== Processing Book 2: 《清音寺居》 ===")

b2_html = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
b2_md = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.md')

with open(b2_html, 'r', encoding='utf-8') as f:
    html = f.read()

# ---- 3 renames ----
renames = [
    # (old_title_substring, new_title_substring) - applied to H2, TOC, end markers
    ('扩展四百四十六 采蕨', '扩展四百四十六 再采蕨'),
    ('扩展四百七十一 听蝉', '扩展四百七十一 闻蝉'),
    ('扩展五百一十七 送春', '扩展五百一十七 春尽'),
]

for old, new in renames:
    count = html.count(old)
    html = html.replace(old, new)
    print(f"  Renamed: '{old}' → '{new}' ({count} occurrences)")

# ---- Add 卷首 note about 晒书/晒经/晾书 ----
# Find the 卷上 section marker or the TOC area to add a note
# Add as a small note after the subtitle/intro area, before chapter list
# Insert after the hero/header, before first chapter
ch1_marker = '<h2 id="ch1">'
ch1_pos = html.find(ch1_marker)
if ch1_pos > 0:
    # Find the paragraph before ch1
    before_ch1 = html[:ch1_pos]
    # Find the last </p> or </div> before ch1 to insert after
    last_p = before_ch1.rfind('</p>')
    if last_p < 0:
        last_p = before_ch1.rfind('</div>')

    if last_p > 0:
        note_html = (
            '\n\n'
            '    <div class="editor-note" style="margin:24px 0;padding:12px 16px;'
            'background:var(--panel);border-left:3px solid var(--accent);'
            'font-size:14px;color:var(--muted);">'
            '编者按：卷上中有"晒书"（ch3）、"晒经"（ch127）、"晾书"（ch138）三章，'
            '虽主题相近，然各有侧重——晒书为日常整理、晒经为佛经养护之仪轨、晾书为春末翻晒防蠹之法，请读者细辨其趣。'
            '</div>\n'
        )
        insert_pos = last_p + len('</p>')
        html = html[:insert_pos] + note_html + html[insert_pos:]
        print(f"  Added 晒书/晒经/晾书 editor note before ch1")

# ---- Rebuild TOC ----
def rebuild_toc(html_content):
    """Rebuild TOC based on current h2 chapters, preserving section markers."""
    chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html_content)

    # Preserve subsection structure
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

    html_content = re.sub(
        r'<nav class="toc-panel" id="toc">.*?</nav>',
        new_toc,
        html_content,
        flags=re.DOTALL
    )
    return html_content

html = rebuild_toc(html)
print("  TOC rebuilt")

# Save HTML
with open(b2_html, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"  HTML saved: {b2_html}")

# ---- Sync MD ----
with open(b2_md, 'r', encoding='utf-8') as f:
    md = f.read()

for old, new in renames:
    # In MD, the titles appear as: ## 扩展四百四十六 采蕨
    md_count = md.count(old)
    md = md.replace(old, new)
    print(f"  MD renamed: '{old}' → '{new}' ({md_count} occurrences)")

# Add 晒书 note in MD (before ## 扩展四百二十八)
first_ch_md = md.find('## 扩展四百二十八')
if first_ch_md > 0:
    md_note = (
        '> **编者按：** 卷上中有"晒书"（ch3）、"晒经"（ch127）、"晾书"（ch138）三章，'
        '虽主题相近，然各有侧重——晒书为日常整理、晒经为佛经养护之仪轨、晾书为春末翻晒防蠹之法，请读者细辨其趣。\n\n'
    )
    # Find the --- separator before first chapter
    sep_before = md.rfind('---', 0, first_ch_md)
    if sep_before > 0:
        # Insert after the separator line
        insert_at = md.find('\n', sep_before) + 1
        md = md[:insert_at] + '\n' + md_note + md[insert_at:]
        print(f"  Added MD 晒书 editor note")

with open(b2_md, 'w', encoding='utf-8') as f:
    f.write(md)
print(f"  MD saved: {b2_md}")

print("\n=== Round 2 Complete ===")
print("Changes:")
print("  - ch19: 采蕨 → 再采蕨")
print("  - ch44: 听蝉 → 闻蝉")
print("  - ch90: 送春 → 春尽")
print("  - 卷首: 添加晒书/晒经/晾书区分说明")
print("  - TOC rebuilt, .html + .md synced")
