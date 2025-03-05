# 字幕烧录模块

这个模块提供了将字幕烧录到视频中的功能，使用FFmpeg实现字幕硬编码。

## 功能特点

- 支持SRT格式字幕烧录
- 可自定义字体大小
- 可选择字幕位置（底部、顶部、中间）
- 可自定义字体颜色和轮廓颜色
- 透明背景和阴影效果，提高可读性
- 自动选择合适的字幕文件

## 使用方法

### 基本用法

```python
from subtitle_burner import burn_subtitles_to_video

# 将字幕烧录到视频中
output_video = burn_subtitles_to_video(
    video_path="input_video.mp4",
    subtitle_path="subtitle.srt",
    font_size=28,
    position="bottom",  # 可选: "bottom", "top", "middle"
    font_color="white",  # 可选: "white", "yellow", "green", "cyan", "blue", "magenta", "red"
    outline_color="black"  # 可选: "black", "white", 等
)

if output_video:
    print(f"字幕烧录成功，输出视频: {output_video}")
else:
    print("字幕烧录失败")
```

### 选择合适的字幕文件

```python
from subtitle_burner import select_subtitle_file

# 从多个字幕文件中选择合适的字幕文件
subtitle_files = [
    "video.srt",
    "video.zh-CN.srt",
    "video.bilingual.srt"
]

# 根据字幕类型选择合适的字幕文件
subtitle_file = select_subtitle_file(subtitle_files, "bilingual")

if subtitle_file:
    print(f"选择的字幕文件: {subtitle_file}")
else:
    print("未找到合适的字幕文件")
```

### 命令行使用

本模块可以通过以下命令行方式使用：

#### 专用字幕烧录工具

最直接的方式是使用专用的字幕烧录命令行工具，只需提供视频文件和字幕文件路径：

```bash
python -m subtitle_burner.burn_subtitle_cli 视频文件路径 字幕文件路径 [选项]
```

例如：

```bash
python -m subtitle_burner.burn_subtitle_cli ./input/video.mp4 ./input/subtitle.srt --font-size 24 --position bottom --font-color yellow
```

选项说明：
- `--output`, `-o`: 指定输出视频文件路径（默认自动生成）
- `--font-size`, `-fs`: 设置字体大小（默认28）
- `--position`, `-p`: 设置字幕位置（bottom/top/middle）
- `--font-color`, `-fc`: 设置字体颜色
- `--outline-color`, `-oc`: 设置轮廓颜色

#### 主程序命令

```bash
python main.py process 视频文件路径 --burn-subtitles --font-size 28 --subtitle-position bottom --font-color white --outline-color black
```

例如：

```bash
python main.py process ./output/video.mp4 --burn-subtitles --font-size 28 --subtitle-position bottom --font-color yellow --outline-color black
```

#### 字幕提取器直接调用

```bash
python -m subtitle_extractor.whisper_subtitle_extractor 视频文件路径 --burn-subtitles --font-size 28 --subtitle-position bottom --font-color white --outline-color black
```

例如：

```bash
python -m subtitle_extractor.whisper_subtitle_extractor ./output/video.mp4 --burn-subtitles --font-size 28 --subtitle-position bottom --font-color yellow --outline-color black
```

#### 命令行参数说明

- `--burn-subtitles`: 启用字幕烧录功能
- `--font-size`: 设置字体大小（默认28）
- `--subtitle-position`: 设置字幕位置（bottom/top/middle）
- `--font-color`: 设置字体颜色（white/yellow/green/cyan/blue/magenta/red）
- `--outline-color`: 设置轮廓颜色（black/white等）

这些参数也可以在配置文件`config/config.ini`中设置默认值。

## 参数说明

### burn_subtitles_to_video 函数

- `video_path`: 视频文件路径
- `subtitle_path`: 字幕文件路径
- `output_path`: 输出视频文件路径，如果为None则自动生成
- `font_size`: 字幕字体大小，默认为28
- `position`: 字幕位置，可选值: "bottom", "top", "middle"，默认为"bottom"
- `font_color`: 字体颜色，默认为"white"，支持以下预设颜色:
  - "white": 白色
  - "yellow": 黄色
  - "green": 绿色
  - "cyan": 青色
  - "blue": 蓝色
  - "magenta": 品红
  - "red": 红色
  - 也可以直接使用6位十六进制颜色值，如"ffff00"表示黄色
- `outline_color`: 字体轮廓颜色，默认为"black"，支持与`font_color`相同的颜色选项

### select_subtitle_file 函数

- `subtitle_files`: 字幕文件列表
- `subtitle_type`: 字幕类型，可选值: "original", "translated", "bilingual"

## 颜色选择建议

为了确保字幕在不同背景下都清晰可见，建议：

1. 使用高对比度的颜色组合，如白色字体配黑色轮廓，或黄色字体配黑色轮廓
2. 避免使用与视频主色调相近的颜色，以防字幕与背景混淆
3. 对于大多数视频，白色字体配黑色轮廓是最安全的选择
4. 如果视频中有大量白色背景，可以考虑使用黄色字体配黑色轮廓

## 依赖要求

- FFmpeg: 必须安装FFmpeg并确保可以在命令行中访问
- Python 3.7+

## 注意事项

- 字幕烧录是一个耗时的过程，尤其是对于长视频
- 烧录后的视频文件通常比原始视频文件大
- 确保字幕文件与视频文件的时间轴匹配
- 字幕烧录后无法再更改字幕内容，这是一个不可逆的过程