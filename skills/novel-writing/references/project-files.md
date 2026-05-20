# 小说项目文件契约

## 文件清单

| 文件 | 所有者 | 职责 |
|---|---|---|
| `project.md` | novel-brainstorm（初始化）、novel-update（canon 追加） | 项目设定、风格、世界观 |
| `人物/[角色名].md` | novel-brainstorm（创建）、novel-update（变更记录） | 角色详细信息 |
| `outline.md` | novel-outline | 卷结构和章节路线 |
| `章节/chapter-xxx.md` | novel-draft（草稿）、novel-review（审查） | 章节目标 + 修改意见 + 定稿摘要 |
| `【书名】/第X卷/chapter-xxx.md` | novel-draft（草稿）、novel-review（定稿） | 纯正文 |
| `project-state.md` | novel-writing（调度快照） | 项目状态记录 |

## project.md 必填字段

```markdown
# [中文书名]

## 核心 Premise
> 一句话：谁 + 在什么处境 + 必须做什么 + 否则会怎样
> 开篇策略：XXX

## 主题
## 角色与关系
## 世界观硬规则（至少1条，最多7条）
## 核心冲突（主线冲突 + 升级方向）
## 写作风格（叙事视角、文风要求、节奏偏好、禁止事项）
## 字数规划（全书目标 + 每章目标）
## 变更日志（运行时追加）
```

## outline.md 必填字段

| 字段 | 约束 |
|---|---|
| 全书主线摘要 | 2-3 句话 |
| 卷目标 | 1-2 句话，具体可执行 |
| 任务说明 | 每章恰好一句话 |
| 结构标记 | setup / build / climax / fallout，必填 |
| 状态 | planned / drafting / reviewing / done / blocked |
| 后续方向 | 每卷 1-2 句话种子 |

## 章节文件 frontmatter

```yaml
---
id: chapter-001
volume: 1
status: drafting
review_round: 0
canon_changed: false
source_outline_version: 1
updated_at: 2026-05-16
---
```

## 章节文件必填 section

- 本章目标（从 outline 继承）
- 修改意见（review skill 填写）
- 定稿摘要（review 通过后填写，2-3 句话）

## 修改意见格式

```markdown
**review_status:** pass / minor_fix / rewrite_required / reject
**review_severity:** minor / structural

### 判定依据
### 建议修改
```
