"""
《清音寺居》深度叙事优化 Part 2
组A: 增强沈秋白存在感 + 组B: 强化情感暗线
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

changes = []

def find_ch_end(html, ch_id):
    """Find position right before next chapter or end marker."""
    pos = html.find(f'<h2 id="ch{ch_id}">')
    next_h2 = html.find('<h2 id="ch', pos + 20)
    if next_h2 < 0:
        next_h2 = html.find('<footer', pos)
    if next_h2 < 0:
        next_h2 = html.find('<div class="divider">· 尾声 ·</div>', pos)
    return pos, next_h2 if next_h2 > 0 else pos + 5000

def insert_at_end_marker(html, ch_id, insert_text):
    """Insert text before the end marker (完) of a chapter."""
    pos, _ = find_ch_end(html, ch_id)
    if pos < 0:
        return html, False
    # Find （完） in this chapter's content
    content_end = html.find('（完）', pos)
    if content_end < 0:
        # Fallback: find last </p>
        next_h2 = html.find('<h2 id="ch', pos + 20)
        if next_h2 < 0:
            next_h2 = html.find('<footer', pos)
        content = html[pos:next_h2] if next_h2 > 0 else html[pos:]
        last_p = content.rfind('</p>')
        if last_p > 0:
            content_end = pos + last_p
    if content_end < 0:
        return html, False
    return html[:content_end] + insert_text + html[content_end:], True

def insert_inner_monologue(html, ch_id, monologue_text):
    """Add inner-monologue div before end marker."""
    inner = f'\n\n    <div class="inner-monologue">\n      <p>{monologue_text}</p>\n    </div>\n'
    return insert_at_end_marker(html, ch_id, inner)

def insert_paragraph(html, ch_id, para_text):
    """Insert a paragraph before the end marker."""
    p = f'\n    <p>{para_text}</p>\n'
    return insert_at_end_marker(html, ch_id, p)

def insert_at_chapter_start(html, ch_id, para_text):
    """Insert a paragraph right after the H2 heading."""
    pos = html.find(f'<h2 id="ch{ch_id}">')
    if pos < 0:
        return html, False
    first_p = html.find('<p>', pos)
    if first_p < 0:
        return html, False
    bridge = f'<p>{para_text}</p>\n\n    '
    return html[:first_p + 3] + bridge + html[first_p + 3:], True


# ============================================================
# 组A1: 老孙独白章节注入寂声视角 (10章)
# ============================================================

# A1-ch34 收蜜: Add Ji's observation
html, ok = insert_paragraph(html, 34,
    "寂声站在梯子下面——仰着头看老孙在椴树的枝叶间小心翼翼地割蜂巢。阳光从树叶的缝隙里漏下来——在寂声的脸上画了一道一道的光斑。他忽然想——老孙在这棵树下收了这么多年蜜，那些蜜蜂认得他吗。大概是认得的——因为它们从来没有蜇过他。"
)
if ok: changes.append('A1-ch34: added 寂声 observation (收蜜)')

# A1-ch39 晒药: Add Ji's participation
html, ok = insert_paragraph(html, 39,
    "寂声蹲在地上帮老孙翻药材——当归要翻面了，黄芪还差一点。他翻着翻着忽然发现——每一味药材在太阳底下都会发出自己独特的气味。当归是甜的，黄芪是土味的，甘草是焦糖味的——这些气味平时藏在药柜的抽屉里，只有晒的时候才肯出来见阳光。"
)
if ok: changes.append('A1-ch39: added 寂声 participation (晒药)')

# A1-ch40 捣药
html, ok = insert_paragraph(html, 40,
    "寂声试着捣了一会儿——石杵在石臼里转着圈，药材在下面咔咔地碎裂。他发现捣药有一种奇异的节奏——不是快，是匀。快一下慢一下——药末粗细不匀——入药时效力就不准。老孙接过石杵示范了一遍——手腕不动，是整个手臂在画圈。寂声看了一会儿——忽然觉得老孙不像在捣药——像在推磨——像在磨墨——像在做一切需要耐心的事。"
)
if ok: changes.append('A1-ch40: added 寂声 perspective (捣药)')

# A1-ch52 画壁: Add Ji watching the restoration
html, ok = insert_paragraph(html, 52,
    "寂声站在大殿门口——不敢进去——怕自己的影子落在壁画上。老孙爬在梯子上——手里拿着一支极细的毛笔——在观音的衣褶上一点一点地补色。他的动作很慢——慢到寂声几乎看不出笔尖在动。寂声忽然意识到——老孙不是在画——是在跟几百年前那个画师对话——一笔一笔地——隔着几百年的时光——说：我替你把颜色留住。"
)
if ok: changes.append('A1-ch52: added 寂声 watching (画壁)')

# A1-ch53 制香: Ji participates
html, ok = insert_paragraph(html, 53,
    "寂声被叫来帮忙搓香——把调好的香泥搓成细条，一根一根码在竹筛上。他搓了几根就发现——不是搓不直，是搓不匀——有的粗有的细——粗的烧得快——细的烧得慢——同一炉香烧出两个速度——佛前就不整齐了。老孙看了他一眼说：'不急——手稳心才稳。'寂声深吸一口气——重新开始——这一根终于搓匀了。"
)
if ok: changes.append('A1-ch53: added 寂声 participation (制香)')

# A1-ch61 播种: Ji helps
html, ok = insert_paragraph(html, 61,
    "寂声蹲在菜园边上——看着老孙把种子一粒一粒放进土里——每个穴三粒——不多不少。寂声问为什么是三粒——不是两粒也不是四粒。老孙说：'一粒怕不发芽——两粒怕只发一苗——三粒——总有一粒是最壮的。不是贪多——是给每颗种子一次被淘汰的机会。'寂声想了一会儿——觉得这话说的好像不止是种子。"
)
if ok: changes.append('A1-ch61: added 寂声 questioning (播种)')

# A1-ch71 寻泉: Ji helps find the spring
html, ok = insert_paragraph(html, 71,
    "寂声跟着老孙在后山找了两个时辰——拨开枯藤——爬过碎石坡——耳朵贴着岩壁听水声。老孙说寻泉不是用眼睛——是用耳朵和脚——耳朵听水的声音——脚底板感受地面的湿度。寂声趴在一块青石上听了很久——终于听到了——不是水流的哗哗声——是更细的——一种几乎听不见的、从石头深处传来的呜咽。'找到了。'寂声说。老孙笑了——那是寂声第一次靠自己找到一眼泉。"
)
if ok: changes.append('A1-ch71: added 寂声 helping (寻泉)')

# A1-ch91 迎夏
html, ok = insert_paragraph(html, 91,
    "寂声帮老孙烧火——火大了——米汤溢出来浇在灶沿上——嗞的一声。老孙没有责备他——只是用抹布擦了擦灶沿——把火调小了——说：'迎夏不用大火——大火是赶夏——小火才是迎。赶——夏天来得急，走得也急。迎——夏天慢慢进门——坐下来——喝完一碗立夏饭——就不走了。'"
)
if ok: changes.append('A1-ch91: added 寂声 helping (迎夏)')

# A1-ch108 煨芋: Ji shares the food
html, ok = insert_paragraph(html, 108,
    "寂声从灰里扒出两颗芋头——一颗递给老孙——一颗留给自己。掰开芋头——热气从里面冒出来——带着一种只有煨芋才有的焦香——烤焦的外皮下面——芋肉是粉粉的——沙沙的——含在嘴里不用嚼——用舌头一压就化开了。寂声吃着芋头——忽然很想让沈秋白也尝一口——他在洛城——这时候不知道有没有人给他煨芋头。"
)
if ok: changes.append('A1-ch108: added 寂声 sharing + 沈秋白 mention (煨芋)')

# A1-ch149 换衣: Ji's perspective already added in part1 with inner-monologue
# Additional: Ji notices Lao Sun's ritual
html, ok = insert_paragraph(html, 149,
    "寂声看着老孙把自己的旧棉袍叠好——不是随便折几下——是对齐了肩线、袖口、下摆——四四方方——像叠一封要寄给秋天的信。寂声忽然觉得——老孙对待衣服的态度，就是对待时间的态度：不丢、不弃、不赶、不拖——该来的时候穿上，该走的时候收好。"
)
if ok: changes.append('A1-ch149: added 寂声 observing 老孙 (换衣)')


# ============================================================
# 组A2: 沈秋白下山期间"信中人" (3章)
# ============================================================

# A2-ch58 望山: Ji reads Shen's letter while looking at mountains
html, ok = insert_paragraph(html, 58,
    "寂声走到望云台上——从怀里掏出一封折得整整齐齐的信——沈秋白两个月前托樵夫带上来的。信纸已经起了毛边——被翻看了太多次。信里只有几行字——但寂声每次读都能读出新的意思。沈秋白写道：'山下的月亮和山上是同一个——只是山下看它的人太多——它累了。'寂声抬头看了看天——白天——月亮还没出来——但他知道它在那里——在山的那一边——也在洛城的那一边。"
)
if ok: changes.append('A2-ch58: added letter reading (望山)')

# A2-ch64 午憩: Ji dreams of Shen
ji_line_start = html.find('老孙有一个习惯——每天午饭后要在禅房里躺一刻钟', html.find('<h2 id="ch64">'))
if ji_line_start > 0:
    # Insert a paragraph about Ji's own afternoon thoughts
    old_line = '老孙有一个习惯——每天午饭后要在禅房里躺一刻钟。不是睡——是"眯"。'
    new_line = '老孙有一个习惯——每天午饭后要在禅房里躺一刻钟。不是睡——是"眯"。寂声没有午睡的习惯——但今天中午他也在自己的禅房里闭了一会儿眼。半梦半醒之间——他听见院子里有脚步声——是那种不急不缓的——沈秋白特有的步伐——轻——但有分量。他睁开眼——院子是空的——只有银杏树叶在风里翻着银白色的背面。'
    html = html.replace(old_line, new_line, 1)
    changes.append('A2-ch64: added Ji dreaming of Shen (午憩)')

# A2-ch70 封笔: Ji remembers Shen's calligraphy
html, ok = insert_paragraph(html, 70,
    "寂声看着老孙把笔一支一支洗干净、挂好、罩上布——忽然想起沈秋白在寺里的时候——每天早晨写字——写完了也要洗笔——但沈秋白洗笔的动作和老孙不一样——沈秋白洗得慢——像是在跟笔告别——老孙洗得快——像是在跟笔说回头见。两个人的动作不一样——但寂声觉得——他们在做同一件事：对工具表示敬意。"
)
if ok: changes.append('A2-ch70: added Shen memory (封笔)')


# ============================================================
# 组A3: 新增寂声+沈秋白二人场景 (2处)
# ============================================================

# A3-ch43 夜读: Add duo scene after main content
html, ok = insert_paragraph(html, 43,
    "那天晚上——老孙早早回房歇了。寂声和沈秋白两个人坐在大殿的廊檐下——月光把院子里的石板照得发白——银杏树在月光里像是一棵银子打成的树。沈秋白忽然开口——不是对寂声说话——是自言自语：'我年轻的时候——以为人生最怕的是没有知己。后来才知道——最怕的是遇到了知己——然后又要各自走散。'寂声没有说话——他不知道怎么接——但他记住了这句话——记住了月光——记住了廊檐下两个人之间那一小片安静的黑暗。"
)
if ok: changes.append('A3-ch43: added Ji+Shen duo scene (夜读)')

# A3-ch103 寄远: Add duo scene walking under ginkgo tree
html, ok = insert_paragraph(html, 103,
    "晚饭后——沈秋白说想去银杏树下走走。寂声跟着他——两个人绕着银杏树走了一圈又一圈——银杏叶已经开始黄了——在暮色里泛着一种介于金色和灰色之间的光泽。沈秋白忽然停下来——伸手摸了摸树干——那上面有一道很深的裂纹——是老树皮在冬天冻裂之后留下的疤。'它在自己补自己。'沈秋白说。'树不像人——人受伤了会喊——树受伤了只是继续长。'寂声想了一会儿——说：'你也是。'沈秋白没有回答——但他碰了碰寂声的肩膀——很轻——像一片银杏叶落在肩上。"
)
if ok: changes.append('A3-ch103: added Ji+Shen duo scene (寄远)')


# ============================================================
# 组B1: 寂声成长弧 (7个节点)
# ============================================================

# B1-ch1 磨墨: Deepen Ji's initial confusion
mo_mo_old = '寂声第一次被安排磨墨时，他并不理解——'
mo_mo_new = '寂声第一次被安排磨墨时，他并不理解——为什么是他。寺里有好几个沙弥——为什么偏偏挑中了他来做这件看起来最枯燥的事。他不敢问老孙——只是垂着眼接过了墨锭——心想：也许师父是在考验我——也许磨完了就会让我做别的。后来他才发现——这个"别的"一直没有来。——'
if mo_mo_old in html:
    html = html.replace(mo_mo_old, mo_mo_new, 1)
    changes.append('B1-ch1: deepened initial confusion (磨墨)')

# B1-ch25 补经: Add insight about brokenness and wholeness
html, ok = insert_paragraph(html, 25,
    "补完那本《楞严经》之后——寂声看了很久自己的手——手上沾了浆糊和纸屑——但经书看起来比补之前更完整了。不是'完美'——是一页一页的残缺被另一双手接住了——继续往下讲它的故事。寂声忽然想——会不会人也像书——越老越容易破——但每破一次——就被人温柔地补一次——补到最后——那些补丁成了这本书最好看的部分。"
)
if ok: changes.append('B1-ch25: added brokenness insight (补经)')

# B1-ch57 独处: Expand from loss to independence
html, ok = insert_paragraph(html, 57,
    "第七天——寂声在磨墨的时候忽然停下来——看着砚台里那一圈一圈的墨痕——他意识到——磨墨的声音没有变——水缸里的水没有变——银杏树的叶子没有变——这个世界还在照常运转。沈秋白不在了——但清音寺还在——墨还在——墨要磨——字要写——明天的太阳还是会从东山升起来。他不是'不习惯'——他是不习惯自己已经习惯了。习惯失去——是失去的最后一步。走完这一步——剩下的不是空白——是继续。"
)
if ok: changes.append('B1-ch57: expanded independence turn (独处)')

# B1-ch67 临帖: Add self-questioning
html, ok = insert_paragraph(html, 67,
    "寂声写完一页——搁下笔——看着自己的字。进步是有的——但跟沈秋白的字比起来——还是差了一大截。他不气馁——因为他忽然发现了一个自己以前没想过的问题：他练字到底是为什么。是为了让沈秋白看到进步？还是为了字本身？为了别人做的事——做不久。为了自己的事——做不累。也许现在这两个原因都有——但他隐隐觉得——总有一天——'让沈秋白看到'这个理由会自己消失——然后'写字'本身会变成唯一的理由。"
)
if ok: changes.append('B1-ch67: added self-questioning (临帖)')

# B1-ch74 辞行: Expand determination
# Find existing content about Ji making his decision
ji_decision = html.find('他找到老孙——说自己也想下山一趟', html.find('<h2 id="ch74">'))
if ji_decision > 0:
    old_decision = '他找到老孙——说自己也想下山一趟。"不是离开——是辞行。"'
    new_decision = '他找到老孙——说自己也想下山一趟。说这句话之前——他在银杏树下站了一整个下午——把自己想说的话在心里排了好几遍——排到最后——只剩下最简单的这一句。他怕自己说多了会让人觉得他在找借口——说少了又显得不够郑重。最后他说出来的话是："不是离开——是辞行。"'
    html = html.replace(old_decision, new_decision, 1)
    changes.append('B1-ch74: expanded determination (辞行)')

# B1-ch75 归途: Expand Luo City experience
# Find the existing description and add more detail
luo_city_start = html.find('洛城和他记忆里的不太一样', html.find('<h2 id="ch75">'))
if luo_city_start > 0:
    old_luo = '洛城和他记忆里的不太一样——他之前在山上住了一年多，看惯了树、石、云、雾——忽然被丢进一个满是屋宇、车马、叫卖声的地方——'
    new_luo = '洛城和他记忆里的不太一样。他之前在山上住了一年多——看惯了树、石、云、雾——每一种东西都有它自己的节奏：树一年长一轮，石头几百年不动，云从这边飘到那边最快也要小半个时辰。忽然被丢进一个满是屋宇、车马、叫卖声的地方——他站在城门洞里——有些恍惚——像个刚醒过来的人——还在梦里和醒的边缘。'
    if old_luo in html:
        html = html.replace(old_luo, new_luo, 1)

    # Add a paragraph about his inner state in the city
    html, ok = insert_paragraph(html, 75,
        "他在洛城只停留了一天一夜——找到沈秋白的旧宅——宅门紧锁——门缝里塞了半年的灰尘。他在门口站了很久——想象沈秋白每天早晨推开这扇门——走过这条街——然后在某个路口停下来——看一眼远山——也许那时候他就在想：什么时候能回到清音寺。寂声没有找到沈秋白——但他找到了一种奇怪的确信：沈秋白不是逃避洛城——他是在清音寺找到了洛城给不了他的东西。"
    )
    changes.append('B1-ch75: expanded Luo City experience (归途)')

# B1-ch119 忍寒: Add insight about endurance
html, ok = insert_paragraph(html, 119,
    "寂声在禅房里坐了一夜——没有点灯——只是听着窗外的风声——从西边刮到东边——从屋顶刮过树梢——从这座山刮到那座山。天亮的时候——他发现自己还在——手指还能屈伸——呼吸还是热的。这具身体比他想象的要更能承受。冷会过去——就像热也会过去——但'承受过冷'这件事——不会过去。它变成你的一部分——一个在冬天的夜里被冻出来的——坚硬的核。"
)
if ok: changes.append('B1-ch119: added endurance insight (忍寒)')


# ============================================================
# 组B2: 三人关系层次 (3处)
# ============================================================

# B2-ch49 论道: Add Lao Sun's silent observation
html, ok = insert_paragraph(html, 49,
    "老孙坐在廊檐的另一头——手里的佛珠一颗一颗地捻着——不发一言。月光照不到他坐的那个角落——他的脸藏在阴影里——看不清表情。但寂声知道他在听。老孙有个本事——他能同时在场和不在场——听着你们的每一句话——却不打扰。很多年以后寂声才明白——这种沉默不是冷漠——是把空间让出来——让年轻人自己去发现——去碰撞——去产生自己的思想。真正的高明不是教你什么——而是让你以为是你自己想到的。"
)
if ok: changes.append('B2-ch49: added Lao Sun observation (论道)')

# B2-ch77 叙旧: Add inner states for all three
html, ok = insert_paragraph(html, 77,
    "寂声在旁边听着——偶尔插一两句。他发现一件有趣的事：老孙今晚的话比平时多了很多——而且每句话都带着笑。老孙平时不是不爱笑——只是笑的时候嘴角上扬一毫米就算笑过了——但今晚他的眼睛也在笑——眼角那几道皱纹比平时深了三倍。沈秋白也是——他的声音不再是养病时那种小心翼翼的——而是像一块被解冻的溪水——活过来了——带着被冻了一整个冬天之后重获自由的欢快。三个人在月光下说着闲话——没人提'回来后要待多久'——好像这个问题根本不需要问——清音寺的门是开着的——它从来没有关过。"
)
if ok: changes.append('B2-ch77: added three-character inner states (叙旧)')

# B2-ch107 话旧: Add deeper relationship understanding
html, ok = insert_paragraph(html, 107,
    "寂声忽然觉得——他们三个人之间的关系——不像师徒——不像朋友——不像主客——也许最接近的词是'同行者'。三个各自走了很远的路的人——在清音寺这棵银杏树下偶然停下来——发现彼此都在——于是决定多坐一会儿。没有谁在等谁——也没有谁在赶谁——就是刚好一起走了一段路。这段路可能很长——可能很短——没有人知道。但这不重要——重要的是走的时候——身边有人——脚步声不孤单。"
)
if ok: changes.append('B2-ch107: added relationship understanding (话旧)')


# ============================================================
# 组B3: 老孙的隐退线 (2处)
# ============================================================

# B3-ch80 斋戒: Add Lao Sun letting Ji handle things independently
html, ok = insert_paragraph(html, 80,
    "今年佛诞日的斋戒——老孙说让寂声来操持。'你在这寺里住了一年了——该你知道的规矩你都知道了——不该知道的你也该从'不知道'里自己学。'寂声有些紧张——但老孙说这话的时候语气很平淡——不像是在交代任务——像是在说一件理所当然的事。寂声后来才想明白——老孙是在退。不是退场——是退后一步——让寂声站到他前面去。一个好的师父——最后的任务——是让自己不再被需要。"
)
if ok: changes.append('B3-ch80: added Lao Sun stepping back (斋戒)')

# B3-ch145 晚钟: Ji rings the bell for the first time alone
# Insert after existing content about the bell
html, ok = insert_paragraph(html, 145,
    "今晚的晚钟——老孙让寂声来敲。寂声走到钟楼——拿起那根被无数双手磨光滑了的木杵——站了一息——然后对准钟的圆心撞了下去。第一声——轻了。第二声——太重了。第三声——刚好。钟声从钟楼飘出去——越过银杏树——越过山门——越过山谷——消失在对面的山体上。寂声忽然明白了老孙为什么让他敲——不是他敲得有多好——是这口钟总会换人的——在老孙的手还不能敲钟之前——先把它交出去。钟不会留恋敲钟的人——但敲钟的人会留恋钟。老孙把这份留恋——提前送给了寂声。"
)
if ok: changes.append('B3-ch145: added Ji ringing bell (晚钟)')


# ============================================================
# Save
# ============================================================
with open(B2_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Applied {len(changes)} changes:")
for c in changes:
    print(f"  {c}")

ch_count = len(re.findall(r'<h2 id="ch(\d+)">', html))
print(f"\nChapter count: {ch_count}")
ids = [int(x) for x in re.findall(r'<h2 id="ch(\d+)">', html)]
assert ids == list(range(1, 153)), f'ID mismatch!'
print("IDs: continuous ch1-ch152 OK")
