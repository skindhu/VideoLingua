# Whisper 字幕提取工具

这是一个使用OpenAI的Whisper模型从视频文件中提取字幕并支持使用Google Gemini Flash 2.0 API进行翻译的工具。

## 功能特点

- 使用OpenAI的Whisper模型从视频中提取高质量字幕
- 支持多种Whisper模型（tiny, base, small, medium, large）
- 支持多语言字幕提取和自动语言检测
- 支持字幕翻译功能（使用Google Gemini Flash 2.0 API）
- 支持三种字幕类型：原始语言、翻译后和双语
- 支持多种输出格式：SRT、VTT和TXT
- 支持将字幕烧录到视频中，可自定义字体大小、位置和颜色
- 提供命令行和图形用户界面
- 字幕文件默认保存在output目录中

## 使用方法

### 图形界面

运行GUI应用程序：

```
python -m subtitle_extractor.whisper_gui
```

### 命令行工具

基本用法:
```
python -m subtitle_extractor.whisper_subtitle_extractor 视频文件路径
```

这将使用默认设置（base模型，自动检测语言）从视频中提取字幕，并生成SRT、VTT和TXT格式的字幕文件。

### 高级选项

```
python -m subtitle_extractor.whisper_subtitle_extractor 视频文件路径 [选项]

选项:
  --model MODEL           Whisper模型大小 (可选: tiny, base, small, medium, large)
                          默认: base
  --language LANG         指定源语言代码 (例如: zh, en, ja)
  --output OUTPUT         输出文件路径
  --formats FORMATS       输出格式，用逗号分隔 (默认: srt,vtt,txt)
  --keep-audio            保留提取的音频文件
  --subtitle-type TYPE    字幕类型: original(原始语言), translated(翻译后),
                          bilingual(双语) (默认: original)
  --dest-language LANG    目标翻译语言 (默认: zh-CN，中文)
  --api-key KEY           Gemini API密钥（也可通过GEMINI_API_KEY环境变量设置）
  --burn-subtitles        将字幕烧录到视频中
  --font-size SIZE        烧录字幕的字体大小 (默认: 28)
  --subtitle-position POS 烧录字幕的位置 (bottom/top/middle, 默认: bottom)
  --font-color COLOR      烧录字幕的字体颜色 (默认: white)
  --outline-color COLOR   烧录字幕的轮廓颜色 (默认: black)
```

### 示例

1. 使用基本设置提取字幕:
   ```
   python -m subtitle_extractor.whisper_subtitle_extractor /path/to/video.mp4
   ```

2. 使用更大的模型并指定中文:
   ```
   python -m subtitle_extractor.whisper_subtitle_extractor /path/to/video.mp4 --model medium --language zh
   ```

3. 生成翻译后的字幕:
   ```
   python -m subtitle_extractor.whisper_subtitle_extractor /path/to/video.mp4 --subtitle-type translated --dest-language en-US
   ```

4. 生成双语字幕:
   ```
   python -m subtitle_extractor.whisper_subtitle_extractor /path/to/video.mp4 --subtitle-type bilingual --dest-language zh-CN
   ```

5. 提取字幕并烧录到视频中:
   ```
   python -m subtitle_extractor.whisper_subtitle_extractor /path/to/video.mp4 --burn-subtitles --font-size 24 --font-color yellow
   ```

## 模型说明

Whisper提供了不同大小的模型，准确性和速度各不相同:

- `tiny`: 最小最快，但准确性较低
- `base`: 平衡速度和准确性（默认）
- `small`: 比base更准确，但更慢
- `medium`: 比small更准确，但更慢
- `large`: 最准确，但也最慢且需要更多内存

首次运行时，模型会自动下载到本地缓存中。

## 翻译功能

使用翻译功能需要提供Google Gemini Flash 2.0 API密钥，可以通过以下方式设置：

1. 通过命令行参数 `--api-key` 传入
2. 通过环境变量 `GEMINI_API_KEY` 设置
3. 在GUI界面中输入

## 字幕烧录

本工具支持将提取的字幕直接烧录到视频中，可以自定义以下参数：

- 字体大小：控制字幕的大小
- 字幕位置：可选底部、顶部或中间
- 字体颜色：支持多种预设颜色（白色、黄色、绿色、青色、蓝色、品红、红色）
- 轮廓颜色：字体轮廓颜色，提高可读性

烧录字幕是一个不可逆的过程，会生成一个新的视频文件，原始视频不会被修改。

## 作为模块使用

```python
from subtitle_extractor.whisper_subtitle_extractor import extract_subtitles

# 提取字幕
subtitle_files = extract_subtitles(
    video_path="video.mp4",
    model="base",
    language="en",
    subtitle_type="bilingual",
    dest_language="zh-CN",
    burn_subtitles=True,
    font_size=24,
    subtitle_position="bottom",
    font_color="yellow",
    outline_color="black"
)
```

## 注意事项

- 使用GPU可以显著加快处理速度
- 较大的模型（medium, large）需要更多内存和计算资源
- 首次运行时需要下载模型，请确保网络连接良好
- 翻译功能需要稳定的网络连接以访问Google Gemini API
- 字幕文件默认保存在output目录中
- 字幕烧录功能需要安装FFmpeg
