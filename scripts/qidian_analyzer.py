#!/usr/bin/env python3
"""
起点热门小说分析爬虫。
每次启动时获取起点 Top100 热门小说，分析写作技巧和读者吸引力要素，
将结果写入 docs/ 供写作计划参考。

用法:
  python3 scripts/qidian_analyzer.py                    # 获取 Top100 并分析
  python3 scripts/qidian_analyzer.py --top 50            # 只获取 Top50
  python3 scripts/qidian_analyzer.py --genre 玄幻        # 按分类筛选
  python3 scripts/qidian_analyzer.py --output analysis.md # 输出到指定文件

输出:
  docs/YYYY-MM-DD/小说/qidian-analysis.md  # 分析报告
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("[!] 缺少 requests 库，尝试安装: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] 缺少 beautifulsoup4 库，尝试安装: pip install beautifulsoup4")
    sys.exit(1)

# --- 配置 ---

BASE_URL = "https://www.qidian.com"
RANK_URL = "https://www.qidian.com/rank/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 1.5  # 请求间隔（秒）

# 起点小说分类
GENRES = [
    "玄幻", "奇幻", "武侠", "仙侠", "都市", "现实",
    "军事", "历史", "游戏", "体育", "科幻", "悬疑",
    "轻小说", "短篇",
]

# 写作技巧关键词检测
TECHNIQUE_PATTERNS = {
    "爽文循环": re.compile(r"(压抑|憋屈|反转|释放|打脸|逆袭|翻身|碾压)"),
    "信息差": re.compile(r"(隐藏|伪装|秘密|不知道|隐瞒|卧底|隐藏身份)"),
    "升级体系": re.compile(r"(升级|突破|进阶|等级|境界|觉醒|修炼|进级)"),
    "金手指": re.compile(r"(系统|传承|上古|奇遇|获得.*能力|穿越|重生|随身|天降)"),
    "反派设计": re.compile(r"(反派|死对头|宿敌|仇人|敌人|对手)"),
    "钩子/悬念": re.compile(r"(秘密|真相|阴谋|到底|竟然|原来|怎么会|突然)"),
    "身份反差": re.compile(r"(伪装|扮猪|低调|隐藏实力|废柴|天才|隐藏大佬)"),
    "伏线设计": re.compile(r"(伏笔|暗示|线索|细节|真相|揭露|谜团|解开)"),
    "情绪节奏": re.compile(r"(热血|感动|爽|紧张|刺激|震撼|哭|笑)"),
    "人物关系网": re.compile(r"(兄弟|姐妹|师徒|父子|红颜|伙伴|盟友|背叛)"),
}


def fetch_page(url: str) -> str | None:
    """获取页面 HTML。"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.encoding = "utf-8"
        if resp.status_code == 200:
            return resp.text
        print(f"  [!] HTTP {resp.status_code}: {url}")
        return None
    except requests.RequestException as e:
        print(f"  [!] 请求失败: {url} - {e}")
        return None


def parse_rank_page(html: str) -> list[dict]:
    """从排行榜页面解析小说列表。"""
    soup = BeautifulSoup(html, "html.parser")
    novels = []

    # 尝试多种选择器适配起点页面结构
    selectors = [
        ".rank-list .book-list li",
        ".book-img-text li",
        ".rank-list li",
        ".book-list li",
        "[data-rid]",
    ]

    items = []
    for sel in selectors:
        items = soup.select(sel)
        if items:
            break

    for item in items:
        try:
            # 提取书名和链接
            name_el = item.select_one("h4 a") or item.select_one("h2 a") or item.select_one(".book-name a") or item.select_one("a[data-eid]")
            if not name_el:
                continue

            title = name_el.get_text(strip=True)
            link = name_el.get("href", "")
            if link and not link.startswith("http"):
                link = urljoin(BASE_URL, link)

            # 提取作者
            author_el = item.select_one(".author a") or item.select_one(".author-name")
            author = author_el.get_text(strip=True) if author_el else "未知"

            # 提取分类
            genre_el = item.select_one(".cat") or item.select_one(".tag") or item.select_one(".book-classify")
            genre = genre_el.get_text(strip=True) if genre_el else "未知"

            # 提取简介
            intro_el = item.select_one(".intro") or item.select_one(".desc") or item.select_one("p.description")
            intro = intro_el.get_text(strip=True) if intro_el else ""

            # 提取字数/状态
            word_count_el = item.select_one(".word-count") or item.select_one(".update span")
            word_count = word_count_el.get_text(strip=True) if word_count_el else ""

            novels.append({
                "title": title,
                "author": author,
                "genre": genre,
                "intro": intro,
                "word_count": word_count,
                "link": link,
            })
        except Exception as e:
            print(f"  [!] 解析条目失败: {e}")
            continue

    return novels


def parse_book_page(html: str) -> dict:
    """从书籍详情页解析更多信息。"""
    soup = BeautifulSoup(html, "html.parser")
    info = {
        "tags": [],
        "full_intro": "",
        "total_words": "",
        "total_chapters": "",
        "reader_count": "",
        "recommendations": "",
    }

    # 标签
    tag_els = soup.select(".tag") or soup.select(".book-tag a")
    info["tags"] = [t.get_text(strip=True) for t in tag_els[:10]]

    # 完整简介
    intro_el = soup.select_one(".book-intro p") or soup.select_one(".intro p")
    if intro_el:
        info["full_intro"] = intro_el.get_text(strip=True)

    # 统计数据
    for stat in soup.select(".book-data .data-item") or soup.select(".book-info .stat"):
        text = stat.get_text(strip=True)
        if "万字" in text or "字" in text:
            info["total_words"] = text
        elif "章" in text:
            info["total_chapters"] = text

    return info


def analyze_techniques(novel: dict) -> dict:
    """分析小说的写作技巧。"""
    text = f"{novel.get('title','')} {novel.get('intro','')} {novel.get('tags','')}"
    techniques_found = {}

    for tech_name, pattern in TECHNIQUE_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            techniques_found[tech_name] = len(matches)

    return dict(sorted(techniques_found.items(), key=lambda x: x[1], reverse=True))


def generate_analysis_report(novels: list[dict], max_display: int = 100) -> str:
    """生成分析报告。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# 起点热门小说写作技巧分析",
        f"",
        f"> 采集时间: {now}",
        f"> 数据来源: 起点中文网排行榜",
        f"> 分析数量: {len(novels)} 本",
        f"",
        "---",
        "",
    ]

    # 1. 总体技术分布
    lines.append("## 一、写作技巧总体分布")
    lines.append("")
    all_techniques = Counter()
    for novel in novels:
        techs = analyze_techniques(novel)
        for tech, count in techs.items():
            all_techniques[tech] += 1

    lines.append("| 技巧 | 出现小说数 | 占比 |")
    lines.append("|------|----------|------|")
    total = len(novels)
    for tech, count in all_techniques.most_common():
        pct = f"{count/total*100:.1f}%" if total > 0 else "0%"
        lines.append(f"| {tech} | {count} | {pct} |")
    lines.append("")

    # 2. 分类分布
    lines.append("## 二、分类分布")
    lines.append("")
    genre_counter = Counter(n.get("genre", "未知") for n in novels)
    lines.append("| 分类 | 数量 | 占比 |")
    lines.append("|------|------|------|")
    for genre, count in genre_counter.most_common():
        pct = f"{count/total*100:.1f}%" if total > 0 else "0%"
        lines.append(f"| {genre} | {count} | {pct} |")
    lines.append("")

    # 3. 分类 × 技巧交叉分析
    lines.append("## 三、分类 × 技巧交叉分析")
    lines.append("")
    genre_techniques = defaultdict(Counter)
    for novel in novels:
        g = novel.get("genre", "未知")
        techs = analyze_techniques(novel)
        for tech in techs:
            genre_techniques[g][tech] += 1

    for genre in sorted(genre_techniques.keys()):
        g_count = genre_counter[genre]
        if g_count < 2:
            continue
        lines.append(f"### {genre}（{g_count}本）")
        lines.append("")
        lines.append("| 常用技巧 | 出现次数 | 占比 |")
        lines.append("|---------|---------|------|")
        for tech, count in genre_techniques[genre].most_common(5):
            pct = f"{count/g_count*100:.1f}%"
            lines.append(f"| {tech} | {count} | {pct} |")
        lines.append("")

    # 4. Top 10 详细分析
    lines.append("## 四、Top 10 详细分析")
    lines.append("")
    for i, novel in enumerate(novels[:10], 1):
        techs = analyze_techniques(novel)
        top_techs = list(techs.keys())[:5]
        lines.append(f"### {i}. {novel['title']}")
        lines.append("")
        lines.append(f"- **作者**: {novel.get('author','未知')}")
        lines.append(f"- **分类**: {novel.get('genre','未知')}")
        lines.append(f"- **字数**: {novel.get('word_count','未知')}")
        lines.append(f"- **简介**: {novel.get('intro','无')[:150]}...")
        lines.append(f"- **检测到的技巧**: {'、'.join(top_techs) if top_techs else '未检测到明显技巧'}")
        lines.append("")

    # 5. 写作建议
    lines.append("## 五、基于分析的写作建议")
    lines.append("")
    if all_techniques:
        top3 = [t for t, _ in all_techniques.most_common(3)]
        lines.append(f"当前热门小说最常用的三种技巧是 **{top3[0]}**、**{top3[1]}**、**{top3[2]}**。")
    lines.append("")
    lines.append("建议在写作计划中：")
    lines.append("1. 确保核心技法覆盖当前热门技巧")
    lines.append("2. 根据小说类型选择对应的技法组合（参考 genre-technique-mapping.md）")
    lines.append("3. 关注分析报告中同一分类下高频出现的差异化元素")

    return "\n".join(lines)


def get_output_path() -> Path:
    """获取输出文件路径。"""
    today = datetime.now().strftime("%Y-%m-%d")
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "docs" / today / "小说"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "qidian-analysis.md"


def main():
    parser = argparse.ArgumentParser(description="起点热门小说分析爬虫")
    parser.add_argument("--top", type=int, default=100, help="获取前 N 本小说（默认 100）")
    parser.add_argument("--genre", type=str, default=None, help="按分类筛选")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    parser.add_argument("--no-detail", action="store_true", help="跳过详情页，只从列表页分析")
    args = parser.parse_args()

    print(f"📊 起点小说分析器")
    print(f"   目标: Top {args.top}" + (f" / 分类: {args.genre}" if args.genre else ""))
    print()

    # 1. 获取排行榜页面
    print("[1/3] 获取排行榜...")
    rank_url = f"{RANK_URL}"
    if args.genre:
        rank_url = f"{RANK_URL}{args.genre}/"
    html = fetch_page(rank_url)
    if not html:
        print("[!] 无法获取排行榜页面，尝试备用方案...")
        # 备用：尝试多个排行榜页面
        for alt_url in [
            "https://www.qidian.com/rank/hotsales/",
            "https://www.qidian.com/rank/collect/",
            "https://www.qidian.com/rank/recom/",
        ]:
            html = fetch_page(alt_url)
            if html:
                break
        if not html:
            print("[!] 所有排行榜页面均无法访问")
            sys.exit(1)

    novels = parse_rank_page(html)
    print(f"   从排行榜解析到 {len(novels)} 本小说")

    if not novels:
        print("[!] 未解析到任何小说，可能是页面结构已变化")
        print("   请检查是否需要更新选择器")
        sys.exit(1)

    # 2. 获取详情（可选）
    if not args.no_detail and len(novels) > 0:
        print(f"[2/3] 获取详情页（取前 {min(args.top, 20)} 本）...")
        detail_count = min(args.top, min(len(novels), 20))  # 最多获取 20 本详情
        for i, novel in enumerate(novels[:detail_count]):
            if novel.get("link"):
                print(f"   [{i+1}/{detail_count}] {novel['title']}...", end=" ")
                detail_html = fetch_page(novel["link"])
                if detail_html:
                    detail = parse_book_page(detail_html)
                    novel.update(detail)
                    print("✓")
                else:
                    print("✗")
                time.sleep(REQUEST_DELAY)
    else:
        print("[2/3] 跳过详情页获取")

    # 截取 top N
    novels = novels[: args.top]

    # 3. 生成分析报告
    print(f"[3/3] 生成分析报告...")
    report = generate_analysis_report(novels)

    output_path = args.output or get_output_path()
    if isinstance(output_path, str):
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ 分析报告已写入: {output_path}")
    print(f"   共分析 {len(novels)} 本小说")
    print(f"   报告大小: {output_path.stat().st_size:,} 字节")


if __name__ == "__main__":
    main()
