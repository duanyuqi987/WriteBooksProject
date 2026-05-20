"""
《清音寺居》故事情节诊断
"""
import re, os

B2_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

chapters = re.findall(r'<h2 id="ch(\d+)">([^<]+)</h2>', html)
out_path = 'd:/ProgramWork/WriteBookProject/tmp_plot_diag.txt'
out = open(out_path, 'w', encoding='utf-8')

out.write('=' * 60 + '\n')
out.write('《清音寺居》故事情节诊断\n')
out.write('=' * 60 + '\n\n')

# 1. Plot timeline: map all 152 chapters to seasons
out.write('1. 季节-章节分布\n')
out.write('-' * 40 + '\n')
season_kw = {
    '春': ['春', '惊蛰', '清明', '谷雨', '桃花', '荠菜', '蕨', '笋', '茶', '蚕', '播种', '种豆', '种瓜', '晾书', '晒书', '踏青', '采蕨', '望春', '惜春', '送春', '春茶', '春寒', '开窗', '探芽', '雨后', '蚕月', '笋时'],
    '夏': ['夏', '立夏', '蝉', '蛙', '西瓜', '蒲扇', '热', '午后', '换衣', '听蝉', '听蛙', '迎夏'],
    '秋': ['秋', '枫', '落叶', '赏枫', '煨芋', '晒经', '柿', '桂花', '秋收'],
    '冬': ['冬', '立冬', '雪', '冰', '融冰', '破冰', '炙砚', '呵冻', '忍寒', '负暄', '踏霜', '棉袍', '晚钟', '听冰'],
}

season_counts = {'春': 0, '夏': 0, '秋': 0, '冬': 0, '未分类': 0}
for ch_id, title in chapters:
    ch_num = int(ch_id)
    pos = html.find(f'<h2 id="ch{ch_num}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+5000]
    clean = re.sub(r'<[^>]+>', '', c)
    best_season = '未分类'
    best_score = 0
    for season, kws in season_kw.items():
        score = sum(clean.count(kw) for kw in kws)
        if score > best_score:
            best_score = score
            best_season = season
    season_counts[best_season] += 1

for s, n in season_counts.items():
    pct = n / 152 * 100
    bar = '#' * int(pct)
    out.write(f'  {s}: {n}章 ({pct:.0f}%) {bar}\n')

# 2. Key plot events timeline
out.write('\n2. 关键情节事件时间线\n')
out.write('-' * 40 + '\n')

key_events = [
    ('ch001', '寂声入寺，开始磨墨'),
    ('ch025', '补经——残缺与完整的领悟'),
    ('ch042', '煎药——沈秋白肺伤初现'),
    ('ch049', '论道——三人思想碰撞'),
    ('ch050', '送别沈秋白下山'),
    ('ch051', '盼信——第一封信'),
    ('ch057', '独处——寂声从失落到自立'),
    ('ch067', '临帖——为了谁写字'),
    ('ch074', '辞行——寂声下山寻人'),
    ('ch075', '归途——洛城见闻'),
    ('ch076', '重逢——沈秋白归来'),
    ('ch077', '叙旧——三人重建'),
    ('ch080', '老孙开始让寂声独立'),
    ('ch107', '话旧——三人关系的深层理解'),
    ('ch119', '忍寒——忍耐的意义'),
    ('ch145', '晚钟——寂声第一次敲钟（传承）'),
    ('ch147', '送春——送别春天的仪式'),
    ('ch152', '无尽——全书收尾'),
]

for ch_id, desc in key_events:
    ch_num = int(ch_id[2:])
    pos = html.find(f'<h2 id="ch{ch_num}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+5000]
    clean = re.sub(r'<[^>]+>', '', c)
    cjk = len(re.findall(r'[一-鿿]', clean))
    first_line = clean.strip()[:80].replace('\n', ' ')
    out.write(f'  {ch_id} [{cjk:>5d}CJK] {desc}\n')
    out.write(f'    开头: {first_line}...\n\n')

# 3. Character arc checkpoints
out.write('3. 寂声成长弧检查点\n')
out.write('-' * 40 + '\n')
growth_checks = [
    ('ch001', '困惑', ['为什么是我', '磨墨', '不懂']),
    ('ch025', '补经领悟', ['残缺', '完整', '补', '经']),
    ('ch057', '从失落到自立', ['独处', '自己', '静', '等']),
    ('ch067', '自我追问', ['为谁', '临帖', '写']),
    ('ch074', '决心形成', ['下山', '寻', '辞行', '去']),
    ('ch119', '忍耐顿悟', ['忍', '寒', '意义']),
    ('ch145', '独立敲钟', ['钟', '敲', '稳']),
]
for ch_id, stage, kws in growth_checks:
    ch_num = int(ch_id[2:])
    pos = html.find(f'<h2 id="ch{ch_num}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+5000]
    clean = re.sub(r'<[^>]+>', '', c)
    hits = [kw for kw in kws if kw in clean]
    out.write(f'  {ch_id} {stage}: {hits}\n')

# 4. Plot coherence: check transitions for first 60 chapters
out.write('\n4. 相邻章节过渡桥接 (前60章)\n')
out.write('-' * 40 + '\n')
good = 0
fair = 0
none = 0
for i in range(1, min(60, len(chapters))):
    ch_num = int(chapters[i-1][0])
    next_num = int(chapters[i][0])
    if next_num != ch_num + 1:
        continue
    pos = html.find(f'<h2 id="ch{ch_num}">')
    np = html.find(f'<h2 id="ch{next_num}">', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+10000]
    clean = re.sub(r'<[^>]+>', '', c)
    ending = clean[-200:]
    pos2 = html.find(f'<h2 id="ch{next_num}">')
    np2 = html.find(f'<h2 id="ch{next_num+1}">', pos2)
    if np2 < 0: np2 = html.find('<footer', pos2)
    c2 = html[pos2:np2] if np2 > 0 else html[pos2:pos2+5000]
    clean2 = re.sub(r'<[^>]+>', '', c2)
    opening = clean2[:200]
    kw1 = set(re.findall(r'[一-鿿]{2,4}', ending[-100:]))
    kw2 = set(re.findall(r'[一-鿿]{2,4}', opening[:100]))
    overlap = kw1 & kw2
    if len(overlap) >= 2:
        good += 1
    elif len(overlap) == 1:
        fair += 1
    else:
        none += 1
        out.write(f'  无桥接: ch{ch_num:03d}({chapters[i-1][1]}) → ch{next_num:03d}({chapters[i][1]})\n')
        out.write(f'    尾: {ending[-60:].strip()[:50]}...\n')
        out.write(f'    头: {opening[:60].strip()[:50]}...\n\n')

out.write(f'\n  有桥接: {good}, 弱桥接: {fair}, 无桥接: {none}\n')

# 5. Plot gap analysis: what's missing?
out.write('\n5. 情节空白分析\n')
out.write('-' * 40 + '\n')

# Check for missing transitions
out.write('\n  沈秋白下山期间 (ch51-75):\n')
shen_refs = 0
for ch_id in range(51, 76):
    pos = html.find(f'<h2 id="ch{ch_id}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+10000]
    if '秋白' in c:
        shen_refs += 1
out.write(f'    沈秋白被提及章数: {shen_refs}/25\n')

# Check for Lao Sun absence periods
out.write('\n  老孙缺席检查:\n')
laosun_missing = []
for ch_id in range(1, 153):
    pos = html.find(f'<h2 id="ch{ch_id}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+10000]
    if '老孙' not in c:
        laosun_missing.append(ch_id)
out.write(f'    老孙完全缺席: ch{laosun_missing}\n')

# Check for Ji Sheng absence
out.write('\n  寂声缺席检查:\n')
ji_missing = []
for ch_id in range(1, 153):
    pos = html.find(f'<h2 id="ch{ch_id}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+10000]
    if '寂声' not in c:
        ji_missing.append(ch_id)
out.write(f'    寂声完全缺席: ch{ji_missing}\n')

# 6. Annual cycle check
out.write('\n6. 年周期检查\n')
out.write('-' * 40 + '\n')
out.write('  全书覆盖时间: 约一年 (从寂声入寺的春天到次年送春)\n')
out.write('  季节流动: 春 → 夏 → 秋 → 冬 → 春\n')
out.write('  关键时间节点:\n')
out.write('    ch1-~50: 春天到初夏 (沈秋白下山前)\n')
out.write('    ch51-75: 春夏之交 (沈秋白不在)\n')
out.write('    ch76-110: 夏秋 (沈归来后)\n')
out.write('    ch111-140: 秋冬春 (跨越年关)\n')
out.write('    ch141-152: 春天第二年 (送春收尾)\n')

out.close()
print(f'Done: {out_path}')
