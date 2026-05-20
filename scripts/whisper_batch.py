#!/usr/bin/env python3
"""
Whisper 批量语音转文字处理器。
扫描输入目录，批量处理所有音视频文件，生成写作素材。

用法:
  # 基本批量处理
  python3 scripts/whisper_batch.py ./audio_files/

  # 批量处理 + 小说素材模式
  python3 scripts/whisper_batch.py ./recordings/ --pipeline novel-collect

  # 输出到指定目录
  python3 scripts/whisper_batch.py ./videos/ --output-dir ./docs/素材/
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 支持的音视频格式
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus", ".wma", ".aiff", ".ape",
}
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v", ".ts",
}
ALL_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


def scan_input_dir(input_dir: str, recursive: bool = True) -> list[Path]:
    """扫描输入目录中的所有音视频文件。"""
    input_path = Path(input_dir).resolve()
    if not input_path.exists():
        print(f"[!] 目录不存在: {input_dir}")
        sys.exit(1)

    files = []
    if recursive:
        for ext in ALL_EXTENSIONS:
            files.extend(input_path.rglob(f"*{ext}"))
    else:
        for f in input_path.iterdir():
            if f.suffix.lower() in ALL_EXTENSIONS:
                files.append(f)

    return sorted(files)


def run_transcribe(file_path: Path, output_dir: str, args) -> int:
    """对单个文件运行转写。"""
    cmd = [
        "python3",
        str(Path(__file__).parent / "whisper_transcribe.py"),
        str(file_path),
        "--model", args.model,
        "--language", args.language,
        "--output-dir", output_dir,
    ]

    if args.no_clean:
        cmd.append("--no-clean")

    if args.output_srt:
        cmd.append("--output-srt")
    if args.output_vtt:
        cmd.append("--output-vtt")
    if args.output_notes:
        cmd.append("--output-notes")
    if args.output_json:
        cmd.append("--output-json")
    if args.output_novel:
        cmd.append("--output-novel")

    if args.speakers > 1:
        cmd.extend(["--speakers", str(args.speakers)])

    if args.tags:
        cmd.extend(["--tags", args.tags])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [!] 失败: {result.stderr[:200]}")
        return 1
    return 0


def generate_batch_index(files: list[Path], results: list[dict], output_dir: str) -> str:
    """生成批量处理的索引文件。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_words = sum(r.get("word_count", 0) for r in results)
    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    lines = [
        f"# 语音转写批量处理报告",
        f"",
        f"- **处理时间**: {now}",
        f"- **总文件数**: {len(files)}",
        f"- **成功**: {len(success)}",
        f"- **失败**: {len(failed)}",
        f"- **总字数**: {total_words}",
        f"",
        f"## 文件清单",
        f"",
    ]

    for r in results:
        status_icon = "✓" if r["status"] == "success" else "✗"
        lines.append(f"- {status_icon} {r['file']} ({r.get('words', 0)} 字)")

    if failed:
        lines.append(f"")
        lines.append(f"## 失败文件")
        for r in failed:
            lines.append(f"- {r['file']}: {r.get('error', '未知错误')}")

    return "\n".join(lines)


def pipeline_novel_collect(files: list[Path], output_dir: str, args) -> int:
    """小说素材采集流水线：
    批量转写 → 生成素材md → 输出索引 → 统计
    """
    print(f"\n{'='*60}")
    print(f"  小说素材采集模式")
    print(f"{'='*60}")
    print(f"  输入文件: {len(files)} 个")
    print(f"  模型: {args.model}")
    print(f"  输出目录: {output_dir}")
    print()

    results = []
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)...")

        t0 = time.time()
        rc = run_transcribe(f, output_dir, args)
        elapsed = time.time() - t0

        status = "success" if rc == 0 else "failed"
        results.append({
            "file": f.name,
            "status": status,
            "elapsed": elapsed,
        })
        print(f"  [{status}] 耗时 {elapsed:.0f} 秒")

    # 生成索引
    if results:
        index_path = os.path.join(output_dir, f"_批量处理报告_{datetime.now():%Y%m%d_%H%M}.md")
        index_content = generate_batch_index(files, results, output_dir)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

        print(f"\n  报告已写入: {index_path}")

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n  完成: {success_count}/{len(files)} 成功")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Whisper 批量语音转文字处理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_dir", help="输入目录（含音视频文件）")
    parser.add_argument("--output-dir", default=None,
                        help="输出目录 (默认 输入目录/output/)")
    parser.add_argument("--model", default="medium",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisper 模型 (默认 medium)")
    parser.add_argument("--language", default="auto",
                        help="语言代码 (zh/en/ja/auto)")
    parser.add_argument("--speakers", type=int, default=1,
                        help="说话人数量")
    parser.add_argument("--output-srt", action="store_true",
                        help="输出 SRT 字幕")
    parser.add_argument("--output-vtt", action="store_true",
                        help="输出 WebVTT 字幕")
    parser.add_argument("--output-notes", action="store_true",
                        help="输出结构化笔记")
    parser.add_argument("--output-json", action="store_true",
                        help="输出 JSON")
    parser.add_argument("--output-novel", action="store_true",
                        help="输出小说素材格式")
    parser.add_argument("--no-clean", action="store_true",
                        help="不执行文本清洗")
    parser.add_argument("--tags", default="",
                        help="素材标签 (逗号分隔)")
    parser.add_argument("--pipeline", default=None,
                        choices=["novel-collect"],
                        help="使用预设流水线")
    parser.add_argument("--no-recursive", action="store_true",
                        help="不递归搜索子目录")
    parser.add_argument("--limit", type=int, default=0,
                        help="最大处理文件数 (0=全部)")
    args = parser.parse_args()

    # 1. 扫描文件
    print("[1/3] 扫描输入目录...")
    files = scan_input_dir(args.input_dir, recursive=not args.no_recursive)

    if not files:
        print(f"[!] 未找到音视频文件: {args.input_dir}")
        print(f"    支持格式: {', '.join(sorted(ALL_EXTENSIONS))}")
        sys.exit(1)

    print(f"   ✓ 找到 {len(files)} 个文件")

    if args.limit > 0 and args.limit < len(files):
        files = files[:args.limit]
        print(f"   ✓ 限制处理前 {args.limit} 个")

    # 2. 设置输出目录
    if args.output_dir is None:
        output_dir = os.path.join(args.input_dir, "output")
    else:
        output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    # 3. 按流水线执行
    if args.pipeline == "novel-collect":
        # 小说素材采集默认启用 novel 输出
        args.output_novel = True
        return pipeline_novel_collect(files, output_dir, args)

    # 默认批量处理
    print(f"\n[2/3] 批量转写 (模型: {args.model})...")
    print()

    results = []
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f.name}...", end=" ")
        file_output_dir = os.path.join(output_dir, f.stem)
        rc = run_transcribe(f, file_output_dir, args)
        print("✓" if rc == 0 else "✗")
        results.append({
            "file": f.name,
            "status": "success" if rc == 0 else "failed",
        })

    # 生成报告
    print(f"\n[3/3] 生成批量处理报告...")
    report_path = os.path.join(output_dir, f"_批量报告_{datetime.now():%Y%m%d_%H%M}.md")
    report = generate_batch_index(files, results, output_dir)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    success = sum(1 for r in results if r["status"] == "success")
    print(f"   ✓ 完成: {success}/{len(files)}")
    print(f"   ✓ 报告: {report_path}")


if __name__ == "__main__":
    main()
