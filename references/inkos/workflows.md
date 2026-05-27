# InkOS 工作流参考

本文件用于在需要自动化、批量化或工具化写作时选择 InkOS。默认仍以本项目小说 skill 为主，InkOS 只在能明显降低人工调度成本时启用。

## 三种模式

| 模式 | 入口 | 适用 |
|---|---|---|
| 本地创作模式 | `novel-writing` / `novel-draft` | 单章、片段、精修、审稿、强人工把控 |
| InkOS 加速模式 | `inkos-bridge` + `scripts/inkos.ps1` | 批量写章、导入续写、短篇包、AI 检测、风格分析 |
| 融合模式 | 先 InkOS 生成，再归档到 `docs/` | 快速产出草稿后继续用本项目精修、记忆和中文风格体系 |

## 常用命令

所有命令都从项目根目录执行，运行目录会自动切到 `.inkos-runtime/`：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\inkos_bootstrap.ps1
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 --help
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 doctor
```

新书和批量写章：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 init .
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 book create --title "书名" --genre urban --chapter-words 3000
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 write next "书名" --count 3 --words 3000
```

导入已有章节并续写：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 import chapters "书名" --from "path\to\novel.txt"
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 write next "书名" --count 3
```

短篇包：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 short run --direction "都市婚姻反转，女主证据反杀" --chapters 12 --chars 1000
```

审稿、修订、导出：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 audit "书名" chapter-1 --json
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 revise "书名" chapter-1 --mode polish --json
powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 export "书名" --format md
```

## 归档规则

- InkOS 运行数据留在 `.inkos-runtime/`，不要直接提交。
- 需要纳入本项目的正文，先导出 Markdown，再复制到 `docs/YYYY-MM-DD/小说/<中文书名>/正文/`。
- 导入后的 InkOS truth files 可以作为参考，但本项目最终真相源仍是 `project.md`、`outline.md`、`memory-snapshot.md`、`人物/`、`伏笔/`。
