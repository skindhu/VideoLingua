#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Google Gemini API的工具模块
"""

import os
import json
import time
import requests
import logging
from typing import List, Dict, Any, Optional, Union
from .config import get_api_key

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gemini_api')

class GeminiAPI:
    """使用Google Gemini API的工具类"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Gemini API客户端

        Args:
            api_key: Gemini API密钥，如果为None，则尝试从环境变量GEMINI_API_KEY获取
        """
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise ValueError("必须提供Gemini API密钥，可以通过参数传入、环境变量GEMINI_API_KEY设置或保存在配置文件中")

        # 使用gemini-2.0-flash模型：generativelanguage.googleapis.com
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        logger.info(f"初始化Gemini API，使用URL: {self.api_url}")
        logger.info(f"API密钥: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
        self.session = requests.Session()

    def generate_content(self, prompt: Union[str, List[Dict[str, Any]]], temperature: float = 0.2,
                        top_p: float = 0.8, top_k: int = 40,
                        max_output_tokens: int = 8192) -> str:
        """
        使用Gemini API生成内容

        Args:
            prompt: 提示词，可以是字符串或消息列表格式
            temperature: 温度参数，控制输出的随机性
            top_p: 控制输出多样性的参数
            top_k: 控制输出多样性的参数
            max_output_tokens: 最大输出token数量

        Returns:
            生成的内容
        """
        try:
            # 构建API请求
            params = {"key": self.api_key}

            # 根据prompt类型构建不同的请求体
            if isinstance(prompt, str):
                # 字符串格式的提示词
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": temperature,
                        "topP": top_p,
                        "topK": top_k,
                        "maxOutputTokens": max_output_tokens,
                    }
                }
                logger.info(f"提示词: {prompt[:50]}..." if len(prompt) > 50 else f"提示词: {prompt}")
            else:
                # 消息列表格式的提示词
                contents = []
                for message in prompt:
                    role = message.get("role", "user")
                    parts = message.get("parts", [])

                    if role == "system":
                        # 系统消息作为模型设置
                        system_instruction = parts[0] if parts else ""
                        logger.info(f"系统指令: {system_instruction[:50]}..." if len(system_instruction) > 50 else f"系统指令: {system_instruction}")
                    else:
                        # 用户消息添加到contents
                        content = {
                            "role": role,
                            "parts": [{"text": part} if isinstance(part, str) else part for part in parts]
                        }
                        contents.append(content)

                        # 记录用户消息
                        if role == "user" and parts:
                            user_text = parts[0] if isinstance(parts[0], str) else str(parts[0])
                            logger.info(f"用户消息: {user_text[:50]}..." if len(user_text) > 50 else f"用户消息: {user_text}")

                payload = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": temperature,
                        "topP": top_p,
                        "topK": top_k,
                        "maxOutputTokens": max_output_tokens,
                    }
                }

                # 如果有系统指令，添加到请求中
                system_instruction = next((message.get("parts", [""])[0] for message in prompt if message.get("role") == "system"), None)
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

            # 记录请求信息
            logger.info(f"发送请求到 Gemini API")
            logger.info(f"参数: temperature={temperature}, top_p={top_p}, top_k={top_k}, max_tokens={max_output_tokens}")

            # 发送请求
            start_time = time.time()
            response = self.session.post(
                self.api_url,
                params=params,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            elapsed_time = time.time() - start_time

            # 记录响应信息
            logger.info(f"收到响应，状态码: {response.status_code}，耗时: {elapsed_time:.2f}秒")

            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    logger.info(f"成功生成内容，长度: {len(generated_text)}")
                    logger.info(f"生成内容预览: {generated_text[:50]}..." if len(generated_text) > 50 else f"生成内容: {generated_text}")
                    return generated_text.strip()
                else:
                    logger.error(f"Gemini API返回了空结果: {result}")
                    print(f"Gemini API返回了空结果: {result}")
                    return ""
            else:
                logger.error(f"Gemini API请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")

                # 检查是否是地区限制错误
                if response.status_code == 400 and "User location is not supported" in response.text:
                    error_msg = "错误: 您当前的地区不支持使用Google Gemini API。请使用原始语言字幕类型(original)，或考虑使用VPN服务。"
                    logger.error(error_msg)
                    print(error_msg)
                else:
                    print(f"Gemini API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return ""

        except Exception as e:
            logger.exception(f"Gemini API调用过程中出错")
            print(f"Gemini API调用过程中出错: {e}")
            return ""

def get_gemini_api(api_key: Optional[str] = None) -> GeminiAPI:
    """
    获取Gemini API实例

    Args:
        api_key: Gemini API密钥，如果为None，则尝试从环境变量获取

    Returns:
        Gemini API实例
    """
    return GeminiAPI(api_key)

# 简单的命令行接口，用于测试
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="使用Google Gemini API生成内容")
    parser.add_argument("prompt", help="提示词")
    parser.add_argument("--temperature", type=float, default=0.2, help="温度参数 (默认: 0.2)")
    parser.add_argument("--api-key", help="Gemini API密钥 (也可通过GEMINI_API_KEY环境变量设置)")

    args = parser.parse_args()

    try:
        gemini_api = get_gemini_api(args.api_key)
        generated = gemini_api.generate_content(args.prompt, args.temperature)
        print(f"提示词: {args.prompt}")
        print(f"生成内容: {generated}")
    except Exception as e:
        print(f"错误: {e}")
