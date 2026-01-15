# -*- coding: utf-8 -*-
"""
測試啟動時間 - 驗證延遲載入優化效果
"""

import time
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()


def test_mvp_startup():
    """測試 MVP 模式啟動時間（應該 <5 秒）"""
    print("=" * 60)
    print("🚀 測試 MVP 模式啟動時間")
    print("=" * 60)
    print("預期：< 5 秒（理想 2-3 秒）")
    print()

    start_time = time.time()

    # 只導入 NovelGenerator，不啟用 Phase 2.1
    from core.generator import NovelGenerator

    api_key = os.getenv("SILICONFLOW_API_KEY")
    generator = NovelGenerator(api_key, enable_phase2=False)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n✓ MVP 模式啟動完成")
    print(f"⏱️  耗時: {elapsed:.2f} 秒")

    if elapsed < 5:
        print(f"✅ 成功！啟動時間 < 5 秒")
    elif elapsed < 10:
        print(f"⚠️  還可以，但可以更快")
    else:
        print(f"❌ 失敗！啟動時間 > 10 秒")

    return elapsed


def test_phase21_startup():
    """測試 Phase 2.1 模式啟動時間（允許較慢，10-60 秒）"""
    print("\n" + "=" * 60)
    print("🚀 測試 Phase 2.1 模式啟動時間")
    print("=" * 60)
    print("預期：10-60 秒（首次載入 TensorFlow 較慢）")
    print()

    start_time = time.time()

    # 導入 NovelGenerator，啟用 Phase 2.1
    from core.generator import NovelGenerator

    api_key = os.getenv("SILICONFLOW_API_KEY")
    generator = NovelGenerator(api_key, enable_phase2=True)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n✓ Phase 2.1 模式啟動完成")
    print(f"⏱️  耗時: {elapsed:.2f} 秒")

    if elapsed < 60:
        print(f"✅ 成功！啟動時間 < 60 秒")
    else:
        print(f"⚠️  較慢，但在可接受範圍")

    return elapsed


def test_import_only():
    """測試單純導入時間（不實例化）"""
    print("\n" + "=" * 60)
    print("🚀 測試模組導入時間")
    print("=" * 60)
    print("預期：< 2 秒（只導入，不實例化）")
    print()

    start_time = time.time()

    # 只導入模組
    from core.generator import NovelGenerator

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\n✓ 模組導入完成")
    print(f"⏱️  耗時: {elapsed:.2f} 秒")

    if elapsed < 2:
        print(f"✅ 優秀！延遲載入生效")
    elif elapsed < 5:
        print(f"⚠️  還行，但可能有改進空間")
    else:
        print(f"❌ 失敗！模組導入本身就很慢")

    return elapsed


if __name__ == '__main__':
    print("\n🧪 啟動時間測試套件")
    print("測試延遲載入優化效果\n")

    # 測試 1: 單純導入
    print("\n📝 測試 1/3: 模組導入時間")
    import_time = test_import_only()

    # 測試 2: MVP 模式
    print("\n📝 測試 2/3: MVP 模式啟動時間")
    mvp_time = test_mvp_startup()

    # 測試 3: Phase 2.1 模式
    print("\n📝 測試 3/3: Phase 2.1 模式啟動時間")
    phase21_time = test_phase21_startup()

    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    print(f"模組導入時間:      {import_time:.2f} 秒")
    print(f"MVP 模式啟動:      {mvp_time:.2f} 秒")
    print(f"Phase 2.1 啟動:    {phase21_time:.2f} 秒")
    print(f"延遲載入節省:      {phase21_time - mvp_time:.2f} 秒")

    # 評分
    print("\n🎯 性能評分:")
    score = 0

    if import_time < 2:
        print("  ✅ 模組導入: 優秀")
        score += 33
    elif import_time < 5:
        print("  ⚠️  模組導入: 及格")
        score += 20
    else:
        print("  ❌ 模組導入: 需改進")

    if mvp_time < 5:
        print("  ✅ MVP 啟動: 優秀")
        score += 34
    elif mvp_time < 10:
        print("  ⚠️  MVP 啟動: 及格")
        score += 20
    else:
        print("  ❌ MVP 啟動: 需改進")

    if phase21_time < 60:
        print("  ✅ Phase 2.1 啟動: 優秀")
        score += 33
    else:
        print("  ⚠️  Phase 2.1 啟動: 可接受")
        score += 20

    print(f"\n總分: {score}/100")
    if score >= 90:
        print("🏆 優秀！延遲載入優化非常成功")
    elif score >= 70:
        print("✅ 及格，達到優化目標")
    else:
        print("⚠️  仍有改進空間")

    print("\n" + "=" * 60)
