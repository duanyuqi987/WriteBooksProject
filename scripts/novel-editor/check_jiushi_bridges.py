# -*- coding: utf-8 -*-
"""检查《银杏城旧事》32章的章节间过渡桥接"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 桥接关键词（承上启下的时间/逻辑连接词）
bridge_patterns = [
    '之后', '完了', '第二天', '次日', '从此', '此后', '接下来',
    '过了', '接着', '后来', '那年', '这年', '那年', '今[年春夏秋冬]',
    '自[从打]', '那[天日晚]', '这[天次日]', '第[一二三]',
    '转眼', '不久', '没多久', '紧接着', '接下来',
    '上一', '如前', '同样的', '同样的这一年', '同年',
    '上次', '上回', '前面', '此[前后]',
    '收[拾到]', '回[到来去]', '继续',
    # 弱桥接: 时间/季节连续性
    '^[春夏秋冬]', '^[一二三四五六七八九十]月',
    '^[立雨惊春清谷立小芒夏小大处白秋寒霜立冬小大冬雪]',
    '这[天个]', '那[天个]',
]

def has_bridge(first_text):
    """检查章节开头是否有桥接语句"""
    first_text = first_text.strip()
    if not first_text:
        return False, ''

    # 检查开头50字内是否有桥接词
    head = first_text[:60]
    for pat in bridge_patterns:
        m = re.search(pat, head)
        if m:
            return True, m.group(0)
    return False, ''

# 提取所有章节
chapters = []
h2_re = re.compile(r'<h2 id="(ch\d+)">([^<]+)</h2>')
pos = 0
while True:
    m = h2_re.search(html, pos)
    if not m:
        break
    ch_id = m.group(1)
    ch_title = m.group(2)
    ch_start = m.end()

    next_h2 = h2_re.search(html, ch_start)
    footer_m = re.compile(r'<footer').search(html, ch_start)
    end_pos = len(html)
    if next_h2:
        end_pos = next_h2.start()
    if footer_m and footer_m.start() < end_pos:
        end_pos = footer_m.start()

    ch_html = html[ch_start:end_pos]

    # 提取第一个<p>的纯文本
    first_p = re.search(r'<p[^>]*>(.*?)</p>', ch_html, re.DOTALL)
    if first_p:
        first_text = re.sub(r'<[^>]+>', '', first_p.group(1)).strip()
    else:
        first_text = ''

    has, keyword = has_bridge(first_text)
    chapters.append((ch_id, ch_title, has, keyword, first_text[:80]))

    pos = ch_start + (end_pos - ch_start) if ch_start < end_pos else end_pos

# 输出报告
out_path = 'd:/ProgramWork/WriteBookProject/tmp_jiushi_bridge_check.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    no_bridge = [c for c in chapters if not c[2]]
    has_bridge = [c for c in chapters if c[2]]

    out.write('《银杏城旧事》章节过渡桥接检查\n')
    out.write('=' * 50 + '\n')
    out.write('总章节: %d\n' % len(chapters))
    out.write('有桥接: %d (%.0f%%)\n' % (len(has_bridge), len(has_bridge)/len(chapters)*100))
    out.write('无桥接: %d (%.0f%%)\n\n' % (len(no_bridge), len(no_bridge)/len(chapters)*100))

    out.write('--- 缺少桥接的章节 ---\n\n')
    for ch_id, ch_title, _, _, first_text in no_bridge:
        # 跳过第一章（无需桥接）
        if ch_id == 'ch1':
            continue
        out.write('%s %s:\n' % (ch_id, ch_title))
        out.write('  开头: %s...\n\n' % first_text[:60])

    out.write('\n--- 已有桥接的章节 ---\n\n')
    for ch_id, ch_title, _, keyword, first_text in has_bridge:
        out.write('%s %s: [%s]\n' % (ch_id, ch_title, keyword))
        out.write('  %s...\n\n' % first_text[:60])

print('Done: ' + out_path)
print('有桥接: %d/%d (%.0f%%)' % (len(has_bridge), len(chapters), len(has_bridge)/len(chapters)*100))
print('无桥接: %d' % len(no_bridge))
