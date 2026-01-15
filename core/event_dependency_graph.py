# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 事件依賴圖
使用有向圖追蹤事件依賴關係，檢測情節漏洞
"""

import logging
from typing import Dict, List, Optional, Set, Tuple

# 嘗試導入 networkx，優雅降級
try:
    import networkx as nx
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    logging.warning(
        "networkx 未安裝，事件依賴圖功能受限。"
        "安裝方法: pip install networkx"
    )


logger = logging.getLogger(__name__)


class EventDependencyGraph:
    """
    事件依賴圖

    功能:
    - 建立事件依賴關係（有向圖）
    - 驗證事件完整性（前置事件是否發生）
    - 檢測情節漏洞（孤立事件、循環依賴）
    - 追蹤事件影響鏈
    """

    def __init__(self, use_networkx: bool = True):
        """
        初始化事件圖

        Args:
            use_networkx: 是否使用 networkx（需要安裝庫）
        """
        self.use_networkx = use_networkx and GRAPH_AVAILABLE

        if self.use_networkx:
            self.graph = nx.DiGraph()
        else:
            # 使用簡單字典實現
            self.graph = {}

        self.events = {}  # event_id -> event_info

        logger.info(f"事件依賴圖初始化完成 (使用 networkx: {self.use_networkx})")

    def add_event(
        self,
        event_id: str,
        chapter_num: int,
        description: str = "",
        dependencies: Optional[List[str]] = None,
        consequences: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        添加事件

        Args:
            event_id: 事件唯一標識
            chapter_num: 發生章節號
            description: 事件描述
            dependencies: 前置事件列表（必須先發生的事件）
            consequences: 後續事件列表（此事件導致的事件）
            metadata: 額外元數據
        """
        dependencies = dependencies or []
        consequences = consequences or []
        metadata = metadata or {}

        # 儲存事件信息
        self.events[event_id] = {
            'chapter_num': chapter_num,
            'description': description,
            'dependencies': dependencies,
            'consequences': consequences,
            'metadata': metadata
        }

        if self.use_networkx:
            # 添加節點
            self.graph.add_node(
                event_id,
                chapter=chapter_num,
                description=description,
                **metadata
            )

            # 添加依賴邊（dependency -> event）
            for dep in dependencies:
                self.graph.add_edge(dep, event_id, relation='prerequisite')

            # 添加結果邊（event -> consequence）
            for cons in consequences:
                self.graph.add_edge(event_id, cons, relation='consequence')

        else:
            # 簡單實現
            if event_id not in self.graph:
                self.graph[event_id] = {'in': [], 'out': []}

            for dep in dependencies:
                if dep not in self.graph:
                    self.graph[dep] = {'in': [], 'out': []}
                self.graph[dep]['out'].append(event_id)
                self.graph[event_id]['in'].append(dep)

        logger.info(
            f"添加事件: {event_id} (第{chapter_num}章), "
            f"依賴={len(dependencies)}, 結果={len(consequences)}"
        )

    def validate_event_integrity(self) -> Dict:
        """
        驗證事件完整性

        Returns:
            驗證結果字典:
            {
                'is_valid': bool,           # 是否完整
                'missing_dependencies': list,# 缺失的前置事件
                'orphaned_events': list,    # 孤立事件（無依賴無結果）
                'circular_dependencies': list,# 循環依賴
                'timeline_violations': list,# 時間線錯誤
                'warnings': list,           # 警告訊息
                'errors': list,             # 錯誤訊息
            }
        """
        result = {
            'is_valid': True,
            'missing_dependencies': [],
            'orphaned_events': [],
            'circular_dependencies': [],
            'timeline_violations': [],
            'warnings': [],
            'errors': [],
        }

        # 1. 檢查缺失的依賴
        missing = self._check_missing_dependencies()
        result['missing_dependencies'] = missing

        if missing:
            result['is_valid'] = False
            result['errors'].append(
                f"缺失前置事件: {', '.join(missing)}"
            )

        # 2. 檢查孤立事件
        orphaned = self._find_orphaned_events()
        result['orphaned_events'] = orphaned

        if orphaned:
            result['warnings'].append(
                f"孤立事件（無前後關係）: {', '.join(orphaned)}"
            )

        # 3. 檢查循環依賴
        if self.use_networkx:
            try:
                cycles = list(nx.simple_cycles(self.graph))
                if cycles:
                    result['circular_dependencies'] = cycles
                    result['is_valid'] = False
                    result['errors'].append(
                        f"檢測到循環依賴: {cycles}"
                    )
            except Exception as e:
                logger.warning(f"循環依賴檢測失敗: {e}")

        # 4. 檢查時間線錯誤
        timeline_errors = self._check_timeline_violations()
        result['timeline_violations'] = timeline_errors

        if timeline_errors:
            result['is_valid'] = False
            result['errors'].append(
                "時間線錯誤：後續事件發生在前置事件之前"
            )

        logger.info(
            f"事件完整性驗證: 完整={result['is_valid']}, "
            f"缺失={len(missing)}, 孤立={len(orphaned)}, "
            f"循環={len(result['circular_dependencies'])}"
        )

        return result

    def _check_missing_dependencies(self) -> List[str]:
        """檢查缺失的依賴事件"""
        missing = []

        for event_id, event_info in self.events.items():
            for dep in event_info['dependencies']:
                if dep not in self.events:
                    missing.append(dep)

        return list(set(missing))

    def _find_orphaned_events(self) -> List[str]:
        """查找孤立事件（無依賴且無結果）"""
        orphaned = []

        if self.use_networkx:
            for node in self.graph.nodes():
                if self.graph.in_degree(node) == 0 and self.graph.out_degree(node) == 0:
                    orphaned.append(node)
        else:
            for event_id in self.graph:
                if not self.graph[event_id]['in'] and not self.graph[event_id]['out']:
                    orphaned.append(event_id)

        return orphaned

    def _check_timeline_violations(self) -> List[Tuple[str, str]]:
        """
        檢查時間線錯誤

        Returns:
            錯誤列表 [(event, dependency)]
        """
        violations = []

        for event_id, event_info in self.events.items():
            event_chapter = event_info['chapter_num']

            for dep in event_info['dependencies']:
                if dep in self.events:
                    dep_chapter = self.events[dep]['chapter_num']

                    # 依賴事件應在當前事件之前發生
                    if dep_chapter >= event_chapter:
                        violations.append((event_id, dep))

        return violations

    def get_plot_holes(self) -> List[Dict]:
        """
        獲取情節漏洞列表

        Returns:
            漏洞列表，每個漏洞包含:
            {
                'type': str,        # 漏洞類型
                'event': str,       # 相關事件
                'description': str, # 描述
                'severity': str,    # 嚴重程度（high/medium/low）
            }
        """
        holes = []

        # 驗證完整性
        validation = self.validate_event_integrity()

        # 缺失依賴 -> 高嚴重度
        for missing in validation['missing_dependencies']:
            holes.append({
                'type': 'missing_dependency',
                'event': missing,
                'description': f"事件 {missing} 被引用但未定義",
                'severity': 'high'
            })

        # 循環依賴 -> 高嚴重度
        for cycle in validation['circular_dependencies']:
            holes.append({
                'type': 'circular_dependency',
                'event': ' -> '.join(cycle),
                'description': f"循環依賴: {' -> '.join(cycle)}",
                'severity': 'high'
            })

        # 時間線錯誤 -> 高嚴重度
        for event, dep in validation['timeline_violations']:
            holes.append({
                'type': 'timeline_violation',
                'event': event,
                'description': f"事件 {event} 依賴 {dep}，但發生時間順序錯誤",
                'severity': 'high'
            })

        # 孤立事件 -> 中嚴重度
        for orphan in validation['orphaned_events']:
            holes.append({
                'type': 'orphaned_event',
                'event': orphan,
                'description': f"孤立事件 {orphan}，無前後關係",
                'severity': 'medium'
            })

        return holes

    def get_event_chain(self, event_id: str) -> Dict:
        """
        獲取事件的影響鏈

        Args:
            event_id: 事件ID

        Returns:
            影響鏈信息:
            {
                'predecessors': list,  # 前置事件鏈
                'successors': list,    # 後續事件鏈
                'depth': int,          # 依賴深度
            }
        """
        result = {
            'predecessors': [],
            'successors': [],
            'depth': 0
        }

        if event_id not in self.events:
            return result

        if self.use_networkx:
            try:
                # 前置事件（所有祖先）
                result['predecessors'] = list(nx.ancestors(self.graph, event_id))

                # 後續事件（所有後代）
                result['successors'] = list(nx.descendants(self.graph, event_id))

                # 依賴深度（最長路徑）
                if result['predecessors']:
                    paths = []
                    for pred in result['predecessors']:
                        if self.graph.in_degree(pred) == 0:  # 根節點
                            try:
                                path_length = nx.shortest_path_length(
                                    self.graph, pred, event_id
                                )
                                paths.append(path_length)
                            except nx.NetworkXNoPath:
                                pass
                    result['depth'] = max(paths) if paths else 0

            except Exception as e:
                logger.warning(f"獲取事件鏈失敗: {e}")

        return result

    def visualize_graph(self, max_events: int = 20) -> str:
        """
        可視化事件圖（簡單文本表示）

        Args:
            max_events: 最多顯示事件數

        Returns:
            文本圖表
        """
        lines = ["事件依賴圖", "=" * 60]

        event_ids = list(self.events.keys())[:max_events]

        for event_id in event_ids:
            event_info = self.events[event_id]
            chapter = event_info['chapter_num']
            desc = event_info['description'][:30]

            lines.append(f"\n[{event_id}] 第{chapter}章: {desc}")

            if event_info['dependencies']:
                lines.append(f"  ← 依賴: {', '.join(event_info['dependencies'])}")

            if event_info['consequences']:
                lines.append(f"  → 導致: {', '.join(event_info['consequences'])}")

        if len(self.events) > max_events:
            lines.append(f"\n... 還有 {len(self.events) - max_events} 個事件未顯示")

        return '\n'.join(lines)


if __name__ == '__main__':
    # 測試事件圖
    logging.basicConfig(level=logging.INFO)

    graph = EventDependencyGraph()

    # 添加事件
    graph.add_event("E1", 1, "主角遇到導師")
    graph.add_event("E2", 3, "主角習得心法", dependencies=["E1"])
    graph.add_event("E3", 5, "主角戰勝強敵", dependencies=["E2"])
    graph.add_event("E4", 7, "導師被殺", dependencies=["E1"], consequences=["E5"])
    graph.add_event("E5", 9, "主角復仇", dependencies=["E3", "E4"])
    graph.add_event("E6", 2, "孤立事件")  # 孤立事件

    print("=== 事件圖 ===")
    print(graph.visualize_graph())

    print("\n=== 完整性驗證 ===")
    validation = graph.validate_event_integrity()
    print(f"完整: {validation['is_valid']}")
    print(f"孤立事件: {validation['orphaned_events']}")

    print("\n=== 情節漏洞 ===")
    holes = graph.get_plot_holes()
    for hole in holes:
        print(f"[{hole['severity'].upper()}] {hole['type']}: {hole['description']}")

    print("\n=== E5 事件鏈 ===")
    chain = graph.get_event_chain("E5")
    print(f"前置: {chain['predecessors']}")
    print(f"後續: {chain['successors']}")
    print(f"深度: {chain['depth']}")
