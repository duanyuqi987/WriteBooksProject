"""
诊断破折号使用密度
"""
import re, os

B2_PATH = 'd:/ProgramWork/WriteBookProject/docs/2026-05-15/学习书/qingyin-siju-temple-life-2026-05-15.html'
OUT = 'd:/ProgramWork/WriteBookProject/tmp_dash_diag.txt'

with open(B2_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

chapters = re.findall(r'<h2 id="ch(\d+)">([^<]+)</h2>', html)

with open(OUT, 'w', encoding='utf-8') as f:
    total_dash = html.count('——')
    f.write(f"全书破折号总数: {total_dash}\n\n")

    data = []
    for ch_id, title in chapters:
        ch_num = int(ch_id)
        pos = html.find(f'<h2 id="ch{ch_num}">')
        np = html.find('<h2 id="ch', pos + 20)
        if np < 0: np = html.find('<footer', pos)
        c = html[pos:np] if np > 0 else html[pos:pos+5000]
        clean = re.sub(r'<[^>]+>', '', c)
        cjk = len(re.findall(r'[一-鿿]', clean))
        dashes = clean.count('——')
        ratio = dashes / max(cjk, 1) * 100  # dashes per 100 CJK chars
        data.append((ch_num, title, cjk, dashes, ratio))

    avg_ratio = sum(x[4] for x in data) / len(data)
    f.write(f"平均每100 CJK字的破折号数: {avg_ratio:.1f}\n\n")

    # Sort by ratio (highest first = worst offenders)
    data.sort(key=lambda x: -x[4])

    f.write("破折号密度最高的20章 (最需要优化):\n")
    f.write("-" * 60 + "\n")
    for ch_num, title, cjk, dashes, ratio in data[:20]:
        f.write(f"ch{ch_num:03d} [{cjk:>5d}CJK] {title}: {dashes}个破折号, 密度={ratio:.1f}/100字\n")

    f.write(f"\n破折号密度最低的10章 (最自然的):\n")
    f.write("-" * 60 + "\n")
    for ch_num, title, cjk, dashes, ratio in data[-10:]:
        f.write(f"ch{ch_num:03d} [{cjk:>5d}CJK] {title}: {dashes}个破折号, 密度={ratio:.1f}/100字\n")

    # Show worst chapter content sample
    worst = data[0]
    f.write(f"\n\n最严重章 ch{worst[0]} {worst[1]} 全文:\n")
    f.write("=" * 60 + "\n")
    pos = html.find(f'<h2 id="ch{worst[0]}">')
    np = html.find('<h2 id="ch', pos + 20)
    if np < 0: np = html.find('<footer', pos)
    c = html[pos:np] if np > 0 else html[pos:pos+5000]
    clean = re.sub(r'<[^>]+>', '', c)
    f.write(clean[:2000] + "\n")

print(f"Done: {OUT}")
