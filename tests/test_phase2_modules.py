# -*- coding: utf-8 -*-
"""
Phase 2.1 模組測試腳本
驗證所有新增模組是否正確導入和運行
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """測試所有模組導入"""
    print("\n" + "="*60)
    print("Phase 2.1 模組導入測試")
    print("="*60)

    modules_to_test = [
        ("utils.outline_validator", "OutlineValidator"),
        ("core.character_arc_enforcer", "CharacterArcEnforcer"),
        ("core.conflict_escalator", "ConflictEscalator"),
        ("core.event_dependency_graph", "EventDependencyGraph"),
        ("utils.plot_manager", "PlotManager"),
        ("utils.volume_manager", "VolumeManager"),
        ("templates.prompts", "PromptTemplates"),
    ]

    results = []

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            results.append((module_name, class_name, "✓", None))
            print(f"✓ {module_name}.{class_name}")
        except Exception as e:
            results.append((module_name, class_name, "✗", str(e)))
            print(f"✗ {module_name}.{class_name}: {e}")

    return results


def test_basic_functionality():
    """測試基本功能"""
    print("\n" + "="*60)
    print("基本功能測試")
    print("="*60)

    try:
        # 1. OutlineValidator
        print("\n1. 測試 OutlineValidator...")
        from utils.outline_validator import OutlineValidator
        validator = OutlineValidator(similarity_threshold=0.7)
        result = validator.validate_chapter_outline(
            "主角遇到神秘老人，學習心法",
            [],
            chapter_num=1
        )
        print(f"   驗證結果: {result['is_valid']}")

        # 2. CharacterArcEnforcer
        print("\n2. 測試 CharacterArcEnforcer...")
        from core.character_arc_enforcer import CharacterArcEnforcer
        enforcer = CharacterArcEnforcer()
        enforcer.add_character_arc(
            "主角",
            ["普通人", "覺醒", "強者"],
            {1: "普通人", 5: "覺醒", 10: "強者"}
        )
        result = enforcer.enforce_arc_consistency("主角", 5, "覺醒")
        print(f"   一致性檢查: {result['is_consistent']}")

        # 3. ConflictEscalator
        print("\n3. 測試 ConflictEscalator...")
        from core.conflict_escalator import ConflictEscalator
        escalator = ConflictEscalator()
        arc = escalator.plan_conflict_arc(30)
        print(f"   衝突曲線長度: {len(arc)}")

        # 4. EventDependencyGraph
        print("\n4. 測試 EventDependencyGraph...")
        from core.event_dependency_graph import EventDependencyGraph
        graph = EventDependencyGraph()
        graph.add_event("E1", 1, "事件1")
        graph.add_event("E2", 2, "事件2", dependencies=["E1"])
        validation = graph.validate_event_integrity()
        print(f"   事件圖完整性: {validation['is_valid']}")

        # 5. PlotManager
        print("\n5. 測試 PlotManager...")
        from utils.plot_manager import PlotManager
        manager = PlotManager(total_chapters=30)
        chapter_type = manager.get_chapter_type(15)
        print(f"   第15章類型: {chapter_type}")

        # 6. VolumeManager
        print("\n6. 測試 VolumeManager...")
        from utils.volume_manager import VolumeManager
        volume_mgr = VolumeManager()
        plan = volume_mgr.plan_volumes("測試", "玄幻", "逆天改命", 60)
        print(f"   分卷數: {plan['total_volumes']}")

        # 7. PromptTemplates Phase 2
        print("\n7. 測試 PromptTemplates Phase 2...")
        from templates.prompts import PromptTemplates
        pt = PromptTemplates()

        # 檢查新增方法
        phase2_methods = [
            'build_volume_plan_prompt',
            'build_volume_outline_prompt',
            'build_chapter_outline_prompt_phase2',
            'build_chapter_prompt_phase2'
        ]

        for method in phase2_methods:
            if hasattr(pt, method):
                print(f"   ✓ {method}")
            else:
                print(f"   ✗ {method} 不存在")

        print("\n✓ 所有基本功能測試通過！")
        return True

    except Exception as e:
        print(f"\n✗ 功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_files():
    """測試配置文件"""
    print("\n" + "="*60)
    print("配置文件測試")
    print("="*60)

    import json
    import os

    config_files = [
        "config/arcs.json",
        "config/conflict_curve.json",
        "config/validator_rules.json"
    ]

    for config_file in config_files:
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ {config_file} ({len(data)} 項)")
            else:
                print(f"✗ {config_file} 不存在")
        except Exception as e:
            print(f"✗ {config_file} 讀取失敗: {e}")


def main():
    """主測試流程"""
    print("\n" + "="*60)
    print("AI 小說生成器 Phase 2.1 模組驗證")
    print("="*60)

    # 1. 測試導入
    import_results = test_imports()

    # 2. 測試配置文件
    test_config_files()

    # 3. 測試基本功能
    functionality_ok = test_basic_functionality()

    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)

    success_count = sum(1 for r in import_results if r[2] == "✓")
    total_count = len(import_results)

    print(f"\n模組導入: {success_count}/{total_count} 成功")
    print(f"功能測試: {'通過' if functionality_ok else '失敗'}")

    if success_count == total_count and functionality_ok:
        print("\n🎉 所有測試通過！Phase 2.1 核心模組已就緒。")
        return 0
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
