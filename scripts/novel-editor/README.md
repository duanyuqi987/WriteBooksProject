# 小说编辑脚本存档

本目录存放的是小说《银杏辞》编辑过程中实际使用的 Python 脚本，共计 70+ 个，分为以下类别。

**这些脚本是实战案例存档，不是持续维护的通用工具。** 如果您不需要参考小说编辑管线实现，可以删除整个目录。

## 脚本分类

### 叙事优化
- `optimize_b2_narrative.py` / `apply_b2_narrative.py` / `build_b2_narrative_json.py` — Book 2 叙事结构优化管线
- `diagnose_narrative.py` — 叙事诊断

### 破折号处理
- `optimize_dashes.py` ~ `optimize_dashes_v4.py` — 破折号规范化（多轮迭代）
- `optimize_b2_dashes.py` / `optimize_renwu_dashes.py` / `optimize_fulu_dashes.py` — 各卷破折号专项处理
- `optimize_jiushi_dashes_v1.py` ~ `v3.py` — 旧事卷破折号处理
- `diagnose_dashes.py` / `diagnose_jiushi_dashes.py` — 破折号诊断

### 章节提取
- `extract_books.py` / `extract_all_books.py` / `extract_books_345.py` — 从主 HTML 提取各 Book
- `extract_b2_target_chapters.py` / `extract_high_density_chapters.py` / `extract_dash_context.py`

### 去重与结构优化
- `round1_dedupe.py` / `round2_dedupe.py` — 跨书去重
- `round3_structural.py` — 结构调整
- `round4_enrich.py` — 章节充实

### Book 2 优化管线
- `optimize_b2_part1.py` ~ `optimize_b2_part6.py` — 分步迭代优化
- `fix_b3.py` / `fix_b3_v2.py` — Book 3 修复

### 桥接章节
- `add_jiushi_bridges.py` / `check_jiushi_bridges.py` / `prep_jiushi_bridges.py` / `check_bridges.py` / `optimize_b2_bridge.py`

### JSON 构建与同步
- `build_jiushi_v2_json.py` / `apply_jiushi_v2.py` / `fix_jiushi_v2_quotes.py` — 九式 v2 替换管线
- `build_jiushi_weak_json.py` / `apply_jiushi_weak.py` — 弱替换
- `build_renwu_opt_json.py` / `apply_renwu_opt.py` — 人物卷优化
- `build_fulu_opt_json.py` / `apply_fulu_opt.py` — 附录卷优化
- `sync_b2_md.py` / `sync_jiushi_md.py` / `sync_renwu_md.py` / `sync_fulu_md.py` — 同步输出

### 完整性检查
- `check_integrity.py` / `diagnose_characters.py` / `diagnose_plot.py` / `diagnose_b2_round6.py` / `diagnose_round9.py`

### 其他
- `optimize_books.py` / `regenerate_md.py` / `finalize_b2.py` / `fix_html_and_extract.py` / `read_target_openings.py` / `debug_v2_misses.py`

## 依赖

所有脚本仅使用 Python 标准库（`re`、`os`、`json`、`html`、`pathlib`、`argparse`、`sys`），无需 pip 安装任何第三方包。
