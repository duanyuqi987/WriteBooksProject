"""
Fix B3 by rebuilding from master using original chapter IDs.
Applies R1 (dedup) + R3 (prefix removal, transition) + R4 (10 new chapters).
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
MASTER = 'd:/ProgramWork/WriteBookProject/docs/2026-05-14/学习书/银杏辞-yinxing-ci-novel-2026-05-14.html'

with open(MASTER, 'r', encoding='utf-8') as f:
    master = f.read()

SC = r'[零一二三四五六七八九十百千]+'

def extract_chapter(master_ch_id):
    """Extract chapter HTML by master ch ID."""
    marker = f'<h2 id="ch{master_ch_id}">'
    pos = master.find(marker)
    if pos < 0:
        return None, None
    next_ch = master.find('<h2 id="ch', pos + len(marker))
    if next_ch < 0:
        next_ch = master.find('<footer class="colophon"', pos)
    if next_ch < 0:
        next_ch = len(master)
    content = master[pos:next_ch]
    title_match = re.search(r'<h2 id="ch\d+">([^<]+)</h2>', content)
    title = title_match.group(1) if title_match else '?'
    return content, title

def clean_chapter(ch_html):
    """Remove extension prefix, clean end marker."""
    ch_html = re.sub(rf'<h2 id="ch\d+">扩展{SC} ', '<h2 id="chPLACEHOLDER">', ch_html, count=1)
    ch_html = re.sub(rf'（扩展{SC} 完）', '（完）', ch_html)
    return ch_html

# Original B3 master IDs (from extract_all_books.py)
original_b3 = [
    # 春之卷
    94, 106, 570, 571,
    # 夏之卷
    90, 85, 471, 428, 105,
    # 秋之卷
    91, 92, 88, 121, 547, 246,
    # 冬之卷
    93, 95, 126, 552, 564, 551,
    # 洛城风物
    56, 59, 71, 117, 135, 197, 87, 168, 111, 108,
]

# R1: IDs to remove (9 chapters)
remove_ids = set()
# Find IDs by searching for specific ext titles
for ext_num in ['五百五十一', '五百五十二', '四百五十二', '五百二十八',
                '五百三十三', '五百四十五', '五百三十二']:
    pattern = rf'<h2 id="ch(\d+)">扩展{ext_num} '
    matches = re.findall(pattern, master)
    for m in matches:
        remove_ids.add(int(m))

# Also: 扩展四十 银杏食录 (but NOT 扩展四百XX)
# 扩展五十二 洛城风物志
for ext_num in ['四十', '五十二']:
    # Use word boundary: match exactly "扩展四十 " not "扩展四百"
    pattern = rf'<h2 id="ch(\d+)">扩展{ext_num} ([^<]+)</h2>'
    for m_obj in re.finditer(pattern, master):
        title = m_obj.group(2)
        title_before = '扩展' + ext_num + ' ' + title
        # Only match if ext is standalone (not part of larger number)
        if not re.search(rf'扩展{ext_num}\d', title_before):
            remove_ids.add(int(m_obj.group(1)))

print(f"Remove IDs: {sorted(remove_ids)}")

# Verify each ID is in original_b3
for rid in sorted(remove_ids):
    if rid in original_b3:
        print(f"  Will remove master-ch{rid}")
    else:
        print(f"  WARNING: master-ch{rid} not in original_b3!")

# Build final ID list (without removed, with R4 additions)
b3_ids = [x for x in original_b3 if x not in remove_ids]

# R4: New master IDs to add
# Insert as (master_id, position_keyword, 'after'|'before')
r4_additions = [
    (337, '纸鸢', 'after'),     # 春冰 → after 纸鸢(ch106)
    (257, '纸鸢', 'after'),     # 归燕 → after 春冰
    (340, '试茶', 'after'),     # 晒伏 → after 试茶(ch85)
    (322, '暮鸦', 'after'),     # 秋收 → after 暮鸦(ch246)
    (366, '暮鸦', 'after'),     # 霜晨 → after 秋收
    (335, '初雪', 'after'),     # 雪晴 → after 初雪(ch95)
    (367, '初雪', 'after'),     # 雪后 → after 雪晴
    (256, '晒书日', 'before'),  # 旧匾 → before 晒书日(ch108)
    (209, '晒书日', 'before'),  # 残简 → before 晒书日
    (359, '晒书日', 'before'),  # 断碑 → before 晒书日
]

# Build title→position mapping
# First, extract all current titles
current_titles = {}
for mid in b3_ids:
    _, title = extract_chapter(mid)
    if title:
        current_titles[mid] = title

# For each R4 addition, find the reference chapter's position in b3_ids
for new_id, ref_kw, direction in r4_additions:
    # Find which chapter in b3_ids has ref_kw in its title
    ref_pos = None
    for i, mid in enumerate(b3_ids):
        if mid in current_titles and ref_kw in current_titles[mid]:
            ref_pos = i
            break

    if ref_pos is not None:
        insert_at = ref_pos + 1 if direction == 'after' else ref_pos
        b3_ids.insert(insert_at, new_id)
        _, title = extract_chapter(new_id)
        current_titles[new_id] = title if title else '?'
        print(f"  Added master-ch{new_id} ({title}) {direction} ch{ref_pos+1}")
    else:
        print(f"  WARNING: Cannot find ref '{ref_kw}' in B3 for ch{new_id}")

print(f"\nTotal chapters after R4: {len(b3_ids)}")

# Extract, clean, and assemble
all_chapters_html = []
for i, mid in enumerate(b3_ids):
    ch_html, title = extract_chapter(mid)
    if ch_html:
        ch_html = clean_chapter(ch_html)
        # Set correct ch ID
        ch_html = ch_html.replace('id="chPLACEHOLDER"', f'id="ch{i+1}"')
        cjk = len(re.findall(r'[一-鿿]', ch_html))
        print(f"  ch{i+1}: {title} (master-ch{mid}, {cjk} CJK)")
        all_chapters_html.append(ch_html)
    else:
        print(f"  MISSING: master-ch{mid}")

# Read template from old B3
with open(os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html'), 'r', encoding='utf-8') as f:
    old_b3 = f.read()

# Extract header and footer
hero_end = old_b3.find('</header>')
if hero_end < 0:
    hero_end = old_b3.find('<main')
    hero_section = old_b3[:hero_end]
else:
    hero_section = old_b3[:hero_end + len('</header>')]

footer_start = old_b3.find('<footer class="colophon"')
if footer_start < 0:
    footer_start = old_b3.find('<footer')
footer_section = old_b3[footer_start:] if footer_start >= 0 else ''

# Assemble
chapters_str = '\n\n'.join(all_chapters_html)
full_html = hero_section + '\n' + chapters_str + '\n' + footer_section

# Add transition (before 洛城四季图)
luo_match = re.search(r'<h2 id="ch(\d+)">洛城四季图</h2>', full_html)
if luo_match:
    pos = luo_match.start()
    prev_end = full_html.rfind('</p>', 0, pos)
    if prev_end > 0:
        insert_at = prev_end + len('</p>')
        transition = '''

    <div style="text-align:center;margin:48px 0;color:var(--muted);font-size:15px;line-height:2;">
    四时轮转，风物不歇。<br>
    以下诸篇，记银杏城中街巷、渡口、市声、灯火——<br>
    是一城之人，在四季之外写下的另一种时间。
    </div>
'''
        full_html = full_html[:insert_at] + transition + full_html[insert_at:]

# Add 编者识
sub_match = re.search(r'<p class="no-indent"[^>]*>——[^<]+</p>', full_html)
if sub_match:
    insert_pos = sub_match.end()
    intro_html = (
        '\n\n    <div class="editor-intro" style="margin:20px 0;padding:12px 16px;'
        'background:var(--panel);border-radius:4px;'
        'font-size:14px;color:var(--muted);line-height:1.9;">'
        '本篇为《银杏辞》系列第三部。精选银杏城中与二十四节俗、四时物候、街巷市井相关的风物散文，'
        '按春、夏、秋、冬、洛城风物五部分编排。一城四季，各自成趣。'
        '</div>\n'
    )
    full_html = full_html[:insert_pos] + intro_html + full_html[insert_pos:]

# Rebuild TOC
chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', full_html)
# Determine section boundaries based on content
sections = {}
vol_spring = True
vol_summer = False
vol_autumn = False
vol_winter = False
vol_fengwu = False

for ch_id, title in chapters:
    ch_num = int(ch_id[2:])
    if ch_num == 1:
        sections[ch_id] = '春之卷'
    elif '纳凉' in title and vol_summer is False:
        sections[ch_id] = '夏之卷'
        vol_summer = True
    elif '霜降' in title and vol_autumn is False:
        sections[ch_id] = '秋之卷'
        vol_autumn = True
    elif '除夕' in title and vol_winter is False:
        sections[ch_id] = '冬之卷'
        vol_winter = True
    elif '洛城四季图' in title and vol_fengwu is False:
        sections[ch_id] = '洛城风物'
        vol_fengwu = True

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

full_html = re.sub(
    r'<nav class="toc-panel" id="toc">.*?</nav>',
    new_toc,
    full_html,
    flags=re.DOTALL
)

# Verify IDs
final_ch = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', full_html)
ids = [int(c[0][2:]) for c in final_ch]
expected = list(range(1, len(final_ch) + 1))
if ids != expected:
    print(f"ID MISMATCH!")
    for i, (ch_id, title) in enumerate(final_ch):
        print(f"  ch{ids[i]}: {title}")
else:
    print(f"\nIDs continuous: 1-{len(final_ch)} OK")

# Save
b3_path = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
with open(b3_path, 'w', encoding='utf-8') as f:
    f.write(full_html)
print(f"\nSaved: {b3_path}")

# Regenerate MD
def html_to_md_simple(html_chapters):
    def inner_to_bq(m):
        inner = m.group(1)
        p_match = re.search(r'<p>(.*?)</p>', inner, re.DOTALL)
        if p_match:
            text = p_match.group(1).strip()
            lines = text.split('\n')
            quoted = '\n'.join('> ' + line.strip() for line in lines if line.strip())
            return '\n\n' + quoted + '\n\n'
        return ''
    md = re.sub(r'<div class="inner-monologue">(.*?)</div>', inner_to_bq, html_chapters, flags=re.DOTALL)
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

# Extract chapters portion
main_start = full_html.find('<main class="content">')
footer_pos = full_html.find('<footer class="colophon"')
hero_end_md = full_html.find('</header>', main_start)
chapters_html = full_html[hero_end_md + len('</header>'):footer_pos]
colophon_html = full_html[footer_pos:full_html.find('</footer>', footer_pos) + len('</footer>')]

chapters_md = html_to_md_simple(chapters_html)
colophon_clean = re.sub(r'<[^>]+>', '', colophon_html).strip()
colophon_clean = '\n'.join(line.strip() for line in colophon_clean.split('\n') if line.strip())

md_content = f'# 银杏城旧事\n\n**四时风物，一城旧事**\n\n---\n\n{chapters_md}\n\n---\n\n{colophon_clean}\n'

b3_md_path = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.md')
with open(b3_md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)
print(f"MD saved: {b3_md_path}")

print("\nB3 rebuild complete!")
