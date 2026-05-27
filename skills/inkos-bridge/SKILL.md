---
name: inkos-bridge
description: |
  Use when the user wants InkOS acceleration inside this Chinese novel project: automated multi-chapter writing, write-audit-revise loops, importing existing novels and continuing, standalone short fiction packages, style analysis, AI-tell detection, cover prompts, Studio/TUI, or explicit InkOS CLI usage. Keep ordinary one-off Chinese prose polishing on the local novel skills instead.
---

# InkOS 加速桥

本 skill 把内嵌的 InkOS 作为工具层接入当前中文小说写作台。日常创作仍以本项目 `novel-writing` 系列为主；只有自动化、批量化或 InkOS 专属能力明显有价值时才启用。

## 启动检查

1. 读取 `skills/novel-writing/references/inkos-integration.md`。
2. 读取 `references/inkos/workflows.md`，需要状态或审稿细节时再读 `references/inkos/state-and-audit.md`。
3. 如涉及题材规则，读取 `references/inkos/genre-map.md` 和对应 `references/inkos/genres/*.md`。
4. 确认 `vendor/inkos/package.json`、`vendor/inkos/LICENSE`、`vendor/inkos/skills/SKILL.md` 存在。

## 命令入口

从项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\inkos_bootstrap.ps1
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 --help
```

`scripts/inkos.ps1` 会把运行目录切到 `.inkos-runtime/`。不要把 `.inkos-runtime/` 里的 API key、运行书库、封面图、短篇输出直接提交。

## 路由

| 用户目标 | 默认做法 |
|---|---|
| 自动批量写多章 | 用 `inkos write next`，完成后导出 Markdown，再回到本项目审稿 |
| 导入已有长篇续写 | 用 `inkos import chapters` 反推状态，再生成续写草稿 |
| 完整短篇包 | 用 `inkos short run` 生成正文、卖点、封面提示词 |
| 风格仿写 | 用 `inkos style analyze/import`，再用本项目 `novel-review` 控制中文质感 |
| AI 味检测或工具化审稿 | 用 `inkos audit` / `detect`，结论映射到 `novel-review` 判定 |
| 只润色一段 | 不启用 InkOS，转 `novel-review` 或 `novel-draft` |

## 归档

InkOS 产物进入本项目时，必须按这个顺序：

1. 从 InkOS 导出 Markdown 或复制明确的正文片段。
2. 放入 `docs/YYYY-MM-DD/小说/<中文书名>/`。
3. 用 `novel-review` 做项目目标复审。
4. 通过后用 `novel-update` 更新 canon、人物、伏笔、记忆和进度。

## 红线

- 不让 InkOS truth files 静默覆盖本项目 `project.md`、`outline.md`、`memory-snapshot.md`、`人物/`、`伏笔/`。
- 不为单段润色、单个标题、少量审稿强行启动完整 InkOS。
- 不提交 `.inkos-runtime/` 中的密钥、运行状态、生成封面、短篇临时包或模型缓存。
- 不把 InkOS 的网文题材规则套到所有中文小说。
