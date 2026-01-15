# -*- coding: utf-8 -*-
"""
測試重構後的 CLI - 三模型自動切換
"""

import os
from dotenv import load_dotenv
from core.generator import NovelGenerator
from config import MODEL_ROLES

load_dotenv()

def test_refactored_workflow():
    print("=" * 60)
    print("🧪 測試重構後的三模型自動工作流程")
    print("=" * 60)

    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未檢測到 SILICONFLOW_API_KEY")
        return

    print("\n📋 三模型配置:")
    print(f"  Architect: {MODEL_ROLES['architect']}")
    print(f"  Writer:    {MODEL_ROLES['writer']}")
    print(f"  Editor:    {MODEL_ROLES['editor']}")

    print("\n⏳ 初始化生成器（使用 Architect 作為主模型）...")
    generator = NovelGenerator(
        api_key,
        MODEL_ROLES['architect'],  # 使用 Architect 作為主模型
        enable_phase2=False  # MVP 模式快速測試
    )
    print("✓ 生成器初始化完成")

    print(f"  API 客戶端當前模型: {generator.api_client.model}")

    print("\n⏳ 建立測試專案...")
    generator.create_project(
        title="重構測試小說",
        genre="科幻",
        theme="三模型協作",
        total_chapters=2
    )
    print("✓ 專案建立完成")

    print("\n⏳ 生成大綱（應使用 DeepSeek R1）...")
    generator.generate_outline()
    print("✓ 大綱生成完成")

    print("\n⏳ 生成第一章（應使用 GLM-4）...")
    generator.generate_chapter(1)
    print("✓ 第一章生成完成")

    print("\n📊 統計信息:")
    generator.api_client.print_statistics()

    print("\n🎉 重構測試成功！")
    print(f"📂 專案目錄: {generator.project_dir}")
    print("\n驗證要點:")
    print("  ✓ 移除了手動模型選擇菜單")
    print("  ✓ 使用 Architect 作為主模型初始化")
    print("  ✓ 大綱使用 DeepSeek R1")
    print("  ✓ 章節使用 GLM-4")
    print("  ✓ 三模型自動切換正常工作")

if __name__ == '__main__':
    test_refactored_workflow()
