# 视频字幕处理工具

这是一个综合性的视频字幕处理工具，包含字幕提取、翻译、烧录和视频内容总结功能。该工具采用模块化设计，每个模块都可以独立使用，也可以组合使用完成完整的字幕处理流程。

文章介绍：
[AI助力英语视频学习，轻松实现中英双语字幕与智能总结，效率翻倍](https://mp.weixin.qq.com/s/Kh67B746xTGrhOJ6mB8rOw)


## 项目结构

```
VideoLingua/
├── main.py                 # 主程序入口
├── subtitle_processor.py   # 字幕处理器（组合模块）
├── subtitle_extractor/     # 字幕提取模块
│   ├── whisper_subtitle_extractor.py  # 字幕提取工具
│   ├── whisper_gui.py      # 图形界面
│   ├── subtitle_writer.py  # 字幕写入工具
│   └── README.md           # 模块说明文档
├── translation/            # 翻译模块
│   ├── subtitle_translator.py  # 字幕翻译工具
│   ├── subtitle_translator_cli.py  # 字幕翻译命令行工具
│   ├── translator.py       # 翻译API封装
│   ├── __init__.py
│   └── README.md           # 模块说明文档
├── subtitle_burner/        # 字幕烧录模块
│   ├── subtitle_burner.py  # 字幕烧录工具
│   ├── burn_subtitle_cli.py # 字幕烧录命令行工具
│   ├── utils.py            # 辅助函数
│   ├── __init__.py
│   └── README.md           # 模块说明文档
├── video_summary/          # 视频总结模块
│   ├── summarizer.py       # 视频总结生成器
│   └── __init__.py
├── utils/                  # 工具模块
│   ├── gemini_api.py       # Gemini API工具
│   ├── config.py           # 配置管理工具
│   └── __init__.py
├── config/                 # 配置文件目录
│   └── .gitignore          # Git忽略配置
├── output/                 # 默认输出目录
├── test/                   # 测试目录
│   ├── run_all_tests.py                # 运行所有测试的主脚本
│   ├── test_subtitle_processor.py      # 字幕处理器集成测试
│   ├── test_subtitle_extractor.py      # 字幕提取模块测试
│   ├── test_subtitle_translator.py     # 字幕翻译模块测试
│   ├── test_subtitle_burner.py         # 字幕烧录模块测试
│   ├── test_video_summary.py           # 视频总结模块测试
│   ├── __init__.py
│   └── README.md                       # 测试说明文档
└── requirements.txt        # 项目依赖
```

## 安装

1. 确保已安装Python 3.7或更高版本
2. 安装FFmpeg（必须）:
   ```
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   ```
3. 安装Python依赖:
   ```
   pip install -r requirements.txt
   ```

## 功能特点

- **模块化设计**：每个功能模块可独立使用，也可组合使用
- **字幕提取**：使用OpenAI的Whisper模型从视频中提取高质量字幕
- **多语言支持**：支持多种语言的字幕提取和翻译
- **字幕翻译**：使用Google Gemini API进行高质量翻译
- **字幕烧录**：将字幕直接烧录到视频中，支持自定义字体大小、位置和颜色
- **视频总结**：根据字幕内容，使用Gemini API生成视频内容的详细总结
- **多种字幕类型**：支持原始语言、翻译后和双语字幕
- **多格式输出**：支持SRT、VTT和TXT格式
- **图形界面**：提供简单易用的GUI操作界面
- **命令行工具**：支持脚本和批处理操作

## 使用方法

### 完整处理流程

使用主程序可以一次性完成字幕提取、翻译和烧录：

```bash
python main.py video_file.mp4 [选项]

选项:
  --output DIR            指定输出目录
  --summarize             生成视频内容总结
  --subtitle FILE         指定用于总结的字幕文件（可选）
  --gui                   启动图形用户界面
```

主程序会根据配置文件中的设置自动处理视频，包括字幕提取、翻译和烧录（如果配置中启用）。处理完成后，如果指定了`--summarize`选项，还会生成视频内容总结。

### 图形界面

启动图形用户界面，可以通过可视化方式操作所有功能：

```bash
python main.py --gui
```

### 单独使用各模块

如果需要单独使用各功能模块，可以直接调用相应的模块：

#### 1. 字幕提取

```bash
# 直接使用模块
python -m subtitle_extractor.whisper_subtitle_extractor 视频文件路径 [选项]
```

详细说明请参阅[字幕提取模块文档](subtitle_extractor/README.md)。

#### 2. 字幕翻译

```bash
# 直接使用模块
python -m translation.subtitle_translator_cli 字幕文件路径 [选项]
```

详细说明请参阅[字幕翻译模块文档](subtitle_translator/README.md)。

#### 3. 字幕烧录

```bash
# 直接使用模块
python -m subtitle_burner.burn_subtitle_cli 视频文件路径 字幕文件路径 [选项]
```

详细说明请参阅[字幕烧录模块文档](subtitle_burner/README.md)。

#### 4. 视频总结

```bash
# 使用主程序
python main.py video_file.mp4 --summarize [--subtitle subtitle_file.srt] [--output DIR]

# 或直接使用模块
python -m video_summary.summarizer video_file.mp4 [--subtitle subtitle_file.srt] [--api-key YOUR_API_KEY] [--output-dir output_directory]
```

视频总结功能会根据视频的字幕文件，调用Gemini API生成视频内容的详细总结，并输出为一个与视频同名的Markdown文件（`video_file_summary.markdown`）。

如果不指定字幕文件，程序会尝试查找与视频同名的字幕文件，或使用字幕处理后生成的字幕文件。

### API密钥管理

使用翻译和视频总结功能需要提供Google Gemini API密钥，可以通过以下方式设置：

1. **环境变量**（推荐）：设置环境变量 `GEMINI_API_KEY`
   ```bash
   # Linux/macOS
   export GEMINI_API_KEY="your_api_key_here"

   # Windows
   set GEMINI_API_KEY=your_api_key_here
   ```

2. **配置文件**：在 `config/config.ini` 文件中设置
   ```ini
   [API]
   GEMINI_API_KEY = your_api_key_here
   ```

3. **使用脚本**：使用提供的脚本设置API密钥
   ```bash
   # 设置API密钥
   python set_api_key.py "your_api_key_here"
   ```

程序会优先使用环境变量中的API密钥，如果环境变量不存在，则使用配置文件中的设置。

## 字幕类型说明

本工具支持三种字幕类型：

1. **原始语言 (original)**：保持视频原始语言的字幕
2. **翻译后 (translated)**：将原始语言翻译为目标语言的字幕
3. **双语 (bilingual)**：同时包含原始语言和翻译后语言的双语字幕

## 配置文件

工具的默认设置保存在`config/config.ini`文件中，包括：

- 默认Whisper模型大小
- 默认源语言和目标语言
- 默认字幕类型
- 默认字幕烧录设置（字体大小、位置、颜色等）

## 测试工具

本项目提供了完整的单元测试和集成测试，用于确保各模块功能的正确性和稳定性。测试用例位于`test`目录下。

### 运行测试

```bash
# 运行所有测试（推荐方式）
python -m test.run_all_tests

# 或者直接运行测试脚本
python test/run_all_tests.py

# 运行特定模块的测试
python -m test.test_subtitle_extractor
python -m test.test_subtitle_translator
python -m test.test_subtitle_burner
python -m test.test_subtitle_processor
python -m test.test_video_summary
python -m test.test_real_summary
```

`run_all_tests.py`脚本提供了彩色输出和详细的测试时间统计，是运行测试的推荐方式。

详细的测试说明请参阅[测试文档](test/README.md)。

## 注意事项

- 字幕提取需要下载Whisper模型，首次运行时请确保网络连接良好
- 翻译功能需要有效的Google Gemini API密钥
- 字幕烧录功能需要安装FFmpeg
- 使用GPU可以显著加快字幕提取速度
- **地区限制**：Google Gemini API在某些地区可能不可用。如果您收到"User location is not supported"错误，请使用原始语言字幕类型(original)，或考虑使用VPN服务

## 若希望了解更多AI探索相关的内容，可关注作者公众号
<img src="https://wechat-account-1251781786.cos.ap-guangzhou.myqcloud.com/wechat_account.jpeg" width="30%">