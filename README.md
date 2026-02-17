# EXIF Agent - 照片 EXIF 資訊管理系統

這是一個用於處理自動相機照片的 EXIF 資訊提取、OCR 日期辨識以及資料儲存的專業工具。專為野生動物研究和生態調查設計，可自動處理大量相機陷阱照片，提取物種資訊並計算 OI (Occurrence Index) 值。

## 核心功能

### 1. EXIF 資訊提取
- 自動讀取照片和影片的完整 EXIF 元數據
- 解析 Adobe Bridge 的 HierarchicalSubject 標籤
- **支援多物種標記**：同一張照片可標記多個物種，自動產生多筆記錄
- 自動識別相機站點（Site）、樣點編號（Plot_ID）、相機編號（Camera_ID）

### 2. 多重日期時間來源
按優先順序自動選擇最準確的時間資訊：
1. **CSV 參考檔案** - 最準確的時間來源
2. **EXIF CreateDate** - 照片內嵌的拍攝時間
3. **OCR 辨識** - 使用 EasyOCR 辨識照片上的日期戳記
4. **前一筆記錄** - 連續檔案使用相近時間
5. **預設值** - 2000/1/1（最後手段）

### 3. 資料處理
- **有效照片計算**：根據時間間隔（預設30分鐘）自動計算獨立事件
- **多物種處理**：自動偵測並分離同張照片中的不同物種記錄
- **資料驗證**：自動過濾無效資料（如 unknown 物種）
- **警告提示**：缺少 Camera_ID 或發現多物種時自動警告

### 4. 多格式資料儲存
- **Access Database** (.accdb) - 完整的關聯式資料庫（可在 config 中開關）
- **SQLite** (.sqlite) - 跨平台輕量資料庫，無需安裝額外驅動（可在 config 中開關）
- **Excel** (.xlsx) - 方便檢視和編輯
- **CSV** (.csv) - 通用格式，易於匯入其他系統

## 硬體建議

### nvidia
建議可用的顯卡 RTX 2060 / 3060 / 4060, VRAM各為 6 / 12 / 8 GB  
VRAM愈大可開的batch愈高, 如果VRAM較低, 那麼嘗試在cfg把batch設小一點

### intel XPU
[2026.2] 現在這個時間點應該還不支援使用torch的xpu版本用在easyocr  
因此使用cpu純跑也可, 速度會稍慢, 可能是GPU的5倍時間?

## 系統需求

- Python 3.12 或更高版本
- Windows 10/11（Access DB 支援）
- 4GB RAM 以上（建議 8GB）
- 支援純 CPU 或 NVIDIA GPU 環境

## 快速開始

### 安裝步驟

1. **clone 或下載專案**
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

4. **（NVIDIA GPU 使用者）先安裝 PyTorch GPU 版**

> **重要**：如果你的電腦有 NVIDIA 顯示卡，**務必先安裝 GPU 版 PyTorch**，再安裝其他套件。
> 否則 EasyOCR 會自動安裝 CPU 版 PyTorch，無法利用 GPU 加速。

```bash
# 確認你的 CUDA 版本（在 cmd 執行 nvidia-smi 查看右上角 CUDA Version）
# 例如 CUDA 12.6
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

常見 CUDA 版本對應：
| CUDA 版本 | 安裝指令 |
|-----------|---------|
| CUDA 11.8 | `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118` |
| CUDA 12.1 | `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121` |
| CUDA 12.4 | `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124` |
| CUDA 12.6 | `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126` |
| 純 CPU | 不需要這一步，直接到下一步 |

[參考]  
https://www.notion.so/PyTorch-30936ed5d3d680ceb0e1ed1dc8c2c7bf?source=copy_link

5. **安裝相依套件**
```bash
pip install -r requirements.txt
```

> 純 CPU 環境直接執行此步驟即可，EasyOCR 會自動以 CPU 模式運行。

6. **（可選）安裝 Tesseract OCR 作為備用引擎**

Tesseract 是備用的 OCR 引擎，僅在 EasyOCR 無法使用時才需要。

```bash
pip install pytesseract
```

另外需安裝 Tesseract 執行檔：
- Windows：從 [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki) 下載安裝
- 安裝後將路徑加入系統 PATH，或在程式中指定路徑

## 使用方式

### 方式一：圖形化介面（推薦）

```bash
python main.py
```

**操作步驟：**
1. 選擇輸入資料夾（包含照片的目錄）
2. 選擇輸出資料夾（儲存結果）
3. 設定時間間隔（預設 30 分鐘）
4. 選擇 OCR 引擎（預設 EasyOCR）
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

## 資料準備

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

## 輸出資料說明

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
- **OI 最大值限制**：當 `oi_max_one: true` 時，同一張照片即使包含多種動物，對 OI 的貢獻最多為 1；設為 `false` 則依照實際物種數計算

## 設定檔案

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
  ocr_engine: "easyocr"           # OCR 引擎（easyocr / tesseract）
  oi_max_one: true                # 同一照片多物種時 OI 最大值為 1（false = 依實際個數）
  debug_mode: false               # 除錯模式

# 資料庫設定
database:
  save_access_db: true                   # 是否儲存到 Access DB（true/false）
  save_sqlite: true                      # 是否儲存到 SQLite（true/false）
  access_db_name: "exif_data.accdb"
  sqlite_db_name: "exif_data.sqlite"
  excel_file_name: "exif_data.xlsx"
  csv_file_name: "exif_data.csv"
```

> Access DB 和 SQLite 檔案存放在專案的 `db/` 目錄；CSV 和 Excel 存放在設定的 output 目錄。

也可以從範本檔案開始：
```bash
cp cfg/config.yaml.template cfg/config.yaml
```

### OCR 引擎選擇

**EasyOCR**（預設推薦）：
- 準確率高、支援多語言
- 自動偵測 NVIDIA GPU 加速（有 GPU 時自動啟用）
- 純 CPU 環境也可正常運行
- 首次執行會自動下載模型

**Tesseract**（備用方案）：
- 傳統 OCR 引擎
- 需另外安裝 `pytesseract` 套件與 Tesseract 執行檔
- 僅在 EasyOCR 無法使用時作為備選

## 故障排除

### 常見問題

#### 1. Access DB 連接失敗
**錯誤訊息**：`[Microsoft][ODBC Driver Manager] Data source name not found`

**解決方法**：
1. 下載並安裝 [Microsoft Access Database Engine 2016](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
2. 選擇與 Python 版本相符的位元版本（32/64 位元）
3. 如已安裝 Office，確認版本相容性

#### 2. EasyOCR 模型下載失敗
**問題**：網路連接問題導致模型下載失敗

**解決方法**：
```bash
# 手動測試 EasyOCR 是否正常
python -c "import easyocr; reader = easyocr.Reader(['en']); print('OK')"
```

#### 3. GPU 未被偵測到
**問題**：已安裝 NVIDIA 顯示卡但 EasyOCR 使用 CPU

**解決方法**：
```bash
# 確認 PyTorch 是否偵測到 GPU
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# 如果顯示 CUDA: False，重新安裝 GPU 版 PyTorch
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

#### 4. PyQt6 介面無法啟動
**錯誤**：`Could not find the Qt platform plugin "windows"`

**解決方法**：
```bash
# 重新安裝 PyQt6
pip uninstall PyQt6 PyQt6-Qt6
pip install PyQt6
```

#### 5. OCR 辨識率低
**問題**：照片上的日期文字模糊或位置不標準

**解決方法**：
- 準備 CSV 參考檔案提供準確時間
- 調整照片品質或重新拍攝

### 效能優化建議

1. **處理大量照片**（>10,000 張）
   - 使用命令列模式（比 GUI 快）
   - 分批處理不同資料夾
   - 關閉不需要的功能（如 --skip-access）

2. **加速 OCR 處理**
   - 使用 NVIDIA GPU 可大幅加速 EasyOCR
   - 確保照片日期戳記清晰
   - 統一日期戳記位置

## 開發者資訊

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
│   │   ├── sqlite_db.py    # SQLite 操作
│   │   └── csv_excel_writer.py # CSV/Excel 寫入
│   └── utils/              # 工具模組
│       ├── config.py       # 配置管理
│       └── logger.py       # 日誌記錄
│
├── db/                     # 資料庫檔案資料夾
│   ├── exif_data.accdb     # Access 資料庫
│   ├── exif_data.sqlite    # SQLite 資料庫（自動建立）
│   └── exif_data_替換用空檔案.accdb  # 空白 Access 模板
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
| `sqlite_db.py` | SQLite 操作 | `SQLiteDB.insert_records_batch()` |
| `csv_excel_writer.py` | CSV/Excel 輸出 | `CSVExcelWriter.write_to_excel()` |
| `main_window.py` | PyQt6 介面 | `MainWindow`, `ProcessThread` |

### 相依套件

主要套件：
- **PyQt6** (>=6.6.0): GUI 框架
- **EasyOCR**: OCR 文字辨識（預設引擎）
- **Pillow** (>=10.0.0): 影像處理
- **exifread** (>=3.0.0): EXIF 資訊讀取
- **pandas** (>=2.1.0): 資料處理
- **openpyxl** (>=3.1.0): Excel 檔案操作
- **pyodbc** (>=5.0.0): Access DB 連接
- **python-dotenv**: 環境變數管理

選用套件：
- **pytesseract**: Tesseract OCR 介面（備用 OCR 引擎）
- **torch + torchvision** (GPU 版): NVIDIA GPU 加速

### 已知限制與注意事項

#### 1. Access DB 支援
- Windows Only
- 需要安裝 Microsoft Access Database Engine
- 32/64 位元需與 Python 版本匹配
- 微軟自家的One Drive不支援開啟AccessDB
- 可以上傳到Google Drive, 然後用外掛程式 `MDB ACCDB Viewer and Reader` 來看
- 也可用 MDB Viewer Tool (https://mdbviewer.herokuapp.com/) 線上觀看
- 或者用 MDB Viewer Plus (http://www.alexnolan.net/software/mdb_viewer_plus.htm) 在本地端看
  這個也需要安裝 Microsoft Access Database Engine

#### 2. OCR 辨識
- EasyOCR 首次執行需下載模型
- 辨識準確度受照片品質影響
- 建議準備 CSV 參考檔案以確保時間準確

#### 3. GPU 加速
- 僅支援 NVIDIA GPU（CUDA）
- 需先安裝 GPU 版 PyTorch，再安裝其他套件
- 純 CPU 環境也完全可用，只是 OCR 速度較慢

#### 4. 標籤格式要求
- 必須使用 Adobe Bridge 的 HierarchicalSubject 格式
- Camera_ID 前綴必須為英文字母（如 JC38，不可 12JC）
- 缺少 Species 標籤的照片會被跳過
- 支援多物種標籤，自動產生多筆記錄

## 更新記錄

### v2.1.2 (2026-02-17)
- 新增 `oi_max_one` 設定：同一照片多物種時，OI 貢獻最大值為 1 或依實際個數計算
- 預設 `true`（限制最大值為 1），可在 `cfg/config.yaml` 中設為 `false` 改用實際個數

### v2.1.1 (2026-02-17)
- 新增 SQLite 資料庫輸出，跨平台免驅動
- Access DB 和 SQLite 統一存放於 `db/` 目錄
- `cfg/config.yaml` 新增 `save_access_db` / `save_sqlite` 開關，可個別啟用或停用

### v2.1.0 (2026-02-16)
- 移除 PaddleOCR，改用 EasyOCR 作為預設 OCR 引擎
- 支援 NVIDIA GPU 加速（自動偵測）
- 純 CPU 環境也可正常運行

### v2.0.0 (2025-10-30)
- 從 tkinter 升級到 PyQt6 介面
- **支援多物種標籤處理** - 同一張照片可產生多筆記錄
- 新增 CSV/Excel 同步輸出
- 修正 Date/Time 欄位資料類型問題
- 改進錯誤處理和日誌系統

## 技術支援

### 日誌檔案位置
所有日誌自動儲存到：
```
logs/exif_agent_YYYYMMDD_HHMMSS.log
```

### 除錯步驟
1. 查看最新的日誌檔案：`logs/exif_agent_YYYYMMDD_HHMMSS.log`
2. 檢查 `cfg/config.yaml` 設定是否正確
3. 確認照片的 EXIF 資訊和標籤格式
4. 驗證 Access Database Engine 是否正確安裝
5. 參考原始文件：`doc/exif2accessDB(EXIF轉換資料表).docx`

## 授權

MIT
本專案為野生動物研究專用工具，僅供內部使用。

---

**開發維護**: Panda  
**版本**: v2.1.2

過去的文件可參考  
https://docs.google.com/document/d/1T9Ed9F1_3lZvY6rEwUN98xR7Bdo0RptoqBX9KmdtfJ8/edit?usp=sharing

**特別感謝**：本專案基於原始 tkinter 版本重建，感謝所有研究人員的回饋與建議。
