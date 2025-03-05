#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕处理器：组合字幕提取和翻译功能
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import glob
import re
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('subtitle_processor')

# 支持的字幕格式
SUBTITLE_FORMATS = ['srt', 'vtt', 'txt']

# 全局参数，由 process_subtitles 函数设置
whisper_model = "base"
whisper_language = "en"
output_formats = None
keep_extracted_audio = False

from subtitle_extractor.whisper_subtitle_extractor import extract_subtitles as extract_subtitles_raw
from subtitle_translator.translator import get_translator
from subtitle_burner import burn_subtitles_to_video, select_subtitle_file

def process_subtitles(video_path: str, model: str = "base", language: str = "en",
                     output: Optional[str] = None, formats: Optional[List[str]] = None,
                     keep_audio: bool = False, subtitle_type: str = "translated",
                     dest_language: str = "zh-CN", api_key: Optional[str] = None,
                     burn_subtitles: bool = False, font_size: int = 28,
                     subtitle_position: str = "bottom", font_color: str = "white",
                     outline_color: str = "black") -> bool:
    """
    处理视频字幕：提取并可选翻译

    Args:
        video_path: 视频文件路径
        model: Whisper模型大小
        language: 指定源语言代码 (默认: en, 英语)
        output: 输出文件路径或目录
        formats: 输出格式列表
        keep_audio: 是否保留提取的音频文件
        subtitle_type: 字幕类型 (original, translated, bilingual)
        dest_language: 目标翻译语言 (默认: zh-CN，中文)
        api_key: Gemini API密钥
        burn_subtitles: 是否将字幕烧录到视频中
        font_size: 烧录字幕的字体大小
        subtitle_position: 烧录字幕的位置 (bottom, top, middle)
        font_color: 烧录字幕的字体颜色
        outline_color: 烧录字幕的轮廓颜色

    Returns:
        成功返回True，失败返回False
    """
    try:
        # 打印当前使用的字幕类型
        subtitle_type_names = {
            "original": "原始语言",
            "translated": "翻译后",
            "bilingual": "双语"
        }
        logger.info(f"开始处理视频字幕: {video_path}")
        logger.info(f"字幕类型: {subtitle_type_names.get(subtitle_type, subtitle_type)}")
        logger.info(f"源语言: {language}, 目标语言: {dest_language}")
        logger.info(f"使用模型: {model}")
        print(f"字幕类型: {subtitle_type_names.get(subtitle_type, subtitle_type)}")

        # 确定输出目录
        if output:
            if os.path.isdir(output):
                output_dir = output
            else:
                output_dir = os.path.dirname(output)
        else:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 设置全局参数，供 extract_subtitle 函数使用
        global whisper_model, whisper_language, output_formats, keep_extracted_audio
        whisper_model = model
        whisper_language = language
        output_formats = formats
        keep_extracted_audio = keep_audio

        # 使用 process_video 函数处理视频和字幕
        subtitle_files = process_video(video_path, subtitle_type, output_dir, dest_language)

        # 如果需要烧录字幕到视频中
        if burn_subtitles and subtitle_files:
            logger.info(f"开始将字幕烧录到视频中")
            logger.info(f"字体大小: {font_size}, 位置: {subtitle_position}")

            # 使用字幕烧录模块的select_subtitle_file函数选择合适的字幕文件
            subtitle_file = select_subtitle_file(subtitle_files, subtitle_type)

            # 如果找到合适的字幕文件，进行烧录
            if subtitle_file:
                logger.info(f"选择字幕文件进行烧录: {subtitle_file}")
                output_video = burn_subtitles_to_video(
                    video_path,
                    subtitle_file,
                    output_path=output_dir,
                    font_size=font_size,
                    position=subtitle_position,
                    font_color=font_color,
                    outline_color=outline_color
                )
                if output_video:
                    logger.info(f"字幕烧录成功，输出视频: {output_video}")
                else:
                    logger.error("字幕烧录失败")
            else:
                logger.error(f"未找到合适的字幕文件进行烧录")

        logger.info("所有字幕处理完成")
        return True

    except Exception as e:
        logger.exception(f"处理字幕时出错: {e}")
        print(f"处理字幕时出错: {e}")
        return False

def translate_subtitle_file(file_path: str, subtitle_type: str = "translated", dest_language: str = "zh-CN", src_language: str = "auto", api_key: Optional[str] = None, output_path: Optional[str] = None):
    """
    翻译字幕文件

    Args:
        file_path: 字幕文件路径
        subtitle_type: 字幕类型 (translated 或 bilingual)
        dest_language: 目标语言
        src_language: 源语言，默认为auto（自动检测）
        api_key: Gemini API密钥
        output_path: 输出文件路径，如果为None则自动生成

    Returns:
        翻译后的字幕文件路径
    """
    logger.info(f"开始处理字幕文件: {file_path}")
    logger.info(f"字幕类型: {subtitle_type}, 源语言: {src_language}, 目标语言: {dest_language}")

    try:
        # 初始化翻译器
        translator = get_translator(api_key)
    except ValueError as e:
        error_msg = f"无法初始化翻译器: {e}"
        logger.error(error_msg)
        print(error_msg)
        return file_path

    # 读取原始字幕文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    logger.info(f"读取字幕文件，内容长度: {len(content)} 字符")

    # 检查文件是否为标准SRT格式
    is_standard_srt = False
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.srt':
        # 简单检查是否包含时间戳格式 (00:00:00,000 --> 00:00:00,000)
        if re.search(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', content):
            is_standard_srt = True
            logger.info("检测到标准SRT格式")
        else:
            logger.warning("SRT文件格式不标准，缺少时间戳")

    # 解析字幕内容
    if is_standard_srt:
        logger.info("解析SRT格式字幕")
        segments = parse_srt(content)
    elif ext == '.srt' and not is_standard_srt:
        # 非标准SRT格式，按行解析
        logger.info("解析非标准SRT格式字幕")
        segments = []
        lines = content.strip().split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                # 创建一个伪时间戳
                time_str = f"00:00:{i:02d},000 --> 00:00:{i+1:02d},000"
                segments.append({
                    'time': time_str,
                    'text': line
                })
    elif ext == '.vtt':
        logger.info("解析VTT格式字幕")
        segments = parse_vtt(content)
    else:  # .txt
        logger.info("解析TXT格式字幕")
        segments = [{'text': line} for line in content.split('\n') if line.strip()]
    logger.info(f"解析出 {len(segments)} 个字幕片段")

    # 根据字幕类型决定翻译方式
    if subtitle_type == 'translated':
        # 整体翻译，保持时间戳对齐
        try:
            logger.info(f"准备整体翻译带时间戳的字幕，共 {len(segments)} 个片段")

            # 构建带时间戳的原始字幕文本
            formatted_subtitle = ""
            for i, segment in enumerate(segments):
                if 'time' in segment and 'text' in segment:
                    # 添加序号、时间戳和文本
                    formatted_subtitle += f"{i+1}\n{segment['time']}\n{segment['text']}\n\n"
                elif 'text' in segment:
                    # 只有文本，没有时间戳
                    formatted_subtitle += f"{segment['text']}\n"

            logger.info(f"构建了带时间戳的字幕文本，长度: {len(formatted_subtitle)} 字符")

            # 构建翻译提示，强调保持时间戳对齐和段落结构
            translation_prompt = f"""请将以下字幕翻译成{dest_language}，必须严格保持原始格式、时间戳和段落结构。
每个字幕片段包含三部分：序号、时间戳和文本。
只翻译文本部分，保持序号和时间戳不变。
非常重要：必须保持原始字幕的段落结构，每个片段单独翻译，不要合并或分割片段。
即使某些句子在语义上是连续的，也必须按照原始字幕的分段进行翻译。
返回完整的翻译后字幕文件，包含所有序号和时间戳。

{formatted_subtitle}"""

            # 发送整体翻译请求
            translated_full_text = translator.translate(translation_prompt, 'auto', dest_language)

            # 检查翻译结果
            if not translated_full_text or translated_full_text == formatted_subtitle:
                logger.warning("整体翻译失败，将使用原文")
                print("警告: 翻译失败，将使用原始文本。请检查API密钥和网络连接。")
                # 使用原文作为翻译结果
                for segment in segments:
                    if 'text' in segment:
                        segment['translated'] = segment['text']
            else:
                logger.info("整体翻译成功，开始解析翻译结果")

                # 解析翻译后的字幕文本，提取翻译后的文本部分
                try:
                    # 尝试解析翻译后的SRT格式文本
                    translated_segments = parse_srt(translated_full_text)

                    # 检查解析后的片段数量是否与原始片段匹配
                    if len(translated_segments) == len(segments):
                        logger.info("翻译后的片段数量与原始片段匹配")
                        # 将翻译后的文本分配给原始片段
                        for i, segment in enumerate(segments):
                            if i < len(translated_segments) and 'text' in translated_segments[i]:
                                segment['translated'] = translated_segments[i]['text']
                            else:
                                segment['translated'] = segment.get('text', '')
                    else:
                        logger.warning(f"翻译后的片段数量不匹配: 原始 {len(segments)}, 翻译后 {len(translated_segments)}")
                        # 尝试按顺序匹配尽可能多的片段
                        for i, segment in enumerate(segments):
                            if i < len(translated_segments) and 'text' in translated_segments[i]:
                                segment['translated'] = translated_segments[i]['text']
                            else:
                                segment['translated'] = segment.get('text', '')
                except Exception as e:
                    logger.warning(f"解析翻译结果时出错: {e}")
                    # 回退到简单的行分割方法
                    lines = translated_full_text.strip().split('\n')
                    text_lines = []

                    # 提取文本行（跳过序号和时间戳行）
                    i = 0
                    while i < len(lines):
                        if i + 2 < len(lines) and re.match(r'\d+', lines[i]) and re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', lines[i+1]):
                            # 这是一个文本行
                            text_lines.append(lines[i+2])
                            i += 4  # 跳过空行
                        else:
                            i += 1

                    # 将提取的文本行分配给原始片段
                    for i, segment in enumerate(segments):
                        if i < len(text_lines):
                            segment['translated'] = text_lines[i]
                        else:
                            segment['translated'] = segment.get('text', '')

                logger.info("翻译结果解析和分配完成")
        except Exception as e:
            logger.exception(f"翻译过程中出错: {e}")
            print(f"翻译文本时出错: {e}")
            # 使用原文作为翻译结果
            for segment in segments:
                if 'text' in segment:
                    segment['translated'] = segment['text']

    elif subtitle_type == 'bilingual':
        # 对于双语字幕，需要翻译
        logger.info(f"正在为双语字幕翻译文本到 {dest_language}")
        try:
            # 提取所有文本段落
            text_segments = [segment['text'] for segment in segments if 'text' in segment]

            # 构建格式化的字幕文本，包含序号、时间戳和文本
            formatted_subtitle = ""
            for i, segment in enumerate(segments, 1):
                formatted_subtitle += f"{i}\n{segment['time']}\n{segment['text']}\n\n"

            # 创建翻译提示
            translation_prompt = f"""
            请将以下字幕文本翻译成{dest_language}。
            请严格保持原始格式和时间戳，只翻译文本内容。
            每个字幕段落必须单独翻译，不要合并或拆分段落。
            保持原始段落数量不变。

            {formatted_subtitle}
            """

            # 发送翻译请求
            translated_full_text = translator.translate(translation_prompt, dest_language)

            if not translated_full_text or translated_full_text.strip() == "":
                logger.warning("翻译结果为空，将使用原文")
                for segment in segments:
                    if 'text' in segment:
                        segment['translated'] = segment['text']
            else:
                logger.info("成功获取翻译结果，正在解析...")

                try:
                    # 尝试解析翻译结果
                    translated_segments = parse_srt(translated_full_text)

                    # 确保翻译后的段落数量与原始段落数量一致
                    if len(translated_segments) == len(segments):
                        for i, segment in enumerate(segments):
                            if 'text' in segment:
                                segment['translated'] = translated_segments[i]['text']
                    else:
                        logger.warning(f"翻译后段落数量不匹配: 原始 {len(segments)}, 翻译后 {len(translated_segments)}")
                        # 尝试匹配尽可能多的段落
                        for i, segment in enumerate(segments):
                            if i < len(translated_segments) and 'text' in segment:
                                segment['translated'] = translated_segments[i]['text']
                            elif 'text' in segment:
                                segment['translated'] = segment['text']
                except Exception as e:
                    logger.warning(f"解析翻译结果时出错: {e}")
                    # 回退到使用原文
                    for segment in segments:
                        if 'text' in segment:
                            segment['translated'] = segment['text']
        except Exception as e:
            logger.exception(f"双语字幕翻译过程中出错: {e}")
            print(f"翻译双语字幕时出错: {e}")
            # 使用原文作为翻译结果
            for segment in segments:
                if 'text' in segment:
                    segment['translated'] = segment['text']

    elif subtitle_type == 'original':
        # 对于原始字幕，不需要翻译，也不需要'translated'字段
        # 但为了保持一致性，我们仍然添加'translated'字段，值与'text'相同
        logger.info("字幕类型为原始语言，不进行翻译")
        for segment in segments:
            if 'text' in segment:
                segment['translated'] = segment['text']

    # 生成新的字幕文件
    if output_path:
        new_path = output_path
        logger.info(f"使用指定的输出路径: {new_path}")
    else:
        dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        # 分析文件名结构
        parts = file_name.split('.')
        ext_without_dot = parts[-1]  # 获取扩展名（不包括点号）

        # 提取基本名称（不包含语言代码和扩展名）
        # 检查是否有语言代码或bilingual标记
        if len(parts) > 2:
            # 可能的语言代码或bilingual标记在倒数第二个位置
            possible_lang = parts[-2]
            # 检查是否为语言代码或bilingual标记
            if possible_lang == 'bilingual' or re.match(r'^[a-z]{2}(-[A-Z]{2})?$', possible_lang):
                # 基本名称不包含语言代码/bilingual标记和扩展名
                base_name = '.'.join(parts[:-2])
                logger.info(f"检测到语言代码或bilingual标记: {possible_lang}, 基本名称: {base_name}")
            else:
                # 没有语言代码或bilingual标记
                base_name = '.'.join(parts[:-1])
        else:
            # 没有语言代码或bilingual标记
            base_name = '.'.join(parts[:-1])

        logger.info(f"文件名基本名称: {base_name}")

        # 构建新的文件名
        if subtitle_type == 'translated':
            new_file_name = f"{base_name}.{dest_language}.{ext_without_dot}"
        elif subtitle_type == 'bilingual':
            new_file_name = f"{base_name}.bilingual.{ext_without_dot}"
        else:  # original
            new_file_name = f"{base_name}.{ext_without_dot}"

        # 完整的新路径
        new_path = os.path.join(dir_path, new_file_name)
        logger.info(f"生成新的字幕文件: {new_path}")

    # 写入翻译后的内容
    with open(new_path, 'w', encoding='utf-8') as f:
        if ext == '.srt':
            logger.info("写入SRT格式字幕")
            write_srt(f, segments, subtitle_type)
        elif ext == '.vtt':
            logger.info("写入VTT格式字幕")
            write_vtt(f, segments, subtitle_type)
        else:  # .txt
            logger.info("写入TXT格式字幕")
            write_txt(f, segments, subtitle_type)
    logger.info(f"字幕文件已保存: {new_path}")

    return new_path

def parse_srt(content: str) -> List[Dict[str, str]]:
    """解析SRT格式字幕"""
    segments = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        # 跳过序号
        i += 1
        if i >= len(lines):
            break
        # 获取时间轴
        time_line = lines[i]
        i += 1
        # 获取文本
        text = []
        while i < len(lines) and lines[i].strip():
            text.append(lines[i])
            i += 1
        segments.append({
            'time': time_line,
            'text': '\\n'.join(text)
        })
        i += 1
    return segments

def parse_vtt(content: str) -> List[Dict[str, str]]:
    """解析VTT格式字幕"""
    segments = []
    lines = content.strip().split('\n')
    # 跳过WEBVTT头部
    i = 1
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        # 获取时间轴
        time_line = lines[i]
        i += 1
        # 获取文本
        text = []
        while i < len(lines) and lines[i].strip():
            text.append(lines[i])
            i += 1
        segments.append({
            'time': time_line,
            'text': '\\n'.join(text)
        })
        i += 1
    return segments

def write_srt(f, segments: List[Dict[str, str]], subtitle_type: str):
    """写入SRT格式字幕"""
    for i, segment in enumerate(segments, 1):
        f.write(f"{i}\n")
        f.write(f"{segment['time']}\n")
        if subtitle_type == 'original':
            # 对于原始字幕，直接使用text字段
            text = segment['text'].replace('\\n', '\n')
            f.write(f"{text}\n")
        elif subtitle_type == 'translated':
            translated_text = segment['translated'].replace('\\n', '\n')
            f.write(f"{translated_text}\n")
        else:  # bilingual
            text = segment['text'].replace('\\n', '\n')
            translated = segment['translated'].replace('\\n', '\n')
            f.write(f"{text}\n")
            f.write(f"{translated}\n")
        f.write("\n")

def write_vtt(f, segments: List[Dict[str, str]], subtitle_type: str):
    """写入VTT格式字幕"""
    f.write("WEBVTT\n\n")
    for i, segment in enumerate(segments, 1):
        f.write(f"{i}\n")
        f.write(f"{segment['time']}\n")
        if subtitle_type == 'original':
            # 对于原始字幕，直接使用text字段
            text = segment['text'].replace('\\n', '\n')
            f.write(f"{text}\n")
        elif subtitle_type == 'translated':
            translated_text = segment['translated'].replace('\\n', '\n')
            f.write(f"{translated_text}\n")
        else:  # bilingual
            text = segment['text'].replace('\\n', '\n')
            translated = segment['translated'].replace('\\n', '\n')
            f.write(f"{text}\n")
            f.write(f"{translated}\n")
        f.write("\n")

def write_txt(f, segments: List[Dict[str, str]], subtitle_type: str):
    """写入TXT格式字幕"""
    for segment in segments:
        if subtitle_type == 'original':
            # 对于原始字幕，直接使用text字段
            text = segment['text'].replace('\\n', '\n')
            f.write(f"{text}\n")
        elif subtitle_type == 'translated':
            translated_text = segment['translated'].replace('\\n', '\n')
            f.write(f"{translated_text}\n")
        else:  # bilingual
            text = segment['text'].replace('\\n', '\n')
            translated = segment['translated'].replace('\\n', '\n')
            f.write(f"{text}\n")
            f.write(f"{translated}\n")
            f.write("\n")

def find_subtitle_files(video_path, output_dir=None):
    """查找与视频相关的字幕文件"""
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(video_path)

    # 获取视频文件的基本名称（不含扩展名）
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]
    logger.info(f"视频基本名称: {video_base_name}")

    # 使用glob模式查找所有可能的字幕文件
    subtitle_files = []
    for ext in SUBTITLE_FORMATS:
        # 查找格式: base_name.*.ext (包含语言代码或bilingual标记)
        pattern = os.path.join(output_dir, f"{video_base_name}.*.{ext}")
        files = glob.glob(pattern)
        subtitle_files.extend(files)

        # 查找格式: base_name.ext (无语言代码)
        pattern = os.path.join(output_dir, f"{video_base_name}.{ext}")
        files = glob.glob(pattern)
        subtitle_files.extend(files)

    logger.info(f"找到的字幕文件: {subtitle_files}")
    return subtitle_files

def process_video(video_path, subtitle_type='original', output_dir=None, dest_language='zh-CN'):
    """处理视频，提取并处理字幕"""
    if output_dir is None:
        output_dir = os.path.dirname(video_path)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 提取字幕
    subtitle_file = extract_subtitle(video_path, output_dir, subtitle_type, dest_language)

    processed_files = []

    if subtitle_file:
        logger.info(f"成功提取字幕到: {subtitle_file}")
        processed_files.append(subtitle_file)

        # 查找所有相关的字幕文件
        all_subtitle_files = find_subtitle_files(video_path, output_dir)
        logger.info(f"找到的所有字幕文件: {all_subtitle_files}")

        # 处理每个字幕文件
        for sub_file in all_subtitle_files:
            # 处理字幕文件（包括重命名或翻译）
            processed_file = translate_subtitle_file(sub_file, subtitle_type, dest_language)
            logger.info(f"处理后的字幕文件: {processed_file}")
            if processed_file and processed_file not in processed_files:
                processed_files.append(processed_file)

        return processed_files
    else:
        logger.error("无法提取字幕")
        return []

def extract_subtitle(video_path, output_dir=None, subtitle_type='original', dest_language='zh-CN'):
    """
    从视频中提取字幕

    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        subtitle_type: 字幕类型 (original, translated, bilingual)
        dest_language: 目标语言

    Returns:
        提取的字幕文件路径，如果失败则返回None
    """
    global whisper_model, whisper_language, output_formats, keep_extracted_audio

    if output_dir is None:
        output_dir = os.path.dirname(video_path)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取视频文件的基本名称（不含扩展名）
    video_base_name = os.path.splitext(os.path.basename(video_path))[0]

    # 构建输出文件路径
    output_path = os.path.join(output_dir, f"{video_base_name}")

    # 调用 extract_subtitles_raw 函数提取字幕
    try:
        # 如果没有设置全局格式，使用默认格式
        formats = output_formats
        if formats is None:
            # 获取默认设置
            from utils.config import get_default_settings
            default_settings = get_default_settings()
            formats = default_settings['output_format'].split(',')

        # 提取字幕
        result = extract_subtitles_raw(
            video_path,
            model=whisper_model,
            language=whisper_language,
            output=output_path,
            formats=formats,
            keep_audio=keep_extracted_audio,
            dest_language=dest_language
        )

        if result:
            # 查找生成的字幕文件
            for ext in SUBTITLE_FORMATS:
                subtitle_file = f"{output_path}.{ext}"
                if os.path.exists(subtitle_file):
                    logger.info(f"找到提取的字幕文件: {subtitle_file}")
                    return subtitle_file

            # 如果没有找到默认格式的字幕文件，尝试查找带语言代码的文件
            for ext in SUBTITLE_FORMATS:
                pattern = f"{output_path}.*.{ext}"
                files = glob.glob(pattern)
                if files:
                    logger.info(f"找到提取的字幕文件: {files[0]}")
                    return files[0]

        logger.error("未能找到提取的字幕文件")
        return None
    except Exception as e:
        logger.exception(f"提取字幕时出错: {e}")
        return None
