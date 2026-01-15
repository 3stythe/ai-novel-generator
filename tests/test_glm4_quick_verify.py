#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GLM-4 快速验证脚本 - 测试单个参数组合验证 GLM-4 特有指标
"""

# 路徑設置：將父目錄添加到 sys.path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
from tests.test_glm4_params import GLM4ParamsTester

# 加载环境变量
load_dotenv()
api_key = os.getenv('SILICONFLOW_API_KEY')

if not api_key:
    print("❌ 错误: 未检测到 SILICONFLOW_API_KEY")
    exit(1)

# 创建测试器（啟用 debug 模式顯示詳細評分過程）
tester = GLM4ParamsTester(api_key, quick_mode=False, enable_ai_review=False, debug_mode=True)

# 单个测试参数
test_params = {'temperature': 0.7, 'top_p': 0.9, 'repetition_penalty': 1.1, 'max_tokens': 6000}

print("\n🧪 GLM-4 单参数验证测试")
print("="*60)
print(f"参数: {test_params}\n")

# 生成大纲
outline = tester.generate_outline(test_params)

print(f"\n✅ 大纲生成完成（{len(outline)} 字）\n")

# 评估质量
score = tester.evaluate_quality(outline, test_params)

print("📊 评分详情:")
# evaluate_quality 返回的分數結構
if 'format_score' in score and 'content_score' in score:
    auto_score = score['format_score'] + score['content_score'] + score.get('length_score', 0)
    print(f"  基础自动评分: {auto_score:.0f}/100")
    print(f"    - 格式分: {score['format_score']:.0f}/40")
    print(f"    - 内容分: {score['content_score']:.0f}/40")
    print(f"    - 长度分: {score.get('length_score', 0):.0f}/20")
elif 'auto_score' in score:
    print(f"  基础自动评分: {score['auto_score']:.0f}/100")
else:
    print(f"  ⚠️  评分结构未知，可用键: {list(score.keys())}")

print(f"  GLM-4 特有评分: {score.get('glm4_score', 0):.0f}/20")
print(f"  总分: {score.get('total_score', 0):.0f}/120")

if 'glm4_checks' in score:
    checks = score['glm4_checks']
    print(f"\n🎯 GLM-4 特有指标:")
    print(f"  中文流暢度: {checks['chinese_fluency']*100:.1f}%")
    print(f"  文化底蘊: {checks['cultural_depth']*100:.1f}%")
    print(f"  創意性: {checks['creativity']*100:.1f}%")
    print(f"  邏輯連貫性: {checks['coherence']*100:.1f}%")
elif 'details' in score:
    print(f"\n🎯 GLM-4 特有指标（从 details 读取）:")
    details = score['details']
    if 'glm4_chinese_fluency' in details:
        print(f"  中文流暢度: {details['glm4_chinese_fluency']*100:.1f}%")
        print(f"  文化底蘊: {details['glm4_cultural_depth']*100:.1f}%")
        print(f"  創意性: {details['glm4_creativity']*100:.1f}%")
        print(f"  邏輯連貫性: {details['glm4_coherence']*100:.1f}%")
    else:
        print("  ⚠️  GLM-4 指标未找到于 details 中")
else:
    print("\n⚠️  GLM-4 特有指标未找到！")

print("\n✅ 验证完成！")
