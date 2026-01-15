# Phase 2 快速參考指南

## 🎯 核心模組速查

### 1️⃣ OutlineValidator - 大綱驗證器
```python
from utils.outline_validator import OutlineValidator

validator = OutlineValidator(similarity_threshold=0.75)

# 驗證章節大綱
result = validator.validate_chapter_outline(
    outline="本章大綱內容",
    previous_outlines=["前面章節大綱1", "前面章節大綱2"],
    chapter_num=5,
    strict_mode=False
)

# 結果包含
result['is_valid']              # bool: 是否通過
result['similarity_score']      # float: 相似度 (0-1)
result['conflict_intensity']    # float: 衝突強度 (0-1)
result['has_growth']            # bool: 是否有成長元素
result['warnings']              # list: 警告訊息
result['errors']                # list: 錯誤訊息

# 生成修復建議
suggestions = validator.generate_fix_suggestions(result)
```

---

### 2️⃣ CharacterArcEnforcer - 角色弧光
```python
from core.character_arc_enforcer import CharacterArcEnforcer

# 從配置文件載入
enforcer = CharacterArcEnforcer('config/arcs.json')

# 或手動添加
enforcer.add_character_arc(
    character="主角",
    states=["普通人", "覺醒", "強者"],
    triggers={1: "普通人", 10: "覺醒", 20: "強者"},
    milestones=[{
        "chapter": 10,
        "event": "遇到導師",
        "state_change": "普通人 -> 覺醒"
    }]
)

# 檢查一致性
result = enforcer.enforce_arc_consistency(
    character="主角",
    chapter_num=15,
    current_state="覺醒階段",
    chapter_outline="本章大綱"  # 可選
)

result['is_consistent']         # bool
result['is_regression']         # bool: 是否倒退
result['expected_state']        # str: 預期狀態
result['missed_triggers']       # list: 遺漏觸發點
```

---

### 3️⃣ ConflictEscalator - 衝突曲線
```python
from core.conflict_escalator import ConflictEscalator

escalator = ConflictEscalator('wave_with_climax')

# 規劃衝突曲線（一次性，50章）
arc = escalator.plan_conflict_arc(total_chapters=50)
# arc = [0.23, 0.31, 0.28, ..., 0.95]  50個值

# 獲取單章預期強度
intensity = escalator.get_chapter_intensity(chapter_num=15)

# 驗證實際強度
result = escalator.enforce_escalation(
    chapter_num=15,
    current_intensity=0.45,  # 實際測得
    tolerance=0.15
)

result['is_acceptable']         # bool
result['action']                # str: 'escalate'/'maintain'/'reduce'
result['suggestions']           # list: 具體建議

# 可視化（ASCII 圖表）
print(escalator.visualize_curve())

# 飽和檢測
is_saturated, msg = escalator.detect_conflict_saturation(
    recent_intensities=[0.85, 0.87, 0.86, 0.88, 0.9],
    threshold=0.85,
    window=5
)
```

---

### 4️⃣ EventDependencyGraph - 事件圖
```python
from core.event_dependency_graph import EventDependencyGraph

graph = EventDependencyGraph()

# 添加事件
graph.add_event(
    event_id="E1",
    chapter_num=5,
    description="主角遇到導師",
    dependencies=[],        # 前置事件
    consequences=["E2"]     # 後續事件
)

graph.add_event("E2", 10, "習得心法", dependencies=["E1"])

# 驗證完整性
validation = graph.validate_event_integrity()

validation['is_valid']              # bool
validation['missing_dependencies']  # list
validation['orphaned_events']       # list: 孤立事件
validation['circular_dependencies'] # list: 循環依賴
validation['timeline_violations']   # list: 時間線錯誤

# 獲取情節漏洞
holes = graph.get_plot_holes()
for hole in holes:
    print(f"{hole['severity']}: {hole['description']}")

# 獲取事件影響鏈
chain = graph.get_event_chain("E2")
chain['predecessors']  # 前置事件
chain['successors']    # 後續事件
chain['depth']         # 依賴深度
```

---

### 5️⃣ PlotManager - 劇情控制
```python
from utils.plot_manager import PlotManager

manager = PlotManager(total_chapters=50)

# 判斷章節類型
chapter_type = manager.get_chapter_type(chapter_num=15)
# 'opening'/'setup'/'development'/'escalation'/'climax'/'resolution'

# 計算衝突強度
intensity = manager.calculate_conflict_level(chapter_num=15)

# 生成完整劇情指引
guidance = manager.generate_plot_guidance(
    chapter_num=15,
    volume_num=1,           # 可選
    volume_context="卷背景" # 可選
)

guidance['chapter_type']           # str
guidance['chapter_type_name']      # str: 中文名
guidance['conflict_level']         # float
guidance['pacing_suggestions']     # list: 節奏建議
guidance['content_focus']          # list: 內容重點
guidance['tone']                   # str: 基調
guidance['key_elements']           # list: 關鍵要素

# 驗證節奏
result = manager.validate_chapter_pacing(15, 0.45)
```

---

### 6️⃣ VolumeManager - 分卷管理
```python
from utils.volume_manager import VolumeManager
from utils.plot_manager import PlotManager

# 初始化（可選整合 PlotManager）
plot_mgr = PlotManager(total_chapters=60)
volume_mgr = VolumeManager(plot_manager=plot_mgr)

# 規劃分卷
plan = volume_mgr.plan_volumes(
    title="測試小說",
    genre="玄幻",
    theme="逆天改命",
    total_chapters=60,
    chapters_per_volume=20  # 可選，自動計算
)

plan['total_volumes']      # int: 總卷數
plan['volumes']            # list: 卷信息
# 每卷: {volume_num, title, theme, start_chapter, end_chapter, chapter_count}

# 生成卷大綱（可接入 API 生成函數）
def my_api_generator(prompt):
    # 調用 AI API
    return "生成的大綱文本"

outline = volume_mgr.generate_volume_outline(
    volume_num=1,
    api_generator_func=my_api_generator  # 可選
)

# 生成本卷所有章節大綱
chapter_outlines = volume_mgr.generate_chapter_outlines(
    volume_num=1,
    volume_outline=outline,
    api_generator_func=my_api_generator
)

# 判斷是否結束卷
should_end, reason = volume_mgr.should_end_volume(
    volume_num=1,
    chapters_in_volume=20,
    current_chapter=20
)

# 生成卷摘要
summary = volume_mgr.generate_volume_summary(
    volume_num=1,
    chapter_contents=["第1章內容", "第2章內容", ...],
    api_generator_func=my_api_generator
)
```

---

## 📋 Phase 2 提示詞方法

```python
from templates.prompts import PromptTemplates

pt = PromptTemplates()

# 1. 分卷規劃提示詞
prompt = pt.build_volume_plan_prompt(
    title="小說標題",
    genre="玄幻",
    theme="主題",
    total_chapters=60
)

# 2. 卷大綱提示詞
prompt = pt.build_volume_outline_prompt(
    title="小說標題",
    genre="玄幻",
    theme="總主題",
    volume_num=1,
    volume_title="第一卷：起",
    volume_theme="覺醒與探索",
    start_chapter=1,
    end_chapter=20,
    total_volumes=3,
    previous_volume_summary="上卷摘要"  # 可選
)

# 3. 章節大綱提示詞（Phase 2）
prompt = pt.build_chapter_outline_prompt_phase2(
    title="小說標題",
    genre="玄幻",
    volume_num=1,
    volume_outline="卷大綱",
    chapter_num=15,
    total_chapters=60,
    chapter_type="development",
    conflict_level=0.45,
    plot_guidance={
        'chapter_type_name': '發展',
        'pacing_suggestions': [...],
        'content_focus': [...],
        'tone': '穩步推進'
    },
    previous_outline="上章大綱"  # 可選
)

# 4. 章節內容生成提示詞（Phase 2）
prompt = pt.build_chapter_prompt_phase2(
    chapter_num=15,
    total_chapters=60,
    volume_num=1,
    volume_outline="卷大綱",
    chapter_outline="本章大綱",
    plot_guidance={...},
    previous_chapter="上章內容",      # 可選
    character_states={'主角': '覺醒'}, # 可選
    event_context="事件背景"           # 可選
)
```

---

## 🔧 典型工作流程

### 工作流 1: 單卷生成（無分卷）
```python
# 1. 創建劇情管理器
plot_mgr = PlotManager(total_chapters=30)

# 2. 規劃衝突曲線（自動完成）
# plot_mgr.conflict_arc 已包含 30 個衝突值

# 3. 生成第 15 章
guidance = plot_mgr.generate_plot_guidance(15)

# 4. 生成章節大綱提示詞
prompt = pt.build_chapter_outline_prompt_phase2(
    ...,
    chapter_type=guidance['chapter_type'],
    conflict_level=guidance['conflict_level'],
    plot_guidance=guidance
)

# 5. 調用 API 生成大綱
outline = api_client.generate(prompt)

# 6. 驗證大綱
validator = OutlineValidator()
result = validator.validate_chapter_outline(outline, previous_outlines, 15)

if not result['is_valid']:
    suggestions = validator.generate_fix_suggestions(result)
    # 根據建議修改或重新生成

# 7. 生成章節內容
prompt = pt.build_chapter_prompt_phase2(
    chapter_num=15,
    ...,
    chapter_outline=outline,
    plot_guidance=guidance
)

content = api_client.generate(prompt)
```

---

### 工作流 2: 多卷生成
```python
# 1. 規劃分卷
volume_mgr = VolumeManager(plot_manager=PlotManager(60))
plan = volume_mgr.plan_volumes("小說", "玄幻", "主題", 60)

# 2. 遍歷每卷
for vol_info in plan['volumes']:
    vol_num = vol_info['volume_num']

    # 2.1 生成卷大綱
    vol_outline = volume_mgr.generate_volume_outline(vol_num, api_func)

    # 2.2 生成本卷所有章節大綱
    ch_outlines = volume_mgr.generate_chapter_outlines(vol_num, vol_outline, api_func)

    # 2.3 生成本卷所有章節內容
    chapter_contents = []
    for i, ch_outline in enumerate(ch_outlines):
        ch_num = vol_info['start_chapter'] + i

        # 獲取劇情指引
        guidance = volume_mgr.plot_manager.generate_plot_guidance(ch_num, 60, vol_num)

        # 生成內容
        prompt = pt.build_chapter_prompt_phase2(
            chapter_num=ch_num,
            total_chapters=60,
            volume_num=vol_num,
            volume_outline=vol_outline,
            chapter_outline=ch_outline,
            plot_guidance=guidance,
            previous_chapter=chapter_contents[-1] if chapter_contents else ""
        )

        content = api_client.generate(prompt)
        chapter_contents.append(content)

    # 2.4 生成卷摘要
    vol_summary = volume_mgr.generate_volume_summary(vol_num, chapter_contents, api_func)
```

---

### 工作流 3: 角色弧光追蹤
```python
# 1. 載入角色弧光
enforcer = CharacterArcEnforcer('config/arcs.json')

# 2. 在每章生成前檢查
result = enforcer.enforce_arc_consistency(
    character="主角",
    chapter_num=15,
    current_state="成長階段",
    chapter_outline=outline
)

if not result['is_consistent']:
    print("警告：角色發展不一致")
    print(f"預期: {result['expected_state']}")
    print(f"實際: {result['current_state']}")
    print(f"錯誤: {result['errors']}")

# 3. 獲取建議
suggestions = enforcer.generate_state_suggestions("主角", 15)

# 4. 在提示詞中注入角色狀態
character_states = {"主角": result['expected_state']}
prompt = pt.build_chapter_prompt_phase2(
    ...,
    character_states=character_states
)
```

---

## 📊 配置文件使用

### arcs.json - 角色弧光
```json
{
  "主角": {
    "states": ["普通人", "覺醒", "成長", "強者"],
    "triggers": {
      "1": "普通人",
      "10": "覺醒",
      "20": "成長",
      "30": "強者"
    },
    "milestones": [
      {"chapter": 10, "event": "遇到導師", "state_change": "普通人 -> 覺醒"}
    ]
  }
}
```

### conflict_curve.json - 衝突曲線
```json
{
  "curve_type": "wave_with_climax",
  "total_chapters": 50,
  "wave_config": {
    "wave_period": 6,
    "climax_start_percent": 0.9
  }
}
```

### validator_rules.json - 驗證規則
```json
{
  "similarity_detection": {
    "threshold": 0.75,
    "strict_mode_threshold": 0.65
  },
  "conflict_intensity": {
    "min_threshold": 0.2
  },
  "growth_indicators": {
    "check_interval": 5
  }
}
```

---

## 🧪 快速測試

```bash
# 運行完整測試
python test_phase2_modules.py

# 測試單個模組（在 Python 中）
python -m utils.outline_validator
python -m core.character_arc_enforcer
python -m core.conflict_escalator
python -m utils.plot_manager
python -m utils.volume_manager
```

---

## 🚨 常見問題

### Q1: sentence-transformers 太大/太慢？
**A**: OutlineValidator 會自動降級到基礎相似度算法（Jaccard），功能正常但精度略低。

### Q2: networkx 不想安裝？
**A**: EventDependencyGraph 會自動降級到字典實現，核心功能不受影響。

### Q3: 如何自定義衝突曲線？
**A**: 修改 `config/conflict_curve.json` 或調用 `ConflictEscalator` 時傳入自定義參數。

### Q4: 如何禁用某些驗證？
**A**: 在 `validate_chapter_outline()` 前設置 `validator.use_embeddings = False` 等。

---

## 📚 更多文檔

- **完整實作報告**: `PHASE2.1_IMPLEMENTATION.md`
- **代碼示例**: 各模組的 `__main__` 部分
- **配置範例**: `config/*.json`

---

**Phase 2.1 核心模組已就緒，開始創作！** 🎉
