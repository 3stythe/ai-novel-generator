# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 分卷管理器
自動規劃分卷、生成卷大綱和章節大綱
"""

import logging
from typing import Dict, List, Optional, Tuple

from utils.outline_validator import OutlineValidator
from utils.plot_manager import PlotManager


logger = logging.getLogger(__name__)


class VolumeManager:
    """
    分卷管理器

    功能:
    - AI 自動分卷規劃
    - 生成卷大綱
    - 生成章節大綱
    - 卷完成判斷
    - 卷摘要生成
    - 整合 OutlineValidator 和 PlotManager
    """

    def __init__(
        self,
        validator: Optional[OutlineValidator] = None,
        plot_manager: Optional[PlotManager] = None
    ):
        """
        初始化分卷管理器

        Args:
            validator: 大綱驗證器（可選）
            plot_manager: 劇情管理器（可選）
        """
        self.validator = validator or OutlineValidator()
        self.plot_manager = plot_manager

        self.volume_plan = {}
        self.current_volume = 0

        logger.info("分卷管理器初始化完成")

    def plan_volumes(
        self,
        title: str,
        genre: str,
        theme: str,
        total_chapters: int,
        chapters_per_volume: Optional[int] = None
    ) -> Dict:
        """
        規劃分卷

        Args:
            title: 小說標題
            genre: 類型
            theme: 主題
            total_chapters: 總章節數
            chapters_per_volume: 每卷章節數（可選，自動計算）

        Returns:
            分卷計劃字典:
            {
                'title': str,
                'genre': str,
                'theme': str,
                'total_chapters': int,
                'total_volumes': int,
                'volumes': [
                    {
                        'volume_num': int,
                        'title': str,
                        'theme': str,
                        'start_chapter': int,
                        'end_chapter': int,
                        'chapter_count': int,
                    },
                    ...
                ]
            }
        """
        # 自動計算每卷章節數
        if chapters_per_volume is None:
            chapters_per_volume = self._auto_calculate_volume_size(total_chapters)

        # 計算卷數
        total_volumes = (total_chapters + chapters_per_volume - 1) // chapters_per_volume

        logger.info(
            f"規劃分卷: 總章節={total_chapters}, "
            f"每卷={chapters_per_volume}章, 總卷數={total_volumes}"
        )

        # 生成卷信息
        volumes = []
        for i in range(total_volumes):
            start_chapter = i * chapters_per_volume + 1
            end_chapter = min((i + 1) * chapters_per_volume, total_chapters)

            volume = {
                'volume_num': int(i + 1),
                'title': self._generate_volume_title(i + 1, total_volumes, title),
                'theme': self._generate_volume_theme(i + 1, total_volumes, theme),
                'start_chapter': int(start_chapter),
                'end_chapter': int(end_chapter),
                'chapter_count': int(end_chapter - start_chapter + 1),
            }

            volumes.append(volume)

        self.volume_plan = {
            'title': title,
            'genre': genre,
            'theme': theme,
            'total_chapters': total_chapters,
            'total_volumes': total_volumes,
            'chapters_per_volume': chapters_per_volume,
            'volumes': volumes,
        }

        logger.info(f"分卷規劃完成: {total_volumes} 卷")

        return self.volume_plan

    def _auto_calculate_volume_size(self, total_chapters: int) -> int:
        """
        自動計算每卷章節數

        Args:
            total_chapters: 總章節數

        Returns:
            建議的每卷章節數
        """
        # 根據總章節數智能分卷
        if total_chapters <= 20:
            return total_chapters  # 不分卷

        elif total_chapters <= 50:
            return 15  # 每卷 15 章

        elif total_chapters <= 100:
            return 20  # 每卷 20 章

        elif total_chapters <= 200:
            return 25  # 每卷 25 章

        else:
            return 30  # 每卷 30 章

    def _generate_volume_title(self, volume_num: int, total_volumes: int, base_title: str) -> str:
        """
        生成卷標題

        Args:
            volume_num: 卷號
            total_volumes: 總卷數
            base_title: 基礎標題

        Returns:
            卷標題
        """
        # 簡單實現，可根據需要使用 AI 生成
        if total_volumes == 1:
            return base_title

        # 根據位置生成默認標題
        if volume_num == 1:
            return f"{base_title} - 第一卷：起"

        elif volume_num == total_volumes:
            return f"{base_title} - 第{volume_num}卷：終"

        else:
            return f"{base_title} - 第{volume_num}卷"

    def _generate_volume_theme(self, volume_num: int, total_volumes: int, base_theme: str) -> str:
        """
        生成卷主題

        Args:
            volume_num: 卷號
            total_volumes: 總卷數
            base_theme: 基礎主題

        Returns:
            卷主題
        """
        # 簡單實現，可根據需要使用 AI 生成
        progress = volume_num / total_volumes

        if progress <= 0.33:
            return f"{base_theme} - 起始與探索"

        elif progress <= 0.67:
            return f"{base_theme} - 成長與挑戰"

        else:
            return f"{base_theme} - 高潮與結局"

    def generate_volume_outline(
        self,
        volume_num: int,
        api_generator_func: Optional[callable] = None
    ) -> str:
        """
        生成卷大綱

        Args:
            volume_num: 卷號
            api_generator_func: API 生成函數（可選）
                簡潔: func(prompt) -> str

        Returns:
            卷大綱文本
        """
        if not self.volume_plan:
            raise ValueError("請先調用 plan_volumes() 規劃分卷")

        if volume_num < 1 or volume_num > self.volume_plan['total_volumes']:
            raise ValueError(f"卷號 {volume_num} 超出範圍")

        volume = self.volume_plan['volumes'][volume_num - 1]

        logger.info(f"生成第 {volume_num} 卷大綱")

        # 構建提示詞
        prompt = self._build_volume_outline_prompt(volume_num)

        # 使用 API 生成（如果有）
        if api_generator_func:
            outline = api_generator_func(prompt)
        else:
            # 默認大綱模板
            outline = self._default_volume_outline(volume_num)

        logger.info(f"第 {volume_num} 卷大綱生成完成（{len(outline)} 字）")

        return outline

    def _build_volume_outline_prompt(self, volume_num: int) -> str:
        """構建卷大綱生成提示詞"""
        volume = self.volume_plan['volumes'][volume_num - 1]

        prompt = f"""請為以下小說的第 {volume_num} 卷創作詳細大綱：

小說資訊:
- 標題：{self.volume_plan['title']}
- 類型：{self.volume_plan['genre']}
- 總主題：{self.volume_plan['theme']}

本卷資訊:
- 卷號：第 {volume_num} 卷（共 {self.volume_plan['total_volumes']} 卷）
- 卷標題：{volume['title']}
- 卷主題：{volume['theme']}
- 章節範圍：第 {volume['start_chapter']}-{volume['end_chapter']} 章（共 {volume['chapter_count']} 章）

請生成包含以下內容的卷大綱：

1. 【卷概要】（200-300字）
   - 本卷的核心事件
   - 主要衝突發展
   - 角色成長軌跡

2. 【關鍵轉折點】
   - 列出本卷的3-5個關鍵事件

3. 【章節規劃簡述】
   - 簡要說明本卷各章的內容走向

請開始創作大綱："""

        return prompt

    def _default_volume_outline(self, volume_num: int) -> str:
        """默認卷大綱模板（當無 API 時使用）"""
        volume = self.volume_plan['volumes'][volume_num - 1]

        return f"""【第 {volume_num} 卷大綱】

卷標題：{volume['title']}
卷主題：{volume['theme']}
章節範圍：第 {volume['start_chapter']}-{volume['end_chapter']} 章

【卷概要】
本卷承接前文，繼續展開 {self.volume_plan['theme']} 的主題。
故事在第 {volume['start_chapter']} 章開始新的階段，
通過 {volume['chapter_count']} 章的發展，推進主線劇情。

【關鍵轉折點】
（待詳細規劃）

【章節規劃】
各章將逐步展開本卷主題，保持節奏和張力。
"""

    def generate_chapter_outlines(
        self,
        volume_num: int,
        volume_outline: str,
        api_generator_func: Optional[callable] = None
    ) -> List[str]:
        """
        生成本卷所有章節的大綱

        Args:
            volume_num: 卷號
            volume_outline: 卷大綱
            api_generator_func: API 生成函數（可選）

        Returns:
            章節大綱列表
        """
        if not self.volume_plan:
            raise ValueError("請先調用 plan_volumes() 規劃分卷")

        volume = self.volume_plan['volumes'][volume_num - 1]

        # 確保類型為整數（防止從 JSON 加載時變成字符串）
        start_chapter = int(volume['start_chapter'])
        end_chapter = int(volume['end_chapter'])

        logger.info(
            f"生成第 {volume_num} 卷的章節大綱 "
            f"({start_chapter}-{end_chapter})"
        )

        chapter_outlines = []

        for chapter_num in range(start_chapter, end_chapter + 1):
            # 構建提示詞
            prompt = self._build_chapter_outline_prompt(
                chapter_num, volume_num, volume_outline, chapter_outlines
            )

            # 使用 API 生成
            if api_generator_func:
                outline = api_generator_func(prompt)
            else:
                outline = f"第 {chapter_num} 章大綱（待生成）"

            # 驗證大綱
            if self.validator:
                validation = self.validator.validate_chapter_outline(
                    outline, chapter_outlines, chapter_num
                )

                if not validation['is_valid']:
                    logger.warning(
                        f"第 {chapter_num} 章大綱驗證失敗: "
                        f"{validation['errors']}"
                    )

            chapter_outlines.append(outline)

        logger.info(f"第 {volume_num} 卷章節大綱生成完成（{len(chapter_outlines)} 章）")

        return chapter_outlines

    def _build_chapter_outline_prompt(
        self,
        chapter_num: int,
        volume_num: int,
        volume_outline: str,
        previous_outlines: List[str]
    ) -> str:
        """構建章節大綱生成提示詞"""
        volume = self.volume_plan['volumes'][volume_num - 1]

        # 確保類型為整數（防止從 JSON 加載時變成字符串）
        start_chapter = int(volume['start_chapter'])

        # 獲取劇情指引（如果有 PlotManager）
        plot_guidance = ""
        if self.plot_manager:
            guidance = self.plot_manager.generate_plot_guidance(
                chapter_num,
                self.volume_plan['total_chapters'],
                volume_num,
                volume['theme']
            )

            plot_guidance = f"""
劇情指引:
- 章節類型：{guidance['chapter_type_name']}
- 衝突強度：{guidance['conflict_level']:.2f}
- 內容重點：{', '.join(guidance['content_focus'])}
- 節奏基調：{guidance['tone']}
"""

        # 上一章大綱預覽
        previous_context = ""
        if previous_outlines:
            prev_outline = previous_outlines[-1]
            preview_length = min(200, len(prev_outline))
            previous_context = f"\n【上一章大綱】\n{prev_outline[:preview_length]}...\n"

        prompt = f"""請為以下小說的第 {chapter_num} 章創作詳細大綱：

小說資訊:
- 標題：{self.volume_plan['title']}
- 類型：{self.volume_plan['genre']}

本卷資訊:
- 第 {volume_num} 卷：{volume['title']}
- 卷主題：{volume['theme']}

【卷大綱】
{volume_outline}
{previous_context}{plot_guidance}
當前任務:
- 創作第 {chapter_num} 章大綱
- 位置：第 {volume_num} 卷的第 {chapter_num - start_chapter + 1} 章
- 總進度：全書第 {chapter_num}/{self.volume_plan['total_chapters']} 章

請生成包含以下內容的章節大綱（200-300字）：
1. 本章的核心事件
2. 角色發展重點
3. 為下一章埋下伏筆
4. 衝突或張力的設置

請開始創作大綱："""

        return prompt

    def should_end_volume(
        self,
        volume_num: int,
        chapters_in_volume: int,
        current_chapter: int
    ) -> Tuple[bool, str]:
        """
        判斷是否應結束當前卷

        Args:
            volume_num: 當前卷號
            chapters_in_volume: 本卷已生成章節數
            current_chapter: 當前章節號（全書）

        Returns:
            (是否結束, 原因說明)
        """
        if not self.volume_plan:
            return False, "未規劃分卷"

        volume = self.volume_plan['volumes'][volume_num - 1]

        # 確保類型為整數（防止從 JSON 加載時變成字符串）
        end_chapter = int(volume['end_chapter'])
        chapter_count = int(volume['chapter_count'])

        # 已達到預定章節數
        if current_chapter >= end_chapter:
            return True, f"已達到第 {volume_num} 卷預定結束章節"

        # 超過計劃章節數（允許小幅彈性）
        if chapters_in_volume >= chapter_count + 2:
            return True, f"本卷章節數已超過計劃（{chapters_in_volume}/{chapter_count}）"

        return False, ""

    def generate_volume_summary(
        self,
        volume_num: int,
        chapter_contents: List[str],
        api_generator_func: Optional[callable] = None
    ) -> str:
        """
        生成卷摘要

        Args:
            volume_num: 卷號
            chapter_contents: 本卷所有章節內容列表
            api_generator_func: API 生成函數（可選）

        Returns:
            卷摘要文本
        """
        if not self.volume_plan:
            raise ValueError("請先調用 plan_volumes() 規劃分卷")

        volume = self.volume_plan['volumes'][volume_num - 1]

        logger.info(f"生成第 {volume_num} 卷摘要")

        # 構建提示詞
        prompt = self._build_volume_summary_prompt(volume_num, chapter_contents)

        # 使用 API 生成
        if api_generator_func:
            summary = api_generator_func(prompt)
        else:
            summary = self._default_volume_summary(volume_num, chapter_contents)

        logger.info(f"第 {volume_num} 卷摘要生成完成（{len(summary)} 字）")

        return summary

    def _build_volume_summary_prompt(
        self,
        volume_num: int,
        chapter_contents: List[str]
    ) -> str:
        """構建卷摘要生成提示詞"""
        volume = self.volume_plan['volumes'][volume_num - 1]

        # 確保類型為整數（防止從 JSON 加載時變成字符串）
        start_chapter = int(volume['start_chapter'])

        # 提取各章關鍵內容（每章取前300字）
        chapter_previews = []
        for i, content in enumerate(chapter_contents):
            chapter_num = start_chapter + i
            preview = content[:300] + "..." if len(content) > 300 else content
            chapter_previews.append(f"第{chapter_num}章預覽:\n{preview}")

        previews_text = "\n\n".join(chapter_previews)

        prompt = f"""請為以下小說的第 {volume_num} 卷創作摘要：

小說資訊:
- 標題：{self.volume_plan['title']}
- 第 {volume_num} 卷：{volume['title']}
- 章節範圍：第 {volume['start_chapter']}-{volume['end_chapter']} 章

【各章預覽】
{previews_text}

請生成包含以下內容的卷摘要（400-600字）：
1. 本卷主要事件梳理
2. 角色成長與關係變化
3. 重要伏筆和轉折點
4. 為下一卷的鋪墊

請開始創作摘要："""

        return prompt

    def _default_volume_summary(self, volume_num: int, chapter_contents: List[str]) -> str:
        """默認卷摘要模板"""
        volume = self.volume_plan['volumes'][volume_num - 1]

        return f"""【第 {volume_num} 卷摘要】

本卷標題：{volume['title']}
本卷涵蓋第 {volume['start_chapter']}-{volume['end_chapter']} 章，共 {len(chapter_contents)} 章。

本卷通過一系列事件推進主線劇情，角色經歷成長與變化。
關鍵轉折點為下一卷埋下伏筆。

總字數：約 {sum(len(c) for c in chapter_contents)} 字
"""

    def get_volume_info(self, volume_num: int) -> Dict:
        """獲取卷信息"""
        if not self.volume_plan or volume_num < 1 or volume_num > self.volume_plan['total_volumes']:
            return {}

        return self.volume_plan['volumes'][volume_num - 1].copy()


if __name__ == '__main__':
    # 測試分卷管理器
    logging.basicConfig(level=logging.INFO)

    # 創建 PlotManager
    plot_manager = PlotManager(total_chapters=60)

    # 創建 VolumeManager
    manager = VolumeManager(plot_manager=plot_manager)

    # 規劃分卷
    plan = manager.plan_volumes(
        title="測試小說",
        genre="玄幻",
        theme="逆天改命",
        total_chapters=60
    )

    print("=== 分卷計劃 ===")
    print(f"總卷數: {plan['total_volumes']}")
    for vol in plan['volumes']:
        print(f"第{vol['volume_num']}卷: {vol['title']} ({vol['start_chapter']}-{vol['end_chapter']}章)")

    print("\n=== 生成第 1 卷大綱 ===")
    outline = manager.generate_volume_outline(1)
    print(outline[:300])

    print("\n=== 卷完成判斷 ===")
    should_end, reason = manager.should_end_volume(1, 20, 20)
    print(f"結束: {should_end}, 原因: {reason}")
