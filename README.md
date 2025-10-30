# EXIF Agent - 照片 EXIF 資訊管理系統

這是一個用於處理自動相機照片的 EXIF 資訊提取、OCR 日期辨識以及資料儲存的工具。

## 功能特色

- **EXIF 資訊提取**: 自動讀取照片和影片的 EXIF 元數據
- **OCR 日期辨識**: 使用 PaddleOCR 辨識照片中的日期時間資訊
- **多重儲存格式**: 同時儲存到 Access DB 和 CSV/Excel 檔案
- **自動相機資料分析**: 計算有效照片數、相機工作時數、OI 值等
- **圖形化介面**: 使用 PyQt6 建立友善的操作介面

## 系統需求

- Python 3.11+
- Windows 10/11 (Access DB 支援)

## 安裝步驟

1. 建立虛擬環境：
```bash
python -m venv venv
```

2. 啟動虛擬環境：
```bash
venv\Scripts\activate
```

3. 安裝相依套件：
```bash
pip install -r requirements.txt
```

## 使用方式

```bash
python main.py
```

## 專案結構

```
exif_agent/
├── main.py                 # 主程式入口
├── config.txt             # 設定檔
├── requirements.txt       # Python 套件清單
├── src/
│   ├── ui/               # PyQt6 介面模組
│   ├── exif/             # EXIF 處理模組
│   ├── ocr/              # OCR 處理模組
│   ├── database/         # 資料庫處理模組
│   └── utils/            # 工具函數
├── doc/                  # 文件資料夾
└── output/               # 輸出資料夾
```

## 資料庫結構

### file_record 資料表
- SourceFile: 檔案名稱
- DateTimeOriginal: 原始拍攝時間
- Camera_ID: 相機編號
- Site: 樣區代碼
- Plot_ID: 樣點編號
- Group: 動物群組
- Species: 物種名稱
- Number: 個體數量
- IndependentPhoto: 有效照片標記

## 授權

本專案為內部使用工具
