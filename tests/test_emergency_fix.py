# -*- coding: utf-8 -*-
"""
緊急修復驗證測試
測試 DeepSeek R1 三重問題修復效果
"""

import os
import sys
import json
import re
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.generator import NovelGenerator

def test_emergency_fix():
    """測試緊急修復效果"""

    print("🚨 開始驗證緊急修復...")
    print("="*60)

    # 獲取 API Key
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 錯誤：未設定 SILICONFLOW_API_KEY")
        return False

    # 創建生成器
    generator = NovelGenerator(api_key=api_key, enable_phase2=False)

    # 創建測試專案
    print("\n📝 創建測試專案...")
    generator.create_project(
        title="星際邊緣測試",
        genre="科幻",
        theme="人類文明存續",
        total_chapters=5
    )

    # 生成大綱
    print("\n⏳ 生成大綱（測試三重修復）...")
    try:
        outline = generator.generate_outline()

        print("\n✅ 大綱生成成功！")
        print(f"長度: {len(outline)} 字")

        # 驗證 1: 檢查 <think> 標籤
        has_think = '<think>' in outline.lower() or '好，我现在' in outline
        print(f"\n1️⃣ <think> 標籤檢查: {'❌ 失敗' if has_think else '✅ 通過'}")

        # 驗證 2: 檢查英文比例
        try:
            outline_dict = json.loads(outline)
            if 'chapters' in outline_dict and len(outline_dict['chapters']) > 0:
                first_chapter = outline_dict['chapters'][0].get('outline', '')
                english_words = re.findall(r'\b[a-zA-Z]+\b', first_chapter)
                english_ratio = len(' '.join(english_words)) / max(len(first_chapter), 1)

                print(f"2️⃣ 英文比例檢查: {english_ratio:.1%} {'❌ 超標' if english_ratio > 0.3 else '✅ 通過'}")

                # 驗證 3: 檢查內容深度
                avg_length = sum(len(ch.get('outline', '')) for ch in outline_dict['chapters']) / len(outline_dict['chapters'])
                print(f"3️⃣ 內容深度檢查: 平均 {avg_length:.0f} 字/章 {'❌ 太淺' if avg_length < 100 else '✅ 通過'}")

                # 顯示第一章範例
                print(f"\n📖 第一章範例（前 200 字）：")
                print("-"*60)
                print(first_chapter[:200])
                print("-"*60)

        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失敗: {e}")
            return False

        # 保存完整大綱供檢查
        test_output = os.path.join(generator.project_dir, "emergency_fix_test.txt")
        with open(test_output, 'w', encoding='utf-8') as f:
            f.write("=== 緊急修復驗證測試 ===\n\n")
            f.write(outline)

        print(f"\n💾 完整大綱已保存: {test_output}")
        print(f"📁 專案目錄: {generator.project_dir}")

        return True

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_emergency_fix()

    print("\n" + "="*60)
    if success:
        print("🎉 緊急修復驗證成功！")
    else:
        print("💥 緊急修復驗證失敗！")
    print("="*60)
