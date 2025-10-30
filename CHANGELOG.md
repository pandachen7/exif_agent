# 更新日誌 (Changelog)

## [v2.0.0] - 2025-10-30

### 🎉 重大更新

#### 從 tkinter 完全重建到 PyQt6
- 全新的現代化圖形介面
- 更好的使用者體驗和回饋機制
- 支援背景執行緒處理，介面不會凍結

### ✨ 新功能

#### 1. 多物種標籤支援 (Critical Feature)
- **問題**：原版本無法處理同一張照片拍到多個物種的情況
- **解決**：自動偵測多個 `2_Animal` 標籤並產生對應的多筆記錄
- **實作位置**：
  - `src/exif/exif_reader.py` - 解析多個動物標籤
  - `src/processor.py` - 產生多筆記錄
- **警告機制**：當發現多物種標籤時自動警告使用者

**範例**：
```
照片同時拍到水鹿和野豬
標籤: 2_Animal|Mammal|Deer, 2_Animal|Mammal|Boar
結果: 產生 2 筆記錄
```

#### 2. PaddleOCR 整合
- 使用更先進的 PaddleOCR 取代 Tesseract
- 支援動態切換 OCR 引擎
- 更高的日期辨識準確率
- 自動下載和管理模型

#### 3. 多格式資料輸出
- **Access Database** (.accdb) - 關聯式資料庫
- **Excel** (.xlsx) - 方便檢視和編輯
- **CSV** (.csv) - 通用格式
- 三種格式同步產生，便於對照和備份

#### 4. 命令列介面 (CLI)
- 新增 `cli.py` 用於批次處理
- 支援完整的參數設定
- 適合處理大量照片
- 可整合到自動化腳本

### 🔧 修正問題

#### 1. Date/Time 欄位資料類型
- **問題**：使用 `datetime.date()` 和 `datetime.time()` 可能導致 Access DB 儲存問題
- **修正**：改用完整的 `datetime` 物件
- **影響**：確保 Access DB 正確儲存日期時間資料

#### 2. 日誌系統改進
- **新增**：所有日誌檔案統一儲存到 `logs/` 資料夾
- **格式**：`logs/exif_agent_YYYYMMDD_HHMMSS.log`
- **好處**：更容易管理和清理日誌檔案

### 📚 文件改進

#### 1. README.md 大幅擴充
- 新增詳細的使用範例（GUI、CLI、批次腳本）
- 完整的資料準備指南
- Adobe Bridge 標籤設定教學
- 故障排除指南
- 效能優化建議
- 開發者資訊和架構圖

#### 2. 新增文件
- `USAGE.md` - 詳細使用手冊
- `PROJECT_SUMMARY.md` - 技術總結
- `CHANGELOG.md` - 本文件

### 🏗️ 架構改進

#### 模組化設計
```
src/
├── processor.py          # 核心處理邏輯
├── ui/                   # PyQt6 介面
├── exif/                 # EXIF 處理
├── ocr/                  # OCR 辨識
├── database/             # 資料庫操作
└── utils/                # 工具模組
```

#### 關鍵改進
- 職責清晰分離
- 易於測試和維護
- 支援擴充新功能
- 完整的錯誤處理

### 🔍 程式碼品質

#### 改進項目
1. 刪除未實作的空方法
2. 統一函數返回格式
3. 加強日誌輸出的資訊豐富度
4. 改進異常處理機制
5. 新增類型提示

### ⚙️ 設定檔案

#### config.txt 增強
```ini
[Path]
PathInput = D:\CameraTrap\2024
PathOutput = D:\Results\2024

[Processing]
DefaultTimeInterval = 30
OCREngine = paddle
DebugMode = False

[Database]
AccessDBName = wildlife_data.accdb
ExcelFileName = wildlife_data.xlsx
CSVFileName = wildlife_data.csv
```

### 📊 功能符合度對照

| 功能項目 | v1.0 (tkinter) | v2.0 (PyQt6) | 狀態 |
|---------|----------------|--------------|------|
| EXIF 資訊提取 | ✅ | ✅ | 保持 |
| 多物種標籤處理 | ❌ | ✅ | 新增 |
| OCR 日期辨識 | ✅ (Tesseract) | ✅ (PaddleOCR) | 升級 |
| 時間優先順序 | ✅ | ✅ | 保持 |
| Access DB 儲存 | ✅ | ✅ | 保持 |
| CSV 輸出 | ❌ | ✅ | 新增 |
| Excel 輸出 | ❌ | ✅ | 新增 |
| 圖形介面 | ✅ (tkinter) | ✅ (PyQt6) | 升級 |
| 命令列介面 | ❌ | ✅ | 新增 |
| Camera_ID 解析 | ✅ | ✅ | 保持 |
| 有效照片計算 | ✅ | ✅ | 保持 |
| Species 過濾 | ✅ | ✅ | 保持 |

### 🚨 破壞性變更

#### None
本版本完全向後相容，所有舊版功能都保留並改進。

### 🐛 已知問題

#### None
目前沒有已知的嚴重問題。

### 📝 升級指南

#### 從 v1.0 升級到 v2.0

1. **安裝新版本**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

2. **檢查配置檔案**
   - `config.txt` 格式相同，無需修改

3. **測試多物種功能**
   - 準備有多個動物標籤的測試照片
   - 確認系統產生正確數量的記錄

4. **檢查日誌位置**
   - 日誌現在儲存在 `logs/` 資料夾
   - 舊的 log 檔案可以手動移動或刪除

### 💡 使用建議

#### 最佳實踐
1. **大量照片處理**：使用 CLI 模式比 GUI 更快
2. **準備 CSV 參考**：可大幅提升處理速度和準確度
3. **定期備份**：同時產生的三種格式提供多重備份
4. **檢查日誌**：處理完成後檢查 `logs/` 中的警告訊息

#### 常見場景
- **單一站點測試**：使用 GUI，可即時看到進度
- **多站點批次**：使用 CLI，建立 .bat 腳本自動化
- **資料驗證**：對照 Excel 和 Access DB 確認正確性

### 🙏 致謝

感謝所有使用者的回饋和建議，特別是：
- 提供原始文件和需求規格
- 回報多物種標籤處理需求
- 測試和驗證新功能

---

**維護者**：EXIF Agent 開發團隊
**最後更新**：2025-10-30
