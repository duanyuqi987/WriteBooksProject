# 中文小说写作台（Novel Writing Workbench）

一个用于 AI 辅助中文小说创作的技能系统。它面向通用中文小说，而不是只服务网文或某一种题材；可以支持短篇、中篇、长篇、连载、类型小说和文学向小说。

## 核心定位

- 只处理小说创作：构思、大纲、正文、审查、修订、记忆管理。
- 默认使用简体中文进行自然表达。
- 默认小说作者署名为：段锦佑。
- 起小说名时优先通俗易懂、有画面、有阅读欲，让读者一眼知道故事入口并愿意点开。
- 先判断作品目标，再选择流程强度。
- 长篇项目使用文件系统保存设定、角色、伏笔和进度。
- 短篇、片段、局部润色不强制套完整长篇流程。

## 工作流程

```text
目标澄清
  ↓
项目底座 project.md
  ↓
分层大纲 outline.md
  ↓
逐章或逐场景起草
  ↓
审查与修订
  ↓
记忆更新
```

## 流程强度

| 模式 | 适用场景 |
|---|---|
| 轻量一次性 | 单个灵感、短篇片段、局部润色 |
| 标准项目 | 有明确书名、设定和持续写作需求 |
| 长篇连续 | 多章、多卷、跨会话写作 |

## 主要 skill

| Skill | 用途 |
|---|---|
| `novel-writing-workbench` | 总入口 |
| `novel-writing` | 状态判断和路由总控 |
| `novel-brainstorm` | 新小说构思和项目底座 |
| `novel-outline` | 短篇结构、中篇章节路线、长篇卷纲 |
| `novel-draft` | 正文起草、续写、改写 |
| `novel-review` | 审稿、去 AI 味、一致性检查 |
| `novel-update` | canon、角色、伏笔、记忆、进度同步 |
| `novel-whisper` | 语音转写为写作素材 |

## 目录结构

```text
WriteBooksProject/
├── SKILL.md
├── agents/openai.yaml
├── skills/
│   ├── novel-writing/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── styles/
│   │   │   ├── 通用中文小说.md
│   │   │   ├── 冷白描.md
│   │   │   ├── 怪诞悬疑.md
│   │   │   └── 系统爽文.md
│   │   └── templates/
│   ├── novel-brainstorm/
│   ├── novel-outline/
│   ├── novel-draft/
│   ├── novel-review/
│   └── novel-update/
├── references/
├── scripts/
└── docs/
```

## 项目文件约定

长篇或持续项目默认使用：

```text
docs/YYYY-MM-DD/小说/<中文书名>/
├─ project.md
├─ outline.md
├─ project-state.md
├─ memory-snapshot.md
├─ 人物/<角色名>.md
├─ 伏笔/foreshadow-xxx.md
├─ 章节/chapter-xxx.md
└─ 正文/chapter-xxx.md
```

## 使用示例

```text
用 $novel-writing-workbench 帮我构思一篇 2 万字的现实题材中篇小说。
```

```text
用 $novel-writing-workbench 继续写当前小说的下一章。
```

```text
用 $novel-writing-workbench 审查 chapter-003，重点看人物动机和语言是否自然。
```

```text
用 $novel-writing-workbench 把这段改得更像自然中文小说，不要网文腔。
```

## 内置风格

- **通用中文小说**：自然、清晰、有场景感，未指定文风时默认使用。
- **冷白描**：克制、现实、少解释，适合现实主义、历史、乡土、战争等。
- **怪诞悬疑**：信息控制、认知不安、线索与反转。
- **系统爽文**：强连载、爽点、升级、反转回报。作为可选风格，不再是默认路线。

## 环境要求

- Git
- Python 3.x（脚本仅使用标准库）
- FFmpeg（可选，语音转写时使用）

## 许可

MIT License，详见 [LICENSE](LICENSE)。
