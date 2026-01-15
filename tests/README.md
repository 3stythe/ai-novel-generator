# 測試腳本目錄

此目錄包含所有測試腳本，用於驗證和優化 AI 小說生成器的各項功能。

## 📋 主要測試腳本

### GLM-4 參數測試
- **test_glm4_params.py** - GLM-4 參數自動測試系統
  - 測試不同參數組合對 GLM-4 大綱生成品質的影響
  - 包含 GLM-4 特有評估指標（中文流暢度、文化底蘊、創意性、邏輯連貫性）
  - 支持快速測試和完整測試模式

- **test_glm4_quick_verify.py** - GLM-4 快速驗證腳本
  - 單參數組合快速驗證
  - 默認啟用 Debug 模式顯示詳細評分過程

### DeepSeek R1 參數測試
- **test_r1_params_enhanced.py** - R1 參數測試系統（增強版）
  - 整合對抗式評估、多 AI 投票和相對排名法
  - AI 評審功能

- **test_r1_params.py** - R1 參數測試系統（基礎版）
- **test_r1_params_verify.py** - R1 快速驗證腳本
- **test_r1_official_params.py** - R1 官方參數測試

### 功能測試
- **test_generate.py** - 基礎生成功能測試
- **test_phase2.py** - Phase 2 功能測試
- **test_phase2_init.py** - Phase 2 初始化測試
- **test_phase2_modules.py** - Phase 2 模組測試
- **test_three_models.py** - 三模型對比測試
- **test_stress.py** - 壓力測試

### Bug 修復驗證
- **test_emergency_fix.py** - 緊急修復驗證
- **test_character_arc_fix.py** - 角色弧線修復驗證
- **test_should_end_volume_fix.py** - 卷結束判斷修復驗證
- **test_volume_manager_fix.py** - 卷管理器修復驗證
- **test_volume_type_fix_simple.py** - 卷類型修復簡單驗證

### 重構驗證
- **test_refactored_cli.py** - CLI 重構驗證
- **test_editor_config.py** - Editor 配置測試
- **test_startup_time.py** - 啟動時間測試

## 🚀 使用方法

### 從項目根目錄運行

```bash
# GLM-4 參數測試（快速模式）
python tests/test_glm4_params.py --quick --no-ai

# GLM-4 參數測試（完整模式）
python tests/test_glm4_params.py --full

# GLM-4 參數測試（Debug 模式）
python tests/test_glm4_params.py --quick --debug

# GLM-4 快速驗證
python tests/test_glm4_quick_verify.py

# R1 參數測試（快速模式）
python tests/test_r1_params_enhanced.py --quick

# 基礎生成測試
python tests/test_generate.py
```

### 從 tests 目錄運行

```bash
cd tests

# GLM-4 快速測試
python test_glm4_params.py --quick --no-ai

# R1 快速測試
python test_r1_params_enhanced.py --quick
```

## 📊 測試結果

測試結果會保存在項目根目錄的 `test_results/` 目錄中：
- `test_results/glm4/` - GLM-4 測試結果
- `test_results/` - R1 和其他測試結果

## 📝 注意事項

1. **環境變量**: 確保 `.env` 文件中設置了 `SILICONFLOW_API_KEY`
2. **依賴安裝**: 運行測試前確保已安裝所有依賴：`pip install -r requirements.txt`
3. **測試時間**:
   - 快速測試（--quick）: 5-10 分鐘
   - 完整測試（--full）: 1-2 小時
4. **Debug 模式**: 使用 `--debug` 參數可查看詳細的評分過程

## 📚 相關文檔

- [GLM-4 參數測試指南](../docs/reports/GLM4_PARAMS_TEST_README.md)
- [GLM-4 診斷增強報告](../docs/reports/GLM4_DEBUG_ENHANCEMENT_REPORT.md)
- [R1 參數測試指南](../docs/guides/R1_PARAMS_TESTER_GUIDE.md)
- [R1 參數測試總結](../docs/guides/R1_PARAMS_TESTER_SUMMARY.md)
