"""
Extract Books 3, 4, 5 from the master 银杏辞 HTML file.
Book 3: 《银杏城旧事》 — selected festival/city-life chapters
Book 4: 《银杏人物志》 — character side stories (ch20-ch52 + scattered)
Book 5: 《银杏辞·附录卷》 — reference material (ch53-ch84)
"""
import re
import os

SOURCE = 'd:/ProgramWork/WriteBookProject/docs/2026-05-14/学习书/银杏辞-yinxing-ci-novel-2026-05-14.html'
OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

os.makedirs(OUTDIR, exist_ok=True)

with open(SOURCE, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract style block
style_start = content.find('<style>')
style_end = content.find('</style>') + len('</style>')
style_block = content[style_start:style_end]

def extract_chapter_range(content, ch_ids):
    """Extract chapters by their ch IDs, concatenated in order."""
    result = ''
    for ch_id in ch_ids:
        marker = f'<h2 id="ch{ch_id}">'
        pos = content.find(marker)
        if pos < 0:
            print(f'  WARNING: ch{ch_id} not found')
            continue

        # Find next h2 or end marker
        next_h2 = content.find('<h2 id="ch', pos + len(marker))
        if next_h2 < 0:
            next_h2 = content.find('<footer', pos)
        if next_h2 < 0:
            next_h2 = content.find('<div style="max-width:720px;margin:40px', pos)
        if next_h2 < 0:
            next_h2 = len(content)

        chapter_content = content[pos:next_h2]
        # Remove trailing end markers that might bleed in
        # But keep the chapter content intact
        result += chapter_content + '\n\n'

    return result


def renumber_chapters(html_text, start_id=1):
    """Renumber all ch IDs sequentially starting from start_id."""
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
# BOOK 3: 《银杏城旧事》
# ============================================================
print("=== Book 3: 《银杏城旧事》 ===")

# Select festival/city-life chapters by ch ID
# Spring: 清明(ch85=七夕 renamed, need actual mapping)
# Let me use the actual chapter IDs from the scan output

# Manual selection based on chapter scan:
# 节俗核心: ch85(七夕), ch87(灯谜会), ch88(秋祭), ch90(端午), ch91(中秋), ch92(重阳), ch93(除夕), ch94(清明), ch95(初雪)
# 市井生活: ch105(试茶), ch106(纸鸢), ch108(晒书), ch111(酒约), ch112(药香), ch117(灯市)
# 四季: ch121(霜降), ch126(雪夜), ch135(市井), ch197(市声)

book3_chapters = [
    # 春之卷
    94,   # 清明
    106,  # 纸鸢
    570,  # 探芽
    571,  # 迎燕
    # 夏之卷
    90,   # 端午
    85,   # 七夕
    471,  # 听蝉
    428,  # 纳凉
    105,  # 试茶
    # 秋之卷
    91,   # 中秋
    92,   # 重阳
    88,   # 秋祭
    121,  # 霜降
    547,  # 拾叶
    266,  # 暮雪-> not autumn, skip
    246,  # 暮鸦
    # 冬之卷
    93,   # 除夕
    95,   # 初雪
    126,  # 雪夜
    552,  # 围炉
    564,  # 拥炉
    551,  # 候雪
    # 洛城风物
    56,   # 洛城四季图
    59,   # 银杏食录
    71,   # 洛城风物志
    117,  # 灯市
    135,  # 市井
    197,  # 市声
    87,   # 灯谜会
    168,  # 渡口
    111,  # 酒约
    108,  # 晒书
]

chapters_html3 = extract_chapter_range(content, book3_chapters)
chapters_html3, num3 = renumber_chapters(chapters_html3, 1)
print(f"  Extracted {num3} chapters")

toc3 = [
    ("春之卷", "ch1"),
    ("夏之卷", "ch5"),
    ("秋之卷", "ch10"),
    ("冬之卷", "ch16"),
]

colophon3 = f'''<p><strong>《银杏城旧事》</strong></p>
      <p>一部风物民俗散文集 · 洛城市井生活志</p>
      <p>全书四卷 · {num3}章</p>
      <p>写作风格：节俗叙事 + 风物志笔法</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列扩展篇章精选）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第三部</p>
      <p>系列还包括：《银杏辞》《清音寺居》《银杏人物志》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">洛城 · 四时风物 · 一城旧事</p>'''

html3 = build_standalone_html('银杏城旧事', '四时风物，一城旧事', chapters_html3, toc3, colophon3)
outpath3 = os.path.join(OUTDIR, 'yinxing-cheng-jiushi-city-tales-2026-05-15.html')
with open(outpath3, 'w', encoding='utf-8') as f:
    f.write(html3)
print(f"  Written: {outpath3}")
print(f"  Size: {len(html3)} chars")


# ============================================================
# BOOK 4: 《银杏人物志》
# ============================================================
print("\n=== Book 4: 《银杏人物志》 ===")

# Main block: ch20-ch52 (33 chapters of character side stories)
# Plus scattered character chapters from later
book4_chapters = list(range(20, 53))  # ch20-ch52

# Add scattered character chapters:
scattered_char = [
    79,   # 外传·若华
    86,   # 苏映雪授琴记
    97,   # 弈剑暗语
    98,   # 沈若华守树记
    99,   # 银杏再传
    100,  # 青篱学琴
    101,  # 少年游
    102,  # 小蝶的网
    103,  # 长卿的园子
]
book4_chapters.extend(scattered_char)

chapters_html4 = extract_chapter_range(content, book4_chapters)
chapters_html4, num4 = renumber_chapters(chapters_html4, 1)
print(f"  Extracted {num4} chapters")

toc4 = [
    ("人物列传（一至四十二）", "ch1"),
]

colophon4 = f'''<p><strong>《银杏人物志》</strong></p>
      <p>一部人物短篇集 · 配角的独立人生</p>
      <p>全书 · {num4}章</p>
      <p>写作风格：人物传记 + 短篇叙事</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列扩展篇章精选）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第四部</p>
      <p>传主：云姬、苏映雪、楚寒衣、陆明远、赵婉柔、沈怀瑾、顾长卿、小蝶、明远和尚、沈若兮 等</p>
      <p>系列还包括：《银杏辞》《清音寺居》《银杏城旧事》《附录卷》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">人物 · 正传之外 · 各自有光</p>'''

html4 = build_standalone_html('银杏人物志', '正传之外，各自有光', chapters_html4, toc4, colophon4)
outpath4 = os.path.join(OUTDIR, 'yinxing-renwu-zhi-character-tales-2026-05-15.html')
with open(outpath4, 'w', encoding='utf-8') as f:
    f.write(html4)
print(f"  Written: {outpath4}")
print(f"  Size: {len(html4)} chars")


# ============================================================
# BOOK 5: 《银杏辞·附录卷》
# ============================================================
print("\n=== Book 5: 《银杏辞·附录卷》 ===")

# ch53-ch84: reference/compilation material
book5_chapters = list(range(53, 85))  # ch53-ch84

chapters_html5 = extract_chapter_range(content, book5_chapters)
chapters_html5, num5 = renumber_chapters(chapters_html5, 1)
print(f"  Extracted {num5} chapters")

toc5 = [
    ("设定资料汇编", "ch1"),
]

colophon5 = f'''<p><strong>《银杏辞·附录卷》</strong></p>
      <p>设定资料集 · 参考附录</p>
      <p>{num5}章</p>
      <p>内容：诗词全录 · 人物春秋 · 诗谶辑录 · 风物志 · 寺庙志 · 梦境录 · 时序录 · 对白录 等</p>
      <p>版本：v1.00（2026-05-15 · 从《银杏辞》系列汇编）</p>
      <p style="margin-top:12px;">本书为《银杏辞》系列第五部（资料卷）</p>
      <p>系列还包括：《银杏辞》《清音寺居》《银杏城旧事》《银杏人物志》</p>
      <p style="margin-top:16px;color:var(--muted);font-size:13px;">附录 · 诗与物的档案馆</p>'''

html5 = build_standalone_html('银杏辞·附录卷', '诗与物的档案馆', chapters_html5, toc5, colophon5)
outpath5 = os.path.join(OUTDIR, 'yinxing-ci-fulujuan-appendix-2026-05-15.html')
with open(outpath5, 'w', encoding='utf-8') as f:
    f.write(html5)
print(f"  Written: {outpath5}")
print(f"  Size: {len(html5)} chars")

print("\n=== All Books Generated ===")
