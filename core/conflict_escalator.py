# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 衝突升級管理器
實現波浪式衝突曲線，避免劇情平淡或疲勞
"""

import logging
import math
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class ConflictEscalator:
    """
    衝突升級管理器

    功能:
    - 規劃衝突曲線（波浪式、線性、高潮式）
    - 強制升級檢查
    - 檢測衝突飽和
    """

    # 曲線類型
    CURVE_TYPES = ['wave_with_climax', 'linear', 'exponential', 'custom']

    def __init__(self, curve_type: str = 'wave_with_climax'):
        """
        初始化衝突管理器

        Args:
            curve_type: 曲線類型
                - wave_with_climax: 波浪式上升，最後高潮
                - linear: 線性上升
                - exponential: 指數上升
                - custom: 自定義
        """
        if curve_type not in self.CURVE_TYPES:
            logger.warning(f"未知曲線類型 {curve_type}，使用默認 wave_with_climax")
            curve_type = 'wave_with_climax'

        self.curve_type = curve_type
        self.conflict_arc = []

        logger.info(f"衝突升級管理器初始化完成 (曲線類型: {curve_type})")

    def plan_conflict_arc(
        self,
        total_chapters: int,
        curve_type: Optional[str] = None
    ) -> List[float]:
        """
        規劃衝突曲線

        Args:
            total_chapters: 總章節數
            curve_type: 曲線類型（可選，覆蓋初始化設置）

        Returns:
            衝突強度列表（每章一個值，範圍 0-1）
        """
        curve_type = curve_type or self.curve_type

        if curve_type == 'wave_with_climax':
            self.conflict_arc = self._wave_with_climax(total_chapters)
        elif curve_type == 'linear':
            self.conflict_arc = self._linear_curve(total_chapters)
        elif curve_type == 'exponential':
            self.conflict_arc = self._exponential_curve(total_chapters)
        else:
            logger.warning(f"未實現曲線類型 {curve_type}，使用 wave_with_climax")
            self.conflict_arc = self._wave_with_climax(total_chapters)

        logger.info(f"衝突曲線規劃完成: {len(self.conflict_arc)} 章")
        logger.info(f"強度範圍: {min(self.conflict_arc):.2f} - {max(self.conflict_arc):.2f}")

        return self.conflict_arc

    def _wave_with_climax(self, total_chapters: int) -> List[float]:
        """
        波浪式上升曲線（推薦用於長篇）

        特點:
        - 每5-7章一個小高潮
        - 整體上升趨勢
        - 最後10%達到最高潮

        Args:
            total_chapters: 總章節數

        Returns:
            衝突強度列表
        """
        intensities = []
        wave_period = 6  # 波浪週期（章節）
        climax_start = int(total_chapters * 0.9)  # 最終高潮起點

        for i in range(total_chapters):
            chapter = i + 1

            # 基礎上升趨勢（0.2 -> 0.7）
            base_trend = 0.2 + (0.5 * i / total_chapters)

            # 波浪起伏（振幅隨章節遞減）
            wave_amplitude = 0.15 * (1 - i / total_chapters)
            wave = wave_amplitude * math.sin(2 * math.pi * i / wave_period)

            # 組合強度
            intensity = base_trend + wave

            # 最終高潮段落
            if chapter >= climax_start:
                progress = (chapter - climax_start) / (total_chapters - climax_start)
                climax_boost = 0.3 * progress
                intensity += climax_boost

            # 限制在 0-1 範圍
            intensity = max(0.0, min(1.0, intensity))
            intensities.append(intensity)

        return intensities

    def _linear_curve(self, total_chapters: int) -> List[float]:
        """
        線性上升曲線（適合中短篇）

        Args:
            total_chapters: 總章節數

        Returns:
            衝突強度列表
        """
        intensities = []
        start_intensity = 0.2
        end_intensity = 1.0

        for i in range(total_chapters):
            progress = i / (total_chapters - 1) if total_chapters > 1 else 0
            intensity = start_intensity + (end_intensity - start_intensity) * progress
            intensities.append(intensity)

        return intensities

    def _exponential_curve(self, total_chapters: int) -> List[float]:
        """
        指數上升曲線（適合短篇高強度）

        Args:
            total_chapters: 總章節數

        Returns:
            衝突強度列表
        """
        intensities = []

        for i in range(total_chapters):
            progress = i / (total_chapters - 1) if total_chapters > 1 else 0
            # 使用 e^x - 1 進行指數增長，然後歸一化
            intensity = (math.exp(2 * progress) - 1) / (math.exp(2) - 1)
            # 調整到 0.2-1.0 範圍
            intensity = 0.2 + 0.8 * intensity
            intensities.append(intensity)

        return intensities

    def enforce_escalation(
        self,
        chapter_num: int,
        current_intensity: float,
        tolerance: float = 0.15
    ) -> Dict:
        """
        強制升級檢查

        Args:
            chapter_num: 當前章節號（從1開始）
            current_intensity: 當前實際衝突強度（0-1）
            tolerance: 容忍偏差範圍

        Returns:
            檢查結果字典:
            {
                'is_acceptable': bool,      # 是否可接受
                'expected_intensity': float,# 預期強度
                'current_intensity': float, # 當前強度
                'deviation': float,         # 偏差
                'action': str,              # 建議動作（escalate/maintain/reduce）
                'suggestions': list,        # 具體建議
            }
        """
        result = {
            'is_acceptable': True,
            'expected_intensity': 0.0,
            'current_intensity': current_intensity,
            'deviation': 0.0,
            'action': 'maintain',
            'suggestions': [],
        }

        # 檢查曲線是否已規劃
        if not self.conflict_arc:
            result['suggestions'].append("衝突曲線未規劃，請先調用 plan_conflict_arc()")
            return result

        # 檢查章節號合法性
        if chapter_num < 1 or chapter_num > len(self.conflict_arc):
            result['suggestions'].append(f"章節號 {chapter_num} 超出範圍")
            return result

        # 獲取預期強度
        expected = self.conflict_arc[chapter_num - 1]
        result['expected_intensity'] = expected

        # 計算偏差
        deviation = current_intensity - expected
        result['deviation'] = deviation

        # 判斷是否可接受
        if abs(deviation) > tolerance:
            result['is_acceptable'] = False

            if deviation < 0:
                # 強度不足，需要升級
                result['action'] = 'escalate'
                result['suggestions'].append(
                    f"衝突強度不足（預期 {expected:.2f}，實際 {current_intensity:.2f}），"
                    "建議增強以下元素："
                )
                result['suggestions'].extend(self._get_escalation_suggestions(expected))

            else:
                # 強度過高，需要緩和
                result['action'] = 'reduce'
                result['suggestions'].append(
                    f"衝突強度過高（預期 {expected:.2f}，實際 {current_intensity:.2f}），"
                    "建議：給予角色喘息空間，或轉移衝突焦點"
                )

        logger.info(
            f"第 {chapter_num} 章衝突檢查: "
            f"預期={expected:.2f}, 實際={current_intensity:.2f}, "
            f"偏差={deviation:.2f}, 動作={result['action']}"
        )

        return result

    def _get_escalation_suggestions(self, target_intensity: float) -> List[str]:
        """
        根據目標強度生成升級建議

        Args:
            target_intensity: 目標強度（0-1）

        Returns:
            建議列表
        """
        suggestions = []

        if target_intensity < 0.3:
            suggestions.append("- 加入小型障礙或誤會")
            suggestions.append("- 引入新線索或謎團")

        elif target_intensity < 0.5:
            suggestions.append("- 增加角色間的摩擦或對立")
            suggestions.append("- 引入外部壓力或時間限制")
            suggestions.append("- 讓主角面對道德兩難")

        elif target_intensity < 0.7:
            suggestions.append("- 安排重要角色間的衝突")
            suggestions.append("- 製造危機或失敗")
            suggestions.append("- 揭露隱藏的威脅")

        elif target_intensity < 0.9:
            suggestions.append("- 設計高風險對抗或戰鬥")
            suggestions.append("- 讓角色面臨重大損失")
            suggestions.append("- 多線衝突同時爆發")

        else:
            suggestions.append("- 最終決戰或終極對決")
            suggestions.append("- 不可逆轉的重大選擇")
            suggestions.append("- 所有衝突集中解決")

        return suggestions

    def detect_conflict_saturation(
        self,
        recent_intensities: List[float],
        threshold: float = 0.85,
        window: int = 5
    ) -> Tuple[bool, str]:
        """
        檢測衝突飽和（長期高強度可能導致疲勞）

        Args:
            recent_intensities: 最近章節的強度列表
            threshold: 飽和閾值（0-1）
            window: 檢測窗口大小（章節數）

        Returns:
            (是否飽和, 警告訊息)
        """
        if len(recent_intensities) < window:
            return False, ""

        # 取最近 window 章的平均強度
        recent = recent_intensities[-window:]
        avg_intensity = sum(recent) / len(recent)

        if avg_intensity >= threshold:
            return True, (
                f"檢測到衝突飽和（{window}章平均強度 {avg_intensity:.2f}），"
                "建議安排緩和章節，避免讀者疲勞"
            )

        return False, ""

    def get_chapter_intensity(self, chapter_num: int) -> float:
        """
        獲取指定章節的預期強度

        Args:
            chapter_num: 章節號（從1開始）

        Returns:
            強度值（0-1），如果章節號無效返回 0.0
        """
        if not self.conflict_arc or chapter_num < 1 or chapter_num > len(self.conflict_arc):
            return 0.0

        return self.conflict_arc[chapter_num - 1]

    def visualize_curve(self, width: int = 60) -> str:
        """
        可視化衝突曲線（ASCII 圖表）

        Args:
            width: 圖表寬度（字符數）

        Returns:
            ASCII 圖表字符串
        """
        if not self.conflict_arc:
            return "衝突曲線未規劃"

        height = 15
        chart = [[' ' for _ in range(width)] for _ in range(height)]

        # 繪製曲線
        for i, intensity in enumerate(self.conflict_arc):
            x = int(i / len(self.conflict_arc) * (width - 1))
            y = height - 1 - int(intensity * (height - 1))
            chart[y][x] = '●'

        # 轉換為字符串
        lines = []
        lines.append("衝突強度曲線")
        lines.append("1.0 " + "┬" + "─" * (width - 2))

        for row in chart:
            lines.append("    │" + ''.join(row))

        lines.append("0.0 " + "┴" + "─" * (width - 2))
        lines.append(f"    1{' ' * (width - 10)}章節{' ' * 3}{len(self.conflict_arc)}")

        return '\n'.join(lines)


if __name__ == '__main__':
    # 測試衝突管理器
    logging.basicConfig(level=logging.INFO)

    escalator = ConflictEscalator(curve_type='wave_with_climax')

    # 規劃30章的衝突曲線
    arc = escalator.plan_conflict_arc(30)

    print("=== 衝突曲線可視化 ===")
    print(escalator.visualize_curve())

    print("\n=== 第 5 章檢查 ===")
    result1 = escalator.enforce_escalation(5, 0.35)
    print(f"可接受: {result1['is_acceptable']}")
    print(f"預期強度: {result1['expected_intensity']:.2f}")
    print(f"動作: {result1['action']}")

    print("\n=== 第 15 章檢查（強度不足） ===")
    result2 = escalator.enforce_escalation(15, 0.3)
    print(f"可接受: {result2['is_acceptable']}")
    print(f"建議:")
    for suggestion in result2['suggestions']:
        print(f"  {suggestion}")

    print("\n=== 飽和檢測 ===")
    high_intensities = [0.85, 0.87, 0.86, 0.88, 0.9]
    is_saturated, msg = escalator.detect_conflict_saturation(high_intensities)
    print(f"飽和: {is_saturated}")
    if msg:
        print(f"訊息: {msg}")
