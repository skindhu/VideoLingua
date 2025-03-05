#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频总结生成器

该模块负责读取视频的字幕文件，调用Gemini API总结视频内容，
并输出为一个与视频同名的Markdown文件。
"""

import os
import sys
import logging
from typing import Optional, List, Dict
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('video_summarizer')

# 添加项目根目录到路径，确保可以导入utils模块
sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_api import get_gemini_api
from subtitle_processor import parse_srt, parse_vtt

def read_subtitle_file(subtitle_path: str) -> str:
    """
    读取字幕文件内容

    Args:
        subtitle_path: 字幕文件路径

    Returns:
        字幕文件内容
    """
    logger.info(f"读取字幕文件: {subtitle_path}")

    if not os.path.exists(subtitle_path):
        logger.error(f"字幕文件不存在: {subtitle_path}")
        raise FileNotFoundError(f"字幕文件不存在: {subtitle_path}")

    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        logger.exception(f"读取字幕文件失败: {e}")
        raise

def extract_text_from_subtitle(subtitle_content: str, file_ext: str) -> str:
    """
    从字幕内容中提取纯文本

    Args:
        subtitle_content: 字幕文件内容
        file_ext: 字幕文件扩展名

    Returns:
        提取的纯文本
    """
    logger.info(f"从{file_ext}格式字幕中提取文本")

    # 解析字幕内容
    segments = []
    if file_ext.lower() == '.srt':
        segments = parse_srt(subtitle_content)
    elif file_ext.lower() == '.vtt':
        segments = parse_vtt(subtitle_content)
    elif file_ext.lower() == '.txt':
        # 对于纯文本文件，按行分割
        segments = [{'text': line} for line in subtitle_content.split('\n') if line.strip()]
    else:
        logger.warning(f"不支持的字幕格式: {file_ext}")
        return subtitle_content

    # 提取文本内容
    text_content = []
    for segment in segments:
        if 'text' in segment:
            # 替换特殊的换行符标记
            text = segment['text'].replace('\\n', ' ')
            text_content.append(text)

    return '\n'.join(text_content)

def generate_summary(text_content: str, api_key: Optional[str] = None) -> str:
    """
    使用Gemini API生成视频内容总结

    Args:
        text_content: 字幕文本内容
        api_key: Gemini API密钥

    Returns:
        生成的总结内容
    """
    logger.info("使用Gemini API生成视频内容总结")

    # 获取Gemini API实例
    gemini_api = get_gemini_api(api_key)

    # 构建提示词
    prompt = f"""
请根据以下视频字幕内容，生成一个详细的视频内容总结。请务必使用中文进行总结。总结应该包括：

1. 视频的主要主题和目的
2. 视频中讨论的关键点和重要信息
3. 视频的结构和内容组织
4. 视频中提到的任何重要数据、事实或观点

请以Markdown格式输出，包含适当的标题、小标题和列表。确保总结全面但简洁，突出最重要的信息。
无论原始字幕是什么语言，都请使用中文进行总结。

字幕内容：
{text_content}
"""

    # 调用API生成总结
    try:
        summary = gemini_api.generate_content(prompt, temperature=0.2)
        if not summary:
            logger.error("生成总结失败，API返回空结果")
            return "无法生成视频总结，请检查API密钥和网络连接。"
        return summary
    except Exception as e:
        logger.exception(f"生成总结时出错: {e}")
        return f"生成总结时出错: {e}"

def save_summary_to_markdown(summary: str, output_path: str) -> str:
    """
    将总结内容保存为Markdown文件

    Args:
        summary: 总结内容
        output_path: 输出文件路径

    Returns:
        保存的文件路径
    """
    logger.info(f"保存总结到Markdown文件: {output_path}")

    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        logger.info(f"总结已保存到: {output_path}")
        return output_path
    except Exception as e:
        logger.exception(f"保存总结文件失败: {e}")
        raise

def summarize_video_from_subtitle(video_path: str, subtitle_path: Optional[str] = None,
                                 api_key: Optional[str] = None, output_dir: Optional[str] = None) -> str:
    """
    根据视频的字幕文件生成视频内容总结

    Args:
        video_path: 视频文件路径
        subtitle_path: 字幕文件路径，如果为None，则尝试查找同名字幕文件
        api_key: Gemini API密钥
        output_dir: 输出目录，如果为None，则使用视频所在目录

    Returns:
        生成的总结文件路径
    """
    logger.info(f"开始为视频生成内容总结: {video_path}")

    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        logger.error(f"视频文件不存在: {video_path}")
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    # 如果未提供字幕文件，尝试查找同名字幕文件
    if subtitle_path is None:
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]

        # 尝试查找常见字幕格式
        for ext in ['.srt', '.vtt', '.txt']:
            potential_path = os.path.join(video_dir, f"{video_name}{ext}")
            if os.path.exists(potential_path):
                subtitle_path = potential_path
                logger.info(f"找到字幕文件: {subtitle_path}")
                break

        if subtitle_path is None:
            logger.error(f"未找到视频对应的字幕文件: {video_path}")
            raise FileNotFoundError(f"未找到视频对应的字幕文件: {video_path}")

    # 确定输出目录和文件名
    if output_dir is None:
        output_dir = os.path.dirname(video_path)

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, f"{video_name}_summary.markdown")

    # 读取字幕文件
    subtitle_content = read_subtitle_file(subtitle_path)

    # 提取字幕文本
    file_ext = os.path.splitext(subtitle_path)[1]
    text_content = extract_text_from_subtitle(subtitle_content, file_ext)

    # 生成总结
    summary = generate_summary(text_content, api_key)

    # 保存总结到Markdown文件
    result_path = save_summary_to_markdown(summary, output_path)

    logger.info(f"视频内容总结已生成: {result_path}")
    print(f"✅ 视频内容总结已生成: {result_path}")

    return result_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="根据视频字幕生成内容总结")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("--subtitle", help="字幕文件路径，如果不提供则尝试查找同名字幕文件")
    parser.add_argument("--api-key", help="Gemini API密钥")
    parser.add_argument("--output-dir", help="输出目录")

    args = parser.parse_args()

    try:
        summary_path = summarize_video_from_subtitle(
            args.video_path,
            args.subtitle,
            args.api_key,
            args.output_dir
        )
        print(f"视频内容总结已保存到: {summary_path}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)