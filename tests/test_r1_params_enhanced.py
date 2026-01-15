#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek R1 參數自動測試系統（AI 評審增強版）

測試不同參數組合對大綱生成品質的影響
整合對抗式評估、多 AI 投票和相對排名法
"""

# 路徑設置：將父目錄添加到 sys.path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import re
import time
import random
import argparse
from datetime import datetime
from itertools import product
from typing import Dict, List, Tuple
import logging
from dotenv import load_dotenv

from core.generator import NovelGenerator
from core.api_client import SiliconFlowClient
from utils.json_parser import RobustJSONParser
from config import MODEL_ROLES

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 參數測試矩陣
PARAM_MATRIX = {
    'temperature': [0.3, 0.4, 0.5, 0.6, 0.7],
    'top_p': [0.8, 0.85, 0.9, 0.95],
    'repetition_penalty': [1.0, 1.05, 1.1, 1.15],
    'max_tokens': [6000, 8000, 10000]
}

# 快速測試模式（關鍵參數組合）
QUICK_PARAM_COMBINATIONS = [
    {'temperature': 0.3, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 8000},
    {'temperature': 0.4, 'top_p': 0.8, 'repetition_penalty': 1.1, 'max_tokens': 8000},
    {'temperature': 0.4, 'top_p': 0.85, 'repetition_penalty': 1.0, 'max_tokens': 8000},
    {'temperature': 0.4, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 6000},
    {'temperature': 0.4, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 8000},  # 緊急修復參數
    {'temperature': 0.4, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 10000},
    {'temperature': 0.4, 'top_p': 0.9, 'repetition_penalty': 1.1, 'max_tokens': 8000},
    {'temperature': 0.5, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 8000},
    {'temperature': 0.5, 'top_p': 0.95, 'repetition_penalty': 1.0, 'max_tokens': 8192},  # R1 官方參數
    {'temperature': 0.6, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 8000},
]


class R1ParamsTesterEnhanced:
    """DeepSeek R1 參數測試器（AI 評審增強版）"""

    def __init__(self, api_key: str, quick_mode: bool = False, enable_ai_review: bool = True):
        self.api_key = api_key
        self.quick_mode = quick_mode
        self.enable_ai_review = enable_ai_review
        self.results = []
        # 輸出目錄（相對於項目根目錄）
        project_root = Path(__file__).parent.parent
        self.output_dir = str(project_root / "test_results")
        self.start_time = None

        # 初始化 API 客戶端和 JSON 解析器
        self.api_client = SiliconFlowClient(api_key)
        self.json_parser = RobustJSONParser()

        # 創建輸出目錄
        os.makedirs(f"{self.output_dir}/outlines", exist_ok=True)
        os.makedirs(f"{self.output_dir}/ai_reviews", exist_ok=True)

    def generate_param_combinations(self) -> List[Dict]:
        """生成參數組合"""
        if self.quick_mode:
            return QUICK_PARAM_COMBINATIONS

        # 生成所有組合
        keys = PARAM_MATRIX.keys()
        values = PARAM_MATRIX.values()
        combinations = []

        for combo in product(*values):
            param_dict = dict(zip(keys, combo))
            combinations.append(param_dict)

        return combinations

    def adversarial_review(self, outline: str, model: str) -> Dict:
        """
        對抗式評估：AI 扮演挑剔編輯，找出 5 個致命缺陷

        Args:
            outline: 大綱文本
            model: 評審模型（DeepSeek/Qwen/GLM）

        Returns:
            {
                'model': 'DeepSeek',
                'fatal_flaws': [缺陷1, 缺陷2, ...],
                'flaw_count': 5,
                'severity_score': 85  # 100 - (缺陷數×嚴重度)
            }
        """

        prompt = f"""你是一位極度挑剔的資深小說編輯，專門找大綱的致命缺陷。

【任務】
請找出這份大綱的 5 個最嚴重的問題。如果找不到 5 個，說明品質很好。

【大綱】
{outline[:3000]}

【要求】
1. 只列出真正致命的缺陷（會讓讀者放棄的問題）
2. 每個缺陷要具體指出位置和原因
3. 按嚴重程度排序（最嚴重的放第一）

【輸出格式】
嚴格使用 JSON 格式：
{{
    "fatal_flaws": [
        {{"issue": "問題描述", "location": "第X章", "severity": "high/medium/low"}},
        ...
    ],
    "flaw_count": 實際找到的缺陷數量,
    "overall_verdict": "整體評價一句話"
}}

不要輸出思考過程，直接輸出 JSON。
"""

        try:
            # 調用 API（使用指定模型）
            response = self.api_client.generate(prompt, model=model, max_tokens=2000, temperature=0.3)

            # 解析 JSON
            result = self.json_parser.parse(response)

            # 確保有必要的字段
            if 'fatal_flaws' not in result:
                result['fatal_flaws'] = []
            if 'flaw_count' not in result:
                result['flaw_count'] = len(result['fatal_flaws'])
            if 'overall_verdict' not in result:
                result['overall_verdict'] = "無評價"

            # 計算嚴重度分數
            severity_map = {'high': 20, 'medium': 10, 'low': 5}
            severity_penalty = sum(severity_map.get(f.get('severity', 'medium'), 10)
                                  for f in result['fatal_flaws'])

            return {
                'model': model,
                'fatal_flaws': result['fatal_flaws'],
                'flaw_count': result['flaw_count'],
                'severity_score': max(0, 100 - severity_penalty),
                'verdict': result['overall_verdict']
            }

        except Exception as e:
            logger.error(f"對抗式評審失敗 ({model}): {e}")
            # 返回默認值
            return {
                'model': model,
                'fatal_flaws': [],
                'flaw_count': 0,
                'severity_score': 50,  # 默認中等分數
                'verdict': f"評審失敗: {str(e)[:50]}",
                'error': str(e)
            }

    def multi_ai_voting(self, outline: str) -> Dict:
        """
        多 AI 投票：3 個模型評分，取中位數

        Returns:
            {
                'reviews': [AI1結果, AI2結果, AI3結果],
                'median_score': 78,
                'agreement': 'high/medium/low'
            }
        """

        # 三個評審模型
        reviewers = [
            ('DeepSeek R1', MODEL_ROLES['architect']),  # 邏輯推理
            ('GLM-4', MODEL_ROLES['writer']),           # 創意寫作
            ('Qwen Coder', MODEL_ROLES['editor'])       # 品質檢查
        ]

        reviews = []

        for name, model in reviewers:
            logger.info(f"  評審模型: {name}")

            try:
                review = self.adversarial_review(outline, model)
                review['reviewer_name'] = name
                reviews.append(review)
            except Exception as e:
                logger.error(f"  評審失敗 ({name}): {e}")
                # 添加失敗記錄
                reviews.append({
                    'model': model,
                    'reviewer_name': name,
                    'fatal_flaws': [],
                    'flaw_count': 0,
                    'severity_score': 0,
                    'verdict': f"評審失敗: {str(e)[:50]}",
                    'error': str(e)
                })

        if len(reviews) < 2:
            logger.warning("評審模型不足，使用默認分數")
            return {
                'reviews': reviews,
                'median_score': 50,
                'agreement': 'unknown',
                'score_range': 0
            }

        # 計算中位數分數
        scores = [r['severity_score'] for r in reviews]
        sorted_scores = sorted(scores)
        median_score = sorted_scores[len(sorted_scores) // 2]

        # 計算一致性
        score_range = max(scores) - min(scores)
        if score_range <= 10:
            agreement = 'high'
        elif score_range <= 20:
            agreement = 'medium'
        else:
            agreement = 'low'

        return {
            'reviews': reviews,
            'median_score': median_score,
            'agreement': agreement,
            'score_range': score_range,
            'mean_score': sum(scores) / len(scores)
        }

    def pairwise_comparison(self, outline_a: str, outline_b: str,
                            params_a: Dict, params_b: Dict) -> Dict:
        """
        兩兩比較：評審 AI 判斷哪個更好

        Returns:
            {
                'winner': 'A' or 'B',
                'reason': '勝出原因',
                'confidence': 'high/medium/low'
            }
        """

        prompt = f"""你是資深小說編輯，請比較以下兩份大綱，判斷哪一份更好。

【大綱 A】
{outline_a[:1500]}...

【大綱 B】
{outline_b[:1500]}...

【評估標準】
1. 情節完整性和吸引力
2. 角色設定的獨特性
3. 邏輯一致性
4. 創意性（是否避開老梗）
5. 描述的具體性

【輸出格式】
嚴格使用 JSON：
{{
    "winner": "A" or "B",
    "reason": "勝出原因（一句話）",
    "confidence": "high/medium/low",
    "score_diff": 5
}}
"""

        try:
            # 使用 Writer 模型（GLM-4）作為評審
            response = self.api_client.generate(prompt, model=MODEL_ROLES['writer'],
                                              max_tokens=500, temperature=0.3)
            result = self.json_parser.parse(response)

            # 確保有必要的字段
            if 'winner' not in result:
                result['winner'] = 'A'  # 默認
            if 'reason' not in result:
                result['reason'] = '無理由'
            if 'confidence' not in result:
                result['confidence'] = 'low'

            # 記錄結果
            result['params_winner'] = params_a if result['winner'] == 'A' else params_b

            return result

        except Exception as e:
            logger.error(f"兩兩比較失敗: {e}")
            # 返回默認結果（隨機選擇）
            return {
                'winner': random.choice(['A', 'B']),
                'reason': f'比較失敗: {str(e)[:50]}',
                'confidence': 'low',
                'score_diff': 0,
                'params_winner': params_a,
                'error': str(e)
            }

    def rank_by_comparison(self, outlines_with_params: List[Tuple]) -> List:
        """
        通過兩兩比較排序所有大綱

        Args:
            outlines_with_params: [(outline, params, score_dict), ...]

        Returns:
            排序後的列表（按勝率降序）
        """

        n = len(outlines_with_params)
        win_count = {i: 0 for i in range(n)}

        # 兩兩比較
        comparisons = 0
        max_comparisons = min(n * (n - 1) // 2, 20)  # 最多 20 次比較（控制成本）

        logger.info(f"\n🏆 開始相對排名（{n} 個候選，最多 {max_comparisons} 次比較）")

        # 生成所有配對
        pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
        random.shuffle(pairs)

        for i, j in pairs[:max_comparisons]:
            outline_a, params_a, score_a = outlines_with_params[i]
            outline_b, params_b, score_b = outlines_with_params[j]

            logger.info(f"  比較: #{i+1} vs #{j+1} ({comparisons+1}/{max_comparisons})")

            try:
                result = self.pairwise_comparison(outline_a, outline_b, params_a, params_b)

                if result['winner'] == 'A':
                    win_count[i] += 1
                else:
                    win_count[j] += 1

                logger.info(f"  結果: {result['winner']} 勝 ({result['confidence']})")

                comparisons += 1

            except Exception as e:
                logger.error(f"  比較失敗: {e}")

        # 按勝率排序
        ranked_indices = sorted(range(n), key=lambda i: win_count[i], reverse=True)

        logger.info("\n📊 相對排名結果:")
        for rank, idx in enumerate(ranked_indices, 1):
            logger.info(f"  {rank}. 測試 #{idx+1} - 勝場: {win_count[idx]}/{comparisons}")

        return [outlines_with_params[i] for i in ranked_indices]

    def test_param_combination(self, params: Dict, index: int, total: int) -> Tuple[str, Dict]:
        """測試單組參數（整合 AI 評審）"""
        logger.info(f"\n{'='*60}")
        logger.info(f"測試 {index}/{total}")
        logger.info(f"參數: temp={params['temperature']}, top_p={params['top_p']}, "
                   f"rep={params['repetition_penalty']}, max_tok={params['max_tokens']}")
        logger.info(f"{'='*60}")

        try:
            # 1. 生成大綱
            outline = self.generate_outline(params)

            # 2. 自動評估（原有的 10 項檢查）
            auto_score = self.evaluate_quality(outline, params)

            # 3. AI 評審（對抗式 + 多 AI 投票）
            if self.enable_ai_review:
                logger.info("🤖 開始 AI 評審...")
                ai_review = self.multi_ai_voting(outline)
            else:
                # 不啟用 AI 評審時使用默認值
                ai_review = {
                    'reviews': [],
                    'median_score': auto_score['total_score'],
                    'agreement': 'N/A',
                    'score_range': 0
                }

            # 4. 綜合分數
            final_score = {
                'params': params,
                'auto_score': auto_score['total_score'],      # 自動評分（100分）
                'ai_score': ai_review['median_score'],        # AI 評分（100分）
                'combined_score': (auto_score['total_score'] * 0.4 +
                                  ai_review['median_score'] * 0.6) if self.enable_ai_review
                                  else auto_score['total_score'],  # 綜合（40%自動 + 60%AI）
                'ai_reviews': ai_review['reviews'],
                'ai_agreement': ai_review['agreement'],
                'auto_details': auto_score['details']
            }

            # 5. 保存大綱（包含 AI 評審意見）
            self.save_outline_with_reviews(outline, params, final_score, index)

            logger.info(f"✅ 測試完成")
            logger.info(f"  自動分數: {final_score['auto_score']:.0f}/100")
            if self.enable_ai_review:
                logger.info(f"  AI 分數: {final_score['ai_score']:.0f}/100")
                logger.info(f"  綜合分數: {final_score['combined_score']:.1f}/100")
                logger.info(f"  AI 一致性: {final_score['ai_agreement']}")

            return outline, final_score

        except Exception as e:
            logger.error(f"❌ 測試失敗: {e}")
            import traceback
            traceback.print_exc()

            # 返回空大綱和默認分數
            return "", {
                'params': params,
                'auto_score': 0,
                'ai_score': 0,
                'combined_score': 0,
                'ai_reviews': [],
                'ai_agreement': 'N/A',
                'auto_details': {},
                'error': str(e)
            }

    def generate_outline(self, params: Dict) -> str:
        """生成大綱（使用指定參數）"""
        # 臨時修改配置
        import config
        original_config = config.ROLE_CONFIGS['architect'].copy()

        try:
            # 應用測試參數
            config.ROLE_CONFIGS['architect'] = params

            # 創建生成器
            generator = NovelGenerator(self.api_key, enable_phase2=False)

            # 創建測試專案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title = f"測試小說_{timestamp}"

            generator.create_project(
                title=title,
                genre="科幻",
                theme="AI 覺醒與人類關係",
                total_chapters=5
            )

            # 生成大綱
            generator.generate_outline()

            # 讀取大綱
            outline_file = os.path.join(generator.project_dir, 'outline.txt')
            with open(outline_file, 'r', encoding='utf-8') as f:
                outline = f.read()

            # 清理測試專案
            import shutil
            shutil.rmtree(generator.project_dir)

            return outline

        finally:
            # 恢復原始配置
            config.ROLE_CONFIGS['architect'] = original_config

    def evaluate_quality(self, outline: str, params: Dict) -> Dict:
        """評估大綱品質（原有的自動評估）"""
        score = {
            'params': params,
            'format_score': 0,
            'content_score': 0,
            'length_score': 0,
            'total_score': 0,
            'details': {}
        }

        # 格式品質評估（40分）
        think_score = self.check_no_think_tags(outline)
        star_score = self.check_no_star_placeholders(outline)
        dot_score = self.check_no_dot_placeholders(outline)
        lang_score = self.check_no_mixed_language(outline)

        score['format_score'] = (think_score + star_score + dot_score + lang_score) * 10
        score['details']['think_tags'] = think_score
        score['details']['star_placeholders'] = star_score
        score['details']['dot_placeholders'] = dot_score
        score['details']['mixed_language'] = lang_score

        # 內容品質評估（40分）
        unique_score = self.check_unique_titles(outline)
        concrete_score = self.check_concrete_plots(outline)
        names_score = self.check_complete_names(outline)
        repeat_score = self.check_no_repetition(outline)

        score['content_score'] = (unique_score + concrete_score + names_score + repeat_score) * 10
        score['details']['unique_titles'] = unique_score
        score['details']['concrete_plots'] = concrete_score
        score['details']['complete_names'] = names_score
        score['details']['no_repetition'] = repeat_score

        # 長度品質評估（20分）
        length_score = self.check_outline_length(outline)
        chapter_score = self.check_chapter_length(outline)

        score['length_score'] = (length_score + chapter_score) * 10
        score['details']['outline_length'] = length_score
        score['details']['chapter_length'] = chapter_score

        score['total_score'] = score['format_score'] + score['content_score'] + score['length_score']

        return score

    # 品質檢查方法（保持與原版一致）
    def check_no_think_tags(self, outline: str) -> float:
        """檢查無 <think> 標籤（0-1）"""
        if '<think>' in outline or '</think>' in outline:
            return 0.0
        if outline.startswith('嗯，') or outline.startswith('好的，') or outline.startswith('首先，'):
            return 0.3
        return 1.0

    def check_no_star_placeholders(self, outline: str) -> float:
        """檢查無星號佔位符（0-1）"""
        if '*********' in outline or '****' in outline:
            return 0.0
        star_count = outline.count('*')
        if star_count > 50:
            return 0.3
        elif star_count > 20:
            return 0.7
        return 1.0

    def check_no_dot_placeholders(self, outline: str) -> float:
        """檢查無省略號佔位符（0-1）"""
        if '........' in outline or '......' in outline:
            return 0.0
        dot_count = outline.count('...')
        if dot_count > 20:
            return 0.3
        elif dot_count > 10:
            return 0.7
        return 1.0

    def check_no_mixed_language(self, outline: str) -> float:
        """
        檢查無中英文混雜（0-1）

        策略：檢測所有連續英文單詞，排除允許的專有名詞
        """
        chinese_sections = re.findall(r'[\u4e00-\u9fff]+', outline)
        if not chinese_sections:
            return 0.0

        # 允許的專有名詞白名單（不計入混雜）
        allowed_terms = {
            'ai', 'cpu', 'gpu', 'vr', 'ar', 'ml', 'nlp', 'api',  # 技術縮寫
            'ok', 'no', 'yes',  # 常見短詞
            'cyberpunk', 'steampunk',  # 括號標註的專有名詞
        }

        # 檢測所有連續英文單詞（2+ 字母）
        english_words = re.findall(r'\b[a-zA-Z]{2,}\b', outline.lower())

        # 過濾掉白名單詞彙
        mixed_words = [w for w in english_words if w not in allowed_terms]

        # 計算混雜程度
        mixed_count = len(mixed_words)
        total_words = len(chinese_sections) + len(english_words)

        if total_words == 0:
            return 0.0

        mixed_ratio = mixed_count / total_words

        # 評分標準（更嚴格）
        if mixed_ratio > 0.15:  # 超過 15% 英文 → 0 分
            return 0.0
        elif mixed_ratio > 0.08:  # 8-15% → 0.3 分
            return 0.3
        elif mixed_ratio > 0.03:  # 3-8% → 0.6 分
            return 0.6
        elif mixed_ratio > 0:     # 1-3% → 0.8 分
            return 0.8
        return 1.0  # 0% → 滿分

    def check_unique_titles(self, outline: str) -> float:
        """檢查章節標題有差異（0-1）"""
        titles = re.findall(r'第\d+章[：:]\s*(.+)', outline)
        if len(titles) < 3:
            return 0.5

        unique_titles = set(titles)
        uniqueness = len(unique_titles) / max(len(titles), 1)
        return uniqueness

    def check_concrete_plots(self, outline: str) -> float:
        """檢查情節描述具體（0-1）"""
        action_verbs = ['發現', '探索', '對抗', '選擇', '犧牲', '進入', '返回',
                       '揭開', '面對', '突破', '決定', '遭遇']

        verb_count = sum(outline.count(verb) for verb in action_verbs)

        if verb_count >= 10:
            return 1.0
        elif verb_count >= 5:
            return 0.7
        elif verb_count >= 3:
            return 0.5
        return 0.3

    def check_complete_names(self, outline: str) -> float:
        """檢查角色名稱完整（0-1）"""
        if re.search(r'\*+[\u4e00-\u9fff]', outline) or re.search(r'[\u4e00-\u9fff]\*+', outline):
            return 0.0

        if '某某' in outline or '某個' in outline:
            return 0.3

        chinese_names = re.findall(r'[\u4e00-\u9fff]{2,3}(?=[，。：、]|$)', outline)
        if len(chinese_names) >= 3:
            return 1.0
        elif len(chinese_names) >= 1:
            return 0.7
        return 0.5

    def check_no_repetition(self, outline: str) -> float:
        """檢查章節間無高度重複（0-1）"""
        chapters = re.split(r'第\d+章', outline)
        if len(chapters) < 3:
            return 0.5

        repetition_count = 0
        common_phrases = ['新的', '開始', '探索', '發現', '解決', '面對', '突破']

        for phrase in common_phrases:
            count = outline.count(phrase)
            if count > 5:
                repetition_count += 1

        if repetition_count > 3:
            return 0.3
        elif repetition_count > 1:
            return 0.7
        return 1.0

    def check_outline_length(self, outline: str) -> float:
        """檢查大綱長度適中（0-1）"""
        length = len(outline)

        if 2000 <= length <= 5000:
            return 1.0
        elif 1500 <= length < 2000 or 5000 < length <= 6000:
            return 0.7
        elif 1000 <= length < 1500 or 6000 < length <= 8000:
            return 0.5
        return 0.3

    def check_chapter_length(self, outline: str) -> float:
        """檢查每章描述充分（0-1）"""
        chapters = re.split(r'第\d+章', outline)
        if len(chapters) < 2:
            return 0.0

        chapters = chapters[1:]

        adequate_count = 0
        for chapter in chapters:
            if len(chapter.strip()) >= 50:
                adequate_count += 1

        ratio = adequate_count / max(len(chapters), 1)
        return ratio

    def save_outline_with_reviews(self, outline: str, params: Dict, score: Dict, index: int):
        """保存大綱（包含 AI 評審意見）"""
        # 保存大綱
        filename = f"{self.output_dir}/outlines/outline_{index:03d}_auto{score['auto_score']:.0f}_ai{score['ai_score']:.0f}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 參數配置\n")
            f.write(f"temperature: {params['temperature']}\n")
            f.write(f"top_p: {params['top_p']}\n")
            f.write(f"repetition_penalty: {params['repetition_penalty']}\n")
            f.write(f"max_tokens: {params['max_tokens']}\n")
            f.write(f"\n# 品質評分\n")
            f.write(f"自動評分: {score['auto_score']:.0f}/100\n")
            f.write(f"AI 評分: {score['ai_score']:.0f}/100\n")
            f.write(f"綜合分數: {score['combined_score']:.1f}/100\n")
            f.write(f"AI 一致性: {score['ai_agreement']}\n")

            # AI 評審意見
            if score['ai_reviews']:
                f.write(f"\n# AI 評審意見\n")
                for review in score['ai_reviews']:
                    f.write(f"\n## {review.get('reviewer_name', 'Unknown')}\n")
                    f.write(f"嚴重度分數: {review['severity_score']}/100\n")
                    f.write(f"缺陷數量: {review['flaw_count']}\n")
                    f.write(f"整體評價: {review['verdict']}\n")

                    if review['fatal_flaws']:
                        f.write(f"\n致命缺陷:\n")
                        for i, flaw in enumerate(review['fatal_flaws'], 1):
                            f.write(f"  {i}. [{flaw.get('severity', '?')}] {flaw.get('location', '?')}: {flaw.get('issue', '?')}\n")

            f.write(f"\n{'='*60}\n\n")
            f.write(outline)

        # 保存 AI 評審詳細數據（JSON）
        if score['ai_reviews']:
            review_filename = f"{self.output_dir}/ai_reviews/review_{index:03d}.json"
            with open(review_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'params': params,
                    'scores': {
                        'auto': score['auto_score'],
                        'ai': score['ai_score'],
                        'combined': score['combined_score']
                    },
                    'ai_reviews': score['ai_reviews'],
                    'ai_agreement': score['ai_agreement']
                }, f, ensure_ascii=False, indent=2)

    def run_full_test(self):
        """執行完整測試（整合相對排名）"""
        self.start_time = time.time()

        print("\n" + "="*60)
        print("🧪 DeepSeek R1 參數自動測試系統（AI 評審增強版）")
        print("="*60)

        # 生成參數組合
        param_combinations = self.generate_param_combinations()
        total = len(param_combinations)

        mode_name = "快速測試" if self.quick_mode else "完整測試"
        ai_status = "啟用" if self.enable_ai_review else "停用"

        print(f"\n模式: {mode_name}")
        print(f"AI 評審: {ai_status}")
        print(f"總測試組合數: {total}")

        if self.enable_ai_review:
            print(f"預計時間: {total * 1.5:.0f}-{total * 3:.0f} 分鐘（含 AI 評審）")
        else:
            print(f"預計時間: {total * 0.5:.0f}-{total * 1:.0f} 分鐘")

        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Phase 1: 自動測試 + AI 評審
        logger.info("="*60)
        logger.info("Phase 1: 參數測試與評估")
        logger.info("="*60)

        results_with_outlines = []

        for i, params in enumerate(param_combinations, 1):
            try:
                outline, score = self.test_param_combination(params, i, total)
                results_with_outlines.append((outline, params, score))

                # 顯示當前最佳
                if results_with_outlines:
                    best = max(results_with_outlines, key=lambda x: x[2]['combined_score'])
                    print(f"\n💡 當前最佳: 綜合分數 {best[2]['combined_score']:.1f}/100")
                    print(f"   參數: temp={best[1]['temperature']}, "
                          f"top_p={best[1]['top_p']}, "
                          f"rep={best[1]['repetition_penalty']}, "
                          f"max_tok={best[1]['max_tokens']}")

                # 顯示進度
                elapsed = time.time() - self.start_time
                avg_time = elapsed / i
                remaining = (total - i) * avg_time
                print(f"\n⏱️  進度: {i}/{total} ({i/total*100:.1f}%)")
                print(f"   已用時間: {elapsed/60:.1f} 分鐘")
                print(f"   預計剩餘: {remaining/60:.1f} 分鐘")

            except Exception as e:
                logger.error(f"❌ 測試失敗: {e}")
                import traceback
                traceback.print_exc()

        # Phase 2: 相對排名（Top 10，僅在啟用 AI 評審時執行）
        if self.enable_ai_review and len(results_with_outlines) >= 3:
            logger.info("\n" + "="*60)
            logger.info("Phase 2: 相對排名（Top 候選）")
            logger.info("="*60)

            # 先按綜合分數排序，取前 10（或全部如果少於 10）
            top_n = min(10, len(results_with_outlines))
            top_candidates = sorted(results_with_outlines,
                                   key=lambda x: x[2]['combined_score'],
                                   reverse=True)[:top_n]

            # 兩兩比較排名
            final_ranking = self.rank_by_comparison(top_candidates)

            # 更新 results（用於報告生成）
            self.results = [x[2] for x in final_ranking]

            # 保存完整排名信息
            for rank, (outline, params, score) in enumerate(final_ranking, 1):
                score['final_rank'] = rank

        else:
            # 不進行相對排名，直接按綜合分數排序
            self.results = [x[2] for x in sorted(results_with_outlines,
                                                 key=lambda x: x[2]['combined_score'],
                                                 reverse=True)]

        # Phase 3: 生成報告
        print("\n" + "="*60)
        print("📊 生成測試報告...")
        print("="*60)
        self.generate_enhanced_report()

        total_time = time.time() - self.start_time
        print(f"\n✅ 測試完成！總耗時: {total_time/60:.1f} 分鐘")

    def generate_enhanced_report(self):
        """生成增強報告"""
        if not self.results:
            logger.warning("沒有測試結果")
            return

        # 排序結果
        sorted_results = sorted(self.results, key=lambda x: x['combined_score'], reverse=True)

        # 生成 Markdown 報告
        report = self.build_enhanced_markdown_report(sorted_results)

        # 保存報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode_suffix = "quick" if self.quick_mode else "full"
        ai_suffix = "ai" if self.enable_ai_review else "auto"

        report_path = f"{self.output_dir}/r1_params_test_report_{mode_suffix}_{ai_suffix}_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        # 同時保存為最新報告
        latest_path = f"{self.output_dir}/r1_params_test_report_latest_{ai_suffix}.md"
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 報告已生成:")
        print(f"   {report_path}")
        print(f"   {latest_path}")

    def build_enhanced_markdown_report(self, sorted_results: List[Dict]) -> str:
        """生成增強 Markdown 報告"""
        mode_name = "快速測試" if self.quick_mode else "完整測試"
        ai_status = "AI 評審" if self.enable_ai_review else "自動評估"
        total_time = time.time() - self.start_time if self.start_time else 0

        report = f"""# DeepSeek R1 參數測試報告（{ai_status}版）

## 測試時間
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 測試配置
- 測試模式: {mode_name}
- 評估方式: {ai_status}
- 總測試組合: {len(self.results)} 組
- 每組測試次數: 1 次
- 總生成次數: {len(self.results)} 次
- 總耗時: {total_time/60:.1f} 分鐘

"""

        # Top 3 結果
        report += "## 🏆 最終排名\n\n"

        medals = ['🥇', '🥈', '🥉']
        rankings = ['冠軍', '亞軍', '季軍']

        for i, (medal, ranking) in enumerate(zip(medals, rankings)):
            if i >= len(sorted_results):
                break

            result = sorted_results[i]
            params = result['params']
            has_rank = 'final_rank' in result

            rank_info = f" - 相對排名: {result['final_rank']}" if has_rank else ""

            report += f"### {medal} {ranking}{rank_info}\n\n"
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
            report += f"- 自動評分：{result['auto_score']:.0f}/100\n"

            if self.enable_ai_review and result.get('ai_reviews'):
                report += f"- AI 評分（中位數）：{result['ai_score']:.0f}/100\n"
                report += f"- 綜合分數：{result['combined_score']:.1f}/100\n"
                report += f"- AI 一致性：{result['ai_agreement']}\n\n"

                report += "**AI 評審意見**：\n"
                for review in result['ai_reviews']:
                    reviewer_name = review.get('reviewer_name', 'Unknown')
                    verdict = review.get('verdict', '無評價')
                    report += f"- **{reviewer_name}**: \"{verdict}\"\n"

                report += "\n"

                # 致命缺陷匯總
                all_flaws = []
                for review in result['ai_reviews']:
                    all_flaws.extend(review.get('fatal_flaws', []))

                if all_flaws:
                    report += "**主要缺陷**：\n"
                    for flaw in all_flaws[:5]:  # 只顯示前 5 個
                        severity = flaw.get('severity', '?')
                        location = flaw.get('location', '?')
                        issue = flaw.get('issue', '?')
                        report += f"- [{severity}] {location}: {issue}\n"
                    report += "\n"
            else:
                report += f"- 總分：{result['auto_score']:.0f}/100\n\n"

        # 詳細測試結果表格
        report += "## 📊 詳細測試結果\n\n"

        if self.enable_ai_review:
            report += "| 排名 | temp | top_p | rep | max_tok | 自動分 | AI分 | 綜合分 | 一致性 |\n"
            report += "|------|------|-------|-----|---------|--------|------|--------|--------|\n"

            for i, result in enumerate(sorted_results, 1):
                params = result['params']
                report += f"| {i} | {params['temperature']} | {params['top_p']} | "
                report += f"{params['repetition_penalty']} | {params['max_tokens']} | "
                report += f"{result['auto_score']:.0f} | {result['ai_score']:.0f} | "
                report += f"{result['combined_score']:.1f} | {result['ai_agreement']} |\n"
        else:
            report += "| 排名 | temp | top_p | rep | max_tok | 總分 | 格式 | 內容 | 長度 |\n"
            report += "|------|------|-------|-----|---------|------|------|------|------|\n"

            for i, result in enumerate(sorted_results, 1):
                params = result['params']
                details = result.get('auto_details', {})
                format_score = (details.get('think_tags', 0) + details.get('star_placeholders', 0) +
                              details.get('dot_placeholders', 0) + details.get('mixed_language', 0)) * 10
                content_score = (details.get('unique_titles', 0) + details.get('concrete_plots', 0) +
                               details.get('complete_names', 0) + details.get('no_repetition', 0)) * 10
                length_score = (details.get('outline_length', 0) + details.get('chapter_length', 0)) * 10

                report += f"| {i} | {params['temperature']} | {params['top_p']} | "
                report += f"{params['repetition_penalty']} | {params['max_tokens']} | "
                report += f"{result['auto_score']:.0f} | {format_score:.0f} | "
                report += f"{content_score:.0f} | {length_score:.0f} |\n"

        report += "\n"

        # 參數影響分析
        if self.enable_ai_review:
            report += self.analyze_ai_parameter_impact(sorted_results)
        else:
            report += self.analyze_parameter_impact(sorted_results)

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

            if self.enable_ai_review:
                report += f"**理由**：\n"
                report += f"- 自動評分：{best['auto_score']:.0f}/100（品質檢查通過）\n"
                report += f"- AI 評分：{best['ai_score']:.0f}/100（專家一致認可）\n"
                report += f"- 綜合分數：{best['combined_score']:.1f}/100（最佳平衡）\n"
                report += f"- AI 一致性：{best['ai_agreement']}（評審意見{best['ai_agreement'] == 'high' and '高度' or ''}一致）\n\n"

        # 測試數據說明
        report += "## 📁 測試數據\n\n"
        report += f"所有測試大綱已保存至：`{self.output_dir}/outlines/`\n\n"
        report += "檔案命名格式：`outline_XXX_autoYY_aiZZ.txt`\n"
        report += "- XXX: 測試序號（001-999）\n"
        report += "- YY: 自動評分（0-100）\n"
        report += "- ZZ: AI 評分（0-100）\n\n"

        if self.enable_ai_review:
            report += f"AI 評審詳細數據：`{self.output_dir}/ai_reviews/`\n\n"

        return report

    def analyze_parameter_impact(self, sorted_results: List[Dict]) -> str:
        """分析參數影響（自動評估版）"""
        report = "## 📈 參數影響分析\n\n"

        # 按參數分組統計
        temp_groups = {}
        topp_groups = {}
        rep_groups = {}
        tok_groups = {}

        for result in sorted_results:
            params = result['params']
            score = result['auto_score']

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
            report += f"- **{temp}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # Top_P 影響
        report += "### Top_P 影響\n\n"
        for topp in sorted(topp_groups.keys()):
            scores = topp_groups[topp]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(topp_groups[t])/len(topp_groups[t]) for t in topp_groups) else ""
            report += f"- **{topp}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # Repetition Penalty 影響
        report += "### Repetition Penalty 影響\n\n"
        for rep in sorted(rep_groups.keys()):
            scores = rep_groups[rep]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(rep_groups[r])/len(rep_groups[r]) for r in rep_groups) else ""
            report += f"- **{rep}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # Max Tokens 影響
        report += "### Max Tokens 影響\n\n"
        for tok in sorted(tok_groups.keys()):
            scores = tok_groups[tok]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(tok_groups[t])/len(tok_groups[t]) for t in tok_groups) else ""
            report += f"- **{tok}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        return report

    def analyze_ai_parameter_impact(self, sorted_results: List[Dict]) -> str:
        """分析參數影響（AI 評審版）"""
        report = "## 📈 參數影響分析（AI 評審）\n\n"

        # 按參數分組統計（使用綜合分數）
        temp_groups = {}
        topp_groups = {}
        rep_groups = {}
        tok_groups = {}

        for result in sorted_results:
            params = result['params']
            score = result['combined_score']

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
        report += "### Temperature 影響（綜合分數）\n\n"
        for temp in sorted(temp_groups.keys()):
            scores = temp_groups[temp]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(temp_groups[t])/len(temp_groups[t]) for t in temp_groups) else ""
            report += f"- **{temp}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # Top_P 影響
        report += "### Top_P 影響（綜合分數）\n\n"
        for topp in sorted(topp_groups.keys()):
            scores = topp_groups[topp]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(topp_groups[t])/len(topp_groups[t]) for t in topp_groups) else ""
            report += f"- **{topp}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # Repetition Penalty 影響
        report += "### Repetition Penalty 影響（綜合分數）\n\n"
        for rep in sorted(rep_groups.keys()):
            scores = rep_groups[rep]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(rep_groups[r])/len(rep_groups[r]) for r in rep_groups) else ""
            report += f"- **{rep}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # Max Tokens 影響
        report += "### Max Tokens 影響（綜合分數）\n\n"
        for tok in sorted(tok_groups.keys()):
            scores = tok_groups[tok]
            avg_score = sum(scores) / len(scores)
            best_mark = " ⭐" if avg_score == max(sum(tok_groups[t])/len(tok_groups[t]) for t in tok_groups) else ""
            report += f"- **{tok}**: 平均分 {avg_score:.1f}{best_mark}\n"
        report += "\n"

        # AI 評審一致性分析
        report += "### AI 評審一致性分析\n\n"
        agreement_counts = {'high': 0, 'medium': 0, 'low': 0, 'N/A': 0}

        for result in sorted_results:
            agreement = result.get('ai_agreement', 'N/A')
            agreement_counts[agreement] = agreement_counts.get(agreement, 0) + 1

        total = sum(agreement_counts.values())
        for agreement, count in sorted(agreement_counts.items()):
            if count > 0:
                percentage = count / total * 100
                report += f"- **{agreement}**: {count} 次 ({percentage:.1f}%)\n"

        report += "\n"

        return report


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='DeepSeek R1 參數自動測試系統（AI 評審增強版）')
    parser.add_argument('--quick', action='store_true', help='快速測試模式（10組關鍵參數）')
    parser.add_argument('--full', action='store_true', help='完整測試模式（所有組合）')
    parser.add_argument('--no-ai', action='store_true', help='停用 AI 評審（僅自動評估）')
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
        print("   使用 --full 可進行完整測試（所有 240 組組合）")
        print("   使用 --quick 明確指定快速測試")
        print("   使用 --no-ai 停用 AI 評審\n")

    # AI 評審狀態
    enable_ai = not args.no_ai

    if not enable_ai:
        print("⚠️  AI 評審已停用，僅使用自動評估")

    # 創建測試器並運行
    tester = R1ParamsTesterEnhanced(api_key, quick_mode=quick_mode, enable_ai_review=enable_ai)
    tester.run_full_test()


if __name__ == "__main__":
    main()
