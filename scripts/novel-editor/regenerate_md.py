"""
Regenerate .md files with improved HTML-to-markdown conversion.
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

def html_to_markdown_v2(html_chapters):
    """Convert chapter HTML to clean markdown format."""
    # Step 1: Handle inner-monologue divs -> blockquote
    def inner_to_blockquote(m):
        inner_content = m.group(1)
        p_match = re.search(r'<p>(.*?)</p>', inner_content, re.DOTALL)
        if p_match:
            text = p_match.group(1).strip()
            lines = text.split('\n')
            quoted_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped:
                    quoted_lines.append('> ' + stripped)
            return '\n\n' + '\n'.join(quoted_lines) + '\n\n'
        return ''

    md = re.sub(
        r'<div class="inner-monologue">(.*?)</div>',
        inner_to_blockquote,
        html_chapters,
        flags=re.DOTALL
    )

    # Step 2: Handle poem-block divs -> blockquote poetry
    def poem_to_blockquote(m):
        inner = m.group(1)
        poem_lines = re.findall(r'<p>(.*?)</p>', inner)
        quoted = '\n'.join('> ' + line.strip() for line in poem_lines if line.strip())
        return '\n\n' + quoted + '\n\n'

    md = re.sub(
        r'<div class="poem-block">(.*?)</div>',
        poem_to_blockquote,
        md,
        flags=re.DOTALL
    )

    # Step 3: Handle chapter headings <h2 id="chN">title</h2>
    md = re.sub(r'<h2 id="ch\d+">([^<]+)</h2>', r'\n## \1\n', md)

    # Step 4: Handle <h3>
    md = re.sub(r'<h3[^>]*>([^<]+)</h3>', r'\n### \1\n', md)

    # Step 5: Handle divider <div class="divider">
    md = re.sub(r'<div class="divider">.*?</div>', '\n---\n', md)

    # Step 6: Handle end markers
    md = re.sub(
        r'<p style="text-align:center;text-indent:0;color:var\(--muted\);">(.*?)</p>',
        r'\n\n*\1*\n',
        md
    )

    # Step 7: Convert <p> tags — extract inner text
    def p_replacer(m):
        inner = m.group(1)
        # Remove any nested HTML tags
        inner = re.sub(r'<br\s*/?>', '\n', inner)
        inner = re.sub(r'<[^>]+>', '', inner)
        return '\n' + inner.strip() + '\n'

    md = re.sub(r'<p(?:\s[^>]*)?>(.*?)</p>', p_replacer, md, flags=re.DOTALL)

    # Step 8: Remove any remaining HTML tags
    md = re.sub(r'<[^>]+>', '', md)

    # Step 9: Clean up whitespace
    # Remove leading whitespace on each line
    lines = md.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_lines.append(line.strip())
    md = '\n'.join(cleaned_lines)

    # Collapse excessive blank lines (max 2 consecutive)
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    md = re.sub(r'\n{3,}', '\n\n', md)

    # Remove leading/trailing whitespace
    md = md.strip()

    return md


def build_markdown(title, subtitle, chapters_md, colophon_html, word_count=""):
    """Build a clean markdown book."""
    # Clean colophon
    colophon_clean = re.sub(r'<[^>]+>', '', colophon_html)
    colophon_clean = re.sub(r'\n\s+', '\n', colophon_clean).strip()
    colophon_clean = '\n'.join(line.strip() for line in colophon_clean.split('\n') if line.strip())

    md = f'# {title}\n\n**{subtitle}**\n\n---\n\n{chapters_md}\n\n---\n\n{colophon_clean}\n'
    return md


# Process all 5 books
books = [
    ('yinxing-ci-novel-2026-05-15.html', 'yinxing-ci-novel-2026-05-15.md',
     '银杏辞', '三秋叶落，与君同看雪花轻'),
    ('qingyin-siju-temple-life-2026-05-15.html', 'qingyin-siju-temple-life-2026-05-15.md',
     '清音寺居', '山中无历日，寒尽不知年'),
    ('yinxing-cheng-jiushi-city-tales-2026-05-15.html', 'yinxing-cheng-jiushi-city-tales-2026-05-15.md',
     '银杏城旧事', '四时风物，一城旧事'),
    ('yinxing-renwu-zhi-character-tales-2026-05-15.html', 'yinxing-renwu-zhi-character-tales-2026-05-15.md',
     '银杏人物志', '正传之外，各自有光'),
    ('yinxing-ci-fulujuan-appendix-2026-05-15.html', 'yinxing-ci-fulujuan-appendix-2026-05-15.md',
     '银杏辞·附录卷', '诗与物的档案馆'),
]

for html_name, md_name, title, subtitle in books:
    html_path = os.path.join(OUTDIR, html_name)
    md_path = os.path.join(OUTDIR, md_name)

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract chapters portion (between <main class="content"> and <footer class="colophon")
    main_start = html_content.find('<main class="content">')
    footer_start = html_content.find('<footer class="colophon"')

    if main_start >= 0 and footer_start >= 0:
        # Get the hero header
        hero_end = html_content.find('</header>', main_start)
        hero_section = html_content[main_start:hero_end + len('</header>')] if hero_end >= 0 else ''

        # Get chapters
        chapters_html = html_content[hero_end + len('</header>'):footer_start] if hero_end >= 0 else html_content[main_start:footer_start]

        # Get colophon
        colophon_end = html_content.find('</footer>', footer_start)
        colophon_html = html_content[footer_start:colophon_end + len('</footer>')] if colophon_end >= 0 else ''
    else:
        print(f'WARNING: Could not find main/content structure in {html_name}')
        continue

    # Convert to markdown
    chapters_md = html_to_markdown_v2(chapters_html)

    # Get word count
    wc_match = re.search(r'content="(\d+)"', html_content)
    wc = wc_match.group(1) if wc_match else ''

    # Build markdown
    md_content = build_markdown(title, subtitle, chapters_md, colophon_html, wc)

    # Write
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f'{title}: {md_path} ({len(md_content):,} chars)')

print('\nAll .md files regenerated.')
