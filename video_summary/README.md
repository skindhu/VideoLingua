# 视频总结模块

视频总结模块是一个强大的工具，可以根据视频的字幕内容，使用Google Gemini API生成视频内容的详细总结。该模块可以独立使用，也可以与其他模块组合使用，完成完整的视频处理流程。

## 功能特点

- **自动提取文本**：从字幕文件中提取文本内容
- **智能总结生成**：使用Google Gemini API生成高质量的视频内容总结
- **中文输出**：默认生成中文总结，无论原始字幕语言
- **Markdown格式**：总结以Markdown格式保存，便于阅读和分享
- **自定义输出**：支持自定义输出目录和文件名
- **灵活集成**：可以独立使用，也可以与其他模块集成

## 安装依赖

视频总结模块依赖于以下Python包：

```bash
pip install google-generativeai pysrt tqdm
```

## 使用方法

### 命令行使用

```bash
# 直接使用模块
python -m video_summary.summarizer video_file.mp4 [选项]

选项:
  --subtitle FILE         指定字幕文件路径（如果不指定，将尝试查找与视频同名的字幕文件）
  --api-key KEY           指定Google Gemini API密钥（如果不指定，将尝试从配置文件读取）
  --output-dir DIR        指定输出目录（默认为视频文件所在目录）
  --verbose               显示详细日志信息
```

### 通过主程序使用

```bash
# 使用主程序
python main.py video_file.mp4 --summarize [--subtitle subtitle_file.srt] [--output DIR]
```

### 作为Python模块导入

```python
from video_summary.summarizer import VideoSummarizer

# 创建总结器实例
summarizer = VideoSummarizer(api_key="YOUR_API_KEY")

# 从字幕文件生成总结
summary = summarizer.summarize_video_from_subtitle(
    video_path="path/to/video.mp4",
    subtitle_path="path/to/subtitle.srt",
    output_dir="path/to/output"
)

# 或者直接从字幕文本生成总结
subtitle_text = "这是字幕文本内容..."
summary = summarizer.generate_summary(subtitle_text)
```

## 输出示例

视频总结模块会生成一个Markdown格式的总结文件，包含以下内容：

```markdown
# 视频内容总结

## 主题与目的
- 视频的主要主题和目的
- 视频的背景和上下文

## 关键点与重要信息
- 视频中提到的主要观点
- 重要的数据和事实
- 关键的论点和结论

## 结构与组织
- 视频内容的组织方式
- 主要部分和章节
- 内容的逻辑流程

## 数据与观点
- 视频中提到的数据和统计信息
- 专家观点和引用
- 案例研究和示例

## 总结与结论
- 视频的主要结论
- 行动建议和下一步
- 最终思考和观点
```

## API密钥管理

使用视频总结功能需要提供Google Gemini API密钥，可以通过以下方式设置：

1. **命令行参数**：使用`--api-key`参数直接指定
2. **环境变量**：设置`GEMINI_API_KEY`环境变量
3. **配置文件**：在`config/config.ini`文件中设置`api_key`

```bash
# 通过主程序设置API密钥
python main.py key set --value YOUR_API_KEY
```

## 注意事项

- 视频总结功能需要有效的Google Gemini API密钥
- 总结质量取决于字幕的质量和完整性
- 总结生成可能需要一定时间，特别是对于长视频
- 默认生成中文总结，无论原始字幕语言
- **地区限制**：Google Gemini API在某些地区可能不可用。如果您收到"User location is not supported"错误，请考虑使用VPN服务

## 示例用法

### 基本用法

```bash
# 使用默认设置生成总结
python -m video_summary.summarizer my_video.mp4
```

### 指定字幕文件

```bash
# 指定字幕文件
python -m video_summary.summarizer my_video.mp4 --subtitle my_subtitle.srt
```

### 指定输出目录

```bash
# 指定输出目录
python -m video_summary.summarizer my_video.mp4 --output-dir ./summaries
```

### 完整示例

```bash
# 完整示例
python -m video_summary.summarizer my_video.mp4 --subtitle my_subtitle.srt --api-key YOUR_API_KEY --output-dir ./summaries --verbose
```

## 测试

视频总结模块包含完整的单元测试和集成测试，用于确保功能的正确性和稳定性。测试用例位于`test`目录下。

```bash
# 运行视频总结模块测试
python -m unittest test.test_video_summary

# 运行实际调用API的测试
python -m unittest test.test_video_summary.TestVideoSummary.test_real_video_summary
```

详细的测试说明请参阅[测试文档](../test/README.md)。