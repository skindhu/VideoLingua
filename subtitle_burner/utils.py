#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕烧录工具的辅助函数
"""

import os
import logging
from typing import List, Optional

# 配置日志
logger = logging.getLogger('subtitle_burner.utils')

def select_subtitle_file(subtitle_files: List[str], subtitle_type: str) -> Optional[str]:
    """
    根据字幕类型选择合适的字幕文件

    Args:
        subtitle_files: 字幕文件列表
        subtitle_type: 字幕类型 (original, translated, bilingual)

    Returns:
        选择的字幕文件路径，如果没有找到合适的文件则返回None
    """
    if not subtitle_files:
        return None

    for file in subtitle_files:
        # 根据字幕类型选择合适的字幕文件
        if subtitle_type == "original" and ".srt" in file and not ".zh-CN." in file and not ".bilingual." in file:
            logger.info(f"选择原始字幕文件: {file}")
            return file
        elif subtitle_type == "translated" and ".zh-CN.srt" in file:
            logger.info(f"选择翻译字幕文件: {file}")
            return file
        elif subtitle_type == "bilingual" and ".bilingual.srt" in file:
            logger.info(f"选择双语字幕文件: {file}")
            return file

    # 如果没有找到完全匹配的文件，尝试使用第一个.srt文件
    for file in subtitle_files:
        if file.endswith(".srt"):
            logger.warning(f"未找到完全匹配{subtitle_type}类型的字幕文件，使用: {file}")
            return file

    logger.error(f"未找到任何可用的字幕文件")
    return None