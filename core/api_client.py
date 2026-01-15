# -*- coding: utf-8 -*-
"""
AI 小說生成器 - API 客戶端
"""

import requests
import time
import logging
import re
from typing import Dict, Optional
from config import API_CONFIG, MODELS

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SiliconFlowClient:
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or API_CONFIG['default_model']
        self.base_url = API_CONFIG['base_url']
        self.timeout = API_CONFIG['timeout']
        self.max_retries = API_CONFIG['max_retries']

        # 統計
        self.total_tokens_input = 0
        self.total_tokens_output = 0
        self.total_cost = 0.0
        self.request_count = 0

    def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        生成文本（簡化版，直接返回字符串）

        Args:
            prompt: 提示詞
            model: 指定模型（可選）
            **kwargs: 其他參數（temperature, max_tokens 等）

        Returns:
            生成的文本內容
        """
        target_model = model or self.model
        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            **kwargs
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()

                content = response.json()['choices'][0]['message']['content']

                # 🔥 DeepSeek R1 專用濾網：移除 <think> 標籤
                if '<think>' in content:
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                # 更新統計
                usage = response.json().get('usage', {})
                self.total_tokens_input += usage.get('prompt_tokens', 0)
                self.total_tokens_output += usage.get('completion_tokens', 0)
                self.request_count += 1

                return content

            except Exception as e:
                logger.warning(f"請求失敗 ({attempt+1}/{self.max_retries}): {e}")
                time.sleep(2)

        raise Exception("API 調用多次失敗")

    def generate_with_details(self, prompt: str, temperature: float = 0.8, max_tokens: int = 5000,
                             model: str = None, top_p: float = None, repetition_penalty: float = None) -> Dict:
        """
        生成文本（詳細版，返回完整信息）

        Args:
            prompt: 提示詞
            temperature: 溫度參數
            max_tokens: 最大 token 數
            model: 指定模型（可選，默認使用初始化時的模型）
            top_p: 核採樣參數（可選）
            repetition_penalty: 重複懲罰參數（可選）

        Returns:
            包含生成結果的字典
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        target_model = model or self.model

        data = {
            'model': target_model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        # 添加可選參數
        if top_p is not None:
            data['top_p'] = top_p
        if repetition_penalty is not None:
            data['repetition_penalty'] = repetition_penalty

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"發送 API 請求（第 {attempt + 1}/{self.max_retries} 次）")

                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                result = response.json()

                if 'choices' not in result or len(result['choices']) == 0:
                    raise Exception(f"API 回應格式異常: {result}")

                content = result['choices'][0]['message']['content']

                # 🔥 DeepSeek R1 專用濾網：移除 <think> 標籤
                if '<think>' in content:
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                usage = result.get('usage', {})
                tokens_input = usage.get('prompt_tokens', 0)
                tokens_output = usage.get('completion_tokens', 0)

                cost = self._calculate_cost(tokens_input, tokens_output)

                self.total_tokens_input += tokens_input
                self.total_tokens_output += tokens_output
                self.total_cost += cost
                self.request_count += 1

                logger.info(f"API 請求成功")
                logger.info(f"Token 使用: 輸入 {tokens_input}, 輸出 {tokens_output}")
                logger.info(f"本次成本: ¥{cost:.4f}")

                return {
                    'content': content,
                    'tokens_input': tokens_input,
                    'tokens_output': tokens_output,
                    'cost': cost
                }

            except requests.exceptions.Timeout:
                last_error = "請求超時"
                logger.warning(f"請求超時（第 {attempt + 1} 次）")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

            except requests.exceptions.ConnectionError:
                last_error = "網路連接失敗"
                logger.warning(f"網路連接失敗（第 {attempt + 1} 次）")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

            except Exception as e:
                last_error = str(e)
                logger.error(f"API 調用失敗: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

        error_msg = f"API 調用失敗（已重試 {self.max_retries} 次）: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """計算成本"""
        if self.model not in MODELS:
            logger.warning(f"未知模型 {self.model}，無法計算成本")
            return 0.0

        model_info = MODELS[self.model]
        price_input = model_info['price_input']
        price_output = model_info['price_output']

        cost_input = (tokens_input / 1000) * price_input
        cost_output = (tokens_output / 1000) * price_output

        return cost_input + cost_output

    def get_statistics(self):
        """獲取統計信息"""
        return {
            'model': self.model,
            'request_count': self.request_count,
            'total_tokens': self.total_tokens_input + self.total_tokens_output,
            'total_cost': 0.0  # 免費模型，成本為 0
        }

    def print_statistics(self):
        """打印統計信息"""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("📊 API 調用統計")
        print("="*60)
        print(f"模型.................... {stats['model']}")
        print(f"請求次數................ {stats['request_count']}")
        print(f"總 Token 使用........... {stats['total_tokens']:,}")
        print(f"  ├─ 輸入............... {self.total_tokens_input:,}")
        print(f"  └─ 輸出............... {self.total_tokens_output:,}")
        print(f"總成本.................. ¥{stats['total_cost']:.4f} (免費)")
        print("="*60 + "\n")


if __name__ == '__main__':
    # 測試
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    if api_key:
        client = SiliconFlowClient(api_key)

        # 測試請求
        result = client.generate("請用一句話介紹自己。", max_tokens=100)
        print("生成結果:", result)

        # 打印統計
        client.print_statistics()
    else:
        print("請設定 SILICONFLOW_API_KEY 環境變數")
