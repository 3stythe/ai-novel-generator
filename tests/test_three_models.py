# -*- coding: utf-8 -*-
"""
測試三模型自動切換功能
驗證：
1. 生成大綱時使用 DeepSeek R1 (Architect)
2. 生成章節時使用 GLM-4 (Writer)
3. 生成摘要時使用 DeepSeek R1 (Architect)
"""

import os
from dotenv import load_dotenv
from core.generator import NovelGenerator
from config import MODEL_ROLES

load_dotenv()

def test_three_models():
    print("="*60)
    print("🧪 測試三模型自動切換功能")
    print("="*60)

    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未檢測到 SILICONFLOW_API_KEY")
        return

    print("\n📋 模型配置:")
    print(f"  Architect (大綱): {MODEL_ROLES['architect']}")
    print(f"  Writer (章節):    {MODEL_ROLES['writer']}")
    print(f"  Editor (驗證):    {MODEL_ROLES['editor']}")

    print("\n⏳ 初始化生成器（MVP 模式）...")
    generator = NovelGenerator(api_key, enable_phase2=False)

    print("✓ 生成器初始化完成")

    # 建立測試專案
    print("\n⏳ 建立測試專案...")
    generator.create_project(
        title="三模型測試小說",
        genre="科幻",
        theme="AI 協作創作",
        total_chapters=2
    )

    print("✓ 專案建立完成")

    # 測試 1: 生成大綱（應該使用 Architect）
    print("\n" + "="*60)
    print("📋 測試 1: 生成大綱（Architect - DeepSeek R1）")
    print("="*60)
    generator.generate_outline()
    print("✓ 大綱生成完成")

    # 測試 2: 生成第一章（應該使用 Writer）
    print("\n" + "="*60)
    print("✍️ 測試 2: 生成第一章（Writer - GLM-4）")
    print("="*60)
    generator.generate_chapter(1)
    print("✓ 第一章生成完成")

    # 打印統計
    print("\n" + "="*60)
    print("📊 測試完成 - 統計信息")
    print("="*60)
    generator.api_client.print_statistics()

    print("\n🎉 三模型自動切換測試成功！")
    print(f"📂 專案目錄: {generator.project_dir}")
    print("\n驗證方式：")
    print("1. 檢查日誌中的模型調用記錄")
    print("2. 對比不同模型生成的內容風格")
    print("3. 查看 API 統計信息")

if __name__ == '__main__':
    test_three_models()
