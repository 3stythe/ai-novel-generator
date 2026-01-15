#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek R1 參數自動測試系統

測試不同參數組合對大綱生成品質的影響
"""

import os
import json
import re
import time
import argparse
from datetime import datetime
from itertools import product
from typing import Dict, List, Tuple
import logging
from dotenv import load_dotenv

from core.generator import NovelGenerator
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


class R1ParamsTester:
    """DeepSeek R1 參數測試器"""

    def __init__(self, api_key: str, quick_mode: bool = False):
        self.api_key = api_key
        self.quick_mode = quick_mode
        self.results = []
        self.output_dir = "test_results"
        self.start_time = None

        # 創建輸出目錄
        os.makedirs(f"{self.output_dir}/outlines", exist_ok=True)

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

    def test_param_combination(self, params: Dict, index: int, total: int) -> Dict:
        """測試單組參數"""
        logger.info(f"\n{'='*60}")
        logger.info(f"測試 {index}/{total}")
        logger.info(f"參數: temp={params['temperature']}, top_p={params['top_p']}, "
                   f"rep={params['repetition_penalty']}, max_tok={params['max_tokens']}")
        logger.info(f"{'='*60}")

        try:
            # 生成大綱
            outline = self.generate_outline(params)

            # 評估品質
            score = self.evaluate_quality(outline, params)

            # 保存大綱
            self.save_outline(outline, params, score, index)

            logger.info(f"✅ 測試完成 - 總分: {score['total_score']}/100")

            return score

        except Exception as e:
            logger.error(f"❌ 測試失敗: {e}")
            return {
                'params': params,
                'format_score': 0,
                'content_score': 0,
                'length_score': 0,
                'total_score': 0,
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
        """評估大綱品質"""
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

    def check_no_think_tags(self, outline: str) -> float:
        """檢查無 <think> 標籤（0-1）"""
        if '<think>' in outline or '</think>' in outline:
            return 0.0
        # 檢查未標記的思考過程（簡體中文開頭）
        if outline.startswith('嗯，') or outline.startswith('好的，') or outline.startswith('首先，'):
            return 0.3  # 部分分數
        return 1.0

    def check_no_star_placeholders(self, outline: str) -> float:
        """檢查無星號佔位符（0-1）"""
        if '*********' in outline or '****' in outline:
            return 0.0
        # 允許少量星號（用於 Markdown 格式）
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
        # 允許少量省略號（用於表達語氣）
        dot_count = outline.count('...')
        if dot_count > 20:
            return 0.3
        elif dot_count > 10:
            return 0.7
        return 1.0

    def check_no_mixed_language(self, outline: str) -> float:
        """檢查無中英文混雜（0-1）"""
        # 提取中文段落
        chinese_sections = re.findall(r'[\u4e00-\u9fff]+', outline)
        if not chinese_sections:
            return 0.0

        # 檢查英文單詞（排除專有名詞）
        common_english = ['time machine', 'AI', 'technology', 'tech', 'loop', 'paradox',
                         'resolver', 'partner', 'assistant', 'antagonistic']

        mixed_count = 0
        for word in common_english:
            if word.lower() in outline.lower():
                mixed_count += 1

        if mixed_count > 10:
            return 0.0
        elif mixed_count > 5:
            return 0.5
        elif mixed_count > 0:
            return 0.8
        return 1.0

    def check_unique_titles(self, outline: str) -> float:
        """檢查章節標題有差異（0-1）"""
        # 提取章節標題
        titles = re.findall(r'第\d+章[：:]\s*(.+)', outline)
        if len(titles) < 3:
            return 0.5

        # 檢查重複
        unique_titles = set(titles)
        uniqueness = len(unique_titles) / max(len(titles), 1)

        return uniqueness

    def check_concrete_plots(self, outline: str) -> float:
        """檢查情節描述具體（0-1）"""
        # 檢查是否包含具體動詞
        action_verbs = ['發現', '探索', '對抗', '選擇', '犧牲', '進入', '返回',
                       '揭開', '面對', '突破', '決定', '遭遇']

        verb_count = sum(outline.count(verb) for verb in action_verbs)

        # 至少 5 章，每章應該有動詞
        if verb_count >= 10:
            return 1.0
        elif verb_count >= 5:
            return 0.7
        elif verb_count >= 3:
            return 0.5
        return 0.3

    def check_complete_names(self, outline: str) -> float:
        """檢查角色名稱完整（0-1）"""
        # 檢查是否有星號代替角色名
        if re.search(r'\*+[\u4e00-\u9fff]', outline) or re.search(r'[\u4e00-\u9fff]\*+', outline):
            return 0.0

        # 檢查是否有省略號代替
        if '某某' in outline or '某個' in outline:
            return 0.3

        # 檢查是否有具體角色名（中文名）
        chinese_names = re.findall(r'[\u4e00-\u9fff]{2,3}(?=[，。：、]|$)', outline)
        if len(chinese_names) >= 3:
            return 1.0
        elif len(chinese_names) >= 1:
            return 0.7
        return 0.5

    def check_no_repetition(self, outline: str) -> float:
        """檢查章節間無高度重複（0-1）"""
        # 提取每章的描述
        chapters = re.split(r'第\d+章', outline)
        if len(chapters) < 3:
            return 0.5

        # 簡單檢查：計算重複短語
        repetition_count = 0
        common_phrases = ['新的', '開始', '探索', '發現', '解決', '面對', '突破']

        for phrase in common_phrases:
            count = outline.count(phrase)
            if count > 5:  # 過度重複
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
        # 提取每章的描述
        chapters = re.split(r'第\d+章', outline)
        if len(chapters) < 2:
            return 0.0

        chapters = chapters[1:]  # 移除開頭

        adequate_count = 0
        for chapter in chapters:
            if len(chapter.strip()) >= 50:
                adequate_count += 1

        ratio = adequate_count / max(len(chapters), 1)
        return ratio

    def save_outline(self, outline: str, params: Dict, score: Dict, index: int):
        """保存大綱"""
        filename = f"{self.output_dir}/outlines/outline_{index:03d}_score{score['total_score']:.0f}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 參數配置\n")
            f.write(f"temperature: {params['temperature']}\n")
            f.write(f"top_p: {params['top_p']}\n")
            f.write(f"repetition_penalty: {params['repetition_penalty']}\n")
            f.write(f"max_tokens: {params['max_tokens']}\n")
            f.write(f"\n# 品質評分\n")
            f.write(f"總分: {score['total_score']}/100\n")
            f.write(f"格式品質: {score['format_score']}/40\n")
            f.write(f"內容品質: {score['content_score']}/40\n")
            f.write(f"長度品質: {score['length_score']}/20\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(outline)

    def run_full_test(self):
        """執行完整測試"""
        self.start_time = time.time()

        print("\n" + "="*60)
        print("🧪 DeepSeek R1 參數自動測試系統")
        print("="*60)

        # 生成參數組合
        param_combinations = self.generate_param_combinations()
        total = len(param_combinations)

        mode_name = "快速測試" if self.quick_mode else "完整測試"
        print(f"\n模式: {mode_name}")
        print(f"總測試組合數: {total}")
        print(f"預計時間: {total * 0.5:.0f}-{total * 1:.0f} 分鐘")
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 測試每組參數
        for i, params in enumerate(param_combinations, 1):
            try:
                score = self.test_param_combination(params, i, total)
                self.results.append(score)

                # 顯示當前最佳
                if self.results:
                    best = max(self.results, key=lambda x: x['total_score'])
                    print(f"\n💡 當前最佳: 總分 {best['total_score']:.0f}/100")
                    print(f"   參數: temp={best['params']['temperature']}, "
                          f"top_p={best['params']['top_p']}, "
                          f"rep={best['params']['repetition_penalty']}, "
                          f"max_tok={best['params']['max_tokens']}")

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

        # 生成報告
        print("\n" + "="*60)
        print("📊 生成測試報告...")
        print("="*60)
        self.generate_report()

        total_time = time.time() - self.start_time
        print(f"\n✅ 測試完成！總耗時: {total_time/60:.1f} 分鐘")

    def generate_report(self):
        """生成測試報告"""
        if not self.results:
            logger.warning("沒有測試結果")
            return

        # 排序結果
        sorted_results = sorted(self.results, key=lambda x: x['total_score'], reverse=True)

        # 生成 Markdown 報告
        report = self.build_markdown_report(sorted_results)

        # 保存報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.output_dir}/r1_params_test_report_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        # 同時保存為最新報告
        latest_path = f"{self.output_dir}/r1_params_test_report_latest.md"
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 報告已生成:")
        print(f"   {report_path}")
        print(f"   {latest_path}")

    def build_markdown_report(self, sorted_results: List[Dict]) -> str:
        """生成 Markdown 報告"""
        mode_name = "快速測試" if self.quick_mode else "完整測試"
        total_time = time.time() - self.start_time if self.start_time else 0

        report = f"""# DeepSeek R1 參數測試報告

## 測試時間
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 測試配置
- 測試模式: {mode_name}
- 總測試組合: {len(self.results)} 組
- 每組測試次數: 1 次
- 總生成次數: {len(self.results)} 次
- 總耗時: {total_time/60:.1f} 分鐘

"""

        # Top 3 結果
        report += "## 最佳參數組合\n\n"

        medals = ['🥇', '🥈', '🥉']
        rankings = ['第一名', '第二名', '第三名']

        for i, (medal, ranking) in enumerate(zip(medals, rankings)):
            if i >= len(sorted_results):
                break

            result = sorted_results[i]
            params = result['params']

            report += f"### {medal} {ranking}（總分：{result['total_score']:.0f}/100）\n\n"
            report += "```python\n"
            report += "{\n"
            report += f"    'temperature': {params['temperature']},\n"
            report += f"    'top_p': {params['top_p']},\n"
            report += f"    'repetition_penalty': {params['repetition_penalty']},\n"
            report += f"    'max_tokens': {params['max_tokens']}\n"
            report += "}\n"
            report += "```\n\n"
            report += "品質評估：\n"
            report += f"- 格式品質：{result['format_score']:.0f}/40\n"
            report += f"- 內容品質：{result['content_score']:.0f}/40\n"
            report += f"- 長度品質：{result['length_score']:.0f}/20\n\n"

            if 'details' in result:
                report += "詳細指標：\n"
                details = result['details']
                report += f"- 無 think 標籤: {details.get('think_tags', 0)*100:.0f}%\n"
                report += f"- 無星號佔位: {details.get('star_placeholders', 0)*100:.0f}%\n"
                report += f"- 無省略號佔位: {details.get('dot_placeholders', 0)*100:.0f}%\n"
                report += f"- 無中英混雜: {details.get('mixed_language', 0)*100:.0f}%\n"
                report += f"- 章節標題差異: {details.get('unique_titles', 0)*100:.0f}%\n"
                report += f"- 情節描述具體: {details.get('concrete_plots', 0)*100:.0f}%\n"
                report += f"- 角色名稱完整: {details.get('complete_names', 0)*100:.0f}%\n"
                report += f"- 無高度重複: {details.get('no_repetition', 0)*100:.0f}%\n"
                report += f"- 大綱長度適中: {details.get('outline_length', 0)*100:.0f}%\n"
                report += f"- 章節描述充分: {details.get('chapter_length', 0)*100:.0f}%\n"

            report += "\n"

        # 詳細測試結果表格
        report += "## 詳細測試結果\n\n"
        report += "| 排名 | temp | top_p | rep_penalty | max_tokens | 總分 | 格式 | 內容 | 長度 |\n"
        report += "|------|------|-------|-------------|------------|------|------|------|------|\n"

        for i, result in enumerate(sorted_results, 1):
            params = result['params']
            report += f"| {i} | {params['temperature']} | {params['top_p']} | "
            report += f"{params['repetition_penalty']} | {params['max_tokens']} | "
            report += f"{result['total_score']:.0f} | {result['format_score']:.0f} | "
            report += f"{result['content_score']:.0f} | {result['length_score']:.0f} |\n"

        report += "\n"

        # 參數影響分析
        report += self.analyze_parameter_impact(sorted_results)

        # 建議配置
        if sorted_results:
            best = sorted_results[0]
            params = best['params']

            report += "## 建議配置\n\n"
            report += "基於測試結果，建議使用：\n\n"
            report += "```python\n"
            report += "'architect': {\n"
            report += f"    'temperature': {params['temperature']},\n"
            report += f"    'top_p': {params['top_p']},\n"
            report += f"    'repetition_penalty': {params['repetition_penalty']},\n"
            report += f"    'max_tokens': {params['max_tokens']}\n"
            report += "}\n"
            report += "```\n\n"

        # 測試數據說明
        report += "## 測試數據\n\n"
        report += f"所有測試大綱已保存至：`{self.output_dir}/outlines/`\n\n"
        report += "檔案命名格式：`outline_XXX_scoreYY.txt`\n"
        report += "- XXX: 測試序號（001-999）\n"
        report += "- YY: 總分（0-100）\n\n"

        return report

    def analyze_parameter_impact(self, sorted_results: List[Dict]) -> str:
        """分析參數影響"""
        report = "## 參數影響分析\n\n"

        # 按參數分組統計
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


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='DeepSeek R1 參數自動測試系統')
    parser.add_argument('--quick', action='store_true', help='快速測試模式（10組關鍵參數）')
    parser.add_argument('--full', action='store_true', help='完整測試模式（所有組合）')
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
        print("   使用 --quick 明確指定快速測試\n")

    # 創建測試器並運行
    tester = R1ParamsTester(api_key, quick_mode=quick_mode)
    tester.run_full_test()


if __name__ == "__main__":
    main()
