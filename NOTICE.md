# InkOS 融合来源说明

本项目已将 InkOS 作为内嵌写作引擎复制到 `vendor/inkos/`，用于增强中文小说的批量写章、导入续写、审稿、短篇包、题材规则、状态沉淀和可选 Studio/TUI 能力。

## 来源

- 上游仓库：`https://github.com/Narcooo/inkos`
- 本次迁移源：`C:\Users\usv\Downloads\inkos-master\inkos-master`
- 本地内嵌位置：`vendor/inkos/`
- 上游许可：`AGPL-3.0-only`

## 融合边界

- 日常入口仍以本项目 `novel-writing-workbench`、`novel-writing`、`novel-draft`、`novel-review`、`novel-update` 为主。
- InkOS 作为加速层，由 `skills/inkos-bridge/SKILL.md` 和 `scripts/inkos.ps1` 调用。
- InkOS 运行时数据放在 `.inkos-runtime/`，不提交 API key、书籍运行状态、封面图、短篇生成物和模型缓存。
- 原 MIT 许可文本已保留在 `LICENSES/MIT-original.txt`，当前根 `LICENSE` 使用 AGPL-3.0 文本以匹配完整内嵌后的仓库状态。

## 维护原则

- 不直接改写既有小说正文、人物卡、大纲和记忆快照。
- 从 InkOS 生成的内容进入本项目时，先导出为 Markdown，再按 `docs/YYYY-MM-DD/小说/<中文书名>/` 归档。
- 升级 InkOS 时优先替换 `vendor/inkos/`，再检查 `skills/inkos-bridge/` 和 `references/inkos/` 是否需要同步。
