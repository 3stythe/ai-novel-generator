# -*- coding: utf-8 -*-
"""
測試 Phase 2.1 初始化是否正常
"""

import os
from dotenv import load_dotenv
from core.generator import NovelGenerator

load_dotenv()

def test_phase2_initialization():
    print("=" * 60)
    print("🧪 測試 Phase 2.1 初始化")
    print("=" * 60)

    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未檢測到 SILICONFLOW_API_KEY")
        return

    print("\n⏳ 初始化生成器（Phase 2.1 啟用）...")
    try:
        generator = NovelGenerator(api_key, enable_phase2=True)
        print("✓ 生成器初始化完成")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return

    # 檢查所有 Phase 2.1 組件
    print("\n📋 檢查 Phase 2.1 組件:")
    components = {
        'outline_validator': generator.outline_validator,
        'character_arc_enforcer': generator.character_arc_enforcer,
        'event_graph': generator.event_graph,
        'conflict_escalator': generator.conflict_escalator,
        'volume_manager': generator.volume_manager,
        'plot_manager': generator.plot_manager,
    }

    all_ok = True
    for name, component in components.items():
        status = "✓" if component is not None else "❌"
        print(f"  {status} {name}: {type(component).__name__ if component else 'None'}")
        if component is None and name in ['outline_validator', 'character_arc_enforcer', 'event_graph', 'conflict_escalator']:
            all_ok = False

    print("\n⏳ 建立測試專案...")
    try:
        generator.create_project(
            title="Phase 2.1 測試小說",
            genre="科幻",
            theme="AI 協作",
            total_chapters=10
        )
        print("✓ 專案建立成功")
    except Exception as e:
        print(f"❌ 專案建立失敗: {e}")
        import traceback
        traceback.print_exc()
        return

    # 再次檢查所有組件（專案建立後）
    print("\n📋 檢查專案建立後的組件:")
    components_after = {
        'outline_validator': generator.outline_validator,
        'character_arc_enforcer': generator.character_arc_enforcer,
        'event_graph': generator.event_graph,
        'conflict_escalator': generator.conflict_escalator,
        'volume_manager': generator.volume_manager,
        'plot_manager': generator.plot_manager,
    }

    for name, component in components_after.items():
        status = "✓" if component is not None else "❌"
        print(f"  {status} {name}: {type(component).__name__ if component else 'None'}")
        if component is None:
            all_ok = False

    if all_ok:
        print("\n🎉 Phase 2.1 初始化測試通過！")
        print(f"📂 專案目錄: {generator.project_dir}")
    else:
        print("\n⚠️  部分組件初始化失敗")

if __name__ == '__main__':
    test_phase2_initialization()
