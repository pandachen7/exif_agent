# EXIF Agent 專案總結

## 專案概述

本專案是基於舊版 tkinter 程式重建的 EXIF 照片資訊管理系統，主要用於處理自動相機拍攝的照片與影片，提取EXIF資訊並進行資料分析。

## 主要改進

### 1. 使用者介面升級
- **舊版**: tkinter
- **新版**: PyQt6
- 更現代化的介面設計
- 更好的跨平台支援

### 2. OCR 引擎升級
- **舊版**: Tesseract OCR
- **新版**: 支援 PaddleOCR（主要）和 Tesseract（備選）
- PaddleOCR 提供更好的辨識準確度
- 支援動態切換 OCR 引擎

### 3. 資料儲存增強
- **保留**: Access DB (.accdb) 儲存
- **新增**: CSV (.csv) 同步儲存
- **新增**: Excel (.xlsx) 同步儲存
- 方便資料對照與檢視

### 4. 程式架構改進
- 模組化設計，各功能獨立
- 清楚的目錄結構
- 完整的日誌記錄
- 支援 GUI 和命令列兩種模式

## 專案結構

```
exif_agent/
├── main.py                     # GUI 主程式
├── cli.py                      # 命令列介面
├── config.txt                  # 配置檔案
├── requirements.txt            # Python 套件清單
├── README.md                   # 專案說明
├── USAGE.md                    # 使用手冊
├── PROJECT_SUMMARY.md          # 本文件
│
├── doc/                        # 文件資料夾
│   └── exif2accessDB(EXIF轉換資料表).docx
│
├── src/                        # 原始碼目錄
│   ├── __init__.py
│   ├── processor.py            # 照片處理核心邏輯
│   │
│   ├── ui/                     # 使用者介面模組
│   │   ├── __init__.py
│   │   └── main_window.py      # PyQt6 主視窗
│   │
│   ├── exif/                   # EXIF 處理模組
│   │   ├── __init__.py
│   │   └── exif_reader.py      # EXIF 讀取器
│   │
│   ├── ocr/                    # OCR 模組
│   │   ├── __init__.py
│   │   └── ocr_detector.py     # OCR 日期偵測器
│   │
│   ├── database/               # 資料庫模組
│   │   ├── __init__.py
│   │   ├── access_db.py        # Access DB 操作
│   │   └── csv_excel_writer.py # CSV/Excel 寫入器
│   │
│   └── utils/                  # 工具模組
│       ├── __init__.py
│       ├── config.py           # 配置管理
│       └── logger.py           # 日誌管理
│
├── output/                     # 輸出資料夾（自動建立）
│   ├── exif_data.accdb
│   ├── exif_data.xlsx
│   └── exif_data.csv
│
└── venv/                       # 虛擬環境
```

## 核心功能

### 1. EXIF 資訊提取 (`src/exif/exif_reader.py`)
- 讀取照片與影片的 EXIF 元數據
- 提取日期時間、相機 ID、標籤資訊
- 解析 Adobe Bridge 的 HierarchicalSubject 標籤
- 自動識別 Site、Plot_ID、Camera_ID
- 提取物種分類（Group、Species）與數量

### 2. 日期時間偵測 (`src/ocr/ocr_detector.py`)
日期時間取得優先順序：
1. **CSV 參考檔案**：從同名 CSV 讀取準確時間
2. **EXIF CreateDate**：從照片 EXIF 資訊中提取
3. **OCR 辨識**：使用 PaddleOCR 辨識照片上的日期
4. **前一筆記錄**：使用連續檔案的時間

支援的日期格式：
- `2020/06/22 09:40:05`
- `2020-06-22 09:40:05`
- `2020.06.22 09:40:05`
- `2020/6/22 09:40` (無秒數自動補 00)

### 3. 有效照片計算 (`src/processor.py`)
- 按照 Camera_ID 和 Species 分組
- 根據設定的時間間隔（預設 30 分鐘）計算有效照片
- 同一物種在時間間隔內只計算一次
- IndependentPhoto 欄位標記：1 為有效，0 為無效

### 4. 資料儲存
**Access DB** (`src/database/access_db.py`):
- 自動建立 file_record 資料表
- 批次插入資料
- 支援清空資料表功能

**CSV/Excel** (`src/database/csv_excel_writer.py`):
- 同時輸出 CSV 和 Excel 格式
- 便於資料檢視與對照
- 支援讀取 CSV 作為時間參考

### 5. 使用者介面 (`src/ui/main_window.py`)
**PyQt6 GUI 功能**：
- 路徑選擇（輸入/輸出資料夾）
- 處理參數設定（時間間隔、OCR 引擎）
- 即時進度顯示
- 警告訊息顯示
- 資料表清空功能
- 設定儲存功能

**執行緒處理**：
- 使用 QThread 進行背景處理
- 避免 UI 凍結
- 即時更新處理進度

## 技術特點

### 1. 模組化設計
- 各功能模組獨立，易於維護與擴充
- 清晰的依賴關係
- 便於單元測試

### 2. 錯誤處理
- 完整的異常捕捉
- 詳細的錯誤日誌
- 友善的錯誤提示

### 3. 日誌系統
- 自動產生日誌檔案
- 記錄所有重要操作
- 支援不同等級的日誌（INFO、WARNING、ERROR）

### 4. 彈性配置
- 支援 config.txt 設定檔
- 可透過 GUI 或手動修改
- 設定即時儲存

## 相依套件

主要套件：
- **PyQt6**: GUI 框架
- **PaddleOCR**: OCR 文字辨識
- **Pillow**: 影像處理
- **exifread**: EXIF 資訊讀取
- **pandas**: 資料處理
- **openpyxl**: Excel 檔案操作
- **pyodbc**: Access DB 連接

## 使用情境

### 情境 1: 大量照片批次處理
```bash
python cli.py -i D:\Photos\2020_Wildlife -o D:\Output
```

### 情境 2: 需要調整參數的處理
1. 啟動 GUI: `python main.py`
2. 選擇輸入/輸出資料夾
3. 調整時間間隔（如 60 分鐘）
4. 選擇 OCR 引擎
5. 開始處理

### 情境 3: 已有 CSV 時間參考
1. 將 CSV 檔案放在照片資料夾中
2. 命名為與資料夾同名（如 `100RECNX.csv`）
3. 執行處理，系統會優先使用 CSV 時間

## 已知限制與注意事項

### 1. Access DB 支援
- Windows Only
- 需要安裝 Microsoft Access Database Engine
- 32/64 位元需與 Python 版本匹配

### 2. OCR 辨識
- PaddleOCR 首次執行需下載模型（約 10-20 MB）
- 辨識準確度受照片品質影響
- 建議準備 CSV 參考檔案以確保時間準確

### 3. 效能考量
- 大量照片處理較耗時
- OCR 處理速度較慢
- 建議使用命令列模式進行大批次處理

### 4. 標籤格式
- 必須使用 Adobe Bridge 的 HierarchicalSubject 格式
- Camera_ID 前綴必須為英文字母（如 JC38，不可 12JC）
- 缺少 Species 標籤的照片會被跳過

## 未來改進方向

1. **效能優化**
   - 多執行緒並行處理
   - OCR 批次處理
   - 資料庫批次寫入優化

2. **功能擴充**
   - 支援更多 OCR 引擎
   - 影片 EXIF 支援加強
   - 自動產生 OI 計算報表

3. **使用者體驗**
   - 處理進度更精確顯示
   - 支援拖放檔案
   - 預覽功能

4. **資料分析**
   - 內建 OI 值計算
   - 資料視覺化
   - 自動產生統計報表

## 授權與支援

本專案為內部使用工具，基於原 tkinter 版本重建而成。

技術支援：
- 檢查日誌檔案: `exif_agent_YYYYMMDD_HHMMSS.log`
- 參考使用手冊: `USAGE.md`
- 閱讀原始文件: `doc/exif2accessDB(EXIF轉換資料表).docx`
