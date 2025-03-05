# 字幕处理工具测试

本目录包含字幕处理工具各模块的测试用例，用于确保功能的正确性和稳定性。

## 测试结构

测试目录结构如下：

```
test/
├── run_all_tests.py                # 运行所有测试的主脚本
├── test_subtitle_processor.py      # 字幕处理器集成测试
├── test_subtitle_extractor.py      # 字幕提取模块测试
├── test_subtitle_translator.py     # 字幕翻译模块测试
├── test_subtitle_burner.py         # 字幕烧录模块测试
├── test_video_summary.py           # 视频总结模块测试
└── test_real_summary.py            # 视频总结实际调用测试
```

## 测试执行顺序

**重要提示：测试用例之间存在依赖关系，必须按照特定顺序执行！**

测试用例的正确执行顺序为：

1. **test_subtitle_extractor.py** - 首先执行字幕提取测试，生成原始字幕文件
2. **test_subtitle_translator.py** - 然后执行字幕翻译测试，使用提取的字幕文件生成翻译后的字幕
3. **test_subtitle_burner.py** - 最后执行字幕烧录测试，使用翻译后的字幕文件生成带字幕的视频
4. **test_video_summary.py** - 视频总结测试可以在任何时候执行，但需要字幕文件存在

这是因为后面的测试依赖于前面测试生成的文件：
- 翻译测试需要使用提取测试生成的字幕文件作为输入
- 烧录测试需要使用翻译测试生成的双语字幕文件作为输入
- 视频总结测试需要使用字幕文件作为输入

如果不按照此顺序执行，测试可能会失败，因为所需的输入文件不存在。

## 运行测试

### 运行所有测试

要按照正确顺序运行所有模块的测试，请执行以下命令：

```bash
# 使用test目录下的run_all_tests.py脚本（推荐）
cd test
python run_all_tests.py

# 或者使用Python模块方式
python -m test.run_all_tests
```

`run_all_tests.py`脚本会按照正确的依赖顺序执行测试，提供彩色输出和详细的测试时间统计。

### 运行单个模块的测试

如果需要单独运行特定模块的测试，请确保按照上述依赖顺序执行：

```bash
# 1. 首先运行字幕提取模块测试
python -m test.test_subtitle_extractor

# 2. 然后运行字幕翻译模块测试
python -m test.test_subtitle_translator

# 3. 最后运行字幕烧录模块测试
python -m test.test_subtitle_burner

# 4. 运行视频总结模块测试
python -m test.test_video_summary

# 集成测试可以在任何时候运行
python -m test.test_subtitle_processor
```

### 运行特定的测试方法

如果只需要运行某个测试类中的特定测试方法，可以使用以下命令：

```bash
# 运行视频总结模块中的实际调用测试
python -m unittest test.test_video_summary.TestVideoSummary.test_real_video_summary
```

## 测试内容

### 字幕提取模块测试

- 测试从视频中提取音频功能
- 测试加载Whisper模型功能
- 测试时间格式化功能
- 测试字幕提取主功能
- **输出文件**: `output/test/Getting_Started_First_App.srt`

### 字幕翻译模块测试

- 测试获取翻译器实例
- 测试SRT格式解析
- 测试VTT格式解析
- 测试字幕文件翻译功能
- 测试字幕写入不同格式
- **输入文件**: `output/test/Getting_Started_First_App.srt`
- **输出文件**:
  - `output/test/Getting_Started_First_App.zh-CN.srt` (翻译字幕)
  - `output/test/Getting_Started_First_App.bilingual.srt` (双语字幕)

### 字幕烧录模块测试

- 测试字幕文件选择功能
- 测试生成FFmpeg命令
- 测试字幕烧录到视频功能
- **输入文件**:
  - `output/test/Getting_Started_First_App.mp4` (原始视频)
  - `output/test/Getting_Started_First_App.bilingual.srt` (双语字幕)
- **输出文件**: `output/test/Getting_Started_First_App.bilingual.hardcoded.mp4` (带字幕的视频)

### 视频总结模块测试

- 测试读取字幕文件功能
- 测试从字幕中提取文本功能
- 测试生成视频总结功能（使用模拟对象）
- 测试保存总结到Markdown文件功能
- 测试视频总结主功能
- 测试实际调用Gemini API生成中文视频总结
- **输入文件**:
  - `output/test/test_demo.mp4` (测试视频)
  - `output/test/test_demo.srt` (测试字幕)
- **输出文件**: `output/test/test_demo_summary.markdown` (视频总结文件)

### 字幕处理器集成测试

- 测试字幕提取功能
- 测试查找字幕文件功能
- 测试视频处理功能
- 测试字幕文件翻译功能
- 测试字幕处理主功能

## 视频总结测试用例用法

### 基本测试用例

`test_video_summary.py` 包含以下测试用例：

1. **test_read_subtitle_file**: 测试读取字幕文件功能
2. **test_extract_text_from_subtitle**: 测试从字幕中提取文本功能
3. **test_generate_summary**: 测试生成视频总结功能（使用模拟对象）
4. **test_save_summary_to_markdown**: 测试保存总结到Markdown文件功能
5. **test_summarize_video_from_subtitle**: 测试视频总结主功能（使用模拟对象）
6. **test_real_video_summary**: 测试实际调用Gemini API生成中文视频总结

### 实际调用测试

`test_real_summary.py` 包含一个专门的测试用例，用于测试实际调用Gemini API生成视频总结：

1. **test_real_summary_generation**: 使用实际的Gemini API生成视频总结，并验证结果

### 运行视频总结测试

```bash
# 运行所有视频总结测试
python -m unittest test_video_summary.py

# 只运行实际调用Gemini API的测试
python -m unittest test_video_summary.TestVideoSummary.test_real_video_summary

# 运行专门的实际调用测试
python -m unittest test_real_summary.py
```

### 测试输出

视频总结测试会在 `output/test` 目录中生成以下文件：

- `test_demo_summary.markdown`: 视频内容总结文件（Markdown格式）

测试会验证生成的总结文件是否存在，内容是否为中文，以及内容是否非空。

## 注意事项

- 测试会在`output/test`目录中生成实际的字幕、视频和总结文件，可以查看这些文件以验证测试结果
- 测试会创建临时文件和目录，测试完成后会自动清理，但生成的字幕、视频和总结文件会保留
- 如果要添加新的测试，请确保遵循现有的测试结构和命名约定
- 确保测试环境中安装了所有必要的依赖，包括FFmpeg（用于字幕烧录测试）
- 视频总结测试需要有效的Gemini API密钥，可以通过环境变量`GEMINI_API_KEY`设置，或者在配置文件中设置