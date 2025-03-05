#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频总结模块

该模块负责根据视频的字幕文件，调用Gemini API总结视频内容，
并输出为一个与视频同名的Markdown文件。
"""

from .summarizer import summarize_video_from_subtitle

__all__ = ['summarize_video_from_subtitle']