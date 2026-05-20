"""
Round 1: Cross-book deduplication.
Remove duplicate chapters from B3 and B5, fix B3 节俗排序.
Sync changes to both .html and .md files.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

# ============================================================
# Helper functions
# ============================================================
def get_chapter_map(html_content):
    """Get ordered list of (ch_id, ext_title) from HTML."""
    chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html_content)
    return chapters

def extract_chapter_content(html_content, ch_id):
    """Extract the full HTML content for a specific chapter ID."""
    marker = f'<h2 id="{ch_id}">'
    pos = html_content.find(marker)
    if pos < 0:
        return None, None, None

    # Find next chapter or footer
    next_h2 = html_content.find('<h2 id="ch', pos + len(marker))
    if next_h2 < 0:
        next_h2 = html_content.find('<footer class="colophon"', pos)
    if next_h2 < 0:
        next_h2 = html_content.find('</main>', pos)
    if next_h2 < 0:
        next_h2 = len(html_content)

    return pos, next_h2, html_content[pos:next_h2]

def remove_chapters_by_ext_titles(html_content, ext_titles_to_remove):
    """Remove chapters matching specific '扩展XXX' titles. Returns (new_html, removed_count)."""
    chapters = get_chapter_map(html_content)
    ids_to_remove = set()
    for ch_id, ext_title in chapters:
        for remove_title in ext_titles_to_remove:
            if remove_title in ext_title:
                ids_to_remove.add(ch_id)
                break

    print(f"  Chapters to remove: {sorted(ids_to_remove)}")

    # Remove chapters from HTML
    for ch_id in sorted(ids_to_remove, key=lambda x: int(x[2:]), reverse=True):
        pos, end_pos, _ = extract_chapter_content(html_content, ch_id)
        if pos is not None:
            html_content = html_content[:pos] + html_content[end_pos:]

    return html_content, len(ids_to_remove)

def swap_chapters(html_content, ch_id1, ch_id2):
    """Swap two adjacent chapters in HTML."""
    chapters = get_chapter_map(html_content)
    id_list = [c[0] for c in chapters]

    if ch_id1 not in id_list or ch_id2 not in id_list:
        print(f"  WARNING: Cannot swap {ch_id1} and {ch_id2} - not both found")
        return html_content

    idx1 = id_list.index(ch_id1)
    idx2 = id_list.index(ch_id2)

    # Extract both chapters
    pos1, end1, content1 = extract_chapter_content(html_content, ch_id1)
    pos2, end2, content2 = extract_chapter_content(html_content, ch_id2)

    if None in (pos1, pos2):
        return html_content

    # Ensure pos1 < pos2
    if pos1 > pos2:
        pos1, pos2 = pos2, pos1
        end1, end2 = end2, end1
        content1, content2 = content2, content1

    # Swap: content before pos1 + content2 + content between end1 and pos2 + content1 + content after end2
    before = html_content[:pos1]
    between = html_content[end1:pos2]
    after = html_content[end2:]

    return before + content2 + between + content1 + after

def renumber_all_ids(html_content, start=1):
    """Renumber all ch IDs sequentially."""
    ch_map = {}
    current = start

    def replacer(match):
        nonlocal current
        old_id = int(match.group(1))
        if old_id not in ch_map:
            ch_map[old_id] = current
            current += 1
        return f'id="ch{ch_map[old_id]}"'

    return re.sub(r'id="ch(\d+)"', replacer, html_content), len(ch_map)

def rebuild_toc_html(html_content):
    """Rebuild TOC based on current h2 chapters."""
    chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html_content)

    # Build simple TOC
    toc_items = []
    for ch_id, title in chapters:
        toc_items.append(f'      <li><a href="#{ch_id}">{title}</a></li>')

    toc_html = '<ol>\n' + '\n'.join(toc_items) + '\n    </ol>'

    # Replace existing TOC
    old_toc = re.search(r'<nav class="toc-panel" id="toc">(.*?)</nav>', html_content, re.DOTALL)
    if old_toc:
        new_toc = f'<nav class="toc-panel" id="toc">\n      <div class="toc-title">目 录</div>\n      {toc_html}\n    </nav>'
        html_content = html_content[:old_toc.start()] + new_toc + html_content[old_toc.end():]

    return html_content

def sync_html_md(html_path, md_path, new_html):
    """Update .html file and regenerate .md from it."""
    # Write HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    # Regenerate MD from HTML
    # Extract chapters portion and colophon
    main_start = new_html.find('<main class="content">')
    footer_start = new_html.find('<footer class="colophon"')
    hero_end = new_html.find('</header>', main_start)

    if hero_end >= 0 and footer_start >= 0:
        chapters_html = new_html[hero_end + len('</header>'):footer_start]
        colophon_end = new_html.find('</footer>', footer_start)
        colophon_html = new_html[footer_start:colophon_end + len('</footer>')] if colophon_end >= 0 else ''

        # Convert to MD
        chapters_md = html_to_md(chapters_html)
        colophon_clean = re.sub(r'<[^>]+>', '', colophon_html).strip()
        colophon_clean = '\n'.join(line.strip() for line in colophon_clean.split('\n') if line.strip())

        title_match = re.search(r'<title>(.+?)</title>', new_html)
        subtitle_match = re.search(r'<p class="no-indent"[^>]*>——([^<]+)</p>', new_html)
        title = title_match.group(1) if title_match else ''
        subtitle = subtitle_match.group(1) if subtitle_match else ''

        md_content = f'# {title}\n\n**{subtitle}**\n\n---\n\n{chapters_md}\n\n---\n\n{colophon_clean}\n'

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

def html_to_md(html_chapters):
    """Convert chapter HTML to markdown."""
    def inner_to_blockquote(m):
        inner = m.group(1)
        p_match = re.search(r'<p>(.*?)</p>', inner, re.DOTALL)
        if p_match:
            text = p_match.group(1).strip()
            lines = text.split('\n')
            quoted = '\n'.join('> ' + line.strip() for line in lines if line.strip())
            return '\n\n' + quoted + '\n\n'
        return ''

    md = re.sub(r'<div class="inner-monologue">(.*?)</div>', inner_to_blockquote, html_chapters, flags=re.DOTALL)

    def poem_to_blockquote(m):
        inner = m.group(1)
        lines = re.findall(r'<p>(.*?)</p>', inner)
        return '\n\n' + '\n'.join('> ' + l.strip() for l in lines if l.strip()) + '\n\n'

    md = re.sub(r'<div class="poem-block">(.*?)</div>', poem_to_blockquote, md, flags=re.DOTALL)
    md = re.sub(r'<h2 id="ch\d+">([^<]+)</h2>', r'\n## \1\n', md)
    md = re.sub(r'<h3[^>]*>([^<]+)</h3>', r'\n### \1\n', md)
    md = re.sub(r'<div class="divider">.*?</div>', '\n---\n', md)

    def p_replacer(m):
        inner = m.group(1)
        inner = re.sub(r'<br\s*/?>', '\n', inner)
        inner = re.sub(r'<[^>]+>', '', inner)
        return '\n' + inner.strip() + '\n'

    md = re.sub(r'<p(?:\s[^>]*)?>(.*?)</p>', p_replacer, md, flags=re.DOTALL)
    md = re.sub(r'<[^>]+>', '', md)

    # Clean whitespace
    lines = [l.strip() for l in md.split('\n')]
    md = '\n'.join(lines)
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    md = md.strip()

    return md


# ============================================================
# Book 3: 银杏城旧事 - Remove 9 chapters + swap 重阳/秋祭
# ============================================================
print("=== Processing Book 3: 《银杏城旧事》 ===")

b3_html = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
b3_md = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.md')

with open(b3_html, 'r', encoding='utf-8') as f:
    html3 = f.read()

# Show current chapters
chapters_before = get_chapter_map(html3)
print(f"  Before: {len(chapters_before)} chapters")
for ch_id, title in chapters_before:
    print(f"    {ch_id}: {title}")

# Remove chapters by 扩展 title
b3_remove = [
    '扩展五百五十一',  # 探芽 → keep in B2
    '扩展五百五十二',  # 迎燕 → keep in B2
    '扩展四百五十二',  # 补经 → keep in B2 (need to match: 扩展四百五十二)
    '扩展五百二十八',  # 拾叶 → keep in B2
    '扩展五百三十三',  # 围炉 → keep in B2
    '扩展五百四十五',  # 拥衾 → keep in B2
    '扩展五百三十二',  # 初雪 → keep in B2
    '扩展四十',        # 银杏食录 → keep in B5 (match: 扩展四十 but not 扩展四百)
    '扩展五十二',      # 洛城风物志 → keep in B5
]

# Need to be more precise: some titles like '扩展四十' might match '扩展四百'
# Use regex word boundary or exact match
b3_remove_exact = [
    '扩展五百五十一',
    '扩展五百五十二',
    '扩展四百五十二',
    '扩展五百二十八',
    '扩展五百三十三',
    '扩展五百四十五',
    '扩展五百三十二',
    # For these, need to avoid matching 扩展四百XX
]

# For B3, let me use a more targeted approach - match by current chapter ID
# Based on the grep results, I know the exact chapter IDs:
# ch3 = 扩展五百五十一 探芽
# ch4 = 扩展五百五十二 迎燕
# ch7 = 扩展四百五十二 补经
# ch14 = 扩展五百二十八 拾叶
# ch19 = 扩展五百三十三 围炉
# ch20 = 扩展五百四十五 拥衾
# ch21 = 扩展五百三十二 初雪
# ch23 = 扩展四十 银杏食录
# ch24 = 扩展五十二 洛城风物志

b3_remove_ids = ['ch3', 'ch4', 'ch7', 'ch14', 'ch19', 'ch20', 'ch21', 'ch23', 'ch24']

# Remove chapters (reverse order to avoid position shifts)
for ch_id in sorted(b3_remove_ids, key=lambda x: int(x[2:]), reverse=True):
    pos, end_pos, content = extract_chapter_content(html3, ch_id)
    if pos is not None:
        title_match = re.search(r'<h2 id="ch\d+">([^<]+)</h2>', content)
        title = title_match.group(1) if title_match else '?'
        html3 = html3[:pos] + html3[end_pos:]
        print(f"  Removed {ch_id}: {title}")

# Swap 重阳 and 秋祭 (after removal, need to find them by content)
# 重阳 is '扩展九十二' and 秋祭 is '扩展八十八'
# After removals, we need to find them in the current HTML
current_chapters = get_chapter_map(html3)
print(f"  After removal: {len(current_chapters)} chapters")

# Find 重阳 (扩展九十二) and 秋祭 (扩展八十八) in remaining chapters
chongyang_id = None
qiuji_id = None
for ch_id, title in current_chapters:
    if '重阳' in title:
        chongyang_id = ch_id
    if '秋祭' in title:
        qiuji_id = ch_id

if chongyang_id and qiuji_id:
    print(f"  Swapping {chongyang_id}(重阳) <-> {qiuji_id}(秋祭)")
    html3 = swap_chapters(html3, chongyang_id, qiuji_id)
else:
    print(f"  WARNING: Could not find 重阳({chongyang_id}) or 秋祭({qiuji_id})")

# Renumber
html3, num3 = renumber_all_ids(html3, 1)
print(f"  After renumber: {num3} chapters")

# Rebuild TOC
html3 = rebuild_toc_html(html3)

# Verify
final_chapters = get_chapter_map(html3)
print(f"  Final: {len(final_chapters)} chapters")

# Sync MD
sync_html_md(b3_html, b3_md, html3)
print(f"  Files synced: {b3_html} + {b3_md}")


# ============================================================
# Book 5: 银杏辞·附录卷 - Remove 3 chapters
# ============================================================
print("\n=== Processing Book 5: 《银杏辞·附录卷》 ===")

b5_html = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.html')
b5_md = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.md')

with open(b5_html, 'r', encoding='utf-8') as f:
    html5 = f.read()

chapters5_before = get_chapter_map(html5)
print(f"  Before: {len(chapters5_before)} chapters")

# Remove: ch4(洛城四季图), ch19(洛城风物志), ch27(外传·若华)
# Based on grep results:
# ch4 = 扩展三十七 洛城四季图
# ch19 = 扩展五十二 洛城风物志
# ch27 = 扩展六十 外传·若华
b5_remove_ids = ['ch4', 'ch19', 'ch27']

for ch_id in sorted(b5_remove_ids, key=lambda x: int(x[2:]), reverse=True):
    pos, end_pos, content = extract_chapter_content(html5, ch_id)
    if pos is not None:
        title_match = re.search(r'<h2 id="ch\d+">([^<]+)</h2>', content)
        title = title_match.group(1) if title_match else '?'
        html5 = html5[:pos] + html5[end_pos:]
        print(f"  Removed {ch_id}: {title}")

# Renumber
html5, num5 = renumber_all_ids(html5, 1)
print(f"  After renumber: {num5} chapters")

# Rebuild TOC
html5 = rebuild_toc_html(html5)

# Verify
final5 = get_chapter_map(html5)
print(f"  Final: {len(final5)} chapters")

# Sync MD
sync_html_md(b5_html, b5_md, html5)
print(f"  Files synced: {b5_html} + {b5_md}")


print("\n=== Round 1 Complete ===")
print(f"Book 3: {len(chapters_before)} → {len(final_chapters)} chapters")
print(f"Book 5: {len(chapters5_before)} → {len(final5)} chapters")
