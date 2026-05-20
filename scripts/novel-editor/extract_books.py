"""
Extract standalone books from the master 银杏辞 HTML file.
Book 1: 《银杏辞》 — ch1-ch19 (core narrative)
Book 2: 《清音寺居》 — ch447-ch598 (temple life)
"""
import re
import os

SOURCE = 'd:/ProgramWork/WriteBookProject/docs/2026-05-14/学习书/银杏辞-yinxing-ci-novel-2026-05-14.html'
OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

os.makedirs(OUTDIR, exist_ok=True)

with open(SOURCE, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# Extract the header (everything before <main class="content">)
# and the CSS style block
# ============================================================

head_end = content.find('<main class="content">')
header = content[:head_end]

# Extract the style block
style_start = content.find('<style>')
style_end = content.find('</style>') + len('</style>')
style_block = content[style_start:style_end]

# ============================================================
# Helper: extract chapter range
# ============================================================

def extract_chapters(content, start_ch, end_ch):
    """Extract content from chN to chM inclusive, return as string."""
    start_marker = f'<h2 id="ch{start_ch}">'
    start_pos = content.find(start_marker)
    if start_pos < 0:
        print(f"  ERROR: ch{start_ch} not found")
        return ""

    if end_ch:
        end_marker = f'<h2 id="ch{end_ch+1}">'
        end_pos = content.find(end_marker, start_pos)
        if end_pos < 0:
            # Try finding <footer or end of main
            end_pos = content.find('<footer', start_pos)
            if end_pos < 0:
                end_pos = content.find('</main>', start_pos)
    else:
        # Go to end of main content (before footer or revision log)
        end_pos = content.find('<footer', start_pos)
        if end_pos < 0:
            end_pos = content.find('<div style="max-width:720px;margin:40px', start_pos)
        if end_pos < 0:
            end_pos = len(content)

    return content[start_pos:end_pos]


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


# ============================================================
# BOOK 1: 《银杏辞》 — ch1-ch19
# ============================================================
print("=== Book 1: 《银杏辞》 ===")

# Extract ch1-ch19
ch1_to_19 = extract_chapters(content, 1, 19)

# Find the end of ch19 尾声
weisheng_end = ch1_to_19.rfind('</p>')
# Add 赵桓 fate sentence before the final closing
# Find a good insertion point near the end of ch19

# ch19 ends with the poetic closing about ginkgo leaves
# Let's find the text we need to insert near
target = '银杏叶会年年黄。故事会一代一代讲下去'
insert_pos = ch1_to_19.find(target)
if insert_pos > 0:
    insert_pos = ch1_to_19.find('</p>', insert_pos)
    fate_text = '\n\n    <p>同年，景宁二十二年秋，赵桓病逝于宫中。新帝即位，大赦天下。银杏冤案终于等来了迟到的平反——那些被株连的家族后人、散落天涯的幸存者，陆续回到了洛城。银杏书院重新开学的那一天，陆明远在门前的古银杏树上挂了一串风铃。风吹铃响，像是在给所有没能等到这一天的人报信。</p>\n'
    ch1_to_19 = ch1_to_19[:insert_pos] + fate_text + ch1_to_19[insert_pos:]
    print("  Added 赵桓 fate paragraph")
else:
    print("  WARNING: Could not find insertion point for 赵桓 fate")

# Renumber chapter IDs — ch1-ch19 stay the same, just remove extraneous content
# Build TOC
toc1 = [
    ("第一卷 杏花春雨少年时", "ch1"),
    ("第二卷 十里长亭霜满天", "ch5"),
    ("第三卷 深宫犹闻落叶声", "ch9"),
    ("第四卷 月隐剑折为红颜", "ch13"),
    ("第五卷 三秋叶落见君来", "ch16"),
]

colophon1 = f'''<p><strong>《银杏辞》</strong></p>
      <p>一部唯美古典爱情中篇小说</p>
      <p>全书五卷 · 19章 · 完整故事</p>
      <p>写作风格：婉约派诗词 + 青春文学 + 红楼梦叙事</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列提取）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第一部——核心正传</p>
      <p>系列还包括：《清音寺居》《银杏城旧事》《银杏人物志》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">银杏辞 · 三秋叶落 · 与君同看雪花轻</p>'''

html1 = build_standalone_html('银杏辞', '三秋叶落，与君同看雪花轻', ch1_to_19, toc1, colophon1)
outpath1 = os.path.join(OUTDIR, 'yinxing-ci-novel-2026-05-15.html')
with open(outpath1, 'w', encoding='utf-8') as f:
    f.write(html1)
print(f"  Written: {outpath1}")
print(f"  Size: {len(html1)} chars")


# ============================================================
# BOOK 2: 《清音寺居》 — ch447-ch598 (temple life)
# ============================================================
print("\n=== Book 2: 《清音寺居》 ===")

# Find the actual start — ch447 = 扩展四百二十八 磨墨
ch447_pos = content.find('<h2 id="ch447">')
if ch447_pos < 0:
    print("  ERROR: ch447 not found!")
else:
    # Go from ch447 to end of chapter content (before footer/revision log)
    footer_pos = content.find('<footer class="colophon"', ch447_pos)
    ch447_to_end = content[ch447_pos:footer_pos]

    # Clean up: remove the 修订日志 div if present
    rev_log_pos = ch447_to_end.find('<div style="max-width:720px;margin:40px')
    if rev_log_pos > 0:
        ch447_to_end = ch447_to_end[:rev_log_pos]

    # Find the postscript (后记) if present
    postscript_pos = content.find('<h2 id="houji">')
    if postscript_pos > 0 and postscript_pos > ch447_pos and postscript_pos < footer_pos:
        # Include it
        pass

    # Renumber chapter IDs: ch447→ch1, ch448→ch2, ..., ch598→ch152
    def renumber_id(match):
        num = int(match.group(1))
        new_num = num - 446  # ch447 becomes ch1
        return f'id="ch{new_num}"'

    ch447_to_end = re.sub(r'id="ch(\d+)"', renumber_id, ch447_to_end)

    # Renumber chapter titles: 扩展四百二十八 → 寺居一, etc.
    # Keep original titles as-is for now, just renumber the IDs
    # The h2 text can stay as is

    toc2 = [
        ("卷上：寺居日常（一至一一九）", "ch1"),
        ("卷下：山中岁时（一二〇至一七一）", "ch120"),
    ]

    colophon2 = f'''<p><strong>《清音寺居》</strong></p>
      <p>一部禅意散文集 · 寺庙生活志</p>
      <p>全书二卷 · 171章</p>
      <p>写作风格：极简禅意 + 日常叙事</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列扩展篇章提取）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第二部</p>
      <p>主人公：寂声、老孙、沈秋白、陆明远</p>
      <p>系列还包括：《银杏辞》《银杏城旧事》《银杏人物志》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">寺居 · 山中无历日 · 寒尽不知年</p>'''

    html2 = build_standalone_html('清音寺居', '山中无历日，寒尽不知年', ch447_to_end, toc2, colophon2)
    outpath2 = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
    with open(outpath2, 'w', encoding='utf-8') as f:
        f.write(html2)
    print(f"  Written: {outpath2}")
    print(f"  Size: {len(html2)} chars")

print("\n=== Done with Books 1 & 2 ===")
