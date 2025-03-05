# 字幕翻译器模块

这个模块提供了将字幕文件翻译成其他语言的功能，使用Google Gemini API实现高质量翻译。

## 功能特点

- 支持SRT、VTT和TXT格式字幕翻译
- 支持翻译后字幕和双语字幕两种模式
- 自动检测源语言或手动指定源语言
- 支持多种目标语言
- 保持原始字幕格式和时间轴
- 命令行工具和API接口

## 使用方法

### 命令行使用

最直接的方式是使用命令行工具：

```bash
python -m subtitle_translator.subtitle_translator_cli 字幕文件路径 [选项]
```

例如：

```bash
python -m subtitle_translator.subtitle_translator_cli ./input/subtitle.srt --type bilingual --dest-lang zh-CN
```

选项说明：
- `--output`, `-o`: 指定输出字幕文件路径（默认自动生成）
- `--type`, `-t`: 设置字幕类型（translated/bilingual）
- `--src-lang`, `-sl`: 设置源语言代码（默认auto自动检测）
- `--dest-lang`, `-dl`: 设置目标语言代码（默认zh-CN中文）
- `--api-key`, `-k`: 设置Gemini API密钥

### 作为模块导入使用

```python
from subtitle_translator.subtitle_translator import generate_subtitles
from subtitle_processor import translate_subtitle_file

# 方法1：直接翻译字幕文件
translated_file = translate_subtitle_file(
    file_path="subtitle.srt",
    subtitle_type="bilingual",  # 或 "translated"
    dest_language="zh-CN",
    src_language="en"
)

# 方法2：翻译字幕片段
subtitle_data = generate_subtitles(
    result=whisper_result,  # Whisper转录结果
    subtitle_type="bilingual",
    src_lang="en",
    dest_lang="zh-CN"
)
```

## 字幕类型说明

本模块支持两种字幕类型：

1. **翻译后 (translated)**：将原始语言翻译为目标语言的字幕
2. **双语 (bilingual)**：同时包含原始语言和翻译后语言的双语字幕

## 支持的语言

本模块支持多种语言翻译，包括但不限于：

- 中文简体 (zh-CN)
- 中文繁体 (zh-TW)
- 英语 (en)
- 日语 (ja)
- 韩语 (ko)
- 法语 (fr)
- 德语 (de)
- 西班牙语 (es)
- 俄语 (ru)

## 依赖要求

- Python 3.7+
- Google Gemini API密钥

## 注意事项

- 翻译功能需要有效的Google Gemini API密钥
- 翻译质量取决于API的性能和源字幕的质量
- 某些特殊格式或非标准字幕可能需要预处理
- **地区限制**：Google Gemini API在某些地区可能不可用。如果您收到"User location is not supported"错误，请考虑使用VPN服务