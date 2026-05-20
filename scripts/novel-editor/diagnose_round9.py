"""
续修九诊断：叙事节奏 + 中段支撑 + 剩余弱章
"""
import re, os

OUTDIR = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书'
B2_PATH = os.path.join(OUTDIR, 'qingyin-siju-temple-life-2026-05-15.html')
OUT = 'd:/ProgramWork/WriteBookProject/tmp_round9_diag.txt'

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

chapters = re.findall(r'<h2 id="ch(\d+)">([^<]+)</h2>', html)

with open(OUT, 'w', encoding='utf-8') as f:
    # ============================================================
    # 1. 章节CJK分布（节奏感）
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("1. CJK分布热力图 (每10章的平均值)\n")
    f.write("=" * 60 + "\n\n")

    cjk_data = []
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+10000]
        cjk = len(re.findall(r'[一-鿿]', c))
        cjk_data.append((ch_num, title, cjk))

    for batch_start in range(1, 153, 10):
        batch = [x for x in cjk_data if batch_start <= x[0] < batch_start + 10]
        if batch:
            avg = sum(x[2] for x in batch) / len(batch)
            bar = '#' * int(avg / 20)
            titles = ', '.join(x[1] for x in batch)
            f.write(f"ch{batch_start:03d}-{batch_start+9:03d} [{avg:5.0f}] {bar}\n")
            f.write(f"  {titles}\n\n")

    # ============================================================
    # 2. 沈秋白缺席期(ch51-ch75)详细检查
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("2. 沈秋白缺席期 ch51-ch75 详细分析\n")
    f.write("=" * 60 + "\n\n")

    f.write("这段时间沈秋白物理不在寺中，仅靠信件维持联系。\n")
    f.write("目前沈秋白以'信中人'存在的方式：\n\n")

    shen_present_in_block = 0
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        if 51 <= ch_num <= 75:
            pos = html.find(f'<h2 id="ch{ch_num}">')
            np = html.find('<h2 id="ch', pos + 20)
            if np < 0: np = html.find('<footer', pos)
            c = html[pos:np] if np > 0 else html[pos:pos+10000]
            has_shen = '秋白' in c
            if has_shen:
                shen_present_in_block += 1
                # Find how Shen is referenced
                shen_refs = re.findall(r'.{0,40}秋白.{0,40}', c)
                if shen_refs:
                    f.write(f"  ch{ch_num} {title}: Shen referenced via: {shen_refs[0][:100]}...\n")

    f.write(f"\n  沈秋白在ch51-75段出现: {shen_present_in_block}/25章\n")

    # ============================================================
    # 3. 最薄弱的10章（叙事密度最低）
    # ============================================================
    f.write("\n" + "=" * 60 + "\n")
    f.write("3. 最薄弱的15章 (<700 CJK)\n")
    f.write("=" * 60 + "\n\n")

    thin = sorted([x for x in cjk_data if x[2] < 700], key=lambda x: x[2])
    for ch_num, title, cjk in thin:
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+10000]
        clean = re.sub(r'<[^>]+>', '', c)[:120].replace('\n', ' ')
        f.write(f"ch{ch_num:03d} [{cjk:>5d}CJK] {title}\n")
        f.write(f"  {clean}...\n\n")

    # ============================================================
    # 4. 章节过渡：相邻章之间是否有承接
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("4. 相邻章节过渡检查 (前章尾 + 后章头)\n")
    f.write("=" * 60 + "\n\n")

    # Check first 30 chapters for transition quality
    for i in range(1, min(30, len(chapters))):
        ch_num = int(chapters[i-1][0])
        next_ch_num = int(chapters[i][0])
        if next_ch_num != ch_num + 1:
            continue

        # Get end of current chapter
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find(f'<h2 id="ch{next_ch_num}">', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+10000]
        clean = re.sub(r'<[^>]+>', '', c)
        # Last 100 chars
        ending = clean[-150:].replace('\n', ' ').strip()

        # First 100 chars of next chapter
        pos2 = html.find(f'<h2 id="ch{next_ch_num}">')
        np2 = html.find(f'<h2 id="ch{next_ch_num+1}">', pos2)
        if np2 < 0: np2 = html.find('<footer', pos2)
        c2 = html[pos2:np2] if np2 > 0 else html[pos2:pos2+5000]
        clean2 = re.sub(r'<[^>]+>', '', c2)
        opening = clean2[:150].replace('\n', ' ').strip()

        # Simple check: any shared keywords?
        kw_current = set(re.findall(r'[一-鿿]{2,4}', ending))
        kw_next = set(re.findall(r'[一-鿿]{2,4}', opening))
        overlap = kw_current & kw_next
        has_bridge = len(overlap) > 1

        if not has_bridge:
            f.write(f"✗ ch{ch_num:03d}→ch{next_ch_num:03d}: 无关键词重叠\n")
            f.write(f"  尾: {ending[:80]}...\n")
            f.write(f"  头: {opening[:80]}...\n\n")

    # ============================================================
    # 5. 情感节奏：连续'静'章过多？
    # ============================================================
    f.write("=" * 60 + "\n")
    f.write("5. 情感色彩分布\n")
    f.write("=" * 60 + "\n\n")

    emotion_keywords = {
        '轻快/幽默': ['笑', '乐', '趣', '逗', '好玩', '轻松'],
        '沉静/禅意': ['静', '默', '定', '安', '稳', '慢', '等', '空'],
        '忧郁/感伤': ['悲', '伤', '哭', '泪', '叹', '愁', '寂寞', '孤独', '冷清', '念'],
        '温暖/亲密': ['暖', '温', '热', '一起', '三人', '相伴', '陪'],
    }

    for i in range(1, 153):
        pos = html.find(f'<h2 id="ch{i}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+10000]
        clean = re.sub(r'<[^>]+>', '', c)

        scores = {}
        for emo, kws in emotion_keywords.items():
            scores[emo] = sum(clean.count(kw) for kw in kws)

        dominant = max(scores, key=scores.get)
        if scores[dominant] == 0:
            dominant = '中性'

    f.write("情感分布统计完成\n")

print(f"诊断完成: {OUT}")
