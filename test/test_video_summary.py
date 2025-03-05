#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试视频总结模块
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from video_summary.summarizer import (
    read_subtitle_file,
    extract_text_from_subtitle,
    generate_summary,
    save_summary_to_markdown,
    summarize_video_from_subtitle
)
from utils.config import get_api_key

class TestVideoSummary(unittest.TestCase):
    """测试视频总结功能"""

    def setUp(self):
        """测试前的准备工作"""
        # 设置测试文件路径
        self.project_root = Path(__file__).parent.parent

        # 使用实际的测试字幕文件
        self.test_srt = os.path.join(self.project_root, "output", "test", "test_demo.srt")

        # 使用实际的测试视频文件
        self.test_video = os.path.join(self.project_root, "output", "test", "test_demo.mp4")

        # 输出目录
        self.output_dir = os.path.join(self.project_root, "output", "test")
        os.makedirs(self.output_dir, exist_ok=True)

        # 确保测试文件存在
        if not os.path.exists(self.test_srt):
            raise FileNotFoundError(f"测试字幕文件不存在: {self.test_srt}")

        if not os.path.exists(self.test_video):
            raise FileNotFoundError(f"测试视频文件不存在: {self.test_video}")

    def tearDown(self):
        """测试后的清理工作"""
        # 删除生成的总结文件
        summary_path = os.path.join(self.output_dir, "test_demo_summary.markdown")
        if os.path.exists(summary_path) and not self.real_summary_test:
            os.remove(summary_path)
            print(f"已删除测试生成的总结文件: {summary_path}")

        # 重置标志
        self.real_summary_test = False

    def test_read_subtitle_file(self):
        """测试读取字幕文件"""
        self.real_summary_test = False
        content = read_subtitle_file(self.test_srt)
        self.assertIsNotNone(content)
        self.assertTrue(len(content) > 0, "字幕文件内容不应为空")
        print(f"成功读取字幕文件，内容长度: {len(content)} 字符")

    def test_extract_text_from_subtitle(self):
        """测试从字幕中提取文本"""
        self.real_summary_test = False
        with open(self.test_srt, 'r', encoding='utf-8') as f:
            content = f.read()

        text = extract_text_from_subtitle(content, '.srt')
        self.assertIsNotNone(text)
        self.assertTrue(len(text) > 0, "提取的文本不应为空")
        print(f"成功从字幕中提取文本，内容长度: {len(text)} 字符")

    @patch('video_summary.summarizer.get_gemini_api')
    def test_generate_summary(self, mock_get_api):
        """测试生成总结"""
        self.real_summary_test = False
        # 配置模拟对象
        mock_api = MagicMock()
        mock_api.generate_content.return_value = "# 视频总结\n\n这是一个测试视频的总结内容。"
        mock_get_api.return_value = mock_api

        # 读取实际字幕内容
        with open(self.test_srt, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取文本
        text_content = extract_text_from_subtitle(content, '.srt')

        # 调用被测试函数
        summary = generate_summary(text_content, "test_api_key")

        # 验证结果
        self.assertEqual(summary, "# 视频总结\n\n这是一个测试视频的总结内容。")
        mock_get_api.assert_called_once_with("test_api_key")
        mock_api.generate_content.assert_called_once()
        print(f"成功生成视频总结")

    def test_save_summary_to_markdown(self):
        """测试保存总结到Markdown文件"""
        self.real_summary_test = False
        summary_content = "# 视频总结\n\n这是一个测试视频的总结内容。"
        output_path = os.path.join(self.output_dir, "test_summary.md")

        # 调用被测试函数
        result_path = save_summary_to_markdown(summary_content, output_path)

        # 验证结果
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))

        # 验证文件内容
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, summary_content)
        print(f"成功保存总结到文件: {output_path}")

        # 清理
        if os.path.exists(output_path):
            os.remove(output_path)

    @patch('video_summary.summarizer.generate_summary')
    def test_summarize_video_from_subtitle(self, mock_generate_summary):
        """测试从字幕生成视频总结"""
        self.real_summary_test = False
        # 配置模拟对象
        mock_generate_summary.return_value = "# 视频总结\n\n这是一个测试视频的总结内容。"

        # 调用被测试函数
        result_path = summarize_video_from_subtitle(
            self.test_video,
            self.test_srt,
            "test_api_key",
            self.output_dir
        )

        # 验证结果
        expected_path = os.path.join(self.output_dir, "test_demo_summary.markdown")
        self.assertEqual(result_path, expected_path)
        self.assertTrue(os.path.exists(expected_path))

        # 验证文件内容
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, "# 视频总结\n\n这是一个测试视频的总结内容。")

        # 验证调用
        mock_generate_summary.assert_called_once()
        print(f"成功生成视频总结文件: {result_path}")

    def test_real_video_summary(self):
        """测试实际调用Gemini API生成视频总结"""
        self.real_summary_test = True
        print("\n===== 开始测试实际生成视频总结（中文） =====")
        print(f"视频文件: {self.test_video}")
        print(f"字幕文件: {self.test_srt}")
        print(f"输出目录: {self.output_dir}")

        # 获取API密钥
        api_key = get_api_key()
        if not api_key:
            self.skipTest("未找到Gemini API密钥，跳过测试")

        # 调用被测试函数
        try:
            result_path = summarize_video_from_subtitle(
                self.test_video,
                self.test_srt,
                api_key,
                self.output_dir
            )

            # 验证结果
            expected_path = os.path.join(self.output_dir, "test_demo_summary.markdown")
            self.assertEqual(result_path, expected_path)
            self.assertTrue(os.path.exists(expected_path))

            # 检查文件内容
            with open(expected_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 验证内容不为空
            self.assertTrue(len(content) > 0, "生成的总结内容不应为空")

            # 验证内容是中文
            self.assertTrue(any('\u4e00' <= char <= '\u9fff' for char in content),
                           "总结内容应该包含中文字符")

            # 打印总结内容预览
            preview = content[:500] + "..." if len(content) > 500 else content
            print(f"\n生成的总结内容预览:\n{preview}\n")

            print(f"\n✅ 测试成功！总结文件已保存到: {result_path}")
            print(f"文件大小: {os.path.getsize(result_path) / 1024:.2f} KB")

            return result_path

        except Exception as e:
            self.fail(f"生成视频总结时出错: {e}")

if __name__ == '__main__':
    unittest.main()