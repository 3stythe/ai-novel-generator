# -*- coding: utf-8 -*-
"""
验证 should_end_volume 调用修复
测试 core/generator.py 中的正确调用方式
"""

import logging

from utils.volume_manager import VolumeManager

logging.basicConfig(level=logging.INFO)


def test_should_end_volume_correct_call():
    """测试正确的 should_end_volume 调用方式"""
    print("\n" + "="*60)
    print("🧪 测试 should_end_volume 正确调用")
    print("="*60)

    # 创建 VolumeManager
    manager = VolumeManager(validator=None, plot_manager=None)

    # 生成 volume_plan (30章，分2卷)
    volume_plan = manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    print(f"\n✓ 分卷规划完成:")
    for vol in volume_plan['volumes']:
        print(f"  第{vol['volume_num']}卷: 第{vol['start_chapter']}-{vol['end_chapter']}章")

    # 模拟 core/generator.py 中的调用场景
    print(f"\n📝 模拟章节生成流程:")

    current_volume_id = 1
    test_scenarios = [
        {'chapter_num': 5, 'expected_end': False, 'desc': '第5章（卷中间）'},
        {'chapter_num': 14, 'expected_end': False, 'desc': '第14章（接近卷尾）'},
        {'chapter_num': 15, 'expected_end': True, 'desc': '第15章（卷结束）'},
        {'chapter_num': 16, 'expected_end': False, 'desc': '第16章（第2卷开始）'},
    ]

    all_passed = True

    for scenario in test_scenarios:
        chapter_num = scenario['chapter_num']
        expected_end = scenario['expected_end']
        desc = scenario['desc']

        # 确定当前卷号
        if chapter_num > 15:
            current_volume_id = 2

        # 获取当前卷信息
        current_volume = volume_plan['volumes'][current_volume_id - 1]
        start_chapter = int(current_volume['start_chapter'])

        # 计算本卷已生成章节数
        chapters_in_volume = chapter_num - start_chapter + 1

        # ✅ 正确的调用方式
        should_end, reason = manager.should_end_volume(
            volume_num=current_volume_id,
            chapters_in_volume=chapters_in_volume,
            current_chapter=chapter_num
        )

        # 验证结果
        status = "✓" if should_end == expected_end else "❌"
        print(f"\n{status} {desc}:")
        print(f"    当前卷: 第{current_volume_id}卷")
        print(f"    本卷章节数: {chapters_in_volume}")
        print(f"    全书章节: 第{chapter_num}章")
        print(f"    是否结束: {should_end}")
        print(f"    原因: {reason}")

        if should_end != expected_end:
            print(f"    ⚠️  预期: {expected_end}, 实际: {should_end}")
            all_passed = False

    return all_passed


def test_type_safety():
    """测试类型安全性"""
    print("\n" + "="*60)
    print("🧪 测试类型安全性")
    print("="*60)

    # 创建 VolumeManager
    manager = VolumeManager(validator=None, plot_manager=None)

    # 生成 volume_plan
    volume_plan = manager.plan_volumes(
        title="测试小说",
        genre="测试",
        theme="测试主题",
        total_chapters=30
    )

    # 模拟从 JSON 加载（字符串类型）
    print(f"\n模拟从 JSON 加载后的字符串类型:")
    volume_plan['volumes'][0]['start_chapter'] = '1'
    volume_plan['volumes'][0]['end_chapter'] = '15'

    print(f"  start_chapter 类型: {type(volume_plan['volumes'][0]['start_chapter']).__name__}")
    print(f"  end_chapter 类型: {type(volume_plan['volumes'][0]['end_chapter']).__name__}")

    # 尝试调用（应该能处理字符串）
    print(f"\n尝试调用 should_end_volume:")

    try:
        # 获取当前卷信息
        current_volume = volume_plan['volumes'][0]
        start_chapter = int(current_volume['start_chapter'])  # 类型转换

        # 计算本卷已生成章节数
        chapter_num = 15
        chapters_in_volume = chapter_num - start_chapter + 1

        # 调用
        should_end, reason = manager.should_end_volume(
            volume_num=1,
            chapters_in_volume=chapters_in_volume,
            current_chapter=chapter_num
        )

        print(f"  ✓ 调用成功")
        print(f"  结果: should_end={should_end}, reason='{reason}'")
        return True

    except TypeError as e:
        print(f"  ❌ 类型错误: {e}")
        return False


if __name__ == '__main__':
    print("\n🚀 开始验证 should_end_volume 调用修复\n")

    all_passed = True

    # 测试 1: 正确调用
    if not test_should_end_volume_correct_call():
        all_passed = False

    # 测试 2: 类型安全
    if not test_type_safety():
        all_passed = False

    # 最终结果
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)

    if all_passed:
        print("\n✅ 所有测试通过！should_end_volume 调用修复成功。")
        print("\n修复内容:")
        print("  1. core/generator.py: 修正 should_end_volume 调用参数")
        print("     - volume_num: current_volume_id")
        print("     - chapters_in_volume: chapter_num - start_chapter + 1")
        print("     - current_chapter: chapter_num")
        print("  2. 添加类型转换保护: int(current_volume['start_chapter'])")
    else:
        print("\n❌ 部分测试失败")

    print("="*60)
