# 文檔目錄

此目錄包含 AI 小說生成器的所有技術文檔、測試報告和使用指南。

## 📁 目錄結構

```
docs/
├── reports/      # 測試報告和系統優化報告
└── guides/       # 使用指南和技術文檔
```

## 📊 reports/ - 測試報告

包含各種參數測試和系統優化的詳細報告：

### GLM-4 相關
- **GLM4_PARAMS_TEST_README.md** - GLM-4 參數測試系統使用說明
- **GLM4_DEBUG_ENHANCEMENT_REPORT.md** - GLM-4 診斷增強報告

### DeepSeek R1 相關
- **R1_PARAMS_FINAL_SUMMARY.md** - R1 參數測試最終總結
- **R1_OFFICIAL_PARAMS_TEST_REPORT.md** - R1 官方參數測試報告
- **EMERGENCY_FIX_R1.md** - R1 緊急修復報告

### Bug 修復報告
- **BUGFIX_CHARACTER_ARC_ENFORCER.md** - 角色弧線強制器 Bug 修復
- **BUGFIX_SHOULD_END_VOLUME_CALL.md** - 卷結束判斷 Bug 修復
- **BUGFIX_VOLUME_MANAGER.md** - 卷管理器 Bug 修復

### 系統報告
- **STRESS_TEST_REPORT.md** - 壓力測試報告
- **PHASE2_IMPLEMENTATION_REPORT.md** - Phase 2 實現報告
- **IMPLEMENTATION_REPORT.md** - 功能實現報告

### 發布相關
- **GITHUB_RELEASE_v0.1.0.md** - GitHub 發布說明 v0.1.0
- **RELEASE_NOTES_v0.1.0.md** - 版本發布說明 v0.1.0

## 📚 guides/ - 使用指南

包含重構報告、使用指南等技術文檔：

### 重構文檔
- **REFACTOR_OUTLINE_GENERATOR.md** - 大綱生成器重構報告
- **REFACTOR_LAZY_LOADING.md** - 延遲載入優化報告
- **REFACTOR_OUTLINE_DIFFERENTIATION.md** - 大綱差異化重構
- **REFACTOR_CHAPTER_DIFFERENTIATION.md** - 章節差異化重構
- **REFACTOR_REPORT.md** - 重構總結報告

### 參數測試指南
- **R1_PARAMS_TESTER_GUIDE.md** - R1 參數測試器使用指南
- **R1_PARAMS_TESTER_SUMMARY.md** - R1 參數測試器總結

### Phase 2 文檔
- **PHASE2_IMPLEMENTATION.md** - Phase 2 實現文檔
- **PHASE2.1_IMPLEMENTATION.md** - Phase 2.1 實現文檔
- **PHASE2_QUICK_REFERENCE.md** - Phase 2 快速參考

### 開發文檔
- **AI小說生成器完整技術文檔.md** - 完整技術文檔
- **README_DEV.md** - 開發者文檔
- **CHANGELOG.md** - 變更日誌
- **GITHUB_SETUP.md** - GitHub 設置指南

## 🔍 快速導航

### 想要開始參數測試？
→ [GLM-4 參數測試指南](reports/GLM4_PARAMS_TEST_README.md)
→ [R1 參數測試指南](guides/R1_PARAMS_TESTER_GUIDE.md)

### 想要了解系統架構？
→ [完整技術文檔](guides/AI小說生成器完整技術文檔.md)
→ [開發者文檔](guides/README_DEV.md)

### 想要了解最新優化？
→ [延遲載入優化](guides/REFACTOR_LAZY_LOADING.md)
→ [大綱生成器重構](guides/REFACTOR_OUTLINE_GENERATOR.md)

### 想要了解 Bug 修復？
→ [R1 緊急修復](reports/EMERGENCY_FIX_R1.md)
→ [Bug 修復報告列表](reports/)

### 想要了解版本更新？
→ [變更日誌](guides/CHANGELOG.md)
→ [版本發布說明](reports/RELEASE_NOTES_v0.1.0.md)

## 📝 文檔撰寫規範

所有文檔應遵循以下規範：
1. 使用 Markdown 格式
2. 包含清晰的標題層級
3. 提供代碼示例（如適用）
4. 包含使用方法和注意事項
5. 標註日期和版本信息

## 🔄 更新頻率

- **reports/** - 每次參數測試或 Bug 修復後更新
- **guides/** - 重大功能變更或重構後更新
