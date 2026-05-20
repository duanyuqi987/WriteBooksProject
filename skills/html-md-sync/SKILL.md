---
name: html-md-sync
description: |
  Use when 用户需要把本地历史 HTML 书稿、学习文档、报告阅读版或小说成书稿批量转换为同名 Markdown 源稿，从 Markdown 生成同名 HTML 阅读稿，检查 Markdown/HTML 双轨同步，生成 legacy 基线报告，或维护 HTML 与 Markdown 成对交付。
---

# HTML MD Sync

## 核心职责

把已有 HTML 阅读稿补齐同名 Markdown 源稿，也支持把 Markdown 源稿渲染为同名 HTML 阅读稿，并验证两份文件是否能作为一组双轨产物继续维护。这个 skill 只处理本地文件，不抓取网页，不默认覆盖历史 HTML，不默认使用外部生成服务。

## 快速流程

1. **确认输入**
   - 单文件：`path/to/book.html`
   - 目录：`path/to/books/`
   - 默认只处理 `.html`，输出同目录同名 `.md`。

2. **读取转换规则**
   - 历史 HTML 转 Markdown 前读取 `references/conversion-rules.md`。
   - Markdown 渲染 HTML 前读取 `references/render-rules.md`。
   - 如果任务涉及网页抓取或平台发布，只把 `references/canghe-url-to-markdown` 和 `references/canghe-markdown-to-html` 作为参考；不要默认调用危险或反向工程 API。

3. **生成 Markdown 源稿**
   - 运行 `scripts/html_to_markdown.py`。
   - 默认不覆盖已有 `.md`；若已有人工稿，生成 `.candidate.md`。
   - 转换后保留 HTML 标题、H1、结构 ID、代码块、表格、公式块和 SVG。

4. **检查双轨同步**
   - 运行 `scripts/check_dual_format.py`。
   - 新产物用 `strict` 模式：Markdown H1、HTML `<title>`、HTML H1 必须一致。
   - 历史基线用 `legacy` 模式：Markdown H1 对齐 HTML H1；HTML `<title>` 与 H1 不一致只记 warning。

5. **从 Markdown 渲染 HTML**
   - 运行 `scripts/markdown_to_html.py`。
   - 默认不覆盖已有 `.html`；若已有历史阅读稿，生成 `.candidate.html`。
   - 新渲染产物默认用 `strict` 模式检查：Markdown H1、HTML `<title>`、HTML H1、结构 ID 必须一致。

6. **生成基线或候选报告**
   - 报告记录每对文件的标题、字数、ID 数量、缺失 ID、warnings 和 issues。
   - 有 issues 时不要宣称完成，只能说明已生成候选稿和待复核项。

## 推荐命令

单文件试转：

```bash
python3 scripts/html_to_markdown.py albooks/A1/第一章_机器人抓取与操作介绍.html --mode legacy-baseline
python3 scripts/check_dual_format.py albooks/A1/第一章_机器人抓取与操作介绍.md --mode legacy
```

批量建立历史基线：

```bash
python3 scripts/html_to_markdown.py albooks/A1 --mode legacy-baseline --report docs/2026-05-16/质量检查/albooks-A1-dual-format-baseline.json
python3 scripts/check_dual_format.py albooks/A1 --mode legacy
```

从 Markdown 生成候选 HTML：

```bash
python3 scripts/markdown_to_html.py albooks/A1 --mode strict --report docs/2026-05-16/质量检查/albooks-A1-md-to-html-candidate.json
```

## 输出约定

- Markdown 路径：与 HTML 同目录同名，例如 `第一章_机器人抓取与操作介绍.md`。
- 已存在 `.md` 时：写入 `第一章_机器人抓取与操作介绍.candidate.md`。
- 已存在 `.html` 时：写入 `第一章_机器人抓取与操作介绍.candidate.html`。
- Markdown frontmatter 必须包含：`title`、`source_html`、`generated_at`、`converter_version`、`sync_mode`。
- 章节锚点使用显式 HTML 锚点：

```markdown
<a id="sec1"></a>
## 1. 机器人运动规划
```

## 红线

- 不要默认覆盖已有 `.md`。
- 不要修改原始 `.html`。
- 不要默认用 Markdown 渲染结果覆盖历史 HTML；先生成 `.candidate.html` 并通过 strict 检查。
- 不要为追求纯 Markdown 而丢失 SVG、公式、代码或表格。
- 不要把 HTML `<title>` 与正文 H1 的历史差异当作 legacy 阻塞错误；只记录 warning。
- 不要默认调用 `canghe-danger-*` 这类危险/反向工程规则，除非用户明确点名并确认风险。
