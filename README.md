# EXIF Agent - 照片 EXIF 資訊管理系統

這是一個用於處理自動相機照片的 EXIF 資訊提取、OCR 日期辨識以及資料儲存的專業工具。專為野生動物研究和生態調查設計，可自動處理大量相機陷阱照片，提取物種資訊並計算 OI (Occurrence Index) 值。

## 🎯 核心功能

### 1. EXIF 資訊智能提取
- 自動讀取照片和影片的完整 EXIF 元數據
- 解析 Adobe Bridge 的 HierarchicalSubject 標籤
- **支援多物種標記**：同一張照片可標記多個物種，自動產生多筆記錄
- 自動識別相機站點（Site）、樣點編號（Plot_ID）、相機編號（Camera_ID）

### 2. 多重日期時間來源
按優先順序自動選擇最準確的時間資訊：
1. **CSV 參考檔案** - 最準確的時間來源
2. **EXIF CreateDate** - 照片內嵌的拍攝時間
3. **OCR 智能辨識** - 使用 PaddleOCR 辨識照片上的日期戳記
4. **前一筆記錄** - 連續檔案使用相近時間
5. **預設值** - 2000/1/1（最後手段）

### 3. 智能資料處理
- **有效照片計算**：根據時間間隔（預設30分鐘）自動計算獨立事件
- **多物種處理**：自動偵測並分離同張照片中的不同物種記錄
- **資料驗證**：自動過濾無效資料（如 unknown 物種）
- **警告提示**：缺少 Camera_ID 或發現多物種時自動警告

### 4. 多格式資料儲存
- **Access Database** (.accdb) - 完整的關聯式資料庫
- **Excel** (.xlsx) - 方便檢視和編輯
- **CSV** (.csv) - 通用格式，易於匯入其他系統

## 📋 系統需求

- Python 3.11 或更高版本
- Windows 10/11（Access DB 支援）
- 4GB RAM 以上（建議 8GB）
- 10GB 可用硬碟空間（用於暫存 OCR 模型）

## 🚀 快速開始

### 安裝步驟

1. **clone或下載專案**
```bash
git clone https://github.com/pandachen7/exif_agent
cd exif_agent
```

2. **建立虛擬環境**
```bash
python -m venv venv
```

3. **啟動虛擬環境**
```bash
# Windows
venv\Scripts\activate

# 如果使用 PowerShell 出現權限問題，先執行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. **安裝相依套件**
```bash
pip install -r requirements.txt
```

> ⚠️ **注意**：首次執行時 PaddleOCR 會自動下載模型檔案（約 10-20MB）

## 💻 使用方式

### 方式一：圖形化介面（推薦）

```bash
python main.py
```

**操作步驟：**
1. 選擇輸入資料夾（包含照片的目錄）
2. 選擇輸出資料夾（儲存結果）
3. 設定時間間隔（預設 30 分鐘）
4. 選擇 OCR 引擎（預設 PaddleOCR）
5. 點擊「開始處理」

### 方式二：命令列介面（批次處理）

**基本用法：**
```bash
python cli.py -i <輸入資料夾> -o <輸出資料夾>
```

**進階選項：**
```bash
# 設定時間間隔為 60 分鐘
python cli.py -i D:\Photos\2024 -o D:\Results --time-interval 60

# 使用 Tesseract OCR（需另外安裝）
python cli.py -i D:\Photos -o D:\Results --ocr tesseract

# 跳過 Access DB（只產生 CSV 和 Excel）
python cli.py -i D:\Photos -o D:\Results --skip-access
```

### 方式三：批次處理腳本

建立 `batch_process.bat`：
```batch
@echo off
echo 開始批次處理相機陷阱照片...
python cli.py -i "D:\CameraTrap\Site1" -o "D:\Results\Site1"
python cli.py -i "D:\CameraTrap\Site2" -o "D:\Results\Site2"
echo 處理完成！
pause
```

## 📁 資料準備

### 1. 照片目錄結構範例

```
D:\CameraTrap\
├── 100RECNX\           # 相機 1 的照片
│   ├── IMG_0001.JPG
│   ├── IMG_0002.JPG
│   └── 100RECNX.csv    # 時間參考檔（可選）
├── 101RECNX\           # 相機 2 的照片
│   └── ...
└── JC38_20240101\      # 特定站點的照片
    └── ...
```

### 2. CSV 時間參考檔格式

如果照片的 EXIF 時間不準確，可建立 CSV 檔案提供正確時間：

**檔名**：與資料夾同名（如 `100RECNX.csv`）

**內容格式**：
```csv
Filename,CreateDate
IMG_0001.JPG,2024/01/15 08:30:15
IMG_0002.JPG,2024/01/15 08:35:22
IMG_0003.JPG,2024/01/15 09:15:10
```

### 3. Adobe Bridge 標籤設定

使用 Adobe Bridge 標記照片時，請依照以下格式：

```
階層式關鍵字結構：
├── 1_Site ID
│   └── JC38           # 相機站點編號
├── 2_Animal
│   ├── Mammal         # 哺乳類
│   │   ├── Deer       # 鹿
│   │   └── Boar       # 野豬
│   └── Bird           # 鳥類
│       └── Pheasant   # 雉雞
└── 3_Number
    ├── 1              # 1 隻
    ├── 2              # 2 隻
    └── >5             # 超過 5 隻
```

**多物種標記範例**：
- 同時拍到鹿和野豬：勾選 `2_Animal|Mammal|Deer` 和 `2_Animal|Mammal|Boar`
- 系統會自動產生兩筆記錄

## 📊 輸出資料說明

### 資料表欄位說明

| 欄位名稱 | 資料類型 | 說明 | 範例 |
|---------|---------|------|------|
| SourceFile | VARCHAR(50) | 檔案名稱 | IMG_0001.JPG |
| DateTimeOriginal | DATETIME | 原始拍攝時間 | 2024/01/15 08:30:15 |
| Date | DATETIME | 日期（Access用） | 2024/01/15 00:00:00 |
| Time | DATETIME | 時間（Access用） | 1900/01/01 08:30:15 |
| Site | VARCHAR(6) | 樣區代碼 | JC |
| Plot_ID | VARCHAR(6) | 樣點編號 | 38 |
| Camera_ID | VARCHAR(6) | 相機編號 | JC38 |
| Group | VARCHAR(20) | 動物大類 | Mammal |
| Species | VARCHAR(30) | 物種名稱 | Deer |
| Number | INTEGER | 個體數量 | 1 |
| Note | VARCHAR(100) | 備註 | |
| IndependentPhoto | INTEGER | 有效照片標記（0/1） | 1 |
| CreateDate | DATETIME | 記錄建立時間 | 2024/10/30 12:00:00 |
| period_start | DATETIME | 該相機最早照片 | 2024/01/01 00:00:00 |
| period_end | DATETIME | 該相機最晚照片 | 2024/01/31 23:59:59 |

### OI 值計算

OI (Occurrence Index) = 有效照片數 / 相機工作時數 × 1000

- **有效照片**：同一物種在設定時間間隔內只計算一次
- **相機工作時數**：從第一張照片到最後一張照片的時間差（小時）

## 🔧 進階設定

### 修改 config.txt

```ini
[Path]
PathInput = D:\CameraTrap\2024   # 預設輸入路徑
PathOutput = D:\Results\2024      # 預設輸出路徑

[Processing]
DefaultTimeInterval = 30          # 時間間隔（分鐘）
OCREngine = paddle               # OCR 引擎（paddle/tesseract）
DebugMode = False                # 除錯模式

[Database]
AccessDBName = wildlife_data.accdb
ExcelFileName = wildlife_data.xlsx
CSVFileName = wildlife_data.csv
```

## 🛠️ 故障排除

### 常見問題

#### 1. Access DB 連接失敗
**錯誤訊息**：`[Microsoft][ODBC Driver Manager] Data source name not found`

**解決方法**：
1. 下載並安裝 [Microsoft Access Database Engine 2016](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
2. 選擇與 Python 版本相符的位元版本（32/64 位元）
3. 如已安裝 Office，確認版本相容性

#### 2. PaddleOCR 模型下載失敗
**問題**：網路連接問題導致模型下載失敗

**解決方法**：
```bash
# 手動下載模型
python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')"
```

#### 3. PyQt6 介面無法啟動
**錯誤**：`Could not find the Qt platform plugin "windows"`

**解決方法**：
```bash
# 重新安裝 PyQt6
pip uninstall PyQt6 PyQt6-Qt6
pip install PyQt6
```

#### 4. OCR 辨識率低
**問題**：照片上的日期文字模糊或位置不標準

**解決方法**：
- 準備 CSV 參考檔案提供準確時間
- 調整照片品質或重新拍攝
- 考慮使用其他 OCR 引擎

### 效能優化建議

1. **處理大量照片**（>10,000 張）
   - 使用命令列模式（比 GUI 快）
   - 分批處理不同資料夾
   - 關閉不需要的功能（如 --skip-access）

2. **記憶體優化**
   - 一次處理較少的檔案
   - 定期重啟程式釋放記憶體

3. **加速 OCR 處理**
   - 確保照片日期戳記清晰
   - 統一日期戳記位置
   - 考慮預先裁切日期區域

## 📝 開發者資訊

### 專案架構

```
exif_agent/
├── main.py                 # GUI 主程式入口
├── cli.py                  # 命令列介面
├── config.txt              # 設定檔
├── requirements.txt        # Python 套件清單
├── README.md               # 專案說明文件
├── USAGE.md                # 詳細使用手冊
├── PROJECT_SUMMARY.md      # 專案技術總結
│
├── src/                    # 原始碼目錄
│   ├── processor.py        # 核心處理邏輯
│   ├── ui/                 # PyQt6 介面模組
│   │   └── main_window.py  # 主視窗實作
│   ├── exif/               # EXIF 處理模組
│   │   └── exif_reader.py  # EXIF 讀取器
│   ├── ocr/                # OCR 處理模組
│   │   └── ocr_detector.py # OCR 偵測器
│   ├── database/           # 資料庫模組
│   │   ├── access_db.py    # Access DB 操作
│   │   └── csv_excel_writer.py # CSV/Excel 寫入
│   └── utils/              # 工具模組
│       ├── config.py       # 配置管理
│       └── logger.py       # 日誌記錄
│
├── doc/                    # 文件資料夾
│   └── exif2accessDB(EXIF轉換資料表).docx
│
├── logs/                   # 日誌資料夾（自動建立）
├── output/                 # 輸出資料夾（自動建立）
└── venv/                   # Python 虛擬環境

```

### 核心模組說明

| 模組 | 功能 | 關鍵類別/函數 |
|-----|------|-------------|
| `processor.py` | 照片處理核心 | `PhotoProcessor` |
| `exif_reader.py` | EXIF 資訊提取 | `ExifReader._parse_hierarchical_subject()` |
| `ocr_detector.py` | OCR 日期辨識 | `OCRDetector.detect_datetime_from_image()` |
| `access_db.py` | Access DB 操作 | `AccessDB.insert_records_batch()` |
| `csv_excel_writer.py` | CSV/Excel 輸出 | `CSVExcelWriter.write_to_excel()` |
| `main_window.py` | PyQt6 介面 | `MainWindow`, `ProcessThread` |

## 🔄 更新記錄

### v2.0.0 (2025-10-30)
- 🆕 從 tkinter 升級到 PyQt6 介面
- 🆕 新增 PaddleOCR 支援（替代 Tesseract）
- 🆕 **支援多物種標籤處理** - 同一張照片可產生多筆記錄
- 🆕 新增 CSV/Excel 同步輸出
- 🔧 修正 Date/Time 欄位資料類型問題
- 🔧 改進錯誤處理和日誌系統
- 📚 新增完整中文文件

## 📧 聯絡與支援

如遇到問題或需要技術支援，請：
1. 查看 [USAGE.md](USAGE.md) 詳細使用手冊
2. 查看日誌檔案 `logs/exif_agent_YYYYMMDD_HHMMSS.log`
3. 參考原始文件 `doc/exif2accessDB(EXIF轉換資料表).docx`

## 📄 授權

本專案為野生動物研究專用工具，僅供內部使用。

---

**特別感謝**：本專案基於原始 tkinter 版本重建，感謝所有研究人員的回饋與建議。

