# -*- coding: utf-8 -*-
"""
照片處理核心模組
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.database.csv_excel_writer import CSVExcelWriter
from src.exif.exif_reader import ExifReader
from src.ocr.ocr_detector import OCRDetector
from src.utils.logger import getUniqueLogger

logger = getUniqueLogger()


class PhotoProcessor:
    """照片處理器"""

    def __init__(self, time_interval: int = 30, ocr_engine: str = "paddle"):
        """
        初始化處理器

        Args:
            time_interval: 時間間隔(分鐘)，用於計算有效照片數
            ocr_engine: OCR 引擎
        """
        self.time_interval = time_interval
        self.exif_reader = ExifReader()
        self.ocr_detector = OCRDetector(ocr_engine)
        self.csv_writer = CSVExcelWriter()
        self.logger = logger

        # 儲存處理過的資料
        self.records = []
        self.warnings = []

    def process_directory(self, directory: str) -> List[Dict]:
        """
        處理目錄下的所有照片

        Args:
            directory: 目錄路徑

        Returns:
            處理後的記錄列表
        """
        self.logger.info(f"Processing directory: {directory}")

        # 清空之前的資料
        self.records = []
        self.warnings = []

        # 掃描所有檔案
        files = self.exif_reader.scan_directory(directory)

        if not files:
            self.logger.warning(f"No supported files found in {directory}")
            return []

        # 尋找 CSV 時間參考檔案
        csv_datetime_map = self._find_csv_datetime_reference(directory)

        # 處理每個檔案
        file_records = []
        for i, file_path in enumerate(files):
            self.logger.info(
                f"Processing file {i+1}/{len(files)}: {os.path.basename(file_path)}"
            )

            result = self._process_single_file(
                file_path, csv_datetime_map, file_records
            )

            if result:
                # result 現在是列表（可能包含多筆記錄）
                file_records.extend(result)

        # 計算每個資料夾的時間範圍
        self._calculate_period_ranges(file_records, directory)

        # 計算有效照片數
        self._calculate_independent_photos(file_records)

        self.records = file_records
        self.logger.info(f"Processed {len(file_records)} files successfully")

        return self.records

    def _find_csv_datetime_reference(self, directory: str) -> Dict[str, str]:
        """尋找 CSV 時間參考檔案"""
        csv_datetime_map = {}

        # 尋找與資料夾同名的 CSV 檔
        folder_name = os.path.basename(directory)
        csv_path = os.path.join(directory, f"{folder_name}.csv")

        if os.path.exists(csv_path):
            self.logger.info(f"Found CSV reference file: {csv_path}")
            csv_datetime_map = self.csv_writer.read_csv_datetime(csv_path)
        else:
            # 尋找第一個 CSV 檔
            for file in os.listdir(directory):
                if file.lower().endswith(".csv"):
                    csv_path = os.path.join(directory, file)
                    self.logger.info(f"Using CSV reference file: {csv_path}")
                    csv_datetime_map = self.csv_writer.read_csv_datetime(csv_path)
                    break

        return csv_datetime_map

    def _process_single_file(
        self,
        file_path: str,
        csv_datetime_map: Dict[str, str],
        previous_records: List[Dict],
    ) -> Optional[List[Dict]]:
        """
        處理單一檔案（可能產生多筆記錄）

        Args:
            file_path: 檔案路徑
            csv_datetime_map: CSV 時間對應
            previous_records: 之前處理過的記錄

        Returns:
            處理後的記錄列表（如果有多個動物標籤）或單一記錄
        """
        filename = os.path.basename(file_path)

        # 1. 讀取 EXIF 資訊
        exif_data = self.exif_reader.read_exif(file_path)

        # 2. 決定日期時間 (優先順序: CSV > EXIF > OCR > 前一筆)
        datetime_original = self._determine_datetime(
            filename, exif_data, csv_datetime_map, file_path, previous_records
        )

        if not datetime_original:
            self.logger.warning(
                f"Could not determine datetime for {filename}, using 2000/1/1"
            )
            datetime_original = datetime(2000, 1, 1)

        # 3. 檢查是否有多個動物標籤
        if exif_data.get("has_multiple_animals"):
            # 有多個動物標籤，產生多筆記錄
            records = []
            multiple_animals = exif_data.get("multiple_animals", [])

            warning = f"WARN: {filename} has {len(multiple_animals)} animal tags"
            self.warnings.append(warning)
            self.logger.warning(warning)

            for animal in multiple_animals:
                record = {
                    "SourceFile": filename,
                    "DateTimeOriginal": datetime_original,
                    "Date": datetime_original,  # Access DB 需要完整的 datetime 物件
                    "Time": datetime_original,  # Access DB 需要完整的 datetime 物件
                    "Site": exif_data.get("Site"),
                    "Plot_ID": exif_data.get("Plot_ID"),
                    "Camera_ID": exif_data.get("Camera_ID"),
                    "Group": animal.get("Group", ""),
                    "Species": animal.get("Species", ""),
                    "Number": animal.get("Number", 1),
                    "Note": "",
                    "IndependentPhoto": 0,
                    "period_start": None,
                    "period_end": None,
                }

                # 檢查是否缺少 Camera_ID
                if not record["Camera_ID"]:
                    if filename not in [
                        w for w in self.warnings if "no Camera_ID" in w
                    ]:
                        warning = f"WARN: {filename} has no Camera_ID tag"
                        self.warnings.append(warning)
                        self.logger.warning(warning)

                # 只加入有效的記錄（有 Species 且不是 unknown）
                if record["Species"] and record["Species"].lower() != "unknown":
                    records.append(record)
                else:
                    self.logger.info(
                        f"Skipping {filename} - {animal}: no valid species tag"
                    )

            return records if records else None

        else:
            # 單一動物標籤，正常處理
            record = {
                "SourceFile": filename,
                "DateTimeOriginal": datetime_original,
                "Date": datetime_original,  # Access DB 需要完整的 datetime 物件
                "Time": datetime_original,  # Access DB 需要完整的 datetime 物件
                "Site": exif_data.get("Site"),
                "Plot_ID": exif_data.get("Plot_ID"),
                "Camera_ID": exif_data.get("Camera_ID"),
                "Group": exif_data.get("Group"),
                "Species": exif_data.get("Species"),
                "Number": exif_data.get("Number", 1),
                "Note": "",
                "IndependentPhoto": 0,
                "period_start": None,
                "period_end": None,
            }

            # 檢查是否缺少 Camera_ID
            if not record["Camera_ID"]:
                warning = f"WARN: {filename} has no Camera_ID tag"
                self.warnings.append(warning)
                self.logger.warning(warning)

            # 如果沒有 Species 或 Species 為 unknown，則忽略
            if not record["Species"] or record["Species"].lower() == "unknown":
                self.logger.info(f"Skipping {filename}: no valid species tag")
                return None

            return [record]  # 返回列表格式以保持一致性

    def _determine_datetime(
        self,
        filename: str,
        exif_data: Dict,
        csv_datetime_map: Dict[str, str],
        file_path: str,
        previous_records: List[Dict],
    ) -> Optional[datetime]:
        """
        決定檔案的日期時間

        優先順序:
        1. CSV 檔案
        2. EXIF CreateDate
        3. OCR 偵測
        4. 使用前一筆記錄的時間
        """
        # 1. 檢查 CSV
        if filename in csv_datetime_map:
            try:
                dt = self._parse_datetime_string(csv_datetime_map[filename])
                if dt:
                    self.logger.debug(f"Using CSV datetime for {filename}: {dt}")
                    return dt
            except Exception as e:
                self.logger.warning(
                    f"Failed to parse CSV datetime for {filename}: {str(e)}"
                )

        # 2. 檢查 EXIF
        if exif_data.get("DateTimeOriginal"):
            return exif_data["DateTimeOriginal"]

        # 3. 使用 OCR
        self.logger.warning(f"{filename} has no EXIF CreateDate, using OCR")
        try:
            dt = self.ocr_detector.detect_datetime_from_image(file_path)
            if dt:
                self.logger.warning(f"OCR result: {dt}")
                return dt
            else:
                self.logger.warning(f"OCR failed for {filename}")
        except Exception as e:
            self.logger.error(f"OCR error for {filename}: {str(e)}")

        # 4. 使用前一筆記錄
        if previous_records:
            prev_dt = previous_records[-1]["DateTimeOriginal"]
            self.logger.warning(f"Using previous datetime for {filename}: {prev_dt}")
            return prev_dt

        return None

    def _parse_datetime_string(self, datetime_str: str) -> Optional[datetime]:
        """
        解析日期時間字串

        支援格式:
        - 2020/6/22 09:40:5
        - 2020/06/22 09:40
        - 2020:06:22 09:40:12
        """
        import re

        # 清理字串
        datetime_str = datetime_str.strip()

        # 替換冒號為斜線 (處理 2020:06:22 格式)
        datetime_str = re.sub(
            r"^(\d{4}):(\d{1,2}):(\d{1,2})", r"\1/\2/\3", datetime_str
        )

        # 解析格式
        formats = [
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue

        return None

    def _calculate_period_ranges(self, records: List[Dict], directory: str):
        """計算時間範圍"""
        if not records:
            return

        # 按照 Camera_ID 分組
        camera_groups = {}
        for record in records:
            camera_id = record.get("Camera_ID", "Unknown")
            if camera_id not in camera_groups:
                camera_groups[camera_id] = []
            camera_groups[camera_id].append(record)

        # 計算每組的時間範圍
        for camera_id, group_records in camera_groups.items():
            # 排序
            group_records.sort(key=lambda x: x["DateTimeOriginal"])

            # 設定範圍
            period_start = group_records[0]["DateTimeOriginal"]
            period_end = group_records[-1]["DateTimeOriginal"]

            self.logger.info(
                f"Camera {camera_id} period: {period_start} ~ {period_end}"
            )

            # 更新所有記錄
            for record in group_records:
                record["period_start"] = period_start
                record["period_end"] = period_end

    def _calculate_independent_photos(self, records: List[Dict]):
        """
        計算有效照片數

        根據時間間隔，同一物種在指定時間內只算一張有效照片
        """
        if not records:
            return

        # 按照 Camera_ID 和 Species 分組
        groups = {}
        for record in records:
            key = (record.get("Camera_ID"), record.get("Species"))
            if key not in groups:
                groups[key] = []
            groups[key].append(record)

        # 計算每組的有效照片數
        for key, group_records in groups.items():
            # 排序
            group_records.sort(key=lambda x: x["DateTimeOriginal"])

            # 第一張總是有效的
            if group_records:
                group_records[0]["IndependentPhoto"] = 1

            # 計算後續的
            last_independent_time = group_records[0]["DateTimeOriginal"]

            for i in range(1, len(group_records)):
                current_time = group_records[i]["DateTimeOriginal"]
                time_diff = current_time - last_independent_time

                # 如果時間差超過間隔，則為有效照片
                if time_diff >= timedelta(minutes=self.time_interval):
                    group_records[i]["IndependentPhoto"] = 1
                    last_independent_time = current_time
                else:
                    group_records[i]["IndependentPhoto"] = 0

    def get_warnings(self) -> List[str]:
        """取得警告訊息列表"""
        return self.warnings
