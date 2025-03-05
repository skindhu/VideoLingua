#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频字幕处理工具主入口

这个工具可以从视频中提取字幕，翻译字幕，并将字幕烧录到视频中。
它组合了四个主要模块的功能：
1. 字幕提取 (subtitle_extractor)
2. 字幕翻译 (subtitle_translator)
3. 字幕烧录 (subtitle_burner)
4. 视频总结 (video_summary)

使用示例:
    # 完整处理视频（提取、翻译和烧录）
    python main.py video.mp4

    # 启动图形界面
    python main.py --gui

    # 生成视频内容总结
    python main.py video.mp4 --summarize
"""

import os
import sys
import argparse
from subtitle_processor import process_subtitles, find_subtitle_files
from subtitle_extractor.whisper_gui import run_gui
from utils.config import get_default_settings, get_api_key
from video_summary import summarize_video_from_subtitle

def main():
    """
    主函数，处理命令行参数并调用相应的功能
    """
    # 获取默认设置
    default_settings = get_default_settings()

    parser = argparse.ArgumentParser(
        description="视频字幕处理工具 - 提取、翻译、烧录字幕和生成视频总结",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 完整处理视频（提取、翻译和烧录）
  python main.py video.mp4

  # 启动图形界面
  python main.py --gui

  # 生成视频内容总结
  python main.py video.mp4 --summarize
        """
    )

    # GUI选项
    parser.add_argument("--gui", action="store_true", help="启动图形用户界面")

    # 视频文件参数（可选，如果使用GUI则不需要）
    parser.add_argument("video_file", nargs="?", help="要处理的视频文件路径")

    # 输出路径（可选）
    parser.add_argument("--output", help="输出文件路径或目录")

    # 视频总结选项
    parser.add_argument("--summarize", action="store_true", help="生成视频内容总结")
    parser.add_argument("--subtitle", help="用于总结的字幕文件路径（如果不提供，将使用处理后的字幕或尝试查找同名字幕文件）")

    args = parser.parse_args()

    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 处理不同的命令
    if args.gui:
        run_gui()
    elif args.video_file:
        # 构建参数字典，直接使用配置文件中的设置
        params = {
            "model": default_settings['model'],
            "language": default_settings['language'],
            "output": args.output or output_dir,
            "formats": default_settings['output_format'].split(","),
            "keep_audio": False,  # 默认不保留音频文件
            "subtitle_type": default_settings['subtitle_type'],
            "dest_language": default_settings['dest_language'],
            "api_key": get_api_key(),
            "burn_subtitles": default_settings['burn_subtitles'],
            "font_size": default_settings['subtitle_font_size'],
            "subtitle_position": default_settings['subtitle_position'],
            "font_color": default_settings['subtitle_font_color'],
            "outline_color": default_settings['subtitle_outline_color']
        }

        # 打印处理信息
        print(f"\n===== 开始处理视频字幕 =====")
        print(f"视频文件: {args.video_file}")
        print(f"字幕类型: {default_settings['subtitle_type']}")
        print(f"源语言: {default_settings['language']}, 目标语言: {default_settings['dest_language']}")
        print(f"使用模型: {default_settings['model']}")
        if default_settings['burn_subtitles']:
            print(f"将烧录字幕到视频中")
            print(f"字幕设置: 字体大小={default_settings['subtitle_font_size']}, "
                  f"位置={default_settings['subtitle_position']}")
        print(f"===========================\n")

        # 调用字幕处理函数
        result = process_subtitles(args.video_file, **params)

        if result:
            print(f"\n✅ 字幕处理成功完成！")
            print(f"输出目录: {params['output']}")

            # 如果需要生成视频总结
            if args.summarize:
                print(f"\n===== 开始生成视频内容总结 =====")

                # 确定用于总结的字幕文件
                subtitle_path = args.subtitle
                if not subtitle_path:
                    # 如果没有提供字幕文件，查找处理后的字幕文件
                    output_dir = params['output']
                    video_base_name = os.path.splitext(os.path.basename(args.video_file))[0]
                    subtitle_files = find_subtitle_files(args.video_file, output_dir)

                    if subtitle_files and len(subtitle_files) > 0:
                        # 优先使用双语字幕，其次是翻译后的字幕，最后是原始字幕
                        bilingual_subtitles = [f for f in subtitle_files if ".bilingual." in f]
                        translated_subtitles = [f for f in subtitle_files if ".translated." in f]

                        if bilingual_subtitles:
                            subtitle_path = bilingual_subtitles[0]
                        elif translated_subtitles:
                            subtitle_path = translated_subtitles[0]
                        else:
                            subtitle_path = subtitle_files[0]

                # 生成视频总结
                try:
                    summary_path = summarize_video_from_subtitle(
                        args.video_file,
                        subtitle_path,
                        get_api_key(),
                        params['output']
                    )
                    print(f"\n✅ 视频内容总结生成成功！")
                    print(f"总结文件: {summary_path}")
                except Exception as e:
                    print(f"\n❌ 视频内容总结生成失败: {e}")
        else:
            print(f"\n❌ 字幕处理失败！")
            return 1
    elif args.summarize and args.video_file:
        # 仅生成视频总结
        print(f"\n===== 开始生成视频内容总结 =====")
        print(f"视频文件: {args.video_file}")

        try:
            summary_path = summarize_video_from_subtitle(
                args.video_file,
                args.subtitle,
                get_api_key(),
                args.output or output_dir
            )
            print(f"\n✅ 视频内容总结生成成功！")
            print(f"总结文件: {summary_path}")
        except Exception as e:
            print(f"\n❌ 视频内容总结生成失败: {e}")
            return 1
    else:
        parser.print_help()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
