#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试字幕处理器模块功能
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subtitle_processor import (
    process_subtitles,
    translate_subtitle_file,
    process_video,
    extract_subtitle,
    find_subtitle_files
)

class TestSubtitleProcessor(unittest.TestCase):
    """测试字幕处理器功能"""

    def setUp(self):
        """测试前准备工作"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.test_dir, "test_video.mp4")

        # 创建测试视频文件
        with open(self.test_video, 'wb') as f:
            f.write(b'test video content')

        # 创建测试字幕文件
        self.test_srt = os.path.join(self.test_dir, "test_video.srt")
        with open(self.test_srt, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:01,000 --> 00:00:05,000\nThis is a test subtitle.\n\n")
            f.write("2\n00:00:06,000 --> 00:00:10,000\nSecond line of subtitle.\n\n")

    def tearDown(self):
        """测试后清理工作"""
        # 删除临时目录
        shutil.rmtree(self.test_dir)

    @patch('subtitle_processor.extract_subtitles_raw')
    def test_extract_subtitle(self, mock_extract):
        """测试字幕提取功能"""
        # 配置模拟对象
        mock_extract.return_value = True

        # 创建预期的输出文件
        expected_output = os.path.join(self.test_dir, "test_video.srt")
        with open(expected_output, 'w', encoding='utf-8') as f:
            f.write("Test subtitle content")

        # 调用被测试函数
        result = extract_subtitle(
            video_path=self.test_video,
            output_dir=self.test_dir,
            subtitle_type="original",
            dest_language="zh-CN"
        )

        # 验证结果
        self.assertEqual(result, expected_output)
        mock_extract.assert_called_once()

        # 测试提取失败的情况
        mock_extract.return_value = False
        os.remove(expected_output)

        result = extract_subtitle(
            video_path=self.test_video,
            output_dir=self.test_dir
        )

        # 验证结果
        self.assertIsNone(result)

    def test_find_subtitle_files(self):
        """测试查找字幕文件功能"""
        # 创建多个测试字幕文件
        test_files = [
            os.path.join(self.test_dir, "test_video.srt"),
            os.path.join(self.test_dir, "test_video.vtt"),
            os.path.join(self.test_dir, "test_video.zh-CN.srt"),
            os.path.join(self.test_dir, "test_video.bilingual.srt"),
            os.path.join(self.test_dir, "other_video.srt")
        ]

        for file_path in test_files:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Test content")

        # 调用被测试函数
        found_files = find_subtitle_files(self.test_video, self.test_dir)

        # 验证结果
        self.assertEqual(len(found_files), 4)  # 应该找到4个与test_video相关的字幕文件
        self.assertIn(test_files[0], found_files)
        self.assertIn(test_files[1], found_files)
        self.assertIn(test_files[2], found_files)
        self.assertIn(test_files[3], found_files)
        self.assertNotIn(test_files[4], found_files)  # other_video.srt不应该被找到

    @patch('subtitle_processor.translate_subtitle_file')
    @patch('subtitle_processor.extract_subtitle')
    def test_process_video(self, mock_extract, mock_translate):
        """测试视频处理功能"""
        # 配置模拟对象
        mock_extract.return_value = self.test_srt
        mock_translate.return_value = os.path.join(self.test_dir, "test_video.zh-CN.srt")

        # 调用被测试函数
        result = process_video(
            video_path=self.test_video,
            subtitle_type="translated",
            output_dir=self.test_dir,
            dest_language="zh-CN"
        )

        # 验证结果
        self.assertEqual(len(result), 2)  # 原始字幕和翻译后的字幕
        self.assertIn(self.test_srt, result)
        self.assertIn(mock_translate.return_value, result)
        mock_extract.assert_called_once()
        mock_translate.assert_called_once()

        # 测试提取失败的情况
        mock_extract.return_value = None
        mock_translate.reset_mock()

        result = process_video(
            video_path=self.test_video,
            subtitle_type="translated",
            output_dir=self.test_dir
        )

        # 验证结果
        self.assertEqual(result, [])
        mock_translate.assert_not_called()

    @patch('subtitle_processor.get_translator')
    def test_translate_subtitle_file(self, mock_get_translator):
        """测试字幕文件翻译功能"""
        # 配置模拟对象
        mock_translator = MagicMock()
        mock_translator.translate.return_value = """1
00:00:01,000 --> 00:00:05,000
这是一个测试字幕。

2
00:00:06,000 --> 00:00:10,000
字幕的第二行。
"""
        mock_get_translator.return_value = mock_translator

        # 调用被测试函数
        output_file = translate_subtitle_file(
            file_path=self.test_srt,
            subtitle_type="translated",
            dest_language="zh-CN",
            src_language="en",
            api_key="test_api_key"
        )

        # 验证结果
        self.assertTrue(os.path.exists(output_file))
        self.assertIn("zh-CN", output_file)
        mock_get_translator.assert_called_once()
        mock_translator.translate.assert_called_once()

    @patch('subtitle_processor.burn_subtitles_to_video')
    @patch('subtitle_processor.select_subtitle_file')
    @patch('subtitle_processor.process_video')
    def test_process_subtitles(self, mock_process_video, mock_select, mock_burn):
        """测试字幕处理主功能"""
        # 配置模拟对象
        subtitle_files = [
            os.path.join(self.test_dir, "test_video.srt"),
            os.path.join(self.test_dir, "test_video.zh-CN.srt")
        ]
        mock_process_video.return_value = subtitle_files
        mock_select.return_value = subtitle_files[1]
        mock_burn.return_value = os.path.join(self.test_dir, "test_video_subtitled.mp4")

        # 调用被测试函数 - 不烧录字幕
        result = process_subtitles(
            video_path=self.test_video,
            model="base",
            language="en",
            output=self.test_dir,
            formats=["srt"],
            keep_audio=False,
            subtitle_type="translated",
            dest_language="zh-CN",
            api_key="test_api_key",
            burn_subtitles=False
        )

        # 验证结果
        self.assertTrue(result)
        mock_process_video.assert_called_once()
        mock_select.assert_not_called()
        mock_burn.assert_not_called()

        # 测试烧录字幕
        mock_process_video.reset_mock()

        result = process_subtitles(
            video_path=self.test_video,
            subtitle_type="translated",
            burn_subtitles=True,
            font_size=28,
            subtitle_position="bottom"
        )

        # 验证结果
        self.assertTrue(result)
        mock_process_video.assert_called_once()
        mock_select.assert_called_once()
        mock_burn.assert_called_once()

        # 测试处理失败的情况
        mock_process_video.return_value = []
        mock_process_video.reset_mock()
        mock_select.reset_mock()
        mock_burn.reset_mock()

        result = process_subtitles(
            video_path=self.test_video,
            burn_subtitles=True
        )

        # 验证结果
        self.assertTrue(result)  # 即使没有字幕文件，函数也应该返回True
        mock_process_video.assert_called_once()
        mock_select.assert_not_called()
        mock_burn.assert_not_called()

if __name__ == '__main__':
    unittest.main()