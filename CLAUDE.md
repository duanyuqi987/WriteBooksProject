# 小说写作台

本仓库专用于 AI 辅助写小说。纯小说系统，不写技术书、报告、教程。

全局行为规则见 `~/.claude/CLAUDE.md`，本文件仅含项目级约束。

## 核心规则

### 1. docs/ 全部上传，敏感信息绝对不上传

| 策略 | 内容 |
|------|------|
| ✅ 上传 | `docs/` 全部（MD、HTML 等） |
| ✅ 上传 | `skills/`、`references/`、`scripts/`、`assets/` |
| ❌ 不上传 | `.env`、`*.key`、`*.pem`、`*.secret`、`credentials.*` |
| ❌ 不上传 | `.claude/`、`.superpowers/` |
| ❌ 不上传 | `node_modules/`、`__pycache__/`、`.DS_Store`、`*.tmp` |

### 2. 每轮写作完成后必须 Git 提交

写完一章、完成审查、更新记忆后，**必须执行**：

```bash
git status --short && git diff --stat
git add docs/
git commit -m "docs: <中文简述本轮改动>"
git status
```

详细流程见 `skills/auto-commit-books/SKILL.md`。

### 3. 小说写作工序

```
用户输入（含目标字数）
  → 字数评估（计算卷数、章数）
  → 头脑风暴（15维度渐进收束）
  → 大纲规划（四层展开：字数→卷→粗略章→精细章）
  → 正文起草（三层写作：粗写→细写→技法注入）
  → 六层审查（读者视角 + 禁用词 + Canon + 技法 + 升级感 + 声纹）
  → 记忆写入（6项同步：canon + 角色 + 伏笔 + 快照 + 大纲 + 调度）
  → Git 提交
```

### 4. 目录约定

```
docs/YYYY-MM-DD/小说/<书名 slug>/
├─ project.md              # 项目底座（设定、角色列表、风格、技法偏好）
├─ outline.md              # 大纲（四层展开、章节状态追踪）
├─ project-state.md        # 调度快照
├─ memory-snapshot.md      # 记忆快照（最近 5 章摘要）
├─ 人物/<角色名>.md        # 角色卡（含弧光追踪）
├─ 伏笔/foreshadow-xxx.md  # 伏笔追踪（独立管理）
├─ 章节/chapter-xxx.md     # 章节工作文件（目标+正文+技法+审查）
└─ <书名 slug>/第X卷/      # 纯正文目录
```

### 5. 双轨输出（可选）

每章写完可生成 `.html` 阅读版（通过 `skills/html-md-sync/`）。非必须，除非用户要求。

### 6. 写作技法

系统内置 10 种经典写作技法（源自《红楼梦》等经典小说分析）：
不写之写 / 一击两鸣 / 草蛇灰线 / 春秋笔法 / 白描 / 层峦迭翠 / 反衬法 / 避繁文法 / 繁章波折法 / 暗透法。

详见 `skills/novel-writing/references/writing-techniques.md`。

### 7. Git 提交规范

- 消息语言：中文
- 格式：Conventional Commits（`docs:`/`feat:`/`fix:`/`chore:`）
- 分步提交：书稿内容 → 技能/配置，每次聚焦一类
- 绝不 force push 到 main/master
- 绝不提交敏感文件

## 当前在写小说

| 书名 | 路径 | 状态 |
|------|------|------|
| （暂无进行中的小说） | - | - |
