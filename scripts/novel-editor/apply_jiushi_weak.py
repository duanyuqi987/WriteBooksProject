# -*- coding: utf-8 -*-
"""应用银杏城旧事弱章充实修改"""
import json, shutil, os, re

HTML_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
JSON_PATH = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_weak_mods.json'
BACKUP_DIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/备份/jiushi-weak-pre/'

os.makedirs(BACKUP_DIR, exist_ok=True)
shutil.copy(HTML_PATH, BACKUP_DIR + os.path.basename(HTML_PATH))
print('Backup done')

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    mods = json.load(f)

def get_ch_range(html, ch_id):
    pos = html.find('<h2 id="%s">' % ch_id)
    if pos < 0: return None, None, None
    h2_end = html.find('</h2>', pos) + len('</h2>')
    np = html.find('<h2 id="ch', h2_end)
    if np < 0: np = html.find('<footer', h2_end)
    if np < 0: np = len(html)
    return pos, h2_end, np

def insert_paragraph_after(html, ch_id, anchor, new_para):
    pos, _, end = get_ch_range(html, ch_id)
    if pos is None: return html, False, 'chapter not found'
    idx = html.find(anchor, pos)
    if idx < 0 or idx > end: return html, False, 'anchor not found'
    para_end = html.find('</p>', idx)
    if para_end < 0 or para_end > end: return html, False, 'no </p> after anchor'
    html = html[:para_end+4] + '\n\n    <p>' + new_para + '</p>' + html[para_end+4:]
    return html, True, 'ok'

def insert_after(html, ch_id, anchor, new_text):
    pos, _, end = get_ch_range(html, ch_id)
    if pos is None: return html, False, 'chapter not found'
    idx = html.find(anchor, pos)
    if idx < 0 or idx > end: return html, False, 'anchor not found'
    html = html[:idx+len(anchor)] + new_text + html[idx+len(anchor):]
    return html, True, 'ok'

ok = 0
fail = 0
for m in mods:
    typ = m['type']
    if typ == 'insert_paragraph_after':
        html, success, msg = insert_paragraph_after(html, m['ch_id'], m['anchor'], m['new_text'])
    else:
        html, success, msg = insert_after(html, m['ch_id'], m['anchor'], m['new_text'])
    if success:
        ok += 1
        print(f'  OK [{m["desc"]}]')
    else:
        fail += 1
        print(f'  FAIL [{m["desc"]}]: {msg}')

print(f'\nTotal: {ok} OK, {fail} FAIL')
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('Written: ' + HTML_PATH)
