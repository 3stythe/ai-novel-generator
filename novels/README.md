# 生成的小說目錄

此目錄包含所有通過 `novel_generator.py` 生成的小說項目。

## 📁 小說文件夾結構

每個小說文件夾遵循以下命名格式：
```
novel_[小說名稱]_[生成日期時間]
```

例如：
- `novel_星際邊緣_20260104_023632`
- `novel_時空裂痕_20260108_223154`
- `novel_測試小說_20260111_145126_20260111_145126`

## 📝 小說內容結構

每個小說文件夾包含：

```
novel_XXX_YYYYMMDD_HHMMSS/
├── metadata.json      # 小說元數據（標題、作者、生成時間等）
├── outline.txt        # 小說大綱
└── chapters/          # 章節內容目錄
    ├── chapter_1.txt  # 第一章
    ├── chapter_2.txt  # 第二章
    └── ...
```

### metadata.json 內容

```json
{
    "title": "小說標題",
    "author": "AI 小說生成器",
    "created_at": "2026-01-04 02:36:32",
    "genre": "科幻",
    "model": "GLM-4",
    "parameters": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 6000
    }
}
```

### outline.txt 格式

包含完整的小說大綱：
- 基本信息（主題、風格、設定）
- 核心衝突
- 各卷概述
- 詳細章節大綱

### chapters/ 目錄

包含所有生成的章節內容：
- `chapter_1.txt` - 第一章內容
- `chapter_2.txt` - 第二章內容
- ...

## 🚀 如何生成小說

從項目根目錄運行：

```bash
# 互動式生成
python novel_generator.py

# 指定小說名稱
python novel_generator.py --title "我的科幻小說"

# 指定章節數
python novel_generator.py --chapters 10

# 使用特定模型
python novel_generator.py --model glm-4
```

## 📊 小說統計

生成的小說會自動保存到此目錄，可以通過以下方式查看：

```bash
# 查看所有小說
ls -l novels/

# 查看特定小說
cd novels/novel_星際邊緣_20260104_023632
cat outline.txt
ls chapters/

# 統計小說數量
ls -d novels/novel_*/ | wc -l
```

## 🗑️ 清理舊小說

如果需要清理舊的測試小說：

```bash
# 刪除特定日期的小說
rm -rf novels/novel_*_20260104_*

# 清空所有小說（謹慎使用）
rm -rf novels/novel_*/
```

## 📝 注意事項

1. **自動保存**: 所有生成的小說都會自動保存到此目錄
2. **唯一命名**: 每個小說都有唯一的時間戳，避免覆蓋
3. **保留測試**: 測試生成的小說也會保存在此目錄
4. **版本控制**: 如果不想提交生成的小說到 Git，可在 `.gitignore` 中添加：
   ```
   novels/novel_*/
   ```

## 🎯 小說類型

根據文件夾名稱可以看出小說的用途：

- `novel_測試小說_*` - 測試生成
- `novel_R1_官方參數測試_*` - R1 參數測試
- `novel_Phase_2_1_測試小說_*` - Phase 2.1 功能測試
- `novel_MVP_兼容性測試_*` - MVP 模式兼容性測試
- `novel_三模型測試小說_*` - 三模型對比測試
- `novel_緊急修復測試_*` - Bug 修復驗證
- 其他命名 - 實際小說生成

## 📚 相關文檔

- [小說生成器使用指南](../docs/guides/AI小說生成器完整技術文檔.md)
- [參數優化指南](../docs/reports/GLM4_PARAMS_TEST_README.md)
- [開發者文檔](../docs/guides/README_DEV.md)
