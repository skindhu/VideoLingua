#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字幕翻译命令行工具
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from subtitle_translator.translator import get_translator
from subtitle_processor import translate_subtitle_file

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('subtitle_translator_cli')

def main():
    """字幕翻译命令行工具主函数"""
    parser = argparse.ArgumentParser(description="翻译字幕文件")
    parser.add_argument("subtitle_path", help="字幕文件路径")
    parser.add_argument("--output", "-o", help="输出字幕文件路径，默认自动生成")
    parser.add_argument("--type", "-t", choices=["translated", "bilingual"], default="translated",
                        help="字幕类型: translated(翻译后) 或 bilingual(双语) (默认: translated)")
    parser.add_argument("--src-lang", "-sl", default="auto",
                        help="源语言代码 (默认: auto，自动检测)")
    parser.add_argument("--dest-lang", "-dl", default="zh-CN",
                        help="目标语言代码 (默认: zh-CN，中文)")
    parser.add_argument("--api-key", "-k", help="Gemini API密钥")

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.subtitle_path):
        print(f"错误: 字幕文件不存在: {args.subtitle_path}")
        return 1

    print(f"开始翻译字幕...")
    print(f"字幕文件: {args.subtitle_path}")
    print(f"字幕类型: {args.type}")
    print(f"源语言: {args.src_lang}")
    print(f"目标语言: {args.dest_lang}")

    try:
        # 调用翻译函数
        output_file = translate_subtitle_file(
            file_path=args.subtitle_path,
            subtitle_type=args.type,
            dest_language=args.dest_lang,
            src_language=args.src_lang,
            api_key=args.api_key,
            output_path=args.output
        )

        if output_file:
            print(f"字幕翻译成功，输出文件: {output_file}")
            return 0
        else:
            print("字幕翻译失败")
            return 1
    except Exception as e:
        logger.exception(f"翻译字幕时出错: {e}")
        print(f"翻译字幕时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())