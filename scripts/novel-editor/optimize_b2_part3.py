"""
《清音寺居》深度叙事优化 Part 3
组C: 填充叙事空白 + D3: ch152结尾检查
"""
import re
import os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

changes = []

def insert_paragraph(html, ch_id, para_text):
    """Insert a paragraph before the end marker of a chapter."""
    pos = html.find(f'<h2 id="ch{ch_id}">')
    if pos < 0:
        return html, False
    content_end = html.find('（完）', pos)
    if content_end < 0:
        next_h2 = html.find('<h2 id="ch', pos + 20)
        if next_h2 < 0:
            next_h2 = html.find('<footer', pos)
            if next_h2 < 0:
                next_h2 = html.find('<div class="divider">· 尾声 ·</div>', pos)
        content = html[pos:next_h2] if next_h2 > 0 else html[pos:]
        last_p = content.rfind('</p>')
        if last_p > 0:
            content_end = pos + last_p
    if content_end < 0:
        return html, False
    p = f'\n    <p>{para_text}</p>\n'
    return html[:content_end] + p + html[content_end:], True

def insert_after_text(html, search_text, insert_text):
    """Insert text after a specific text match."""
    pos = html.find(search_text)
    if pos < 0:
        return html, False
    insert_at = pos + len(search_text)
    return html[:insert_at] + insert_text + html[insert_at:], True


# ============================================================
# 组C1: 沈秋白背景碎片化揭示 (4处)
# ============================================================

# C1-ch42 煎药: 老孙暗示沈秋白的伤不仅是身体
html, ok = insert_paragraph(html, 42,
    "老孙煎药的时候格外安静——不像捣药时那样会自言自语地念药名。寂声有一次问他——为什么沈秋白的药要煎这么久。老孙把蒲扇从灶口拿开——看着药罐里翻腾的褐色汤液——说了一句寂声没太听懂的话：'肺里的病——有时候不是肺的问题。'说完又继续扇火——好像什么都没说过。寂声没有再问——但他记住了这句话——记了很久。"
)
if ok: changes.append('C1-ch42: added hint about Shen deeper wound (煎药)')

# C1-ch49 论道: 沈秋白无意提及朝中往事
shen_says_old = '沈秋白忽然问——不是问老孙——是问夜空：'
if shen_says_old in html:
    # This is the key dialogue moment in ch49
    shen_says_new = '沈秋白忽然问——不是问老孙——是问夜空——他的语气里有一种寂声之前没听到过的东西——不是悲伤——不是愤怒——是一种很淡的疲倦——像是在朝廷里说了太多话之后剩下来的那种安静：'

    if shen_says_old in html:
        html = html.replace(shen_says_old, shen_says_new, 1)

    # Add a line where Shen mentions his past
    html, ok = insert_after_text(html,
        '沈秋白忽然问——不是问老孙——',
        '是问夜空——他的语气里有一种寂声之前没听到过的东西——不是悲伤——不是愤怒——是一种很淡的疲倦——像是在朝廷里说了太多话之后剩下来的那种安静：')
    if ok:
        changes.append('C1-ch49: added Shen past hint (论道)')

# Actually let me handle ch49 more carefully
# Check what's there now
ch49_pos = html.find('<h2 id="ch49">')
ch49_next = html.find('<h2 id="ch50">', ch49_pos)
ch49_content = html[ch49_pos:ch49_next]

# Add an additional paragraph near the end
html, ok = insert_paragraph(html, 49,
    "沈秋白后来不小心说了一句话——说完就沉默了。他说：'在朝堂上站久了——会忘记一棵树是怎么长的。树不用开会——不用写奏折——不用揣摩圣意——树只需要往土里扎根——往天上长——每年春天发出新叶——秋天落下来——第二年再来。人为什么做不到？'他不是在问谁——他只是把这句话放在月光底下——让它自己晾着。"
)
if ok: changes.append('C1-ch49: added Shen court reflection (论道)')

# C1-ch51 盼信: 第一封信透露沈秋白在洛城处境
html, ok = insert_paragraph(html, 51,
    "第一封信里——沈秋白提到他的旧宅已经封了——'庭前那棵老桂花树——今年没开花——不知是因为旱——还是因为没人看它。'寂声反复读这句话——觉得沈秋白不是在写树——是在写自己。一个人在山下——守着封了的旧宅——等着不知什么时候才能了结的事——庭前的桂花树不开花——他也不开花。"
)
if ok: changes.append('C1-ch51: added Shen letter detail (盼信)')

# C1-ch77 叙旧: 沈秋白简述下山经历
html, ok = insert_paragraph(html, 77,
    "沈秋白说得很少——但寂声从他的话里拼出了一幅图：下山之后——他在洛城住了半年——处理了一些'需要了结的事'——然后就往南走——没有目的地——只是走。'走到一条河边——觉得水好——就多住了几天。走到一座山前——觉得山像清音寺的大雪山——就拐进去了——住了一个多月——帮庙里的老和尚抄了好几本经。'他说这些的时候语气很轻——像是在说别人的事。但寂声注意到——他说到'抄经'的时候——手指在桌上比划了一下写字的手势——那是肌肉记忆——比他说的话更诚实。"
)
if ok: changes.append('C1-ch77: added Shen journey detail (叙旧)')


# ============================================================
# 组C2: 关键转折扩展 (3处, ch75 already done in B1)
# ============================================================

# C2-ch50 送别: 增加送别后的空寂感
html, ok = insert_paragraph(html, 50,
    "沈秋白走后——寂声在那棵银杏树下站了很久。树是光秃秃的——冬天的银杏树像一把倒插在土里的扫帚——枝桠朝天——没有一片叶子替他挡住冷风。他低头看了看自己站的地方——沈秋白每天早上在这里站一刻钟——脚下的石板被踩得比旁边的更光滑。寂声忽然发现——一个人走了——但他站过的地方还在——那些被压紧了的泥土和被磨光了的石板——都是他存在过的证据。"
)
if ok: changes.append('C2-ch50: added emptiness after farewell (送别)')

# C2-ch76 重逢: 增加重逢时的细节描写
chongfeng_pos = html.find('沈秋白真的回来了', html.find('<h2 id="ch76">'))
if chongfeng_pos > 0:
    old_text = '沈秋白真的回来了。'
    new_text = '沈秋白真的回来了。他站在山门口——穿着一件洗旧了的灰布衫——比下山前瘦了一些——但气色比之前好了很多——脸上不再是那种病恹恹的苍白——而是一种被日光和风打磨过的微褐色。他肩上斜挎着一个布包袱——手里拄着一根竹杖——看起来不像回寺的居士——更像走了很远的路终于到了家的行路人。'
    html = html.replace(old_text, new_text, 1)

    # Add more reunion detail
    html, ok = insert_paragraph(html, 76,
        "寂声蹲在菜地里——满手是泥——忘了站起来。沈秋白走到菜地边上——低头看了一眼他手里的草——说：'杂草拔得很好——不过那棵是萝卜苗。'寂声低头一看——手边那棵被他当成杂草的小苗——叶子被揪了一半——歪歪倒倒地戳在土里。两个人同时笑了。老孙从厨房里探出头来——看了一眼——又缩回去了——什么也没说。但寂声听见厨房里传来了案板切菜的声音——比平时更快更勤——老孙在用刀表达语言表达不了的东西。"
    )
    changes.append('C2-ch76: expanded reunion detail (重逢)')

# C2-ch147 送春: 增加三人对"循环与告别"的对话 (this is the second 送春, the proper one)
# First check if there's content to expand
ch147_pos = html.find('<h2 id="ch147">')
ch147_next = html.find('<h2 id="ch148">', ch147_pos)
if ch147_next < 0:
    ch147_next = html.find('<footer', ch147_pos)
if ch147_next < 0:
    ch147_next = html.find('<div class="divider">· 尾声 ·</div>', ch147_pos)

html, ok = insert_paragraph(html, 147,
    "晚饭后——三个人又坐在院子里。沈秋白忽然说——这是他在清音寺过的第二个春天——'去年春天我大部分时间躺着——今年我能坐着了。明年——我也许能站着。'老孙笑了一声——说：'后年你就可以帮寂声拔萝卜苗了。'寂声假装生气——'我已经会分萝卜苗和杂草了。'沈秋白点点头——认真地说：'春天每年都来——但我们不是每年都能看到它。去年从床边的小窗户看——今年坐在院子里看——春天是同一个春天——看春天的人——已经不一样了。'"
)
if ok: changes.append('C2-ch147: added trio dialogue (送春)')


# ============================================================
# D3: ch152 无尽 — 检查结尾融入度
# ============================================================
ch152_pos = html.find('<h2 id="ch152">')
ch152_next = html.find('<footer', ch152_pos)
if ch152_next < 0:
    ch152_next = len(html)
ch152_content = html[ch152_pos:ch152_next]

# Check if the R3 narrative closure (尾声) is present and flows well
if '· 尾声 ·' in ch152_content:
    # It's there. Check if there's a natural transition before it
    weisheng_pos = ch152_content.find('· 尾声 ·')
    before_weisheng = ch152_content[weisheng_pos - 200:weisheng_pos]
    # If the transition is too abrupt, add a bridge paragraph
    if '秋天' not in before_weisheng and '银杏' not in before_weisheng:
        # Find the position right before 尾声 in the main html
        abs_weisheng = ch152_pos + weisheng_pos
        bridge = '\n\n    <p>立夏过后——山里进入了漫长的、饱满的夏天。蝉声灌满了整座山——银杏树的叶子从嫩绿变成了深绿——菜园里的南瓜藤爬满了竹篱笆——瓜叶大得像一把一把的蒲扇。寂声在院子里磨墨——砚台里的墨汁在夏天的空气里干得特别快——得不停地加水。沈秋白在廊檐下看书——老孙在菜地里拔草。三个人保持着一种不用说话的默契——各自做各自的事——却又在同一个院子里——呼吸着同一片树荫漏下来的光影。日子就是这样——不是每一天都有意义——但每一天都是日子。银杏叶年年黄。故事——会一代一代讲下去。</p>\n'
        html = html[:abs_weisheng] + bridge + html[abs_weisheng:]
        changes.append('D3-ch152: added transition before 尾声 (无尽)')
        print(f"  Added bridge before 尾声")

# Also check that the ending (全书完) flows from the narrative
if '（全书完）' in ch152_content:
    quan_end = ch152_content.find('（全书完）')
    # Make sure there's a natural flow before the end
    before_end = ch152_content[quan_end - 100:quan_end]
    if '春天' not in before_end and '闻蝉' not in before_end:
        abs_end = ch152_pos + quan_end
        final_touch = '\n    <p>愿读到这里的你——也能找到属于你自己的"清音寺"——一个能让你安心洗石、种豆、闻蝉、等春天的地方。</p>\n\n'
        # Check if this line already exists
        if '找到属于你自己的' not in ch152_content:
            html = html[:abs_end] + final_touch + html[abs_end:]
            changes.append('D3-ch152: added final blessing line')
        print(f"  Added final blessing")


# ============================================================
# Save
# ============================================================
with open(B2_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nApplied {len(changes)} changes:")
for c in changes:
    print(f"  {c}")

ch_count = len(re.findall(r'<h2 id="ch(\d+)">', html))
print(f"\nChapter count: {ch_count}")
ids = [int(x) for x in re.findall(r'<h2 id="ch(\d+)">', html)]
assert ids == list(range(1, 153)), f'ID mismatch!'
print("IDs: continuous ch1-ch152 OK")
