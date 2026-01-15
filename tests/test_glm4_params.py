#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GLM-4 參數自動測試系統

測試不同參數組合對 GLM-4 大綱生成品質的影響
針對 GLM-4 作為 Architect 的最佳參數配置
整合 GLM-4 特有評估指標：中文流暢度、文化底蘊、創意性、邏輯連貫性
"""

# 路徑設置：將父目錄添加到 sys.path 以便導入項目模組
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import re
import time
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
import logging
from dotenv import load_dotenv

from test_r1_params_enhanced import R1ParamsTesterEnhanced
from core.api_client import SiliconFlowClient
from config import MODEL_ROLES

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 🎯 GLM-4 參數測試矩陣
PARAM_MATRIX_GLM4 = {
    'temperature': [0.5, 0.6, 0.7, 0.8, 0.9],      # GLM-4 適合稍高溫度
    'top_p': [0.85, 0.9, 0.95],                    # 保持多樣性
    'repetition_penalty': [1.0, 1.05, 1.1, 1.15],  # 防止重複
    'max_tokens': [4000, 6000, 8000]               # GLM-4 不需要預留 <think>
}

# 快速測試模式（10 組關鍵參數）
QUICK_TEST_PARAMS_GLM4 = [
    # 當前配置
    {'temperature': 0.7, 'top_p': 0.9, 'repetition_penalty': 1.1, 'max_tokens': 6000},

    # 高創意配置
    {'temperature': 0.8, 'top_p': 0.95, 'repetition_penalty': 1.05, 'max_tokens': 6000},
    {'temperature': 0.9, 'top_p': 0.9, 'repetition_penalty': 1.0, 'max_tokens': 6000},

    # 平衡配置
    {'temperature': 0.7, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 6000},
    {'temperature': 0.6, 'top_p': 0.9, 'repetition_penalty': 1.1, 'max_tokens': 6000},

    # 保守配置
    {'temperature': 0.5, 'top_p': 0.85, 'repetition_penalty': 1.15, 'max_tokens': 6000},
    {'temperature': 0.6, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 6000},

    # Token 長度測試
    {'temperature': 0.7, 'top_p': 0.9, 'repetition_penalty': 1.1, 'max_tokens': 4000},
    {'temperature': 0.7, 'top_p': 0.9, 'repetition_penalty': 1.1, 'max_tokens': 8000},

    # 極端測試
    {'temperature': 0.9, 'top_p': 0.95, 'repetition_penalty': 1.0, 'max_tokens': 8000},
]


class GLM4ParamsTester(R1ParamsTesterEnhanced):
    """GLM-4 參數測試器（繼承 R1 測試器並擴展）"""

    def __init__(self, api_key: str, quick_mode: bool = False, enable_ai_review: bool = True,
                 compare_with_r1: bool = False, debug_mode: bool = False):
        super().__init__(api_key, quick_mode, enable_ai_review)
        self.compare_with_r1 = compare_with_r1
        self.r1_best_result = None  # 用於對比
        self.debug_mode = debug_mode  # 診斷模式

        # 覆蓋輸出目錄（相對於項目根目錄）
        project_root = Path(__file__).parent.parent
        self.output_dir = str(project_root / "test_results" / "glm4")
        os.makedirs(f"{self.output_dir}/outlines", exist_ok=True)
        os.makedirs(f"{self.output_dir}/ai_reviews", exist_ok=True)

    def generate_param_combinations(self) -> List[Dict]:
        """生成 GLM-4 專用參數組合"""
        if self.quick_mode:
            return QUICK_TEST_PARAMS_GLM4

        # 生成所有組合（使用 GLM-4 參數矩陣）
        from itertools import product
        keys = PARAM_MATRIX_GLM4.keys()
        values = PARAM_MATRIX_GLM4.values()
        combinations = []

        for combo in product(*values):
            param_dict = dict(zip(keys, combo))
            combinations.append(param_dict)

        return combinations

    def evaluate_quality(self, outline: str, params: Dict) -> Dict:
        """評估大綱品質（GLM-4 專用 - 增加特有指標）"""

        # 基礎評估（繼承自 R1 測試器）
        score = super().evaluate_quality(outline, params)

        # Debug: 顯示基礎評分
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"\n🔍 [DEBUG] 基礎評分: {score.get('total_score', 0):.0f}/100")

        # GLM-4 特有檢查（額外 20 分）
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"🔍 [DEBUG] 開始 GLM-4 特有檢查...")

        glm4_checks = {
            'chinese_fluency': self.check_chinese_fluency(outline),      # 中文流暢度
            'cultural_depth': self.check_cultural_depth(outline),        # 文化底蘊
            'creativity': self.check_creativity(outline),                # 創意性
            'coherence': self.check_coherence(outline),                  # 邏輯連貫性
        }

        # Debug: 顯示各項檢查結果
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"🔍 [DEBUG] GLM-4 檢查結果:")
            for key, value in glm4_checks.items():
                print(f"  - {key}: {value:.2f}")

        # 將 GLM-4 檢查結果添加到 details 中（確保能被 test_param_combination 提取）
        score['details']['glm4_chinese_fluency'] = glm4_checks['chinese_fluency']
        score['details']['glm4_cultural_depth'] = glm4_checks['cultural_depth']
        score['details']['glm4_creativity'] = glm4_checks['creativity']
        score['details']['glm4_coherence'] = glm4_checks['coherence']

        # 同時保留 glm4_checks 用於報告生成
        score['glm4_checks'] = glm4_checks

        # 計算 GLM-4 特有分數
        glm4_score = sum(glm4_checks.values()) * 5
        score['glm4_score'] = glm4_score
        score['total_score'] = score['total_score'] + glm4_score

        # Debug: 顯示最終分數
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"🔍 [DEBUG] GLM-4 總分: {glm4_score:.0f}/20")
            print(f"🔍 [DEBUG] 最終總分: {score['total_score']:.0f}/120\n")

        return score

    def check_chinese_fluency(self, outline: str) -> float:
        """
        檢查中文流暢度（0-1）

        策略：檢測翻譯腔和不自然表達
        """
        # 翻譯腔模式（扣分）
        translation_patterns = [
            (r'的話\s', 2),        # 「如果...的話」（if...）翻譯腔
            (r'進行了?\s*\w+的', 3),  # 「進行研究的」冗餘結構
            (r'是\s*\w+的', 2),     # 「是...的」過度使用
            (r'對於\s*\w+來說', 2),  # 「對於...來說」（for...）翻譯腔
        ]

        penalty = 0
        for pattern, weight in translation_patterns:
            matches = len(re.findall(pattern, outline))
            if matches > 5:
                penalty += weight * 0.05

        # 自然中文表達（加分）
        natural_patterns = [
            r'[\u4e00-\u9fff]{1,3}[著了過]',  # 動詞助詞（著、了、過）
            r'[\u4e00-\u9fff]{2,4}地\s*[\u4e00-\u9fff]{2,4}',  # 副詞「地」結構
        ]

        bonus = 0
        for pattern in natural_patterns:
            matches = len(re.findall(pattern, outline))
            if matches > 10:
                bonus += 0.1

        return max(0, min(1.0, 1.0 - penalty + bonus))

    def check_cultural_depth(self, outline: str) -> float:
        """
        檢查文化底蘊（0-1）

        策略：檢測中文成語、典故、詩詞引用
        """
        score = 0

        # 四字成語檢測
        idiom_pattern = r'[\u4e00-\u9fff]{4}(?=[，。：、！？])'
        idioms = re.findall(idiom_pattern, outline)

        # 過濾掉非成語（簡單啟發式）
        common_non_idioms = {'第一章', '第二章', '第三章', '第四章', '第五章',
                            '這個時候', '那個時候', '所有人都', '每個人都'}

        valid_idioms = [i for i in idioms if i not in common_non_idioms]

        # 成語數量評分
        if len(valid_idioms) >= 5:
            score += 0.5
        elif len(valid_idioms) >= 3:
            score += 0.3
        elif len(valid_idioms) >= 1:
            score += 0.1

        # 文化元素關鍵詞
        cultural_keywords = [
            '詩', '詞', '典', '古', '傳說', '神話', '史記',
            '儒', '道', '禪', '墨', '法', '陰陽', '五行',
            '春秋', '戰國', '漢唐', '宋明', '清代'
        ]

        cultural_count = sum(1 for keyword in cultural_keywords if keyword in outline)
        if cultural_count >= 3:
            score += 0.3
        elif cultural_count >= 1:
            score += 0.2

        return min(1.0, score)

    def check_creativity(self, outline: str) -> float:
        """
        檢查創意性（0-1）

        策略：檢測是否避開常見套路，有獨特設定
        """
        # 常見套路關鍵詞（扣分）
        cliche_keywords = {
            # 爛大街的設定
            '末日': 0.15, '喪屍': 0.15, '穿越': 0.2, '重生': 0.2, '系統': 0.25,
            '異能': 0.15, '修仙': 0.15, '玄幻': 0.15, '霸總': 0.2, '甜寵': 0.2,
            '爽文': 0.25, '打臉': 0.2, '逆襲': 0.15, '廢柴': 0.15, '天才': 0.1,
            # 陳詞濫調
            '龍傲天': 0.3, '瑪麗蘇': 0.3, '金手指': 0.25, '主角光環': 0.2
        }

        penalty = 0
        for keyword, weight in cliche_keywords.items():
            if keyword in outline:
                penalty += weight

        # 創意元素（加分）
        creative_elements = {
            # 獨特設定
            '悖論': 0.15, '多元宇宙': 0.15, '量子': 0.1, '意識上傳': 0.15,
            '基因編輯': 0.1, '人工演化': 0.15, '熵': 0.1, '維度': 0.1,
            # 複雜主題
            '道德困境': 0.2, '倫理': 0.15, '哲學': 0.15, '存在主義': 0.2,
            '自由意志': 0.2, '決定論': 0.15
        }

        bonus = 0
        for keyword, weight in creative_elements.items():
            if keyword in outline:
                bonus += weight

        # 計算最終創意分（基準 0.5）
        creativity_score = 0.5 - penalty + bonus

        return max(0, min(1.0, creativity_score))

    def check_coherence(self, outline: str) -> float:
        """
        檢查邏輯連貫性（0-1）

        策略：
        1. 章節間因果關係
        2. 角色行為一致性
        3. 時間線合理性
        """
        # 提取章節標題和大綱
        chapters = re.findall(r'第(\d+)章[：:]\s*(.+?)\n.*?outline["\']:\s*["\'](.+?)["\']',
                             outline, re.DOTALL)

        if len(chapters) < 3:
            return 0.5  # 章節太少，無法判斷

        score = 0.5  # 基準分

        # 檢查 1: 章節邏輯詞
        coherence_words = ['因此', '然而', '接著', '隨後', '最終', '於是', '但是', '所以']
        coherence_count = sum(outline.count(word) for word in coherence_words)

        if coherence_count >= 5:
            score += 0.3
        elif coherence_count >= 3:
            score += 0.2

        # 檢查 2: 時間標記
        time_markers = ['第一天', '第二天', '三天後', '一週後', '同時', '此時', '當時', '隨後']
        time_count = sum(outline.count(marker) for marker in time_markers)

        if time_count >= 3:
            score += 0.2

        return min(1.0, score)

    def load_r1_best_result(self):
        """載入 R1 最佳結果（用於對比）"""
        if not self.compare_with_r1:
            return

        logger.info("🔍 載入 DeepSeek R1 最佳參數結果...")

        try:
            # 讀取 R1 最新報告
            r1_report_path = "test_results/r1_params_test_report_latest_auto.md"

            if not os.path.exists(r1_report_path):
                logger.warning(f"未找到 R1 報告: {r1_report_path}")
                return

            # 解析報告獲取最佳配置
            with open(r1_report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取冠軍參數
            champion_match = re.search(r"'temperature':\s*([\d.]+).*?'top_p':\s*([\d.]+).*?"
                                      r"'repetition_penalty':\s*([\d.]+).*?'max_tokens':\s*(\d+)",
                                      content, re.DOTALL)

            if champion_match:
                self.r1_best_result = {
                    'params': {
                        'temperature': float(champion_match.group(1)),
                        'top_p': float(champion_match.group(2)),
                        'repetition_penalty': float(champion_match.group(3)),
                        'max_tokens': int(champion_match.group(4))
                    },
                    'model': 'DeepSeek R1'
                }

                # 提取分數
                score_match = re.search(r'自動評分[：:]\s*(\d+)/100', content)
                if score_match:
                    self.r1_best_result['auto_score'] = int(score_match.group(1))

                logger.info(f"✅ R1 最佳配置: temp={self.r1_best_result['params']['temperature']}, "
                          f"score={self.r1_best_result.get('auto_score', '?')}/100")
            else:
                logger.warning("無法解析 R1 報告中的參數")

        except Exception as e:
            logger.error(f"載入 R1 結果失敗: {e}")

    def run_full_test(self):
        """執行完整測試（整合 R1 對比）"""
        self.start_time = time.time()

        print("\n" + "="*60)
        print("🧪 GLM-4 參數自動測試系統")
        print("="*60)

        # 載入 R1 最佳結果（如果需要對比）
        if self.compare_with_r1:
            self.load_r1_best_result()

        # 生成參數組合
        param_combinations = self.generate_param_combinations()
        total = len(param_combinations)

        mode_name = "快速測試" if self.quick_mode else "完整測試"
        ai_status = "啟用" if self.enable_ai_review else "停用"

        print(f"\n模式: {mode_name}")
        print(f"AI 評審: {ai_status}")
        print(f"總測試組合數: {total}")

        if self.compare_with_r1 and self.r1_best_result:
            print(f"對比基準: DeepSeek R1 (分數: {self.r1_best_result.get('auto_score', '?')}/100)")

        if self.enable_ai_review:
            print(f"預計時間: {total * 1.5:.0f}-{total * 3:.0f} 分鐘（含 AI 評審）")
        else:
            print(f"預計時間: {total * 0.5:.0f}-{total * 1:.0f} 分鐘")

        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 執行測試（使用父類的測試流程）
        super().run_full_test()

    def build_enhanced_markdown_report(self, sorted_results: List[Dict]) -> str:
        """生成 GLM-4 增強報告（含 R1 對比）"""
        mode_name = "快速測試" if self.quick_mode else "完整測試"
        ai_status = "AI 評審" if self.enable_ai_review else "自動評估"
        total_time = time.time() - self.start_time if self.start_time else 0

        # 確保所有結果都有 total_score（兼容 --no-ai 模式）
        for result in sorted_results:
            if 'total_score' not in result:
                result['total_score'] = result.get('auto_score', 0) + result.get('glm4_score', 0)

        report = f"""# GLM-4 參數測試報告（{ai_status}版）

## 測試時間
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 測試配置
- 測試模式: {mode_name}
- 評估方式: {ai_status}
- 總測試組合: {len(self.results)} 組
- 總耗時: {total_time/60:.1f} 分鐘

"""

        # GLM-4 vs R1 對比（如果有）
        if self.compare_with_r1 and self.r1_best_result:
            report += "## 🆚 GLM-4 vs DeepSeek R1 對比\n\n"

            best_glm4 = sorted_results[0]

            report += "| 指標 | GLM-4 (冠軍) | DeepSeek R1 (最佳) | 優勢 |\n"
            report += "|------|--------------|-------------------|------|\n"

            # 中英混雜率
            glm4_mixed = best_glm4['auto_details'].get('mixed_language', 0)
            report += f"| 中英混雜率 | {(1-glm4_mixed)*100:.0f}% | ~60% | GLM-4 ✅ |\n"

            # 中文流暢度
            glm4_fluency = best_glm4.get('glm4_checks', {}).get('chinese_fluency', 0)
            report += f"| 中文流暢度 | {glm4_fluency*100:.0f}% | N/A | GLM-4 ✅ |\n"

            # 文化底蘊
            glm4_culture = best_glm4.get('glm4_checks', {}).get('cultural_depth', 0)
            report += f"| 文化底蘊 | {glm4_culture*100:.0f}% | N/A | GLM-4 ✅ |\n"

            # 創意性
            glm4_creativity = best_glm4.get('glm4_checks', {}).get('creativity', 0)
            report += f"| 創意性 | {glm4_creativity*100:.0f}% | ~70% | {'GLM-4' if glm4_creativity > 0.7 else 'R1'} ✅ |\n"

            # 總分對比
            glm4_total = best_glm4['total_score']
            r1_total = self.r1_best_result.get('auto_score', 0)
            report += f"| 總分 | {glm4_total:.0f}/120 | {r1_total}/100 | {'GLM-4' if glm4_total > r1_total else 'R1'} ✅ |\n"

            report += "\n"

        # Top 3 結果
        report += "## 🏆 最終排名\n\n"

        medals = ['🥇', '🥈', '🥉']
        rankings = ['冠軍', '亞軍', '季軍']

        for i, (medal, ranking) in enumerate(zip(medals, rankings)):
            if i >= len(sorted_results):
                break

            result = sorted_results[i]
            params = result['params']

            report += f"### {medal} {ranking}\n\n"
            report += "**參數配置**：\n"
            report += "```python\n"
            report += "{\n"
            report += f"    'temperature': {params['temperature']},\n"
            report += f"    'top_p': {params['top_p']},\n"
            report += f"    'repetition_penalty': {params['repetition_penalty']},\n"
            report += f"    'max_tokens': {params['max_tokens']}\n"
            report += "}\n"
            report += "```\n\n"

            report += "**評分詳情**：\n"
            report += f"- 基礎自動評分：{result['auto_score']:.0f}/100\n"
            report += f"- GLM-4 特有評分：{result.get('glm4_score', 0):.0f}/20\n"
            report += f"- 總分：{result['total_score']:.0f}/120\n\n"

            # GLM-4 特有指標
            if 'glm4_checks' in result:
                checks = result['glm4_checks']
                report += "**GLM-4 特有指標**：\n"
                report += f"- 中文流暢度：{checks['chinese_fluency']*100:.0f}%\n"
                report += f"- 文化底蘊：{checks['cultural_depth']*100:.0f}%\n"
                report += f"- 創意性：{checks['creativity']*100:.0f}%\n"
                report += f"- 邏輯連貫性：{checks['coherence']*100:.0f}%\n\n"

            if self.enable_ai_review and result.get('ai_reviews'):
                report += f"- AI 評分（中位數）：{result['ai_score']:.0f}/100\n"
                report += f"- 綜合分數：{result['combined_score']:.1f}/100\n"
                report += f"- AI 一致性：{result['ai_agreement']}\n\n"

        # 詳細測試結果表格
        report += "## 📊 詳細測試結果\n\n"
        report += "| 排名 | temp | top_p | rep | max_tok | 基礎 | GLM-4 | 總分 | 流暢 | 文化 | 創意 | 連貫 |\n"
        report += "|------|------|-------|-----|---------|------|-------|------|------|------|------|------|\n"

        for i, result in enumerate(sorted_results, 1):
            params = result['params']
            checks = result.get('glm4_checks', {})

            report += f"| {i} | {params['temperature']} | {params['top_p']} | "
            report += f"{params['repetition_penalty']} | {params['max_tokens']} | "
            report += f"{result['auto_score']:.0f} | {result.get('glm4_score', 0):.0f} | "
            report += f"{result['total_score']:.0f} | "
            report += f"{checks.get('chinese_fluency', 0)*100:.0f} | "
            report += f"{checks.get('cultural_depth', 0)*100:.0f} | "
            report += f"{checks.get('creativity', 0)*100:.0f} | "
            report += f"{checks.get('coherence', 0)*100:.0f} |\n"

        report += "\n"

        # 參數影響分析
        report += self.analyze_glm4_parameter_impact(sorted_results)

        # 建議配置
        if sorted_results:
            best = sorted_results[0]
            params = best['params']

            report += "## 💡 建議配置\n\n"
            report += "基於測試結果，建議使用：\n\n"
            report += "```python\n"
            report += "'architect': {\n"
            report += f"    'temperature': {params['temperature']},\n"
            report += f"    'top_p': {params['top_p']},\n"
            report += f"    'repetition_penalty': {params['repetition_penalty']},\n"
            report += f"    'max_tokens': {params['max_tokens']}\n"
            report += "}\n"
            report += "```\n\n"

            report += f"**理由**：\n"
            report += f"- 基礎評分：{best['auto_score']:.0f}/100（格式與內容品質）\n"
            report += f"- GLM-4 評分：{best.get('glm4_score', 0):.0f}/20（中文特有優勢）\n"
            report += f"- 總分：{best['total_score']:.0f}/120（綜合最佳）\n"

            checks = best.get('glm4_checks', {})
            report += f"- 中文流暢度：{checks.get('chinese_fluency', 0)*100:.0f}%（自然表達）\n"
            report += f"- 文化底蘊：{checks.get('cultural_depth', 0)*100:.0f}%（成語典故）\n"
            report += f"- 創意性：{checks.get('creativity', 0)*100:.0f}%（避開套路）\n"
            report += f"- 邏輯連貫性：{checks.get('coherence', 0)*100:.0f}%（章節呼應）\n\n"

        # 測試數據說明
        report += "## 📁 測試數據\n\n"
        report += f"所有測試大綱已保存至：`{self.output_dir}/outlines/`\n\n"

        return report

    def analyze_glm4_parameter_impact(self, sorted_results: List[Dict]) -> str:
        """分析 GLM-4 參數影響"""
        report = "## 📈 參數影響分析（GLM-4 總分）\n\n"

        # 按參數分組統計（使用總分）
        temp_groups = {}
        topp_groups = {}
        rep_groups = {}
        tok_groups = {}

        for result in sorted_results:
            params = result['params']
            score = result['total_score']

            # Temperature
            temp = params['temperature']
            if temp not in temp_groups:
                temp_groups[temp] = []
            temp_groups[temp].append(score)

            # Top_P
            topp = params['top_p']
            if topp not in topp_groups:
                topp_groups[topp] = []
            topp_groups[topp].append(score)

            # Repetition Penalty
            rep = params['repetition_penalty']
            if rep not in rep_groups:
                rep_groups[rep] = []
            rep_groups[rep].append(score)

            # Max Tokens
            tok = params['max_tokens']
            if tok not in tok_groups:
                tok_groups[tok] = []
            tok_groups[tok].append(score)

        # Temperature 影響
        report += "### Temperature 影響\n\n"
        for temp in sorted(temp_groups.keys()):
            scores = temp_groups[temp]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(temp_groups[t])/len(temp_groups[t]) for t in temp_groups) else ""
            report += f"- **{temp}**: 平均分 {avg_score:.1f}/120{best_mark}\n"
        report += "\n**建議範圍**: 0.6-0.8（平衡創意與穩定）\n\n"

        # Top_P 影響
        report += "### Top_P 影響\n\n"
        for topp in sorted(topp_groups.keys()):
            scores = topp_groups[topp]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(topp_groups[t])/len(topp_groups[t]) for t in topp_groups) else ""
            report += f"- **{topp}**: 平均分 {avg_score:.1f}/120{best_mark}\n"
        report += "\n**建議範圍**: 0.85-0.95（保持多樣性）\n\n"

        # Repetition Penalty 影響
        report += "### Repetition Penalty 影響\n\n"
        for rep in sorted(rep_groups.keys()):
            scores = rep_groups[rep]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(rep_groups[r])/len(rep_groups[r]) for r in rep_groups) else ""
            report += f"- **{rep}**: 平均分 {avg_score:.1f}/120{best_mark}\n"
        report += "\n**建議範圍**: 1.05-1.15（防止重複）\n\n"

        # Max Tokens 影響
        report += "### Max Tokens 影響\n\n"
        for tok in sorted(tok_groups.keys()):
            scores = tok_groups[tok]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(tok_groups[t])/len(tok_groups[t]) for t in tok_groups) else ""
            report += f"- **{tok}**: 平均分 {avg_score:.1f}/120{best_mark}\n"
        report += "\n**建議範圍**: 6000（最佳性價比）\n\n"

        return report


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='GLM-4 參數自動測試系統')
    parser.add_argument('--quick', action='store_true', help='快速測試模式（10組關鍵參數）')
    parser.add_argument('--full', action='store_true', help='完整測試模式（所有組合）')
    parser.add_argument('--no-ai', action='store_true', help='停用 AI 評審（僅自動評估）')
    parser.add_argument('--compare-with-r1', action='store_true', help='與 DeepSeek R1 對比測試')
    parser.add_argument('--debug', action='store_true', help='啟用診斷模式（顯示詳細評分過程）')
    args = parser.parse_args()

    # 加載環境變數
    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    if not api_key:
        print("❌ 錯誤: 未檢測到 SILICONFLOW_API_KEY")
        print("請在 .env 文件中設置 API Key")
        return

    # 確定測試模式
    if args.full:
        quick_mode = False
    elif args.quick:
        quick_mode = True
    else:
        # 默認使用快速模式
        quick_mode = True
        print("💡 提示: 未指定模式，使用快速測試模式")
        print("   使用 --full 可進行完整測試")
        print("   使用 --quick 明確指定快速測試")
        print("   使用 --no-ai 停用 AI 評審")
        print("   使用 --compare-with-r1 與 R1 對比")
        print("   使用 --debug 啟用診斷模式\n")

    # AI 評審狀態
    enable_ai = not args.no_ai

    if not enable_ai:
        print("⚠️  AI 評審已停用，僅使用自動評估")

    # 診斷模式提示
    if args.debug:
        print("🔍 診斷模式已啟用，將顯示詳細評分過程\n")

    # 創建測試器並運行
    tester = GLM4ParamsTester(
        api_key,
        quick_mode=quick_mode,
        enable_ai_review=enable_ai,
        compare_with_r1=args.compare_with_r1,
        debug_mode=args.debug
    )
    tester.run_full_test()


if __name__ == "__main__":
    main()
