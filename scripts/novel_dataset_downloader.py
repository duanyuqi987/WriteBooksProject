#!/usr/bin/env python3
"""
中文小说数据集下载器。
从 HuggingFace (via hf-mirror.com) 和 ModelScope 下载小说数据集，
作为写作参考和素材库。

用法:
  # 下载所有推荐数据集（每个取前 N 条）
  python3 scripts/novel_dataset_downloader.py

  # 指定下载数量和输出目录
  python3 scripts/novel_dataset_downloader.py --max-per-dataset 5000 --output-dir ./docs/小说素材/

  # 只下载特定数据集
  python3 scripts/novel_dataset_downloader.py --dataset webnovel-chinese

  # 列出所有可用数据集
  python3 scripts/novel_dataset_downloader.py --list

推荐数据集（已调研）:
  1. wdndev/webnovel-chinese       — 9000 本网文小说，已清洗，~9B tokens
  2. jetaudio/chinese_web_novels   — 20 万本中文网文（最大）
  3. silk-road/50-Chinese-Novel-Characters — 50 个小说角色数据
  4. mrzjy/Chinese_interactive_novels_3k  — 3534 本互动小说
  5. qwertyuiopasdfg/Chinese-web-novel   — 12740 项清洗后章节
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# ---- 数据集清单 ----

DATASETS = {
    "webnovel-chinese": {
        "id": "wdndev/webnovel-chinese",
        "description": "9000本网文小说，已清洗分割，约9B tokens",
        "source": "huggingface",
        "recommended": True,
        "sample_count": 5000,
    },
    "chinese-web-novels": {
        "id": "jetaudio/chinese_web_novels",
        "description": "20万+中文网文小说（体量最大）",
        "source": "huggingface",
        "recommended": True,
        "sample_count": 10000,  # 太大，只取部分
    },
    "novel-characters": {
        "id": "silk-road/50-Chinese-Novel-Characters",
        "description": "50个小说角色数据集，含角色描述和对话",
        "source": "huggingface",
        "recommended": True,
        "sample_count": 0,  # 全取
    },
    "interactive-novels": {
        "id": "mrzjy/Chinese_interactive_novels_3k",
        "description": "3534本中文互动小说，结构化语料",
        "source": "huggingface",
        "recommended": False,
        "sample_count": 2000,
    },
    "chinese-web-novel": {
        "id": "qwertyuiopasdfg/Chinese-web-novel",
        "description": "12740项清洗后网文章节",
        "source": "huggingface",
        "recommended": False,
        "sample_count": 3000,
    },
}


def install_dependencies():
    """安装所需依赖。"""
    deps = ["datasets", "huggingface_hub"]
    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            print(f"[*] 安装 {dep}...")
            import subprocess
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep,
                "--break-system-packages", "-q"
            ])
            print(f"   ✓ {dep} 安装完成")


def setup_mirror():
    """设置 HF 镜像（国内加速）。"""
    if not os.environ.get("HF_ENDPOINT"):
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        print("[*] 已自动设置 HF_ENDPOINT=https://hf-mirror.com")


def list_datasets():
    """列出所有可用数据集。"""
    print("\n可用中文小说数据集:\n")
    for key, ds in DATASETS.items():
        rec = "⭐" if ds["recommended"] else "  "
        print(f"  {rec} {key}")
        print(f"     HuggingFace: {ds['id']}")
        print(f"     {ds['description']}")
        print()


def download_dataset(ds_key: str, ds_info: dict, output_dir: str, max_samples: int,
                     raw_dir: str) -> dict:
    """下载单个数据集。"""
    from datasets import load_dataset

    ds_id = ds_info["id"]
    print(f"\n{'='*60}")
    print(f"  下载: {ds_key} ({ds_id})")
    print(f"{'='*60}")

    result = {"key": ds_key, "status": "failed", "count": 0, "output": ""}

    try:
        # 尝试加载数据集
        print(f"  连接 {ds_id} ...")
        dataset = load_dataset(ds_id, split="train", trust_remote_code=True, streaming=True)
        print(f"  ✓ 连接成功")

        # 流式读取
        samples = []
        for i, row in enumerate(dataset):
            if max_samples > 0 and i >= max_samples:
                break
            samples.append(row)
            if (i + 1) % 500 == 0:
                print(f"  已读取 {i+1} 条...")

        print(f"  ✓ 共读取 {len(samples)} 条")

        if not samples:
            print("  [!] 数据集为空")
            return result

        # 检测数据格式
        first_row = samples[0]
        print(f"  列名: {list(first_row.keys())}")

        # 保存原始 JSONL
        raw_path = os.path.join(raw_dir, f"{ds_key}.jsonl")
        os.makedirs(raw_dir, exist_ok=True)
        with open(raw_path, "w", encoding="utf-8") as f:
            for s in samples:
                # 将复杂类型转为字符串
                clean = {}
                for k, v in s.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean[k] = v
                    elif v is None:
                        clean[k] = ""
                    else:
                        clean[k] = str(v)
                f.write(json.dumps(clean, ensure_ascii=False) + "\n")

        # 处理成写作参考格式
        processed = process_samples(ds_key, samples)
        output_path = os.path.join(output_dir, f"{ds_key}-写作参考.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(processed)

        result["status"] = "success"
        result["count"] = len(samples)
        result["output"] = output_path
        print(f"  ✓ 写入: {output_path}")

    except ImportError as e:
        print(f"  [!] 缺少依赖: {e}")
        print(f"  [*] 请运行: pip install datasets --break-system-packages")
        result["error"] = str(e)
    except Exception as e:
        error_msg = str(e)[:200]
        print(f"  [!] 下载失败: {error_msg}")
        result["error"] = error_msg

    return result


def process_samples(ds_key: str, samples: list[dict]) -> str:
    """将数据集的原始数据转换为写作参考 markdown。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {ds_key} 写作参考",
        f"",
        f"- **来源**: {DATASETS[ds_key]['id']}",
        f"- **下载时间**: {now}",
        f"- **条目数**: {len(samples)}",
        f"",
        f"---",
        f"",
    ]

    # 根据数据集类型生成不同格式
    if ds_key in ("webnovel-chinese", "chinese-web-novels", "chinese-web-novel"):
        lines.append("## 小说文本参考")
        lines.append("")
        lines.append(f"共 {len(samples)} 篇/段小说文本，可用于：")
        lines.append("- 分析网络小说常用句式、对话模式")
        lines.append("- 提取爽文写作套路")
        lines.append("- 统计高频词汇和语言习惯")
        lines.append("")

        # 文本统计分析
        all_text = ""
        for s in samples:
            # 尝试各种可能的文本字段
            text = s.get("text") or s.get("content") or s.get("novel_text") or s.get("chapter") or ""
            all_text += text + "\n"

        if all_text.strip():
            # 高频词
            words = re.findall(r"[一-鿿]{2,4}", all_text)
            top_words = Counter(words).most_common(50)

            lines.append("### 高频词汇 Top50")
            lines.append("")
            lines.append("| 词汇 | 出现次数 |")
            lines.append("|------|---------|")
            for word, count in top_words:
                lines.append(f"| {word} | {count} |")
            lines.append("")

            # 句式分析
            sentences = re.split(r"[。！？.!?\n]+", all_text[:50000])
            sentences = [s.strip() for s in sentences if s.strip()]
            if sentences:
                avg_len = sum(len(s) for s in sentences) / len(sentences)
                short = sum(1 for s in sentences if len(s) <= 10)
                medium = sum(1 for s in sentences if 10 < len(s) <= 25)
                long = sum(1 for s in sentences if len(s) > 25)

                lines.append("### 句式结构分析")
                lines.append("")
                lines.append(f"- 平均句长: {avg_len:.1f} 字")
                lines.append(f"- 短句(≤10字): {short} ({short/max(len(sentences),1)*100:.0f}%)")
                lines.append(f"- 中句(11-25字): {medium} ({medium/max(len(sentences),1)*100:.0f}%)")
                lines.append(f"- 长句(>25字): {long} ({long/max(len(sentences),1)*100:.0f}%)")
                lines.append("")

        # 小说片段示例
        lines.append("### 文本片段示例")
        lines.append("")
        for i, s in enumerate(samples[:15], 1):
            text = s.get("text") or s.get("content") or s.get("novel_text") or s.get("chapter") or ""
            if not text:
                continue
            excerpt = text[:300].replace("\n", " ").strip()
            if len(text) > 300:
                excerpt += "……"
            lines.append(f"**片段 {i}**")
            lines.append(f"> {excerpt}")
            lines.append("")

    elif ds_key == "novel-characters":
        lines.append("## 角色数据参考")
        lines.append("")
        lines.append("可用于角色工坊的参考素材。")
        lines.append("")

        for i, s in enumerate(samples[:50], 1):
            name = s.get("name") or s.get("character_name") or f"角色{i}"
            desc = s.get("description") or s.get("bio") or s.get("简介") or ""
            dialogue = s.get("dialogue") or s.get("对话") or ""

            lines.append(f"### {name}")
            lines.append("")
            if desc:
                lines.append(f"**角色描述**: {str(desc)[:200]}")
                lines.append("")
            if dialogue:
                lines.append(f"**对话示例**: {str(dialogue)[:200]}")
                lines.append("")

    elif ds_key == "interactive-novels":
        lines.append("## 互动小说参考")
        lines.append("")
        lines.append("可用于分支故事设计的参考。")
        lines.append("")

        for i, s in enumerate(samples[:30], 1):
            title = s.get("title") or s.get("name") or f"互动小说{i}"
            content = s.get("content") or s.get("text") or ""
            if isinstance(content, dict):
                content = json.dumps(content, ensure_ascii=False)

            lines.append(f"### {title}")
            lines.append("")
            excerpt = str(content)[:250]
            if len(str(content)) > 250:
                excerpt += "……"
            lines.append(f"> {excerpt}")
            lines.append("")

    else:
        # 通用格式
        lines.append("## 数据预览")
        lines.append("")
        for i, s in enumerate(samples[:20], 1):
            lines.append(f"### 条目 {i}")
            lines.append("```json")
            lines.append(json.dumps(s, ensure_ascii=False, indent=2)[:500])
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


def generate_index(results: list[dict], output_dir: str) -> str:
    """生成数据集索引文件。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = sum(r["count"] for r in results)
    success = [r for r in results if r["status"] == "success"]

    lines = [
        f"# 小说数据集索引",
        f"",
        f"- **下载时间**: {now}",
        f"- **数据集数**: {len(results)}",
        f"- **成功**: {len(success)}",
        f"- **总条目**: {total}",
        f"",
        f"## 数据集清单",
        f"",
    ]

    for r in results:
        icon = "✓" if r["status"] == "success" else "✗"
        ds_info = DATASETS.get(r["key"], {})
        lines.append(f"- {icon} **{r['key']}** — {ds_info.get('description','')} ({r['count']}条)")

    lines.append("")
    lines.append("## 使用方式")
    lines.append("")
    lines.append("这些数据集可作为写作时的参考素材：")
    lines.append("- **novel-draft**: 参考高频词和句式结构，校准文风")
    lines.append("- **novel-brainstorm**: 参考角色设计模式")
    lines.append("- **novel-review**: 对比审查时的基准参考")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="中文小说数据集下载器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dataset", default=None,
                        help="下载指定数据集 (key name, 用 --list 查看)")
    parser.add_argument("--max-per-dataset", type=int, default=0,
                        help="每个数据集最大下载数 (0=使用默认值)")
    parser.add_argument("--output-dir", default=None,
                        help="输出目录")
    parser.add_argument("--list", action="store_true",
                        help="列出所有可用数据集")
    parser.add_argument("--no-recommended-only", action="store_true",
                        help="下载所有数据集（不仅推荐）")
    args = parser.parse_args()

    if args.list:
        list_datasets()
        return

    # 初始化
    print("📚 中文小说数据集下载器\n")
    install_dependencies()
    setup_mirror()

    # 确定输出目录
    today = datetime.now().strftime("%Y-%m-%d")
    if args.output_dir:
        output_dir = args.output_dir
    else:
        project_root = Path(__file__).resolve().parent.parent
        output_dir = str(project_root / "docs" / today / "小说" / "数据集")

    raw_dir = os.path.join(output_dir, "_raw")
    os.makedirs(output_dir, exist_ok=True)

    # 选择数据集
    if args.dataset:
        if args.dataset not in DATASETS:
            print(f"[!] 未知数据集: {args.dataset}")
            print(f"    可用: {', '.join(DATASETS.keys())}")
            print(f"    用 --list 查看详情")
            sys.exit(1)
        selected = {args.dataset: DATASETS[args.dataset]}
    elif args.no_recommended_only:
        selected = DATASETS
    else:
        selected = {k: v for k, v in DATASETS.items() if v["recommended"]}

    print(f"将下载 {len(selected)} 个数据集:")
    for k, v in selected.items():
        print(f"  - {k}: {v['description']}")
    print(f"输出目录: {output_dir}\n")

    # 逐一下载
    results = []
    for key, info in selected.items():
        max_n = args.max_per_dataset if args.max_per_dataset > 0 else info["sample_count"]
        result = download_dataset(key, info, output_dir, max_n, raw_dir)
        results.append(result)
        time.sleep(1)  # 请求间隔

    # 生成索引
    print(f"\n{'='*60}")
    print(f"  生成索引报告")
    print(f"{'='*60}")

    index_path = os.path.join(output_dir, "_数据集索引.md")
    index_content = generate_index(results, output_dir)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    # 汇总报告
    print(f"\n{'='*60}")
    print(f"  下载完成")
    print(f"{'='*60}")
    success_count = sum(1 for r in results if r["status"] == "success")
    total_items = sum(r["count"] for r in results)
    print(f"  数据集: {success_count}/{len(results)} 成功")
    print(f"  总条目: {total_items}")
    print(f"  索引: {index_path}")
    for r in results:
        if r["status"] == "success":
            print(f"  ✓ {r['key']}: {r['count']} 条 → {r['output']}")
        else:
            print(f"  ✗ {r['key']}: {r.get('error', '未知错误')}")


if __name__ == "__main__":
    main()
