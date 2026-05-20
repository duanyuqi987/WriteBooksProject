# HTML 输出规范

## 适用场景

本项目最终书稿一律保存为 `.html`。用户要求写书、学习文档、源码导读、网站知识整理、书籍学习指南、教师用书或混合资料课程时，最终交付都使用单文件 HTML。优先从 `assets/templates/learning-document.html` 复制模板，再替换占位符。

## 基本要求

- 单 HTML 文件，正文、样式和最小交互内嵌。
- 书名必须是中文，并同时出现在 HTML `<title>` 和正文首个 `<h1>` 中。
- 默认输出到 `docs/YYYY-MM-DD/学习书/<英文安全文件名>.html`；文件名可用英文 slug，书名不能用英文替代。
- 左侧或顶部目录支持至少四级结构。
- 正文区域适合长时间阅读：正文宽度适中、行高舒适、代码块可横向滚动。
- 章节 ID 稳定，方便后续精确替换。
- 包含文档版本、来源说明、字数信息、更新时间和修订日志。
- 可打印，移动端可阅读。

## 模板占位符

`assets/templates/learning-document.html` 包含这些占位符：

| 占位符 | 替换内容 |
|---|---|
| `{{TITLE}}` | 中文书名 |
| `{{SUBTITLE}}` | 副标题、读者对象或文档定位 |
| `{{DOC_META}}` | 版本、来源、字数、更新时间等元信息 |
| `{{TOC}}` | 目录树 |
| `{{CONTENT}}` | 正文 |
| `{{CHANGELOG}}` | 修订日志 |

## 章节 ID

稳定 ID 是后续更新的基础。

| 层级 | ID 格式 | 示例 |
|---|---|---|
| 章 | `chapter-1` | `第1章` |
| 节 | `sec-1-2` | `1.2节` |
| 小节 | `subsec-1-2-3` | `1.2.3小节` |
| 知识点 | `point-1-2-3-4` | `1.2.3.4知识点` |

不要在更新章节时改变旧 ID，否则目录链接、进度记录和外部引用会失效。

## 正文块结构

短知识点或资料卡可以使用：

```html
<section id="point-1-2-3-4" class="knowledge-point" data-source="repo-core,web-official">
  <h4>1.2.3.4 知识点标题</h4>
  <p class="goal">本节导读：...</p>
  <div class="concept">...</div>
  <pre><code>...</code></pre>
  <div class="pitfalls">...</div>
  <div class="review">...</div>
</section>
```

`data-source` 用于保留来源追踪。没有明确来源、属于原创桥接讲解时，可写 `data-source="synthesis"`。

学习书式长文应使用更自然的章节结构：

```html
<section id="chapter-3" data-source="web-official">
  <h2>第3章 抽样式规划为什么有效</h2>
  <p>连续正文...</p>
  <figure class="diagram">...</figure>
  <h3>3.1 PRM：先修路网，再问路线</h3>
  <p>连续正文...</p>
  <pre><code class="language-text">伪代码或代码</code></pre>
  <div class="num-example">数值例子...</div>
  <div class="callout">注意事项...</div>
</section>
```

用户要求“像书一样”“写成书”“小白理解算法和代码”时，优先使用学习书结构，不要每个小节重复 `goal/pitfalls/review`，也不要写成教案或课堂流程。

## 图、公式和代码

- Mermaid 可作为可选增强。如果文档必须完全离线，提供 ASCII 或静态 SVG 替代。
- 学习书式 HTML 优先使用内嵌 SVG 图、流程图、算法示意图、对比表和伪代码，让文件离线可读。
- MathJax 可作为可选增强。公式统一使用 `$$...$$`，不要混用单 `$`。
- 代码块必须带语言名，如 `<code class="language-python">`。
- 代码块前后要解释用途、输入、输出和风险。

## 目录要求

目录不只是章节列表，还要帮助读者判断进度。

目录项建议包含：

- 章节编号和标题。
- 当前章节学习目标。
- 可选的完成状态或阅读进度。
- 到正文 ID 的链接。

长文目录应可折叠。移动端可以放到顶部或通过按钮展开。

## 元信息

HTML `<head>` 中建议包含：

```html
<meta name="doc-version" content="v1.0">
<meta name="last-update" content="2026-05-13 12:00:00">
<meta name="word-count" content="0">
<meta name="book-title-language" content="zh-CN">
<meta name="source-policy" content="summarized-and-transformative">
```

正文开头建议包含来源说明，明确哪些来自项目、网站、书籍、用户资料，哪些是原创讲解。

## 占位章节

资料缺失但大纲需要保留时，不要只写“待补充”。占位章节至少包括：

- 为什么现在占位。
- 预计补充哪些内容。
- 需要用户或项目提供哪些来源。
- 这个章节与前后章节的关系。
- 临时学习建议。

## 更新已有 HTML

更新流程：

1. 读取现有 HTML。
2. 找到目标章节或知识点的稳定 ID。
3. 只替换目标 `<section>`。
4. 更新目录中对应标题或状态。
5. 更新 `word-count`、`last-update` 和修订日志。
6. 不改无关章节，不重排已有 ID。

## 可访问性与可读性

- 标题层级不要跳级。
- 链接文本要能看出目的，不写“点击这里”。
- 深浅色切换要保持对比度。
- 移动端正文不要横向溢出，代码块除外。
- 打印时隐藏交互按钮，保留标题、正文、来源和修订日志。
