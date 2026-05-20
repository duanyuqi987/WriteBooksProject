# -*- coding: utf-8 -*-
"""v3: 针对密度>5.0的剩余4章做保守启发式破折号替换"""
import re

B2 = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(B2, 'r', encoding='utf-8') as f:
    html = f.read()

def get_chapter_range(html, ch_id):
    """获取章节在HTML中的起止位置"""
    pos = html.find('<h2 id="%s">' % ch_id)
    if pos < 0:
        return None, None
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0:
        np = html.find('<footer', pos)
    if np < 0:
        np = len(html)
    return pos, np

def safe_reduce_dashes(chunk, max_reduce=None):
    """在章节HTML中安全地减少破折号，限制减少数量"""
    dashes_before = chunk.count('——')
    if dashes_before == 0:
        return chunk, 0

    if max_reduce is None:
        max_reduce = max(1, dashes_before // 3)  # 默认减少1/3

    # 规则1: ，—— → ， (逗号后的破折号多余)
    pattern1 = '，——'
    count1 = chunk.count(pattern1)
    if count1 > 0:
        limit1 = min(count1, max_reduce // 2 + 1)
        chunk = chunk.replace(pattern1, '，', limit1)

    # 规则2: ——， → ， (破折号后紧跟逗号，保留逗号)
    pattern2 = '——，'
    count2 = chunk.count(pattern2)
    if count2 > 0:
        limit2 = min(count2, max_reduce // 3 + 1)
        chunk = chunk.replace(pattern2, '，', limit2)

    # 规则3: ——在对话引号之间，将其替换为逗号
    # "X——Y" → "X，Y" (但要小心不破坏HTML属性中的引号)
    # 安全做法: 只处理中文引号语境
    # 在"和"之间（中文双引号之间）的——
    # 注：中文引号是U+201C和U+201D，但此文件中使用ASCII "

    # 规则4: 中文字符间的——替换为，
    # 找到 —— 前后都是CJK字符的实例
    pattern4 = re.compile(r'([一-鿿　-〿＀-￯])——([一-鿿　-〿＀-￯])')
    matches4 = list(pattern4.finditer(chunk))
    reduced = dashes_before - chunk.count('——')
    remaining = max_reduce - reduced
    if matches4 and remaining > 0:
        limit4 = min(len(matches4), remaining)
        # 从后往前替换避免位置偏移
        for m in reversed(matches4[-limit4:]):
            start, end = m.start(), m.end()
            chunk = chunk[:start] + m.group(1) + '，' + m.group(2) + chunk[end:]

    # 规则5: 如果还需要减少更多, 再处理 。——  → 。
    if max_reduce > 0:
        reduced = dashes_before - chunk.count('——')
        remaining = max_reduce - reduced
        if remaining > 0:
            pattern5 = '。——'
            count5 = chunk.count(pattern5)
            limit5 = min(count5, remaining)
            if limit5 > 0:
                chunk = chunk.replace(pattern5, '。', limit5)

    total_reduced = dashes_before - chunk.count('——')
    return chunk, total_reduced


targets = ['ch24', 'ch25', 'ch23', 'ch13']
total_reduced = 0

for ch_id in targets:
    pos, np = get_chapter_range(html, ch_id)
    if pos is None:
        print('%s: NOT FOUND' % ch_id)
        continue

    chunk = html[pos:np]
    # 统计
    cjk = len(re.findall(r'[一-鿿]', chunk))
    dashes_before = chunk.count('——')
    density_before = dashes_before / cjk * 100 if cjk > 0 else 0

    # 计算需要减少多少才能达到密度<5
    # 目标密度: 4.5, 保留足够破折号
    target_dashes = int(cjk * 0.045)  # 目标密度4.5
    need_reduce = max(0, dashes_before - target_dashes)
    # 限制最多减少40%
    max_reduce = min(need_reduce, dashes_before * 2 // 5)

    print('%s: before=%d dashes (%.1f/100), need_reduce=%d, max=%d' % (
        ch_id, dashes_before, density_before, need_reduce, max_reduce))

    new_chunk, reduced = safe_reduce_dashes(chunk, max_reduce)
    html = html[:pos] + new_chunk + html[np:]
    total_reduced += reduced

    dashes_after = new_chunk.count('——')
    density_after = dashes_after / cjk * 100 if cjk > 0 else 0
    print('  reduced=%d, after=%d dashes (%.1f/100)' % (reduced, dashes_after, density_after))

# 写入
with open(B2, 'w', encoding='utf-8') as f:
    f.write(html)

# 最终统计
total_cjk = len(re.findall(r'[一-鿿]', html))
total_dashes = html.count('——')
print('\n=== Final ===')
print('Total dashes: %d' % total_dashes)
print('Avg density: %.1f/100' % (total_dashes / total_cjk * 100 if total_cjk > 0 else 0))
print('Total reduced in v3: %d' % total_reduced)
print('Done: ' + B2)
