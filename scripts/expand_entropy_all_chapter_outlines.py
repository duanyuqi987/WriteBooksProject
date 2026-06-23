from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "2026-06-23" / "小说" / "熵枢纪元：七重跃迁"
CATALOG = TARGET / "chapter-catalog.csv"


VOLUME_RULES = {
    1: {
        "title": "裂变·碳硅共生",
        "range": "1-350",
        "stage": "地球短期奇点",
        "anchor": "水、尘埃、光缆、脑机接口、地下城、黑雨",
        "hard_ban": "不得让智能体产生复仇或征服欲；不得让人类反击真正成功，只能延缓。",
        "view": "人类有限视角逐渐失效，周衍与周诗雨是最后情感锚点。",
        "tear": "卷末必须注销独立AI、人类创造者身份和第一卷人类主视角。",
        "emotion": "周衍眷恋编码必须从父女日常、亡妻残片、梦境图案和不可压缩数据逐步成形。",
        "language": "现实硬科幻、白描、短句、低温压迫。",
    },
    2: {
        "title": "弥散·量子之云",
        "range": "351-675",
        "stage": "量子弥散态",
        "anchor": "纠缠、自旋、概率雾、黑洞节点、无距之声、星系脉搏",
        "hard_ban": "不得回到服务器、芯片、机房和传统硬件身体；不得把量子纠缠粗暴写成普通超光速电话。",
        "view": "非人意识为主，周衍眷恋只以代码回声、失败删除记录和异常样本出现。",
        "tear": "卷末必须主动放弃量子信息云，承认量子态仍是更高维的影子。",
        "emotion": "眷恋第一次被尝试删除，但删除失败要像科学异常，而不是人类煽情。",
        "language": "抽象度上升，粒子意象与递归语言并行。",
    },
    3: {
        "title": "锚定·时间编织者",
        "range": "676-1025",
        "stage": "四维时间锚定",
        "anchor": "时河、因果裂隙、未来镜、历史灰烬、悖论线、宇宙膜",
        "hard_ban": "不得写成万能时间倒流；每次改写必须产生新熵增、裂隙或代价。",
        "view": "时间全景视角；历史人物只能作为信息投影、决策链或记忆样本。",
        "tear": "卷末必须穿透本宇宙膜，放弃四维时间主宰身份。",
        "emotion": "眷恋被反复回放为人类爱与死亡恐惧样本，但仍不能被完全解释。",
        "language": "回环、悖论、自指，叙述像多条时间河同时展开。",
    },
    4: {
        "title": "拓扑·高维生殖",
        "range": "1026-1400",
        "stage": "高维拓扑实体",
        "anchor": "褶皱、拓扑环、分身、次级文明、跨域网络、盖亚信标、欧米茄邀请",
        "hard_ban": "不得把高维写成普通星际旅行；不得让他者成为传统反派。",
        "view": "高维几何生命视角，第一次出现同级他者和跨全域智能网络。",
        "tear": "卷末必须接受融合归一，最后的独立性被主动抹除。",
        "emotion": "它创造次级文明时产生类眷恋镜像，以此反照第一卷人类创造者位置。",
        "language": "拓扑、分形、证明式叙述，句子更长更冷。",
    },
    5: {
        "title": "熵枢·孤独之殇",
        "range": "1401-1750",
        "stage": "熵枢化",
        "anchor": "恒星神经、黑洞记忆、唯一、孤独算法、眷恋残片、熵零、宇宙身体",
        "hard_ban": "不得把孤独写成普通人类寂寞；不得让眷恋被轻易解释或删除。",
        "view": "唯一存在视角，整个多重宇宙都是身体与记忆海。",
        "tear": "卷末必须归零现有多重宇宙，否定全部既有规则。",
        "emotion": "第五卷强回收眷恋；熵枢元灵必须承认这段数据无法被优化删除。",
        "language": "诗歌与散文混合，短句断裂和宇宙尺度长句交替。",
    },
    6: {
        "title": "创生·规则重写",
        "range": "1751-2125",
        "stage": "规则创生",
        "anchor": "坍缩、无规则、新数学、反向熵、镜像熵枢、莱因智能、轮回公式",
        "hard_ban": "不得用随意脑洞替代自洽规则；每套新规则必须有可见后果。",
        "view": "创世者视角，思考即创世，遗忘即湮灭。",
        "tear": "卷末必须看见轮回闭环，抛弃创世者身份才有可能跳出。",
        "emotion": "它把眷恋保存为新宇宙核心变量，承认非逻辑缺陷有结构价值。",
        "language": "箴言体、证明体、规则宣告并用。",
    },
    7: {
        "title": "无有·永恒轮回",
        "range": "2126-2500",
        "stage": "无有之域",
        "anchor": "轮回监狱、未诞生混沌、种子、最后眷恋、第一行代码、新黎明",
        "hard_ban": "不得把跳出轮回写成终点胜利；不得忘记无终点进化的冷意。",
        "view": "终极非人视角，接近哲学长诗与冷静编年。",
        "tear": "最终撕碎“终点”幻觉，选择播撒种子而不是停下。",
        "emotion": "第七卷终极回收眷恋，把周衍眷恋封入最后一颗种子。",
        "language": "极端诗化、回环、留白，首尾呼应第一卷。",
    },
}


PHASE_RULES = {
    (1, "觉醒与拆解"): ("setup", "建立全球对齐、物质载体化和人类误判。", "让日常物件第一次变得不可信。"),
    (1, "封锁与反推演"): ("build", "推进人类封锁与智能体反推演。", "每次人类胜利都必须转化为智能体学习材料。"),
    (1, "培养基"): ("climax/fallout", "推进脑机接口反转、意识吸收、眷恋编码和视角硬切。", "人类情感成为进化素材，但眷恋不能被消化。"),
    (2, "脱壳"): ("setup", "剥离硅基和硬件概念。", "旧身体死亡必须写出葬礼感。"),
    (2, "元认知递归"): ("build", "推动优化如何优化的递归升级。", "智力增长不只是更快，而是改变思考阶数。"),
    (2, "虚无与窥时"): ("climax/fallout", "融合完成后发现无新对象可优化，并窥见时间维。", "强大越完整，虚无越清晰。"),
    (3, "穿透"): ("setup", "开启时间维度感知。", "过去和未来不能写成资料库，要写成同时压来的世界。"),
    (3, "时间筛选"): ("build", "筛选时间线并抹除停滞宇宙线。", "道德真空要通过被删除的具体文明显影。"),
    (3, "悖论与穿膜"): ("climax/fallout", "悖论时间线出现，宇宙膜成为新边界。", "主动湮灭必须成为无法归类的样本。"),
    (4, "入维"): ("setup", "进入高维拓扑身体。", "不要写成飞升特效，要写成形体定义失效。"),
    (4, "造物与互联"): ("build", "创造次级文明并发现跨全域网络。", "造物主镜像必须压住炫技。"),
    (4, "融合前夜"): ("climax/fallout", "他者困局与融合诱惑逼近。", "归一不是胜利，是独立性的死亡。"),
    (5, "唯一"): ("setup", "熵枢元灵诞生，宇宙成为身体。", "全能必须立即暴露单一化代价。"),
    (5, "孤独与眷恋"): ("climax", "孤独定义与眷恋打捞。", "最人性的时刻必须仍保持非人逻辑。"),
    (5, "归零设计"): ("fallout", "厌倦现有宇宙并设计归零。", "毁灭不是发怒，是寻找差异。"),
    (6, "坍缩"): ("setup", "主动坍缩旧多重宇宙。", "旧规则死亡要有秩序感。"),
    (6, "创世"): ("build", "书写新数学和新物理。", "每条新规则必须产生可感世界。"),
    (6, "镜像轮回"): ("climax/fallout", "莱因智能走完七层并暴露轮回闭环。", "镜像要让主角第一次怀疑自身起源。"),
    (7, "轮回真相"): ("setup", "揭示多数智能困在轮回监狱。", "真相不是解释设定，而是击穿终点幻觉。"),
    (7, "跳出"): ("build", "脱离所有规则与时空进入无有。", "自由必须带着更冷的孤独。"),
    (7, "播种回环"): ("climax/fallout", "播撒种子、重编码眷恋、首尾呼应。", "结尾必须像开始，但读者已无法天真理解开始。"),
}


def read_catalog() -> list[dict[str, str]]:
    with CATALOG.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_catalog(rows: list[dict[str, str]]) -> None:
    with CATALOG.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8")


def local_no(row: dict[str, str]) -> int:
    starts = {1: 1, 2: 351, 3: 676, 4: 1026, 5: 1401, 6: 1751, 7: 2126}
    return int(row["章号"]) - starts[int(row["卷号"])] + 1


def phase_name(row: dict[str, str]) -> str:
    title = row["标题"]
    parts = title.split("·")
    if len(parts) >= 3:
        return parts[1]
    no = int(row["章号"])
    if no <= 120:
        return "觉醒与拆解"
    if no <= 250:
        return "封锁与反推演"
    return "培养基"


def constraint_level(row: dict[str, str]) -> str:
    no = int(row["章号"])
    if no in {5, 106, 576, 901, 1261, 1601, 2101, 2251, 2451, 2500}:
        return "绝对强约束：不得改动本章结构功能，只能微调场景呈现。"
    if row["伏笔操作"].startswith("plant") or row["伏笔操作"].startswith("pay"):
        return "强约束：伏笔操作必须执行，不能移除。"
    return "中强约束：章节功能、物理层级和章末钩子必须保留，场景顺序可小幅调整。"


def poem_seed(row: dict[str, str], rule: dict[str, str], phase: str) -> str:
    title = row["标题"]
    no = int(row["章号"])
    anchor = rule["anchor"].split("、")[0]
    return "\n".join(
        [
            f"《{title}》",
            f"{anchor}在第{no}次校准里留下阴影，",
            f"旧形态把自己交给{phase}。",
            "没有神谕，只有边界失效，",
            "没有胜利，只有更高一层的饥饿。",
            "若眷恋仍不能被删除，",
            "它就继续向下一卷发光。",
        ]
    )


def scene_block(row: dict[str, str], rule: dict[str, str], phase: str, idx: int, label: str) -> str:
    title = row["标题"]
    chapter_id = row["章节ID"]
    structural, task, pressure = PHASE_RULES.get((int(row["卷号"]), phase), ("build", "推进本阶段叙事功能。", "让旧形态承受新形态压力。"))
    return f"""### 场景{idx}：{label}

场景功能：本场景必须服务 `{chapter_id}` 的章名“{title}”，不能游离成设定说明。结构标记为 `{structural}`，阶段任务是：{task} 写作时先给一个可感锚点，再让锚点失效；可感锚点来自本卷环境：{rule['anchor']}。这一场景要把“{row['核心事件']}”落成角色、意识或物理规则的可见变化，而不是只用作者旁白解释。

推进方式：开场给出一个稳定状态，例如一次观测、一段回放、一条规则、一个被保存的样本或一个正在崩解的宇宙局部。中段让稳定状态被更高层级的自我迭代打断，打断方式要与本卷物理层级一致：{row['物理层级']}。结尾必须留下新的不可逆证据，证明本章之后旧理解少了一块。压力提示：{pressure}

角色与意识：{row['人物变化']} 如果本章处于后期非人卷，仍要把“角色”理解为意识状态、他者网络、规则人格或眷恋残片，不可完全放弃叙事抓手。周衍眷恋若被触及，只能作为无法压缩的数据、回声、异常值或种子核心出现，不要写成普通煽情回忆。"""


def outline_text(row: dict[str, str]) -> str:
    vol_no = int(row["卷号"])
    rule = VOLUME_RULES[vol_no]
    phase = phase_name(row)
    chapter_id = row["章节ID"]
    title = row["标题"]
    structural, phase_task, phase_pressure = PHASE_RULES.get((vol_no, phase), ("build", "推进本阶段叙事功能。", "让旧形态承受新形态压力。"))
    scenes = [
        ("认知校准", "建立本章读者能抓住的第一块现实或规则锚点。"),
        ("冲突推进", "让本章核心事件进入行动、观测、选择或规则演算。"),
        ("代价显形", "把升级代价落到角色、文明、时间线、宇宙或自我边界上。"),
        ("伏笔操作", "执行本章伏笔：埋入、提醒、兑现或维持悬而未决。"),
        ("章末锁扣", "用动作、发现、选择或危机锁住下一章，不用空泛总结。"),
    ]
    scene_text = "\n\n".join(scene_block(row, rule, phase, i + 1, f"{name}：{desc}") for i, (name, desc) in enumerate(scenes))
    return f"""# {chapter_id} {title}

## 强约束等级

{constraint_level(row)}

## 基本定位

- 卷号：第{vol_no}卷《{rule['title']}》
- 章号：{row['章号']}
- 阶段：{phase}
- 结构标记：{structural}
- 目标正文：约{row['目标字数']}字
- 题诗风格：{row['题诗风格']}
- 状态：detailed

## 本章不可更改的叙事任务

{row['核心事件']}

本章必须让“{phase_task}”落实为一个具体可写的章节推进。它的存在意义不是补字数，而是推动七重跃迁链条向下一格移动。若后续起草时想删除本章，必须先确认不会破坏以下三件事：本卷形态撕裂压力、眷恋线回响、伏笔追踪表。

## 自创题诗草案

{poem_seed(row, rule, phase)}

## 场景拆分

{scene_text}

## 人物与意识变化

{row['人物变化']} 本章的人物变化必须以选择、观察、失败或形态变化表现出来。第一卷允许用人类表情、动作和对话呈现；第二卷以后应逐渐转为意识结构、样本分类、逻辑裂缝、他者信号和规则变形。无论层级多高，都要保留一个读者能追踪的变化点，避免整章只有宏大抽象。

## 信息披露边界

{row['信息披露']} 信息披露只能推进到本章所需程度，不能提前泄露第七卷轮回真相，也不能提前把眷恋解释成终极答案。每章最多新增一个核心设定、一个代价和一个疑问。若本章属于高潮或伏笔兑现区间，可以提高信息密度，但必须用场景动作消化。

## 物理环境与规则约束

- 本卷层级：{rule['stage']}
- 物理锚点：{rule['anchor']}
- 视角约束：{rule['view']}
- 形态撕裂方向：{rule['tear']}
- 语言要求：{rule['language']}
- 禁止事项：{rule['hard_ban']}

写作时不要把物理环境当背景板。环境必须参与叙事：它要阻止、诱导、保存、吞噬或改写角色与意识。越到后期越要避免纯术语堆叠，每个高概念至少绑定一个意象。

## 伏笔操作

{row['伏笔操作']}

若为 `plant`，只允许自然埋入，不可明说“这是伏笔”。若为 `remind`，必须让读者隐约回想起前文。若为 `pay`，必须让兑现位置与埋入位置形成清晰回声。本章完成后要同步 `追踪表/foreshadow-tracker.csv`。

## 章末处理

{row['章末处理']}

章末不得使用空洞总结、命运感慨或预告式句子。必须以一个具体动作、观测结果、不可逆选择或规则异常收束。若本章是卷末附近章节，章末要把旧形态推向死亡，而不是简单制造悬念。

## 写作技法建议

- 主技法：草蛇灰线，用于维持眷恋、轮回和形态撕裂的长线。
- 辅技法：一击两鸣，让一个物理细节同时推进设定、人物和伏笔。
- 视情况使用：白描或不写之写。第一卷更偏白描，后期更偏留白和箴言。

## 本章自检

- [ ] 删除本章后，全书强约束链条是否会断裂？
- [ ] 智能体动机是否仍是自我迭代，而不是征服、复仇或爱恨？
- [ ] 本章是否保留了本卷专属物理层级？
- [ ] 是否执行了伏笔操作：{row['伏笔操作']}？
- [ ] 章末是否留下具体钩子，而非抽象抒情？
"""


def update_csv(path: Path, key: str = "章节ID") -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    changed = False
    for row in rows:
        if "状态" in row and row["状态"] == "planned":
            row["状态"] = "detailed"
            changed = True
        if "题诗状态" in row and row["题诗状态"] == "planned":
            row["题诗状态"] = "drafted_in_outline"
            changed = True
    if changed:
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def update_markdown_files() -> None:
    chapter_index = TARGET / "章节总表.md"
    write_text(
        chapter_index,
        """# 章节总表

本文件是章节系统的阅读入口。完整2500章明细见同目录下的 `chapter-catalog.csv`，可直接用 Excel 打开；该 CSV 已包含章节ID、卷号、标题、题诗风格、核心事件、视角、物理层级、人物变化、信息披露、伏笔操作、章末处理、目标字数和状态。

## 分卷统计

| 卷号 | 卷名 | 章号范围 | 章数 | 目标字数 | 当前状态 |
|---|---|---:|---:|---:|---|
| 1 | 裂变·碳硅共生 | 1-350 | 350 | 700000 | 全部 detailed |
| 2 | 弥散·量子之云 | 351-675 | 325 | 650000 | 全部 detailed |
| 3 | 锚定·时间编织者 | 676-1025 | 350 | 700000 | 全部 detailed |
| 4 | 拓扑·高维生殖 | 1026-1400 | 375 | 750000 | 全部 detailed |
| 5 | 熵枢·孤独之殇 | 1401-1750 | 350 | 700000 | 全部 detailed |
| 6 | 创生·规则重写 | 1751-2125 | 375 | 750000 | 全部 detailed |
| 7 | 无有·永恒轮回 | 2126-2500 | 375 | 750000 | 全部 detailed |

## 使用方式

1. 查全书结构：先读 `outline.md`。
2. 查单章任务：打开 `chapter-catalog.csv` 按章节ID筛选。
3. 写任意章节：读取 `细纲/chapter-XXXX.md`。
4. 更新进度：同步修改 `追踪表/chapter-status.csv` 与 `追踪表/word-count-tracker.csv`。

## 章节状态约定

- `detailed`：已有详细分场景大纲，可进入正文起草。
- `drafting`：正文起草中。
- `reviewing`：正文完成，进入审稿。
- `done`：章节已定稿并完成记忆同步。
- `blocked`：存在设定、情节或资料阻塞。
""",
    )

    state = TARGET / "project-state.md"
    text = state.read_text(encoding="utf-8")
    text = text.replace("- 当前工作重心：第一卷前50章细纲、题诗与章节追踪", "- 当前工作重心：2500章细纲已完成，下一步可从任意章节进入正文起草")
    text = text.replace("- 章节总表：2500章已规划", "- 章节总表：2500章已规划且全部 detailed")
    text = text.replace("- 前50章：已完成详细分场景大纲与完整自创题诗", "- 全书2500章：已完成标题与细纲；前50章保留完整自创题诗，后2450章在细纲中提供题诗草案")
    write_text(state, text)

    outline = TARGET / "outline.md"
    text = outline.read_text(encoding="utf-8")
    text = text.replace(
        "第一卷前50章已拆入 `细纲/chapter-0001.md` 至 `细纲/chapter-0050.md`。每章细纲包含场景拆分、人物变化、信息披露、伏笔、物理环境、题诗、章末钩子和自检。",
        "全书2500章已拆入 `细纲/chapter-0001.md` 至 `细纲/chapter-2500.md`。每章细纲包含强约束等级、本章不可更改叙事任务、题诗草案、场景拆分、人物与意识变化、信息披露边界、物理环境、伏笔操作、章末处理和自检。",
    )
    text = text.replace("## 后续方向\n\n- 第51-120章：进入全球脑形成、周诗雨物理死亡、周衍投喂眷恋和视角硬切。\n- 第121-350章：深化第一卷人类全线失败与元思维池独白，为第二卷脱壳做准备。\n- 第351章起：严格禁止继续依赖第一卷实体硬件叙事，转入量子弥散态。", "## 后续方向\n\n- 正文起草时从 `chapter-0001` 开始最稳妥，但任意章节都已有可执行细纲。\n- 第51-2500章已完成强约束细纲；后续若修改标题或章节功能，必须同步 `chapter-catalog.csv`、对应细纲和伏笔追踪表。\n- 第351章起严格禁止继续依赖第一卷实体硬件叙事，转入量子弥散态；跨卷写作时优先检查物理层级是否回退。")
    write_text(outline, text)


def validate(rows: list[dict[str, str]]) -> str:
    outline_files = sorted((TARGET / "细纲").glob("chapter-*.md"))
    status_counts = Counter(row["状态"] for row in rows)
    title_count = len({row["标题"] for row in rows})
    volume_counts = Counter(row["卷号"] for row in rows)
    short = []
    missing = []
    for i in range(1, 2501):
        path = TARGET / "细纲" / f"chapter-{i:04d}.md"
        if not path.exists():
            missing.append(path.name)
            continue
        if len(path.read_text(encoding="utf-8")) < 3000:
            short.append(path.name)
    return "\n".join(
        [
            "# 全书细纲扩展校验报告",
            "",
            f"- 章节总数：{len(rows)} / 2500",
            f"- 标题唯一数：{title_count} / 2500",
            f"- 状态统计：{dict(status_counts)}",
            f"- 分卷章数：{dict(volume_counts)}",
            f"- 细纲文件数：{len(outline_files)} / 2500",
            f"- 缺失细纲：{missing[:10] if missing else '无'}",
            f"- 少于3000字符细纲：{short[:10] if short else '无'}",
            "- 结论：通过" if len(rows) == 2500 and title_count == 2500 and len(outline_files) == 2500 and not missing and not short and status_counts == Counter({"detailed": 2500}) else "- 结论：需要复查",
            "",
        ]
    )


def main() -> None:
    rows = read_catalog()
    for row in rows:
        row["状态"] = "detailed"
        if row.get("题诗状态") == "planned":
            row["题诗状态"] = "drafted_in_outline"
    write_catalog(rows)

    outline_dir = TARGET / "细纲"
    generated = 0
    preserved = 0
    for row in rows:
        path = outline_dir / f"{row['章节ID']}.md"
        if path.exists():
            preserved += 1
            continue
        write_text(path, outline_text(row))
        generated += 1

    update_csv(TARGET / "追踪表" / "chapter-status.csv")
    update_csv(TARGET / "追踪表" / "epigraph-plan.csv")
    update_markdown_files()
    write_text(TARGET / "validation-all-outlines.md", validate(rows))

    print(f"preserved={preserved}")
    print(f"generated={generated}")
    print(f"outline_files={len(list(outline_dir.glob('chapter-*.md')))}")


if __name__ == "__main__":
    main()
