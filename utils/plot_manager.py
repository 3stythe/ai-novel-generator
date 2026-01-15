# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 劇情節奏控制器
管理章節類型、衝突強度、劇情指引
"""

import logging
from typing import Dict, Optional

from core.conflict_escalator import ConflictEscalator


logger = logging.getLogger(__name__)


class PlotManager:
    """
    劇情節奏控制器

    功能:
    - 判斷章節類型（開局/升級/高潮/收尾）
    - 計算衝突強度
    - 生成劇情指引
    - 整合 ConflictEscalator
    """

    # 章節類型
    CHAPTER_TYPES = {
        'opening': '開局',
        'setup': '鋪墊',
        'development': '發展',
        'escalation': '升級',
        'climax': '高潮',
        'resolution': '收尾',
    }

    def __init__(self, total_chapters: int, curve_type: str = 'wave_with_climax'):
        """
        初始化劇情管理器

        Args:
            total_chapters: 總章節數
            curve_type: 衝突曲線類型
        """
        self.total_chapters = total_chapters
        self.conflict_escalator = ConflictEscalator(curve_type=curve_type)

        # 規劃衝突曲線
        self.conflict_arc = self.conflict_escalator.plan_conflict_arc(total_chapters)

        logger.info(f"劇情管理器初始化完成 (總章節: {total_chapters})")

    def get_chapter_type(self, chapter_num: int, total_chapters: Optional[int] = None) -> str:
        """
        判斷章節類型

        Args:
            chapter_num: 章節號（從1開始）
            total_chapters: 總章節數（可選，覆蓋初始化設置）

        Returns:
            章節類型標識（opening/setup/development/escalation/climax/resolution）
        """
        total = total_chapters or self.total_chapters

        # 百分比位置
        progress = chapter_num / total

        # 根據位置判斷類型
        if chapter_num == 1:
            return 'opening'

        elif progress <= 0.15:
            return 'setup'

        elif progress <= 0.7:
            return 'development'

        elif progress <= 0.85:
            return 'escalation'

        elif progress <= 0.95:
            return 'climax'

        else:
            return 'resolution'

    def calculate_conflict_level(
        self,
        chapter_num: int,
        chapter_type: Optional[str] = None
    ) -> float:
        """
        計算章節衝突強度

        Args:
            chapter_num: 章節號
            chapter_type: 章節類型（可選，自動計算）

        Returns:
            衝突強度（0-1）
        """
        # 從衝突曲線獲取預期強度
        expected_intensity = self.conflict_escalator.get_chapter_intensity(chapter_num)

        # 根據章節類型微調
        chapter_type = chapter_type or self.get_chapter_type(chapter_num)

        if chapter_type == 'opening':
            # 開局保持中低強度
            return min(expected_intensity, 0.4)

        elif chapter_type == 'setup':
            # 鋪墊階段逐步上升
            return expected_intensity * 0.8

        elif chapter_type == 'climax':
            # 高潮階段保證高強度
            return max(expected_intensity, 0.8)

        elif chapter_type == 'resolution':
            # 收尾階段可高可低
            return expected_intensity

        else:
            # 其他階段使用預期值
            return expected_intensity

    def generate_plot_guidance(
        self,
        chapter_num: int,
        total_chapters: Optional[int] = None,
        volume_num: Optional[int] = None,
        volume_context: Optional[str] = None
    ) -> Dict:
        """
        生成劇情指引

        Args:
            chapter_num: 章節號
            total_chapters: 總章節數（可選）
            volume_num: 卷號（可選，用於分卷）
            volume_context: 卷背景信息（可選）

        Returns:
            劇情指引字典:
            {
                'chapter_num': int,
                'chapter_type': str,
                'chapter_type_name': str,
                'conflict_level': float,
                'pacing_suggestions': list,
                'content_focus': list,
                'tone': str,
                'key_elements': list,
            }
        """
        total = total_chapters or self.total_chapters

        # 章節類型
        chapter_type = self.get_chapter_type(chapter_num, total)
        chapter_type_name = self.CHAPTER_TYPES.get(chapter_type, '未知')

        # 衝突強度
        conflict_level = self.calculate_conflict_level(chapter_num, chapter_type)

        # 生成建議
        pacing_suggestions = self._get_pacing_suggestions(chapter_type, conflict_level)
        content_focus = self._get_content_focus(chapter_type, chapter_num, total)
        tone = self._get_tone(chapter_type, conflict_level)
        key_elements = self._get_key_elements(chapter_type)

        guidance = {
            'chapter_num': chapter_num,
            'chapter_type': chapter_type,
            'chapter_type_name': chapter_type_name,
            'conflict_level': conflict_level,
            'pacing_suggestions': pacing_suggestions,
            'content_focus': content_focus,
            'tone': tone,
            'key_elements': key_elements,
        }

        # 分卷信息（如果有）
        if volume_num is not None:
            guidance['volume_num'] = volume_num
            guidance['volume_context'] = volume_context or ''

        logger.info(
            f"第 {chapter_num} 章劇情指引: "
            f"類型={chapter_type_name}, 衝突強度={conflict_level:.2f}"
        )

        return guidance

    def _get_pacing_suggestions(self, chapter_type: str, conflict_level: float) -> list:
        """根據章節類型和衝突強度生成節奏建議"""
        suggestions = []

        if chapter_type == 'opening':
            suggestions.extend([
                "引入主角和核心設定",
                "建立故事基調和世界觀",
                "設置初始懸念或目標",
                "節奏適中，避免過快或過慢"
            ])

        elif chapter_type == 'setup':
            suggestions.extend([
                "深化角色塑造",
                "展開世界觀細節",
                "鋪設伏筆和線索",
                "逐步提升衝突"
            ])

        elif chapter_type == 'development':
            suggestions.extend([
                "推進主線劇情",
                "發展角色關係",
                "設置阻礙和挑戰",
                "保持節奏變化"
            ])

        elif chapter_type == 'escalation':
            suggestions.extend([
                "加快節奏",
                "提升衝突強度",
                "製造緊迫感",
                "為高潮做準備"
            ])

        elif chapter_type == 'climax':
            suggestions.extend([
                "達到最高衝突點",
                "解決主要矛盾",
                "展現角色成長",
                "製造情感高潮"
            ])

        elif chapter_type == 'resolution':
            suggestions.extend([
                "收束劇情線",
                "提供角色結局",
                "解答關鍵懸念",
                "給予讀者滿足感"
            ])

        # 根據衝突強度補充建議
        if conflict_level > 0.7:
            suggestions.append("維持高張力，動作和對話緊湊")
        elif conflict_level < 0.3:
            suggestions.append("適當加入緩衝內容，如描寫或回憶")

        return suggestions

    def _get_content_focus(self, chapter_type: str, chapter_num: int, total: int) -> list:
        """根據章節類型確定內容重點"""
        focus = []

        if chapter_type == 'opening':
            focus.extend(['角色引入', '背景設定', '主題暗示'])

        elif chapter_type == 'setup':
            focus.extend(['世界觀展開', '角色塑造', '線索鋪設'])

        elif chapter_type == 'development':
            focus.extend(['劇情推進', '角色發展', '矛盾升級'])

        elif chapter_type == 'escalation':
            focus.extend(['衝突激化', '危機製造', '情緒累積'])

        elif chapter_type == 'climax':
            focus.extend(['決戰對決', '真相揭曉', '角色蛻變'])

        elif chapter_type == 'resolution':
            focus.extend(['劇情收尾', '角色歸宿', '主題昇華'])

        return focus

    def _get_tone(self, chapter_type: str, conflict_level: float) -> str:
        """根據章節類型和衝突強度確定基調"""
        if chapter_type in ['climax', 'escalation']:
            return '緊張激烈'

        elif chapter_type == 'opening':
            return '引人入勝'

        elif chapter_type == 'resolution':
            return '平和感傷' if conflict_level < 0.5 else '激昂壯烈'

        else:
            if conflict_level > 0.6:
                return '緊迫不安'
            elif conflict_level > 0.4:
                return '穩步推進'
            else:
                return '平穩舒緩'

    def _get_key_elements(self, chapter_type: str) -> list:
        """根據章節類型列出關鍵要素"""
        elements = {
            'opening': ['主角亮相', '故事起點', '初始目標'],
            'setup': ['人物關係', '背景信息', '伏筆設置'],
            'development': ['事件推進', '角色成長', '矛盾深化'],
            'escalation': ['壓力增加', '時間緊迫', '選擇困境'],
            'climax': ['最終對決', '真相大白', '情感爆發'],
            'resolution': ['結局交代', '懸念解答', '情感餘韻'],
        }

        return elements.get(chapter_type, [])

    def validate_chapter_pacing(self, chapter_num: int, actual_intensity: float) -> Dict:
        """
        驗證章節節奏

        Args:
            chapter_num: 章節號
            actual_intensity: 實際衝突強度

        Returns:
            驗證結果（來自 ConflictEscalator）
        """
        return self.conflict_escalator.enforce_escalation(chapter_num, actual_intensity)

    def visualize_plot_curve(self) -> str:
        """可視化劇情曲線"""
        return self.conflict_escalator.visualize_curve()


if __name__ == '__main__':
    # 測試劇情管理器
    logging.basicConfig(level=logging.INFO)

    manager = PlotManager(total_chapters=30)

    print("=== 劇情曲線 ===")
    print(manager.visualize_plot_curve())

    print("\n=== 第 1 章劇情指引 ===")
    guidance1 = manager.generate_plot_guidance(1)
    print(f"類型: {guidance1['chapter_type_name']}")
    print(f"衝突強度: {guidance1['conflict_level']:.2f}")
    print(f"基調: {guidance1['tone']}")
    print("節奏建議:")
    for s in guidance1['pacing_suggestions']:
        print(f"  - {s}")

    print("\n=== 第 15 章劇情指引 ===")
    guidance15 = manager.generate_plot_guidance(15)
    print(f"類型: {guidance15['chapter_type_name']}")
    print(f"衝突強度: {guidance15['conflict_level']:.2f}")
    print(f"內容重點: {', '.join(guidance15['content_focus'])}")

    print("\n=== 第 28 章劇情指引（高潮） ===")
    guidance28 = manager.generate_plot_guidance(28)
    print(f"類型: {guidance28['chapter_type_name']}")
    print(f"衝突強度: {guidance28['conflict_level']:.2f}")
    print(f"關鍵要素: {', '.join(guidance28['key_elements'])}")
