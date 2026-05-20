"""
Fix B3 by rebuilding from master with all R1+R3 changes + R4 chapter additions.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
MASTER = 'd:/ProgramWork/WriteBookProject/docs/2026-05-14/学习书/银杏辞-yinxing-ci-novel-2026-05-14.html'

with open(MASTER, 'r', encoding='utf-8') as f:
    master = f.read()

SC = r'[零一二三四五六七八九十百千]+'

def extract_master_ch(num):
    """Extract chapter HTML by master chapter number."""
    marker = f'<h2 id="ch{num}">'
    pos = master.find(marker)
    if pos < 0:
        return None
    next_ch = master.find('<h2 id="ch', pos + len(marker))
    if next_ch < 0:
        next_ch = master.find('<footer class="colophon"', pos)
    if next_ch < 0:
        next_ch = len(master)
    return master[pos:next_ch]

def clean_chapter(ch_html, new_num):
    """Remove extension prefix, update master ch ID to new_num, clean end marker."""
    # Update H2 id
    ch_html = re.sub(r'<h2 id="ch\d+">', f'<h2 id="ch{new_num}">', ch_html, count=1)
    # Remove prefix from title
    ch_html = re.sub(rf'<h2 id="ch{new_num}">扩展{SC} ', f'<h2 id="ch{new_num}">', ch_html)
    # Clean end marker
    ch_html = re.sub(rf'（扩展{SC} 完）', '（完）', ch_html)
    return ch_html

def cjk_count(text):
    return len(re.findall(r'[一-鿿]', text))

# Build B3 from scratch
# Source chapters from master (original ch IDs -> new position)
# Phase 1: R1 dedup - remove 9 chapters from original B3
# Original B3 had 31 chapters (master ext numbers mapped to original positions)
# After R1: removed 探芽, 迎燕, 补经, 拾叶, 围炉, 拥衾, 初雪(532), 银杏食录, 洛城风物志
# And swapped 重阳/秋祭

# B3 after R1 had these master chapters (in order):
b3_master_chapters = [
    # 春之卷
    ('扩展七十五 清明', None),       # will extract by content
    ('扩展八十七 纸鸢', None),
    ('扩展七十一 端午', None),
    ('扩展六十六 七夕', None),
    # 夏之卷
    ('扩展四百零九 纳凉', None),
    ('扩展八十六 试茶', None),
    ('扩展七十二 中秋', None),
    ('扩展六十九 秋祭', None),  # swapped with 重阳
    ('扩展七十三 重阳', None),
    # 秋之卷
    ('扩展一百零二 霜降', None),
    ('扩展二百二十七 暮鸦', None),
    # 冬之卷
    ('扩展七十四 除夕', None),
    ('扩展七十六 初雪', None),  # this is 扩展七十六, NOT 扩展五百三十二
    ('扩展一百零七 雪夜', None),
    # 洛城风物
    ('扩展三十七 洛城四季图', None),
    ('扩展九十八 灯市', None),
    ('扩展一百一十六 市井', None),
    ('扩展一百七十八 市声', None),
    ('扩展六十八 灯谜会', None),
    ('扩展一百四十九 渡口', None),
    ('扩展九十二 酒约', None),
    ('扩展八十九 晒书日', None),
]

# Build mapping: ext_title → master_ch_id
# Scan master for all chapters
all_master = re.findall(rf'<h2 id="ch(\d+)">(扩展{SC} [^<]+)</h2>', master)
ext_to_master = {}
for ch_id_str, title in all_master:
    ext_to_master[title] = int(ch_id_str)

# Verify all chapters exist
for ext_title, _ in b3_master_chapters:
    if ext_title in ext_to_master:
        pass  # OK
    else:
        print(f"  WARNING: '{ext_title}' not found in master")

# R4: New chapters to add (master ext title, section position keyword)
r4_additions = [
    ('扩展三百一十八 春冰', 'after', '纸鸢'),      # 春之卷
    ('扩展二百三十八 归燕', 'after', '纸鸢'),      # 春之卷 (after 春冰)
    ('扩展三百二十一 晒伏', 'after', '试茶'),      # 夏之卷
    ('扩展三百零三 秋收', 'after', '暮鸦'),        # 秋之卷
    ('扩展三百四十七 霜晨', 'after', '暮鸦'),      # 秋之卷 (after 秋收)
    ('扩展三百一十六 雪晴', 'after', '初雪'),      # 冬之卷
    ('扩展三百四十八 雪后', 'after', '初雪'),      # 冬之卷 (after 雪晴)
    ('扩展二百三十七 旧匾', 'before', '晒书日'),   # 洛城风物
    ('扩展一百九十 残简', 'before', '晒书日'),     # 洛城风物
    ('扩展三百四十 断碑', 'before', '晒书日'),     # 洛城风物
]

# Build the final chapter list
final_titles = []
added_r4 = set()

# Helper to find ext_title in b3_master_chapters
def find_idx(keyword):
    for i, (t, _) in enumerate(b3_master_chapters):
        if keyword in t:
            return i
    return -1

for ext_title, position, ref_kw in r4_additions:
    if ext_title not in ext_to_master:
        print(f"  MISSING in master: {ext_title}")
        continue

    ref_idx = find_idx(ref_kw)
    if ref_idx < 0:
        print(f"  Cannot find reference '{ref_kw}' in B3 chapters")
        continue

    if position == 'after':
        insert_idx = ref_idx + 1
    else:  # before
        insert_idx = ref_idx

    # Insert, being careful about multiple inserts at same position
    b3_master_chapters.insert(insert_idx, (ext_title, 'R4'))
    added_r4.add(ext_title)
    print(f"  Added {ext_title} {position} {ref_kw} (at idx {insert_idx})")

print(f"\n  Total chapters: {len(b3_master_chapters)}")

# Now extract all chapters from master, clean, renumber
all_ch_html = []
for i, (ext_title, source) in enumerate(b3_master_chapters):
    if ext_title in ext_to_master:
        master_ch = ext_to_master[ext_title]
        ch_html = extract_master_ch(master_ch)
        if ch_html:
            ch_html = clean_chapter(ch_html, i + 1)
            all_ch_html.append(ch_html)
        else:
            print(f"  FAILED to extract: {ext_title} (master ch{master_ch})")
    else:
        print(f"  NOT FOUND: {ext_title}")

print(f"  Extracted {len(all_ch_html)} chapters")

# Build B3 HTML
# Read template from existing B3
with open(os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html'), 'r', encoding='utf-8') as f:
    old_b3 = f.read()

# Extract header (everything before <main>) and footer (from <footer)
header_end = old_b3.find('<main class="content">')
if header_end < 0:
    header_end = old_b3.find('<main>')

hero_end = old_b3.find('</header>', header_end)
footer_start = old_b3.find('<footer class="colophon"')
if footer_start < 0:
    footer_start = old_b3.find('<footer')

header = old_b3[:hero_end + len('</header>')]
footer = old_b3[footer_start:]

# Combine
chapters_html = '\n'.join(all_ch_html)
main_html = header + '\n' + chapters_html + '\n' + footer

# Add transition paragraph between 冬之卷 and 洛城风物
# Find 雪夜 → 洛城四季图 transition (now chapters 14 and 17 after additions?)
# Actually find "洛城四季图" heading
luo_match = re.search(r'<h2 id="ch\d+">洛城四季图</h2>', main_html)
if luo_match:
    pos = luo_match.start()
    # Find the end of previous chapter
    prev_end = main_html.rfind('</p>', 0, pos)
    if prev_end > 0:
        insert_at = prev_end + len('</p>')
        transition = '''

    <div style="text-align:center;margin:48px 0;color:var(--muted);font-size:15px;line-height:2;">
    四时轮转，风物不歇。<br>
    以下诸篇，记银杏城中街巷、渡口、市声、灯火——<br>
    是一城之人，在四季之外写下的另一种时间。
    </div>
'''
        main_html = main_html[:insert_at] + transition + main_html[insert_at:]

# Add editor note (编者识)
subtitle_match = re.search(r'<p class="no-indent"[^>]*>——[^<]+</p>', main_html)
if subtitle_match:
    insert_pos = subtitle_match.end()
    intro_html = (
        '\n\n    <div class="editor-intro" style="margin:20px 0;padding:12px 16px;'
        'background:var(--panel);border-radius:4px;'
        'font-size:14px;color:var(--muted);line-height:1.9;">'
        '本篇为《银杏辞》系列第三部。精选银杏城中与二十四节俗、四时物候、街巷市井相关的风物散文，'
        '按春、夏、秋、冬、洛城风物五部分编排。一城四季，各自成趣。'
        '</div>\n'
    )
    main_html = main_html[:insert_pos] + intro_html + main_html[insert_pos:]

# Rebuild TOC
chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', main_html)
sections = {
    'ch1': '春之卷',
    'ch6': '夏之卷',
    'ch13': '秋之卷',
    'ch21': '冬之卷',
    'ch27': '洛城风物',
}

toc_html = '<ol>\n'
for ch_id, title in chapters:
    if ch_id in sections:
        toc_html += f'      <li class="toc-section"><strong>{sections[ch_id]}</strong></li>\n'
    toc_html += f'      <li><a href="#{ch_id}">{title}</a></li>\n'
toc_html += '    </ol>'

new_toc = f'''<nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc_html}
    </nav>'''

main_html = re.sub(
    r'<nav class="toc-panel" id="toc">.*?</nav>',
    new_toc,
    main_html,
    flags=re.DOTALL
)

# Verify
final_ch = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', main_html)
print(f"\n  Final B3: {len(final_ch)} chapters")
ids = [int(c[0][2:]) for c in final_ch]
expected = list(range(1, len(final_ch) + 1))
assert ids == expected, f'ID mismatch: got {ids}'
print(f"  IDs continuous: OK")
for ch_id, title in final_ch:
    print(f"    {ch_id}: {title}")

# Save
b3_path = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
with open(b3_path, 'w', encoding='utf-8') as f:
    f.write(main_html)
print(f"\n  Saved: {b3_path}")

# Also regenerate MD
# Re-use the sync function from round3
import sys
sys.path.insert(0, 'd:/ProgramWork/WriteBookProject/scripts')
# Just do it inline
from scripts.round3_structural import sync_md_from_html
b3_md = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.md')
sync_md_from_html(b3_path, b3_md, '银杏城旧事', '四时风物，一城旧事')
print(f"  MD synced: {b3_md}")
print("\nB3 rebuild complete!")
