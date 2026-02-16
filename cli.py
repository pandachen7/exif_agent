# -*- coding: utf-8 -*-
"""
EXIF Agent 命令列介面
用於批次處理，不需要 GUI
"""
import argparse
import os
import sys

# 將 src 目錄加入路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.access_db import AccessDB
from src.database.csv_excel_writer import CSVExcelWriter
from src.processor import PhotoProcessor
from src.utils.config import Config
from src.utils.logger import getUniqueLogger


def main():
    """命令列主程式"""
    parser = argparse.ArgumentParser(
        description="EXIF Agent - 照片資訊管理系統 (命令列版)"
    )

    parser.add_argument("-i", "--input", required=True, help="輸入資料夾路徑")
    parser.add_argument("-o", "--output", required=True, help="輸出資料夾路徑")
    parser.add_argument(
        "-t", "--time-interval", type=int, default=30, help="時間間隔(分鐘)，預設 30"
    )
    parser.add_argument(
        "--ocr",
        choices=["easyocr", "tesseract"],
        default="easyocr",
        help="OCR 引擎選擇，預設 easyocr",
    )
    parser.add_argument(
        "--skip-access", action="store_true", help="跳過 Access DB 儲存"
    )

    args = parser.parse_args()

    # 初始化 logger
    logger = getUniqueLogger()
    logger.info("=" * 50)
    logger.info("EXIF Agent CLI 啟動")
    logger.info("=" * 50)

    # 驗證輸入
    if not os.path.exists(args.input):
        logger.error(f"輸入資料夾不存在: {args.input}")
        sys.exit(1)

    # 建立輸出資料夾
    os.makedirs(args.output, exist_ok=True)

    # 建立處理器
    logger.info(f"輸入路徑: {args.input}")
    logger.info(f"輸出路徑: {args.output}")
    logger.info(f"時間間隔: {args.time_interval} 分鐘")
    logger.info(f"OCR 引擎: {args.ocr}")

    processor = PhotoProcessor(time_interval=args.time_interval, ocr_engine=args.ocr)

    # 處理照片
    logger.info("開始處理照片...")
    records = processor.process_directory(args.input)

    if not records:
        logger.warning("沒有找到任何可處理的檔案")
        sys.exit(0)

    logger.info(f"處理完成，共 {len(records)} 筆記錄")

    # 儲存資料
    config = Config()
    writer = CSVExcelWriter()

    # CSV
    csv_path = os.path.join(args.output, config.csv_file_name)
    logger.info(f"儲存到 CSV: {csv_path}")
    writer.write_to_csv(records, csv_path)

    # Excel
    excel_path = os.path.join(args.output, config.excel_file_name)
    logger.info(f"儲存到 Excel: {excel_path}")
    writer.write_to_excel(records, excel_path)

    # Access DB
    if not args.skip_access:
        access_db_path = os.path.join(args.output, config.access_db_name)
        logger.info(f"儲存到 Access DB: {access_db_path}")

        try:
            with AccessDB(access_db_path) as db:
                db.insert_records_batch(records)
            logger.info("Access DB 儲存完成")
        except Exception as e:
            logger.error(f"Access DB 儲存失敗: {str(e)}")
            logger.warning("請確認已安裝 Microsoft Access Database Engine")

    # 顯示警告訊息
    warnings = processor.get_warnings()
    if warnings:
        logger.info("\n" + "=" * 50)
        logger.info("警告訊息:")
        logger.info("=" * 50)
        for warning in warnings:
            logger.warning(warning)

    logger.info("\n" + "=" * 50)
    logger.info("處理完成!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
