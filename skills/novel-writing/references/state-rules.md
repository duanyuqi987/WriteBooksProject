# 小说状态机规则

## 状态定义（6 个）

| status | 含义 | 文件证据 |
|--------|------|---------|
| `idea` | 有初步概念，未开工 | `project.md` 不存在，或 outline 中无章节 |
| `planned` | 当前卷章节已规划 | `outline.md` 中当前卷有章节列表，status=planned |
| `drafting` | 当前章正在写 | `章节/chapter-xxx.md` frontmatter.status=drafting |
| `reviewing` | 草稿完成，等待审查 | `章节/chapter-xxx.md` frontmatter.status=reviewing |
| `done` | 审查通过，记忆已写入 | `章节/chapter-xxx.md` frontmatter.status=done |
| `blocked` | 需要人工干预 | `project-state.md` 中 `blocked_reason` 非空 |

## 状态流转

```
idea → planned → drafting → reviewing → done
                      ↑           ↓
                      └── 小修/重写 ──→ blocked（方向错误）
```

### 正常流程

1. **idea → planned**：novel-brainstorm 完成 project.md → novel-outline 完成分层大纲
2. **planned → drafting**：novel-draft 开始写当前章
3. **drafting → reviewing**：novel-draft 完成三层写作
4. **reviewing → done**：novel-review 五层审查判定通过
5. **done → next**：novel-update 执行 6 项同步 → 路由到下一章或下一卷

### 异常流程

- **reviewing → drafting**：小修（1-3 处，改 1 轮）或重写（核心问题，改 1 次）
- **reviewing → blocked**：reject（方向错误，回退到 novel-outline）
- **任何状态 → blocked**：canon 冲突或用户暂停

## 冲突解决优先级

frontmatter > outline > project-state.md

| 数据 | 真相源 | 说明 |
|------|--------|------|
| 章节执行状态 | 章节 frontmatter | 以 `章节/chapter-xxx.md` frontmatter 为准 |
| 结构顺序 | outline.md | 以 outline.md 章节列表为准 |
| 项目设定 | project.md | 最新 canon 以 project.md + 变更日志为准 |
| 调度快照 | project-state.md | 仅调度快照，不是真相源 |
| 伏笔状态 | 伏笔/foreshadow-xxx.md | 每条伏笔独立文件为真相源 |
| 角色状态 | 人物/<角色>.md | 角色卡变更记录为真相源 |
| 记忆快照 | memory-snapshot.md | 最近章节摘要，用于快速恢复 |

## 当前章选择规则

1. 优先选 status=reviewing（中断恢复）
2. 其次选 status=drafting（中断恢复）
3. 其次选 status=planned（正常推进，选最早）
4. 当前卷全部 done → 触发卷完成 → 路由到 novel-outline 规划下一卷

## 不跳章规则

- 不能在有 planned 章节时去写后面的章节
- 章节必须按 outline.md 顺序依次推进
- 唯一例外：review 判定为 reject 时可回到当前章重新规划

## 记忆检查规则

每次状态变更时必须检查：
1. memory-snapshot.md 是否与当前进度一致？
2. 伏笔/ 中的未兑现伏笔是否与 outline 保持同步？
3. 人物/ 中的角色状态是否反映了最新完成的章节？
