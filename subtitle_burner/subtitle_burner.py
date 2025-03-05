#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕烧录工具：将字幕烧录到视频中
"""

import os
import re
import logging
from shutil import which
import subprocess
from typing import Optional

# 配置日志
logger = logging.getLogger('subtitle_burner')

def burn_subtitles_to_video(video_path: str, subtitle_path: str, output_path: Optional[str] = None,
                           font_size: int = 28, position: str = "bottom",
                           font_color: str = "white", outline_color: str = "black",
                           shadow_radius: int = 1) -> Optional[str]:
    """
    将字幕烧录到视频中

    Args:
        video_path: 视频文件路径
        subtitle_path: 字幕文件路径
        output_path: 输出视频文件路径，如果为None则自动生成
        font_size: 字幕字体大小
        position: 字幕位置，可选值: bottom, top, middle
        font_color: 字体颜色
        outline_color: 字体轮廓颜色
        shadow_radius: 字幕阴影半径，默认为1

    Returns:
        成功返回输出视频路径，失败返回None
    """
    # 检查FFmpeg是否安装
    if not which("ffmpeg"):
        error_msg = "未找到FFmpeg，请先安装FFmpeg"
        logger.error(error_msg)
        print(error_msg)
        return None

    # 确定输出路径
    if output_path is None:
        # 获取视频文件信息
        video_dir = os.path.dirname(video_path)
        video_name = os.path.basename(video_path)
        video_name_without_ext, video_ext = os.path.splitext(video_name)

        # 从字幕文件名中提取字幕类型信息
        subtitle_name = os.path.basename(subtitle_path)
        subtitle_parts = subtitle_name.split('.')

        # 检查是否包含语言代码或bilingual标记
        subtitle_type_marker = ""
        if len(subtitle_parts) > 2:
            possible_marker = subtitle_parts[-2]
            if possible_marker == 'bilingual' or re.match(r'^[a-z]{2}(-[A-Z]{2})?$', possible_marker):
                subtitle_type_marker = f".{possible_marker}"

        # 使用与视频相同的目录
        output_path = os.path.join(video_dir, f"{video_name_without_ext}{subtitle_type_marker}.hardcoded{video_ext}")
    elif os.path.isdir(output_path):
        # 如果output_path是目录，则在该目录下使用视频文件名
        video_name = os.path.basename(video_path)
        video_name_without_ext, video_ext = os.path.splitext(video_name)

        # 从字幕文件名中提取字幕类型信息
        subtitle_name = os.path.basename(subtitle_path)
        subtitle_parts = subtitle_name.split('.')

        # 检查是否包含语言代码或bilingual标记
        subtitle_type_marker = ""
        if len(subtitle_parts) > 2:
            possible_marker = subtitle_parts[-2]
            if possible_marker == 'bilingual' or re.match(r'^[a-z]{2}(-[A-Z]{2})?$', possible_marker):
                subtitle_type_marker = f".{possible_marker}"

        output_path = os.path.join(output_path, f"{video_name_without_ext}{subtitle_type_marker}.hardcoded{video_ext}")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        logger.info(f"开始将字幕烧录到视频中: {video_path}")
        logger.info(f"使用字幕文件: {subtitle_path}")
        logger.info(f"输出视频: {output_path}")
        logger.info(f"字幕设置: 字体大小={font_size}, 位置={position}, 字体颜色={font_color}, 轮廓颜色={outline_color}, 阴影半径={shadow_radius}")

        # 构建FFmpeg命令行字符串
        if position == "top":
            position_param = "y=10"
        elif position == "middle":
            position_param = "y=(h-text_h)/2"
        else:  # bottom
            position_param = "y=h-text_h-10"

        # 颜色转换为FFmpeg ASS格式
        # 颜色映射表
        color_to_hex = {
            "white": "ffffff",
            "black": "000000",
            "yellow": "ffff00",
            "green": "00ff00",
            "cyan": "00ffff",
            "blue": "0000ff",
            "magenta": "ff00ff",
            "red": "ff0000"
        }

        # 获取颜色的十六进制值，如果不在映射表中则使用原值
        font_color_hex = color_to_hex.get(font_color.lower(), font_color)
        outline_color_hex = color_to_hex.get(outline_color.lower(), outline_color)

        # 如果颜色值不是十六进制格式，则使用默认值
        if not re.match(r'^[0-9a-fA-F]{6}$', font_color_hex):
            logger.warning(f"无效的字体颜色值: {font_color}，使用默认值: white")
            font_color_hex = "ffffff"

        if not re.match(r'^[0-9a-fA-F]{6}$', outline_color_hex):
            logger.warning(f"无效的轮廓颜色值: {outline_color}，使用默认值: black")
            outline_color_hex = "000000"

        # 使用shell命令直接执行，避免参数转义问题
        # 设置BorderStyle=1(带轮廓)和Shadow参数(带阴影)，使背景透明
        cmd_str = f'ffmpeg -y -i "{video_path}" -vf "subtitles={subtitle_path}:force_style=\'FontName=Arial,FontSize={font_size},PrimaryColour=&H{font_color_hex},OutlineColour=&H{outline_color_hex},BorderStyle=1,Outline=2,Shadow={shadow_radius},Bold=1\'" -c:v libx264 -crf 18 -c:a copy "{output_path}"'

        logger.info(f"FFmpeg命令: {cmd_str}")

        # 使用shell=True执行命令
        process = subprocess.Popen(
            cmd_str,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # 实时获取输出
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.debug(output.strip())

        # 检查命令执行结果
        if process.returncode == 0:
            logger.info(f"字幕烧录成功，输出文件: {output_path}")
            return output_path
        else:
            logger.error(f"字幕烧录失败，返回码: {process.returncode}")
            return None

    except Exception as e:
        logger.exception(f"烧录字幕时出错: {e}")
        return None