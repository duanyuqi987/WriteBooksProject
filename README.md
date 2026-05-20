# 小说写作台（Novel Writing Workbench）

专门用于 AI 辅助写小说的技能系统。纯小说，不写技术书、不写报告、不写教程。

## 核心设计

### 写作流程
- **字数驱动**：所有规划以目标字数为起点反向推导（字数 → 卷数 → 章数 → 每章字数）
- **15 维度头脑风暴**：含第一性原理挑战、读者体验规格、竞争性情节
- **四层大纲**：字数 → 卷结构 → 粗略章 → 精细章，滚动展开
- **三层写作**：粗写骨架 → 细写填充 → 技法注入
- **六层审查**：读者视角 + 三遍校对（内容/6类AI检测/细节）+ Canon + 技法 + 升级感 + 声纹

### 核心系统

| 系统 | 来源 | 核心功能 |
|------|------|---------|
| 角色工坊 | persona-forge | 身份张力公式（前世×当下×矛盾）、底线规则、浓度控制 |
| 声纹系统 | brand-voice | 角色声纹 + 叙事者声纹 + 差异化对比 + 声纹演变 |
| 三遍校对 | huashu-proofreading | 6 大类 AI 腔检测（套话/AI句式/正式词汇/机械结构/中立态度/缺乏细节） |
| 双盲审查 | Santa Method | 双独立审查者 + 裁决门 + 收敛循环（最多3轮） |
| 体验规格 | iPhone 团队 | 人的时刻 → 核心感受 → 技术约束 → 反模式 |
| 任务管理 | task-harness | JSON 真相源 + 增量式进度 + 5 秒上下文恢复 |
| 10 种技法 | 红楼梦分析 | 写作技法库 + 场景映射表 + 技法自查 |
| 记忆系统 | 融合设计 | 7 层文件记忆 + project-state 调度快照 + progress 叙事日志 |
| Skill查找 | 自主设计 | prompt → 技法匹配 → 第三方技能推荐 → 风格路由 |
| 类型技法映射 | 起点分析 | 8种类型 × 核心技法组合 × 爽点/悬念/情绪策略 |
| 起点分析器 | 爬虫脚本 | 获取 Top100 热门小说，分析技法趋势 |
| Whisper语音转写 | OpenAI Whisper | 本地语音转文字，音频不出本机，写作素材采集 |
| 小说数据集 | HuggingFace/Mirror | 下载中文网文数据集用作写作参考 |

## 10 种写作技法

系统内置源自《红楼梦》等经典小说的 10 种写作技法：

| 技法 | 核心思想 |
|------|---------|
| 不写之写 | 关键处故意留白，比写出更有力 |
| 一击两鸣 | 一个场景同时推进多条线索 |
| 草蛇灰线 | 提前埋伏笔，似断非断，后文兑现 |
| 春秋笔法 | 用中立叙述传达含而不露的评判 |
| 白描 | 用具体动作和细节代替抽象形容 |
| 层峦迭翠 | 相似情境产生对照和互文 |
| 反衬法 | 表面写东实际写西，似贬实褒 |
| 避繁文法 | 重复内容用侧面交代代替详写 |
| 繁章波折法 | 短小场景内制造多重转折 |
| 暗透法 | 让他人说出角色心里话 |

## 文件结构

```
WriteBooksProject/
├── SKILL.md                              # 总入口（纯小说路由）
├── README.md                             # 本文件
├── CLAUDE.md                             # 项目级行为约束
├── LICENSE                               # MIT 许可证
├── 使用说明.md                            # 用户使用指南
├── agents/
│   └── openai.yaml                       # Agent 元数据配置
├── skills/
│   ├── novel-writing/                    # 写作总控 + 模板 + 参考
│   │   ├── SKILL.md                      # 状态机 + 记忆加载 + 路由
│   │   ├── references/                   # 16 个参考文件
│   │   │   ├── writing-techniques.md     # 10 种技法详解 + 场景映射表
│   │   │   ├── memory-system.md          # 7 层记忆系统设计
│   │   │   ├── ai-flavor-banlist.md      # 去 AI 味禁用词
│   │   │   ├── character-creation.md     # 角色工坊：身份张力公式
│   │   │   ├── dual-review-system.md     # 双盲审查系统
│   │   │   ├── voice-profile.md          # 声纹档案系统
│   │   │   ├── chapter-rhythm.md         # 章节节奏规则
│   │   │   ├── canon-and-brief.md        # Canon 底座
│   │   │   ├── genre-technique-mapping.md # 8种类型×技法组合
│   │   │   ├── reader-experience-spec.md  # 读者体验规格
│   │   │   ├── skill-catalog.md          # 第三方技能完整清单
│   │   │   ├── skill-finder.md           # prompt→技法/技能匹配路由
│   │   │   ├── novel-harness.md          # 任务管理系统
│   │   │   ├── project-files.md          # 文件契约
│   │   │   ├── review-gates.md           # 审查闸门定义
│   │   │   └── state-rules.md            # 状态机规则
│   │   ├── styles/                       # 写作风格预设
│   │   │   ├── 冷白描.md
│   │   │   ├── 系统爽文.md
│   │   │   └── 怪诞悬疑.md
│   │   └── templates/                    # 文件模板
│   │       ├── project.md
│   │       ├── outline.md
│   │       └── 人物卡.md
│   ├── novel-brainstorm/                 # 头脑风暴工序
│   ├── novel-outline/                    # 大纲规划工序
│   ├── novel-draft/                      # 正文起草工序
│   ├── novel-review/                     # 审查工序
│   ├── novel-update/                     # 记忆写入工序
│   ├── novel-whisper/                    # Whisper 语音转文字
│   ├── auto-commit-books/                # 自动 Git 提交
│   └── html-md-sync/                     # MD/HTML 双轨同步（可选）
├── references/                           # 写作规则与方法参考
│   ├── 写书规则/                          # 写书硬约束
│   ├── 写作方法/                          # 写作方法索引
│   └── learning-doc-legacy/              # 原始学习书系统存档
├── scripts/
│   ├── count_text.py                     # 中英文字数统计
│   ├── whisper_transcribe.py             # 语音转文字核心
│   ├── whisper_batch.py                  # 批量语音处理
│   ├── html_to_markdown.py               # HTML → MD 转换
│   ├── markdown_to_html.py               # MD → HTML 渲染
│   ├── check_dual_format.py              # 双格式检查
│   ├── qidian_analyzer.py                # 起点排行榜分析
│   ├── novel_dataset_downloader.py       # 小说数据集下载
│   └── novel-editor/                     # 《银杏辞》编辑脚本存档
└── assets/
    └── templates/
        └── learning-document.html         # HTML 模板
```

## 快速开始

```bash
git clone <repo-url>
cd WriteBooksProject
```

### 开始新小说

```
我要写一本 50 万字的小说，讲的是 XXX
```

### 继续写作

```
继续写小说
```

### 查看进度

```
查看小说进度
```

## 调用示例

```text
用 $novel-writing-workbench 帮我写一本 50 万字的修仙小说。主角是废柴弟子，意外获得上古传承。
先帮我确定世界观和主角设定，再规划第一卷大纲。
```

```text
用 $novel-writing-workbench 继续写小说。
```

```text
用 $novel-writing-workbench 审查 chapter-012，重点检查伏笔一致性和技法使用。
```

```text
用 $novel-writing-workbench 分析当前起点修仙小说的热门趋势。
```

```text
用 $novel-writing-workbench 帮我匹配：现在要写一个情感冲突场景，推荐什么技法和技能？
```

```text
用 $novel-writing-workbench 把 ./录音/ 文件夹批量转成写作素材。用 medium 模型，输出小说素材格式。
```

```text
用 $novel-writing-workbench 下载中文网文小说数据集，用来做写作参考。
```

## 写作风格

系统内置 3 种风格文件，支持按小说类型路由：

- **冷白描** — 克制、冰山原则、情感内敛。适合现实主义、历史、悬疑、战争
- **系统爽文** — 憋屈→反转→爽、打脸升级。适合系统流、升级流、都市逆袭
- **怪诞悬疑** — 规则设计、信息不对称、认知入侵。适合规则怪谈、无限流、克苏鲁

## 环境要求

- Python 3.x（脚本仅使用标准库，无需 pip 安装）
- FFmpeg（可选，Whisper 语音转写用）
- Git（可选，自动提交用）

## 目录约定

```
docs/YYYY-MM-DD/小说/<书名 slug>/
├─ project.md              # 项目底座
├─ outline.md              # 大纲
├─ project-state.md        # 调度快照
├─ memory-snapshot.md      # 记忆快照
├─ 人物/<角色名>.md        # 角色卡
├─ 伏笔/foreshadow-xxx.md  # 伏笔追踪
└─ 章节/chapter-xxx.md     # 章节文件
```

## 许可

MIT License — 详见 [LICENSE](LICENSE)

## 贡献

欢迎贡献新的写作风格、技法或改进现有流程。请通过 Issue 或 PR 提交。
