# InkOS 融合规则

## 什么时候调用 InkOS

优先使用 `skills/inkos-bridge` 的情况：

- 用户要求自动批量写多章、连续生产章节或全流程“写、审、改”。
- 用户要导入已有长篇，让系统反推设定、角色、风格后续写。
- 用户要生成完整短篇包、简介卖点、封面提示词或可选封面图。
- 用户要做 AI 味检测、自动审稿、风格分析、题材趋势或 Studio/TUI 工作台。
- 用户明确提到 InkOS、Studio、TUI、truth files、hook ledger 或 33 维审稿。

## 什么时候不用 InkOS

继续使用本项目原生小说 skills：

- 单段润色、局部改写、只看语言质感。
- 单章人工把控写作，用户希望逐段确认。
- 文学向、现实向、短篇余味型文本，不需要批量自动化。
- 已有本项目 `docs/YYYY-MM-DD/小说/<书名>/` 真相源非常完整，只需要续写或同步。

## 融合模式步骤

1. 用 InkOS 快速生成草稿、审稿结果或短篇包。
2. 导出 Markdown，不直接提交 `.inkos-runtime/`。
3. 按本项目目录放入 `docs/YYYY-MM-DD/小说/<中文书名>/`。
4. 用 `novel-review` 做中文小说目标复审。
5. 通过后用 `novel-update` 写入本项目 canon、人物、伏笔和记忆快照。

## 冲突优先级

当前对话要求 > 本项目 `project.md` > 本项目 `outline.md` / `project-state.md` > InkOS truth files > InkOS 题材规则。

InkOS 生成的状态只能作为候选材料，不能静默覆盖本项目已有真相源。
