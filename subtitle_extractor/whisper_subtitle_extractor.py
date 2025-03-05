#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用OpenAI的Whisper模型从视频文件中提取字幕
"""

import os
import argparse
import whisper
import torch
from tqdm import tqdm
import ffmpeg
import numpy as np
import time
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

def extract_audio_from_video(video_path, output_path=None):
    """从视频文件中提取音频"""
    if output_path is None:
        output_path = os.path.splitext(video_path)[0] + ".wav"

    try:
        # 使用ffmpeg提取音频
        (
            ffmpeg
            .input(video_path)
            .output(output_path, acodec='pcm_s16le', ac=1, ar='16k')
            .run(quiet=True, overwrite_output=True)
        )
        print(f"音频已提取到: {output_path}")
        return output_path
    except ffmpeg.Error as e:
        print(f"提取音频时出错: {e.stderr.decode()}")
        return None

def load_whisper_model(model_name="base"):
    """加载Whisper模型"""
    print(f"正在加载Whisper模型 ({model_name})...")
    try:
        # 检查是否有GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            print("警告: 未检测到GPU，使用CPU进行处理可能会很慢")
        else:
            print(f"使用GPU: {torch.cuda.get_device_name(0)}")

        # 加载模型
        model = whisper.load_model(model_name, device=device)
        print(f"模型加载完成: {model_name}")
        return model
    except Exception as e:
        print(f"加载模型时出错: {e}")
        return None

def transcribe_audio(model, audio_path, language=None):
    """使用Whisper模型转录音频"""
    print(f"开始转录音频: {audio_path}")
    start_time = time.time()

    try:
        # 转录选项
        options = {}
        if language:
            options["language"] = language

        # 执行转录
        result = model.transcribe(audio_path, **options)

        elapsed_time = time.time() - start_time
        print(f"转录完成，用时: {elapsed_time:.2f}秒")
        return result
    except Exception as e:
        print(f"转录音频时出错: {e}")
        return None

def save_subtitles(result, output_path=None, formats=None, src_lang="en", dest_lang="zh-CN", api_key=None):
    """保存字幕到文件

    Args:
        result: Whisper转录结果
        output_path: 输出文件路径（不包含扩展名）
        formats: 输出格式列表
        src_lang: 源语言，默认为英语
        dest_lang: 目标语言，默认为中文
        api_key: API密钥（用于翻译服务）
    """
    if output_path is None:
        raise ValueError("必须提供输出路径")

    if formats is None:
        formats = ["srt", "vtt", "txt"]

    # 不再需要分离扩展名，因为output_path已经不包含扩展名
    base_path = output_path
    saved_files = []

    try:
        # 保存SRT格式
        if "srt" in formats:
            srt_path = f"{base_path}.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], 1):
                    # 转换时间格式 (秒 -> HH:MM:SS,mmm)
                    start_time = format_time(segment["start"])
                    end_time = format_time(segment["end"])

                    text = segment["text"].strip()

                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")

            saved_files.append(srt_path)
            print(f"SRT字幕已保存到: {srt_path}")

        # 保存VTT格式
        if "vtt" in formats:
            vtt_path = f"{base_path}.vtt"
            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
                for i, segment in enumerate(result["segments"], 1):
                    # 转换时间格式 (秒 -> HH:MM:SS.mmm)
                    start_time = format_time(segment["start"], vtt=True)
                    end_time = format_time(segment["end"], vtt=True)

                    text = segment["text"].strip()

                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")

            saved_files.append(vtt_path)
            print(f"VTT字幕已保存到: {vtt_path}")

        # 保存纯文本格式
        if "txt" in formats:
            txt_path = f"{base_path}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
            saved_files.append(txt_path)
            print(f"文本已保存到: {txt_path}")

        # 保存JSON格式（包含所有信息，便于后续处理）
        if "json" in formats:
            json_path = f"{base_path}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json_data = result
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            saved_files.append(json_path)
            print(f"JSON数据已保存到: {json_path}")

        return saved_files
    except Exception as e:
        print(f"保存字幕时出错: {e}")
        return []

def format_time(seconds, vtt=False):
    """将秒数转换为字幕时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60

    if vtt:
        # VTT格式: HH:MM:SS.mmm
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ".")
    else:
        # SRT格式: HH:MM:SS,mmm
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")

def extract_subtitles(video_path, model="base", language="en", output=None, formats=None, keep_audio=False, dest_language="zh-CN", api_key=None, burn_subtitles=False, font_size=28, subtitle_position="bottom", font_color="white", outline_color="black"):
    """
    从视频中提取字幕的主要API函数

    Args:
        video_path: 视频文件路径
        model: Whisper模型大小 (tiny, base, small, medium, large)
        language: 指定源语言代码 (默认: en, 英语)
        output: 输出文件路径或目录
        formats: 输出格式列表 (例如: ["srt", "vtt", "txt"])
        keep_audio: 是否保留提取的音频文件
        dest_language: 目标翻译语言 (默认: zh-CN，中文)
        api_key: Gemini API密钥
        burn_subtitles: 是否将字幕烧录到视频中
        font_size: 字幕字体大小
        subtitle_position: 字幕位置 (bottom, top, middle)
        font_color: 字幕字体颜色
        outline_color: 字幕轮廓颜色

    Returns:
        bool: 操作是否成功
    """
    try:
        # 处理输出路径
        if output is None:
            # 默认输出到与视频相同的目录
            output_dir = os.path.dirname(video_path)
            output_base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(output_dir, output_base)
        elif os.path.isdir(output):
            # 如果output是目录，则在该目录下使用视频文件名
            output_base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(output, output_base)
        else:
            # 如果output是文件路径，则直接使用
            output_path = os.path.splitext(output)[0]

        # 提取音频
        audio_path = extract_audio_from_video(video_path)
        if not audio_path:
            print("提取音频失败，无法继续处理")
            return False

        # 加载模型
        whisper_model = load_whisper_model(model)
        if not whisper_model:
            print("加载模型失败，无法继续处理")
            if not keep_audio and audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            return False

        # 转录音频
        result = transcribe_audio(whisper_model, audio_path, language)
        if not result:
            print("转录音频失败，无法继续处理")
            if not keep_audio and audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            return False

        # 保存字幕
        saved_files = save_subtitles(
            result,
            output_path,
            formats,
            src_lang=language,
            dest_lang=dest_language,
            api_key=api_key
        )

        # 如果不保留音频文件，则删除
        if not keep_audio and audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"临时音频文件已删除: {audio_path}")

        # 如果需要烧录字幕到视频中
        if burn_subtitles and saved_files:
            # 找到第一个SRT格式的字幕文件
            srt_file = next((f for f in saved_files if f.endswith('.srt')), None)
            if srt_file:
                # 这里应该有烧录字幕的逻辑，但当前未实现
                print("烧录字幕功能尚未实现")

        print("字幕提取完成！")
        return True

    except Exception as e:
        print(f"提取字幕时出错: {e}")
        # 清理临时文件
        if not keep_audio and 'audio_path' in locals() and audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        return False

def main():
    parser = argparse.ArgumentParser(description="使用Whisper从视频中提取字幕")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper模型大小 (默认: base)")
    parser.add_argument("--language", default="en", help="指定源语言代码 (默认: en, 英语)")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--formats", default="srt,vtt,txt", help="输出格式，用逗号分隔 (默认: srt,vtt,txt)")
    parser.add_argument("--keep-audio", action="store_true", help="保留提取的音频文件")
    parser.add_argument("--dest-language", default="zh-CN", help="目标翻译语言 (默认: zh-CN，中文)")
    parser.add_argument("--api-key", help="Gemini API密钥（也可通过GEMINI_API_KEY环境变量设置）")
    parser.add_argument("--burn-subtitles", action="store_true", help="将字幕烧录到视频中")
    parser.add_argument("--font-size", type=int, default=28, help="烧录字幕的字体大小 (默认: 28)")
    parser.add_argument("--subtitle-position", default="bottom", choices=["bottom", "top", "middle"],
                        help="烧录字幕的位置 (默认: bottom)")
    parser.add_argument("--font-color", default="white", help="烧录字幕的字体颜色 (默认: white)")
    parser.add_argument("--outline-color", default="black", help="烧录字幕的轮廓颜色 (默认: black)")

    args = parser.parse_args()

    # 调用extract_subtitles函数
    success = extract_subtitles(
        video_path=args.video_path,
        model=args.model,
        language=args.language,
        output=args.output,
        formats=args.formats.split(","),
        keep_audio=args.keep_audio,
        dest_language=args.dest_language,
        api_key=args.api_key,
        burn_subtitles=args.burn_subtitles,
        font_size=args.font_size,
        subtitle_position=args.subtitle_position,
        font_color=args.font_color,
        outline_color=args.outline_color
    )

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
