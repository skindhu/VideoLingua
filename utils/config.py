#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块，用于处理应用程序配置
"""

import os
import configparser
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 配置文件路径
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config", "config.ini")

def ensure_config_dir():
    """确保配置目录存在"""
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)

    # 创建.gitignore文件以忽略配置文件
    gitignore_path = os.path.join(config_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("# 忽略配置文件\n*.ini\n")

def load_config():
    """
    加载配置文件

    Returns:
        配置对象，如果文件不存在则返回新的配置对象
    """
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        try:
            config.read(CONFIG_FILE, encoding='utf-8')
        except Exception as e:
            print(f"读取配置文件时出错: {e}")

    # 确保API部分存在
    if 'API' not in config:
        config['API'] = {}

    return config

def save_config(config):
    """
    保存配置到文件

    Args:
        config: 要保存的配置对象
    """
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
    except Exception as e:
        print(f"保存配置文件时出错: {e}")

def get_api_key():
    """
    获取Gemini API密钥，优先级：
    1. 环境变量 GEMINI_API_KEY
    2. 配置文件中的API部分的GEMINI_API_KEY

    Returns:
        API密钥字符串，如果未找到则返回None
    """
    # 首先检查环境变量
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        return api_key

    # 然后检查配置文件
    config = load_config()
    return config['API'].get('GEMINI_API_KEY')

def get_default_settings():
    """
    获取默认设置，从配置文件的SETTINGS部分读取

    Returns:
        包含默认设置的字典
    """
    config = load_config()

    # 确保SETTINGS部分存在
    if 'SETTINGS' not in config:
        config['SETTINGS'] = {
            'default_model': 'base',
            'default_output_format': 'srt,vtt,txt',
            'default_language': 'en',
            'default_dest_language': 'zh-CN',
            'default_subtitle_type': 'original',
            'default_subtitle_font_size': '28',
            'default_subtitle_position': 'bottom',
            'default_subtitle_font_color': 'white',
            'default_subtitle_outline_color': 'black',
            'default_subtitle_shadow_radius': '1.0',
            'default_burn_subtitles': 'false'
        }
        save_config(config)

    settings = config['SETTINGS']
    return {
        'model': settings.get('default_model', 'base'),
        'output_format': settings.get('default_output_format', 'srt,vtt,txt'),
        'language': settings.get('default_language', 'en'),
        'dest_language': settings.get('default_dest_language', 'zh-CN'),
        'subtitle_type': settings.get('default_subtitle_type', 'original'),
        'subtitle_font_size': int(settings.get('default_subtitle_font_size', '28')),
        'subtitle_position': settings.get('default_subtitle_position', 'bottom'),
        'subtitle_font_color': settings.get('default_subtitle_font_color', 'white'),
        'subtitle_outline_color': settings.get('default_subtitle_outline_color', 'black'),
        'subtitle_shadow_radius': float(settings.get('default_subtitle_shadow_radius', '1.0')),
        'burn_subtitles': settings.get('default_burn_subtitles', 'false').lower() == 'true'
    }

def set_api_key(api_key):
    """
    设置Gemini API密钥到配置文件

    Args:
        api_key: API密钥字符串
    """
    config = load_config()
    config['API']['GEMINI_API_KEY'] = api_key
    save_config(config)
    print("API密钥已保存到配置文件")
