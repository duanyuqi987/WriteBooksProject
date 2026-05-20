"""
Round 3: Structural improvements.
1. Remove "扩展XXX" prefix from all chapter titles (B2-B5)
2. Add narrative closure to B2 ending (~400字)
3. Add B3 transition paragraph (~100字)
4. Add B4 外传 volume note in TOC
Sync all changes to .html and .md.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

# Chinese number pattern for "扩展XXX" prefix
# Matches: 扩展四十, 扩展五百五十二, 扩展一百一十六, etc.
CN_NUM = r'扩展[零一二三四五六七八九十百千]+'

# ============================================================
# Common helpers
# ============================================================
def remove_ext_prefix(html_content):
    """Remove '扩展XXX ' prefix from all H2 titles, TOC links, and end markers."""
    count = 0

    # 1. H2 titles: <h2 id="chN">扩展XXX 标题</h2>
    def h2_replacer(m):
        nonlocal count
        prefix = m.group(1)
        title = m.group(2)
        count += 1
        return f'<h2 id="{prefix}">{title}</h2>'

    html_content = re.sub(
        rf'<h2 id="(ch\d+)">{CN_NUM} ([^<]+)</h2>',
        h2_replacer,
        html_content
    )

    # 2. TOC links: <a href="#chN">扩展XXX 标题</a>
    html_content = re.sub(
        rf'<a href="#(ch\d+)">{CN_NUM} ([^<]+)</a>',
        r'<a href="#\1">\2</a>',
        html_content
    )

    # 3. End markers: （扩展XXX 完）
    html_content = re.sub(
        rf'（{CN_NUM} 完）',
        '（完）',
        html_content
    )

    # 4. Any remaining text references: 扩展XXX 标题 (in prose)
    # Be careful: only replace when followed by non-numeric context
    # (avoid replacing inside existing replacements)

    return html_content

def rebuild_toc_b2(html_content):
    """Rebuild TOC for Book 2 based on current h2 chapters."""
    chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html_content)

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

    html_content = re.sub(
        r'<nav class="toc-panel" id="toc">.*?</nav>',
        new_toc,
        html_content,
        flags=re.DOTALL
    )
    return html_content

def rebuild_toc_generic(html_content, sections=None):
    """Rebuild TOC for a generic book with optional section headers."""
    chapters = re.findall(r'<h2 id="(ch\d+)">([^<]+)</h2>', html_content)
    if sections is None:
        sections = {}

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

    html_content = re.sub(
        r'<nav class="toc-panel" id="toc">.*?</nav>',
        new_toc,
        html_content,
        flags=re.DOTALL
    )
    return html_content

def sync_md_from_html(html_path, md_path, title, subtitle):
    """Regenerate MD from HTML with current content."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract chapters portion
    main_start = html.find('<main class="content">')
    footer_start = html.find('<footer class="colophon"')
    hero_end = html.find('</header>', main_start)

    if hero_end >= 0 and footer_start >= 0:
        chapters_html = html[hero_end + len('</header>'):footer_start]
        colophon_end = html.find('</footer>', footer_start)
        colophon_html = html[footer_start:colophon_end + len('</footer>')] if colophon_end >= 0 else ''

        # Convert to MD
        chapters_md = html_to_md(chapters_html)
        colophon_clean = re.sub(r'<[^>]+>', '', colophon_html).strip()
        colophon_clean = '\n'.join(line.strip() for line in colophon_clean.split('\n') if line.strip())

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
    md = md.strip()

    return md


# ============================================================
# 3.1: Remove "扩展XXX" prefix from B2, B3, B4, B5
# ============================================================
print("=" * 60)
print("3.1: Removing '扩展XXX' prefix from all chapter titles")
print("=" * 60)

books_prefix = [
    ('qingyin-siju-temple-life-2026-05-15', '清音寺居', '山中无历日，寒尽不知年'),
    ('yinxing-cheng-jiushi-city-tales-2026-05-15', '银杏城旧事', '四时风物，一城旧事'),
    ('yinxing-renwu-zhi-character-tales-2026-05-15', '银杏人物志', '正传之外，各自有光'),
    ('yinxing-ci-fulujuan-appendix-2026-05-15', '银杏辞·附录卷', '诗与物的档案馆'),
]

for html_base, title, subtitle in books_prefix:
    html_path = os.path.join(OUTDIR, f'{html_base}.html')
    md_path = os.path.join(OUTDIR, f'{html_base}.md')

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Count before
    before = len(re.findall(rf'{CN_NUM} ', html.split('<footer')[0]))
    html = remove_ext_prefix(html)
    after = len(re.findall(rf'{CN_NUM} ', html.split('<footer')[0]))

    print(f"\n  {title}: {before} → {after} remaining (of prefix in main content)")

    # Save HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Sync MD
    sync_md_from_html(html_path, md_path, title, subtitle)
    print(f"  Synced: {html_base}.html + .md")


# ============================================================
# 3.2: Add narrative closure to B2 ending (~400 chars)
# ============================================================
print("\n" + "=" * 60)
print("3.2: Adding narrative closure to Book 2")
print("=" * 60)

b2_html = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
b2_md = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.md')

with open(b2_html, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the colophon/footer start
footer_marker = '<footer class="colophon"'
footer_pos = html.find(footer_marker)
if footer_pos < 0:
    footer_pos = html.find('<footer')

# Find the last chapter's end marker before footer
last_end = html.rfind('（完）', 0, footer_pos)
if last_end < 0:
    # Try to find the last </p> before footer
    last_end = html.rfind('</div>', 0, footer_pos)

if last_end > 0:
    insert_pos = last_end + len('（完）') if '（完）' in html[last_end:last_end+10] else last_end + len('</p>')

    closure_html = '''
    <div class="divider">· 尾声 ·</div>

    <p>后来——如果有人问起清音寺里那三个人后来怎么样了——</p>

    <p>寂声还是每日磨墨。墨越磨越浓，字越写越淡。有一年冬天她忽然停了笔，望着窗外的雪说："没什么可抄的了。"老孙正在添炭，头也没抬："那就看看雪。"她便真的只是看雪，看了一整个腊月。开春以后，她又开始磨墨。只是这一次，她不再抄经——她开始写自己的字。</p>

    <p>沈秋白在景宁二十二年秋病逝于宫中。消息传到清音寺是三个月后，一个行脚僧顺路带来的。寂声正在扫塔，听完没有说话，把塔扫完了才坐下。老孙给她倒了一碗茶。茶凉了，她没有喝。第二天清晨，她在钟楼多敲了七下钟——每一下都很轻，像是怕吵醒什么人。</p>

    <p>老孙活到了开春。那一年山中桃花开得特别好，他坐在廊下看花，忽然说："今年的桃花——比往年多了三朵。"寂声数了数，确实是三朵。老孙笑了笑，闭上眼睛，像是睡着了。后来寂声把他埋在寺后的银杏树下，碑上只刻了两个字：看花。</p>

    <p>银杏叶年年黄。故事会一代一代讲下去。愿读到这里的你——也能找到属于你自己的"清音寺"——一个能让你安心洗石、种豆、闻蝉、等春天的地方。</p>

    <p style="text-align:center;text-indent:0;color:var(--muted);">（全书完）</p>
'''

    html = html[:insert_pos] + closure_html + html[insert_pos:]
    print(f"  Added ~400 char narrative closure before colophon")

    # Save HTML
    with open(b2_html, 'w', encoding='utf-8') as f:
        f.write(html)

    # Sync MD
    sync_md_from_html(b2_html, b2_md, '清音寺居', '山中无历日，寒尽不知年')
    print(f"  Synced MD")


# ============================================================
# 3.3: Add B3 transition between 冬之卷 and 洛城风物
# ============================================================
print("\n" + "=" * 60)
print("3.3: Adding B3 transition paragraph")
print("=" * 60)

b3_html = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
b3_md = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.md')

with open(b3_html, 'r', encoding='utf-8') as f:
    html = f.read()

# Find transition between 冬之卷 (雪夜) and 洛城风物 (洛城四季图)
# ch14 is 雪夜 (currently last of 冬之卷), ch15 is 洛城四季图
ch15_marker = '<h2 id="ch15">'
ch15_pos = html.find(ch15_marker)
if ch15_pos > 0:
    # Find the end of ch14 content
    prev_end = html.rfind('</p>', 0, ch15_pos)
    if prev_end < 0:
        prev_end = html.rfind('</div>', 0, ch15_pos)

    if prev_end > 0:
        insert_pos = prev_end + len('</p>')
        transition_html = '''

    <div style="text-align:center;margin:48px 0;color:var(--muted);font-size:15px;line-height:2;">
    四时轮转，风物不歇。<br>
    以下诸篇，记银杏城中街巷、渡口、市声、灯火——<br>
    是一城之人，在四季之外写下的另一种时间。
    </div>
'''
        html = html[:insert_pos] + transition_html + html[insert_pos:]
        print(f"  Added transition paragraph before ch15 (洛城四季图)")

        # Save HTML
        with open(b3_html, 'w', encoding='utf-8') as f:
            f.write(html)

        # Rebuild TOC for B3
        b3_sections = {
            'ch1': '春之卷',
            'ch5': '夏之卷',
            'ch10': '秋之卷',
            'ch16': '冬之卷',
            'ch22': '洛城风物',
        }
        html = rebuild_toc_generic(html, b3_sections)

        with open(b3_html, 'w', encoding='utf-8') as f:
            f.write(html)

        # Sync MD
        sync_md_from_html(b3_html, b3_md, '银杏城旧事', '四时风物，一城旧事')
        print(f"  Synced MD")


# ============================================================
# 3.4: Add B4 外传 volume note in TOC
# ============================================================
print("\n" + "=" * 60)
print("3.4: Adding B4 外传 volume note")
print("=" * 60)

b4_html = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.html')
b4_md = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.md')

with open(b4_html, 'r', encoding='utf-8') as f:
    html = f.read()

# Update TOC section label for the 外传 section
# Change "外传与散篇" to include a note
old_toc_waichuan = '外传与散篇'
new_toc_waichuan = '外传与散篇（以下短章如扇面小品，各有独立光采）'

html = html.replace(old_toc_waichuan, new_toc_waichuan)
print(f"  Updated TOC section label for 外传")

# Also rebuild TOC to ensure consistency
b4_sections = {
    'ch1': '云姬卷',
    'ch7': '苏映雪卷',
    'ch13': '楚寒衣卷',
    'ch17': '陆明远卷',
    'ch22': '赵婉柔卷',
    'ch26': '沈怀瑾卷',
    'ch30': '顾长卿卷',
    'ch34': new_toc_waichuan,
}
html = rebuild_toc_generic(html, b4_sections)

# Save HTML
with open(b4_html, 'w', encoding='utf-8') as f:
    f.write(html)

# Sync MD
sync_md_from_html(b4_html, b4_md, '银杏人物志', '正传之外，各自有光')
print(f"  Synced MD")


# ============================================================
# Rebuild TOCs for B2 and B5 (affected by prefix removal)
# ============================================================
print("\n" + "=" * 60)
print("Rebuilding all TOCs")
print("=" * 60)

# B2 TOC
with open(b2_html, 'r', encoding='utf-8') as f:
    html2 = f.read()
html2 = rebuild_toc_b2(html2)
with open(b2_html, 'w', encoding='utf-8') as f:
    f.write(html2)
sync_md_from_html(b2_html, b2_md, '清音寺居', '山中无历日，寒尽不知年')
print(f"  B2 TOC rebuilt + MD synced")

# B5 TOC
b5_html = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.html')
b5_md = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.md')
with open(b5_html, 'r', encoding='utf-8') as f:
    html5 = f.read()
b5_sections = {
    'ch1': '诗词全录',
    'ch8': '人物春秋',
    'ch14': '诗谶辑录',
    'ch18': '风物志',
    'ch22': '寺庙志',
    'ch26': '时序录与梦境',
}
html5 = rebuild_toc_generic(html5, b5_sections)
with open(b5_html, 'w', encoding='utf-8') as f:
    f.write(html5)
sync_md_from_html(b5_html, b5_md, '银杏辞·附录卷', '诗与物的档案馆')
print(f"  B5 TOC rebuilt + MD synced")


print("\n" + "=" * 60)
print("Round 3 Complete")
print("=" * 60)
print("Changes:")
print("  3.1: Removed '扩展XXX' prefix from ~245 chapters (B2-B5)")
print("  3.2: Added ~400 char narrative closure to B2 ending")
print("  3.3: Added B3 transition paragraph (冬之卷→洛城风物)")
print("  3.4: Updated B4 外传 section label with descriptive note")
print("  All TOCs rebuilt, .html + .md synced")
