---
name: novel-whisper
description: |
  本地 Whisper 语音转文字系统。音频不出本机，支持批量处理。
  用途：聊天录音转文字、语音备忘清洗成笔记、视频生成字幕、写作素材采集。
---

# Whisper 语音转文字

本地运行 OpenAI Whisper 模型，高质量语音转文字。所有处理在本机完成，音频不出机器。

## 核心能力

| 用途 | 输入 | 输出 | 写小说场景 |
|------|------|------|-----------|
| 聊天录音转文字 | 音频/录音 | 对话文本 | 对话素材、口语语感 |
| 语音备忘清洗 | 录音 | 结构化笔记 | 灵感记录、碎片整理 |
| 视频字幕生成 | 视频文件 | SRT/VTT 字幕 | 视频素材转文字素材 |
| 批量素材采集 | 文件夹 | 清洗后文本 | 大量素材快速转写 |
| 会议/播客转写 | 长音频 | 分段文本+摘要 | 话题素材、观点收集 |

## 模型选择

| 模型 | 参数量 | 速度(CPU) | 准确率 | 显存 | 适用场景 |
|------|--------|-----------|--------|------|---------|
| tiny | 39M | 最快 | ~85% | ~1GB | 实时、低资源设备 |
| base | 74M | 快 | ~90% | ~1GB | 日常录音 |
| small | 244M | 中等 | ~93% | ~2GB | 清晰录音、视频字幕 |
| medium | 769M | 较慢 | ~96% | ~5GB | 高质量需求 |
| large-v3 | 1550M | 慢 | ~98% | ~10GB | 最高质量、出版级 |

**推荐**：写小说素材采集用 `medium`（平衡速度和准确率），正式出版用 `large-v3`。

## HARD-GATE

使用前必须确认：

1. **安装检查**：`whisper` 和 `ffmpeg` 是否已安装
2. **磁盘空间**：模型文件约 1.5GB（large-v3），确保有足够空间
3. **隐私确认**：所有处理在本机完成，音频不出机器

## 首次安装

```bash
# 1. 安装 ffmpeg（音频处理）
sudo apt install ffmpeg -y

# 2. 安装 whisper（推荐 faster-whisper，CPU 加速 4 倍）
pip install faster-whisper --break-system-packages

# 3. 国内用户：设置 HuggingFace 镜像（否则模型下载失败）
export HF_ENDPOINT=https://hf-mirror.com

# 持久化镜像设置（写入 ~/.bashrc）
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
```

### 手动下载模型（离线使用）

如果镜像也不稳定，可以手动下载模型到本地：

```bash
# 从 hf-mirror.com 下载模型（以 medium 为例）
# 模型地址: https://hf-mirror.com/Systran/faster-whisper-medium

# 下载后解压到:
mkdir -p ~/.cache/huggingface/hub/
# 将下载的模型目录放入上述路径

# 或设置自定义模型路径:
export HF_HOME=/mnt/usvdisk/models/whisper
```

### 首次运行验证

```bash
# 用 tiny 模型跑一个测试（首次会自动下载约 150MB）
python3 scripts/whisper_transcribe.py test.mp3 --model tiny

# 如果网络有问题，先设置镜像:
HF_ENDPOINT=https://hf-mirror.com python3 scripts/whisper_transcribe.py test.mp3 --model tiny
```

## 使用方式

### 单文件转写

```bash
# 基本转写（默认 medium 模型）
python3 scripts/whisper_transcribe.py input.mp3

# 指定模型和语言
python3 scripts/whisper_transcribe.py input.mp3 --model large-v3 --language zh

# 输出字幕文件
python3 scripts/whisper_transcribe.py input.mp4 --output-srt

# 输出清洗后的笔记
python3 scripts/whisper_transcribe.py recording.wav --output-notes
```

### 批量处理

```bash
# 批量处理整个文件夹
python3 scripts/whisper_batch.py ./audio_files/ --model medium --language zh

# 批量处理并生成写作素材
python3 scripts/whisper_batch.py ./recordings/ --output-dir ./docs/素材/ --mode novel-material
```

### 写小说工作流集成

```bash
# 口语素材采集：录音 → 转写 → 清洗 → 按主题分类 → 写入素材库
python3 scripts/whisper_batch.py ./录音/ --pipeline novel-collect

# 对话研究：多人对话录音 → 分离说话人 → 对话模式分析
python3 scripts/whisper_transcribe.py chat.mp3 --speakers 3 --analyze-dialogue

# 播客/课程转写 → 结构化笔记 → 话题标签
python3 scripts/whisper_transcribe.py podcast.mp3 --output-notes --tags
```

## 转写清洗流水线

```
原始音频
  ↓
1. Whisper 转写（语音→原始文本）
  ↓
2. 说话人分离（多人对话场景）
  ↓
3. 文本清洗：
   - 去除口语填充词（嗯、啊、那个……）
   - 去除重复和口吃
   - 断句优化
   - 标点修正
  ↓
4. 结构化（可选）：
   - 对话模式 → 说话人标注
   - 笔记模式 → 要点+待办+关键词
   - 素材模式 → 主题标签+来源+时间戳
  ↓
5. 输出文件
```

## 输出格式

| 模式 | 输出文件 | 说明 |
|------|---------|------|
| --output-txt | `.txt` | 纯文本转写 |
| --output-srt | `.srt` | 字幕文件（带时间戳） |
| --output-vtt | `.vtt` | Web 字幕文件 |
| --output-notes | `.md` | 结构化笔记 |
| --output-json | `.json` | 完整 JSON（含时间戳/置信度/说话人） |
| --output-novel | `.md` | 小说素材格式（主题+标签+摘要） |

## 写小说素材输出格式

当使用 `--output-novel` 时，输出文件包含：

```markdown
---
source: 2026-05-17-录音-写作灵感.wav
date: 2026-05-17
tags: [人物对话, 市井语言, 吵架场景]
word_count: 3420
---

# 录音素材：市井吵架对话采集

## 原始转写
[完整转写文本]

## 可用片段
### 片段 1：菜市场争吵
> "你这秤不对！""谁说的？你拿回去称！"[具体对话]
- 可用于：市井场景对话
- 技法关联：白描、繁章波折法

### 片段 2：路人劝架
> "算了算了，大清早的……"[具体对话]
- 可用于：围观群众反应描写

## 语言特征
- 短句为主，平均句长 8 字
- 高频词：你、我、不、就、那个
- 句式：反问句多、省略主语
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| --model | medium | 模型选择：tiny/base/small/medium/large-v3 |
| --language | auto | 语言：zh/en/ja/auto |
| --output-dir | ./output | 输出目录 |
| --output-txt | True | 输出纯文本 |
| --output-srt | False | 输出 SRT 字幕 |
| --output-notes | False | 输出结构化笔记 |
| --output-novel | False | 输出小说素材格式 |
| --speakers | 1 | 说话人数量（用于分离） |
| --clean | True | 是否清洗文本 |
| --tags | "" | 素材标签（逗号分隔） |

## 性能参考（CPU 模式）

| 模型 | 1 小时音频处理时间 | 内存占用 |
|------|------------------|---------|
| tiny | ~10 分钟 | 1GB |
| base | ~15 分钟 | 1.5GB |
| small | ~30 分钟 | 2GB |
| medium | ~1 小时 | 5GB |
| large-v3 | ~3 小时 | 10GB |

## 集成到写小说流程

当用户说"把这段录音转成写作素材"时：

1. 确认音频文件路径
2. 执行 `whisper_transcribe.py --output-novel`
3. 将输出 `.md` 写入 `docs/YYYY-MM-DD/小说/<书名>/素材/` 目录
4. 更新 `memory-snapshot.md` 记录新素材来源
5. 在写作时，`novel-draft` 的 10 步读取可包含相关素材文件

## 隐私保证

- 所有处理在本机 CPU 上完成
- 音频文件不发送到任何外部服务器
- 模型文件下载一次后离线可用
- 转写结果仅存储在本机 `docs/` 目录
