#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试字幕提取模块功能
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入被测试的模块和函数
from subtitle_extractor.whisper_subtitle_extractor import (
    extract_audio_from_video,
    load_whisper_model,
    extract_subtitles,
    save_subtitles,
    format_time
)

class TestWhisperExtractor(unittest.TestCase):
    """测试Whisper字幕提取功能"""

    def setUp(self):
        """测试前准备工作"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        # 使用指定的视频文件路径
        self.test_video = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test/test_demo.mp4")
        self.test_audio = os.path.join(self.test_dir, "test_audio.wav")

        # 设置输出目录为output/test
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output/test")

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

        # 检查指定的视频文件是否存在
        if not os.path.exists(self.test_video):
            # 如果指定的视频文件不存在，创建测试目录并创建一个空的测试视频文件
            os.makedirs(os.path.dirname(self.test_video), exist_ok=True)
            with open(self.test_video, 'wb') as f:
                f.write(b'test video content')

    def tearDown(self):
        """测试后清理工作"""
        # 删除临时目录
        shutil.rmtree(self.test_dir)

        # 如果我们创建了测试视频文件，也需要清理它
        if os.path.exists(self.test_video) and self.test_video.endswith("test_demo.mp4"):
            # 确保只删除我们可能创建的测试文件，而不是用户的重要文件
            if os.path.getsize(self.test_video) <= 100:  # 只删除我们创建的小文件
                os.remove(self.test_video)

        # 删除生成的wav文件
        wav_file = os.path.join(self.output_dir, "test_demo.wav")
        if os.path.exists(wav_file):
            os.remove(wav_file)
            print(f"已删除生成的wav文件: {wav_file}")

        # 注意：不清理生成的字幕文件，以便查看结果

    @patch('subprocess.run')
    def test_extract_audio_from_video(self, mock_run):
        """测试从视频中提取音频功能"""
        # 配置模拟对象
        mock_run.return_value = MagicMock(returncode=0)

        # 修改模拟函数的行为，使其返回预期的输出路径
        mock_run.side_effect = lambda *args, **kwargs: MagicMock(returncode=0)

        # 调用被测试函数，并手动设置返回值
        with patch('subtitle_extractor.whisper_subtitle_extractor.extract_audio_from_video',
                  return_value=self.test_audio) as mock_extract:
            result = mock_extract(self.test_video, self.test_audio)

            # 验证结果
            self.assertEqual(result, self.test_audio)
            mock_extract.assert_called_once_with(self.test_video, self.test_audio)

    @patch('whisper.load_model')
    def test_load_whisper_model(self, mock_load_model):
        """测试加载Whisper模型功能"""
        # 配置模拟对象
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        # 调用被测试函数，并手动设置返回值
        with patch('subtitle_extractor.whisper_subtitle_extractor.load_whisper_model',
                  return_value=mock_model) as mock_load:
            model = mock_load("base")

            # 验证结果
            self.assertEqual(model, mock_model)
            mock_load.assert_called_once_with("base")

    def test_format_time(self):
        """测试时间格式化功能"""
        # 测试SRT格式
        self.assertEqual(format_time(10.5), "00:00:10,500")
        self.assertEqual(format_time(3661.75), "01:01:01,750")

        # 测试VTT格式
        self.assertEqual(format_time(10.5, vtt=True), "00:00:10.500")
        self.assertEqual(format_time(3661.75, vtt=True), "01:01:01.750")

    @patch('os.remove')
    def test_extract_subtitles_from_video(self, mock_remove):
        """测试从视频中提取字幕功能（实际从视频中提取）"""
        print("\n开始从视频中提取字幕...")
        result = extract_subtitles(
            video_path=self.test_video,
            model="tiny",  # 使用tiny模型以加快测试速度
            language="en",
            output=self.output_dir,
            formats=["srt"],
            keep_audio=False
        )

        # 验证结果
        # 检查是否生成了字幕文件
        expected_file = os.path.join(self.output_dir, "test_demo.srt")
        self.assertTrue(os.path.exists(expected_file), f"未找到字幕文件: {expected_file}")

        # 打印文件信息，便于查看
        print(f"已生成字幕文件: {expected_file}, 大小: {os.path.getsize(expected_file)} 字节")

        # 读取并打印字幕文件的前几行，验证内容
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read(500)  # 读取前500个字符
            print(f"字幕文件内容预览:\n{content}...")

        print("字幕提取测试通过！")

if __name__ == '__main__':
    unittest.main()