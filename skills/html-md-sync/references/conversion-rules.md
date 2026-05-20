# HTML 到 Markdown 转换规则

## 读取范围

本地历史 HTML 默认按下面优先级提取正文：

1. `main#main`
2. `main`
3. `article`
4. `body`

删除阅读无关元素：`script`、`style`、`noscript`、`template`、`nav`、`aside`、`button`、`progress`、`#sidebar`、`#progress-bar`、`#mobile-nav-btn`、`.back-top`、`.chapter-nav`。

## 标题与元信息

- Markdown H1 使用 HTML 正文首个 `h1`。
- HTML `<title>` 写入 frontmatter 的 `html_title`，但 legacy 模式不要求它与 H1 完全一致。
- hero 中的副标题可作为 H1 后的斜体说明。
- `source_html` 使用相对路径，方便迁移。

## 结构 ID

带 `id` 的 `h2`、`h3`、`h4` 必须转成显式锚点：

```markdown
<a id="sec1-2"></a>
### 1.2 刚体旋转
```

这些 ID 是后续双轨同步和局部更新的锚点，不要改名。

## 内容保留

| HTML 内容 | Markdown 输出 |
|---|---|
| `pre > code.language-*` | fenced code block，保留语言名 |
| `table` | GitHub 风格 Markdown 表格 |
| `div.formula-block` | 原始 HTML 块，避免公式语义丢失 |
| `div.tip-box`、`div.summary-box`、`div.warning-box` | 原始 HTML 块或等价可读块 |
| `svg` | 原始 SVG HTML 块 |
| `mark` | 加粗保留重点 |
| `a[href]` | Markdown 链接 |

## 质量判断

转换后至少检查：

- `.md` 和 `.html` 是否成对存在。
- Markdown H1 是否等于 HTML H1。
- Markdown 锚点 ID 是否覆盖 HTML 的结构 ID。
- 字数差异是否异常。
- 是否有代码块、公式块、表格或 SVG 被完全丢失。
