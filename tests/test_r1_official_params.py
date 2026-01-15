# -*- coding: utf-8 -*-
"""
測試 DeepSeek R1 官方推薦參數配置
"""

import os
from dotenv import load_dotenv
from core.generator import NovelGenerator
from config import ROLE_CONFIGS, MODEL_ROLES

load_dotenv()

def test_r1_official_params():
    print("=" * 60)
    print("🧪 測試 DeepSeek R1 官方推薦參數")
    print("=" * 60)

    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未檢測到 SILICONFLOW_API_KEY")
        return

    # 顯示 R1 官方參數
    print("\n📋 DeepSeek R1 官方推薦參數:")
    print(f"  模型: {MODEL_ROLES['architect']}")
    for key, value in ROLE_CONFIGS['architect'].items():
        print(f"  {key:20s}: {value}")

    print("\n💡 參數設計理念:")
    print("  temperature=0.5      → R1 官方建議 0.5-0.7，保證格式穩定")
    print("  top_p=0.95           → 提高推理路徑選擇空間")
    print("  repetition_penalty=1.0 → 不懲罰重複，推理需重複確認邏輯")
    print("  max_tokens=8192      → 為 <think> 思考過程預留足夠空間")

    print("\n⏳ 初始化生成器...")
    generator = NovelGenerator(api_key, enable_phase2=False)

    print("\n⏳ 建立測試專案...")
    generator.create_project(
        title="R1 官方參數測試",
        genre="科幻",
        theme="時間悖論",
        total_chapters=5
    )

    print("\n⏳ 生成大綱（使用 R1 官方參數）...")
    try:
        generator.generate_outline()

        # 讀取生成的大綱
        outline_file = os.path.join(generator.project_dir, 'outline.txt')
        with open(outline_file, 'r', encoding='utf-8') as f:
            outline = f.read()

        print("\n" + "=" * 60)
        print("✅ 品質驗證")
        print("=" * 60)

        # 驗證項目
        checks = {
            '長度充足': len(outline) >= 500,
            '無 <think> 洩漏': '<think>' not in outline and '</think>' not in outline,
            '星號使用正常': outline.count('*') < 50,
            '省略號使用正常': outline.count('...') < 20,
            '無連續星號': '*********' not in outline,
            '無連續省略號': '........' not in outline,
            '繁體中文為主': outline.count('的') > outline.count('的'),  # 簡單檢測
        }

        all_passed = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'通過' if result else '失敗'}")
            if not result:
                all_passed = False

        print("\n" + "=" * 60)
        print("📄 大綱預覽（前 800 字）")
        print("=" * 60)
        print(outline[:800])
        if len(outline) > 800:
            print("...")

        print("\n" + "=" * 60)
        print("📊 統計信息")
        print("=" * 60)
        print(f"大綱總長度: {len(outline)} 字")
        print(f"星號數量: {outline.count('*')}")
        print(f"省略號數量: {outline.count('...')}")
        print(f"專案目錄: {generator.project_dir}")

        # API 統計
        print("\n" + "=" * 60)
        print("📡 API 調用統計")
        print("=" * 60)
        generator.api_client.print_statistics()

        if all_passed:
            print("\n🎉 R1 官方參數測試通過！")
            print("\n✅ 驗證結果:")
            print("  • <think> 標籤成功過濾")
            print("  • 內容品質符合預期")
            print("  • 參數配置生效")
        else:
            print("\n⚠️  部分檢查未通過，需要進一步調整")

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_r1_official_params()
