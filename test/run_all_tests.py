#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运行所有模块的测试，按照依赖顺序执行
"""

import os
import sys
import subprocess
import time

# 定义颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """打印带颜色的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def run_test(test_path):
    """运行指定的测试文件"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}运行测试: {test_path}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")

    start_time = time.time()
    result = subprocess.run(['python', test_path], capture_output=False)
    end_time = time.time()

    duration = end_time - start_time
    success = result.returncode == 0

    status = f"{Colors.GREEN}通过{Colors.ENDC}" if success else f"{Colors.RED}失败{Colors.ENDC}"
    print(f"\n{Colors.BOLD}测试结果: {status} (耗时: {duration:.2f}秒){Colors.ENDC}")

    return success

def main():
    """主函数，按照依赖顺序运行所有测试"""
    print_header("视频字幕处理工具 - 测试套件")

    print(f"\n{Colors.YELLOW}{Colors.BOLD}注意: 测试按照依赖顺序执行，确保数据流正确{Colors.ENDC}")
    print(f"{Colors.YELLOW}1. 先执行字幕提取测试，生成字幕文件{Colors.ENDC}")
    print(f"{Colors.YELLOW}2. 再执行字幕翻译测试，使用提取的字幕{Colors.ENDC}")
    print(f"{Colors.YELLOW}3. 最后执行字幕烧录测试，使用翻译后的字幕{Colors.ENDC}")
    print(f"{Colors.YELLOW}4. 视频总结测试可以在任何时候执行，但需要字幕文件存在{Colors.ENDC}")

    # 测试文件列表，按照依赖顺序排列
    test_files = [
        'test_subtitle_extractor.py',
        'test_subtitle_translator.py',
        'test_subtitle_burner.py',
        'test_video_summary.py',
        'test_real_summary.py',
        'test_subtitle_processor.py'
    ]

    # 记录测试结果
    results = {}
    all_passed = True
    total_start_time = time.time()

    # 运行每个测试文件
    for test_file in test_files:
        success = run_test(test_file)
        results[test_file] = success
        if not success:
            all_passed = False

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    # 打印测试结果摘要
    print_header("测试结果摘要")

    for test_file, success in results.items():
        status = f"{Colors.GREEN}通过{Colors.ENDC}" if success else f"{Colors.RED}失败{Colors.ENDC}"
        print(f"{test_file}: {status}")

    # 返回整体结果
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}所有测试通过！{Colors.ENDC}")
        print(f"{Colors.BOLD}总耗时: {total_duration:.2f}秒{Colors.ENDC}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}有测试失败！{Colors.ENDC}")
        print(f"{Colors.BOLD}总耗时: {total_duration:.2f}秒{Colors.ENDC}")
        return 1

if __name__ == '__main__':
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    sys.exit(main())