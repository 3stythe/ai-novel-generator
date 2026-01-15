# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 角色弧光強制器
確保角色發展遵循預定弧線，防止人設崩潰和發展倒退
"""

import json
import logging
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class CharacterArcEnforcer:
    """
    角色弧光強制器

    功能:
    - 載入角色弧光配置
    - 檢查角色狀態一致性
    - 檢測狀態倒退
    - 檢測遺漏的關鍵轉折點
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化強制器

        Args:
            config_path: 角色弧光配置文件路徑（JSON）
        """
        self.arcs = {}
        self.config_path = config_path

        if config_path:
            self.load_arcs_from_config(config_path)

        logger.info("角色弧光強制器初始化完成")

    def load_arcs_from_config(self, config_path: str) -> Dict:
        """
        從配置文件載入角色弧光

        Args:
            config_path: 配置文件路徑

        Returns:
            角色弧光字典

        配置格式:
        {
            "character_name": {
                "states": ["state1", "state2", "state3"],  # 狀態序列
                "triggers": {                              # 觸發條件
                    1: "state1",  # 第1章應達到 state1
                    5: "state2",  # 第5章應達到 state2
                    10: "state3"  # 第10章應達到 state3
                },
                "milestones": [                            # 關鍵里程碑
                    {
                        "chapter": 3,
                        "event": "遇到導師",
                        "state_change": "state1 -> state2"
                    }
                ]
            }
        }
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 清空現有配置
            self.arcs = {}

            # 過濾並載入角色配置
            for char_name, arc_data in data.items():
                # 跳過元數據字段（以 _ 開頭）
                if char_name.startswith('_'):
                    logger.debug(f"跳過元數據字段: {char_name}")
                    continue

                # 驗證是否為字典
                if not isinstance(arc_data, dict):
                    logger.warning(f"跳過無效角色配置 '{char_name}': 不是字典類型 ({type(arc_data).__name__})")
                    continue

                # 驗證必要欄位
                if 'states' not in arc_data:
                    logger.warning(f"角色 '{char_name}' 缺少 states 定義，已跳過")
                    continue

                if 'triggers' not in arc_data:
                    logger.warning(f"角色 '{char_name}' 缺少 triggers 定義，已跳過")
                    continue

                # 驗證 states 是列表
                if not isinstance(arc_data['states'], list):
                    logger.warning(f"角色 '{char_name}' 的 states 不是列表類型，已跳過")
                    continue

                # 驗證 triggers 是字典
                if not isinstance(arc_data['triggers'], dict):
                    logger.warning(f"角色 '{char_name}' 的 triggers 不是字典類型，已跳過")
                    continue

                # 通過所有驗證，載入角色配置
                self.arcs[char_name] = arc_data
                logger.info(f"載入角色弧光: {char_name} ({len(arc_data['states'])} 個狀態)")

            logger.info(f"成功載入 {len(self.arcs)} 個角色弧光配置")

            if len(self.arcs) == 0:
                logger.warning("未載入任何有效的角色弧光配置")

            return self.arcs

        except FileNotFoundError:
            logger.error(f"配置文件不存在: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"載入配置失敗: {e}")
            raise

    def add_character_arc(
        self,
        character: str,
        states: List[str],
        triggers: Dict[int, str],
        milestones: Optional[List[Dict]] = None
    ):
        """
        手動添加角色弧光

        Args:
            character: 角色名稱
            states: 狀態序列
            triggers: 觸發章節映射 {章節號: 狀態}
            milestones: 里程碑列表（可選）
        """
        self.arcs[character] = {
            'states': states,
            'triggers': triggers,
            'milestones': milestones or []
        }

        logger.info(f"添加角色弧光: {character}, 狀態數={len(states)}")

    def enforce_arc_consistency(
        self,
        character: str,
        chapter_num: int,
        current_state: str,
        chapter_outline: Optional[str] = None
    ) -> Dict:
        """
        強制角色弧光一致性檢查

        Args:
            character: 角色名稱
            chapter_num: 當前章節號
            current_state: 當前狀態描述
            chapter_outline: 當前章節大綱（可選，用於里程碑檢查）

        Returns:
            檢查結果字典:
            {
                'is_consistent': bool,      # 是否一致
                'expected_state': str,       # 預期狀態
                'current_state': str,        # 當前狀態
                'is_regression': bool,       # 是否倒退
                'missed_triggers': list,     # 遺漏的觸發點
                'missed_milestones': list,   # 遺漏的里程碑
                'warnings': list,            # 警告訊息
                'errors': list,              # 錯誤訊息
            }
        """
        result = {
            'is_consistent': True,
            'expected_state': '',
            'current_state': current_state,
            'is_regression': False,
            'missed_triggers': [],
            'missed_milestones': [],
            'warnings': [],
            'errors': [],
        }

        # 檢查角色是否已配置
        if character not in self.arcs:
            result['warnings'].append(f"角色 {character} 未配置弧光，跳過檢查")
            return result

        arc = self.arcs[character]

        # 1. 獲取預期狀態
        expected_state = self._get_expected_state(character, chapter_num)
        result['expected_state'] = expected_state

        if not expected_state:
            result['warnings'].append(f"第 {chapter_num} 章無預期狀態定義")
            return result

        # 2. 檢查狀態倒退
        is_regression = self._is_state_regression(character, current_state, expected_state)
        result['is_regression'] = is_regression

        if is_regression:
            result['is_consistent'] = False
            result['errors'].append(
                f"角色 {character} 狀態倒退: 預期 {expected_state}，實際 {current_state}"
            )

        # 3. 檢查遺漏的觸發點
        missed = self._check_missed_triggers(character, chapter_num)
        result['missed_triggers'] = missed

        if missed:
            result['warnings'].append(
                f"遺漏觸發點: 第 {', '.join(map(str, missed))} 章應有狀態變化"
            )

        # 4. 檢查里程碑
        if chapter_outline and 'milestones' in arc:
            missed_milestones = self._check_milestones(
                character, chapter_num, chapter_outline
            )
            result['missed_milestones'] = missed_milestones

            if missed_milestones:
                result['warnings'].append(
                    f"遺漏里程碑事件: {', '.join(m['event'] for m in missed_milestones)}"
                )

        logger.info(
            f"角色 {character} 第 {chapter_num} 章弧光檢查: "
            f"一致={result['is_consistent']}, "
            f"倒退={is_regression}, "
            f"遺漏觸發={len(missed)}"
        )

        return result

    def _get_expected_state(self, character: str, chapter_num: int) -> str:
        """
        獲取角色在指定章節的預期狀態

        Args:
            character: 角色名稱
            chapter_num: 章節號

        Returns:
            預期狀態（如果有觸發點），否則返回空字符串
        """
        # 檢查角色是否存在
        if character not in self.arcs:
            logger.debug(f"角色 '{character}' 不在弧光配置中")
            return ''

        arc = self.arcs[character]

        # 類型檢查：確保 arc 是字典
        if not isinstance(arc, dict):
            logger.warning(f"角色 '{character}' 的弧光配置格式錯誤: {type(arc).__name__}（應為字典）")
            return ''

        triggers = arc.get('triggers', {})

        # 類型檢查：確保 triggers 是字典
        if not isinstance(triggers, dict):
            logger.warning(f"角色 '{character}' 的 triggers 格式錯誤: {type(triggers).__name__}（應為字典）")
            return ''

        # 查找最近的觸發點
        # 將 triggers 按章節號（整數）排序
        expected_state = ''
        try:
            sorted_triggers = sorted(
                triggers.items(),
                key=lambda x: int(x[0])  # 按章節號（整數）排序
            )

            for trigger_chapter_str, state in sorted_triggers:
                try:
                    trigger_chapter = int(trigger_chapter_str)
                    if trigger_chapter <= chapter_num:
                        expected_state = state
                    else:
                        break
                except (ValueError, TypeError) as e:
                    logger.warning(f"角色 '{character}' 的觸發點格式錯誤: {trigger_chapter_str} -> {state}")
                    continue
        except (ValueError, TypeError) as e:
            logger.warning(f"角色 '{character}' 的 triggers 排序錯誤: {e}")

        return expected_state

    def _is_state_regression(
        self,
        character: str,
        current_state: str,
        expected_state: str
    ) -> bool:
        """
        判斷是否發生狀態倒退

        Args:
            character: 角色名稱
            current_state: 當前狀態
            expected_state: 預期狀態

        Returns:
            是否倒退
        """
        # 檢查角色是否存在
        if character not in self.arcs:
            return False

        arc = self.arcs[character]

        # 類型檢查：確保 arc 是字典
        if not isinstance(arc, dict):
            logger.warning(f"角色 '{character}' 的弧光配置格式錯誤: {type(arc).__name__}（應為字典）")
            return False

        states = arc.get('states', [])

        # 類型檢查：確保 states 是列表
        if not isinstance(states, list):
            logger.warning(f"角色 '{character}' 的 states 格式錯誤: {type(states).__name__}（應為列表）")
            return False

        if not states or not current_state or not expected_state:
            return False

        # 查找狀態在序列中的位置
        try:
            current_index = self._find_state_index(states, current_state)
            expected_index = self._find_state_index(states, expected_state)

            # 當前狀態索引小於預期狀態索引，表示倒退
            return current_index < expected_index

        except ValueError:
            # 狀態不在序列中，無法判斷
            logger.warning(f"狀態 {current_state} 或 {expected_state} 不在序列中")
            return False

    def _find_state_index(self, states: List[str], state: str) -> int:
        """
        查找狀態在序列中的索引（支持部分匹配）

        Args:
            states: 狀態序列
            state: 要查找的狀態

        Returns:
            狀態索引

        Raises:
            ValueError: 狀態不存在
        """
        # 完全匹配
        if state in states:
            return states.index(state)

        # 部分匹配（狀態描述包含關鍵詞）
        for i, s in enumerate(states):
            if s in state or state in s:
                return i

        raise ValueError(f"狀態 {state} 不在序列中")

    def _check_missed_triggers(self, character: str, chapter_num: int) -> List[int]:
        """
        檢查遺漏的觸發點

        Args:
            character: 角色名稱
            chapter_num: 當前章節號

        Returns:
            遺漏的觸發章節列表
        """
        # 檢查角色是否存在
        if character not in self.arcs:
            return []

        arc = self.arcs[character]

        # 類型檢查：確保 arc 是字典
        if not isinstance(arc, dict):
            logger.warning(f"角色 '{character}' 的弧光配置格式錯誤: {type(arc).__name__}（應為字典）")
            return []

        triggers = arc.get('triggers', {})

        # 類型檢查：確保 triggers 是字典
        if not isinstance(triggers, dict):
            logger.warning(f"角色 '{character}' 的 triggers 格式錯誤: {type(triggers).__name__}（應為字典）")
            return []

        missed = []

        for trigger_chapter in triggers.keys():
            try:
                trigger_chapter = int(trigger_chapter)
                # 如果觸發點在當前章節之前，但沒有被記錄，視為遺漏
                # （此處簡化實現，實際應維護狀態歷史）
                if trigger_chapter < chapter_num:
                    # 這裡需要外部傳入狀態歷史才能準確判斷
                    # 暫時跳過
                    pass
            except (ValueError, TypeError) as e:
                logger.warning(f"角色 '{character}' 的觸發點格式錯誤: {trigger_chapter}")
                continue

        return missed

    def _check_milestones(
        self,
        character: str,
        chapter_num: int,
        chapter_outline: str
    ) -> List[Dict]:
        """
        檢查里程碑事件

        Args:
            character: 角色名稱
            chapter_num: 章節號
            chapter_outline: 章節大綱

        Returns:
            遺漏的里程碑列表
        """
        # 檢查角色是否存在
        if character not in self.arcs:
            return []

        arc = self.arcs[character]

        # 類型檢查：確保 arc 是字典
        if not isinstance(arc, dict):
            logger.warning(f"角色 '{character}' 的弧光配置格式錯誤: {type(arc).__name__}（應為字典）")
            return []

        milestones = arc.get('milestones', [])

        # 類型檢查：確保 milestones 是列表
        if not isinstance(milestones, list):
            logger.warning(f"角色 '{character}' 的 milestones 格式錯誤: {type(milestones).__name__}（應為列表）")
            return []

        missed = []

        for milestone in milestones:
            # 確保 milestone 是字典
            if not isinstance(milestone, dict):
                logger.warning(f"角色 '{character}' 的里程碑格式錯誤: {type(milestone).__name__}（應為字典）")
                continue

            try:
                if milestone.get('chapter') == chapter_num:
                    # 檢查大綱中是否包含該事件關鍵詞
                    event = milestone.get('event', '')
                    if event and event not in chapter_outline:
                        missed.append(milestone)
            except (KeyError, TypeError) as e:
                logger.warning(f"角色 '{character}' 的里程碑處理錯誤: {e}")
                continue

        return missed

    def get_character_progression(self, character: str) -> Dict:
        """
        獲取角色發展全貌

        Args:
            character: 角色名稱

        Returns:
            角色發展信息
        """
        if character not in self.arcs:
            return {}

        arc = self.arcs[character]

        return {
            'character': character,
            'total_states': len(arc.get('states', [])),
            'states': arc.get('states', []),
            'trigger_chapters': sorted([int(k) for k in arc.get('triggers', {}).keys()]),
            'milestones_count': len(arc.get('milestones', [])),
            'milestones': arc.get('milestones', [])
        }

    def generate_state_suggestions(self, character: str, chapter_num: int) -> List[str]:
        """
        生成狀態建議

        Args:
            character: 角色名稱
            chapter_num: 章節號

        Returns:
            建議列表
        """
        suggestions = []

        if character not in self.arcs:
            suggestions.append(f"角色 {character} 未配置弧光，建議添加配置")
            return suggestions

        expected_state = self._get_expected_state(character, chapter_num)

        if expected_state:
            suggestions.append(f"當前章節角色應達到狀態: {expected_state}")

        # 檢查即將到來的里程碑
        arc = self.arcs[character]
        for milestone in arc.get('milestones', []):
            if milestone['chapter'] == chapter_num:
                suggestions.append(f"關鍵事件: {milestone['event']}")
            elif milestone['chapter'] == chapter_num + 1:
                suggestions.append(f"下章準備事件: {milestone['event']}")

        return suggestions


if __name__ == '__main__':
    # 測試強制器
    logging.basicConfig(level=logging.INFO)

    enforcer = CharacterArcEnforcer()

    # 手動添加角色弧光
    enforcer.add_character_arc(
        character="主角",
        states=["普通人", "覺醒", "成長", "蛻變", "強者"],
        triggers={
            1: "普通人",
            3: "覺醒",
            7: "成長",
            12: "蛻變",
            20: "強者"
        },
        milestones=[
            {"chapter": 3, "event": "遇到導師", "state_change": "普通人 -> 覺醒"},
            {"chapter": 7, "event": "首次戰鬥", "state_change": "覺醒 -> 成長"},
            {"chapter": 12, "event": "突破瓶頸", "state_change": "成長 -> 蛻變"}
        ]
    )

    print("=== 第 5 章檢查（正常） ===")
    result1 = enforcer.enforce_arc_consistency("主角", 5, "覺醒階段")
    print(f"一致: {result1['is_consistent']}")
    print(f"預期狀態: {result1['expected_state']}")

    print("\n=== 第 10 章檢查（倒退） ===")
    result2 = enforcer.enforce_arc_consistency("主角", 10, "普通人")
    print(f"一致: {result2['is_consistent']}")
    print(f"倒退: {result2['is_regression']}")
    print(f"錯誤: {result2['errors']}")

    print("\n=== 角色發展全貌 ===")
    progression = enforcer.get_character_progression("主角")
    print(json.dumps(progression, ensure_ascii=False, indent=2))
