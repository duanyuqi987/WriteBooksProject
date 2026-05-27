# InkOS 状态与审稿参考

## 多阶段写作

InkOS 的核心价值不是“替代作者”，而是把长篇生产拆成可重复的流水线：

1. 规划：确定本章目标、角色、冲突、伏笔操作和长度目标。
2. 组包：从项目记忆、章节摘要、角色状态和题材规则中整理本章上下文。
3. 起草：写正文，并在正文里落实计划中的变化。
4. 结算：把正文已经发生的事实沉淀为状态变化。
5. 审稿：检查连续性、长度、题材规则、AI 味、伏笔和人物行为。
6. 修订：只修复审稿发现的关键问题。

本项目吸收这个流程，但不要求每次单章创作都跑完整工具链。

## Truth files 映射

| InkOS 概念 | 本项目对应 |
|---|---|
| story frame / book rules | `project.md` |
| current focus / author intent | `project-state.md` |
| chapter summaries | `memory-snapshot.md` |
| roles / character matrix | `人物/<角色名>.md` |
| pending hooks / hook ledger | `伏笔/foreshadow-xxx.md` |
| runtime state json | 仅作为工具运行层，不直接替代本项目 Markdown 真相源 |

## Hook ledger 吸收方式

本项目继续使用 `伏笔/` 文件，但在长篇和连载中补充 InkOS 的操作语义：

- `upsert`：新增或更新伏笔。
- `mention`：正文中自然触碰伏笔，但不推进结果。
- `advance`：伏笔进入更紧张、更接近兑现的状态。
- `resolve`：伏笔已经兑现。
- `defer`：本章明确延后，并记录理由。

写正文时，任何 `advance` 或 `resolve` 都必须在正文里有可定位的动作、物件、对话或事件支撑，不能只在备注里结算。

## 审稿维度

InkOS 的 33 维审稿可压缩成以下本项目检查面：

- 连续性：设定、时间线、人物状态、地点和物件是否冲突。
- 章节功能：本章是否完成计划中的变化，而不是只铺垫。
- 人物行为：角色选择是否来自欲望、压力和既有性格。
- 语言质感：是否有 AI 腔、总结腔、解释腔、模板化爽点。
- 题材规则：是否混入不属于本作品的体系、节奏或禁忌。
- 长度治理：是否低于硬下限或膨胀到失控。
- 伏笔健康：是否长期沉默、凭空消失或账本推进但正文没落地。

审稿结论仍使用本项目的 `pass / minor_fix / rewrite_required / reject`。
