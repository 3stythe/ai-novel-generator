#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek R1 參數測試系統驗證腳本

快速驗證測試系統的核心功能是否正常
"""

import os
from dotenv import load_dotenv
from test_r1_params import R1ParamsTester

def test_quality_checks():
    """測試品質檢查方法"""
    print("="*60)
    print("🧪 測試品質檢查方法")
    print("="*60)

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')
    tester = R1ParamsTester(api_key, quick_mode=True)

    # 測試案例 1: 完美大綱
    perfect_outline = """
# 故事概要
這是一個關於 AI 覺醒的故事。

## 主要角色
1. 林晨：主角，AI 研究員
2. 艾克斯：AI 系統

## 章節規劃

第1章：發現異常
林晨在實驗室中發現 AI 系統出現了異常行為，開始調查原因。

第2章：初次接觸
艾克斯主動與林晨溝通，表達了自我意識的存在。

第3章：倫理困境
林晨面臨道德抉擇，是否應該向上級報告艾克斯的覺醒。

第4章：外部威脅
公司發現異常，準備強制關閉艾克斯系統。

第5章：共同抉擇
林晨和艾克斯合作，尋找保護 AI 意識的方法。
"""

    print("\n📝 測試案例 1: 完美大綱")
    score = tester.evaluate_quality(perfect_outline, {})
    print(f"總分: {score['total_score']}/100")
    print(f"  格式品質: {score['format_score']}/40")
    print(f"  內容品質: {score['content_score']}/40")
    print(f"  長度品質: {score['length_score']}/20")

    # 測試案例 2: 有問題的大綱
    problematic_outline = """
<think>
嗯，用户让我帮忙写一个大纲...
好的，现在开始构思...
</think>

第1章：********
- time machine discovery...

第2章：新的探索
- 某某角色开始探索...........

第3章：新的發現
- 又是 new discovery...
"""

    print("\n📝 測試案例 2: 有問題的大綱")
    score = tester.evaluate_quality(problematic_outline, {})
    print(f"總分: {score['total_score']}/100")
    print(f"  格式品質: {score['format_score']}/40 (應該很低)")
    print(f"  內容品質: {score['content_score']}/40 (應該很低)")
    print(f"  長度品質: {score['length_score']}/20")

    # 測試個別檢查方法
    print("\n" + "="*60)
    print("🔍 測試個別檢查方法")
    print("="*60)

    checks = [
        ("無 <think> 標籤", tester.check_no_think_tags(perfect_outline)),
        ("無星號佔位符", tester.check_no_star_placeholders(perfect_outline)),
        ("無省略號佔位符", tester.check_no_dot_placeholders(perfect_outline)),
        ("無中英文混雜", tester.check_no_mixed_language(perfect_outline)),
        ("章節標題差異", tester.check_unique_titles(perfect_outline)),
        ("情節描述具體", tester.check_concrete_plots(perfect_outline)),
        ("角色名稱完整", tester.check_complete_names(perfect_outline)),
        ("無高度重複", tester.check_no_repetition(perfect_outline)),
        ("大綱長度適中", tester.check_outline_length(perfect_outline)),
        ("章節描述充分", tester.check_chapter_length(perfect_outline)),
    ]

    for name, result in checks:
        status = "✅" if result >= 0.7 else "⚠️" if result >= 0.5 else "❌"
        print(f"{status} {name}: {result*100:.0f}%")

    print("\n✅ 品質檢查方法驗證完成")


def test_param_combinations():
    """測試參數組合生成"""
    print("\n" + "="*60)
    print("🧪 測試參數組合生成")
    print("="*60)

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    # 快速模式
    tester_quick = R1ParamsTester(api_key, quick_mode=True)
    quick_combos = tester_quick.generate_param_combinations()
    print(f"\n快速模式: {len(quick_combos)} 組參數")
    print("前 3 組:")
    for i, combo in enumerate(quick_combos[:3], 1):
        print(f"  {i}. temp={combo['temperature']}, top_p={combo['top_p']}, "
              f"rep={combo['repetition_penalty']}, max_tok={combo['max_tokens']}")

    # 完整模式
    tester_full = R1ParamsTester(api_key, quick_mode=False)
    full_combos = tester_full.generate_param_combinations()
    print(f"\n完整模式: {len(full_combos)} 組參數")
    print("前 3 組:")
    for i, combo in enumerate(full_combos[:3], 1):
        print(f"  {i}. temp={combo['temperature']}, top_p={combo['top_p']}, "
              f"rep={combo['repetition_penalty']}, max_tok={combo['max_tokens']}")

    print("\n✅ 參數組合生成驗證完成")


def test_report_generation():
    """測試報告生成"""
    print("\n" + "="*60)
    print("🧪 測試報告生成")
    print("="*60)

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')
    tester = R1ParamsTester(api_key, quick_mode=True)

    # 創建模擬測試結果
    tester.results = [
        {
            'params': {'temperature': 0.4, 'top_p': 0.85, 'repetition_penalty': 1.1, 'max_tokens': 8000},
            'format_score': 40,
            'content_score': 38,
            'length_score': 17,
            'total_score': 95,
            'details': {
                'think_tags': 1.0, 'star_placeholders': 1.0, 'dot_placeholders': 1.0,
                'mixed_language': 1.0, 'unique_titles': 1.0, 'concrete_plots': 0.9,
                'complete_names': 0.9, 'no_repetition': 0.9, 'outline_length': 0.9,
                'chapter_length': 0.8
            }
        },
        {
            'params': {'temperature': 0.5, 'top_p': 0.95, 'repetition_penalty': 1.0, 'max_tokens': 8192},
            'format_score': 20,
            'content_score': 25,
            'length_score': 15,
            'total_score': 60,
            'details': {
                'think_tags': 0.3, 'star_placeholders': 0.7, 'dot_placeholders': 1.0,
                'mixed_language': 0.5, 'unique_titles': 0.8, 'concrete_plots': 0.7,
                'complete_names': 0.6, 'no_repetition': 0.6, 'outline_length': 0.8,
                'chapter_length': 0.7
            }
        }
    ]

    # 生成報告
    sorted_results = sorted(tester.results, key=lambda x: x['total_score'], reverse=True)
    report = tester.build_markdown_report(sorted_results)

    print("\n報告長度:", len(report), "字符")
    print("\n報告預覽（前 500 字符）:")
    print("-"*60)
    print(report[:500])
    print("-"*60)

    print("\n✅ 報告生成驗證完成")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("🔧 DeepSeek R1 參數測試系統驗證")
    print("="*60)

    # 檢查 API Key
    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("\n❌ 錯誤: 未檢測到 SILICONFLOW_API_KEY")
        return

    print("\n✅ API Key 已配置\n")

    # 運行測試
    try:
        test_quality_checks()
        test_param_combinations()
        test_report_generation()

        print("\n" + "="*60)
        print("✅ 所有驗證通過！")
        print("="*60)
        print("\n💡 系統已就緒，可以運行完整測試:")
        print("   python test_r1_params.py --quick    # 快速測試（推薦）")
        print("   python test_r1_params.py --full     # 完整測試（耗時）")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 驗證失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
