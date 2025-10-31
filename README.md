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

5. **安裝 Tesseract OCR（可選）**

如果需要使用 Tesseract OCR 引擎，請依照以下方式安裝：

**Windows 環境：**
1. 下載 Tesseract 安裝程式：
   - 前往 [Tesseract GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - 下載最新版本的 Windows 安裝檔（如 `tesseract-ocr-w64-setup-5.3.3.20231005.exe`）

2. 執行安裝程式：
   - 建議安裝到預設路徑：`C:\Program Files\Tesseract-OCR`
   - 記得勾選「Additional language data」以支援多語言（如需要）

3. 設定環境變數：
   - 將 Tesseract 的安裝路徑加入系統 PATH
   - 或在程式中指定 tesseract 路徑：
     ```python
     # 在 src/ocr/ocr_detector.py 中設定
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

4. 驗證安裝：
   ```bash
   tesseract --version
   ```

**Ubuntu/Debian 環境：**
```bash
# 更新套件列表
sudo apt update

# 安裝 Tesseract OCR
sudo apt install tesseract-ocr

# 安裝額外語言包（可選）
sudo apt install tesseract-ocr-chi-tra  # 繁體中文
sudo apt install tesseract-ocr-chi-sim  # 簡體中文
sudo apt install tesseract-ocr-eng      # 英文（通常已包含）

# 驗證安裝
tesseract --version
```

> ⚠️ **注意**：
> - PaddleOCR 是預設 OCR 引擎，無需額外安裝，首次執行時會自動下載模型檔案（約 10-20MB）
> - Tesseract 僅在選擇使用時需要安裝

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

## 🔧 設定檔案

### config.yaml 配置說明

配置檔案位於 `cfg/config.yaml`（首次執行時會自動建立）

```yaml
# 路徑設定
path:
  input: "D:\\CameraTrap\\2024"   # 預設輸入路徑
  output: "D:\\Results\\2024"      # 預設輸出路徑

# 處理設定
processing:
  default_time_interval: 30        # 時間間隔（分鐘）
  ocr_engine: "paddle"            # OCR 引擎（paddle/tesseract）
  debug_mode: false               # 除錯模式

# 資料庫設定
database:
  access_db_name: "wildlife_data.accdb"
  excel_file_name: "wildlife_data.xlsx"
  csv_file_name: "wildlife_data.csv"
```

也可以從範本檔案開始：
```bash
cp cfg/config.yaml.template cfg/config.yaml
```

### OCR 引擎選擇

**PaddleOCR**（推薦）：
- ✅ 準確率高、支援多語言
- ✅ 無需額外安裝，自動下載模型
- ⚠️ 首次執行需要下載模型（約 10-20MB）

**Tesseract**：
- ✅ 傳統 OCR 引擎，穩定可靠
- ⚠️ 需要另外安裝 Tesseract OCR 軟體

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
├── requirements.txt        # Python 套件清單
├── README.md               # 專案說明文件
├── CHANGELOG.md            # 更新記錄
│
├── cfg/                    # 配置檔案資料夾
│   ├── config.yaml         # 主配置檔（自動建立）
│   └── config.yaml.template # 配置範本檔
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

### 核心功能詳解

#### 1. EXIF 資訊提取 (`src/exif/exif_reader.py`)
- 讀取照片與影片的 EXIF 元數據
- 提取日期時間、相機 ID、標籤資訊
- 解析 Adobe Bridge 的 HierarchicalSubject 標籤
- **多物種標籤支援**：自動偵測同張照片中的多個物種
- 自動識別 Site、Plot_ID、Camera_ID
- 提取物種分類（Group、Species）與數量

#### 2. 日期時間偵測優先順序 (`src/ocr/ocr_detector.py`)
1. **CSV 參考檔案**：從同名 CSV 讀取準確時間（最優先）
2. **EXIF CreateDate**：從照片 EXIF 資訊中提取
3. **OCR 辨識**：使用 PaddleOCR 辨識照片上的日期
4. **前一筆記錄**：使用連續檔案的時間
5. **預設值**：2000/1/1（最後手段）

支援的日期格式：
- `2020/06/22 09:40:05`
- `2020-06-22 09:40:05`
- `2020.06.22 09:40:05`
- `2020/6/22 09:40` (無秒數自動補 00)

#### 3. 有效照片計算邏輯 (`src/processor.py`)
- 按照 (Camera_ID, Species) 分組
- 根據設定的時間間隔（預設 30 分鐘）計算有效照片
- 同一物種在時間間隔內只計算一次
- IndependentPhoto 欄位標記：1 為有效，0 為無效
- 自動計算每台相機的工作期間（period_start, period_end）

#### 4. 資料儲存機制
**Access DB** (`src/database/access_db.py`):
- 自動建立 file_record 資料表
- 批次插入資料
- 支援清空資料表功能
- 完整的欄位類型定義

**CSV/Excel** (`src/database/csv_excel_writer.py`):
- 同時輸出 CSV 和 Excel 格式
- 便於資料檢視與對照
- 支援讀取 CSV 作為時間參考

### 技術特點

#### 1. 模組化設計
- 各功能模組獨立，易於維護與擴充
- 清晰的依賴關係
- 便於單元測試
- 職責清晰分離

#### 2. 錯誤處理
- 完整的異常捕捉
- 詳細的錯誤日誌
- 友善的錯誤提示
- 警告機制（多物種、缺少 Camera_ID 等）

#### 3. 日誌系統
- 自動產生日誌檔案到 `logs/` 資料夾
- 格式：`logs/exif_agent_YYYYMMDD_HHMMSS.log`
- 記錄所有重要操作
- 支援不同等級的日誌（INFO、WARNING、ERROR、CRITICAL）
- UTF-8 編碼支援中文

#### 4. 彈性配置
- 支援 config.txt 設定檔
- 可透過 GUI 或手動修改
- 設定即時儲存
- 命令列參數覆蓋設定檔

### 相依套件

主要套件：
- **PyQt6** (>=6.6.0): GUI 框架
- **PaddleOCR** (>=2.7.0): OCR 文字辨識
- **paddlepaddle** (>=2.5.0): PaddleOCR 後端
- **Pillow** (>=10.0.0): 影像處理
- **exifread** (>=3.0.0): EXIF 資訊讀取
- **pandas** (>=2.1.0): 資料處理
- **openpyxl** (>=3.1.0): Excel 檔案操作
- **pyodbc** (>=5.0.0): Access DB 連接
- **python-dotenv**: 環境變數管理

### 使用情境範例

#### 情境 1: 大量照片批次處理
```bash
python cli.py -i D:\Photos\2024_Wildlife -o D:\Output
```

#### 情境 2: 設定較長的時間間隔
```bash
python cli.py -i D:\Photos -o D:\Output --time-interval 60
```

#### 情境 3: 只產生 CSV/Excel（跳過 Access DB）
```bash
python cli.py -i D:\Photos -o D:\Output --skip-access
```

#### 情境 4: 已有 CSV 時間參考
1. 將 CSV 檔案放在照片資料夾中
2. 命名為與資料夾同名（如 `100RECNX.csv`）
3. 執行處理，系統會優先使用 CSV 時間

### 已知限制與注意事項

#### 1. Access DB 支援
- ⚠️ Windows Only
- ⚠️ 需要安裝 Microsoft Access Database Engine
- ⚠️ 32/64 位元需與 Python 版本匹配

#### 2. OCR 辨識
- ⏱️ PaddleOCR 首次執行需下載模型（約 10-20 MB）
- 📷 辨識準確度受照片品質影響
- 💡 建議準備 CSV 參考檔案以確保時間準確

#### 3. 效能考量
- 🐌 大量照片處理較耗時
- 🔍 OCR 處理速度較慢
- 💻 建議使用命令列模式進行大批次處理

#### 4. 標籤格式要求
- 📋 必須使用 Adobe Bridge 的 HierarchicalSubject 格式
- 🔤 Camera_ID 前綴必須為英文字母（如 JC38，不可 12JC）
- ⚠️ 缺少 Species 標籤的照片會被跳過
- ✅ 支援多物種標籤，自動產生多筆記錄

## 🔄 更新記錄

### v2.0.0 (2025-10-30)
- 🆕 從 tkinter 升級到 PyQt6 介面
- 🆕 新增 PaddleOCR 支援（替代 Tesseract）
- 🆕 **支援多物種標籤處理** - 同一張照片可產生多筆記錄
- 🆕 新增 CSV/Excel 同步輸出
- 🔧 修正 Date/Time 欄位資料類型問題
- 🔧 改進錯誤處理和日誌系統
- 📚 新增完整中文文件

## 📚 技術支援

### 日誌檔案位置
所有日誌自動儲存到：
```
logs/exif_agent_YYYYMMDD_HHMMSS.log
```

### 錯誤代碼說明
- **INFO**: 一般資訊訊息
- **WARN**: 警告訊息，程式繼續執行（如多物種標籤、缺少 Camera_ID）
- **ERROR**: 錯誤訊息，該檔案處理失敗但程式繼續
- **CRITICAL**: 嚴重錯誤，程式可能中斷

### 除錯步驟
1. 查看最新的日誌檔案：`logs/exif_agent_YYYYMMDD_HHMMSS.log`
2. 檢查 config.txt 設定是否正確
3. 確認照片的 EXIF 資訊和標籤格式
4. 驗證 Access Database Engine 是否正確安裝
5. 參考原始文件：`doc/exif2accessDB(EXIF轉換資料表).docx`

### 改進建議與回饋
如有功能建議或遇到問題，請：
- 📋 記錄詳細的錯誤訊息和操作步驟
- 📁 保留相關的日誌檔案
- 🖼️ 提供問題照片的範例（如涉及 EXIF 或 OCR 問題）

## 📄 授權

本專案為野生動物研究專用工具，僅供內部使用。

---

**維護者**: EXIF Agent 開發者 Panda
**最後更新**: 2025-10-30
**版本**: v2.0.0

**特別感謝**：本專案基於原始 tkinter 版本重建，感謝所有研究人員的回饋與建議。

