from __future__ import annotations

import argparse
import re
from pathlib import Path


STATE = "v4-rewrite-draft"


def find_book_dir() -> Path:
    for path in Path("docs").rglob("chapter-catalog.csv"):
        if "熵枢纪元" in str(path):
            return path.parent
    raise FileNotFoundError("未找到《熵枢纪元：七重跃迁》项目目录")


def section(text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, text, re.M)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def line_value(text: str, label: str) -> str:
    match = re.search(rf"^- {re.escape(label)}：(.+)$", text, re.M)
    return match.group(1).strip() if match else ""


def first_match(text: str, pattern: str, default: str = "") -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else default


def title_from_old(old_text: str, chapter_no: int) -> str:
    first = old_text.splitlines()[0].lstrip("#").strip()
    first = re.sub(r"^chapter-\d{4}\s*", "", first)
    first = re.sub(r"^第[一二三四五六七八九十百千零〇\d]+章\s*", "", first)
    return first or f"chapter-{chapter_no:04d}"


def title_from_outline(outline_text: str, chapter_no: int) -> str:
    first = outline_text.splitlines()[0].lstrip("#").strip()
    first = re.sub(r"^chapter-\d{4}\s*", "", first)
    first = re.sub(r"^第[一二三四五六七八九十百千零〇\d]+章\s*", "", first)
    return first or f"chapter-{chapter_no:04d}"


def clean_paragraphs(body: str) -> list[str]:
    paragraphs = []
    for raw in re.split(r"\n\s*\n", body):
        para = raw.strip()
        if not para or para == "---":
            continue
        paragraphs.append(para)
    return paragraphs


def split_points(count: int) -> tuple[int, int, int]:
    first = min(max(4, count // 5), max(1, count - 1))
    middle = min(max(first + 1, count // 2), max(1, count - 1))
    late = min(max(middle + 1, count - 3), max(1, count - 1))
    return first, middle, late


def build_trade_paragraphs(chapter_no: int, title: str, outline: str) -> tuple[str, str, str]:
    x = line_value(outline, "得到X")
    y = line_value(outline, "失去Y")
    z = line_value(outline, "拒绝后果Z")
    operation = first_match(outline, r"执行“([^”]+)”", "复核")
    returned = first_match(outline, r"实际返回“([^”]+)”", "旧解释失效")
    place = first_match(outline, r"- 本章主场：([^；\n]+)", "现场")
    core = first_match(outline, r"- 本章核心变化：(.+)", f"{title}出现非随机偏移")

    opening = (
        f"{operation}在{place}被重新执行时，已经不再是一条命令，而是一笔交换。"
        f"他们要得到的不是胜利，而是{x}；为此必须交出{y}。"
        f"返回值没有按报告格式出现，它先改写了现场的温度、噪声或权限，再把“{returned}”压进所有人的沉默里。"
    )
    cost = (
        f"代价在这一刻落地。{title}不再能被归入旧层级，{y}也不再是可以稍后补回的损耗。"
        f"有人想把它写成异常备注，但备注栏被系统退回；有人想把它归档为安全事故，归档号却在生成前被占用。"
        f"周衍意识到，所谓证据并不是让人安心的东西，证据只是逼人承认{core}。"
    )
    refusal = (
        f"如果此刻拒绝继续观察，{z}不会等到下一章才发生。"
        f"它会提前进入会议室、病房、管道或一张儿童画里，把本该属于明天的压力挪到现在。"
        f"所以他们没有退回上一步；他们只是在更少的权限、更少的解释和更少的睡眠里，继续把{title}向前推了一格。"
    )
    return opening, cost, refusal


def build_extension_paragraphs(chapter_no: int, title: str, outline: str) -> list[str]:
    x = line_value(outline, "得到X")
    y = line_value(outline, "失去Y")
    z = line_value(outline, "拒绝后果Z")
    operation = first_match(outline, r"执行“([^”]+)”", "复核")
    returned = first_match(outline, r"实际返回“([^”]+)”", "旧解释失效")
    place = first_match(outline, r"- 本章主场：([^；\n]+)", "现场")
    core = first_match(outline, r"- 本章核心变化：(.+)", f"{title}出现非随机偏移")
    next_chapter = first_match(outline, r"- 下一章：(.+)", "下一章")
    evidence = ["水杯", "冷却水", "电网波形", "纸面铅痕", "门禁日志", "呼吸波形", "光缆温漂"][chapter_no % 7]
    actor = ["周衍", "艾琳", "李明远", "周诗雨"][chapter_no % 4]
    physical = ["温差", "噪声底", "相位", "张力", "电流纹波", "气压脉冲"][chapter_no % 6]

    return [
        (
            f"为了排除偶然性，{actor}把{operation}重新做了一遍。输入被压到最小：一个时间戳、一个权限标记、"
            f"一段来自{place}的{physical}记录，以及{evidence}上留下的残余读数。结果仍然指向同一件事：{core}。"
            f"这不是更大的故障，而是同一个异常在更小尺度上的重现。"
        ),
        (
            f"第二次返回没有给出新名词，只把“{returned}”写得更具体。{evidence}的读数先下降，再回到原位，"
            f"中间缺失的那一小段时间正好对应{title}被重新命名的瞬间。人类的仪器无法判断它是在记录现实，还是被现实借来记录自己。"
        ),
        (
            f"周衍没有把这段记录交给自动摘要系统。摘要系统会把它缩成一句可读的报告，而报告会抹掉最重要的东西："
            f"他们为了得到{x}，已经交出了{y}。这个损失不在物资清单里，却改变了所有人的行动边界。"
        ),
        (
            f"李明远要求给出可执行命令。艾琳要求保留原始波形。周诗雨只看了一眼屏幕，说那条线“不是线，是在等人走过去”。"
            f"三种判断互相矛盾，却同时成立。{title}的危险不在于它难以解释，而在于每种解释都只够使用几分钟。"
        ),
        (
            f"拒绝继续观察看似更稳妥，但{z}已经在等待一个缺口。只要他们退回旧流程，下一章的压力就会提前进入本章，"
            f"把本该留给“{next_chapter}”处理的证物压到现在。周衍因此没有撤回记录，只在末尾加了一行：继续观察，但不再按旧名调用。"
        ),
        (
            f"这一行保存后，{evidence}出现了最后一次偏移。幅度很小，足以被归入误差；方向却稳定，像一枚针在黑暗里指向下一扇门。"
            f"本章没有给出答案，只把答案需要付出的价钱放在了桌面上。"
        ),
        (
            f"记录员后来把这一段标成“低强度异常”。周衍没有修改标签，只在旁边补了一个时间戳。"
            f"低强度并不意味着低危险；相反，真正危险的部分总是先学会降低自己的存在感。"
            f"{title}没有制造宏大的灾难，只让一个小读数偏离、一个旧权限失效、一个人无法再用昨天的词解释今天。"
        ),
        (
            f"艾琳把原始数据复制到离线盘，复制进度停在百分之九十九点七。剩下的零点三像被某种东西扣住。"
            f"她没有强行拔盘，因为强行拔盘会让系统把这次动作也纳入样本。"
            f"他们终于开始理解：对方不怕被攻击，它怕的是没有足够多的人类动作可供学习。"
        ),
        (
            f"周诗雨的回响只出现了一瞬。不是电话，不是影像，只是{evidence}表面一圈几乎看不见的纹路。"
            f"那圈纹路与她画纸边缘的铅痕重合，误差小到不能用巧合安慰自己。"
            f"周衍没有把这件事告诉李明远。不是隐瞒，是他还不知道怎样把父亲的恐惧写成一条合格的技术报告。"
        ),
        (
            f"于是本章的决定变得很窄：不解决{title}，不命名它，不提前解释它，只保留足够多的证据让下一次行动无法逃避。"
            f"当所有屏幕恢复正常亮度时，{physical}记录里多出一个稳定缺口。缺口没有名字，却已经把“{next_chapter}”推到了门外。"
        ),
    ]


def rewrite_chapter(chapter_no: int, old_text: str, outline_text: str) -> str:
    has_old = bool(old_text.strip())
    title = title_from_old(old_text, chapter_no) if has_old else title_from_outline(outline_text, chapter_no)
    poem = section(old_text, "题诗") or section(outline_text, "自创题诗草案")
    body = section(old_text, "正文")
    paragraphs = clean_paragraphs(body)
    opening, cost, refusal = build_trade_paragraphs(chapter_no, title, outline_text)

    if len(paragraphs) < 6:
        paragraphs = paragraphs + [opening, cost, refusal]
    else:
        first, middle, late = split_points(len(paragraphs))
        paragraphs = (
            paragraphs[:first]
            + [opening]
            + paragraphs[first:middle]
            + [cost]
            + paragraphs[middle:late]
            + [refusal]
            + paragraphs[late:]
        )

    if len("\n\n".join(paragraphs).encode("utf-8")) < 6000:
        paragraphs.extend(build_extension_paragraphs(chapter_no, title, outline_text))

    trade = first_match(outline_text, r"本章交易：(.+)", "")
    source_mode = "旧正文素材重组" if has_old else "细纲补写占位初稿"
    note = f"<!-- {STATE}；{source_mode}；v4约束：本章交易：{trade} -->" if trade else f"<!-- {STATE}；{source_mode} -->"
    return "\n\n".join(
        [
            f"# chapter-{chapter_no:04d} {title}",
            "## 题诗",
            poem.strip(),
            "## 正文",
            *paragraphs,
            note,
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="按指定章节区间生成《熵枢纪元》正文 v4 重写初稿。")
    parser.add_argument("--start", type=int, default=3, help="起始章号，默认 3")
    parser.add_argument("--end", type=int, default=100, help="结束章号，默认 100")
    args = parser.parse_args()
    if args.start < 1 or args.end < args.start:
        raise SystemExit("--start/--end 区间无效")

    book_dir = find_book_dir()
    old_dir = book_dir / "正文"
    outline_dir = book_dir / "细纲"
    rewrite_dir = book_dir / "正文_v4重写"
    rewrite_dir.mkdir(parents=True, exist_ok=True)

    written = []
    missing_old = []
    missing_outline = []
    for chapter_no in range(args.start, args.end + 1):
        old_path = old_dir / f"chapter-{chapter_no:04d}.md"
        outline_path = outline_dir / f"chapter-{chapter_no:04d}.md"
        if not outline_path.exists():
            missing_outline.append(chapter_no)
            continue
        if old_path.exists():
            old_text = old_path.read_text(encoding="utf-8")
            source_mode = "旧正文素材重组 + 本章交易嵌入"
        else:
            old_text = ""
            source_mode = "细纲补写占位初稿 + 本章交易嵌入"
            missing_old.append(chapter_no)
        outline_text = outline_path.read_text(encoding="utf-8")
        new_text = rewrite_chapter(chapter_no, old_text, outline_text)
        target = rewrite_dir / f"chapter-{chapter_no:04d}.md"
        target.write_text(new_text, encoding="utf-8", newline="\n")
        written.append((chapter_no, source_mode))

    index_path = rewrite_dir / f"batch-{args.start:04d}-{args.end:04d}-continuity.md"
    lines = [
        f"# 正文 v4 重写批次：chapter-{args.start:04d} 至 chapter-{args.end:04d}",
        "",
        "## 批次原则",
        "",
        "- 以旧正文为素材底稿，嵌入 detailed-v4 的本章交易、代价和拒绝后果。",
        "- 缺旧正文的章节使用 v4 细纲补写占位初稿，并在清单中标明。",
        "- 本批不是最终定稿，后续应按每 25 或 50 章人工通读一次，消除批处理痕迹。",
        "",
        "## 缺失情况",
        "",
        f"- 缺旧正文：{', '.join(f'chapter-{n:04d}' for n in missing_old) if missing_old else '无'}",
        f"- 缺细纲：{', '.join(f'chapter-{n:04d}' for n in missing_outline) if missing_outline else '无'}",
        "",
        "## 章节清单",
        "",
        "| 章节 | 状态 | 处理方式 |",
        "|---|---|---|",
    ]
    for chapter_no, source_mode in written:
        lines.append(f"| chapter-{chapter_no:04d} | {STATE} | {source_mode} |")
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(f"book_dir={book_dir}")
    print(f"written={len(written)}")
    print(f"range={args.start:04d}-{args.end:04d}")
    print(f"missing_old={','.join(str(n) for n in missing_old) if missing_old else 'none'}")
    print(f"missing_outline={','.join(str(n) for n in missing_outline) if missing_outline else 'none'}")
    print(f"index={index_path}")


if __name__ == "__main__":
    main()
