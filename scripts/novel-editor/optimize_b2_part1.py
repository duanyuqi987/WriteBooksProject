"""
《清音寺居》深度叙事优化
组D+组E: 弱章充实 + 章节过渡 (优先执行，复杂度低)
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

SC = r'[零一二三四五六七八九十百千]+'
changes = []

# ============================================================
# 组D1: 添加inner-monologue到4章
# ============================================================

# D1-ch2 裁纸: add inner-monologue before end marker
inner_caizhi = '''\n
    <div class="inner-monologue">
      <p>裁纸的时候忽然想到——人这一辈子，不就是在不停地把自己裁成各种形状吗。小时候被父母裁，长大了被世道裁。只有在这清音寺里，没人裁你。纸是什么形状，裁出来就是什么形状。也许这就是"自在"的意思——不是没有边界，是边界由自己定。</p>
    </div>\n'''

ch2_start = html.find('<h2 id="ch2">')
ch2_end = html.find('<h2 id="ch3">', ch2_start)
ch2_content = html[ch2_start:ch2_end]
# Find end marker or last </p> before next chapter
end_pos = ch2_content.rfind('（完）')
if end_pos < 0:
    end_pos = ch2_content.rfind('</p>')
if end_pos > 0:
    html = html[:ch2_start + end_pos] + inner_caizhi + html[ch2_start + end_pos:]
    changes.append('D1-ch2: added inner-monologue (裁纸)')

# D1-ch142 种瓜
inner_zhonggua = '''\n
    <div class="inner-monologue">
      <p>种瓜这件事——你急不得。你把种子埋进土里，浇了水，剩下的不是你能控制的。阳光、雨水、温度、土壤里的虫子——这些都在替你做决定。老孙常说"种瓜得瓜"，但我看他种了一辈子瓜，也种出了不少"没瓜"。所以这话的意思也许不是因果报应——而是你得先种下去，得不得瓜是另一回事。重要的不是瓜，是种。</p>
    </div>\n'''

ch142_start = html.find('<h2 id="ch142">')
ch142_next = html.find('<h2 id="ch143">', ch142_start)
ch142_content = html[ch142_start:ch142_next]
end_pos142 = ch142_content.rfind('（完）')
if end_pos142 < 0:
    end_pos142 = ch142_content.rfind('</p>')
if end_pos142 > 0:
    html = html[:ch142_start + end_pos142] + inner_zhonggua + html[ch142_start + end_pos142:]
    changes.append('D1-ch142: added inner-monologue (种瓜)')

# D1-ch145 晚钟
inner_wanzhong = '''\n
    <div class="inner-monologue">
      <p>钟声不是声音——是时间本身在说话。每一记钟声都在说"此刻"——不是上一刻，不是下一刻，就是敲下去的那一瞬间。等你听到了，那个瞬间已经过去了。所以钟声其实是"过去"在跟"现在"打招呼。老孙敲了几十年钟——他不是在报时，是在跟每一个"此刻"告别。</p>
    </div>\n'''

ch145_start = html.find('<h2 id="ch145">')
ch145_next = html.find('<h2 id="ch146">', ch145_start)
ch145_content = html[ch145_start:ch145_next]
end_pos145 = ch145_content.rfind('（完）')
if end_pos145 < 0:
    end_pos145 = ch145_content.rfind('</p>')
if end_pos145 > 0:
    html = html[:ch145_start + end_pos145] + inner_wanzhong + html[ch145_start + end_pos145:]
    changes.append('D1-ch145: added inner-monologue (晚钟)')

# D1-ch149 换衣
inner_huanyi = '''\n
    <div class="inner-monologue">
      <p>换衣服这件事——每次换季都要做一遍，做了一辈子。但每次把冬衣收进箱子的时候，还是会想：这件衣服下一次拿出来的时候，穿它的人还是"我"吗。夏天的人和冬天的人不是同一个——夏天的人轻了、薄了、热了，冬天的人重了、厚了、缩了。衣服知道这个秘密——它在箱子里等了你一个夏天，秋天拿出来的时候，它替你记得上一个冬天的体温。</p>
    </div>\n'''

ch149_start = html.find('<h2 id="ch149">')
ch149_next = html.find('<h2 id="ch150">', ch149_start)
if ch149_next < 0:
    ch149_next = html.find('<div class="divider">· 尾声 ·</div>', ch149_start)
ch149_content = html[ch149_start:ch149_next]
end_pos149 = ch149_content.rfind('（完）')
if end_pos149 < 0:
    end_pos149 = ch149_content.rfind('</p>')
if end_pos149 > 0:
    html = html[:ch149_start + end_pos149] + inner_huanyi + html[ch149_start + end_pos149:]
    changes.append('D1-ch149: added inner-monologue (换衣)')


# ============================================================
# 组D2: 扩展超短章
# ============================================================

# D2-ch149 换衣: add sensory details before the inner-monologue
# Find and expand the existing body paragraph
ch149_para = html.find('立夏当天', ch149_start)
if ch149_para > 0:
    # Find the period after the existing description
    old_text = '换衣不是换布——是换一种身体跟世界相处的方式——冬天——衣服是你的堡垒——夏天——衣服是你的影子。'
    new_text = '换衣不是换布——是换一种身体跟世界相处的方式。冬天——衣服是你的堡垒——棉袍裹在身上，密不透风，每一步都带着布的重量和棉的厚度——你感觉自己是一颗被层层包裹的种子。夏天——衣服是你的影子——薄薄的麻布贴在皮肤上，风一吹就鼓起来，你觉得自己变轻了，轻到可以被一阵风带走。冬天，你用衣服把自己藏起来；夏天，你让自己被风吹散。一年两次的换衣——是身体在跟世界重新谈判距离。'
    if old_text in html:
        html = html.replace(old_text, new_text, 1)
        changes.append('D2-ch149: expanded body text (换衣)')

# D2-ch150 听蝉/闻蝉: expand the metaphor layer
ch150_before = html.find('立夏后第三天', html.find('<h2 id="ch150">'))
if ch150_before > 0:
    # Add a paragraph about the meaning of cicada song
    old_p150 = '那只蝉——选在午后最热的时段——忽然就响了——"吱———"一声长鸣——拖了十几秒——然后停了。'
    new_p150 = '那只蝉——选在午后最热的时段——忽然就响了——"吱———"一声长鸣——拖了十几秒——然后停了。像是它攒了一整个春天的沉默，在这一口气里全部还给了夏天。'
    if old_p150 in html:
        html = html.replace(old_p150, new_p150, 1)

    # Add metaphor paragraph after existing content about cicadas
    cicada_end = html.find('夏天的第一声蝉鸣——是热的宣言。', ch150_before)
    if cicada_end > 0:
        extra_p = '\n\n    <p>蝉这种生物很怪——它在黑暗的土里活了七年，钻出来之后只活一个夏天。七年暗无天日，换一个夏天的阳光。它那么拼命地叫——也许不是在唱歌，是在数日子。每一声都是在说：我还在。我还在这里。夏天还没结束。</p>'
        insert_at = cicada_end + len('夏天的第一声蝉鸣——是热的宣言。')
        # Find next tag
        next_tag = html.find('>', insert_at)
        if html[next_tag-4:next_tag] == '</p>':
            insert_at = next_tag + 1
            html = html[:insert_at] + extra_p + html[insert_at:]
            changes.append('D2-ch150: expanded cicada metaphor (闻蝉)')

# D2-ch91 迎夏: add sensory details
ch91_start = html.find('<h2 id="ch91">')
ch91_text = '老孙在厨房里忙活——他在煮一种特别的东西——"立夏饭"。'
ch91_new = '老孙在厨房里忙活——他在煮一种特别的东西——"立夏饭"。灶膛里的火比平时旺——火舌舔着锅底，锅里的水咕嘟咕嘟冒着泡——蒸腾出来的水汽里带着新米特有的清甜味，混着柴火的松香。厨房比平时热了好几度——老孙的额头上沁出了细密的汗珠。但他是高兴的——每年立夏这天他都是高兴的。'

if ch91_text in html and ch91_start > 0:
    html = html.replace(ch91_text, ch91_new, 1)
    changes.append('D2-ch91: expanded sensory details (迎夏)')


# ============================================================
# 组E1: 相邻章节因果桥接(在章节开头增加呼应)
# ============================================================

# E1-1: ch3 晒书 — connect to ch2/补瓦
# After ch2 H2, add a bridge in ch3's opening
ch3_h2 = '<h2 id="ch3">'
ch3_h2_pos = html.find(ch3_h2)
if ch3_h2_pos > 0:
    # Find the first <p> after ch3 H2
    first_p3 = html.find('<p>', ch3_h2_pos)
    if first_p3 > 0:
        bridge = '<p>补完瓦的第三天，是个大晴天——老孙说正好晒书。天不等人，太阳不等书——说晒就得晒。</p>\n\n    '
        # Insert before first existing paragraph
        html = html[:first_p3 + 3] + bridge + html[first_p3 + 3:]
        changes.append('E1-ch3: added bridge (补瓦→晒书)')

# E1-2: ch4 补瓦 — connect to ch3 晒书
ch4_h2 = '<h2 id="ch4">'
ch4_h2_pos = html.find(ch4_h2)
if ch4_h2_pos > 0:
    first_p4 = html.find('<p>', ch4_h2_pos)
    if first_p4 > 0:
        bridge4 = '<p>晒完了书，老孙抬头看了看大殿的屋脊——"瓦又松了几片。"他像是自言自语，也像是对那些瓦说的。瓦不会回答，但老孙知道它们的意思——该补了。</p>\n\n    '
        html = html[:first_p4 + 3] + bridge4 + html[first_p4 + 3:]
        changes.append('E1-ch4: added bridge (晒书→补瓦)')

# E1-3: ch18 刷墙 — connect to ch17 理香
ch18_h2 = '<h2 id="ch18">'
ch18_h2_pos = html.find(ch18_h2)
if ch18_h2_pos > 0:
    first_p18 = html.find('<p>', ch18_h2_pos)
    if first_p18 > 0:
        bridge18 = '<p>香房的香料整理好了之后——老孙的鼻子比平时灵了好几倍——他站在禅房门口闻了闻，皱起眉头："霉味。该刷墙了。"在山里住了几十年的人，鼻子能闻出空气里最细微的变化——水气重了、木头朽了、墙霉了——每一样他都能在别人察觉之前先闻出来。</p>\n\n    '
        html = html[:first_p18 + 3] + bridge18 + html[first_p18 + 3:]
        changes.append('E1-ch18: added bridge (理香→刷墙)')

# E1-4: ch25 补经 — connect to ch24 捡柴
ch25_h2 = '<h2 id="ch25">'
ch25_h2_pos = html.find(ch25_h2)
if ch25_h2_pos > 0:
    first_p25 = html.find('<p>', ch25_h2_pos)
    if first_p25 > 0:
        bridge25 = '<p>柴房满了——过冬的柴火够用了。老孙拍了拍手上的木屑，走进了藏经阁。他在最里面那排书架前站了很久——手指从一本本经书的脊背上滑过去，最后停在一本快要散架的《楞严经》上。"该补经了。"他说这话的时候声音比平时轻——像是怕惊动书页里睡着了的字。</p>\n\n    '
        html = html[:first_p25 + 3] + bridge25 + html[first_p25 + 3:]
        changes.append('E1-ch25: added bridge (捡柴→补经)')

# E1-5: ch42 煎药 — connect to ch41 施药
ch42_h2 = '<h2 id="ch42">'
ch42_h2_pos = html.find(ch42_h2)
if ch42_h2_pos > 0:
    first_p42 = html.find('<p>', ch42_h2_pos)
    if first_p42 > 0:
        bridge42 = '<p>给山下的人施完了药——药柜空了一小半。但老孙的手没有停——他转身从另一个抽屉里抓出一把黄芪、几片麦冬、几块桔梗——这是沈秋白的方子。每个月逢五逢十施药给村民，但沈秋白的药——每天都得煎。</p>\n\n    '
        html = html[:first_p42 + 3] + bridge42 + html[first_p42 + 3:]
        changes.append('E1-ch42: added bridge (施药→煎药)')

# E1-6: ch50 送别 — connect to ch49 论道
ch50_h2 = '<h2 id="ch50">'
ch50_h2_pos = html.find(ch50_h2)
if ch50_h2_pos > 0:
    first_p50 = html.find('<p>', ch50_h2_pos)
    if first_p50 > 0:
        bridge50 = '<p>那晚论道之后——沈秋白在院子里又多坐了一会儿。月光把银杏树的影子投在地上——枝桠的剪影像一张摊开的地图。寂声不知道他在看什么——也许是看树，也许是看月亮，也许是在看一条只有他自己能看见的路。第二天一早——沈秋白说他要下山了。</p>\n\n    '
        html = html[:first_p50 + 3] + bridge50 + html[first_p50 + 3:]
        changes.append('E1-ch50: added bridge (论道→送别)')

# E1-7: ch76 重逢 — connect to ch75 归途
ch76_h2 = '<h2 id="ch76">'
ch76_h2_pos = html.find(ch76_h2)
if ch76_h2_pos > 0:
    first_p76 = html.find('<p>', ch76_h2_pos)
    if first_p76 > 0:
        bridge76 = '<p>寂声从洛城回来之后——人瘦了一圈，但眼睛亮了很多。他没有跟老孙说太多洛城的事——只是在晚饭时说了一句："洛城的人太多了。"老孙点点头，没有追问。三个月后——夏天——银杏树满树绿荫的时候——沈秋白真的回来了。</p>\n\n    '
        html = html[:first_p76 + 3] + bridge76 + html[first_p76 + 3:]
        changes.append('E1-ch76: added bridge (归途→重逢)')

# E1-8: ch119 忍寒 — connect to ch118 拥衾
ch119_h2 = '<h2 id="ch119">'
ch119_h2_pos = html.find(ch119_h2)
if ch119_h2_pos > 0:
    first_p119 = html.find('<p>', ch119_h2_pos)
    if first_p119 > 0:
        bridge119 = '<p>被子再厚——也有不够的时候。最冷的那几个夜里——不是被子不够暖和——是寒气从墙壁、地板、窗缝里渗进来——围着你——像一盆冷水慢慢浸透一张纸。拥衾是被动的抵御，忍寒是主动的承受。老孙说这两件事不一样。</p>\n\n    '
        html = html[:first_p119 + 3] + bridge119 + html[first_p119 + 3:]
        changes.append('E1-ch119: added bridge (拥衾→忍寒)')


# ============================================================
# 组E2: 季节感知线索
# ============================================================

# E2-1: ch120 送寒 — add winter→spring transition notice
ch120_h2_pos = html.find('<h2 id="ch120">')
if ch120_h2_pos > 0:
    # Find the first body paragraph
    first_body = html.find('<p>', html.find('</h2>', ch120_h2_pos))
    if first_body > 0:
        season_hint = '<p>大寒那天早上——老孙推开山门——发现门外的石阶上——在砖缝里——冒出了一星绿色。不是苔藓（苔藓冬天也是绿的），是一株荠菜的嫩芽——只有两片叶子——小得几乎看不见。老孙蹲下来看了很久——然后站起来，自言自语："它在送寒了。"</p>\n\n    '
        html = html[:first_body + 3] + season_hint + html[first_body + 3:]
        changes.append('E2-ch120: added spring hint (冬→春)')

# E2-2: ch90 春尽 → ch91 迎夏 transition
ch90_end_marker = html.find('（完）', html.find('<h2 id="ch90">'))
if ch90_end_marker > 0:
    add_text = '\n    <p>那天傍晚——寂声在院子里闻到了一股不一样的气味——不是春天的花香（桃花早就谢了），而是一种更浓的、带着青草汁液味的暖风。夏天已经在路上了。</p>\n'
    html = html[:ch90_end_marker + len('（完）')] + add_text + html[ch90_end_marker + len('（完）'):]
    changes.append('E2-ch90: added summer hint (春→夏)')

# E2-3: ch147 送春 → ch148 立夏
ch147_end = html.find('（完）', html.find('<h2 id="ch147">'))
if ch147_end > 0:
    bridge147 = '\n    <p>第二天早上——寂声醒来——发现空气变了。不是温度（温度差不多），是一种说不清的东西——也许只是光的颜色——也许只是一阵风的方向——但身体知道——春天已经走了。</p>\n'
    html = html[:ch147_end + len('（完）')] + bridge147 + html[ch147_end + len('（完）'):]
    changes.append('E2-ch147: added season transition (春→夏)')

# ============================================================
# Save
# ============================================================
with open(B2_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Applied {len(changes)} changes:")
for c in changes:
    print(f"  {c}")

# Quick verify
ch_count = len(re.findall(r'<h2 id="ch(\d+)">', html))
print(f"\nChapter count: {ch_count}")
ids = [int(x) for x in re.findall(r'<h2 id="ch(\d+)">', html)]
assert ids == list(range(1, 153)), f'ID mismatch!'
print("IDs: continuous ch1-ch152 OK")
