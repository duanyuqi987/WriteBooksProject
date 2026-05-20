---
name: novel-writing
description: |
  小说写作总控。负责状态判定、记忆加载、路由调度。
  不代写正文、不造设定、不做审查。
---

# 小说写作总控

把小说请求路由到正确工序，维护状态机和记忆系统。

## HARD-GATE

每次写作前必须执行：

1. **扫描项目文件** → 判定当前状态
2. **加载记忆系统** → 恢复上次进度（新项目跳过）
3. **读取硬约束**：
   - `skills/novel-writing/references/ai-flavor-banlist.md`
   - `skills/novel-writing/references/writing-techniques.md`（技法库）
4. **Skill 查找**（步骤 1.5）→ 根据当前场景匹配技法/技能/风格
   - `skills/novel-writing/references/skill-finder.md`
   - `skills/novel-writing/references/genre-technique-mapping.md`
5. **可选：起点分析** → 运行 `scripts/qidian_analyzer.py` 获取市场参考
6. **可选：小说数据集** → 运行 `scripts/novel_dataset_downloader.py` 获取写作参考素材
7. **路由到工序** → 不允许越权代写

## 状态机

状态以文件为真相源，详见 `references/state-rules.md`。

```
idea → planned → drafting → reviewing → done
                    ↑           ↓
                    └── 小修/重写 ──→ blocked（方向错误）
```

## 路由表

| 状态 | 路由目标 | 说明 |
|------|---------|------|
| idea（无 project.md） | `skills/novel-brainstorm` | 字数驱动头脑风暴 |
| idea（有 project.md，缺 outline） | `skills/novel-outline` | 规划章节 |
| planned | `skills/novel-draft` | 写正文 |
| drafting | `skills/novel-draft` | 继续写 |
| reviewing | `skills/novel-review` | 审查 |
| done | `skills/novel-update` → 下一章/下一卷 | 记忆写入后继续 |
| blocked | 按阻塞原因路由 | 人工干预 |

## 扫描文件清单（每次必做）

1. `project.md` 是否存在
2. `outline.md` 是否存在，当前章节状态
3. `章节/chapter-xxx.md` 的 frontmatter 状态
4. `project-state.md` 的 blocked_reason（如存在）
5. `memory-snapshot.md`（如存在，加载最近 5 章摘要）

冲突解决：frontmatter > outline > project-state.md

## 新项目启动流程

当用户说"我要写一本 X 字的小说，讲的是 Y"时：

1. **先做字数评估**：根据目标字数计算卷数和章数
2. **告知用户规模**："您的 50 万字目标约需 200-250 章，分 3-5 卷，每章约 2000-2500 字。是否确认这个规模？"
3. **用户确认后**：路由到 `skills/novel-brainstorm` 开始头脑风暴
4. **头脑风暴完成后**：用户确认设定后路由到 `skills/novel-outline` 生成分层大纲

## 恢复进度流程

当用户说"继续写"或"继续写小说"时：

1. 读取 `project-state.md` → 确认上次停在哪里
2. 读取 `memory-snapshot.md` → 获取最近章节摘要
3. 向用户汇报："上次写到第 X 卷第 Y 章，累计 Z 字。接下来写 chapter-XXX：[任务说明]。是否继续？"
4. 用户确认后路由到对应工序

## 进度报告格式

```markdown
## <书名> 写作进度

- **项目状态：** [status]
- **当前进度：** 第 X 卷 第 Y 章 / 共 Z 章
- **已完成：** N 章 / 当前卷 M 章
- **累计字数：** XXXX 字 / 目标 YYYY 字（完成度 ZZ%）
- **未兑现伏笔：** N 条
- **下一步：** [即将执行的操作]
```

## 红线

- 不跳章：章节按 outline 顺序依次推进
- 单线程：同时只处理一个章节
- 文件优先：每次必须重新读取，不缓存判断
- 不越权：只裁决和路由，不代写产物
- 纯小说：不接技术书、报告、教程等其他文体
