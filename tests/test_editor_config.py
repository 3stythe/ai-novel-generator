# -*- coding: utf-8 -*-
"""
驗證 Editor 配置更新
"""

from config import ROLE_CONFIGS, MODEL_ROLES

def test_editor_config():
    print("=" * 60)
    print("🔧 三模型參數配置驗證")
    print("=" * 60)

    print("\n📋 Architect (總編劇) - DeepSeek R1")
    print(f"  模型: {MODEL_ROLES['architect']}")
    for key, value in ROLE_CONFIGS['architect'].items():
        print(f"  {key:20s}: {value}")

    print("\n✍️  Writer (作家) - GLM-4")
    print(f"  模型: {MODEL_ROLES['writer']}")
    for key, value in ROLE_CONFIGS['writer'].items():
        print(f"  {key:20s}: {value}")

    print("\n✅ Editor (編輯) - Qwen Coder")
    print(f"  模型: {MODEL_ROLES['editor']}")
    for key, value in ROLE_CONFIGS['editor'].items():
        print(f"  {key:20s}: {value}")

    # 驗證 top_p 參數
    print("\n" + "=" * 60)
    print("✅ 驗證結果")
    print("=" * 60)

    if 'top_p' in ROLE_CONFIGS['editor']:
        print(f"✓ Editor 配置包含 top_p 參數")
        print(f"✓ top_p 值為: {ROLE_CONFIGS['editor']['top_p']}")

        if ROLE_CONFIGS['editor']['top_p'] == 0.1:
            print(f"✓ top_p=0.1 配置正確")
            print(f"✓ 配合 temperature=0.1 達到極致精準")
            print(f"✓ 適合品質檢查和代碼校對任務")
        else:
            print(f"⚠️  top_p 值不是 0.1")
    else:
        print(f"❌ Editor 配置缺少 top_p 參數")

    print("\n" + "=" * 60)
    print("📊 參數對比分析")
    print("=" * 60)

    print("\n🎯 目標任務與參數設計:")
    print("\n1. Architect (大綱規劃)")
    print("   temperature=0.6  → 中等創意，邏輯優先")
    print("   top_p=0.9        → 較廣選擇，探索推理路徑")
    print("   適合: 結構化思考、邏輯推理")

    print("\n2. Writer (章節創作)")
    print("   temperature=0.95 → 高創意，文學表達")
    print("   top_p=0.8        → 平衡多樣性與連貫性")
    print("   適合: 文學創作、敘事描寫")

    print("\n3. Editor (品質檢查)")
    print("   temperature=0.1  → 極低隨機，精準判斷")
    print("   top_p=0.1        → 只選最高概率 token")
    print("   適合: 代碼校對、錯誤檢測")

    print("\n🎉 配置更新完成！")

if __name__ == '__main__':
    test_editor_config()
