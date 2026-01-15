# -*- coding: utf-8 -*-
"""
VolumeManager 类型错误修复验证测试
测试 volume_plan 中的整数字段类型转换
"""

import json
import logging
import tempfile
import os

from utils.volume_manager import VolumeManager

logging.basicConfig(level=logging.INFO)


def test_volume_plan_types():
    """测试 1: 验证 plan_volumes() 生成的数据类型"""
    print("\n" + "="*60)
    print("🧪 测试 plan_volumes() 数据类型")
    print("="*60)

    manager = VolumeManager()

    volume_plan = manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    # 检查第一个卷的字段类型
    first_volume = volume_plan['volumes'][0]

    print(f"\n第一个卷的字段类型:")
    print(f"  start_chapter: {type(first_volume['start_chapter']).__name__} = {first_volume['start_chapter']}")
    print(f"  end_chapter: {type(first_volume['end_chapter']).__name__} = {first_volume['end_chapter']}")
    print(f"  chapter_count: {type(first_volume['chapter_count']).__name__} = {first_volume['chapter_count']}")

    # 验证类型
    assert isinstance(first_volume['start_chapter'], int), "start_chapter 应该是整数"
    assert isinstance(first_volume['end_chapter'], int), "end_chapter 应该是整数"
    assert isinstance(first_volume['chapter_count'], int), "chapter_count 应该是整数"

    print(f"\n✓ 所有字段都是整数类型")

    return volume_plan


def test_json_roundtrip():
    """测试 2: 验证 JSON 保存和加载后的类型"""
    print("\n" + "="*60)
    print("🧪 测试 JSON 往返后的数据类型")
    print("="*60)

    manager = VolumeManager()

    # 生成 volume_plan
    volume_plan = manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(volume_plan, f, ensure_ascii=False, indent=2)
        temp_file = f.name

    print(f"\n保存到临时文件: {temp_file}")

    # 从文件加载
    with open(temp_file, 'r', encoding='utf-8') as f:
        loaded_plan = json.load(f)

    # 检查加载后的类型
    first_volume = loaded_plan['volumes'][0]

    print(f"\n从 JSON 加载后的字段类型:")
    print(f"  start_chapter: {type(first_volume['start_chapter']).__name__} = {first_volume['start_chapter']}")
    print(f"  end_chapter: {type(first_volume['end_chapter']).__name__} = {first_volume['end_chapter']}")
    print(f"  chapter_count: {type(first_volume['chapter_count']).__name__} = {first_volume['chapter_count']}")

    # JSON 加载后应该保持整数类型
    is_start_int = isinstance(first_volume['start_chapter'], int)
    is_end_int = isinstance(first_volume['end_chapter'], int)
    is_count_int = isinstance(first_volume['chapter_count'], int)

    if is_start_int and is_end_int and is_count_int:
        print(f"\n✓ JSON 往返后仍然是整数类型")
    else:
        print(f"\n⚠️  警告：JSON 往返后类型可能改变")
        print(f"    这不是错误，JSON 标准支持整数")

    # 清理临时文件
    os.unlink(temp_file)

    return loaded_plan


def test_should_end_volume_with_int():
    """测试 3: 验证 should_end_volume() 使用整数参数"""
    print("\n" + "="*60)
    print("🧪 测试 should_end_volume() 整数参数")
    print("="*60)

    manager = VolumeManager()

    # 生成 volume_plan
    manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    # 测试整数参数
    should_end, reason = manager.should_end_volume(
        volume_num=1,
        chapters_in_volume=10,
        current_chapter=15  # 整数
    )

    print(f"\n测试参数:")
    print(f"  volume_num=1, chapters_in_volume=10, current_chapter=15")
    print(f"结果:")
    print(f"  should_end={should_end}, reason='{reason}'")
    print(f"\n✓ 整数参数测试通过")

    return should_end, reason


def test_should_end_volume_type_comparison():
    """测试 4: 模拟类型比较错误场景"""
    print("\n" + "="*60)
    print("🧪 测试类型比较（模拟潜在错误）")
    print("="*60)

    manager = VolumeManager()

    # 生成 volume_plan
    manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    # 手动修改 volume_plan 以模拟从 JSON 加载可能出现的字符串类型
    # 注意：实际上 JSON 标准的整数不会变成字符串，但我们模拟这种情况
    print(f"\n原始类型:")
    first_volume = manager.volume_plan['volumes'][0]
    print(f"  end_chapter: {type(first_volume['end_chapter']).__name__} = {first_volume['end_chapter']}")

    # 模拟错误情况：将整数改为字符串
    print(f"\n模拟错误情况：将 end_chapter 改为字符串")
    first_volume['end_chapter'] = str(first_volume['end_chapter'])
    first_volume['chapter_count'] = str(first_volume['chapter_count'])

    print(f"  end_chapter: {type(first_volume['end_chapter']).__name__} = {first_volume['end_chapter']}")
    print(f"  chapter_count: {type(first_volume['chapter_count']).__name__} = {first_volume['chapter_count']}")

    # 尝试调用 should_end_volume（这里会触发类型错误）
    print(f"\n尝试调用 should_end_volume()...")

    try:
        should_end, reason = manager.should_end_volume(
            volume_num=1,
            chapters_in_volume=10,
            current_chapter=15  # 整数
        )

        print(f"结果:")
        print(f"  should_end={should_end}, reason='{reason}'")
        print(f"\n✓ 方法能够处理字符串类型（已修复）")

    except TypeError as e:
        print(f"\n❌ 类型错误（需要修复）:")
        print(f"  {e}")
        return False

    return True


def test_generate_chapter_outlines():
    """测试 5: 验证 generate_chapter_outlines() 的类型处理"""
    print("\n" + "="*60)
    print("🧪 测试 generate_chapter_outlines() 类型处理")
    print("="*60)

    manager = VolumeManager()

    # 生成 volume_plan
    manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    # 模拟字符串类型
    first_volume = manager.volume_plan['volumes'][0]
    first_volume['start_chapter'] = str(first_volume['start_chapter'])
    first_volume['end_chapter'] = str(first_volume['end_chapter'])

    print(f"\n模拟 start_chapter 和 end_chapter 为字符串:")
    print(f"  start_chapter: {type(first_volume['start_chapter']).__name__} = {first_volume['start_chapter']}")
    print(f"  end_chapter: {type(first_volume['end_chapter']).__name__} = {first_volume['end_chapter']}")

    # 尝试生成章节大纲（使用默认生成器）
    print(f"\n尝试生成章节大纲...")

    try:
        outlines = manager.generate_chapter_outlines(
            volume_num=1,
            volume_outline="测试卷大纲",  # 添加必需的参数
            api_generator_func=None  # 使用默认生成器
        )

        print(f"结果:")
        print(f"  生成了 {len(outlines)} 个章节大纲")
        print(f"\n✓ 方法能够处理字符串类型（已修复）")

    except (TypeError, ValueError) as e:
        print(f"\n❌ 类型错误（需要修复）:")
        print(f"  {e}")
        return False

    return True


if __name__ == '__main__':
    print("\n🚀 开始 VolumeManager 类型错误修复验证\n")

    all_passed = True

    # 测试 1: 验证生成的数据类型
    try:
        test_volume_plan_types()
    except Exception as e:
        print(f"\n❌ 测试 1 失败: {e}")
        all_passed = False

    # 测试 2: 验证 JSON 往返
    try:
        test_json_roundtrip()
    except Exception as e:
        print(f"\n❌ 测试 2 失败: {e}")
        all_passed = False

    # 测试 3: 验证整数参数
    try:
        test_should_end_volume_with_int()
    except Exception as e:
        print(f"\n❌ 测试 3 失败: {e}")
        all_passed = False

    # 测试 4: 模拟类型比较错误
    try:
        result = test_should_end_volume_type_comparison()
        if not result:
            all_passed = False
    except Exception as e:
        print(f"\n❌ 测试 4 失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    # 测试 5: 测试 generate_chapter_outlines
    try:
        result = test_generate_chapter_outlines()
        if not result:
            all_passed = False
    except Exception as e:
        print(f"\n❌ 测试 5 失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    # 最终结果
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)

    if all_passed:
        print("\n✅ 所有测试通过！VolumeManager 类型处理正常。")
    else:
        print("\n⚠️  部分测试失败，需要修复类型转换问题。")

    print("="*60)
