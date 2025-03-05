#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试字幕翻译模块功能
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 修改导入路径
from subtitle_translator.translator import get_translator
from subtitle_processor import (
    translate_subtitle_file,
    parse_srt,
    parse_vtt,
    write_srt,
    write_vtt,
    write_txt
)

class TestSubtitleTranslator(unittest.TestCase):
    """测试字幕翻译功能"""

    def setUp(self):
        """测试前准备工作"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()

        # 创建测试SRT文件
        self.test_srt = os.path.join(self.test_dir, "test_demo.srt")
        with open(self.test_srt, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:01,000 --> 00:00:05,000\nThis is a test subtitle.\n\n")
            f.write("2\n00:00:06,000 --> 00:00:10,000\nSecond line of subtitle.\n\n")

        # 创建测试VTT文件 - 修复格式
        self.test_vtt = os.path.join(self.test_dir, "test_demo.vtt")
        with open(self.test_vtt, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            f.write("00:00:01.000 --> 00:00:05.000\nThis is a test subtitle.\n\n")
            f.write("00:00:06.000 --> 00:00:10.000\nSecond line of subtitle.\n\n")

    def tearDown(self):
        """测试后清理工作"""
        # 删除临时目录
        shutil.rmtree(self.test_dir)

    @patch('utils.gemini_api.GeminiAPI')
    def test_get_translator(self, mock_api_class):
        """测试获取翻译器实例"""
        # 配置模拟对象
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api

        # 调用被测试函数
        with patch('subtitle_translator.translator.get_gemini_api', return_value=mock_api) as mock_get_api:
            translator = get_translator("test_api_key")
            mock_get_api.assert_called_once_with("test_api_key")

    def test_parse_srt(self):
        """测试SRT格式解析"""
        # 读取测试SRT文件
        with open(self.test_srt, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析SRT内容
        segments = parse_srt(content)

        # 验证结果
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]['time'], "00:00:01,000 --> 00:00:05,000")
        self.assertEqual(segments[0]['text'], "This is a test subtitle.")
        self.assertEqual(segments[1]['time'], "00:00:06,000 --> 00:00:10,000")
        self.assertEqual(segments[1]['text'], "Second line of subtitle.")

    def test_parse_vtt(self):
        """测试VTT格式解析"""
        # 读取测试VTT文件
        with open(self.test_vtt, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析VTT内容
        segments = parse_vtt(content)

        # 验证结果
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]['time'], "00:00:01.000 --> 00:00:05.000")
        self.assertEqual(segments[0]['text'], "This is a test subtitle.")
        self.assertEqual(segments[1]['time'], "00:00:06.000 --> 00:00:10.000")
        self.assertEqual(segments[1]['text'], "Second line of subtitle.")

    @patch('subtitle_translator.translator.get_translator')
    def test_translate_subtitle_file(self, mock_get_translator):
        """测试字幕文件翻译功能"""
        # 配置模拟对象
        mock_translator = MagicMock()
        mock_translator.translate.side_effect = lambda text, *args, **kwargs: "这是一个测试字幕。" if "test subtitle" in text else "字幕的第二行。"
        mock_get_translator.return_value = mock_translator

        # 调用被测试函数 - 翻译模式
        with patch('subtitle_processor.translate_subtitle_file', return_value=os.path.join(self.test_dir, "test.zh-CN.srt")) as mock_translate:
            output_file = mock_translate(
                file_path=self.test_srt,
                subtitle_type="translated",
                dest_language="zh-CN",
                src_language="en",
                api_key="test_api_key"
            )

            # 验证结果
            self.assertTrue(os.path.exists(self.test_dir))
            mock_translate.assert_called_once()

    def test_write_subtitle_formats(self):
        """测试字幕写入不同格式"""
        # 准备测试数据
        segments = [
            {'time': '00:00:01,000 --> 00:00:05,000', 'text': 'Original text', 'translated': '翻译文本'},
            {'time': '00:00:06,000 --> 00:00:10,000', 'text': 'Second line', 'translated': '第二行'}
        ]

        # 测试SRT格式写入 - 原始模式
        srt_file = os.path.join(self.test_dir, "output_original.srt")
        with open(srt_file, 'w', encoding='utf-8') as f:
            write_srt(f, segments, "original")

        # 验证SRT原始模式内容
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Original text", content)
        self.assertNotIn("翻译文本", content)

        # 测试SRT格式写入 - 翻译模式
        srt_file = os.path.join(self.test_dir, "output_translated.srt")
        with open(srt_file, 'w', encoding='utf-8') as f:
            write_srt(f, segments, "translated")

        # 验证SRT翻译模式内容
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("翻译文本", content)
        self.assertNotIn("Original text", content)

        # 测试SRT格式写入 - 双语模式
        srt_file = os.path.join(self.test_dir, "output_bilingual.srt")
        with open(srt_file, 'w', encoding='utf-8') as f:
            write_srt(f, segments, "bilingual")

        # 验证SRT双语模式内容
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Original text", content)
        self.assertIn("翻译文本", content)

        # 测试VTT格式写入
        vtt_file = os.path.join(self.test_dir, "output.vtt")
        with open(vtt_file, 'w', encoding='utf-8') as f:
            write_vtt(f, segments, "bilingual")

        # 验证VTT内容
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("WEBVTT", content)
        self.assertIn("Original text", content)
        self.assertIn("翻译文本", content)

        # 测试TXT格式写入
        txt_file = os.path.join(self.test_dir, "output.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            write_txt(f, segments, "bilingual")

        # 验证TXT内容
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Original text", content)
        self.assertIn("翻译文本", content)
        self.assertNotIn("00:00:01,000", content)  # TXT不应包含时间戳

    def test_translate_real_subtitle_file(self):
        """测试翻译实际的字幕文件，分别测试translated和bilingual类型"""
        # 设置测试输入文件路径
        input_srt = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test/test_demo.srt")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test")

        # 确保输入文件存在
        if not os.path.exists(input_srt):
            self.skipTest(f"测试文件不存在: {input_srt}")

        print(f"\n使用实际字幕文件: {input_srt}")

        # 测试translated类型
        print("\n开始测试translated类型字幕翻译...")
        translated_output = os.path.join(output_dir, "test_demo.zh-CN.srt")

        # 如果文件已存在，先删除
        if os.path.exists(translated_output):
            os.remove(translated_output)

        # 调用实际的翻译函数
        result = translate_subtitle_file(
            file_path=input_srt,
            subtitle_type="translated",
            dest_language="zh-CN",
            src_language="en",
            api_key=None,  # 使用环境变量中的API密钥
            output_path=translated_output
        )

        # 验证文件是否生成
        self.assertTrue(os.path.exists(translated_output), f"未生成translated字幕文件: {translated_output}")
        print(f"已生成translated字幕文件: {translated_output}")

        # 读取并打印字幕文件的前几行
        with open(translated_output, 'r', encoding='utf-8') as f:
            content = f.read(500)
            print(f"translated字幕文件内容预览:\n{content}...")

        # 测试bilingual类型
        print("\n开始测试bilingual类型字幕翻译...")
        bilingual_output = os.path.join(output_dir, "test_demo.bilingual.srt")

        # 如果文件已存在，先删除
        if os.path.exists(bilingual_output):
            os.remove(bilingual_output)

        # 调用实际的翻译函数
        result = translate_subtitle_file(
            file_path=input_srt,
            subtitle_type="bilingual",
            dest_language="zh-CN",
            src_language="en",
            api_key=None,  # 使用环境变量中的API密钥
            output_path=bilingual_output
        )

        # 验证文件是否生成
        self.assertTrue(os.path.exists(bilingual_output), f"未生成bilingual字幕文件: {bilingual_output}")
        print(f"已生成bilingual字幕文件: {bilingual_output}")

        # 读取并打印字幕文件的前几行
        with open(bilingual_output, 'r', encoding='utf-8') as f:
            content = f.read(500)
            print(f"bilingual字幕文件内容预览:\n{content}...")

if __name__ == '__main__':
    unittest.main()