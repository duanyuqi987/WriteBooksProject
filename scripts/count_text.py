#!/usr/bin/env python3
"""Estimate readable text volume in Markdown or HTML files."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af]")
LATIN_WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


# 读取文件并返回文本内容；输入是本地路径，输出是 UTF-8 文本。
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# 去除 HTML 标签、脚本、样式和 Markdown 代码围栏，保留可阅读正文。
def normalize_text(raw: str) -> str:
    without_code = FENCE_RE.sub(" ", raw)
    without_scripts = SCRIPT_STYLE_RE.sub(" ", without_code)
    without_tags = TAG_RE.sub(" ", without_scripts)
    unescaped = html.unescape(without_tags)
    return re.sub(r"\s+", " ", unescaped).strip()


# 统计 CJK 字符和英文词，返回适合 JSON 输出的统计对象。
def count_text(path: Path) -> dict[str, int | str]:
    text = normalize_text(read_text(path))
    cjk_chars = len(CJK_RE.findall(text))
    latin_words = len(LATIN_WORD_RE.findall(CJK_RE.sub(" ", text)))
    return {
        "source": str(path),
        "cjk_chars": cjk_chars,
        "latin_words": latin_words,
        "estimated_total": cjk_chars + latin_words,
    }


# 解析命令行参数；输入为 argv，输出为 argparse 的命名空间。
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate readable text volume in Markdown or HTML files.")
    parser.add_argument("file", type=Path, help="Path to a Markdown or HTML file.")
    return parser.parse_args()


# CLI 入口；校验文件存在后输出 JSON 统计结果。
def main() -> None:
    args = parse_args()
    if not args.file.is_file():
        raise SystemExit(f"File not found: {args.file}")
    print(json.dumps(count_text(args.file), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
