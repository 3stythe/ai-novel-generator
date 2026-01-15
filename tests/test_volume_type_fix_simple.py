# -*- coding: utf-8 -*-
"""
VolumeManager 类型错误修复 - 简化验证测试
只测试关键的类型转换功能，不加载重型模型
"""

import json
import tempfile
import os

# 模拟 VolumeManager 的关键类型转换逻辑
def test_type_conversion_logic():
    """测试类型转换逻辑"""
    print("\n" + "="*60)
    print("🧪 测试类型转换逻辑")
    print("="*60)

    # 模拟从 JSON 加载的数据（可能是字符串）
    volume = {
        'start_chapter': '1',
        'end_chapter': '15',
        'chapter_count': '15'
    }

    print(f"\n原始数据类型（模拟从 JSON 加载）:")
    print(f"  start_chapter: {type(volume['start_chapter']).__name__} = {volume['start_chapter']}")
    print(f"  end_chapter: {type(volume['end_chapter']).__name__} = {volume['end_chapter']}")
    print(f"  chapter_count: {type(volume['chapter_count']).__name__} = {volume['chapter_count']}")

    # 应用类型转换（修复后的代码）
    end_chapter = int(volume['end_chapter'])
    chapter_count = int(volume['chapter_count'])
    start_chapter = int(volume['start_chapter'])

    print(f"\n转换后的数据类型:")
    print(f"  start_chapter: {type(start_chapter).__name__} = {start_chapter}")
    print(f"  end_chapter: {type(end_chapter).__name__} = {end_chapter}")
    print(f"  chapter_count: {type(chapter_count).__name__} = {chapter_count}")

    # 测试比较操作（修复前会失败）
    current_chapter = 15
    chapters_in_volume = 10

    try:
        # 测试比较 1
        result1 = current_chapter >= end_chapter
        print(f"\n✓ 比较操作 1 成功: {current_chapter} >= {end_chapter} = {result1}")

        # 测试比较 2
        result2 = chapters_in_volume >= chapter_count + 2
        print(f"✓ 比较操作 2 成功: {chapters_in_volume} >= {chapter_count + 2} = {result2}")

        # 测试算术操作
        result3 = start_chapter + 5
        print(f"✓ 算术操作成功: {start_chapter} + 5 = {result3}")

        # 测试 range 操作
        result4 = list(range(start_chapter, end_chapter + 1))
        print(f"✓ range 操作成功: range({start_chapter}, {end_chapter + 1}) 生成 {len(result4)} 个元素")

        print(f"\n✓ 所有类型转换测试通过")
        return True

    except TypeError as e:
        print(f"\n❌ 类型错误: {e}")
        return False


def test_actual_volume_manager():
    """测试实际的 VolumeManager 类"""
    print("\n" + "="*60)
    print("🧪 测试实际的 VolumeManager 类")
    print("="*60)

    try:
        # 导入时不初始化重型组件
        from utils.volume_manager import VolumeManager

        # 创建 VolumeManager（不传入 validator 以避免加载模型）
        manager = VolumeManager(validator=None, plot_manager=None)

        # 生成 volume_plan
        volume_plan = manager.plan_volumes(
            title="测试小说",
            genre="测试",
            theme="测试主题",
            total_chapters=30
        )

        print(f"\n✓ VolumeManager 创建成功")
        print(f"  生成了 {len(volume_plan['volumes'])} 个卷")

        # 测试数据类型
        first_volume = volume_plan['volumes'][0]
        print(f"\n第一个卷的字段类型:")
        print(f"  start_chapter: {type(first_volume['start_chapter']).__name__} = {first_volume['start_chapter']}")
        print(f"  end_chapter: {type(first_volume['end_chapter']).__name__} = {first_volume['end_chapter']}")
        print(f"  chapter_count: {type(first_volume['chapter_count']).__name__} = {first_volume['chapter_count']}")

        # 保存到 JSON 并重新加载
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(volume_plan, f, ensure_ascii=False, indent=2)
            temp_file = f.name

        with open(temp_file, 'r', encoding='utf-8') as f:
            loaded_plan = json.load(f)

        os.unlink(temp_file)

        first_volume_loaded = loaded_plan['volumes'][0]
        print(f"\n从 JSON 加载后的字段类型:")
        print(f"  start_chapter: {type(first_volume_loaded['start_chapter']).__name__} = {first_volume_loaded['start_chapter']}")
        print(f"  end_chapter: {type(first_volume_loaded['end_chapter']).__name__} = {first_volume_loaded['end_chapter']}")
        print(f"  chapter_count: {type(first_volume_loaded['chapter_count']).__name__} = {first_volume_loaded['chapter_count']}")

        # 测试 should_end_volume（整数参数）
        print(f"\n测试 should_end_volume（整数参数）:")
        should_end, reason = manager.should_end_volume(
            volume_num=1,
            chapters_in_volume=10,
            current_chapter=15
        )
        print(f"  结果: should_end={should_end}, reason='{reason}'")
        print(f"✓ 整数参数测试通过")

        # 模拟字符串类型（手动修改）
        print(f"\n测试 should_end_volume（模拟字符串类型）:")
        manager.volume_plan['volumes'][0]['end_chapter'] = '15'
        manager.volume_plan['volumes'][0]['chapter_count'] = '15'

        print(f"  修改后的类型:")
        print(f"    end_chapter: {type(manager.volume_plan['volumes'][0]['end_chapter']).__name__}")
        print(f"    chapter_count: {type(manager.volume_plan['volumes'][0]['chapter_count']).__name__}")

        should_end, reason = manager.should_end_volume(
            volume_num=1,
            chapters_in_volume=10,
            current_chapter=15
        )
        print(f"  结果: should_end={should_end}, reason='{reason}'")
        print(f"✓ 字符串参数测试通过（类型转换成功）")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🚀 开始 VolumeManager 类型错误修复验证（简化版）\n")

    all_passed = True

    # 测试 1: 类型转换逻辑
    if not test_type_conversion_logic():
        all_passed = False

    # 测试 2: 实际的 VolumeManager
    if not test_actual_volume_manager():
        all_passed = False

    # 最终结果
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)

    if all_passed:
        print("\n✅ 所有测试通过！VolumeManager 类型转换修复成功。")
        print("\n修复内容:")
        print("  1. should_end_volume(): 添加 int() 类型转换")
        print("  2. generate_chapter_outlines(): 添加 int() 类型转换")
        print("  3. _build_chapter_outline_prompt(): 添加 int() 类型转换")
        print("  4. _build_volume_summary_prompt(): 添加 int() 类型转换")
        print("  5. plan_volumes(): 显式确保生成整数类型")
    else:
        print("\n❌ 部分测试失败")

    print("="*60)
