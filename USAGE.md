# EXIF Agent 使用手冊

## 快速開始

### 1. 安裝必要套件

```bash
# 啟動虛擬環境
venv\Scripts\activate

# 安裝套件（如果尚未安裝）
pip install -r requirements.txt
```

### 2. 啟動圖形介面

```bash
python main.py
```

### 3. 使用命令列版本

```bash
python cli.py -i <輸入資料夾> -o <輸出資料夾>
```

## 功能說明

### 主要功能

1. **EXIF 資訊提取**
   - 自動讀取照片和影片的 EXIF 元數據
   - 提取拍攝時間、相機 ID、物種資訊等

2. **日期時間偵測**
   - 優先順序：CSV 參考檔 > EXIF > OCR > 前一筆記錄
   - 支援 PaddleOCR 和 Tesseract 兩種 OCR 引擎

3. **資料儲存**
   - Access DB (.accdb)
   - Excel (.xlsx)
   - CSV (.csv)

4. **有效照片計算**
   - 根據時間間隔計算有效照片數
   - 預設時間間隔：30 分鐘

### 圖形介面操作

1. **路徑設定**
   - 輸入資料夾：選擇包含照片的資料夾
   - 輸出資料夾：選擇儲存結果的資料夾

2. **處理設定**
   - 時間間隔：設定有效照片的時間間隔（分鐘）
   - OCR 引擎：選擇 paddle 或 tesseract

3. **控制按鈕**
   - 開始處理：執行照片處理
   - 清空資料表：清空 Access DB 中的資料
   - 儲存設定：將目前設定儲存到 config.txt

### 命令列選項

```bash
python cli.py -h  # 顯示幫助

選項:
  -i, --input          輸入資料夾路徑（必要）
  -o, --output         輸出資料夾路徑（必要）
  -t, --time-interval  時間間隔（分鐘），預設 30
  --ocr               OCR 引擎選擇（paddle/tesseract），預設 paddle
  --skip-access       跳過 Access DB 儲存
```

## 資料格式

### CSV 參考檔案

如果資料夾中有與資料夾同名的 CSV 檔案，系統會優先使用該檔案中的時間資訊。

CSV 格式要求：
- 必須包含 "Filename" 和 "CreateDate" 欄位
- 時間格式：`2020/06/22 09:40:05` 或 `2020/06/22 09:40`

範例：
```csv
Filename,CreateDate
IMG_0001.JPG,2020/06/22 09:40:05
IMG_0002.JPG,2020/06/22 09:45:12
```

### HierarchicalSubject 標籤格式

Adobe Bridge 標籤格式：
```
1_Site ID|JC38, 2_Animal|Human|Researcher, 3_Number|1
```

解析規則：
- `1_Site ID|{Camera_ID}` → Site（英文部分）+ Plot_ID（數字部分）
- `2_Animal|{Group}|{Species}` → 動物群組和物種
- `3_Number|{Number}` → 個體數量（支援 >N 格式）

## 輸出資料

### file_record 資料表結構

| 欄位名稱 | 說明 |
|---------|------|
| SourceFile | 檔案名稱 |
| DateTimeOriginal | 原始拍攝時間 |
| Date | 日期部分 |
| Time | 時間部分 |
| Site | 樣區代碼 |
| Plot_ID | 樣點編號 |
| Camera_ID | 相機編號（Site + Plot_ID）|
| Group | 動物群組 |
| Species | 物種名稱 |
| Number | 個體數量 |
| Note | 註記 |
| IndependentPhoto | 有效照片標記（0 或 1）|
| CreateDate | 記錄建立時間 |
| period_start | 該相機最早照片時間 |
| period_end | 該相機最晚照片時間 |

## 常見問題

### 1. Access DB 儲存失敗

**錯誤訊息**：`Driver not found`

**解決方法**：
- 安裝 [Microsoft Access Database Engine](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
- 如果已安裝 Office，確認是 32 位元或 64 位元版本與 Python 相符

### 2. OCR 辨識失敗

**可能原因**：
- 照片中的日期字體不清楚
- 日期位置在非標準區域

**建議**：
- 準備 CSV 參考檔案提供準確時間
- 確認照片的 EXIF 資訊是否完整

### 3. 程式執行緩慢

**優化方法**：
- 處理大量照片時，建議先使用命令列版本
- 關閉不需要的功能（如 `--skip-access`）
- 確保 OCR 引擎已正確安裝

## 進階設定

### 修改 config.txt

```ini
[Path]
PathInput = D:\Photos
PathOutput = D:\Output

[Processing]
DefaultTimeInterval = 30
OCREngine = paddle
DebugMode = False

[Database]
AccessDBName = exif_data.accdb
ExcelFileName = exif_data.xlsx
CSVFileName = exif_data.csv
```

### 切換 OCR 引擎

**PaddleOCR**（推薦）：
- 優點：準確率高、支援多語言、無需額外安裝
- 缺點：首次執行需要下載模型

**Tesseract**：
- 優點：傳統 OCR 引擎
- 缺點：需要另外安裝 Tesseract OCR 軟體

## 技術支援

如有問題請查看日誌檔案：
- `exif_agent_YYYYMMDD_HHMMSS.log`

常見錯誤代碼：
- `WARN`: 警告訊息，程式繼續執行
- `ERROR`: 錯誤訊息，該檔案處理失敗
- `CRITICAL`: 嚴重錯誤，程式可能中斷
