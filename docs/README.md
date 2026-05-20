# docs 目录规范

## 小说写作目录

小说写作产物按日期和书名归档：

```text
docs/
  YYYY-MM-DD/
    小说/
      <书名 slug>/
        ├─ project.md              # 项目底座
        ├─ outline.md              # 大纲
        ├─ project-state.md        # 调度快照
        ├─ memory-snapshot.md      # 记忆快照
        ├─ 人物/<角色名>.md        # 角色卡
        ├─ 伏笔/foreshadow-xxx.md  # 伏笔追踪
        └─ 章节/chapter-xxx.md     # 章节文件
```

## 原始学习书目录（Legacy）

以下目录结构属于原 `project-to-learning-doc` 系统，保留作历史参考：

```text
docs/
  YYYY-MM-DD/
    学习书/
    迭代记录/
    来源缓存/
    构建脚本/
    质量检查/
```

| 目录 | 说明 |
|---|---|
| `学习书/` | 学习书 HTML 产出门 |
| `迭代记录/` | 当天修改记录、验证记录 |
| `来源缓存/` | 网站页面缓存、来源副本 |
| `构建脚本/` | 一次性构建脚本 |
| `质量检查/` | 字数统计、结构检查结果 |

新项目使用"小说/"目录，旧产物不强制迁移。
