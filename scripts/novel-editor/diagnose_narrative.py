"""
宏观叙事结构诊断：情节弧线、因果链、情感节奏
"""
import re, os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
OUT = 'd:/ProgramWork/WriteBookProject/tmp_narrative_diag.txt'

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

chapters = re.findall(r'<h2 id="ch(\d+)">([^<]+)</h2>', html)

with open(OUT, 'w', encoding='utf-8') as f:
    # ============================================================
    # 1. 全书152章的情节骨架：谁在、做什么、发生了什么事
    # ============================================================
    f.write("=" * 70 + "\n")
    f.write("1. 情节骨架：逐章关键事件提取\n")
    f.write("=" * 70 + "\n\n")

    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        next_pos = html.find('<h2 id="ch', pos + 20)
        if next_pos < 0:
            next_pos = html.find('<footer', pos)
        content = html[pos:next_pos] if next_pos > 0 else html[pos:pos+5000]
        clean = re.sub(r'<[^>]+>', '', content)
        clean = re.sub(r'\s+', ' ', clean).strip()

        # Who's present
        has_ji = '寂声' in content
        has_shen = '秋白' in content
        has_sun = '老孙' in content
        chars = []
        if has_ji: chars.append('寂')
        if has_shen: chars.append('沈')
        if has_sun: chars.append('孙')
        who = '+'.join(chars) if chars else '?'

        # Extract first paragraph for summary
        first_p = clean[:150].replace('\n', ' ')

        # CJK count
        cjk = len(re.findall(r'[一-鿿]', content))

        f.write(f"ch{ch_num:03d} [{cjk:>5d}CJK] [{who}] {title}\n")
        f.write(f"       {first_p}...\n\n")

    # ============================================================
    # 2. 故事弧线分析
    # ============================================================
    f.write("\n" + "=" * 70 + "\n")
    f.write("2. 叙事弧线分析：关键转折点\n")
    f.write("=" * 70 + "\n\n")

    # Define narrative phases
    phases = [
        ("卷一：文房日常 (ch1-ch10)", 1, 10,
         "寂声初到清音寺，学习最基本的日常劳作"),
        ("卷二：寺中劳作 (ch11-ch30)", 11, 30,
         "深入寺务，与老孙建立师徒关系，沈秋白出现"),
        ("卷三：厨下烟火 (ch31-ch50)", 31, 50,
         "三人日常成形，沈秋白养病→病情好转→决定下山"),
        ("卷四：四季衣衫 (ch51-ch70)", 51, 70,
         "沈秋白下山期间(仅盼信维持)，寂声开始独立成长"),
        ("卷五：寺中人事 (ch71-ch90)", 71, 90,
         "寂声下山寻沈秋白→归来→沈秋白回归"),
        ("卷六：晨钟暮鼓 (ch91-ch110)", 91, 110,
         "三人重新聚合，季节从夏入秋冬"),
        ("卷七：冬藏时节 (ch111-ch140)", 111, 140,
         "深冬→春回，三人关系深化"),
        ("卷八：山中岁时 (ch141-ch152)", 141, 152,
         "春天→立夏，故事收束"),
    ]

    f.write("叙事阶段划分：\n\n")
    for phase_name, start, end, desc in phases:
        # Count key events in this phase
        f.write(f"[{phase_name}]\n")
        f.write(f"  范围: ch{start}-ch{end} ({end-start+1}章)\n")
        f.write(f"  主题: {desc}\n")
        # Character presence in phase
        shen_chs = 0
        ji_chs = 0
        sun_chs = 0
        all3 = 0
        total_cjk = 0
        for ch_id, title in chapters:
            ch_num = int(ch_id)
            if start <= ch_num <= end:
                pos = html.find(f'<h2 id="ch{ch_num}">')
                np = html.find('<h2 id="ch', pos + 20)
                if np < 0: np = html.find('<footer', pos)
                c = html[pos:np] if np > 0 else html[pos:pos+5000]
                if '寂声' in c: ji_chs += 1
                if '秋白' in c: shen_chs += 1
                if '老孙' in c: sun_chs += 1
                if '寂声' in c and '秋白' in c and '老孙' in c: all3 += 1
                total_cjk += len(re.findall(r'[一-鿿]', c))
        phase_chs = end - start + 1
        f.write(f"  寂声: {ji_chs}/{phase_chs}, 沈秋白: {shen_chs}/{phase_chs}, 老孙: {sun_chs}/{phase_chs}, 三人同在: {all3}/{phase_chs}\n")
        f.write(f"  小计CJK: {total_cjk:,}\n\n")

    # ============================================================
    # 3. 情感节奏分析：高潮与低谷
    # ============================================================
    f.write("=" * 70 + "\n")
    f.write("3. 情感节奏：CJK分布（叙事密度）\n")
    f.write("=" * 70 + "\n\n")

    # Find chapters with unusually high/low CJK
    cjk_list = []
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+10000]
        cjk = len(re.findall(r'[一-鿿]', c))
        cjk_list.append((ch_num, title, cjk))

    avg_cjk = sum(x[2] for x in cjk_list) / len(cjk_list)
    f.write(f"平均每章CJK: {avg_cjk:.0f}\n\n")

    f.write("最长的10章 (叙事密度高，可能是情感重点):\n")
    for ch_num, title, cjk in sorted(cjk_list, key=lambda x: -x[2])[:10]:
        f.write(f"  ch{ch_num:03d} {title}: {cjk} CJK\n")

    f.write("\n最短的10章 (叙事密度低，可能是过渡章):\n")
    for ch_num, title, cjk in sorted(cjk_list, key=lambda x: x[2])[:10]:
        f.write(f"  ch{ch_num:03d} {title}: {cjk} CJK\n")

    # ============================================================
    # 4. "故事"可读性检查
    # ============================================================
    f.write("\n" + "=" * 70 + "\n")
    f.write("4. 故事可读性：能否用一段话概括全书\n")
    f.write("=" * 70 + "\n\n")

    f.write("尝试概括：\n")
    f.write("寂声来到清音寺，跟随老孙学习寺庙日常。沈秋白——一位从朝廷退隐的肺病文人——也在此养病。三人从陌生到熟悉，在磨墨扫地煮粥看云的日复一日中，建立了超越师徒和友人的关系。沈秋白病愈下山了结旧事，寂声在独处中成长，最终下山寻他。沈秋白归来后，三人重新聚合——春去秋来，四季轮回，故事在无尽中收束。\n\n")

    f.write("核心情节驱动力检查：\n")
    f.write("  Q: 寂声为什么来清音寺？A: [需检查ch1是否有交代]\n")
    f.write("  Q: 沈秋白为什么来清音寺？A: [需检查早期章节]\n")
    f.write("  Q: 老孙为什么留在清音寺四十年？A: [需检查是否有背景]\n")
    f.write("  Q: 三人关系如何变化？A: ch1陌生→ch50送别→ch76重逢→ch152无尽\n")
    f.write("  Q: 最大的冲突/张力是什么？A: [需检查——可能缺乏明显冲突]\n")
    f.write("  Q: 结局解决了什么？A: 没有'解决'——是'无尽'的延续\n\n")

    # ============================================================
    # 5. 具体问题定位
    # ============================================================
    f.write("=" * 70 + "\n")
    f.write("5. 具体叙事问题定位\n")
    f.write("=" * 70 + "\n\n")

    # 5.1 检查ch1是否交代了寂声为何来寺
    ch1_pos = html.find('<h2 id="ch1">')
    ch2_pos = html.find('<h2 id="ch2">', ch1_pos)
    ch1_c = html[ch1_pos:ch2_pos]
    ch1_clean = re.sub(r'<[^>]+>', '', ch1_c)
    has_origin = any(kw in ch1_clean for kw in ['来', '到', '上寺', '出家', '为何', '为什么'])
    f.write(f"5.1 ch1是否交代寂声来历: {'有' if has_origin else '缺失！'} \n")
    if not has_origin:
        f.write("    -> 读者不知道主角为什么出现在这里\n")

    # 5.2 检查沈秋白首次出现的章节是否交代了他的来历
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+5000]
        if '秋白' in c:
            c_clean = re.sub(r'<[^>]+>', '', c)
            has_shen_origin = any(kw in c_clean for kw in ['朝廷', '朝中', '洛城', '旧宅', '贬', '退', '辞官', '养病'])
            f.write(f"5.2 沈秋白首次出现在ch{ch_num} {title}，背景交代: {'有' if has_shen_origin else '缺失！'}\n")
            if not has_shen_origin:
                f.write(f"    -> 读者不知道这个重要人物从哪来的\n")
            break

    # 5.3 检查老孙是否有任何背景交代
    sun_background = 0
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+5000]
        c_clean = re.sub(r'<[^>]+>', '', c)
        if any(kw in c_clean for kw in ['老孙.*?四十年', '老孙.*?来.*?寺', '老孙.*?年轻', '老孙.*?出家', '老孙.*?以前']):
            sun_background += 1
    f.write(f"5.3 老孙背景交代: {sun_background}章提及（共152章）\n")
    if sun_background < 3:
        f.write(f"    -> 核心人物背景几乎为空\n")

    # 5.4 检查是否有矛盾/冲突/张力
    conflict_keywords = ['争执', '吵', '不同意', '反对', '矛盾', '犹豫', '挣扎', '生气', '难过', '哭', '担心', '害怕']
    conflict_chapters = []
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+5000]
        c_clean = re.sub(r'<[^>]+>', '', c)
        for kw in conflict_keywords:
            if kw in c_clean:
                conflict_chapters.append((ch_num, title, kw))
                break
    f.write(f"5.4 包含冲突/张力的章节: {len(conflict_chapters)}/152章\n")
    if len(conflict_chapters) < 10:
        f.write(f"    -> 全书缺乏情感张力！152章禅意散文没有矛盾驱动\n")
    for ch_num, title, kw in conflict_chapters[:15]:
        f.write(f"    ch{ch_num} {title}: '{kw}'\n")

    # 5.5 检查对话/互动密度
    dialogue_count = len(re.findall(r'(?:老孙|寂声|沈秋白)(?:说|问|答|道|喊|叫|笑)[：:"]', html))
    f.write(f"\n5.5 三人对话/互动总数: ~{dialogue_count}次\n")
    f.write(f"    平均每章: {dialogue_count/152:.1f}次\n")

    # ============================================================
    # 6. 章节类型分析
    # ============================================================
    f.write("\n" + "=" * 70 + "\n")
    f.write("6. 章节类型分类\n")
    f.write("=" * 70 + "\n\n")

    categories = {
        '日常劳作': ['磨墨', '裁纸', '晒书', '补瓦', '理药', '煮粥', '缝补', '挑水', '劈柴', '喂鱼', '扫雪',
                   '洗碗', '种苔', '理香', '刷墙', '采蕨', '编筐', '磨刀', '晒被', '捡柴', '补经', '制酱',
                   '理石', '采药', '晒药', '捣药', '施药', '煎药', '画壁', '制香', '播种', '浇水', '收获',
                   '洗砚', '寻泉', '磨豆', '扫塔', '种瓜', '种豆', '洗石', '换衣'],
        '自然观赏': ['观云', '纳凉', '听雨', '数星', '看山', '望月', '观瀑', '闻蝉', '踏露', '踏霜', '观蚁',
                   '听雷', '听泉', '赏枫', '观日', '寻幽', '坐石', '探芽', '迎燕', '望春', '听蛙', '听冰',
                   '雨后', '谷雨'],
        '修行与精神': ['敲钟', '诵经', '静坐', '夜读', '抄经', '行脚', '挂单', '斋戒', '放生', '供灯',
                    '晚课', '晨读', '临帖', '试笔', '封笔', '炙砚', '呵冻', '呵笔', '嚼雪', '负暄',
                    '忍寒', '拥衾', '晚钟', '夜坐', '抄谱', '晾书', '煨芋', '破冰', '履冰'],
        '人际关系': ['写信', '论道', '送别', '盼信', '温书', '忆旧', '独处', '望山', '午憩', '辞行', '归途',
                   '重逢', '叙旧', '寄远', '话旧', '围炉', '送春', '惜春', '还愿', '祈福', '留客', '遇客',
                   '问樵', '对弈', '对月', '守岁', '立夏'],
        '季节仪式': ['立夏', '春尽', '迎夏', '送寒', '候雪', '初雪', '踏春', '拾翠', '探谷', '过桥',
                   '避雨', '拾叶', '题叶', '冰凌', '融冰', '试水', '开窗', '晒经', '踏青', '春茶',
                   '清明', '笋时', '蚕月', '午后', '无尽'],
    }

    for cat, keywords in categories.items():
        count = 0
        for ch_id, title in chapters:
            if any(kw in title for kw in keywords):
                count += 1
        f.write(f"{cat}: {count}章\n")

    total_tagged = sum(
        sum(1 for _, t in chapters if any(kw in t for kw in kws))
        for kws in categories.values()
    )
    f.write(f"\n总计标记: {total_tagged} (有重叠), 实际152章\n")

print(f"诊断完成, 写入 {OUT}")
