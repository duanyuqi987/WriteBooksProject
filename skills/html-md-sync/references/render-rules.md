# Markdown 到 HTML 渲染规则

## 适用范围

Markdown 是新稿和后续维护稿的优先源稿；HTML 是阅读稿、发布稿或人工校验稿。历史 HTML 建基线时不要默认重渲染原 HTML；只有用户要求从 Markdown 生成 HTML、或新章节需要交付阅读稿时，才运行 Markdown 到 HTML 渲染。

## 输入与输出

- 输入：本地 `.md` 文件或目录。
- 默认输出：同目录同名 `.html`。
- 如果同名 `.html` 已存在，默认写入 `.candidate.html`，不覆盖历史阅读稿。
- 只有显式使用 `--overwrite` 时才覆盖同名 `.html`。

## 渲染规则

- 读取 YAML frontmatter；`title` 优先，其次正文首个 H1，再其次文件名。
- 渲染时移除正文首个 H1，并将它放入页面 hero，避免正文重复标题。
- Markdown 中显式锚点必须迁移到紧随其后的 `h2/h3/h4`：

```markdown
<a id="sec1"></a>
## 1. 机器人运动规划
```

渲染为：

```html
<h2 id="sec1">1. 机器人运动规划</h2>
```

- 只为已有显式锚点的标题生成结构 ID，不凭空给标题生成 slug，避免双轨检查出现 HTML 多 ID。
- 原始 HTML 块、SVG、公式块、提示块、总结块应保留。
- GitHub 风格表格、代码块、列表、引用、图片和链接交给 Markdown 解析器处理。
- TeX 公式分隔符 `\(...\)`、`\[...\]`、`$$...$$` 必须在渲染前保护，避免 Markdown 解析器吞掉反斜杠。
- 如果检测到公式，HTML 中注入 MathJax 配置；代码块中的公式不应被 MathJax 处理。

## 检查规则

- 新产物默认使用 `strict`：
  - Markdown H1 = HTML `<title>`
  - Markdown H1 = HTML 首个 H1
  - Markdown 显式锚点 ID = HTML `h2/h3/h4` 结构 ID
- 历史候选稿若只是比较原 HTML，可使用 `legacy`；但从 Markdown 新渲染出的 HTML 应尽量通过 `strict`。
- 渲染报告至少记录：输出路径、标题、字数差、warnings、issues 和双轨检查结果。
