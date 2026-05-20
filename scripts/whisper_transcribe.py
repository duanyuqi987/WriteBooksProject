#!/usr/bin/env python3
"""
本地 Whisper 语音转文字系统。
音频不出本机，支持单文件和批量处理。

用法:
  # 基本转写
  python3 scripts/whisper_transcribe.py input.mp3

  # 高质量转写 + 字幕
  python3 scripts/whisper_transcribe.py input.mp4 --model large-v3 --output-srt

  # 输出小说素材格式
  python3 scripts/whisper_transcribe.py recording.wav --output-novel --tags "对话,市井"

依赖:
  pip install faster-whisper
  sudo apt install ffmpeg

模型下载（国内 huggingface 被墙）:
  方式1: 设置 HF 镜像
    export HF_ENDPOINT=https://hf-mirror.com
    python3 scripts/whisper_transcribe.py input.mp3

  方式2: 手动下载模型放到本地
    # 从 https://hf-mirror.com 下载对应模型目录，放到:
    # ~/.cache/huggingface/hub/models--Systran--faster-whisper-<model>/
    # 或者设置环境变量: export HF_HOME=/path/to/models

  方式3: 使用代理
    export HTTP_PROXY=http://127.0.0.1:7890
    export HTTPS_PROXY=http://127.0.0.1:7890
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# --- 文本清洗配置 ---

# 中文口语填充词
FILLER_WORDS_ZH = [
    "嗯", "啊", "呃", "那个", "这个", "就是说", "然后呢", "对吧",
    "你知道", "怎么说", "反正", "就是", "嘛", "吧", "呢", "啦",
]

# 中文口语重复模式
REPEAT_PATTERNS = [
    (r"(\S{1,3})\1{2,}", r"\1"),           # 单字重复 3 次以上 → 单字
    (r"(\S{2,6})\s?\1{1,}", r"\1"),         # 短语重复
]

# 对话标记词（用于说话人猜测）
SPEAKER_MARKERS = [
    r"(说|问|答|喊|叫|道|讲|骂|吼|嚷|嘀咕|嘟囔)",
]


def check_dependencies():
    """检查依赖是否安装。"""
    errors = []

    # 检查 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        errors.append("ffmpeg 未安装。请运行: sudo apt install ffmpeg -y")

    # 检查 whisper（优先 faster-whisper）
    has_whisper = False
    try:
        import faster_whisper
        has_whisper = True
        whisper_backend = "faster-whisper"
    except ImportError:
        try:
            import whisper
            has_whisper = True
            whisper_backend = "openai-whisper"
        except ImportError:
            pass

    if not has_whisper:
        errors.append(
            "Whisper 未安装。请运行:\n"
            "  pip install faster-whisper  (推荐，CPU 快 4 倍)\n"
            "  或 pip install openai-whisper"
        )

    if errors:
        print("[!] 缺少依赖:")
        for e in errors:
            print(f"    {e}")
        sys.exit(1)

    return whisper_backend


def convert_to_wav(input_path: str, output_dir: str) -> str:
    """用 ffmpeg 将任意音视频转为 16kHz 单声道 WAV。"""
    wav_path = os.path.join(output_dir, f"_temp_{os.path.basename(input_path)}.wav")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
        "-loglevel", "error",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 转换失败: {result.stderr.decode()}")
    return wav_path


def transcribe_faster_whisper(audio_path: str, model_name: str, language: str | None) -> dict:
    """使用 faster-whisper 转写。自动使用 HF 镜像。"""
    from faster_whisper import WhisperModel

    # 国内网络：自动尝试镜像
    if not os.environ.get("HF_ENDPOINT"):
        # 先尝试直连，失败后自动切镜像
        pass

    lang = None if language == "auto" else language
    try:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
    except Exception as e:
        error_msg = str(e)
        if "ConnectTimeout" in error_msg or "Connection" in error_msg:
            print("   [!] 无法连接 huggingface.co 下载模型")
            print("   [*] 尝试使用国内镜像...")
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
            try:
                model = WhisperModel(model_name, device="cpu", compute_type="int8")
                print("   ✓ 镜像连接成功")
            except Exception as e2:
                print(f"   [!] 镜像也失败: {e2}")
                print("   [*] 请手动下载模型或配置代理，参见脚本头部注释")
                raise
        else:
            raise

    segments_result, info = model.transcribe(
        audio_path,
        language=lang,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

    segments = []
    full_text = []
    for seg in segments_result:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
        })
        full_text.append(seg.text.strip())

    return {
        "text": " ".join(full_text),
        "segments": segments,
        "language": info.language,
        "duration": info.duration,
    }


def transcribe_openai_whisper(audio_path: str, model_name: str, language: str | None) -> dict:
    """使用 openai-whisper 转写。"""
    import whisper

    lang = None if language == "auto" else language
    model = whisper.load_model(model_name)

    result = model.transcribe(
        audio_path,
        language=lang,
        beam_size=5,
        verbose=False,
    )

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })

    return {
        "text": result["text"].strip(),
        "segments": segments,
        "language": result.get("language", "unknown"),
        "duration": result.get("duration", 0),
    }


def clean_text(text: str) -> str:
    """清洗转写文本：去填充词、去重复、优化断句。"""
    # 去除口语填充词
    for fw in FILLER_WORDS_ZH:
        # 匹配词首/词中的填充词
        text = re.sub(rf"\s*{fw}\s*", "", text)

    # 去除重复
    for pattern, replacement in REPEAT_PATTERNS:
        text = re.sub(pattern, replacement, text)

    # 合并多余空格
    text = re.sub(r"\s{2,}", " ", text)

    # 修正标点：中文标点后不要空格
    text = re.sub(r"([。，！？；：、]) +", r"\1", text)

    # 英文标点后加空格
    text = re.sub(r"([.?!,])([^\s\d])", r"\1 \2", text)

    # 段落间空行
    text = re.sub(r"([。！？])([^\s])", r"\1\n\2", text)

    return text.strip()


def guess_speakers(segments: list[dict], num_speakers: int) -> list[dict]:
    """简单说话人分离：基于停顿和对话标记词。"""
    if num_speakers <= 1:
        for seg in segments:
            seg["speaker"] = 0
        return segments

    # 基于停顿的说话人交替
    speaker = 0
    last_end = 0
    for seg in segments:
        gap = seg["start"] - last_end
        # 停顿超过 2 秒，可能换了说话人
        if gap > 2.0:
            speaker = (speaker + 1) % num_speakers
        seg["speaker"] = speaker
        last_end = seg["end"]

    return segments


def generate_srt(segments: list[dict]) -> str:
    """生成 SRT 字幕文件内容。"""
    lines = []
    for i, seg in enumerate(segments, 1):
        start_ts = _format_timestamp(seg["start"])
        end_ts = _format_timestamp(seg["end"])
        speaker_tag = f"[说话人{seg.get('speaker', 0)+1}] " if "speaker" in seg else ""
        lines.append(f"{i}")
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(f"{speaker_tag}{seg['text']}")
        lines.append("")
    return "\n".join(lines)


def generate_vtt(segments: list[dict]) -> str:
    """生成 WebVTT 字幕文件内容。"""
    lines = ["WEBVTT", ""]
    for i, seg in enumerate(segments, 1):
        start_ts = _format_timestamp(seg["start"], vtt=True)
        end_ts = _format_timestamp(seg["end"], vtt=True)
        speaker_tag = f"[说话人{seg.get('speaker', 0)+1}] " if "speaker" in seg else ""
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(f"{speaker_tag}{seg['text']}")
        lines.append("")
    return "\n".join(lines)


def _format_timestamp(seconds: float, vtt: bool = False) -> str:
    """秒数转为字幕时间戳格式。"""
    td = timedelta(seconds=seconds)
    total_ms = int(seconds * 1000)
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    sep = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def generate_notes(text: str, segments: list[dict], tags: list[str] | None) -> str:
    """生成结构化笔记。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag_line = ", ".join(tags) if tags else ""

    # 提取关键词
    words = re.findall(r"[一-鿿]{2,4}", text)
    from collections import Counter
    top_words = [w for w, _ in Counter(words).most_common(10) if len(w) >= 2]

    # 估计主题
    topic_keywords = {
        "写作": ["写", "故事", "人物", "情节", "角色", "小说"],
        "对话": ["说", "问", "答", "告诉", "讲"],
        "想法": ["觉得", "想", "认为", "应该", "可能"],
        "计划": ["要", "打算", "准备", "计划", "做"],
    }
    topics = []
    for topic, kws in topic_keywords.items():
        if any(kw in text for kw in kws):
            topics.append(topic)

    lines = [
        f"# 语音笔记",
        f"",
        f"- **时间**: {now}",
        f"- **关键词**: {', '.join(top_words[:8])}",
        f"- **主题**: {', '.join(topics) if topics else '待分类'}",
    ]
    if tag_line:
        lines.append(f"- **标签**: {tag_line}")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 摘要",
        f"",
    ])

    # 用前 200 字做摘要
    summary = text[:200].strip()
    if len(text) > 200:
        summary += "……"
    lines.append(summary)

    lines.extend([
        f"",
        f"## 全文",
        f"",
        text,
    ])

    return "\n".join(lines)


def generate_novel_material(text: str, segments: list[dict], source: str, tags: list[str] | None) -> str:
    """生成小说素材格式。"""
    now = datetime.now().strftime("%Y-%m-%d")
    tag_list = tags if tags else []
    word_count = len(text)

    # 分析语言特征
    sentences = re.split(r"[。！？.!?\n]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sent_len = sum(len(s) for s in sentences) / max(len(sentences), 1)

    # 提取可用的对话片段
    dialogue_parts = []
    for seg in segments:
        if len(seg["text"]) > 15:
            dialogue_parts.append(seg["text"])
            if len(dialogue_parts) >= 5:
                break

    lines = [
        f"---",
        f"source: {source}",
        f"date: {now}",
        f"tags: {json.dumps(tag_list, ensure_ascii=False)}",
        f"word_count: {word_count}",
        f"---",
        f"",
        f"# 录音素材：{Path(source).stem}",
        f"",
        f"## 语言特征分析",
        f"",
        f"- 平均句长: {avg_sent_len:.1f} 字",
        f"- 总字数: {word_count}",
        f"- 片段数: {len(segments)}",
        f"- 语言: 中文",
        f"",
        f"## 可用对话片段",
        f"",
    ]

    for i, dp in enumerate(dialogue_parts, 1):
        lines.append(f"### 片段 {i}")
        lines.append(f"> {dp}")
        lines.append("")

    lines.extend([
        f"## 完整转写",
        f"",
        text,
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="本地 Whisper 语音转文字系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="输入音频/视频文件路径")
    parser.add_argument("--model", default="medium",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisper 模型 (默认 medium)")
    parser.add_argument("--language", default="auto",
                        help="语言代码 (zh/en/ja/auto)")
    parser.add_argument("--output-dir", default="./output",
                        help="输出目录 (默认 ./output)")
    parser.add_argument("--output-txt", action="store_true", default=True,
                        help="输出纯文本")
    parser.add_argument("--output-srt", action="store_true",
                        help="输出 SRT 字幕")
    parser.add_argument("--output-vtt", action="store_true",
                        help="输出 WebVTT 字幕")
    parser.add_argument("--output-notes", action="store_true",
                        help="输出结构化笔记")
    parser.add_argument("--output-json", action="store_true",
                        help="输出 JSON (含时间戳/置信度)")
    parser.add_argument("--output-novel", action="store_true",
                        help="输出小说素材格式")
    parser.add_argument("--speakers", type=int, default=1,
                        help="说话人数量 (默认 1)")
    parser.add_argument("--clean", action="store_true", default=True,
                        help="清洗文本 (去填充词/去重复)")
    parser.add_argument("--no-clean", action="store_true",
                        help="不执行文本清洗")
    parser.add_argument("--tags", default="",
                        help="素材标签 (逗号分隔)")
    args = parser.parse_args()

    # 1. 检查依赖
    print("[1/5] 检查依赖...")
    backend = check_dependencies()
    print(f"   ✓ Whisper 后端: {backend}")

    # 2. 检查输入文件
    if not os.path.exists(args.input):
        print(f"[!] 文件不存在: {args.input}")
        sys.exit(1)

    input_path = os.path.abspath(args.input)
    print(f"   ✓ 输入文件: {input_path}")
    file_size = os.path.getsize(input_path) / (1024 * 1024)
    print(f"   ✓ 文件大小: {file_size:.1f} MB")

    # 3. 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    base_name = Path(input_path).stem

    # 4. 转换音频
    print("[2/5] 转换音频格式...")
    wav_path = convert_to_wav(input_path, args.output_dir)
    print(f"   ✓ WAV: {wav_path}")

    # 5. 转写
    print(f"[3/5] Whisper 转写 (模型: {args.model}, 语言: {args.language})...")
    t0 = time.time()

    lang_param = None if args.language == "auto" else args.language
    if backend == "faster-whisper":
        result = transcribe_faster_whisper(wav_path, args.model, lang_param)
    else:
        result = transcribe_openai_whisper(wav_path, args.model, lang_param)

    elapsed = time.time() - t0
    print(f"   ✓ 转写完成，耗时 {elapsed:.0f} 秒")
    print(f"   ✓ 检测语言: {result['language']}")
    print(f"   ✓ 音频时长: {result['duration']:.1f} 秒")
    print(f"   ✓ 文本片段: {len(result['segments'])} 段")

    # 6. 文本清洗
    text = result["text"]
    if args.clean and not args.no_clean:
        print("[4/5] 文本清洗...")
        text = clean_text(text)
        print(f"   ✓ 清洗后字数: {len(text)}")
    else:
        print("[4/5] 跳过文本清洗")

    # 7. 说话人分离
    segments = result["segments"]
    if args.speakers > 1:
        segments = guess_speakers(segments, args.speakers)
        print(f"   ✓ 说话人分离: {args.speakers} 人")

    # 8. 输出文件
    print("[5/5] 生成输出文件...")

    outputs = []

    # 纯文本
    txt_path = os.path.join(args.output_dir, f"{base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    outputs.append(("TXT", txt_path))

    # SRT 字幕
    if args.output_srt:
        srt_path = os.path.join(args.output_dir, f"{base_name}.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(generate_srt(segments))
        outputs.append(("SRT", srt_path))

    # VTT 字幕
    if args.output_vtt:
        vtt_path = os.path.join(args.output_dir, f"{base_name}.vtt")
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write(generate_vtt(segments))
        outputs.append(("VTT", vtt_path))

    # JSON
    if args.output_json:
        json_path = os.path.join(args.output_dir, f"{base_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "text": text,
                "segments": segments,
                "language": result["language"],
                "duration": result["duration"],
                "model": args.model,
            }, f, ensure_ascii=False, indent=2)
        outputs.append(("JSON", json_path))

    # 结构化笔记
    if args.output_notes:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
        notes_path = os.path.join(args.output_dir, f"{base_name}-笔记.md")
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write(generate_notes(text, segments, tags))
        outputs.append(("笔记", notes_path))

    # 小说素材
    if args.output_novel:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
        novel_path = os.path.join(args.output_dir, f"{base_name}-素材.md")
        with open(novel_path, "w", encoding="utf-8") as f:
            f.write(generate_novel_material(text, segments, input_path, tags))
        outputs.append(("素材", novel_path))

    # 清理临时 WAV
    try:
        os.remove(wav_path)
    except OSError:
        pass

    # 报告
    print()
    print("=" * 50)
    print("  转写完成")
    print("=" * 50)
    for fmt, path in outputs:
        size_kb = os.path.getsize(path) / 1024
        print(f"  [{fmt}] {path} ({size_kb:.1f} KB)")
    print(f"  总耗时: {elapsed:.0f} 秒")
    print(f"  文本字数: {len(text)}")


if __name__ == "__main__":
    main()
