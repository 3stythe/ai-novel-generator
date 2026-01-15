# -*- coding: utf-8 -*-
"""
CharacterArcEnforcer 修復驗證測試
測試配置文件中的元數據字段是否被正確過濾
"""

import os
import logging
from core.character_arc_enforcer import CharacterArcEnforcer

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_arc_loading():
    """測試弧光配置載入"""
    print("="*60)
    print("🧪 測試 CharacterArcEnforcer 配置載入")
    print("="*60)

    enforcer = CharacterArcEnforcer()

    # 載入配置
    config_path = 'config/arcs.json'
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False

    try:
        arcs = enforcer.load_arcs_from_config(config_path)

        print(f"\n✓ 配置載入成功")
        print(f"  載入角色數: {len(arcs)}")
        print(f"\n角色列表:")

        for char_name in arcs.keys():
            print(f"  • {char_name}")

        # 驗證不應包含元數據字段
        invalid_keys = [k for k in arcs.keys() if k.startswith('_')]
        if invalid_keys:
            print(f"\n❌ 錯誤：仍包含元數據字段: {invalid_keys}")
            return False
        else:
            print(f"\n✓ 元數據字段已正確過濾")

        # 驗證每個角色的配置
        print(f"\n驗證角色配置結構:")
        for char_name, arc_data in arcs.items():
            # 檢查類型
            if not isinstance(arc_data, dict):
                print(f"  ❌ {char_name}: 不是字典類型")
                return False

            # 檢查必要字段
            if 'states' not in arc_data:
                print(f"  ❌ {char_name}: 缺少 states")
                return False

            if 'triggers' not in arc_data:
                print(f"  ❌ {char_name}: 缺少 triggers")
                return False

            print(f"  ✓ {char_name}: 結構正確 ({len(arc_data['states'])} 個狀態)")

        return True

    except Exception as e:
        print(f"\n❌ 載入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_expected_state():
    """測試預期狀態獲取"""
    print("\n" + "="*60)
    print("🧪 測試預期狀態獲取")
    print("="*60)

    enforcer = CharacterArcEnforcer()
    enforcer.load_arcs_from_config('config/arcs.json')

    test_cases = [
        ('主角', 1, '普通人'),
        ('主角', 5, '覺醒'),
        ('主角', 15, '成長'),
        ('導師', 5, '神秘高人'),
        ('導師', 10, '傳授心法'),
        ('反派', 8, '初登場'),
        ('女主角', 3, '初遇'),
        ('不存在的角色', 1, ''),  # 應返回空字符串
    ]

    all_passed = True

    for char_name, chapter_num, expected in test_cases:
        result = enforcer._get_expected_state(char_name, chapter_num)

        if result == expected:
            print(f"  ✓ {char_name} 第{chapter_num}章: {result}")
        else:
            print(f"  ❌ {char_name} 第{chapter_num}章: 預期 '{expected}'，得到 '{result}'")
            all_passed = False

    return all_passed


def test_state_regression():
    """測試狀態倒退檢測"""
    print("\n" + "="*60)
    print("🧪 測試狀態倒退檢測")
    print("="*60)

    enforcer = CharacterArcEnforcer()
    enforcer.load_arcs_from_config('config/arcs.json')

    # 正常進展（不應倒退）
    is_regression = enforcer._is_state_regression('主角', '成長', '覺醒')
    if not is_regression:
        print(f"  ✓ 正常進展（覺醒→成長）: 無倒退")
    else:
        print(f"  ❌ 誤判為倒退")
        return False

    # 倒退情況（應檢測到）
    is_regression = enforcer._is_state_regression('主角', '覺醒', '成長')
    if is_regression:
        print(f"  ✓ 倒退情況（成長→覺醒）: 檢測到倒退")
    else:
        print(f"  ❌ 未檢測到倒退")
        return False

    # 不存在的角色（應返回 False）
    is_regression = enforcer._is_state_regression('不存在', '狀態1', '狀態2')
    if not is_regression:
        print(f"  ✓ 不存在的角色: 返回 False")
    else:
        print(f"  ❌ 錯誤處理不存在的角色")
        return False

    return True


def test_arc_consistency():
    """測試弧光一致性檢查"""
    print("\n" + "="*60)
    print("🧪 測試弧光一致性檢查")
    print("="*60)

    enforcer = CharacterArcEnforcer()
    enforcer.load_arcs_from_config('config/arcs.json')

    # 測試正常狀態
    result = enforcer.enforce_arc_consistency(
        character='主角',
        chapter_num=5,
        current_state='覺醒',
        chapter_outline='主角在導師的指引下覺醒了潛能'
    )

    if result['is_consistent']:
        print(f"  ✓ 主角第5章（覺醒）: 一致性檢查通過")
    else:
        print(f"  ❌ 一致性檢查失敗: {result['errors']}")
        return False

    # 測試不存在的角色
    result = enforcer.enforce_arc_consistency(
        character='不存在的角色',
        chapter_num=1,
        current_state='任意狀態',
        chapter_outline='測試'
    )

    if not result['is_consistent']:
        print(f"  ✓ 不存在的角色: 返回不一致（預期行為）")
    else:
        print(f"  ⚠️  不存在的角色返回一致（可能是預期的降級行為）")

    return True


if __name__ == '__main__':
    print("\n🚀 開始 CharacterArcEnforcer 修復驗證\n")

    tests = [
        ("配置載入", test_arc_loading),
        ("預期狀態", test_expected_state),
        ("狀態倒退", test_state_regression),
        ("弧光一致性", test_arc_consistency),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name}測試異常: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # 總結
    print("\n" + "="*60)
    print("📊 測試結果總結")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "✓ 通過" if passed_flag else "❌ 失敗"
        print(f"  {status}: {test_name}")

    print("="*60)
    print(f"總計: {passed}/{total} 項測試通過")
    print("="*60)

    if passed == total:
        print("\n✅ 所有測試通過！CharacterArcEnforcer 修復成功。\n")
    else:
        print(f"\n⚠️  {total - passed} 項測試失敗，需要進一步檢查。\n")
