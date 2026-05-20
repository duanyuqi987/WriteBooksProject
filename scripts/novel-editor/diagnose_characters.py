"""
诊断《清音寺居》人物性格饱满度与行为逻辑
"""
import re, os, sys

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Extract clean text for analysis
text = re.sub(r'<[^>]+>', '', html)
text = re.sub(r'\n{3,}', '\n\n', text)

# Write analysis to file to avoid encoding issues
out = 'd:/ProgramWork/WriteBookProject/tmp_diagnose_char.txt'
with open(out, 'w', encoding='utf-8') as f:
    # ============================================================
    # 1. 采样每个人物的对话
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("1. 人物对话采样\n")
    f.write("=" * 60 + "\n\n")

    # 老孙的对话 (search for 老孙说)
    laosun_says = re.findall(r'老孙说[：:](.*?)(?:。|！|？|\n)', text)
    f.write(f"老孙说话: {len(laosun_says)}次\n")
    f.write("前20句:\n")
    for i, s in enumerate(laosun_says[:20]):
        f.write(f"  [{i+1}] {s.strip()[:80]}\n")

    f.write("\n沈秋白说话:\n")
    shen_says = re.findall(r'沈秋白说[：:](.*?)(?:。|！|？|\n)', text)
    f.write(f"共{len(shen_says)}次\n")
    for i, s in enumerate(shen_says[:20]):
        f.write(f"  [{i+1}] {s.strip()[:80]}\n")

    f.write("\n寂声说话:\n")
    ji_says = re.findall(r'寂声说[：:](.*?)(?:。|！|？|\n)', text)
    f.write(f"共{len(ji_says)}次\n")
    for i, s in enumerate(ji_says[:20]):
        f.write(f"  [{i+1}] {s.strip()[:80]}\n")

    # ============================================================
    # 2. 人物思考模式 (inner-monologue 采样)
    # ============================================================
    f.write("\n\n" + "=" * 60 + "\n")
    f.write("2. 内心独白采样 (每人物前5段)\n")
    f.write("=" * 60 + "\n\n")

    inners = re.findall(r'<div class="inner-monologue">\s*<p>(.*?)</p>\s*</div>', html, re.DOTALL)
    f.write(f"inner-monologue总数: {len(inners)}\n\n")

    # Classify by topic
    for i, inner in enumerate(inners[:10]):
        f.write(f"[Inner {i+1}] {inner.strip()[:120]}...\n\n")

    # ============================================================
    # 3. 关键转折逻辑检查
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("3. 关键转折逻辑检查\n")
    f.write("=" * 60 + "\n\n")

    # ch50 送别 - why does Shen leave?
    ch50_pos = html.find('<h2 id="ch50">')
    ch51_pos = html.find('<h2 id="ch51">', ch50_pos)
    ch50 = html[ch50_pos:ch51_pos]
    ch50_clean = re.sub(r'<[^>]+>', '', ch50)
    f.write("--- ch50 送别 (沈秋白为何下山?) ---\n")
    f.write(ch50_clean[:600] + "\n...\n\n")

    # ch74 辞行 - why does Ji decide to go?
    ch74_pos = html.find('<h2 id="ch74">')
    ch75_pos = html.find('<h2 id="ch75">', ch74_pos)
    ch74 = html[ch74_pos:ch75_pos]
    ch74_clean = re.sub(r'<[^>]+>', '', ch74)
    f.write("--- ch74 辞行 (寂声为何下山?) ---\n")
    f.write(ch74_clean[:600] + "\n...\n\n")

    # ch76 重逢 - why does Shen return?
    ch76_pos = html.find('<h2 id="ch76">')
    ch77_pos = html.find('<h2 id="ch77">', ch76_pos)
    ch76 = html[ch76_pos:ch77_pos]
    ch76_clean = re.sub(r'<[^>]+>', '', ch76)
    f.write("--- ch76 重逢 (沈秋白为何回来?) ---\n")
    f.write(ch76_clean[:600] + "\n...\n\n")

    # ============================================================
    # 4. 人物性格一致性检查
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("4. 人物性格特征词统计\n")
    f.write("=" * 60 + "\n\n")

    # 寂声: 年龄、身份、性格标记
    ji_emotions = {
        '困惑': len(re.findall(r'寂声.*?不[解懂明]', text)),
        '好奇': len(re.findall(r'寂声.*?[问想]', text)),
        '安静': len(re.findall(r'寂声.*?[静默沉坐站看听蹲]', text)),
        '成长': len(re.findall(r'寂声.*?[第一次学会终于忽然想明白了原来]', text)),
    }
    f.write(f"寂声情绪标记: {ji_emotions}\n")

    # 沈秋白: 背景、性格标记
    shen_traits = {
        '朝中往事': len(re.findall(r'沈秋白.*?[朝洛城御史官]', text)),
        '病体': len(re.findall(r'沈秋白.*?[咳嗽药肺病弱]', text)),
        '沉默': len(re.findall(r'沈秋白.*?[沉默不说没说话]', text)),
        '文人气质': len(re.findall(r'沈秋白.*?[诗书写琴笔墨]', text)),
    }
    f.write(f"沈秋白性格标记: {shen_traits}\n")

    # 老孙: 性格标记
    sun_traits = {
        '不慌不忙': len(re.findall(r'老孙.*?[慢不急不慌]', text)),
        '自言自语': len(re.findall(r'老孙.*?自言自语', text)),
        '规矩/原则': len(re.findall(r'老孙.*?(?:规矩|从不|一定|必须|不[能会要])', text)),
        '幽默/笑': len(re.findall(r'老孙.*?[笑了笑起来]', text)),
    }
    f.write(f"老孙性格标记: {sun_traits}\n")

    # ============================================================
    # 5. 寂声成长弧关键节点检查
    # ============================================================
    f.write("\n" + "=" * 60 + "\n")
    f.write("5. 寂声成长弧7节点内容检查\n")
    f.write("=" * 60 + "\n\n")

    growth_nodes = {
        'ch1 磨墨': '困惑/被动',
        'ch25 补经': '残缺与完整领悟',
        'ch57 独处': '失落到自立的转折',
        'ch67 临帖': '为谁写字的追问',
        'ch74 辞行': '决心下山',
        'ch75 归途': '洛城见闻',
        'ch119 忍寒': '忍耐的意义',
    }
    for ch_label, theme in growth_nodes.items():
        ch_id = int(ch_label.split()[0][2:])
        pos = html.find(f'<h2 id="ch{ch_id}">')
        next_pos = html.find('<h2 id="ch', pos + 20)
        if next_pos < 0:
            next_pos = html.find('<footer', pos)
        if next_pos < 0:
            next_pos = len(html)
        content = html[pos:next_pos]
        # Check for B1 growth injection markers
        has_growth_injection = False
        growth_markers = {
            1: '为什么是我',
            25: '残缺与完整',
            57: '不是失去',
            67: '为了谁',
            74: '不是离开',
            75: '洛城',
            119: '怕冷',
        }
        if ch_id in growth_markers:
            has_growth_injection = growth_markers[ch_id] in content
        f.write(f"{ch_label} ({theme}): B1注入={'✓' if has_growth_injection else '✗'}\n")

    # ============================================================
    # 6. 沈秋白回寺后的行为一致性
    # ============================================================
    f.write("\n" + "=" * 60 + "\n")
    f.write("6. 沈秋白 ch76回寺后行动轨迹\n")
    f.write("=" * 60 + "\n\n")
    for ch_id in range(76, 153):
        pos = html.find(f'<h2 id="ch{ch_id}">')
        next_pos = html.find('<h2 id="ch', pos + 20)
        if next_pos < 0:
            next_pos = html.find('<footer', pos)
        if next_pos < 0:
            next_pos = len(html)
        content = html[pos:next_pos]
        has_shen = '秋白' in content
        if has_shen:
            # Find what Shen does in this chapter
            shen_actions = re.findall(r'沈秋白(?:.{0,20}?)([说问答看站坐走拿放写念读弹抄补])(?:.{0,10})', content)
            if shen_actions:
                f.write(f"ch{ch_id}: Shen在场, 动作={shen_actions[:3]}\n")

    # ============================================================
    # 7. 问题汇总
    # ============================================================
    f.write("\n" + "=" * 60 + "\n")
    f.write("7. 潜在问题\n")
    f.write("=" * 60 + "\n\n")

    # Check if 寂声 has distinct speech patterns vs 沈秋白
    ji_asks = len(re.findall(r'寂声[问说].*?[？?]', text))
    shen_tells = len(re.findall(r'沈秋白[说].*?(?:在朝[中廷]|以前|曾经|当年)', text))
    f.write(f"寂声提问次数: {ji_asks}\n")
    f.write(f"沈秋白提及往事的次数: {shen_tells}\n")

    # Check for overly similar inner voice
    f.write("\n--- 各人物'觉得/想/明白' 频次 ---\n")
    for name in ['寂声', '秋白', '老孙']:
        think_count = len(re.findall(f'{name}.*?(?:觉得|想|明白|知道|发现)', text))
        f.write(f"{name}: {think_count}次\n")

print(f"诊断完成, 写入 {out}")
