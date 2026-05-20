# -*- coding: utf-8 -*-
"""人物志破折号密度优化"""
import re, shutil, os

HTML_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-renwu-zhi-character-tales-2026-05-15.html'
BACKUP_DIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/备份/renwu-dash-pre/'

os.makedirs(BACKUP_DIR, exist_ok=True)
shutil.copy(HTML_PATH, BACKUP_DIR + os.path.basename(HTML_PATH))
print('Backup done')

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

h2_re = re.compile(r'<h2 id="(ch\d+)">([^<]+)</h2>')
p_tag_re = re.compile(r'(<p[^>]*>)(.*?)(</p>)', re.DOTALL)
cjk_dash_re = re.compile(r'(?<=[一-鿿])——(?=[一-鿿])')

TARGET_DENSITY = 3.5
MAX_REDUCTION = 0.35
# ch23 怀瑾之死 特殊处理——其高密度是断裂叙事的风格选择
CH23_MAX_REDUCTION = 0.20

def safe_rules(text):
    text = text.replace('，——', '，')
    text = text.replace('——，', '，')
    text = text.replace('。——', '。')
    text = text.replace('；——', '；')
    text = text.replace('？——', '？')
    text = text.replace('！——', '！')
    return text

def replace_n_cjk_dashes(text, n):
    if n <= 0: return text, 0
    matches = list(cjk_dash_re.finditer(text))
    if not matches: return text, 0
    count = 0
    parts = []
    last = 0
    for m in matches:
        if count >= n: break
        parts.append(text[last:m.start()])
        parts.append('，')
        last = m.end()
        count += 1
    parts.append(text[last:])
    return ''.join(parts), count

def process_chapter(ch_html, cjk, ch_id):
    old_d = ch_html.count('——')
    max_red = CH23_MAX_REDUCTION if ch_id == 'ch23' else MAX_REDUCTION

    # Step 1: safe rules
    def step1(m):
        return m.group(1) + safe_rules(m.group(2)) + m.group(3)
    ch_html = p_tag_re.sub(step1, ch_html)
    after_safe = ch_html.count('——')

    # Step 2: check if more needed
    cur_density = after_safe / cjk * 100 if cjk > 0 else 0
    if cur_density <= TARGET_DENSITY:
        return ch_html, old_d - after_safe

    target_d = int(cjk * TARGET_DENSITY / 100)
    need = after_safe - target_d
    max_allow = int(old_d * max_red)
    already = old_d - after_safe
    budget = max(0, max_allow - already)
    to_remove = min(need, budget)
    if to_remove <= 0:
        return ch_html, old_d - after_safe

    # Step 3: CJK dash replacement
    paras = list(p_tag_re.finditer(ch_html))
    remaining = to_remove
    result = []
    last_pos = 0
    for m in paras:
        result.append(ch_html[last_pos:m.start()])
        if remaining > 0:
            new_content, removed = replace_n_cjk_dashes(m.group(2), remaining)
            remaining -= removed
            result.append(m.group(1) + new_content + m.group(3))
        else:
            result.append(m.group(0))
        last_pos = m.end()
    result.append(ch_html[last_pos:])
    new_ch = ''.join(result)
    return new_ch, old_d - new_ch.count('——')

# Process all chapters
chapters = []
for m in h2_re.finditer(html):
    ch_id = m.group(1)
    start = m.end()
    nm = h2_re.search(html, start)
    end = nm.start() if nm else len(html)
    chapters.append((ch_id, m.group(2), start, end))

total_removed = 0
results = []
for ch_id, title, start, end in chapters:
    ch_html = html[start:end]
    cjk = len(re.findall(r'[一-鿿]', ch_html))
    old_d = ch_html.count('——')
    new_ch, removed = process_chapter(ch_html, cjk, ch_id)
    if removed > 0:
        total_removed += removed
        html = html[:start] + new_ch + html[end:]
        old_dens = old_d / cjk * 100 if cjk > 0 else 0
        new_d = new_ch.count('——')
        new_dens = new_d / cjk * 100 if cjk > 0 else 0
        results.append((ch_id, title, cjk, old_d, new_d, (old_d-new_d)/old_d*100, old_dens, new_dens))

results.sort(key=lambda x: x[6], reverse=True)
print(f'Modified {len(results)} chapters, removed {total_removed} dashes\n')
print(f'{"章节":<12} {"CJK":>6} {"原→新":>14} {"减少%":>8} {"原密→新密":>18}')
print('-' * 68)
for r in results[:25]:
    print(f'{r[0]} {r[1]:<8} {r[2]:>6} {r[3]:>4}→{r[4]:<4} {r[5]:>7.1f}% {r[6]:>5.1f}%→{r[7]:<5.1f}%')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

cjk = len(re.findall(r'[一-鿿]', html))
dashes = html.count('——')
print(f'\n最终: {dashes}破折号, {cjk}CJK, 密度={dashes/cjk*100:.2f}%')
print('Written: ' + HTML_PATH)
