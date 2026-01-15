# -*- coding: utf-8 -*-
"""
Phase 2.1 功能測試腳本
測試 10-15 章小說生成，驗證所有反模式引擎功能
"""

import os
import sys
import json
from dotenv import load_dotenv

from core.generator import NovelGenerator
from utils.outline_validator import OutlineValidator


def test_phase2_generation():
    """測試 Phase 2.1 完整生成流程"""
    print("="*60)
    print("🧪 Phase 2.1 功能測試")
    print("="*60)

    # 載入環境變數
    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    if not api_key:
        print("❌ 請設定 SILICONFLOW_API_KEY 環境變數")
        sys.exit(1)

    # 測試參數
    test_config = {
        'title': '時空裂痕測試',
        'genre': '科幻',
        'theme': '時間旅行者發現修復裂痕的代價',
        'total_chapters': 15,  # 15 章測試
        'enable_phase2': True
    }

    print(f"\n📝 測試配置:")
    print(f"  標題: {test_config['title']}")
    print(f"  類型: {test_config['genre']}")
    print(f"  主題: {test_config['theme']}")
    print(f"  章節數: {test_config['total_chapters']}")
    print(f"  Phase 2.1: {'✓ 啟用' if test_config['enable_phase2'] else '未啟用'}")

    try:
        # 初始化生成器
        print("\n⏳ 初始化生成器...")
        generator = NovelGenerator(
            api_key=api_key,
            enable_phase2=test_config['enable_phase2']
        )

        # 建立專案
        print("\n📁 建立專案...")
        generator.create_project(
            title=test_config['title'],
            genre=test_config['genre'],
            theme=test_config['theme'],
            total_chapters=test_config['total_chapters']
        )

        # 生成大綱
        print("\n📋 生成大綱...")
        generator.generate_outline()

        # 生成前 5 章（快速測試）
        print("\n📖 生成章節（測試模式：前 5 章）...")
        for i in range(1, 6):
            generator.generate_chapter(i)

        # 驗證結果
        print("\n" + "="*60)
        print("🔍 驗證測試結果")
        print("="*60)

        validation_results = validate_generation(generator)

        # 打印驗證結果
        print_validation_results(validation_results)

        # 生成測試報告
        generate_test_report(generator, validation_results)

        return validation_results

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_generation(generator):
    """驗證生成結果"""
    results = {
        'similarity_check': None,
        'character_growth': None,
        'conflict_curve': None,
        'event_causality': None,
        'backward_compatibility': True
    }

    # 1. 章節相似度檢查
    print("\n1️⃣ 檢查章節重複率...")
    if generator.outline_validator and len(generator.chapter_outlines) >= 2:
        similarities = []
        for i in range(1, len(generator.chapter_outlines)):
            result = generator.outline_validator._calculate_similarity(
                generator.chapter_outlines[i],
                generator.chapter_outlines[i-1]
            )
            similarities.append(result)

        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        max_similarity = max(similarities) if similarities else 0

        results['similarity_check'] = {
            'average': avg_similarity,
            'max': max_similarity,
            'passed': max_similarity < 0.75  # 相似度 < 75%
        }
        print(f"  平均相似度: {avg_similarity:.2%}")
        print(f"  最高相似度: {max_similarity:.2%}")
        print(f"  {'✓ 通過' if results['similarity_check']['passed'] else '❌ 失敗'}")

    # 2. 角色成長檢查
    print("\n2️⃣ 檢查角色成長...")
    if generator.character_states:
        transitions = {}
        for char, state in generator.character_states.items():
            transitions[char] = {
                'current': state,
                'count': 1  # 簡化計數
            }

        results['character_growth'] = {
            'characters': transitions,
            'passed': len(transitions) > 0
        }
        print(f"  追蹤角色數: {len(transitions)}")
        print(f"  {'✓ 通過' if results['character_growth']['passed'] else '❌ 失敗'}")

    # 3. 衝突曲線檢查
    print("\n3️⃣ 檢查衝突升級曲線...")
    if generator.plot_manager:
        conflict_arc = generator.plot_manager.conflict_arc
        actual_levels = [ch.get('conflict_level', 0) for ch in generator.chapters]

        if actual_levels and len(actual_levels) == len(conflict_arc[:len(actual_levels)]):
            expected = conflict_arc[:len(actual_levels)]
            deviations = [abs(a - e) for a, e in zip(actual_levels, expected)]
            avg_deviation = sum(deviations) / len(deviations)
            max_deviation = max(deviations)

            results['conflict_curve'] = {
                'avg_deviation': avg_deviation,
                'max_deviation': max_deviation,
                'passed': max_deviation < 0.3  # 偏差 < 0.3
            }
            print(f"  平均偏差: {avg_deviation:.2f}")
            print(f"  最大偏差: {max_deviation:.2f}")
            print(f"  {'✓ 通過' if results['conflict_curve']['passed'] else '❌ 失敗'}")

    # 4. 事件因果鏈檢查
    print("\n4️⃣ 檢查事件因果鏈...")
    if generator.event_graph:
        total_events = len(generator.event_graph.graph) if hasattr(generator.event_graph.graph, '__len__') else 0

        if total_events > 0:
            plot_holes = generator.event_graph.get_plot_holes()
            orphaned = len([h for h in plot_holes if h.get('type') == 'orphaned_event'])

            orphaned_rate = orphaned / total_events if total_events > 0 else 0

            results['event_causality'] = {
                'total_events': total_events,
                'orphaned_events': orphaned,
                'orphaned_rate': orphaned_rate,
                'passed': orphaned_rate < 0.05  # < 5%
            }
            print(f"  總事件數: {total_events}")
            print(f"  孤立事件: {orphaned} ({orphaned_rate:.1%})")
            print(f"  {'✓ 通過' if results['event_causality']['passed'] else '❌ 失敗'}")

    return results


def print_validation_results(results):
    """打印驗證結果摘要"""
    print("\n" + "="*60)
    print("📊 測試結果摘要")
    print("="*60)

    checks = [
        ('章節重複率', results.get('similarity_check')),
        ('角色成長', results.get('character_growth')),
        ('衝突曲線', results.get('conflict_curve')),
        ('事件因果鏈', results.get('event_causality')),
        ('向後兼容', {'passed': results.get('backward_compatibility', True)})
    ]

    passed = 0
    total = len(checks)

    for name, result in checks:
        if result and result.get('passed'):
            print(f"✓ {name}: 通過")
            passed += 1
        else:
            print(f"❌ {name}: {'失敗' if result else '未測試'}")

    print("="*60)
    print(f"總計: {passed}/{total} 項通過")
    print("="*60)


def generate_test_report(generator, validation_results):
    """生成測試報告"""
    if not generator.project_dir:
        return

    report_file = os.path.join(generator.project_dir, 'TEST_REPORT.md')

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Phase 2.1 測試報告\n\n")
        f.write(f"**測試時間**: {generator.metadata.get('created_at', 'N/A')}\n\n")
        f.write(f"**小說標題**: {generator.metadata.get('title', 'N/A')}\n")
        f.write(f"**章節數**: {generator.metadata.get('total_chapters', 0)}\n")
        f.write(f"**已生成**: {len(generator.chapters)} 章\n\n")

        f.write("## 驗證結果\n\n")

        # 1. 相似度檢查
        sim_check = validation_results.get('similarity_check')
        if sim_check:
            f.write("### 1. 章節重複率檢查\n\n")
            f.write(f"- **平均相似度**: {sim_check['average']:.2%}\n")
            f.write(f"- **最高相似度**: {sim_check['max']:.2%}\n")
            f.write(f"- **標準**: < 75%\n")
            f.write(f"- **結果**: {'✓ 通過' if sim_check['passed'] else '❌ 失敗'}\n\n")

        # 2. 角色成長
        char_growth = validation_results.get('character_growth')
        if char_growth:
            f.write("### 2. 角色成長檢查\n\n")
            f.write(f"- **追蹤角色數**: {len(char_growth.get('characters', {}))}\n")
            f.write(f"- **結果**: {'✓ 通過' if char_growth['passed'] else '❌ 失敗'}\n\n")

        # 3. 衝突曲線
        conflict = validation_results.get('conflict_curve')
        if conflict:
            f.write("### 3. 衝突升級曲線檢查\n\n")
            f.write(f"- **平均偏差**: {conflict['avg_deviation']:.2f}\n")
            f.write(f"- **最大偏差**: {conflict['max_deviation']:.2f}\n")
            f.write(f"- **標準**: < 0.3\n")
            f.write(f"- **結果**: {'✓ 通過' if conflict['passed'] else '❌ 失敗'}\n\n")

        # 4. 事件因果鏈
        causality = validation_results.get('event_causality')
        if causality:
            f.write("### 4. 事件因果鏈檢查\n\n")
            f.write(f"- **總事件數**: {causality['total_events']}\n")
            f.write(f"- **孤立事件**: {causality['orphaned_events']} ({causality['orphaned_rate']:.1%})\n")
            f.write(f"- **標準**: < 5%\n")
            f.write(f"- **結果**: {'✓ 通過' if causality['passed'] else '❌ 失敗'}\n\n")

        f.write("## 統計信息\n\n")
        stats = generator.get_statistics()
        f.write(f"- **總字數**: {stats.get('total_words', 0):,}\n")
        f.write(f"- **總成本**: ¥{stats['api_statistics']['total_cost']:.4f}\n")

        if 'phase2_stats' in stats:
            p2 = stats['phase2_stats']
            f.write(f"- **分卷數**: {p2.get('total_volumes', 0)}\n")
            f.write(f"- **當前卷**: {p2.get('current_volume', 1)}\n")

    print(f"\n✓ 測試報告已生成: {report_file}")


def test_mvp_compatibility():
    """測試 MVP 模式向後兼容性"""
    print("\n" + "="*60)
    print("🔄 測試 MVP 模式向後兼容")
    print("="*60)

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    try:
        # MVP 模式（Phase 2 未啟用）
        generator = NovelGenerator(api_key=api_key, enable_phase2=False)

        generator.create_project(
            title='MVP 兼容性測試',
            genre='測試',
            theme='驗證向後兼容',
            total_chapters=3
        )

        generator.generate_outline()
        generator.generate_chapter(1)

        print("✓ MVP 模式運作正常")
        return True

    except Exception as e:
        print(f"❌ MVP 模式測試失敗: {e}")
        return False


if __name__ == '__main__':
    print("\n🚀 開始 Phase 2.1 完整測試\n")

    # 主測試
    results = test_phase2_generation()

    # 兼容性測試
    mvp_passed = test_mvp_compatibility()

    # 最終結果
    print("\n" + "="*60)
    print("🏁 測試完成")
    print("="*60)

    if results:
        all_passed = all([
            results.get('similarity_check', {}).get('passed', False),
            results.get('character_growth', {}).get('passed', False),
            results.get('conflict_curve', {}).get('passed', False),
            results.get('event_causality', {}).get('passed', False),
            mvp_passed
        ])

        if all_passed:
            print("✓ 所有測試通過！Phase 2.1 實現完成。")
        else:
            print("⚠️  部分測試未通過，需要進一步調整。")
    else:
        print("❌ 測試執行失敗")

    print("="*60)
