# -*- coding: utf-8 -*-
"""应用清音寺居叙事优化修改"""
import json
import shutil
import os
from datetime import datetime

HTML_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
JSON_PATH = 'd:/ProgramWork/WriteBookProject/tmp_b2_narrative_mods.json'
BACKUP_DIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/备份/b2-narrative-pre/'

# 备份
os.makedirs(BACKUP_DIR, exist_ok=True)
backup_path = BACKUP_DIR + os.path.basename(HTML_PATH)
shutil.copy(HTML_PATH, backup_path)
print('Backup: ' + backup_path)

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    mods = json.load(f)

print(f'Loaded {len(mods)} modifications')

def get_chapter_range(html, ch_id):
    """获取章节在HTML中的起止位置"""
    pos = html.find('<h2 id="%s">' % ch_id)
    if pos < 0:
        return None, None, None
    h2_end = html.find('</h2>', pos) + len('</h2>')
    next_pos = html.find('<h2 id="ch', h2_end)
    if next_pos < 0:
        next_pos = html.find('<footer', h2_end)
    if next_pos < 0:
        next_pos = len(html)
    return pos, h2_end, next_pos

def insert_after(html, ch_id, anchor, new_text):
    """在章节中找到anchor文本后插入new_text"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'
    ch_html = html[pos:end]
    idx = ch_html.find(anchor)
    if idx < 0:
        return html, False, 'anchor not found in chapter'
    abs_idx = pos + idx + len(anchor)
    html = html[:abs_idx] + new_text + html[abs_idx:]
    return html, True, 'ok'

def insert_before(html, ch_id, anchor, new_text):
    """在章节中找到anchor文本前插入new_text"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'
    ch_html = html[pos:end]
    idx = ch_html.find(anchor)
    if idx < 0:
        return html, False, 'anchor not found in chapter'
    abs_idx = pos + idx
    html = html[:abs_idx] + new_text + html[abs_idx:]
    return html, True, 'ok'

def replace_text(html, ch_id, old_text, new_text):
    """在章节中替换文本"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'
    ch_html = html[pos:end]
    if old_text not in ch_html:
        return html, False, 'old_text not found in chapter'
    html = html[:pos] + ch_html.replace(old_text, new_text, 1) + html[end:]
    return html, True, 'ok'

def insert_paragraph_after(html, ch_id, anchor, new_para):
    """在anchor所在段落后插入新段落"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'
    ch_html = html[pos:end]
    idx = ch_html.find(anchor)
    if idx < 0:
        return html, False, 'anchor not found in chapter'
    abs_anchor = pos + idx
    para_end = html.find('</p>', abs_anchor)
    if para_end < 0 or para_end > end:
        return html, False, 'paragraph end not found'
    html = html[:para_end + len('</p>')] + '\n\n    <p>' + new_para + '</p>' + html[para_end + len('</p>'):]
    return html, True, 'ok'

# 应用修改
total_ok = 0
total_fail = 0
failed_mods = []

for i, m in enumerate(mods):
    ch_id = m['ch_id']
    typ = m['type']
    anchor = m['anchor']
    new_text = m['new_text']
    desc = m.get('desc', f'{i}')

    if typ == 'insert_after':
        html, ok, msg = insert_after(html, ch_id, anchor, new_text)
    elif typ == 'insert_before':
        html, ok, msg = insert_before(html, ch_id, anchor, new_text)
    elif typ == 'replace_text':
        html, ok, msg = replace_text(html, ch_id, anchor, new_text)
    elif typ == 'insert_paragraph_after':
        html, ok, msg = insert_paragraph_after(html, ch_id, anchor, new_text)
    else:
        ok, msg = False, f'unknown type: {typ}'

    if ok:
        total_ok += 1
        print(f'  OK [{desc}]')
    else:
        total_fail += 1
        failed_mods.append((desc, ch_id, msg))
        print(f'  FAIL [{desc}] ch={ch_id}: {msg}')

print(f'\n总计: {total_ok} OK, {total_fail} FAIL')

if failed_mods:
    print('\n失败明细:')
    for desc, ch_id, msg in failed_mods:
        print(f'  - {desc} ({ch_id}): {msg}')

# 写入
if total_fail == 0:
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Written: ' + HTML_PATH)
else:
    print(f'WARNING: {total_fail} failures')
    # 仍然写入以检查效果
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Written anyway: ' + HTML_PATH)
