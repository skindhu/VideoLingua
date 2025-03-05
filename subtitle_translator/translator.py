#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Google Gemini API进行文本翻译的模块
"""

import os
import sys
import time
import logging
from typing import List, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('translator')

# 添加项目根目录到路径，确保可以导入utils模块
sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_api import get_gemini_api

class Translator:
    """文本翻译类"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化翻译器

        Args:
            api_key: Gemini API密钥，如果为None，则尝试从环境变量GEMINI_API_KEY获取
        """
        logger.info("初始化翻译器")
        self.api_key = api_key
        self.gemini_api = get_gemini_api(api_key)

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "zh-CN") -> str:
        """
        翻译单个文本

        Args:
            text: 要翻译的文本
            source_lang: 源语言代码，"auto"表示自动检测
            target_lang: 目标语言代码

        Returns:
            翻译后的文本
        """
        if not text.strip():
            logger.warning("收到空文本，跳过翻译")
            return text

        logger.info(f"翻译文本，源语言: {source_lang}, 目标语言: {target_lang}")
        logger.info(f"原文: {text[:50]}..." if len(text) > 50 else f"原文: {text}")

        # 构建翻译提示词，将指令和内容分开
        if source_lang == "auto":
            system_prompt = f"请将用户提供的文本翻译成{target_lang}语言，保持原文的格式和语气。只返回翻译结果，不要添加任何解释或说明。"
        else:
            system_prompt = f"请将用户提供的{source_lang}文本翻译成{target_lang}语言，保持原文的格式和语气。只返回翻译结果，不要添加任何解释或说明。"

        try:
            # 使用Gemini API生成翻译，将系统提示和用户内容分开
            start_time = time.time()
            response = self.gemini_api.generate_content(
                [
                    {"role": "system", "parts": [system_prompt]},
                    {"role": "user", "parts": [text]}
                ],
                temperature=0.2
            )
            translated_text = response
            elapsed_time = time.time() - start_time

            # 清理可能的引号和前缀
            translated_text = translated_text.strip()
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]

            logger.info(f"翻译完成，耗时: {elapsed_time:.2f}秒")
            logger.info(f"译文: {translated_text[:50]}..." if len(translated_text) > 50 else f"译文: {translated_text}")

            # 检查翻译结果
            if not translated_text:
                logger.warning("翻译结果为空")
            elif translated_text == text:
                logger.warning("翻译结果与原文相同，可能翻译失败")

            return translated_text
        except Exception as e:
            logger.exception(f"翻译过程中出错: {e}")
            print(f"翻译过程中出错: {e}")
            return text

    def batch_translate(self, texts: List[str], source_lang: str = "auto", target_lang: str = "zh-CN",
                        batch_size: int = 10, delay: float = 1.0) -> List[str]:
        """
        批量翻译多个文本

        Args:
            texts: 要翻译的文本列表
            source_lang: 源语言代码，"auto"表示自动检测
            target_lang: 目标语言代码
            batch_size: 每批处理的文本数量，避免API限制
            delay: 每批之间的延迟时间(秒)

        Returns:
            翻译后的文本列表
        """
        logger.info(f"批量翻译 {len(texts)} 个文本，源语言: {source_lang}, 目标语言: {target_lang}")
        results = []

        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            logger.info(f"处理批次 {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}, 包含 {len(batch)} 个文本")

            batch_results = []
            for j, text in enumerate(batch):
                logger.info(f"翻译批次 {i//batch_size + 1} 中的第 {j+1}/{len(batch)} 个文本")
                translated = self.translate(text, source_lang, target_lang)
                batch_results.append(translated)

            results.extend(batch_results)

            # 添加延迟，避免API限制
            if i + batch_size < len(texts):
                logger.info(f"等待 {delay} 秒后处理下一批...")
                time.sleep(delay)

        logger.info(f"批量翻译完成，共 {len(results)} 个文本")
        return results

def get_translator(api_key: Optional[str] = None) -> Translator:
    """
    获取翻译器实例

    Args:
        api_key: Gemini API密钥，如果为None，则尝试从环境变量获取

    Returns:
        翻译器实例
    """
    logger.info("创建翻译器实例")
    return Translator(api_key)

# 简单的命令行接口，用于测试
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="使用Google Gemini API进行文本翻译")
    parser.add_argument("text", help="要翻译的文本")
    parser.add_argument("--source", default="auto", help="源语言代码 (默认: auto)")
    parser.add_argument("--target", default="zh-CN", help="目标语言代码 (默认: zh-CN)")
    parser.add_argument("--api-key", help="Gemini API密钥 (也可通过GEMINI_API_KEY环境变量设置)")

    args = parser.parse_args()

    try:
        translator = get_translator(args.api_key)
        translated = translator.translate(args.text, args.source, args.target)
        print(f"原文: {args.text}")
        print(f"译文: {translated}")
    except Exception as e:
        print(f"错误: {e}")
