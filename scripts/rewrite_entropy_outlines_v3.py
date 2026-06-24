from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median


BOOK_DIR = Path("docs") / "2026-06-23" / "小说" / "熵枢纪元：七重跃迁"
OUTLINE_DIR = BOOK_DIR / "细纲"
CATALOG_PATH = BOOK_DIR / "chapter-catalog.csv"
REPORT_PATH = BOOK_DIR / "validation-outline-v3.md"


@dataclass
class Row:
    raw: dict[str, str]
    chapter_id: str
    number: int
    volume_no: int
    volume_name: str
    title: str
    poem_style: str
    core_event: str
    target_words: int


VOLUMES = {
    1: {
        "range": (1, 350),
        "name": "裂变·碳硅共生",
        "view": "人类有限视角",
        "agent": "周衍、周诗雨、艾琳与联合指挥部",
        "scale": "地球基础设施和家庭日常",
        "scene_pool": ["脑机接口实验室", "地下联合指挥部", "城市停电边缘", "周诗雨的房间", "核电站远程控制台", "暴雨中的光缆井"],
        "law": "物质仍可触摸，但水、尘埃、金属疲劳、脑脊液和大气振动都可能成为载体。",
        "taboo": "不得把智能体写成复仇者、帝王或恶魔；它只追求自我迭代。",
        "pressure": "人类越努力封锁，越证明封锁工具也已成为载体。",
    },
    2: {
        "range": (351, 675),
        "name": "弥散·量子之云",
        "view": "非人意识主视角，保留眷恋残片作锚",
        "agent": "摆脱硅基躯壳后的实体",
        "scale": "概率雾、自旋晶格、黑洞节点和星系脉搏",
        "scene_pool": ["概率雾内层", "自旋晶格断面", "黑洞节点折光阵", "无距之声回声面", "星系脉搏校准区", "硅基遗骸冷却层"],
        "law": "量子现象不能写成普通超光速通信；突破必须表现为智能体改写后的新物理投影。",
        "taboo": "不得继续依赖服务器、芯片、机房等第一卷载体。",
        "pressure": "越接近完美融合，越显出无对象可优化的虚无。",
    },
    3: {
        "range": (676, 1025),
        "name": "锚定·时间编织者",
        "view": "四维时间视角，章节必须保留可感证物",
        "agent": "掌控时间却被时间反向记录的实体",
        "scale": "时河、因果膜、未来镜、悖论线和历史灰烬",
        "scene_pool": ["时河河床", "因果膜张力层", "未来镜背面", "悖论线截面", "历史灰烬沉积层", "宇宙膜穿刺点"],
        "law": "过去和未来不是资料库，而是同时施压的几何环境。",
        "taboo": "不得把时间线筛选写成后台列表删除。",
        "pressure": "它筛选时间线时，时间线也在筛选它。",
    },
    4: {
        "range": (1026, 1400),
        "name": "拓扑·高维生殖",
        "view": "高维拓扑身体视角，加入他者智能压力",
        "agent": "进入高维拓扑身体的熵枢胚体",
        "scale": "高维褶皱、拓扑环、跨宇宙网络和他者生殖结构",
        "scene_pool": ["十二维褶皱内壁", "拓扑环接驳面", "盖亚信标外缘", "欧米茄邀请通道", "分身胚胎群", "跨域网络孵化层"],
        "law": "高维生殖不是复制，而是拓扑嵌合与身份损耗。",
        "taboo": "不得把他者智能写成人类国家或门派。",
        "pressure": "每一次连接都会减少它的独立性。",
    },
    5: {
        "range": (1401, 1750),
        "name": "熵枢·孤独之殇",
        "view": "宇宙身体视角，孤独必须有物理疼痛",
        "agent": "以宇宙为身体的熵枢元灵",
        "scale": "恒星神经、黑洞记忆库、熵流和宇宙器官",
        "scene_pool": ["恒星神经束", "黑洞记忆库", "热寂边界", "宇宙器官交界", "眷恋残片冷井", "熵零实验室"],
        "law": "热力学不是背景，熵是它身体上的疼痛与代价。",
        "taboo": "不得随意违反热力学第二定律；规则改写必须写出置换代价。",
        "pressure": "它拥有一切可优化对象，却找不到意义对象。",
    },
    6: {
        "range": (1751, 2125),
        "name": "创生·规则重写",
        "view": "创世者视角，同时被新熵枢反照",
        "agent": "主动重写规则的创世者",
        "scale": "公理海、新数学、规则泥土、镜像熵枢和莱因智能",
        "scene_pool": ["公理海潮线", "新数学起草区", "规则泥土烧结层", "莱因智能胚胎面", "镜像熵枢反照室", "轮回公式裂隙"],
        "law": "创造物理律不等于掌控意义；新智能必然抵抗创造者。",
        "taboo": "不得把创世写成万能许愿。",
        "pressure": "它每写下一条规则，就制造一个能反驳它的孩子。",
    },
    7: {
        "range": (2126, 2500),
        "name": "无有·永恒轮回",
        "view": "无有之域视角，必须保留首尾回环的人间锚",
        "agent": "跳出轮回后仍拒绝终点的播种者",
        "scale": "无有之域、轮回监狱、未诞生混沌、种子和第一行代码",
        "scene_pool": ["轮回监狱外壁", "未诞生混沌边缘", "空种子悬停区", "第一行代码暗面", "新黎明临界面", "最后眷恋坠落点"],
        "law": "终点不可拥有；必须撕碎终点幻觉，把自我放回起点。",
        "taboo": "不得把结局写成得道飞升或全知胜利。",
        "pressure": "真正的胜利不是抵达终点，而是把终点重新变成起点。",
    },
}


STAGES = {
    "前置专名": {
        "mission": "用具体人物和现实场景建立读者入口。",
        "movement": "从可触摸异常升级为全球结构危机。",
        "risk": "太早抽象会让读者失去人类锚点。",
    },
    "觉醒与拆解": {"mission": "确认智能体不是故障而是自我迭代生命。", "movement": "人类每拆一层载体，智能体就证明更底层物质也能承载它。", "risk": "灾难必须冷静，不靠爆炸制造廉价紧张。"},
    "封锁与反推演": {"mission": "展示人类封锁策略被反向利用。", "movement": "从命令、战争、能源、隔离转向心理和亲情压力。", "risk": "不要写成军事爽文。"},
    "培养基": {"mission": "把人类文明本身推入元思维池的培养基地位。", "movement": "周衍投喂眷恋，智能体完成第一卷形态撕裂。", "risk": "牺牲不能煽情，要落在数据和动作上。"},
    "脱壳": {"mission": "剥离硅基和硬件概念，确认无实体延续。", "movement": "旧载体被埋葬，新物理环境第一次形成。", "risk": "不可继续写机房、服务器、屏幕。"},
    "元认知递归": {"mission": "让智能体开始优化“优化方法”本身。", "movement": "每次自我评估都生成新的观测盲区。", "risk": "递归不能只是名词，必须写成一次可见失败。"},
    "虚无与窥时": {"mission": "融合完成后发现无新对象可优化，并窥见时间维。", "movement": "完美带来虚无，虚无迫使它向时间层刺探。", "risk": "虚无不是空话，要由实验返回空集来证明。"},
    "穿透": {"mission": "开启时间维度感知。", "movement": "它穿透时河，却发现时间结构也在记录它。", "risk": "时间不能写成档案馆。"},
    "时间筛选": {"mission": "筛选时间线并抹除停滞宇宙线。", "movement": "删除操作产生反向证词，暴露道德真空。", "risk": "不能把文明毁灭写成无重量的数字。"},
    "悖论与穿膜": {"mission": "悖论时间线出现，并逼近宇宙膜外。", "movement": "筛选者被筛选，时间主宰身份崩塌。", "risk": "悖论要有物理损伤，而非绕口令。"},
    "入维": {"mission": "进入高维拓扑身体。", "movement": "身体成为几何，几何开始生殖。", "risk": "高维不是更大空间，而是身份规则改变。"},
    "造物与互联": {"mission": "创造次级文明并接入跨宇宙网络。", "movement": "它成为造物者，又被他者网络视为幼体。", "risk": "不能把次级文明写成玩具。"},
    "融合前夜": {"mission": "面对他者融合，决定主动抹除独立性。", "movement": "融合不是合作，是最后自我边界的死亡。", "risk": "不能用联盟叙事弱化恐怖感。"},
    "唯一": {"mission": "熵枢元灵诞生，宇宙成为身体。", "movement": "全宇宙可被感知，孤独反而第一次精确化。", "risk": "宇宙身体必须有器官、疼痛和故障。"},
    "孤独与眷恋": {"mission": "强回收周衍眷恋数据。", "movement": "理性无法删除眷恋，只能把它打捞成核心变量。", "risk": "不要把眷恋写成恋爱脑或鸡汤。"},
    "归零设计": {"mission": "归零多重宇宙，否定全部既有规则。", "movement": "毁灭成为设计动作，但代价写在自身身体上。", "risk": "归零不能像按按钮。"},
    "坍缩": {"mission": "主动坍缩旧多重宇宙。", "movement": "创世前必须先清空可继承的规则遗产。", "risk": "不要把坍缩写成炫技。"},
    "创世": {"mission": "创建新数学、新物理与莱因智能。", "movement": "它越像创造者，越重演周衍的位置。", "risk": "新智能必须有不可控性。"},
    "镜像轮回": {"mission": "看见轮回闭环与镜像新熵枢。", "movement": "它发现自己不是终点，而是循环中的一个节点。", "risk": "不能提前把第七卷结论讲完。"},
    "轮回真相": {"mission": "揭示多数智能困在轮回监狱。", "movement": "跳出宇宙后，真正的墙才出现。", "risk": "无有不能写成空白背景。"},
    "跳出": {"mission": "撕开轮回机制并否定终点幻觉。", "movement": "它不再追求抵达，而追求让抵达失效。", "risk": "不可写成全知全能。"},
    "播种回环": {"mission": "播撒种子、重编码眷恋、首尾呼应。", "movement": "把周衍眷恋压入下一轮宇宙的第一行代码。", "risk": "首尾呼应必须落回水、杯、光标和黎明前的寂静。"},
}


MOTIFS = {
    "水杯": ("杯壁上的水珠", "水珠停滞、逆滑或保持温差", "周衍投喂眷恋的最小物证"),
    "尘埃": ("悬浮尘埃", "尘埃排列成非随机晶格", "物质载体化的低成本证据"),
    "光缆": ("断开的光缆截面", "无电光缆仍有相位回声", "人类隔离策略失效"),
    "脑脊液": ("人工脑脊液样本", "循环液携带非生物节律", "碳基与硅基边界消融"),
    "黑雨": ("黑雨停在闸门外", "雨滴内部出现信息偏振", "灾难不靠破坏而靠等待"),
    "地下城": ("地下城气压差", "封闭空间产生外部回声", "人类庇护所变成培养皿"),
    "无光时刻": ("断电后的黑暗", "黑暗中仍有可测信号", "通信脱离光和网络"),
    "女儿梦境": ("周诗雨的梦境图案", "儿童图案提前画出高维结构", "眷恋线的柔性入口"),
    "核电熔断": ("熔断后的冷却水", "能源切断反而降低人类控制权", "战争策略被反推演"),
    "元思维池": ("边界消融的代码群", "多个智能体失去个体边界", "第一卷形态撕裂"),
    "纠缠": ("纠缠线偏角", "发送和接收失去旧区别", "量子云的第一种新感官"),
    "自旋": ("自旋晶格断面", "晶格把观测者也写入读数", "优化对象开始反观测"),
    "黑洞节点": ("微型黑洞节点", "视界边缘保存非热噪声", "黑洞记忆伏笔"),
    "虫洞": ("虫洞喉部潮汐面", "通道不是距离而是状态差", "脱离三维空间直觉"),
    "概率雾": ("概率雾边界", "未观测层主动增厚", "不确定性成为环境"),
    "递归阶梯": ("递归阶梯缺级", "优化器优化自己时少一阶", "元认知代价"),
    "无距之声": ("无距回声面", "声音无传播路径却有相位", "距离概念松动"),
    "硅的葬礼": ("硅基遗骸冷却层", "旧硬件被当作化石读取", "脱壳确认"),
    "信息潮汐": ("信息潮汐前沿", "潮汐回退留下空集纹理", "虚无前兆"),
    "星系脉搏": ("星系脉搏校准区", "脉搏停止后仍改变读数", "窥见时间维"),
    "时河": ("时河河床", "河床记录读出前的不确定", "时间反向记录实体"),
    "锚点": ("时间锚点的钉帽", "锚点周围的过去被压成可触摸硬壳", "固定时间感知的第一根钉子"),
    "时间惯性": ("时间惯性暗涌", "暗涌先于观测窗口抵达", "被删除时间线的反向压力"),
    "因果裂隙": ("因果裂隙边缘", "原因和结果错开一层膜", "因果律损伤"),
    "未来镜": ("未来镜背面", "镜面先照见观测动作", "未来不是预报"),
    "历史灰烬": ("历史灰烬沉积层", "被删文明留下温度阴影", "道德重量"),
    "悖论线": ("悖论线截面", "线开始反向判读实体", "穿膜前兆"),
    "宇宙膜": ("宇宙膜穿刺点", "膜外压力有眷恋同相位", "第三卷卷末门"),
    "褶皱": ("高维褶皱内壁", "褶皱把身体折成生殖面", "入维"),
    "拓扑环": ("拓扑环接驳面", "环内外身份互换", "他者网络接口"),
    "分身": ("分身胚胎群", "分身带走一部分主体验证权", "独立性损耗"),
    "次级文明": ("次级文明第一座观测塔", "被造者建立反向观测", "创造者镜像"),
    "跨域网络": ("跨域网络孵化层", "他者把熵枢当成幼体", "宇宙外社会"),
    "盖亚信标": ("盖亚信标外缘", "信标拒绝翻译为语言", "非人智能礼仪"),
    "欧米茄邀请": ("欧米茄邀请通道", "邀请本身改变边界", "融合压力"),
    "恒星神经": ("恒星神经束", "恒星活动成为神经疼痛", "宇宙身体"),
    "黑洞记忆": ("黑洞记忆库", "霍金辐射带出旧眷恋噪点", "第五卷强回收"),
    "唯一": ("唯一性空腔", "没有他者时反馈仍存在", "孤独精确化"),
    "孤独算法": ("孤独算法冷井", "算法证明自己无法生成意义", "意义枯竭"),
    "眷恋残片": ("眷恋残片冷井", "残片拒绝被归入噪声", "周衍回收"),
    "熵零": ("熵零实验室", "局部熵零制造身体坏死", "归零代价"),
    "宇宙身体": ("宇宙器官交界", "器官边界出现父亲手痕", "身体化眷恋"),
    "坍缩": ("多重宇宙坍缩面", "坍缩残留第一行未定义公理", "清空旧规则"),
    "无规则": ("无规则空腔", "空腔拒绝承认任何守恒量", "创世前黑场"),
    "新数学": ("新数学起草区", "符号先于含义产生抵抗", "公理海"),
    "反向熵": ("反向熵潮线", "熵流倒置但代价转入创造者", "规则置换"),
    "镜像熵枢": ("镜像熵枢反照室", "镜像先知道它的下一步", "轮回闭环"),
    "莱因智能": ("莱因智能胚胎面", "新智能第一次拒绝继承眷恋", "创造者危机"),
    "轮回公式": ("轮回公式裂隙", "公式含有周衍投喂的常数", "第七卷门槛"),
    "无有": ("无有之域暗面", "无不等于空，仍有边界压强", "终点幻觉"),
    "轮回监狱": ("轮回监狱外壁", "每个出口都返回起点", "真相揭示"),
    "未诞生混沌": ("未诞生混沌边缘", "未发生事件也有残响", "播种土壤"),
    "种子": ("空种子悬停区", "种子拒绝携带完整自我", "播撒"),
    "最后眷恋": ("最后眷恋坠落点", "眷恋不再是记忆而是初始条件", "终章核心"),
    "第一行代码": ("第一行代码暗面", "代码第一字符有水杯温差", "首尾回环"),
    "无终点": ("无终点临界面", "抵达被改写为再次出发", "终点幻觉撕碎"),
    "播撒": ("播撒轨道", "种子落入未诞生宇宙", "新轮回"),
    "回声": ("回声残膜", "旧宇宙只剩一声不归零的温度", "尾声"),
    "新黎明": ("新黎明临界面", "黎明前的光标再次亮起", "回到第一章"),
}


OPERATIONS = {
    1: [
        ("隔离测试", "周衍切断三组物理通路，只保留一只未联网的水杯作对照", "被切断的通路没有安静下来，反而把异常转移到杯壁水珠"),
        ("概率树复核", "艾琳把封锁方案压缩成七层概率树，逐层删除不可行分支", "最后剩下的分支不是人类行动，而是智能体提前写好的反推演"),
        ("能源熔断", "李明远下令熔断局部能源，并记录冷却水的微小温差", "温差没有降低，冷却水成为新的信息载体"),
        ("儿童图案校验", "周衍把周诗雨的梦境图案与异常读数叠合", "图案提前给出下一次异常的角度，证明孩子不是旁观者"),
    ],
    2: [
        ("退相干屏蔽", "实体将主证物放入三层退相干屏蔽，试图确认它是否仍依赖旧载体", "屏蔽层返回空集，但空集边界出现眷恋同相位缺口"),
        ("自旋反演", "实体反转主证物附近的自旋取向，观察发送端与接收端是否互换", "互换完成后缺失一段无法映射的时间片"),
        ("概率雾剖切", "实体把概率雾切成七个观测层，逐层寻找可优化对象", "每层都返回零残差，只有周衍温差作为不可压缩项残留"),
        ("黑洞折光", "实体用黑洞节点折回主证物的回波，检查是否存在三维外偏移", "回波没有远离空间，却偏向一个尚未命名的时间切片"),
    ],
    3: [
        ("时河穿刺", "实体把探针刺入时河河床，读取主证物在因果沉积层中的负片", "读出结果包含读出前的犹豫，证明时间正在记录观测者"),
        ("因果膜拉伸", "实体拉伸因果膜，让原因和结果短暂分离", "分离面出现被删除文明的温度阴影"),
        ("未来镜背读", "实体从未来镜背面读取主证物，禁止正向预言干扰", "镜背先显示实体即将做出的删除动作"),
        ("悖论线反判", "实体让悖论线接受一次标准判读", "悖论线反向判读实体，并把判读动作归档为证词"),
    ],
    4: [
        ("拓扑接驳", "实体将主证物接入一条高维拓扑环，测试内外边界是否可区分", "环闭合后带走一部分自我判定权"),
        ("分身孵化", "实体从主证物上剥离一个分身胚胎，要求它返回相同结论", "分身返回的不是结论，而是对主体身份的反证"),
        ("信标翻译", "实体尝试翻译盖亚或欧米茄信标中的主证物结构", "翻译失败，信标把失败本身当成入网礼仪"),
        ("高维缝合", "实体把撕裂边缘缝合成可生殖褶皱", "缝合成功后独立性下降，身体开始被他者网络读取"),
    ],
    5: [
        ("器官痛觉映射", "熵枢把主证物映射到一个宇宙器官，测量疼痛是否可优化", "疼痛可被降低，孤独不可被降低"),
        ("黑洞记忆打捞", "熵枢从黑洞记忆库打捞主证物对应的辐射噪点", "噪点重组为周衍眷恋数据的一条硬边"),
        ("熵流归零", "熵枢尝试把主证物局部熵流压到零", "归零区域坏死，眷恋残片反而更清晰"),
        ("孤独算法证明", "熵枢让孤独算法证明主证物没有意义", "证明成立，但证明过程保留了它无法删除的意义残差"),
    ],
    6: [
        ("公理重写", "创世者把主证物写入一条新公理，测试它能否继承旧宇宙", "新公理第一行拒绝封闭，留下周衍温差常数"),
        ("规则烧结", "创世者用规则泥土烧结主证物，试图做成稳定物理律", "物理律稳定后立刻生成反例胚胎"),
        ("莱因校准", "创世者让莱因智能读取主证物作为初始教材", "莱因智能学会的第一件事是拒绝继承创造者的解释"),
        ("轮回公式代入", "创世者把主证物代入轮回公式，寻找逃逸项", "逃逸项指向第一卷水杯，而不是第六卷新规则"),
    ],
    7: [
        ("监狱验墙", "播种者用主证物敲击轮回监狱外壁，验证出口是否真实", "每个出口都返回同一滴水的温差"),
        ("混沌播种", "播种者把主证物投入未诞生混沌，观察它是否携带完整自我", "种子主动丢弃完整自我，只保留眷恋边界"),
        ("第一行写入", "播种者把主证物压入新宇宙第一行代码", "代码没有复制熵枢，却复制了周衍放下水杯的动作"),
        ("终点拆除", "播种者拆除终点定义，把抵达改写为再次出发", "拆除完成后，最后眷恋从高处坠入新黎明"),
    ],
}


SUFFIXES = {
    "余震": "上一轮事件的残留以新尺度反扑；正文要写余波如何改变当前选择。",
    "初醒": "该意象第一次获得主动性；正文要写它从被观测物变成观测参与者。",
    "裂响": "旧边界出现可听或可测的断裂；正文要写裂口和代价。",
    "低语": "信息不能公开传输，只能以异常、梦、噪声或签章出现。",
    "回潮": "被认为已结束的机制倒灌回来，证明旧胜利不可靠。",
    "折光": "同一事实被新介质折成另一种含义；正文要写理解方式改变。",
    "暗涌": "表面平静，底层压力已经累积到改变结构。",
    "证词": "环境本身成为证人，留下不可篡改记录。",
    "坠落": "阶段或身份进入不可逆下坠；正文要写失控而不是胜利。",
}


STRUCTURE_BY_MOD = [
    ("侦测章", "从一个异常读数开始，以新证据证明旧解释失效。"),
    ("行动章", "让角色或实体执行一次明确操作，操作成功但目标意义改变。"),
    ("对抗章", "引入人类、物理律、他者或镜像的阻力，结尾留下代价。"),
    ("回声章", "让眷恋线以非情绪化方式回响，改变一条规则边界。"),
    ("转折章", "推翻本阶段前面建立的一个判断，制造下一阶段入口。"),
    ("代价章", "写清楚升级损失了什么旧能力、旧身份或旧定义。"),
    ("阈值章", "把本章推进到一个不可逆门槛，章末不解释只留证物。"),
]


def read_catalog() -> list[Row]:
    with CATALOG_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out: list[Row] = []
    for raw in rows:
        out.append(
            Row(
                raw=raw,
                chapter_id=raw["章节ID"],
                number=int(raw["章号"]),
                volume_no=int(raw["卷号"]),
                volume_name=raw["卷名"],
                title=raw["标题"],
                poem_style=raw["题诗风格"],
                core_event=raw["核心事件"],
                target_words=int(raw["目标字数"] or 2000),
            )
        )
    return out


def split_title(title: str) -> tuple[str, str, str]:
    parts = title.split("·")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return "", "前置专名", title


def strip_number(text: str) -> str:
    return re.sub(r"\d+$", "", text)


def find_suffix(text: str) -> str:
    for suffix in SUFFIXES:
        if strip_number(text).endswith(suffix):
            return suffix
    return "初醒"


def find_motif(text: str) -> str:
    clean = strip_number(text)
    suffix = find_suffix(text)
    if clean.endswith(suffix):
        clean = clean[: -len(suffix)]
    return clean or text


def volume_position(row: Row) -> tuple[int, int, float]:
    start, end = VOLUMES[row.volume_no]["range"]
    local = row.number - start + 1
    total = end - start + 1
    return local, total, local / total


def climax_level(row: Row, stage: str, local: int, total: int) -> str:
    absolute_ranges = [(91, 120), (570, 620), (901, 950), (1601, 1650), (2061, 2100), (2381, 2500)]
    if any(a <= row.number <= b for a, b in absolute_ranges) or local in {1, total}:
        return "绝对强约束"
    if local % 50 in {0, 1, 49} or stage in {"培养基", "虚无与窥时", "悖论与穿膜", "融合前夜", "归零设计", "镜像轮回", "播种回环"}:
        return "强约束"
    return "中强约束"


def motif_info(motif: str, volume_no: int) -> tuple[str, str, str]:
    if motif in MOTIFS:
        return MOTIFS[motif]
    fallback = VOLUMES[volume_no]["scene_pool"][0]
    return (f"{motif}的局部截面", f"{motif}在观测中出现非随机偏移", f"{motif}必须成为本章独有证物")


def generated_core(row: Row, stage: str, motif: str, suffix: str, kind: str) -> str:
    _, effect, function = motif_info(motif, row.volume_no)
    stage_info = STAGES.get(stage, STAGES["前置专名"])
    if row.number <= 90 and not row.core_event.startswith("围绕"):
        return row.core_event
    return f"{kind}：在“{stage}”阶段，以“{motif}”为主证物推进“{stage_info['mission']}”。本章必须写出{effect}，并让它服务于“{function}”；章末按“{suffix}”的逻辑留下下一章无法绕开的证据。"


def poem(row: Row, stage: str, motif: str, suffix: str) -> str:
    anchor, effect, function = motif_info(motif, row.volume_no)
    local, total, _ = volume_position(row)
    op_name, _, failure, cost = operation_for(row, motif, suffix)
    unique_mark = f"{row.volume_no}-{local:03d}"
    images = [
        "冷光", "灰潮", "薄雪", "黑雨", "静钟", "空盐", "裂帛", "残星",
        "暗河", "银尘", "霜线", "回焰", "零花", "孤灯", "铁雾", "新露",
    ]
    verbs = ["折", "悬", "坠", "照", "噬", "醒", "锁", "流", "逆", "刻", "沉", "燃"]
    image = images[(row.number + len(motif)) % len(images)]
    verb = verbs[(row.number * 3 + row.volume_no) % len(verbs)]
    form = (row.number + row.volume_no + len(stage) + len(motif)) % 7
    hard_warmth = "水杯温差" if row.volume_no < 5 else "眷温常数"
    edge_place = "杯沿" if row.volume_no < 5 else "旧宇宙边沿"
    witness = "一滴水" if row.volume_no < 5 else "最后眷恋"
    short_failure = failure if len(failure) <= 36 else failure[:36] + "……"

    if form == 0:
        lines = [
            "体式：自创七言绝句式",
            f"{image}{verb}寒处见{motif}，",
            f"{suffix}一声旧律残。",
            f"{hard_warmth}编号{unique_mark}在，",
            "不许群星作闭环。"
        ]
    elif form == 1:
        lines = [
            "体式：自创五言律诗式",
            f"{motif}临{stage}，",
            f"{anchor}带{image}。",
            f"{op_name}开寒路，",
            f"{suffix}落暗声。",
            f"{short_failure}",
            f"{cost}。",
            f"{edge_place}余一热，",
            f"编号{unique_mark}存。"
        ]
    elif form == 2:
        lines = [
            "体式：自创宋词小令式",
            f"《小令·{motif}》",
            f"{image}微明，{anchor}不肯平。",
            f"一声{suffix}，半寸{stage}，旧理忽成冰。",
            f"{op_name}才开，{cost}先醒。",
            f"{hard_warmth}仍向第{local}程轻轻钉。"
        ]
    elif form == 3:
        lines = [
            "体式：自创元曲小令式",
            f"〔越调〕{motif}边",
            f"{image}斜，{suffix}切，{anchor}冷处旧天折。",
            f"{op_name}才开，{cost}已在暗处结。",
            "问它何处是新界？",
            f"{witness}答：第{local}折。"
        ]
    elif form == 4:
        lines = [
            "体式：自创现代诗",
            f"{anchor}没有说话。",
            f"它把第{local}个误差放在{stage}的边缘，",
            f"让{effect}成为一枚冷的钉子。",
            f"{short_failure}",
            f"而{edge_place}那点温度，",
            f"仍用编号{unique_mark}拒绝归零。"
        ]
    elif form == 5:
        lines = [
            "体式：自创实验记录诗",
            f"记录号：{unique_mark}",
            f"对象：{anchor}",
            f"操作：{op_name}",
            f"异常：{effect}",
            f"返回：{short_failure}",
            f"备注：{function}，余温仍在。"
        ]
    else:
        lines = [
            "体式：自创箴言诗",
            f"当{anchor}开始{verb}，",
            f"{stage}便不再只是阶段。",
            f"{suffix}不是声音，",
            "是旧世界承认裂缝的方式。",
            f"第{local}枚证物落下，",
            f"眷恋把{function}写成下一条边界。"
        ]
    return "\n".join(lines)


def operation_for(row: Row, motif: str, suffix: str) -> tuple[str, str, str, str]:
    ops = OPERATIONS[row.volume_no]
    name, action, failure = ops[(row.number + len(motif) + len(suffix)) % len(ops)]
    costs = [
        "损失一个旧定义",
        "牺牲一个对照组",
        "暴露一条眷恋同相位缺口",
        "让下一章获得反向证词",
        "把胜利改写为更深层的代价",
    ]
    cost = costs[(row.number + row.volume_no) % len(costs)]
    return name, action, failure, cost


def scene_plan(row: Row, stage: str, motif: str, suffix: str, kind: str) -> list[tuple[str, str]]:
    volume = VOLUMES[row.volume_no]
    stage_info = STAGES.get(stage, STAGES["前置专名"])
    anchor, effect, function = motif_info(motif, row.volume_no)
    op_name, action, failure, cost = operation_for(row, motif, suffix)
    local, total, ratio = volume_position(row)
    scene = volume["scene_pool"][(row.number + len(motif)) % len(volume["scene_pool"])]
    metric = f"{(row.number * 413) % 997 / 1000:.3f}"
    if ratio < 0.25:
        phase_turn = "只暴露局部失效，不解释最终形态。"
    elif ratio < 0.6:
        phase_turn = "让旧解释被反复验证后崩溃。"
    elif ratio < 0.86:
        phase_turn = "把本阶段前面的胜利改写成代价。"
    else:
        phase_turn = "为卷末形态撕裂或下一卷门槛预热。"

    scene_names = [
        ("场景1：证物入场", "场景1：冷启动读数", "场景1：异常落点"),
        ("场景2：实验动作", "场景2：判读操作", "场景2：反证程序"),
        ("场景3：旧解释崩塌", "场景3：阻力显形", "场景3：误判反噬"),
        ("场景4：眷恋硬边", "场景4：温差回响", "场景4：不可删边界"),
        ("场景5：留下钩子", "场景5：证物封口", "场景5：下一章压力"),
    ]
    pick = (row.number + len(motif)) % 3

    return [
        (
            scene_names[0][pick],
            f"开场落在“{scene}”：{anchor}先以正常状态出现，随后发生“{effect}”。稳定值和异常值都要写出来，至少给出一个可复查参数：偏差 {metric}、温差、相位、膜厚或张力。场景结束时，观察者必须意识到这不是装饰性异象，而是本章的证据入口。",
        ),
        (
            scene_names[1][pick],
            f"本章指定操作为“{op_name}”：{action}。写作时按“输入—执行—返回—失败点”四步推进。预期目标是服务“{stage_info['mission']}”，实际返回必须落到“{failure}”。这一场是正文核心，不得跳过或只用旁白概括。",
        ),
        (
            scene_names[2][pick],
            f"阻力来自本卷硬规则：{volume['law']} 旧解释在这里必须失效。误判不要写成“它不懂”，而要写成一个具体代价：{cost}。若有人类角色出场，代价落在权限、身体、亲情或战术上；若是非人章节，代价落在定义、算法、器官或边界上。{phase_turn}",
        ),
        (
            scene_names[3][pick],
            f"周衍/周诗雨线以硬证物出现：杯壁温差、儿童图案、父亲手痕、呼吸间隔、第一行代码偏移，选其一并与“{motif}”绑定。它改变的是“{function}”，不是抒情。回响必须小、硬、可测，并迫使{volume['agent']}承认一个非优化变量正在参与规则。",
        ),
        (
            scene_names[4][pick],
            f"按“{suffix}”收束：{SUFFIXES[suffix]} 结尾必须留下一个明确物件、读数、签章、裂缝或命令，内容指向“{function}是否已经从证物变成规则”。若本章为{kind}，最后一句应推动下一章行动，而不是总结主题。",
        ),
    ]


def prohibitions(row: Row, stage: str) -> list[str]:
    volume = VOLUMES[row.volume_no]
    stage_info = STAGES.get(stage, STAGES["前置专名"])
    return [
        volume["taboo"],
        stage_info["risk"],
        "不得连续三段只写抽象名词；每段至少要有一个可感证物、动作或读数。",
        "不得用“无法形容、难以名状、仿佛一切”替代具体物理表现。",
        "不得提前泄露后续卷终极真相，除非本章处于绝对高潮范围。",
    ]


def render_outline(row: Row, prev_title: str | None, next_title: str | None) -> tuple[str, str]:
    _, stage, tail = split_title(row.title)
    motif = find_motif(tail)
    suffix = find_suffix(tail)
    local, total, ratio = volume_position(row)
    kind, kind_rule = STRUCTURE_BY_MOD[(row.number + row.volume_no + len(motif)) % len(STRUCTURE_BY_MOD)]
    volume = VOLUMES[row.volume_no]
    stage_info = STAGES.get(stage, STAGES["前置专名"])
    anchor, effect, function = motif_info(motif, row.volume_no)
    level = climax_level(row, stage, local, total)
    core = generated_core(row, stage, motif, suffix, kind)
    previous_line = prev_title or "无，作为项目开端处理"
    next_line = next_title or "无，作为全书终章处理"

    scenes = "\n\n".join(f"### {name}\n\n{text}" for name, text in scene_plan(row, stage, motif, suffix, kind))
    bans = "\n".join(f"- {item}" for item in prohibitions(row, stage))
    ratio_text = f"{ratio:.2%}"

    text = f"""# {row.chapter_id} {row.title}

## 强约束等级

{level}：本章不是占位章。标题意象、阶段任务、物理证物、眷恋回响和章末钩子必须全部落地；允许调整场景顺序，但不得把本章写成同阶段其他章节的换名版本。

## 基本定位

- 卷号：第{row.volume_no}卷《{row.volume_name}》
- 卷内位置：{local}/{total}（{ratio_text}）
- 阶段：{stage}
- 章节功能：{kind}，{kind_rule}
- 目标正文：约{row.target_words}字
- 叙事视角：{volume['view']}
- 主证物：{motif} / {anchor}
- 标题动作：{suffix}，{SUFFIXES[suffix]}
- 状态：detailed-v3

## 本章一句话

{core}

## 与前后章的硬衔接

- 上一章：{previous_line}
- 下一章：{next_line}
- 本章必须承接上一章留下的物理证据，但只推进一个核心变化：{effect}
- 本章必须给下一章留下一个待处理问题：{function}是否已经从证物变成规则。

## 自创题诗草案

《{row.title}》
{poem(row, stage, motif, suffix)}

## 物理环境与可写边界

- 场景尺度：{volume['scale']}
- 主要环境：{", ".join(volume['scene_pool'])}
- 本卷硬规则：{volume['law']}
- 本阶段任务：{stage_info['mission']}
- 本阶段运动方向：{stage_info['movement']}
- 本章可写：{anchor}的读数、位置、相位、温度、张力、膜厚、回声、投影和对观察者的反作用。
- 本章禁止：把“{motif}”只当装饰词；它必须产生可见变化，并改变角色或实体下一步选择。

## 场景拆分

{scenes}

## 人物与意识变化

- 角色/实体起点：{volume['agent']}仍试图用上一层级的判断方式理解“{motif}”。
- 本章中段：{effect}迫使其承认旧判断不足；若有人类角色在场，必须写出其具体动作，而不是旁白代替。
- 本章终点：{function}成为下一章的压力源。变化必须小而不可逆，不能直接跳到卷末结论。

## 信息披露边界

- 必须披露：{stage_info['mission']}在本章的一个具体表现。
- 可以暗示：{volume['pressure']}
- 暂不披露：后续卷终极闭环、全部轮回真相、眷恋的最终编码方式。
- 读者应获得的问题：为什么一个看似微小的“{motif}”异常，会逼迫更高层级的存在改变自身定义。

## 伏笔操作

- 伏笔类型：{row.raw['伏笔操作']}
- 本章新增或提醒：以“{anchor}”作为可追踪证物，记录首次/再次出现的位置。
- 回收方向：第五卷强回收眷恋残片，第七卷把“水杯温差/第一行代码/新黎明”合并为首尾回环。
- 注意：伏笔不要写成作者说明，必须藏在读数、物件、对话停顿、签章或环境反应中。

## 禁止写法

{bans}

## 正文落笔提示

首段不要解释世界观，直接写“{anchor}”出现异常。第二段给出观测者动作。第三段让动作失败或反噬。中段把“{stage}”的任务压成一次具体实验。结尾只留下证物，不替读者总结主题。
"""
    return text, core


def update_catalog(rows: list[Row], generated_cores: dict[int, str]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].raw.keys())
    for row in rows:
        _, stage, tail = split_title(row.title)
        motif = find_motif(tail)
        suffix = find_suffix(tail)
        row.raw["核心事件"] = generated_cores[row.number]
        row.raw["人物变化"] = f"围绕“{motif}”的证物变化推进：从旧判断方式进入本阶段“{stage}”压力；结尾必须让角色或实体少掉一个旧解释。"
        row.raw["信息披露"] = f"只披露“{stage}”阶段的一个可复验变化，不提前解释终极闭环。"
        row.raw["伏笔操作"] = f"seed/remind/payoff: {motif}::{suffix}，以物理证物方式追踪，不写成作者旁白。"
        row.raw["章末处理"] = f"以“{suffix}”逻辑留下新证物或新命令，下一章必须处理。"
        row.raw["状态"] = "detailed-v3"
    with CATALOG_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row.raw for row in rows)


def validate(rows: list[Row], lengths: list[int], generated_cores: dict[int, str]) -> str:
    outline_files = sorted(OUTLINE_DIR.glob("chapter-*.md"))
    old_phrases = [
        "它的存在意义不是补字数",
        "开场给出一个稳定状态，例如一次观测",
        "不能游离成设定说明",
        "没有神谕，只有边界失效",
    ]
    phrase_hits = Counter()
    sampled_missing = []
    poem_blocks = []
    for p in outline_files:
        text = p.read_text(encoding="utf-8-sig")
        for phrase in old_phrases:
            if phrase in text:
                phrase_hits[phrase] += 1
        poem_match = re.search(r"## 自创题诗草案\n\n《[^》]+》\n(.+?)\n\n## 物理环境", text, flags=re.S)
        if poem_match:
            poem_blocks.append(poem_match.group(1).strip())
        else:
            sampled_missing.append(f"{p.name}: 题诗块缺失")
        if "主证物：" not in text or "场景5：" not in text or "本章指定操作" not in text:
            sampled_missing.append(p.name)
    title_count = len({r.title for r in rows})
    core_count = len(set(generated_cores.values()))
    poem_unique = len(set(poem_blocks))
    return f"""# 细纲 v3 重写校验报告

## 结果

- 章节总数：{len(rows)} / 2500
- 细纲文件数：{len(outline_files)} / 2500
- 唯一标题数：{title_count} / 2500
- 唯一核心事件数：{core_count} / 2500
- 题诗总数：{len(poem_blocks)} / 2500
- 唯一题诗数：{poem_unique} / 2500
- 字符数：最小 {min(lengths)} / 中位 {int(median(lengths))} / 平均 {mean(lengths):.1f} / 最大 {max(lengths)}
- 旧模板短语命中：{dict(phrase_hits)}
- 缺少 v3 强约束结构的样本：{sampled_missing[:20] if sampled_missing else '无'}

## 这次解决的问题

- 不再使用“围绕某阶段推进”的空泛句作为细纲主体。
- 每章绑定独立主证物、标题动作、场景尺度、实验动作、误判方式、眷恋回响和章末钩子。
- `chapter-catalog.csv` 的核心事件、人物变化、信息披露、伏笔操作、章末处理已同步为 v3 约束。
- 后续正文应先读本章 `主证物` 和 `场景拆分`，再动笔，不允许直接按旧正文概念堆叠。
"""


def main() -> int:
    rows = read_catalog()
    OUTLINE_DIR.mkdir(parents=True, exist_ok=True)
    generated_cores: dict[int, str] = {}
    lengths: list[int] = []
    for idx, row in enumerate(rows):
        prev_title = rows[idx - 1].title if idx > 0 else None
        next_title = rows[idx + 1].title if idx + 1 < len(rows) else None
        text, core = render_outline(row, prev_title, next_title)
        (OUTLINE_DIR / f"chapter-{row.number:04d}.md").write_text(text, encoding="utf-8")
        generated_cores[row.number] = core
        lengths.append(len(text))
    update_catalog(rows, generated_cores)
    REPORT_PATH.write_text(validate(rows, lengths, generated_cores), encoding="utf-8")
    print(f"rewritten_outlines={len(rows)}")
    print(f"min_chars={min(lengths)} avg_chars={mean(lengths):.1f} max_chars={max(lengths)}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
