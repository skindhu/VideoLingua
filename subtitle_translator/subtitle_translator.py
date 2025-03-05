#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕翻译模块，用于翻译提取的字幕
"""

from .translator import get_translator

def translate_subtitle_segments(segments, src_lang='auto', dest_lang='zh-CN', api_key=None):
    """
    翻译字幕片段

    Args:
        segments: 字幕片段列表，每个片段应包含text字段
        src_lang: 源语言代码，默认为auto（自动检测）
        dest_lang: 目标语言代码，默认为zh-CN（中文）
        api_key: Gemini API密钥

    Returns:
        翻译后的字幕片段列表，每个片段包含原始文本和翻译文本
    """
    translated_segments = []
    translator = get_translator(api_key)

    print(f"正在翻译字幕...")
    for segment in segments:
        original_text = segment["text"].strip()
        try:
            translated_text = translator.translate(original_text, src_lang, dest_lang)
        except Exception as e:
            print(f"翻译时出错: {e}")
            translated_text = original_text

        translated_segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "original": original_text,
            "translated": translated_text
        })

    return translated_segments

def generate_subtitles(result, subtitle_type='original', src_lang=None, dest_lang='zh-CN', api_key=None):
    """
    根据字幕类型生成不同格式的字幕内容

    Args:
        result: Whisper转录结果
        subtitle_type: 字幕类型，可以是 'original'(原始语言), 'translated'(翻译语言) 或 'bilingual'(双语)
        src_lang: 源语言，如果为None则自动检测
        dest_lang: 目标语言，默认为中文
        api_key: Gemini API密钥

    Returns:
        字幕数据，包含原始片段和翻译片段（如果需要）
    """
    subtitle_data = {
        "segments": result["segments"],
        "translated_segments": None,
        "language": result.get("language", "unknown")
    }

    # 如果需要翻译，准备翻译后的文本
    if subtitle_type in ['translated', 'bilingual']:
        subtitle_data["translated_segments"] = translate_subtitle_segments(
            result["segments"],
            src_lang,
            dest_lang,
            api_key
        )

    return subtitle_data
