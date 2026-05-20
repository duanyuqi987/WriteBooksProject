# -*- coding: utf-8 -*-
"""为《银杏城旧事》添加章节过渡桥接句"""
import re

html_path = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/yinxing-cheng-jiushi-city-tales-2026-05-15.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 桥接定义: (章节ID, 原第一段开头文本(用于定位), 桥接句)
bridges = [
    # ch4春冰→ch5端午
    ('ch5',
     '洛城的端午和别处不同',
     '春冰化了之后，端午便跟着来了。'),

    # ch6七夕→ch7纳凉
    ('ch7',
     '三伏天的傍晚',
     '七夕的河灯漂远了，三伏天便轰轰烈烈地到了。'),

    # ch7纳凉→ch8试茶
    ('ch8',
     '明远和尚每年立冬后会在清音寺办一场',
     '那个夏夜在银杏树下看过流星之后，天气一日一日凉下去，转眼便入了冬。'),

    # ch8试茶→ch9蝉鸣
    ('ch9',
     '入了伏，满城的蝉都叫了起来',
     '茶会散了，伏天的蝉便接过了清音寺的热闹。'),

    # ch9蝉鸣→ch10中秋
    ('ch10',
     '中秋是洛城最盛大的节日之一',
     '蝉声最烈的那几天过去之后，中秋便悄无声息地到了。'),

    # ch10中秋→ch11重阳
    ('ch11',
     '银杏诗会的举办日期定在九月初九',
     '中秋的月饼还没吃完，银杏树下便有人开始为重阳诗会搭台子了。'),

    # ch11重阳→ch12秋祭
    ('ch12',
     '每年立秋，银杏书院有一场',
     '诗会散了之后，银杏书院的秋祭便接着来了。'),

    # ch13霜降→ch14暮鸦
    ('ch14',
     '黄昏时分，天快黑了',
     '从清音寺下来之后，天色便一日比一日暗得早了。'),

    # ch15霜钟→ch16秋收
    ('ch16',
     '山脚的稻田在九月尾全黄了',
     '霜钟的余音还在山谷里荡着，山脚的稻子便全熟了。'),

    # ch16秋收→ch17除夕
    ('ch17',
     '洛城的除夕有三件事',
     '收了稻子，日子便一天天短下去，转眼就是除夕。'),

    # ch21雪夜→ch22洛城四季图
    ('ch22',
     '洛城的春天是从洛水边开始的',
     '雪夜的脚印被新雪填平之后，洛城的春天便从洛水边一寸一寸地醒了过来。'),

    # ch22洛城四季图→ch23灯市
    ('ch23',
     '洛城的元宵灯市，不是一夜',
     '四季转过一圈，元宵的灯市便挂满了南门正街。'),

    # ch23灯市→ch24市井
    ('ch24',
     '洛城的西市是整座城最早醒来的地方',
     '灯市的最后一盏灯在天亮前灭了。'),

    # ch25市声→ch26灯谜会
    ('ch26',
     '雁回山庄每年上元节都办灯谜会',
     '市声从早到晚不停，而上元节一到，雁回山庄的灯谜会便等着另一种热闹。'),

    # ch26灯谜会→ch27渡口
    ('ch27',
     '洛河上的渡口，从上游往下依次是',
     '灯谜会散了之后，洛河上的渡口便迎来了又一年的春水。'),

    # ch28酒约→ch29旧匾
    ('ch29',
     '沈府大门上有一块匾',
     '酒约之后不久，秋白回了一趟沈府老宅。'),

    # ch30残简→ch31断碑
    ('ch31',
     '通往野寺的半路上有一块断裂的石碑',
     '残简里的"有缘"二字，让秋白想起了半路上那块断碑。'),
]

total = 0
for ch_id, search_text, bridge_sentence in bridges:
    # 定位章节
    ch_pos = html.find('<h2 id="%s">' % ch_id)
    if ch_pos < 0:
        print('ERR: cannot find %s' % ch_id)
        continue

    # 找到第一个<p>的位置
    first_p = html.find('<p>', ch_pos)
    first_p_class = html.find('<p style=', ch_pos)
    if first_p_class >= 0 and (first_p < 0 or first_p_class < first_p):
        first_p = first_p_class

    if first_p < 0:
        print('ERR: no <p> in %s' % ch_id)
        continue

    # 确认search_text在第一个<p>内
    p_end = html.find('</p>', first_p)
    if p_end < 0:
        print('ERR: no </p> after first <p> in %s' % ch_id)
        continue

    first_p_content = html[first_p:p_end]
    if search_text not in first_p_content:
        print('WARN: search_text not found in %s first <p>' % ch_id)
        # 尝试在更广的范围找
        next_h2 = html.find('<h2 id="ch', ch_pos + 20)
        ch_context = html[ch_pos:next_h2 if next_h2 > 0 else ch_pos+5000]
        if search_text not in ch_context:
            print('  SKIP: cannot find search_text anywhere near %s' % ch_id)
            continue
        print('  Found search_text further in chapter, but not in first <p>')

    # 找到search_text在HTML中的确切位置
    search_pos = html.find(search_text, ch_pos)
    if search_pos < 0:
        print('SKIP: search_text not found for %s' % ch_id)
        continue

    # 在search_text之前插入桥接句（跟在<p>标签后面）
    # 找到search_text所在的<p>标签的>位置
    tag_end = html.rfind('>', first_p, search_pos)
    if tag_end < 0:
        print('SKIP: cannot find tag end for %s' % ch_id)
        continue

    # 检查tag_end到search_text之间是否已有内容
    between = html[tag_end+1:search_pos].strip()
    if between:
        # 已有内容，在search_text前插入桥接句+空格
        insert_pos = search_pos
        insert_text = bridge_sentence
    else:
        # 直接跟在标签后
        insert_pos = tag_end + 1
        insert_text = bridge_sentence

    html = html[:insert_pos] + insert_text + html[insert_pos:]
    total += 1
    print('%s: added "%s"' % (ch_id, bridge_sentence))

print('\nTotal bridges added: %d' % total)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Done: ' + html_path)
