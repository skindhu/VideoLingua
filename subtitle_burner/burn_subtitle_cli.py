#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕烧录命令行工具
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from subtitle_burner.subtitle_burner import burn_subtitles_to_video

def main():
    """字幕烧录命令行工具主函数"""
    parser = argparse.ArgumentParser(description="将字幕烧录到视频中")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("subtitle_path", help="字幕文件路径")
    parser.add_argument("--output", "-o", help="输出视频文件路径，默认自动生成")
    parser.add_argument("--font-size", "-fs", type=int, default=28, help="字幕字体大小 (默认: 28)")
    parser.add_argument("--position", "-p", choices=["bottom", "top", "middle"], default="bottom",
                        help="字幕位置 (默认: bottom)")
    parser.add_argument("--font-color", "-fc", default="white",
                        help="字体颜色 (默认: white, 可选: white, yellow, green, cyan, blue, magenta, red 或十六进制颜色值)")
    parser.add_argument("--outline-color", "-oc", default="black",
                        help="轮廓颜色 (默认: black, 可选: black, white, yellow, green, cyan, blue, magenta, red 或十六进制颜色值)")

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.video_path):
        print(f"错误: 视频文件不存在: {args.video_path}")
        return 1

    if not os.path.exists(args.subtitle_path):
        print(f"错误: 字幕文件不存在: {args.subtitle_path}")
        return 1

    print(f"开始烧录字幕...")
    print(f"视频文件: {args.video_path}")
    print(f"字幕文件: {args.subtitle_path}")
    print(f"字体大小: {args.font_size}")
    print(f"字幕位置: {args.position}")
    print(f"字体颜色: {args.font_color}")
    print(f"轮廓颜色: {args.outline_color}")

    # 调用烧录函数
    output_path = burn_subtitles_to_video(
        video_path=args.video_path,
        subtitle_path=args.subtitle_path,
        output_path=args.output,
        font_size=args.font_size,
        position=args.position,
        font_color=args.font_color,
        outline_color=args.outline_color
    )

    if output_path:
        print(f"字幕烧录成功，输出文件: {output_path}")
        return 0
    else:
        print("字幕烧录失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())