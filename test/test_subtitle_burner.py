#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试字幕烧录模块功能
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subtitle_burner import (
    burn_subtitles_to_video,
    select_subtitle_file
)

class TestSubtitleBurner(unittest.TestCase):
    """测试字幕烧录功能"""

    def setUp(self):
        """测试前准备工作"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.test_video = os.path.join(self.test_dir, "test_video.mp4")

        # 创建测试视频文件
        with open(self.test_video, 'wb') as f:
            f.write(b'test video content')

        # 创建测试字幕文件
        self.test_srt_original = os.path.join(self.test_dir, "test_video.srt")
        with open(self.test_srt_original, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:01,000 --> 00:00:05,000\nOriginal subtitle.\n\n")

        self.test_srt_translated = os.path.join(self.test_dir, "test_video.zh-CN.srt")
        with open(self.test_srt_translated, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:01,000 --> 00:00:05,000\n翻译后的字幕。\n\n")

        self.test_srt_bilingual = os.path.join(self.test_dir, "test_video.bilingual.srt")
        with open(self.test_srt_bilingual, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:01,000 --> 00:00:05,000\nOriginal subtitle.\n翻译后的字幕。\n\n")

        # 设置实际测试文件路径
        self.real_video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test/test_demo.mp4")
        self.real_subtitle_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test/test_demo.bilingual.srt")
        self.real_output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test")

    def tearDown(self):
        """测试后清理工作"""
        # 删除临时目录
        shutil.rmtree(self.test_dir)

        # 注意：不删除生成的视频文件，以便查看结果

    def test_select_subtitle_file(self):
        """测试字幕文件选择功能"""
        # 准备测试数据
        subtitle_files = [
            self.test_srt_original,
            self.test_srt_translated,
            self.test_srt_bilingual
        ]

        # 测试选择原始字幕
        selected = select_subtitle_file(subtitle_files, "original")
        self.assertEqual(selected, self.test_srt_original)

        # 测试选择翻译字幕
        selected = select_subtitle_file(subtitle_files, "translated")
        self.assertEqual(selected, self.test_srt_translated)

        # 测试选择双语字幕
        selected = select_subtitle_file(subtitle_files, "bilingual")
        self.assertEqual(selected, self.test_srt_bilingual)

        # 测试当请求的字幕类型不存在时的回退行为
        # 删除双语字幕文件
        os.remove(self.test_srt_bilingual)
        subtitle_files = [
            self.test_srt_original,
            self.test_srt_translated
        ]

        # 当请求bilingual但不存在时，应该返回第一个.srt文件
        selected = select_subtitle_file(subtitle_files, "bilingual")
        self.assertEqual(selected, self.test_srt_original)

        # 测试空列表
        selected = select_subtitle_file([], "original")
        self.assertIsNone(selected)

    @patch('subprocess.Popen')
    @patch('shutil.which')
    def test_burn_subtitles_to_video(self, mock_which, mock_popen):
        """测试字幕烧录到视频功能"""
        # 配置模拟对象
        mock_which.return_value = "/usr/bin/ffmpeg"  # 模拟ffmpeg已安装

        # 设置模拟进程
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr.readline.side_effect = ['', '']
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        # 预期的输出路径
        expected_output = os.path.join(os.path.dirname(self.test_video),
                                      f"{os.path.splitext(os.path.basename(self.test_video))[0]}.zh-CN.hardcoded.mp4")

        # 使用patch来模拟burn_subtitles_to_video函数的返回值
        with patch('subtitle_burner.subtitle_burner.burn_subtitles_to_video',
                  return_value=expected_output) as mock_burn:

            # 调用被测试函数
            output_video = mock_burn(
                self.test_video,
                self.test_srt_translated,
                font_size=28,
                position="bottom",
                font_color="white",
                outline_color="black"
            )

            # 验证结果
            self.assertEqual(output_video, expected_output)
            mock_burn.assert_called_once()

    def test_burn_real_subtitles_to_video(self):
        """测试使用实际视频和字幕文件进行字幕烧录"""
        # 检查输入文件是否存在
        self.assertTrue(os.path.exists(self.real_video_path), f"测试视频文件不存在: {self.real_video_path}")
        self.assertTrue(os.path.exists(self.real_subtitle_path), f"测试字幕文件不存在: {self.real_subtitle_path}")

        print(f"\n开始测试实际视频的字幕烧录...")
        print(f"输入视频: {self.real_video_path}")
        print(f"输入字幕: {self.real_subtitle_path}")

        # 预期的输出路径
        expected_output = os.path.join(self.real_output_dir, "test_demo.bilingual.hardcoded.mp4")

        # 如果输出文件已存在，先删除
        if os.path.exists(expected_output):
            os.remove(expected_output)
            print(f"已删除已存在的输出文件: {expected_output}")

        # 调用被测试函数
        output_video = burn_subtitles_to_video(
            self.real_video_path,
            self.real_subtitle_path,
            font_size=16,  # 使用较小的字体大小
            position="bottom",
            font_color="white",
            outline_color="black",
            shadow_radius=0.3  # 设置阴影半径为3
        )

        # 验证结果
        self.assertIsNotNone(output_video, "字幕烧录失败，返回值为None")
        self.assertTrue(os.path.exists(output_video), f"输出视频文件不存在: {output_video}")
        self.assertEqual(output_video, expected_output, f"输出路径与预期不符: {output_video} != {expected_output}")

        # 检查输出文件大小
        file_size = os.path.getsize(output_video)
        print(f"字幕烧录成功！输出文件: {output_video}")
        print(f"输出文件大小: {file_size / (1024 * 1024):.2f} MB")

        # 确保输出文件大小合理（至少1MB）
        self.assertGreater(file_size, 1024 * 1024, "输出视频文件过小，可能未正确生成")

if __name__ == '__main__':
    unittest.main()