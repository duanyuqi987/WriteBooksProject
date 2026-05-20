# -*- coding: utf-8 -*-
"""
《清音寺居》深度叙事优化 — 综合脚本
组A: 增强沈秋白存在感(~20处)
组B: 强化情感暗线(~12处)
组C: 填充叙事空白(~8处)
组D: 充实弱章(~8处)
组E: 增强章节过渡(~15处)
"""
import re
import shutil
from datetime import datetime

HTML_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
BACKUP_DIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/备份/b2-narrative-pre/'

# 创建备份
import os
os.makedirs(BACKUP_DIR, exist_ok=True)
backup_path = BACKUP_DIR + os.path.basename(HTML_PATH)
shutil.copy(HTML_PATH, backup_path)
print('Backup: ' + backup_path)

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

def get_chapter_range(html, ch_id):
    """获取章节在HTML中的起止位置"""
    pos = html.find('<h2 id="%s">' % ch_id)
    if pos < 0:
        return None, None, None
    # 找章节标题结束
    h2_end = html.find('</h2>', pos) + len('</h2>')
    next_pos = html.find('<h2 id="ch', h2_end)
    if next_pos < 0:
        next_pos = html.find('<footer', h2_end)
    if next_pos < 0:
        next_pos = len(html)
    return pos, h2_end, next_pos

def insert_after(html, ch_id, anchor, new_text):
    """在指定章节中找到anchor文本，在其后插入new_text"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'

    # 在章节范围内搜索anchor
    ch_html = html[pos:end]
    idx = ch_html.find(anchor)
    if idx < 0:
        return html, False, 'anchor not found'

    # 找到anchor的结束位置
    abs_idx = pos + idx + len(anchor)
    html = html[:abs_idx] + new_text + html[abs_idx:]
    return html, True, 'ok'

def insert_before(html, ch_id, anchor, new_text):
    """在指定章节中找到anchor文本，在其前插入new_text"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'

    ch_html = html[pos:end]
    idx = ch_html.find(anchor)
    if idx < 0:
        return html, False, 'anchor not found'

    abs_idx = pos + idx
    html = html[:abs_idx] + new_text + html[abs_idx:]
    return html, True, 'ok'

def replace_text(html, ch_id, old_text, new_text):
    """在指定章节中替换文本"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'

    ch_html = html[pos:end]
    if old_text not in ch_html:
        return html, False, 'old_text not found'

    html = html[:pos] + ch_html.replace(old_text, new_text, 1) + html[end:]
    return html, True, 'ok'

def insert_paragraph_after(html, ch_id, anchor, new_para):
    """在anchor所在段落之后插入新段落"""
    pos, _, end = get_chapter_range(html, ch_id)
    if pos is None:
        return html, False, 'chapter not found'

    ch_html = html[pos:end]
    idx = ch_html.find(anchor)
    if idx < 0:
        return html, False, 'anchor not found'

    # 找到anchor所在段落的</p>
    abs_anchor = pos + idx
    para_end = html.find('</p>', abs_anchor)
    if para_end < 0 or para_end > end:
        return html, False, 'paragraph end not found'

    html = html[:para_end + len('</p>')] + '\n\n    <p>' + new_para + '</p>' + html[para_end + len('</p>'):]
    return html, True, 'ok'

mods = []  # (组, 描述, 是否成功)
total_ok = 0
total_fail = 0

# ================================================================
# 组D: 充实弱章 (8处) - 先做最简单的
# ================================================================
print('=' * 50)
print('组D: 充实弱章')
print('=' * 50)

# D1.1 ch2裁纸 - 添加内心独白
html, ok, msg = insert_after(html, 'ch2',
    '裁纸的时候——心要静',
    '寂声在旁边看着，心里想：师父做每一件事都像在做一件很重要的事，哪怕只是裁一张纸。他以前以为"认真"就是把事情做对，现在才慢慢明白——认真是把心放进手里。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch2:', msg)

# D1.2 ch142种瓜 - 添加内心独白
html, ok, msg = insert_after(html, 'ch142',
    '瓜籽入土那一刻',
    '寂声蹲在土边，看着那些瓜子一粒粒被土盖住，忽然觉得——种瓜和写字很像。你把一颗种子放下去，看不见它在土里干什么，只能等。写字也是——你写下一个字，不知道谁会读到，不知道读的人会不会明白你写下它时的心情。但你还是写。就像老孙还是种。不是因为一定会有结果，是因为——放下去，本身就是意义。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch142:', msg)

# D2.1 ch149换衣 - 添加内心独白+身体感知
html, ok, msg = insert_after(html, 'ch149',
    '换下冬衣，穿上春衫',
    '寂声把冬衣叠好放进柜子的时候，手在粗布上停了一下。这件冬衣的袖口已经磨出了线头，是去年立冬那天老孙递给他的——"山里冷，别逞强。"他当时只是接过来，说了声谢谢。现在叠衣服的时候才注意到，袖口的针脚很密，每一针都走得很均匀——老孙的手已经有些抖了，但他缝的衣服从来不马虎。寂声把袖子翻过来，看着那些针脚，想——这针线里缝进去的，是不是比衣服本身更多。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch149:', msg)

# D2.2 ch149换衣 - 扩展身体感知细节
html, ok, msg = insert_after(html, 'ch149',
    '春天到了',
    '最先感到春天的是皮肤——风吹过来不再是刺的，是推的，轻轻地推着你往院子里走。然后鼻子也醒了——泥土翻新的腥味、远处飘来的不知名的花香、井台边青苔的湿气。最后才是眼睛——看到石缝里不知什么时候冒出了一点绿。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch149-2:', msg)

# D2.3 ch91迎夏 - 夏日感官扩展
html, ok, msg = insert_after(html, 'ch91',
    '立夏这天',
    '立夏的早晨和春天的早晨不一样。春天的早晨是凉的，带着一丝残留的寒意——像冬天临走时搭在肩上的一条薄披风。夏天的早晨是温的，空气里有股被太阳晒了一半的草木味，还没完全热透，但你能预感到——再过一两个时辰，蝉就要开始叫了，石板路要开始烫脚了，井台边的青苔要从湿变干再从干变焦。这一切都还没有发生，但空气已经在预告了。寂声站在院子里吸了一口气——夏天的味道，像一杯泡了刚好的茶，不烫嘴，但你知道它很快就会凉，所以要趁热。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch91:', msg)

# D2.4 ch150闻蝉 - 蝉声隐喻扩展
html, ok, msg = insert_after(html, 'ch150',
    '蝉声',
    '蝉声不是音乐——它单调、固执、不和任何声音商量。但正是这种不商量，让它成了夏天唯一不需要怀疑的存在。你永远不会问"蝉开始叫了吗"——因为它们开始叫的时候，你一定会知道。就像有些人在你生命里——他们不是最会说话的，不是最讨人喜欢的，但他们的存在不需要你确认。他们在，你就知道。蝉在地下活了七年，爬出来只活七天——七天里它们什么都不做，就是叫。七年的沉默换七天的声音——这七天里每一声都是值得的。寂声想——自己的名字里有一个"声"字。也许每个人的一生，都是在用很长很长的沉默，换很短很短的——一声。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch150:', msg)

# D1.3 ch145晚钟 - 添加内心独白
html, ok, msg = insert_after(html, 'ch145',
    '钟声',
    '这是寂声第一次独自敲晚钟——老孙站在旁边看着，没伸手。寂声拉起钟槌的时候，手臂有点抖——不是因为钟槌重，是因为他忽然意识到：一百零八下钟声里，每一下都有人在听。山下的农夫在听，城里的妇人在听，那个明天要赶考的书生在听，那对刚吵完架的夫妻在听。而他在敲。他不再是那个只会在旁边看的人了。钟声敲出去的那一刻，他觉得自己身体里有什么东西也跟着被敲响了——不是金属的声音，是木头的，是沉沉的、闷闷的、从土里长出来的那种声响。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch145:', msg)

# D3 ch152无尽 - 结尾过渡优化
html, ok, msg = insert_after(html, 'ch152',
    '故事到这里',
    '没有结尾——因为每一片银杏叶落下之后，第二年都会从同一根枝上再长出来。黄了绿，绿了黄，黄了再绿——这不是循环，是延续。故事不是讲完的，是放手的——像放一盏河灯，你不知道它会漂到谁的岸边，但你放了。放了就不是你的了——是它的。它有自己的路，自己的水流，自己的春天。')
if ok: total_ok += 1
else: total_fail += 1; print('  FAIL ch152:', msg)

print('组D: %d OK, %d FAIL' % (total_ok, total_fail))

# ================================================================
# 组E: 增强章节过渡 (已在bridge脚本中做过部分，这里补充季节性过渡)
# ================================================================
print('\n' + '=' * 50)
print('组E: 增强章节过渡')
print('=' * 50)
group_e_ok = 0
group_e_fail = 0

# E2: 季节感知线索 — 在季节转折处增加过渡
seasonal_bridges = [
    # 冬→春 转折
    ('ch80', '迎春', '积雪开始融化的时候', '山里的冬天走得很慢——不是一下子就走的，是一寸一寸往后退的。最先发现春天的是老孙——他指着石阶缝里的一点绿说："看，今年的第一朵。每年都是这里最先冒出来——它对春天最敏感。"'),
    # 春→夏 转折
    ('ch90', '立夏', '春天最后一天', '春天的最后一天和夏天的第一天之间，只隔了一夜的南风。风从南边吹来的时候带着潮气——不是春天的湿润，是夏天那种黏黏的、闷闷的潮。老孙说南风一来，春茶就该收起来了——"南风吹过的茶，是夏天的茶了。"'),
    # 夏→秋 转折
    ('ch110', '立秋', '第一片落叶', '立秋那天不一定凉快——有时候比夏天还热。但空气变了。同样的温度，夏天的热是闷的、黏的、赖着不走的；秋天的热是脆的、干的、知道自己待不了多久的。'),
    # 秋→冬 转折
    ('ch130', '初冬', '北风起了', '北风一起，山里的颜色就少了。先走的是花，然后是叶，最后是虫声。但少不是没有——剩下的颜色反而更浓了：天更蓝，松更绿，银杏树皮上的裂纹更深。老孙说冬天是把多余的东西收走，把骨头露给你看。'),
    # 一年循环结束
    ('ch145', '晚钟', '又是一年', '又是一年过去了。同样的钟声，同样的银杏树，同样的人——但今年的寂声已经不是去年那个只会跟在师父身后的孩子了。时间在山上走得很慢，但从不回头。'),
]

for ch_id, ch_name, anchor, bridge_text in seasonal_bridges:
    html, ok, msg = insert_after(html, ch_id, anchor, bridge_text)
    if ok:
        group_e_ok += 1
    else:
        group_e_fail += 1
        print('  FAIL %s(%s): %s' % (ch_id, ch_name, msg))

total_ok += group_e_ok
total_fail += group_e_fail
print('组E: %d OK, %d FAIL' % (group_e_ok, group_e_fail))

# ================================================================
# 先写入并验证D+E组
# ================================================================
print('\n总计: %d OK, %d FAIL' % (total_ok, total_fail))

if total_fail == 0:
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Written: ' + HTML_PATH)
else:
    print('WARNING: %d failures, not writing yet' % total_fail)
    # 但仍然写入以检查效果
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Written anyway: ' + HTML_PATH)
