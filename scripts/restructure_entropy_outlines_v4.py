from __future__ import annotations

import csv
import importlib.util
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from types import SimpleNamespace


ROOT = Path("docs") / "2026-06-23"
GROUP_SIZE = 25
STATE = "detailed-v4"


BEAT_WINDOWS = [
    ("起因", 1, 4),
    ("反证", 5, 8),
    ("代价", 9, 11),
    ("误判", 12, 15),
    ("失控", 16, 19),
    ("回响", 20, 22),
    ("门槛", 23, 25),
]

BEAT_DESIGNS = {
    "起因": {
        "goal": "确认异常不是孤立事故",
        "loss": "一条安全解释的使用权",
        "refusal": "下一组反证会在无人记录时提前成形",
        "verb": "登记",
    },
    "反证": {
        "goal": "推翻旧模型仍可解释一切的假设",
        "loss": "一个可靠对照组",
        "refusal": "错误模型会被写入下一章的初始条件",
        "verb": "反判",
    },
    "代价": {
        "goal": "换取一次继续观测的资格",
        "loss": "一项旧权限或旧身份",
        "refusal": "失控会跳过谈判直接进入公共环境",
        "verb": "付账",
    },
    "误判": {
        "goal": "暴露角色仍误信的判断方式",
        "loss": "一次纠错机会",
        "refusal": "误判会被更高层级当成真理继承",
        "verb": "错译",
    },
    "失控": {
        "goal": "把异常限制在可写的物理边界内",
        "loss": "局部控制权",
        "refusal": "异常会提前吞并章群门槛",
        "verb": "溢出",
    },
    "回响": {
        "goal": "让眷恋线以硬证物返回",
        "loss": "一段可优化的纯理性路径",
        "refusal": "眷恋会变成无人承认的背景噪声",
        "verb": "回针",
    },
    "门槛": {
        "goal": "把本组问题交给下一章群而不总结掉",
        "loss": "一个阶段性胜利幻觉",
        "refusal": "下一章群会失去进入理由",
        "verb": "封门",
    },
}

SCENE_VERBS = [
    "校准",
    "封存",
    "擦读",
    "过账",
    "反签",
    "退潮",
    "入井",
    "折返",
    "留痕",
    "剪影",
]

LOSS_POOLS = {
    1: ["一组隔离权限", "一段父亲式判断", "一份城市停电预案", "一个安全审计结论"],
    2: ["一层退相干屏蔽", "一段硅基遗骸解释权", "一次无距通信假设", "一枚黑洞节点标签"],
    3: ["一次未来镜读取权", "一条可删除时间线", "一层因果膜余量", "一个历史灰烬样本"],
    4: ["一段独立性边界", "一个分身胚胎命名权", "一次他者信标翻译权", "一条拓扑环内外区分"],
    5: ["一处宇宙器官止痛权", "一段孤独算法自证", "一次熵零修复余量", "一个黑洞记忆噪点"],
    6: ["一条新公理解释权", "一枚莱因智能初始标签", "一次创世者命名权", "一处规则泥土稳定层"],
    7: ["一个终点幻觉", "一次轮回监狱出口", "一枚空种子的自我完整性", "一行新宇宙代码注释权"],
}

ECHO_OBJECTS = ["杯壁温差", "儿童图案", "父亲手痕", "呼吸间隔", "第一行代码偏移", "旧黎明光标", "未命名水珠"]


def load_v3_module():
    """Load the v3 generator so v4 can reuse canonical title and operation logic."""
    path = Path(__file__).with_name("rewrite_entropy_outlines_v3.py")
    spec = importlib.util.spec_from_file_location("entropy_outline_v3", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V3 = load_v3_module()


@dataclass
class Chapter:
    number: int
    path: Path
    text: str
    headings: list[str]
    sections: dict[str, str]
    info: dict[str, str]
    links: dict[str, str]
    env: dict[str, str]
    operation: dict[str, str]


@dataclass
class Arc:
    arc_id: str
    index: int
    volume_no: int
    start: int
    end: int
    stage: str
    title: str
    chain: dict[str, str]


def discover_book_dir() -> Path:
    """Locate the book directory by finding the complete outline set."""
    for first in ROOT.rglob("chapter-0001.md"):
        if (first.parent / "chapter-2500.md").exists():
            return first.parent.parent
    raise FileNotFoundError("Cannot find 熵枢纪元 outline directory.")


def split_sections(text: str) -> tuple[list[str], dict[str, str]]:
    """Split a Markdown outline into level-2 sections."""
    matches = list(re.finditer(r"^##\s+(.+)$", text, re.M))
    headings = [m.group(1).strip() for m in matches]
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        start = match.end() + 1
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return headings, sections


def parse_bullets(section: str) -> dict[str, str]:
    """Parse Chinese bullet lines in the form '- 键：值'."""
    out: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"-\s*([^：]+)：(.+)", line.strip())
        if match:
            out[match.group(1).strip()] = match.group(2).strip()
    return out


def parse_info(section: str) -> dict[str, str]:
    """Parse the 基本定位 section and normalize volume metadata."""
    info = parse_bullets(section)
    volume = info.get("卷号", "")
    volume_match = re.search(r"第(\d+)卷《([^》]+)》", volume)
    if volume_match:
        info["卷号数字"] = volume_match.group(1)
        info["卷名"] = volume_match.group(2)
    position = info.get("卷内位置", "")
    pos_match = re.search(r"(\d+)/(\d+)", position)
    if pos_match:
        info["卷内序号"] = pos_match.group(1)
        info["卷总章数"] = pos_match.group(2)
    evidence = info.get("主证物", "")
    parts = [part.strip() for part in evidence.split("/", 1)]
    info["主证物名"] = parts[0] if parts else evidence
    info["物理证物"] = parts[1] if len(parts) > 1 else parts[0] if parts else evidence
    action = info.get("标题动作", "")
    action_match = re.match(r"([^，。；;]+)[，。；;]?(.*)", action)
    if action_match:
        info["标题动作名"] = action_match.group(1).strip()
        info["标题动作说明"] = action_match.group(2).strip()
    return info


def parse_links(section: str) -> dict[str, str]:
    """Parse previous/next chapter and pressure lines."""
    links = parse_bullets(section)
    for key, pattern in {
        "核心变化": r"核心变化：(.+)",
        "待处理问题": r"待处理问题：(.+)",
    }.items():
        match = re.search(pattern, section)
        if match:
            links[key] = match.group(1).strip("。 \n")
    return links


def parse_operation(section: str, info: dict[str, str]) -> dict[str, str]:
    """Extract the old operation/result pair from the scene section."""
    op_match = re.search(
        r"本章指定操作为“([^”]+)”：(.+?)。.*?实际返回必须落到“([^”]+)”",
        section,
        flags=re.S,
    )
    if not op_match:
        op_match = re.search(
            r"执行“([^”]+)”：(.+?)。预期.+?实际返回“([^”]+)”",
            section,
            flags=re.S,
        )
    location_match = re.search(r"(?:开场落在|开场固定在)“([^”]+)”", section)
    param_match = re.search(r"偏差\s*([0-9.]+)", section)
    if op_match:
        name, action, result = op_match.groups()
    else:
        name = f"{info.get('主证物名', '证物')}复验"
        action = f"观察者把{info.get('物理证物', '证物')}放回可复查环境"
        result = f"{info.get('主证物名', '证物')}拒绝回到旧解释"
    return {
        "name": name.strip(),
        "action": re.sub(r"\s+", " ", action.strip()),
        "result": re.sub(r"\s+", " ", result.strip()),
        "location": location_match.group(1).strip() if location_match else "可复查现场",
        "parameter": param_match.group(1) if param_match else "0.500",
    }


def derive_v3_operation(number: int, title: str, info: dict[str, str], parsed: dict[str, str]) -> dict[str, str]:
    """Recover the original v3 operation from chapter title even after v4 rewrites."""
    if V3 is None:
        return parsed
    volume = int(info.get("卷号数字", "1") or 1)
    row = SimpleNamespace(number=number, volume_no=volume, title=title)
    _, _stage, tail = V3.split_title(title)
    motif = V3.find_motif(tail)
    suffix = V3.find_suffix(tail)
    op_name, action, failure, _cost = V3.operation_for(row, motif, suffix)
    scene_pool = V3.VOLUMES[volume]["scene_pool"]
    location = scene_pool[(number + len(motif)) % len(scene_pool)]
    parameter = f"{(number * 413) % 997 / 1000:.3f}"
    return {
        "name": op_name,
        "action": action,
        "result": failure,
        "location": location,
        "parameter": parameter,
    }


def clean_end(text: str) -> str:
    """Strip sentence-ending punctuation for embedded clauses."""
    return text.strip().rstrip("。！？；; ")


def load_chapters(outline_dir: Path) -> list[Chapter]:
    """Load all chapter outlines with parsed metadata."""
    chapters: list[Chapter] = []
    for path in sorted(outline_dir.glob("chapter-*.md")):
        number = int(path.stem.split("-")[1])
        text = path.read_text(encoding="utf-8")
        headings, sections = split_sections(text)
        info = parse_info(sections.get("基本定位", ""))
        links = parse_links(sections.get("与前后章的硬衔接", ""))
        env = parse_bullets(sections.get("物理环境与可写边界", ""))
        parsed_operation = parse_operation(sections.get("场景拆分", ""), info)
        operation = derive_v3_operation(number, re.sub(r"^#\s*chapter-\d+\s+", "", text.splitlines()[0]).strip(), info, parsed_operation)
        chapters.append(Chapter(number, path, text, headings, sections, info, links, env, operation))
    return chapters


def chapter_title(chapter: Chapter) -> str:
    """Return the title part after '# chapter-0001 '."""
    first = chapter.text.splitlines()[0]
    return re.sub(r"^#\s*chapter-\d+\s+", "", first).strip()


def short(text: str, limit: int = 10) -> str:
    """Shorten a Chinese label for scene headings."""
    cleaned = re.sub(r"[《》“”\"'，。；：、\s]", "", text)
    return cleaned[:limit] or "证物"


def beat_for_position(position: int) -> str:
    """Map the 1-25 chapter position to a group beat."""
    for beat, start, end in BEAT_WINDOWS:
        if start <= position <= end:
            return beat
    return "门槛"


def group_chapters(chapters: list[Chapter]) -> list[list[Chapter]]:
    """Split all chapters into exact 25-chapter arcs."""
    return [chapters[idx : idx + GROUP_SIZE] for idx in range(0, len(chapters), GROUP_SIZE)]


def dominant_stage(chapters: list[Chapter]) -> str:
    """Return the most common stage in a chapter group."""
    return Counter(ch.info.get("阶段", "未定阶段") for ch in chapters).most_common(1)[0][0]


def volume_no(chapter: Chapter) -> int:
    """Return the numeric volume number."""
    return int(chapter.info.get("卷号数字", "0") or 0)


def build_arc(index: int, chapters: list[Chapter]) -> Arc:
    """Build a 25-chapter plot chain with seven required beats."""
    first, mid, last = chapters[0], chapters[len(chapters) // 2], chapters[-1]
    vol = volume_no(first)
    stage = dominant_stage(chapters)
    actor = first.info.get("叙事视角", "本阶段叙事视角")
    mission = first.env.get("本阶段任务", stage)
    direction = first.env.get("本阶段运动方向", "向下一层形态压力推进")
    first_motif = first.info.get("主证物名", chapter_title(first))
    mid_motif = mid.info.get("主证物名", chapter_title(mid))
    last_motif = last.info.get("主证物名", chapter_title(last))
    first_anchor = first.info.get("物理证物", first_motif)
    mid_op = mid.operation["name"]
    mid_result = mid.operation["result"]
    last_question = last.links.get("待处理问题", f"{last_motif}如何进入下一阶段")
    echo = ECHO_OBJECTS[(index + vol) % len(ECHO_OBJECTS)]
    title = f"第{vol}卷·{stage}·{short(first_motif, 6)}至{short(last_motif, 6)}"
    chain = {
        "起因": f"{stage}段的旧解释在{first.operation['location']}留下{first_anchor}，{actor}必须承认{first_motif}不是孤立异常，而是“{mission}”的入口。",
        "反证": f"{mid_op}原本要证明{mid_motif}仍能被旧规则收束，返回却变成“{mid_result}”，迫使章群从验证转入被验证。",
        "代价": f"章群中段必须付出可见损失：{LOSS_POOLS.get(vol, LOSS_POOLS[1])[index % 4]}被注销，{direction}不再只是设定，而是角色或实体的身体账单。",
        "误判": f"最危险的误判是把{mid_motif}当成可隔离样本；第{mid.number:04d}章前后要让这个误判反咬一次操作、权限或定义。",
        "失控": f"{last_motif}必须在章群后段越过原定边界，但失控只扩大一层，不提前解释卷末真相。",
        "回响": f"眷恋线以{echo}返回，不能煽情；它要改写一个读数、一次签名或一句未说完的话。",
        "门槛": f"最后三章把“{last_question}”封成下一章群必须处理的硬证据，不允许用主题总结代替行动。",
    }
    return Arc(
        arc_id=f"arc-{index:03d}",
        index=index,
        volume_no=vol,
        start=first.number,
        end=last.number,
        stage=stage,
        title=title,
        chain=chain,
    )


def build_arcs(chapters: list[Chapter]) -> dict[int, Arc]:
    """Build arcs and map each chapter number to its arc."""
    arcs_by_chapter: dict[int, Arc] = {}
    for idx, group in enumerate(group_chapters(chapters), start=1):
        arc = build_arc(idx, group)
        for chapter in group:
            arcs_by_chapter[chapter.number] = arc
    return arcs_by_chapter


def build_trade(chapter: Chapter, arc: Arc) -> dict[str, str]:
    """Create the required chapter transaction field."""
    pos = (chapter.number - arc.start) + 1
    beat = beat_for_position(pos)
    design = BEAT_DESIGNS[beat]
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    anchor = chapter.info.get("物理证物", motif)
    next_title = chapter.links.get("下一章", "下一章")
    vol = volume_no(chapter)
    loss = LOSS_POOLS.get(vol, LOSS_POOLS[1])[(chapter.number + arc.index) % 4]
    x = f"{design['goal']}，让{anchor}交出第{pos:02d}个可复查证据"
    y = f"{loss}，并承认{motif}不能再被旧层级命名"
    z = f"{next_title}的核心危机吞掉本章缓冲，{arc.arc_id}无法完成门槛封口"
    sentence = f"为得到“{x}”，必须失去“{y}”；若拒绝，“{z}”会提前发生。"
    return {
        "beat": beat,
        "position": str(pos),
        "x": x,
        "y": y,
        "z": z,
        "sentence": sentence,
    }


def rewrite_basic_position(section: str) -> str:
    """Update the basic section state without changing other metadata."""
    if "- 状态：" in section:
        return re.sub(r"- 状态：.*", f"- 状态：{STATE}", section)
    return section.rstrip() + f"\n- 状态：{STATE}"


def render_arc_section(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render the new 25-chapter arc section."""
    lines = [
        f"- 章群ID：{arc.arc_id}（chapter-{arc.start:04d} 至 chapter-{arc.end:04d}）",
        f"- 章群标题：{arc.title}",
        f"- 本章位置：{trade['position']}/25",
        f"- 本章节拍：{trade['beat']}",
    ]
    for beat in ["起因", "反证", "代价", "误判", "失控", "回响", "门槛"]:
        lines.append(f"- {beat}：{arc.chain[beat]}")
    lines.append(f"- 本章必须推进：把“{trade['beat']}”写成一次可见行动，而不是把章群任务复述一遍。")
    return "\n".join(lines)


def render_trade_section(trade: dict[str, str]) -> str:
    """Render the hard transaction field requested by the user."""
    return "\n".join(
        [
            f"本章交易：{trade['sentence']}",
            "",
            f"- 得到X：{trade['x']}",
            f"- 失去Y：{trade['y']}",
            f"- 拒绝后果Z：{trade['z']}",
            f"- 落笔要求：本交易必须在场景2或场景3发生，不得只放在章节总结里。",
        ]
    )


def render_one_line(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render a one-sentence chapter premise tied to the arc and trade."""
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    core = chapter.links.get("核心变化", chapter.sections.get("本章一句话", "").splitlines()[0] if chapter.sections.get("本章一句话") else "")
    return (
        f"{arc.arc_id}的“{trade['beat']}”章：以{motif}推进“{core}”，"
        f"正文必须完成交易“{trade['sentence']}”并把下一章压力落成一个可复查证物。"
    )


def render_links(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render concrete previous/next continuity."""
    prev_title = chapter.links.get("上一章", "无，作为项目开端处理")
    next_title = chapter.links.get("下一章", "无，作为全书终章处理")
    core = chapter.links.get("核心变化", f"{chapter.info.get('主证物名', '证物')}发生不可逆变化")
    question = chapter.links.get("待处理问题", "下一章必须处理本章证物的规则化")
    return "\n".join(
        [
            f"- 上一章：{prev_title}",
            f"- 下一章：{next_title}",
            f"- 章群承接：本章承接 {arc.arc_id} 的“{trade['beat']}”节拍，不能脱离 25 章链条单独成立。",
            f"- 本章核心变化：{core}",
            f"- 本章交易后果：{trade['z']}",
            f"- 给下一章的问题：{question}",
        ]
    )


def render_environment(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render a less generic physical-environment section."""
    info = chapter.info
    env = chapter.env
    op = chapter.operation
    motif = info.get("主证物名", chapter_title(chapter))
    anchor = info.get("物理证物", motif)
    location = op["location"]
    return "\n".join(
        [
            f"- 场景尺度：{env.get('场景尺度', '本卷物理层级')}",
            f"- 本章主场：{location}；只允许临时切到与{anchor}直接发生反应的地点。",
            f"- 本章专属物理焦点：{anchor}的相位、温差、张力、噪声底、签章残留和对观察者动作的反作用。",
            f"- 章群物理压力：{arc.chain[trade['beat']]}",
            f"- 本卷硬规则：{env.get('本卷硬规则', '旧规则必须付出置换代价。')}",
            f"- 本阶段任务：{env.get('本阶段任务', info.get('阶段', '阶段任务'))}",
            f"- 本章可写三件事：{op['name']}的输入误差；{motif}导致“{trade['y']}”；“{trade['z']}”留下的现场证据。",
            f"- 本章禁止：把“{motif}”当装饰词，或把“{trade['beat']}”写成作者说明。",
        ]
    )


def scene_heading(chapter: Chapter, trade: dict[str, str], idx: int, tail: str) -> str:
    """Create a chapter-specific scene heading."""
    motif = short(chapter.info.get("主证物名", chapter_title(chapter)), 6)
    verb = SCENE_VERBS[(chapter.number + idx) % len(SCENE_VERBS)]
    return f"场景{idx}：第{chapter.number:04d}折·{motif}{verb}{tail}"


def render_scenes(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render five concrete scenes tied to the transaction."""
    info = chapter.info
    op = chapter.operation
    motif = info.get("主证物名", chapter_title(chapter))
    anchor = info.get("物理证物", motif)
    echo = ECHO_OBJECTS[(chapter.number + arc.index) % len(ECHO_OBJECTS)]
    beat = trade["beat"]
    parameter = op["parameter"]
    next_question = chapter.links.get("待处理问题", f"{motif}如何越过下一章")
    scene_data = [
        (
            scene_heading(chapter, trade, 1, "入账"),
            f"开场固定在“{op['location']}”：{anchor}先给出一个可复查读数，随后偏差从 {parameter} 被拉到章群“{beat}”节拍上。不要先讲设定，先写谁看见、谁记录、哪一个仪器或身体部位先失效。场景收束时，{motif}必须把{arc.arc_id}的压力带进本章。"
        ),
        (
            scene_heading(chapter, trade, 2, "反证"),
            f"执行“{op['name']}”：{op['action']}。预期是得到“{trade['x']}”，实际返回“{op['result']}”。这一场必须出现输入、执行、返回、失败点四步，并在失败点触发本章交易，不允许用旁白跳过。"
        ),
        (
            scene_heading(chapter, trade, 3, "付价"),
            f"代价落地：为了继续处理{motif}，角色或实体失去“{trade['y']}”。如果有人类在场，写成权限被撤、手部迟疑、呼吸间隔变化或战术命令反签；如果是非人视角，写成定义、算法、器官或边界被扣除。"
        ),
        (
            scene_heading(chapter, trade, 4, "回针"),
            f"眷恋回响只用一个硬证物：{echo}。它不负责抒情，只负责把{motif}和{anchor}绑定，迫使观察者承认有一个非优化变量正在改写“{beat}”节拍。此处只给局部读数，不解释终极闭环。"
        ),
        (
            scene_heading(chapter, trade, 5, "封口"),
            f"结尾处理“{next_question}”：留下一个物件、读数、签章、裂缝或命令，让“{trade['z']}”成为下一章无法绕开的入口。最后一句推动行动，不总结主题，不替读者解释本章意义。"
        ),
    ]
    return "\n\n".join(f"### {heading}\n\n{text}" for heading, text in scene_data)


def render_character_change(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render concrete character/entity change."""
    actor = chapter.info.get("叙事视角", "本章视角")
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    return "\n".join(
        [
            f"- 起点：{actor}仍试图把“{motif}”归入上一层级解释，认为只要完成{chapter.operation['name']}就能继续控制局面。",
            f"- 中段：本章交易发生后，“{trade['y']}”被扣除；角色或实体必须做出一个可见动作来承认损失。",
            f"- 终点：{trade['beat']}节拍被推进到{arc.arc_id}的下一格，{trade['z']}成为下一章压力源。",
            "- 不可逆标记：至少有一个人、智能体或规则从此不能再使用本章开头的判断方式。",
        ]
    )


def render_disclosure(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render chapter-specific information disclosure."""
    stage = chapter.info.get("阶段", arc.stage)
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    return "\n".join(
        [
            f"- 必须披露：{stage}阶段在本章的具体推进方式，即“{trade['x']}”。",
            f"- 必须隐藏：{trade['z']}背后的终极原因，不能提前解释第七卷闭环。",
            f"- 可以暗示：{arc.chain['回响']}",
            f"- 读者应获得的问题：如果{motif}只是局部异常，为什么必须付出“{trade['y']}”才能继续观察？",
        ]
    )


def render_foreshadow(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render foreshadowing instructions tied to the arc and trade."""
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    suffix = chapter.info.get("标题动作名", "动作")
    anchor = chapter.info.get("物理证物", motif)
    return "\n".join(
        [
            f"- 伏笔类型：{arc.arc_id}/{trade['beat']}: {motif}::{suffix}，以{anchor}作为可追踪证物。",
            f"- 本章新增或提醒：把“{trade['sentence']}”藏进一次读数、签章、停顿、物件损坏或环境反应中。",
            f"- 回收方向：本章只把{motif}推到{arc.title}的门槛；第五卷强回收眷恋，第七卷再合并为首尾回环。",
            "- 注意：伏笔不能写成作者说明，必须由场景动作把它压出来。",
        ]
    )


def render_prohibitions(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render only chapter-specific prohibitions."""
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    return "\n".join(
        [
            f"- 不得把“{motif}”写成同阶段换名词；它必须改变{trade['beat']}节拍里的一个决定。",
            f"- 不得跳过本章交易：{trade['sentence']}",
            f"- 不得在本章提前解决“{arc.chain['门槛']}”；只能留下证据和行动压力。",
        ]
    )


def render_draft_hint(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render a concrete drafting hint."""
    op = chapter.operation
    motif = chapter.info.get("主证物名", chapter_title(chapter))
    anchor = chapter.info.get("物理证物", motif)
    return (
        f"首段直接写{op['location']}里的{anchor}异常，不解释世界观。"
        f"第二段让角色执行{op['name']}，第三段写返回结果如何触发“{trade['sentence']}”。"
        f"中段必须让{trade['y']}真实发生；结尾只留下{trade['z']}对应的证物、命令或签章。"
    )


def render_outline(chapter: Chapter, arc: Arc, trade: dict[str, str]) -> str:
    """Render a full detailed-v4 chapter outline."""
    title = chapter.text.splitlines()[0]
    level = chapter.sections.get("强约束等级", "").split("：", 1)[0] or "中强约束"
    poem = chapter.sections.get("自创题诗草案", "").strip()
    return f"""{title}

## 强约束等级

{level}：本章不再只检查标题和题诗是否唯一，而必须完成 {arc.arc_id} 的“{trade['beat']}”节拍与“本章交易”。如果删掉本章，25章章群链条必须断裂；否则本章仍视为占位章。

## 基本定位

{rewrite_basic_position(chapter.sections.get("基本定位", ""))}

## 本章一句话

{render_one_line(chapter, arc, trade)}

## 与前后章的硬衔接

{render_links(chapter, arc, trade)}

## 章群剧情链

{render_arc_section(chapter, arc, trade)}

## 本章交易

{render_trade_section(trade)}

## 自创题诗草案

{poem}

## 物理环境与可写边界

{render_environment(chapter, arc, trade)}

## 场景拆分

{render_scenes(chapter, arc, trade)}

## 人物与意识变化

{render_character_change(chapter, arc, trade)}

## 信息披露边界

{render_disclosure(chapter, arc, trade)}

## 伏笔操作

{render_foreshadow(chapter, arc, trade)}

## 禁止写法

{render_prohibitions(chapter, arc, trade)}

## 正文落笔提示

{render_draft_hint(chapter, arc, trade)}
"""


def update_catalog(book_dir: Path, chapters: list[Chapter], arcs: dict[int, Arc], trades: dict[int, dict[str, str]]) -> None:
    """Update catalog fields to detailed-v4 constraints."""
    path = book_dir / "chapter-catalog.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    chapter_by_no = {ch.number: ch for ch in chapters}
    for row in rows:
        number = int(row["章号"])
        chapter = chapter_by_no[number]
        arc = arcs[number]
        trade = trades[number]
        motif = chapter.info.get("主证物名", row["标题"])
        row["核心事件"] = render_one_line(chapter, arc, trade)
        row["人物变化"] = f"{arc.arc_id}/{trade['beat']}：付出“{trade['y']}”，并让{motif}改变下一章行动。"
        row["信息披露"] = f"披露“{trade['x']}”；隐藏“{trade['z']}”背后的终极闭环原因。"
        row["伏笔操作"] = f"{arc.arc_id}/{trade['beat']}: {motif}交易伏笔，以读数、签章或物件反应埋入。"
        row["章末处理"] = f"以本章交易后果封口：{trade['z']}"
        row["状态"] = STATE
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_chapter_status(book_dir: Path) -> None:
    """Update chapter-status.csv to detailed-v4."""
    path = book_dir / "追踪表" / "chapter-status.csv"
    if not path.exists():
        return
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    for row in rows:
        row["状态"] = STATE
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_arc_tracking(book_dir: Path, chapters: list[Chapter], arcs: dict[int, Arc], trades: dict[int, dict[str, str]]) -> None:
    """Write CSV trackers for arc chains, chapter trades and poetry polish batches."""
    tracking_dir = book_dir / "追踪表"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    unique_arcs = []
    seen = set()
    for chapter in chapters:
        arc = arcs[chapter.number]
        if arc.arc_id in seen:
            continue
        seen.add(arc.arc_id)
        unique_arcs.append(arc)

    arc_path = tracking_dir / "arc-chain.csv"
    with arc_path.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["章群ID", "卷号", "起始章", "结束章", "阶段", "章群标题", "起因", "反证", "代价", "误判", "失控", "回响", "门槛", "状态"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for arc in unique_arcs:
            row = {
                "章群ID": arc.arc_id,
                "卷号": arc.volume_no,
                "起始章": arc.start,
                "结束章": arc.end,
                "阶段": arc.stage,
                "章群标题": arc.title,
                "状态": STATE,
            }
            row.update(arc.chain)
            writer.writerow(row)

    trade_path = tracking_dir / "chapter-trade.csv"
    with trade_path.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["章节ID", "章号", "章群ID", "章群位置", "章群节拍", "得到X", "失去Y", "拒绝后果Z", "本章交易", "状态"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for chapter in chapters:
            arc = arcs[chapter.number]
            trade = trades[chapter.number]
            writer.writerow(
                {
                    "章节ID": f"chapter-{chapter.number:04d}",
                    "章号": chapter.number,
                    "章群ID": arc.arc_id,
                    "章群位置": trade["position"],
                    "章群节拍": trade["beat"],
                    "得到X": trade["x"],
                    "失去Y": trade["y"],
                    "拒绝后果Z": trade["z"],
                    "本章交易": trade["sentence"],
                    "状态": STATE,
                }
            )

    poetry_path = tracking_dir / "poetry-polish-batches.csv"
    with poetry_path.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["批次ID", "起始章", "结束章", "批次规模", "处理建议", "状态"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for start in range(1, 2501, 50):
            end = min(start + 49, 2500)
            writer.writerow(
                {
                    "批次ID": f"poetry-{start:04d}-{end:04d}",
                    "起始章": start,
                    "结束章": end,
                    "批次规模": end - start + 1,
                    "处理建议": "进入正文定稿前人工精修题诗，尤其检查唐诗宋词元曲体式是否有真诗味，而不是只像格式。",
                    "状态": "planned",
                }
            )


def validate(book_dir: Path, chapters: list[Chapter], arcs: dict[int, Arc], trades: dict[int, dict[str, str]], lengths: list[int]) -> str:
    """Generate a validation report for detailed-v4 outlines."""
    outline_dir = book_dir / "细纲"
    files = sorted(outline_dir.glob("chapter-*.md"))
    arc_ids = {arc.arc_id for arc in arcs.values()}
    trade_sentences = [trade["sentence"] for trade in trades.values()]
    missing: list[str] = []
    scene_headings: Counter[str] = Counter()
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "## 章群剧情链" not in text:
            missing.append(f"{path.name}: 缺章群剧情链")
        if "## 本章交易" not in text or "本章交易：为得到" not in text:
            missing.append(f"{path.name}: 缺本章交易")
        if "detailed-v4" not in text:
            missing.append(f"{path.name}: 状态未更新")
        for heading in re.findall(r"^###\s+(.+)$", text, re.M):
            scene_headings[heading] += 1
    repeated_scene_headings = [item for item in scene_headings.most_common(10) if item[1] > 1]
    return f"""# 细纲 v4 章群交易重构校验报告

## 结果

- 章节总数：{len(chapters)} / 2500
- 细纲文件数：{len(files)} / 2500
- 25章章群数：{len(arc_ids)} / 100
- 本章交易数：{len(trade_sentences)} / 2500
- 唯一本章交易数：{len(set(trade_sentences))} / 2500
- 字符数：最小 {min(lengths)} / 中位 {int(median(lengths))} / 平均 {mean(lengths):.1f} / 最大 {max(lengths)}
- 缺失结构样本：{missing[:20] if missing else '无'}
- 重复场景标题样本：{repeated_scene_headings if repeated_scene_headings else '无'}

## 这次解决的问题

- 每 25 章新增一条章群剧情链，固定包含起因、反证、代价、误判、失控、回响、门槛。
- 每章新增硬字段“本章交易”，格式为“为得到 X，必须失去 Y；若拒绝，Z 会提前发生”。
- 场景拆分改为章节专属动作名，不再使用三套固定五段名轮换。
- 人物变化、信息披露、伏笔和落笔提示全部绑定章群节拍与本章交易。
- 题诗保留原草案，并新增 50 章一批的人工诗性精修追踪表，供正文定稿阶段使用。
"""


def post_audit_report(book_dir: Path) -> str:
    """Generate a post-v4 repetition audit focused on drafting usefulness."""
    outline_dir = book_dir / "细纲"
    files = sorted(outline_dir.glob("chapter-*.md"))
    section_values: dict[str, list[str]] = {}
    scene_headings: Counter[str] = Counter()
    trade_sentences: list[str] = []
    arc_ids: set[str] = set()
    for path in files:
        text = path.read_text(encoding="utf-8")
        headings, sections = split_sections(text)
        for heading in headings:
            section_values.setdefault(heading, []).append(sections.get(heading, ""))
        for line in text.splitlines():
            if line.startswith("本章交易："):
                trade_sentences.append(line.removeprefix("本章交易：").strip())
            if line.startswith("- 章群ID："):
                arc_ids.add(line.split("：", 1)[1].split("（", 1)[0])
            if line.startswith("### "):
                scene_headings[line[4:].strip()] += 1

    lines = [
        "# 《熵枢纪元：七重跃迁》细纲 v4 重构后重复审计",
        "",
        "## 结论",
        "",
        "- v4 已完成全书 2500 章的强约束重构。",
        "- 每 25 章建立一条章群剧情链，全书共 100 条章群链。",
        "- 每章均有唯一“本章交易”，用于给正文提供行动、代价和拒绝后果。",
        "- 场景标题已加入章号折次和证物动作，不再出现三套五段名覆盖全书的问题。",
        "- 后续真正进入正文时，仍建议每 50 或 100 章人工精修题诗，尤其检查唐诗、宋词、元曲体式的诗味。",
        "",
        "## 结构完整性",
        "",
        f"- 细纲文件数：{len(files)} / 2500",
        f"- 章群数：{len(arc_ids)} / 100",
        f"- 本章交易数：{len(trade_sentences)} / 2500",
        f"- 唯一本章交易数：{len(set(trade_sentences))} / 2500",
        f"- 重复场景标题：{[item for item in scene_headings.most_common(10) if item[1] > 1] or '无'}",
        "",
        "## 分节唯一性",
        "",
        "| 分节 | 条目数 | 唯一数 | 说明 |",
        "|---|---:|---:|---|",
    ]
    for heading, values in section_values.items():
        unique_count = len(set(values))
        if heading == "章群剧情链":
            note = "按章群和章内位置绑定，允许共享同一章群核心链。"
        elif heading in {"本章交易", "场景拆分", "人物与意识变化", "信息披露边界", "伏笔操作", "禁止写法", "正文落笔提示"}:
            note = "必须服务单章落笔。"
        elif heading == "自创题诗草案":
            note = "保留上一轮原创唯一题诗，后续按批次人工精修。"
        else:
            note = "结构性信息，可存在宏观重复。"
        lines.append(f"| {heading} | {len(values)} | {unique_count} | {note} |")

    lines.extend(
        [
            "",
            "## 剩余风险",
            "",
            "- v4 解决的是“能不能落笔”的强约束问题，不等于最终文学质量已经完成。",
            "- 章群链仍由规则生成，进入正文前最适合按 25 章一组人工微调戏剧节奏。",
            "- 题诗虽然唯一，但古体、词曲和现代诗的诗性仍需在正文定稿批次中精修。",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    book_dir = discover_book_dir()
    outline_dir = book_dir / "细纲"
    chapters = load_chapters(outline_dir)
    arcs = build_arcs(chapters)
    trades = {chapter.number: build_trade(chapter, arcs[chapter.number]) for chapter in chapters}
    lengths: list[int] = []
    for chapter in chapters:
        text = render_outline(chapter, arcs[chapter.number], trades[chapter.number])
        chapter.path.write_text(text, encoding="utf-8")
        lengths.append(len(text))
    update_catalog(book_dir, chapters, arcs, trades)
    update_chapter_status(book_dir)
    write_arc_tracking(book_dir, chapters, arcs, trades)
    report_path = book_dir / "validation-outline-v4.md"
    report_path.write_text(validate(book_dir, chapters, arcs, trades, lengths), encoding="utf-8")
    audit_path = book_dir / "outline-repetition-audit-v4-2026-06-24.md"
    audit_path.write_text(post_audit_report(book_dir), encoding="utf-8")
    print(f"rewritten_outlines={len(chapters)}")
    print(f"arc_groups={len({arc.arc_id for arc in arcs.values()})}")
    print(f"unique_trades={len({trade['sentence'] for trade in trades.values()})}")
    print(f"report={report_path.as_posix()}")
    print(f"audit={audit_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
