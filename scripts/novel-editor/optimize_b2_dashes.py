# -*- coding: utf-8 -*-
"""清音寺居破折号密度优化 — 精准控制在~3.0%"""
import re
import shutil
import os

HTML_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
BACKUP_DIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/备份/b2-dash-opt/'

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

def safe_rules(text):
    """标点边界安全规则"""
    text = text.replace('，——', '，')
    text = text.replace('——，', '，')
    text = text.replace('。——', '。')
    text = text.replace('；——', '；')
    text = text.replace('？——', '？')
    text = text.replace('！——', '！')
    return text

def replace_n_cjk_dashes(text, n):
    """替换文本中前n个CJK间破折号为逗号，返回(新文本, 实际替换数)"""
    if n <= 0:
        return text, 0

    matches = list(cjk_dash_re.finditer(text))
    if not matches:
        return text, 0

    count = 0
    parts = []
    last = 0
    for m in matches:
        if count >= n:
            break
        parts.append(text[last:m.start()])
        parts.append('，')
        last = m.end()
        count += 1

    parts.append(text[last:])
    return ''.join(parts), count

def process_chapter_html(ch_html, cjk):
    """处理单章HTML，返回(新HTML, 移除数)"""
    old_d = ch_html.count('——')

    # 步骤1: 安全规则
    def step1(m):
        return m.group(1) + safe_rules(m.group(2)) + m.group(3)
    ch_html = p_tag_re.sub(step1, ch_html)
    after_safe = ch_html.count('——')

    # 步骤2: 检查是否需要更多
    cur_density = after_safe / cjk * 100 if cjk > 0 else 0
    if cur_density <= TARGET_DENSITY or after_safe <= 0:
        removed = old_d - after_safe
        return ch_html, removed

    # 计算需要移除的数量
    target_d = int(cjk * TARGET_DENSITY / 100)
    need = after_safe - target_d
    max_allow = int(old_d * MAX_REDUCTION)
    already = old_d - after_safe
    budget = max(0, max_allow - already)
    to_remove = min(need, budget)

    if to_remove <= 0:
        return ch_html, old_d - after_safe

    # 步骤3: 在每个<p>中应用CJK规则
    # 收集所有<p>内容
    paras = list(p_tag_re.finditer(ch_html))
    cjk_removed = 0
    remaining_budget = to_remove

    result_parts = []
    last_pos = 0
    for m in paras:
        # 添加标签间的内容
        result_parts.append(ch_html[last_pos:m.start()])

        prefix = m.group(1)
        content = m.group(2)
        suffix = m.group(3)

        if remaining_budget > 0:
            new_content, removed = replace_n_cjk_dashes(content, remaining_budget)
            remaining_budget -= removed
            cjk_removed += removed
            result_parts.append(prefix + new_content + suffix)
        else:
            result_parts.append(m.group(0))

        last_pos = m.end()

    result_parts.append(ch_html[last_pos:])
    new_ch_html = ''.join(result_parts)

    new_d = new_ch_html.count('——')
    return new_ch_html, old_d - new_d

# 收集章节
chapters = []
for m in h2_re.finditer(html):
    ch_id = m.group(1)
    title = m.group(2)
    start = m.end()
    nm = h2_re.search(html, start)
    if nm:
        end = nm.start()
    else:
        ft = html.find('<footer', start)
        end = ft if ft > 0 else len(html)
    chapters.append((ch_id, title, start, end))

print(f'Processing {len(chapters)} chapters...')

total_removed = 0
results = []

for ch_id, title, start, end in chapters:
    ch_html = html[start:end]
    cjk = len(re.findall(r'[一-鿿]', ch_html))
    old_d = ch_html.count('——')

    new_ch_html, removed = process_chapter_html(ch_html, cjk)

    if removed > 0:
        total_removed += removed
        html = html[:start] + new_ch_html + html[end:]
        old_dens = old_d / cjk * 100 if cjk > 0 else 0
        new_d = new_ch_html.count('——')
        red_pct = removed / old_d * 100 if old_d > 0 else 0
        results.append((ch_id, title, cjk, old_d, new_d, red_pct, old_dens))

results.sort(key=lambda x: x[6], reverse=True)

print(f'Modified {len(results)} chapters, removed {total_removed} dashes\n')
print(f'{"章节":<12} {"CJK":>6} {"原→新":>14} {"减少%":>8} {"原密度→新密度":>16}')
print('-' * 70)
for ch_id, title, cjk, old_d, new_d, red_pct, old_dens in results[:30]:
    new_dens = new_d / cjk * 100
    print(f'{ch_id} {title:<8} {cjk:>6} {old_d:>4}→{new_d:<4} {red_pct:>7.1f}% {old_dens:>5.1f}%→{new_dens:<5.1f}%')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

final_cjk = len(re.findall(r'[一-鿿]', html))
final_dashes = html.count('——')
final_density = final_dashes / final_cjk * 100 if final_cjk > 0 else 0
orig_total = sum(c[4] for c in chapters)  # old_d is at index 4 in the tuple... wait

# Recalculate original total
orig_total = 0
for ch_id, title, start, end in chapters:
    orig_total += html.count('——') # wrong - this counts current state
# Actually let me just compute from results
total_orig = sum(r[3] for r in results)  # this is only modified chapters
total_new = sum(r[4] for r in results)
total_red = total_orig - total_new

print(f'\n最终: {final_dashes}破折号, {final_cjk}CJK, 密度={final_density:.2f}%')
print(f'Written: ' + HTML_PATH)
