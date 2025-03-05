#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕写入模块，用于将字幕写入不同格式的文件
"""

import os
import json

def format_time(seconds, vtt=False):
    """将秒数转换为字幕时间格式"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    
    if vtt:
        # VTT格式: HH:MM:SS.mmm
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    else:
        # SRT格式: HH:MM:SS,mmm
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")

def save_subtitles(subtitle_data, output_path, formats=None, subtitle_type='original'):
    """
    保存字幕到文件
    
    Args:
        subtitle_data: 字幕数据，包含segments和translated_segments
        output_path: 输出文件路径
        formats: 输出格式列表，如 ["srt", "vtt", "txt"]
        subtitle_type: 字幕类型，可以是 'original'(原始语言), 'translated'(翻译语言) 或 'bilingual'(双语)
        
    Returns:
        保存的文件路径列表
    """
    if output_path is None:
        raise ValueError("必须提供输出路径")
    
    if formats is None:
        formats = ["srt", "vtt", "txt"]
    
    base_path = os.path.splitext(output_path)[0]
    saved_files = []
    
    segments = subtitle_data["segments"]
    translated_segments = subtitle_data.get("translated_segments", [])
    
    try:
        # 保存SRT格式
        if "srt" in formats:
            if subtitle_type == 'original':
                suffix = ""
            elif subtitle_type == 'translated':
                suffix = ".translated"
            else:  # bilingual
                suffix = ".bilingual"
                
            srt_path = f"{base_path}{suffix}.srt"
            with open(srt_path, 'w', encoding='utf-8') as f:
                if subtitle_type in ['original', 'translated']:
                    for i, segment in enumerate(segments, 1):
                        start_time = format_time(segment["start"])
                        end_time = format_time(segment["end"])
                        
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        
                        if subtitle_type == 'translated' and translated_segments:
                            text = translated_segments[i-1]["translated"]
                        else:
                            text = segment["text"].strip()
                            
                        f.write(f"{text}\n\n")
                else:  # bilingual
                    for i, segment in enumerate(translated_segments, 1):
                        start_time = format_time(segment["start"])
                        end_time = format_time(segment["end"])
                        
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{segment['original']}\n{segment['translated']}\n\n")
            
            saved_files.append(srt_path)
            print(f"SRT字幕已保存到: {srt_path}")
        
        # 保存VTT格式
        if "vtt" in formats:
            if subtitle_type == 'original':
                suffix = ""
            elif subtitle_type == 'translated':
                suffix = ".translated"
            else:  # bilingual
                suffix = ".bilingual"
                
            vtt_path = f"{base_path}{suffix}.vtt"
            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                if subtitle_type in ['original', 'translated']:
                    for i, segment in enumerate(segments, 1):
                        start_time = format_time(segment["start"], vtt=True)
                        end_time = format_time(segment["end"], vtt=True)
                        
                        f.write(f"{start_time} --> {end_time}\n")
                        
                        if subtitle_type == 'translated' and translated_segments:
                            text = translated_segments[i-1]["translated"]
                        else:
                            text = segment["text"].strip()
                            
                        f.write(f"{text}\n\n")
                else:  # bilingual
                    for i, segment in enumerate(translated_segments, 1):
                        start_time = format_time(segment["start"], vtt=True)
                        end_time = format_time(segment["end"], vtt=True)
                        
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{segment['original']}\n{segment['translated']}\n\n")
            
            saved_files.append(vtt_path)
            print(f"VTT字幕已保存到: {vtt_path}")
        
        # 保存纯文本格式
        if "txt" in formats:
            if subtitle_type == 'original':
                suffix = ""
                txt_path = f"{base_path}{suffix}.txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join([s["text"].strip() for s in segments]))
            
            elif subtitle_type == 'translated':
                suffix = ".translated"
                txt_path = f"{base_path}{suffix}.txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    translated_text = "\n".join([s["translated"] for s in translated_segments])
                    f.write(translated_text)
            
            else:  # bilingual
                suffix = ".bilingual"
                txt_path = f"{base_path}{suffix}.txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    for segment in translated_segments:
                        f.write(f"{segment['original']}\n{segment['translated']}\n\n")
            
            saved_files.append(txt_path)
            print(f"文本字幕已保存到: {txt_path}")
        
        # 保存JSON格式（可选）
        if "json" in formats:
            json_path = f"{base_path}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json_data = {
                    "segments": segments,
                }
                if subtitle_type in ['translated', 'bilingual']:
                    json_data["translated_segments"] = translated_segments
                
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            saved_files.append(json_path)
            print(f"JSON字幕数据已保存到: {json_path}")
    
    except Exception as e:
        print(f"保存字幕时出错: {e}")
    
    return saved_files
