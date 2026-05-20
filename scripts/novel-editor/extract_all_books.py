"""
Extract all 5 standalone books from the fixed master file.
Generate both .html and .md files for each book.
"""
import re
import os

MASTER = 'd:/ProgramWork/WriteBookProject/docs/2026-05-14/学习书/银杏辞-yinxing-ci-novel-2026-05-14.html'
OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

os.makedirs(OUTDIR, exist_ok=True)

with open(MASTER, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract style block
style_start = content.find('<style>')
style_end = content.find('</style>') + len('</style>')
style_block = content[style_start:style_end]


def extract_chapter_range(content, ch_ids):
    """Extract chapters by ch IDs in order."""
    result = ''
    for ch_id in ch_ids:
        marker = f'<h2 id="ch{ch_id}">'
        pos = content.find(marker)
        if pos < 0:
            print(f'  WARNING: ch{ch_id} not found')
            continue

        next_h2 = content.find('<h2 id="ch', pos + len(marker))
        if next_h2 < 0:
            next_h2 = content.find('<footer', pos)
        if next_h2 < 0:
            next_h2 = content.find('<div class="divider"', pos)
        if next_h2 < 0:
            next_h2 = content.find('</main>', pos)
        if next_h2 < 0:
            next_h2 = len(content)

        chapter_content = content[pos:next_h2]
        result += chapter_content + '\n\n'

    return result


def renumber_chapters(html_text, start_id=1):
    """Renumber all ch IDs sequentially."""
    ch_map = {}
    current_new = start_id

    def replacer(match):
        nonlocal current_new
        old_id = int(match.group(1))
        if old_id not in ch_map:
            ch_map[old_id] = current_new
            current_new += 1
        return f'id="ch{ch_map[old_id]}"'

    return re.sub(r'id="ch(\d+)"', replacer, html_text), len(ch_map)


def html_to_markdown(html_chapters):
    """Convert chapter HTML to markdown format."""
    md = html_chapters

    # Convert <h2 id="chN">title</h2> to ## title
    md = re.sub(r'<h2 id="ch\d+">([^<]+)</h2>', r'## \1\n', md)

    # Convert <h3> to ###
    md = re.sub(r'<h3[^>]*>([^<]+)</h3>', r'### \1\n', md)

    # Convert <div class="inner-monologue">\n<p>...</p>\n</div> to blockquote
    def inner_to_blockquote(m):
        inner_content = m.group(1)
        # Extract <p> content
        p_match = re.search(r'<p>(.*?)</p>', inner_content, re.DOTALL)
        if p_match:
            text = p_match.group(1)
            # Add > prefix to each line
            lines = text.split('\n')
            quoted = '\n'.join('> ' + line.strip() for line in lines if line.strip())
            return '\n' + quoted + '\n'
        return ''

    md = re.sub(r'<div class="inner-monologue">(.*?)</div>', inner_to_blockquote, md, flags=re.DOTALL)

    # Convert <div class="poem-block"> to blockquote (poetry)
    def poem_to_blockquote(m):
        inner = m.group(1)
        # Extract all <p> content
        poem_lines = re.findall(r'<p>(.*?)</p>', inner)
        quoted = '\n'.join('> ' + line for line in poem_lines)
        return '\n' + quoted + '\n'

    md = re.sub(r'<div class="poem-block">(.*?)</div>', poem_to_blockquote, md, flags=re.DOTALL)

    # Convert <div class="divider"> to ---
    md = re.sub(r'<div class="divider">.*?</div>', '\n---\n', md)

    # Convert <p style="text-align:center;...">（... 完）</p> to centered marker
    md = re.sub(r'<p style="text-align:center;text-indent:0;color:var\(--muted\);">(.*?)</p>',
                r'\n<p align="center"><em>\1</em></p>\n', md)

    # Convert <p> to plain paragraphs
    md = re.sub(r'<p(?:\s[^>]*)?>', '\n', md)
    md = re.sub(r'</p>', '\n', md)

    # Convert <em> and <strong>
    md = re.sub(r'<em>([^<]*)</em>', r'*\1*', md)
    md = re.sub(r'<strong>([^<]*)</strong>', r'**\1**', md)

    # Convert <br> to newline
    md = re.sub(r'<br\s*/?>', '\n', md)

    # Remove any remaining HTML tags
    md = re.sub(r'<[^>]+>', '', md)

    # Clean up excessive blank lines
    md = re.sub(r'\n{4,}', '\n\n\n', md)

    return md


def build_standalone_html(title, subtitle, chapters_html, toc_items, colophon_text, word_count=""):
    """Build a complete standalone HTML book."""
    toc_html = '<ol>\n'
    for label, anchor in toc_items:
        toc_html += f'      <li><a href="#{anchor}">{label}</a></li>\n'
    toc_html += '    </ol>'

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="doc-version" content="v1.0">
  <meta name="last-update" content="2026-05-15">
  <meta name="word-count" content="{word_count}">
  <meta name="series" content="《银杏辞》系列">
  <title>{title}</title>
  {style_block}
</head>
<body>
  <div class="layout">
    <nav class="toc-panel" id="toc">
      <div class="toc-title">目 录</div>
      {toc_html}
    </nav>
    <main class="content">
      <header class="hero">
        <h1>{title}</h1>
        <p class="no-indent" style="text-align:center;color:var(--muted);">——{subtitle}</p>
      </header>

{chapters_html}

      <footer class="colophon" style="max-width:720px;margin:0 auto;padding:24px 56px 48px;">
        {colophon_text}
      </footer>
    </main>
  </div>
</body>
</html>'''
    return html


def build_markdown(title, subtitle, chapters_md, colophon_text, word_count=""):
    """Build a markdown version of the book."""
    # Clean colophon of HTML tags
    colophon_clean = re.sub(r'<[^>]+>', '', colophon_text)
    colophon_clean = re.sub(r'\n\s+', '\n', colophon_clean)

    md = f'''# {title}

**{subtitle}**

---

{chapters_md}

---

{colophon_clean}
'''
    return md


def count_cjk(html_text):
    """Estimate CJK character count."""
    cjk = len(re.findall(r'[一-鿿㐀-䶿]', html_text))
    return cjk


# ============================================================
# BOOK 1: 《银杏辞》 — ch1-ch19
# ============================================================
print("=== Book 1: 《银杏辞》 ===")

ch1_to_19 = extract_chapter_range(content, list(range(1, 20)))

# Add 赵桓 fate sentence near end of ch19 尾声
target = '银杏叶会年年黄。故事会一代一代讲下去'
insert_pos = ch1_to_19.find(target)
if insert_pos > 0:
    insert_pos = ch1_to_19.find('</p>', insert_pos)
    fate_text = '\n\n    <p>景宁二十二年秋，赵桓病逝于宫中。新帝即位，大赦天下。银杏冤案终于等来了迟到的平反——那些被株连的家族后人、散落天涯的幸存者，陆续回到了洛城。银杏书院重新开学的那一天，陆明远在门前的古银杏树上挂了一串风铃。风吹铃响，像是在给所有没能等到这一天的人报信。</p>\n'
    ch1_to_19 = ch1_to_19[:insert_pos] + fate_text + ch1_to_19[insert_pos:]
    print("  Added 赵桓 fate paragraph")

toc1 = [
    ("第一卷 杏花春雨少年时", "ch1"),
    ("第二卷 十里长亭霜满天", "ch5"),
    ("第三卷 深宫犹闻落叶声", "ch9"),
    ("第四卷 月隐剑折为红颜", "ch13"),
    ("第五卷 三秋叶落见君来", "ch16"),
]

word_count1 = count_cjk(ch1_to_19)
colophon1 = f'''<p><strong>《银杏辞》</strong></p>
      <p>一部唯美古典爱情中篇小说</p>
      <p>全书五卷 · 19章 · 完整故事</p>
      <p>写作风格：婉约派诗词 + 青春文学 + 红楼梦叙事</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列提取）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第一部——核心正传</p>
      <p>系列还包括：《清音寺居》《银杏城旧事》《银杏人物志》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">银杏辞 · 三秋叶落 · 与君同看雪花轻</p>'''

html1 = build_standalone_html('银杏辞', '三秋叶落，与君同看雪花轻', ch1_to_19, toc1, colophon1, str(word_count1))

# Generate HTML
out_html1 = os.path.join(OUTDIR, 'yinxing-ci-novel-2026-05-15.html')
with open(out_html1, 'w', encoding='utf-8') as f:
    f.write(html1)
print(f"  HTML: {out_html1} ({len(html1):,} chars, {word_count1} CJK chars)")

# Generate MD
chapters_md1 = html_to_markdown(ch1_to_19)
md1 = build_markdown('银杏辞', '三秋叶落，与君同看雪花轻', chapters_md1, colophon1, str(word_count1))
out_md1 = os.path.join(OUTDIR, 'yinxing-ci-novel-2026-05-15.md')
with open(out_md1, 'w', encoding='utf-8') as f:
    f.write(md1)
print(f"  MD:   {out_md1} ({len(md1):,} chars)")


# ============================================================
# BOOK 2: 《清音寺居》 — ch447-ch598
# ============================================================
print("\n=== Book 2: 《清音寺居》 ===")

book2_chapters = list(range(447, 599))  # ch447-ch598
chapters_html2 = extract_chapter_range(content, book2_chapters)
chapters_html2, num2 = renumber_chapters(chapters_html2, 1)
print(f"  Extracted {num2} chapters")

toc2 = [
    ("卷上：寺居日常（一至一一九）", "ch1"),
    ("卷下：山中岁时（一二〇至一五二）", "ch120"),
]

word_count2 = count_cjk(chapters_html2)
colophon2 = f'''<p><strong>《清音寺居》</strong></p>
      <p>一部禅意散文集 · 寺庙生活志</p>
      <p>全书二卷 · {num2}章</p>
      <p>写作风格：极简禅意 + 日常叙事</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列扩展篇章提取）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第二部</p>
      <p>主人公：寂声、老孙、沈秋白</p>
      <p>系列还包括：《银杏辞》《银杏城旧事》《银杏人物志》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">寺居 · 山中无历日 · 寒尽不知年</p>'''

html2 = build_standalone_html('清音寺居', '山中无历日，寒尽不知年', chapters_html2, toc2, colophon2, str(word_count2))
out_html2 = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
with open(out_html2, 'w', encoding='utf-8') as f:
    f.write(html2)
print(f"  HTML: {out_html2} ({len(html2):,} chars, {word_count2} CJK chars)")

chapters_md2 = html_to_markdown(chapters_html2)
md2 = build_markdown('清音寺居', '山中无历日，寒尽不知年', chapters_md2, colophon2, str(word_count2))
out_md2 = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.md')
with open(out_md2, 'w', encoding='utf-8') as f:
    f.write(md2)
print(f"  MD:   {out_md2} ({len(md2):,} chars)")


# ============================================================
# BOOK 3: 《银杏城旧事》
# ============================================================
print("\n=== Book 3: 《银杏城旧事》 ===")

book3_chapters = [
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

chapters_html3 = extract_chapter_range(content, book3_chapters)
chapters_html3, num3 = renumber_chapters(chapters_html3, 1)
print(f"  Extracted {num3} chapters")

toc3 = [
    ("春之卷", "ch1"),
    ("夏之卷", "ch5"),
    ("秋之卷", "ch10"),
    ("冬之卷", "ch16"),
    ("洛城风物", "ch22"),
]

word_count3 = count_cjk(chapters_html3)
colophon3 = f'''<p><strong>《银杏城旧事》</strong></p>
      <p>一部风物民俗散文集 · 洛城市井生活志</p>
      <p>全书五卷 · {num3}章</p>
      <p>写作风格：节俗叙事 + 风物志笔法</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列扩展篇章精选）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第三部</p>
      <p>系列还包括：《银杏辞》《清音寺居》《银杏人物志》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">洛城 · 四时风物 · 一城旧事</p>'''

html3 = build_standalone_html('银杏城旧事', '四时风物，一城旧事', chapters_html3, toc3, colophon3, str(word_count3))
out_html3 = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
with open(out_html3, 'w', encoding='utf-8') as f:
    f.write(html3)
print(f"  HTML: {out_html3} ({len(html3):,} chars, {word_count3} CJK chars)")

chapters_md3 = html_to_markdown(chapters_html3)
md3 = build_markdown('银杏城旧事', '四时风物，一城旧事', chapters_md3, colophon3, str(word_count3))
out_md3 = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.md')
with open(out_md3, 'w', encoding='utf-8') as f:
    f.write(md3)
print(f"  MD:   {out_md3} ({len(md3):,} chars)")


# ============================================================
# BOOK 4: 《银杏人物志》
# ============================================================
print("\n=== Book 4: 《银杏人物志》 ===")

book4_chapters = list(range(20, 53))  # ch20-ch52
scattered_char = [79, 86, 97, 98, 99, 100, 101, 102, 103]
book4_chapters.extend(scattered_char)

chapters_html4 = extract_chapter_range(content, book4_chapters)
chapters_html4, num4 = renumber_chapters(chapters_html4, 1)
print(f"  Extracted {num4} chapters")

toc4 = [("人物列传（一至四十二）", "ch1")]

word_count4 = count_cjk(chapters_html4)
colophon4 = f'''<p><strong>《银杏人物志》</strong></p>
      <p>一部人物短篇集 · 配角的独立人生</p>
      <p>全书 · {num4}章</p>
      <p>写作风格：人物传记 + 短篇叙事</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列扩展篇章精选）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第四部</p>
      <p>传主：云姬、苏映雪、楚寒衣、陆明远、赵婉柔、沈怀瑾、顾长卿、小蝶、明远和尚、沈若兮 等</p>
      <p>系列还包括：《银杏辞》《清音寺居》《银杏城旧事》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">人物 · 正传之外 · 各自有光</p>'''

html4 = build_standalone_html('银杏人物志', '正传之外，各自有光', chapters_html4, toc4, colophon4, str(word_count4))
out_html4 = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.html')
with open(out_html4, 'w', encoding='utf-8') as f:
    f.write(html4)
print(f"  HTML: {out_html4} ({len(html4):,} chars, {word_count4} CJK chars)")

chapters_md4 = html_to_markdown(chapters_html4)
md4 = build_markdown('银杏人物志', '正传之外，各自有光', chapters_md4, colophon4, str(word_count4))
out_md4 = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.md')
with open(out_md4, 'w', encoding='utf-8') as f:
    f.write(md4)
print(f"  MD:   {out_md4} ({len(md4):,} chars)")


# ============================================================
# BOOK 5: 《银杏辞·附录卷》
# ============================================================
print("\n=== Book 5: 《银杏辞·附录卷》 ===")

book5_chapters = list(range(53, 85))  # ch53-ch84
chapters_html5 = extract_chapter_range(content, book5_chapters)
chapters_html5, num5 = renumber_chapters(chapters_html5, 1)
print(f"  Extracted {num5} chapters")

toc5 = [("设定资料汇编", "ch1")]

word_count5 = count_cjk(chapters_html5)
colophon5 = f'''<p><strong>《银杏辞·附录卷》</strong></p>
      <p>设定资料集 · 参考附录</p>
      <p>{num5}章</p>
      <p>内容：诗词全录 · 人物春秋 · 诗谶辑录 · 风物志 · 寺庙志 · 梦境录 · 时序录 · 对白录 等</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列汇编）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第五部（资料卷）</p>
      <p>系列还包括：《银杏辞》《清音寺居》《银杏城旧事》《银杏人物志》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">附录 · 诗与物的档案馆</p>'''

html5 = build_standalone_html('银杏辞·附录卷', '诗与物的档案馆', chapters_html5, toc5, colophon5, str(word_count5))
out_html5 = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.html')
with open(out_html5, 'w', encoding='utf-8') as f:
    f.write(html5)
print(f"  HTML: {out_html5} ({len(html5):,} chars, {word_count5} CJK chars)")

chapters_md5 = html_to_markdown(chapters_html5)
md5 = build_markdown('银杏辞·附录卷', '诗与物的档案馆', chapters_md5, colophon5, str(word_count5))
out_md5 = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.md')
with open(out_md5, 'w', encoding='utf-8') as f:
    f.write(md5)
print(f"  MD:   {out_md5} ({len(md5):,} chars)")


print("\n=== All 5 Books Extracted (HTML + MD) ===")

# Summary
print("\n--- Summary ---")
for name, html_file, md_file, wc in [
    ('《银杏辞》', out_html1, out_md1, word_count1),
    ('《清音寺居》', out_html2, out_md2, word_count2),
    ('《银杏城旧事》', out_html3, out_md3, word_count3),
    ('《银杏人物志》', out_html4, out_md4, word_count4),
    ('《银杏辞·附录卷》', out_html5, out_md5, word_count5),
]:
    html_size = os.path.getsize(html_file)
    md_size = os.path.getsize(md_file)
    print(f"{name}: {wc:,} CJK chars | HTML: {html_size:,}B | MD: {md_size:,}B")
