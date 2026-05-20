# 小说项目文件契约

本文件定义持续写作项目的文件边界。短篇或一次性片段可以不完整创建这些文件，但长篇、连载和跨会话项目必须遵守。

## 文件清单

| 文件 | 所有者 | 职责 |
|---|---|---|
| `project.md` | novel-brainstorm 初始化，novel-update 追加 canon | 项目底座、主题、风格、边界、设定事实 |
| `人物/[角色名].md` | novel-brainstorm 创建，novel-update 追加变化 | 角色欲望、矛盾、关系、声纹、变更记录 |
| `outline.md` | novel-outline 创建，novel-update 更新状态 | 结构、章节路线、滚动规划 |
| `章节/chapter-xxx.md` | novel-draft 创建，novel-review 填审查结果 | 章节目标、正文、修改意见、定稿摘要 |
| `正文/chapter-xxx.md` | novel-draft 创建，novel-review 定稿 | 纯正文 |
| `project-state.md` | novel-writing / novel-update | 调度快照：当前章、下一步、阻塞点 |
| `memory-snapshot.md` | novel-update | 最近章节摘要和累计记忆 |
| `伏笔/foreshadow-xxx.md` | novel-outline / novel-update | 伏笔状态：埋入、提示、兑现、放弃 |

## project.md 必填字段

```markdown
# [书名或暂定名]

## 作品形态
- 篇幅类型：
- 目标字数：
- 创作取向：
- 目标读者或阅读场景：

## 核心 Premise
> 谁 + 在什么处境 + 必须做什么 + 否则会怎样

## 主题与核心问题
## 读者体验
## 主要角色与关系
## 世界、时代与硬规则
## 核心冲突
## 叙事策略
## 写作风格
## 技法偏好
## 伏线与悬念
## 待定问题
## 变更日志
```

## outline.md 必填字段

| 字段 | 约束 |
|---|---|
| 结构模型 | 说明短篇/中篇/长篇/连载采用什么结构 |
| 全书或全文主线 | 2-3 句话 |
| 人物弧线 | 起点、关键变化、终点 |
| 结构规划 | 阶段/幕/卷目标 |
| 当前推进区间 | 章节或场景路线 |
| 状态 | planned / drafting / reviewing / done / blocked |
| 后续方向 | 只写方向种子，不伪造细节 |

## 章节 frontmatter

```yaml
---
id: chapter-001
volume: 1
status: drafting
review_round: 0
word_count_target: 2500
word_count_actual: 0
canon_changed: false
updated_at: 2026-05-20
---
```

## 章节文件必填 section

- 本章目标
- 正文
- 自检记录
- 修改意见
- 定稿摘要

## 状态冲突处理

frontmatter > outline.md > project-state.md。

如果三者冲突，先以章节 frontmatter 为准，再修正 `outline.md` 和 `project-state.md`。
