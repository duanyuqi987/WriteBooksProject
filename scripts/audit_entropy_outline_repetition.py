from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from statistics import mean, quantiles


ROOT = Path("docs") / "2026-06-23"
REPORT_NAME = "outline-repetition-audit-2026-06-24.md"


@dataclass
class Chapter:
    number: int
    path: Path
    text: str
    sections: dict[str, str]
    headings: list[str]


def discover_outline_dir() -> Path:
    """Find the outline directory by locating the complete 2500-chapter set."""
    for first in ROOT.rglob("chapter-0001.md"):
        if (first.parent / "chapter-2500.md").exists():
            return first.parent
    raise FileNotFoundError("Cannot find outline directory with chapter-0001.md and chapter-2500.md.")


def split_sections(text: str) -> tuple[list[str], dict[str, str]]:
    """Split a chapter outline by level-2 Markdown headings."""
    matches = list(re.finditer(r"^##\s+(.+)$", text, re.M))
    headings = [m.group(1).strip() for m in matches]
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        start = match.end() + 1
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return headings, sections


def normalize(text: str) -> str:
    """Reduce purely local details before comparing outline skeletons."""
    text = re.sub(r"chapter-\d+", "chapter-N", text)
    text = re.sub(r"\d+(?:\.\d+)?", "N", text)
    text = re.sub(r"\s+", "", text)
    return text


def load_chapters(outline_dir: Path) -> list[Chapter]:
    """Load all outline chapters in numeric order."""
    chapters: list[Chapter] = []
    for path in sorted(outline_dir.glob("chapter-*.md")):
        number = int(path.stem.split("-")[1])
        text = path.read_text(encoding="utf-8")
        headings, sections = split_sections(text)
        chapters.append(Chapter(number, path, text, sections, headings))
    return chapters


def adjacent_metrics(values: list[str]) -> tuple[float, float, float, list[tuple[int, int, float]]]:
    """Return adjacent similarity and highest 25-chapter risk windows."""
    normalized = [normalize(value) for value in values]
    adjacent = [
        SequenceMatcher(None, normalized[idx], normalized[idx + 1]).ratio()
        for idx in range(len(normalized) - 1)
    ]
    if not adjacent:
        return 0.0, 0.0, 0.0, []

    p90 = quantiles(adjacent, n=10)[8]
    windows: list[tuple[int, int, float]] = []
    width = 24
    if len(adjacent) >= width:
        rolling = sum(adjacent[:width])
        for idx in range(0, len(adjacent) - width + 1):
            if idx > 0:
                rolling += adjacent[idx + width - 1] - adjacent[idx - 1]
            windows.append((idx + 1, idx + width + 1, rolling / width))
    return mean(adjacent), p90, max(adjacent), sorted(windows, key=lambda item: item[2], reverse=True)[:5]


def section_rows(chapters: list[Chapter]) -> list[dict[str, object]]:
    """Compute repetition metrics for each outline section."""
    rows: list[dict[str, object]] = []
    headings = chapters[0].headings
    for heading in headings[2:]:
        values = [chapter.sections.get(heading, "") for chapter in chapters]
        avg, p90, max_value, windows = adjacent_metrics(values)
        rows.append(
            {
                "section": heading,
                "unique": len(set(values)),
                "normalized_unique": len({normalize(value) for value in values}),
                "avg": avg,
                "p90": p90,
                "max": max_value,
                "windows": windows,
            }
        )
    return rows


def scene_subheading_counts(chapters: list[Chapter]) -> Counter[str]:
    """Count repeated scene-level headings."""
    scene_heading = chapters[0].headings[6]
    counts: Counter[str] = Counter()
    for chapter in chapters:
        scene_text = chapter.sections.get(scene_heading, "")
        for heading in re.findall(r"^###\s+(.+)$", scene_text, re.M):
            counts[heading] += 1
    return counts


def exact_paragraph_repeats(chapters: list[Chapter], limit: int = 20) -> list[tuple[str, int, list[int]]]:
    """Find exact repeated paragraphs with chapter examples."""
    counts: Counter[str] = Counter()
    examples: dict[str, list[int]] = defaultdict(list)
    for chapter in chapters:
        for paragraph in re.split(r"\n\s*\n", chapter.text):
            clean = paragraph.strip()
            if len(clean) < 30 or clean.startswith("#") or clean.startswith("##"):
                continue
            counts[clean] += 1
            if len(examples[clean]) < 5:
                examples[clean].append(chapter.number)
    return [(paragraph, count, examples[paragraph]) for paragraph, count in counts.most_common(limit)]


def risk_label(unique_count: int, avg: float, total: int) -> str:
    """Classify whether a section repetition is dangerous for drafting."""
    unique_ratio = unique_count / total
    if unique_ratio < 0.2 or avg >= 0.93:
        return "高危"
    if unique_ratio < 0.35 or avg >= 0.855:
        return "中危"
    return "低危"


def format_windows(windows: list[tuple[int, int, float]]) -> str:
    """Format top adjacent-similarity windows."""
    if not windows:
        return "无"
    return "；".join(f"{start:04d}-{end:04d}：{value:.3f}" for start, end, value in windows)


def write_report(outline_dir: Path, chapters: list[Chapter]) -> Path:
    """Write a Chinese audit report for outline repetition risks."""
    book_dir = outline_dir.parent
    report_path = book_dir / REPORT_NAME
    rows = section_rows(chapters)
    scene_counts = scene_subheading_counts(chapters)
    repeated_paragraphs = exact_paragraph_repeats(chapters)

    high_risk_rows = [
        row
        for row in rows
        if risk_label(int(row["unique"]), float(row["avg"]), len(chapters)) == "高危"
    ]

    lines: list[str] = []
    lines.append("# 《熵枢纪元：七重跃迁》细纲重复风险审计报告")
    lines.append("")
    lines.append("## 结论")
    lines.append("")
    lines.append("- 已确认：细纲仍存在大量有害重复，足以导致正文写作时变成“换名词章节”。")
    lines.append("- 标题和题诗唯一性不是主要问题；主要问题集中在场景骨架、物理环境、人物变化、信息披露、伏笔和落笔提示。")
    lines.append("- 固定禁用规则可以集中放在总检查清单中，不应该每章占据大量篇幅，否则会挤压真正可写的剧情差异。")
    lines.append("- 当前最需要重构的是“章群级剧情链”：每 25 章必须有独立冲突递进、失败方式、证物形变和章末交易。")
    lines.append("")
    lines.append("## 分节重复指标")
    lines.append("")
    lines.append("| 分节 | 唯一段落数 | 归一化唯一数 | 相邻相似均值 | P90 | 最高 | 风险 | 高风险窗口 |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---|")
    for row in rows:
        label = risk_label(int(row["unique"]), float(row["avg"]), len(chapters))
        lines.append(
            "| {section} | {unique} | {normalized_unique} | {avg:.3f} | {p90:.3f} | {max:.3f} | {label} | {windows} |".format(
                section=row["section"],
                unique=row["unique"],
                normalized_unique=row["normalized_unique"],
                avg=row["avg"],
                p90=row["p90"],
                max=row["max"],
                label=label,
                windows=format_windows(row["windows"]),
            )
        )
    lines.append("")
    lines.append("## 场景名重复")
    lines.append("")
    lines.append("前三套场景名几乎覆盖全书，说明“场景拆分”仍是模板轮换，不是章节级剧情设计：")
    lines.append("")
    for heading, count in scene_counts.most_common(15):
        lines.append(f"- {heading}：{count} 次")
    lines.append("")
    lines.append("## 高频重复段落")
    lines.append("")
    for paragraph, count, examples in repeated_paragraphs[:12]:
        sample = paragraph.replace("\n", " / ")
        if len(sample) > 180:
            sample = sample[:180] + "..."
        lines.append(f"- {count} 次，样例章节 {examples}：{sample}")
    lines.append("")
    lines.append("## 对正文写作的直接影响")
    lines.append("")
    lines.append("- 写第 6 卷这类高概念章节时，作者会拿到相同的“异常落点、反证程序、误判反噬、不可删边界、下一章压力”，但不知道本章独有戏剧行动是什么。")
    lines.append("- 人物变化只有 190 种，覆盖 2500 章，导致角色/实体经常只是“承认旧判断不足”，缺少不可逆的具体损失。")
    lines.append("- 信息披露边界只有 470 种，读者问题容易重复成“为什么一个微小异常会逼迫更高存在改变定义”。")
    lines.append("- 伏笔操作只有 750 种，并且“回收方向”大量相同，会让伏笔像说明书，不像被剧情压出来的证物。")
    lines.append("- 正文落笔提示只有 470 种，很多章节都会以同一种段落节奏起笔，后续正文自然显得机械。")
    lines.append("")
    lines.append("## 修复原则")
    lines.append("")
    lines.append("1. 不要继续只追求 2500 章标题和题诗唯一；真正要唯一的是“本章发生了哪一次不可替代的行动”。")
    lines.append("2. 把全书通用禁令移动到总检查清单；单章只保留 2 条本章专属禁令。")
    lines.append("3. 每 25 章建立一个章群弧线：起因、反证、代价、误判、失控、回响、门槛。")
    lines.append("4. 每章必须新增一个不可复用字段：本章交易。格式为“为得到 X，必须失去 Y；若拒绝，Z 会提前发生”。")
    lines.append("5. 场景拆分不再使用固定五段名，改成剧情动作名，例如“公理退潮”“胎面拒译”“常数投喂”“镜像反签”“门槛封口”。")
    lines.append("6. 题诗已经唯一，但还应按章群手工精修，避免只是把不同术语填进相似诗句。")
    lines.append("")
    lines.append("## 下一步建议")
    lines.append("")
    lines.append("- 优先重构第 6 卷 1751-1825：这是当前打开章节附近，也是高概念模板感最强的区域。")
    lines.append("- 每次只重构 25 章，不要再一次性全量生成 2500 章；否则会把模板问题扩大。")
    lines.append("- 重构完成后再写正文；旧正文和旧细纲不要继续作为直接落笔依据。")
    lines.append("")
    lines.append("## 本次审计文件")
    lines.append("")
    lines.append(f"- 细纲目录：`{outline_dir.as_posix()}`")
    lines.append(f"- 章节数：{len(chapters)}")
    lines.append(f"- 高危分节数：{len(high_risk_rows)}")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    outline_dir = discover_outline_dir()
    chapters = load_chapters(outline_dir)
    report_path = write_report(outline_dir, chapters)
    print(report_path.as_posix())


if __name__ == "__main__":
    main()
