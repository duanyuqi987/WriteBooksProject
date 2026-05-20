"""
Fix remaining HTML issues in master file, re-extract all 5 books,
and generate .md mirrors for each book.
"""
import re
import os

MASTER = 'd:/ProgramWork/WriteBookProject/docs/2026-05-14/学习书/银杏辞-yinxing-ci-novel-2026-05-14.html'
OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'

os.makedirs(OUTDIR, exist_ok=True)

with open(MASTER, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# Step 1: Fix unclosed <p> tags using token-based approach
# ============================================================
print("=== Fixing unclosed <p> tags ===")

def fix_unclosed_p_tags(html):
    """Auto-close any unclosed <p> tags before block-level elements."""
    # Block-level elements that should not be inside <p>
    block_elements = ['<h2', '<div', '<footer', '<main', '<nav', '<header', '<ol', '<ul', '<table']

    fixes = 0
    result = []
    i = 0
    p_depth = 0

    while i < len(html):
        # Check if we're at a tag
        if html[i] == '<':
            # Find end of tag
            tag_end = html.find('>', i)
            if tag_end < 0:
                result.append(html[i:])
                break
            tag = html[i:tag_end+1]

            # Is this a block-level opening tag?
            is_block_open = any(tag.startswith(be) for be in block_elements) and not tag.startswith('</')

            # Is this a closing tag?
            is_close = tag.startswith('</')

            # If we're inside a <p> and encounter a block-level element, close the <p> first
            if p_depth > 0 and is_block_open:
                result.append('</p>\n')
                p_depth = 0
                fixes += 1

            # Track <p> depth
            if tag.startswith('<p') and not tag.startswith('</p'):
                # Check if self-closing
                if not tag.endswith('/>'):
                    p_depth += 1
            elif tag == '</p>':
                p_depth = max(0, p_depth - 1)
            elif is_close and tag not in ['</p>', '</div>', '</a>', '</span>', '</em>', '</strong>', '</li>', '</ol>', '</ul>', '</table>', '</tr>', '</td>', '</th>', '</thead>', '</tbody>']:
                # Closing a block element - close any open <p>
                if p_depth > 0:
                    result.append('</p>\n')
                    p_depth = 0
                    fixes += 1

            result.append(tag)
            i = tag_end + 1
        else:
            result.append(html[i])
            i += 1

    # Close any remaining open <p>
    if p_depth > 0:
        result.append('</p>')
        fixes += 1

    print(f"  Fixed {fixes} unclosed <p> tags")
    return ''.join(result)

# Only fix the section from ch447 onwards (where we know issues exist)
ch447_pos = content.find('<h2 id="ch447">')
footer_pos = content.find('<footer class="colophon"', ch447_pos)

before = content[:ch447_pos]
section = content[ch447_pos:footer_pos]
after = content[footer_pos:]

fixed_section = fix_unclosed_p_tags(section)
content = before + fixed_section + after

# ============================================================
# Step 2: Fix extra </div> in ch447 section
# ============================================================
print("\n=== Fixing extra </div> tags ===")

# Re-extract section after p-tag fix
ch447_pos = content.find('<h2 id="ch447">')
footer_pos = content.find('<footer class="colophon"', ch447_pos)
section = content[ch447_pos:footer_pos]

div_open = len(re.findall(r'<div[\s>]', section))
div_close = len(re.findall(r'</div>', section))
print(f"  div balance: open={div_open}, close={div_close}")

if div_close > div_open:
    extra = div_close - div_open
    print(f"  Removing {extra} orphan </div> tags")

    # Strategy: find </div> that immediately follows another </div> (no intervening <div)
    # or find </div> that appears right before <h2 or at section boundaries

    # Tokenize section
    tokens = []
    i = 0
    while i < len(section):
        if section[i] == '<':
            tag_end = section.find('>', i)
            if tag_end < 0:
                tokens.append(('text', section[i:]))
                break
            tag = section[i:tag_end+1]
            if tag.startswith('</div'):
                tokens.append(('close_div', tag, i))
            elif tag.startswith('<div'):
                tokens.append(('open_div', tag, i))
            elif tag.startswith('<h2'):
                tokens.append(('h2', tag, i))
            elif tag.startswith('<p'):
                tokens.append(('open_p', tag, i))
            elif tag == '</p>':
                tokens.append(('close_p', tag, i))
            else:
                tokens.append(('other', tag, i))
            i = tag_end + 1
        else:
            j = section.find('<', i)
            if j < 0:
                tokens.append(('text', section[i:], i))
                break
            tokens.append(('text', section[i:j], i))
            i = j

    # Find orphan </div> tags by tracking div depth
    result_parts = []
    div_depth = 0
    removed = 0
    for token in tokens:
        ttype = token[0]
        ttext = token[1]
        tpos = token[2]

        if ttype == 'open_div':
            div_depth += 1
            result_parts.append(ttext)
        elif ttype == 'close_div':
            if div_depth > 0:
                div_depth -= 1
                result_parts.append(ttext)
            else:
                # Orphan </div> - skip it
                removed += 1
                print(f"  Removed orphan </div> at section position {tpos}")
        else:
            result_parts.append(ttext)

    section = ''.join(result_parts)
    print(f"  Removed {removed} orphan </div> tags")

    # Rebuild content
    before = content[:ch447_pos]
    after = content[footer_pos:]
    content = before + section + after

# ============================================================
# Step 3: Final verification
# ============================================================
print("\n=== Final Verification ===")
p_open = len(re.findall(r'<p[\s>]', content))
p_close = len(re.findall(r'</p>', content))
d_open = len(re.findall(r'<div[\s>]', content))
d_close = len(re.findall(r'</div>', content))
h2_count = len(re.findall(r'<h2\s', content))
h2_close_count = len(re.findall(r'</h2>', content))
print(f"  Master: p={p_open}/{p_close} (diff={p_open-p_close}), div={d_open}/{d_close} (diff={d_open-d_close}), h2={h2_count}/{h2_close_count}")

for name, start_marker, end_marker in [
    ('ch1-ch19', '<h2 id="ch1">', '<h2 id="ch20">'),
    ('ch20-ch52', '<h2 id="ch20">', '<h2 id="ch53">'),
    ('ch53-ch84', '<h2 id="ch53">', '<h2 id="ch85">'),
    ('ch85-ch446', '<h2 id="ch85">', '<h2 id="ch447">'),
    ('ch447-ch598', '<h2 id="ch447">', '<footer class="colophon"'),
]:
    sp = content.find(start_marker)
    ep = content.find(end_marker, sp)
    if sp < 0 or ep < 0:
        print(f"  {name}: markers not found")
        continue
    sec = content[sp:ep]
    po = len(re.findall(r'<p[\s>]', sec))
    pc = len(re.findall(r'</p>', sec))
    do = len(re.findall(r'<div[\s>]', sec))
    dc = len(re.findall(r'</div>', sec))
    status = 'CLEAN' if po == pc and do == dc else f'p:{po-pc} d:{do-dc}'
    print(f"  {name}: p={po}/{pc} div={do}/{dc} -> {status}")

# Save master file
with open(MASTER, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n  Master file saved: {len(content):,} chars")

print("\n=== Master file fixes complete ===")
