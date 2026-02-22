# -*- coding: utf-8 -*-
"""
EXIF 資訊讀取模組 - 使用 exiftool 讀取完整 EXIF / XMP / IPTC 資訊
"""
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import exiftool

from utils.logger import getUniqueLogger

log = getUniqueLogger(__file__)


class ExifReader:
    """EXIF 資訊讀取器 (基於 exiftool)"""

    # 支援的圖片格式
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
    # 支援的影片格式
    VIDEO_EXTENSIONS = {".avi", ".mov", ".mp4", ".mpg", ".mpeg"}

    # DateTimeOriginal 的候選 key (依優先順序)
    _DATETIME_KEYS = [
        "EXIF:DateTimeOriginal",
        "EXIF:CreateDate",
        "EXIF:DateTimeDigitized",
        "XMP:DateTimeOriginal",
        "XMP:CreateDate",
    ]

    _DT_FORMATS = [
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]

    def __init__(self):
        pass

    def is_supported_file(self, file_path: str) -> bool:
        """檢查檔案是否為支援的格式"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.IMAGE_EXTENSIONS or ext in self.VIDEO_EXTENSIONS

    def read_exif(self, file_path: str) -> Dict:
        """
        讀取檔案的 EXIF 資訊

        Returns:
            包含 EXIF 資訊的字典, 額外包含:
            - missing_fields: list[str]  缺失的必要欄位名稱
        """
        if not os.path.exists(file_path):
            log.error(f"File not found: {file_path}")
            return {}

        filename = os.path.basename(file_path)

        exif_data = {
            "SourceFile": filename,
            "FilePath": file_path,
            "DateTimeOriginal": None,
            "CreateDate": None,
            "Subject": None,
            "HierarchicalSubject": None,
            "Camera_ID": None,
            "Site": None,
            "Plot_ID": None,
            "Group": None,
            "Species": None,
            "Number": 1,
            "missing_fields": [],
        }

        try:
            with exiftool.ExifToolHelper(encoding="utf-8") as et:
                meta = et.get_metadata(file_path)[0]

            # 提取日期時間
            dt = self._extract_datetime(meta)
            if dt:
                exif_data["DateTimeOriginal"] = dt
                exif_data["CreateDate"] = dt
            else:
                exif_data["missing_fields"].append("DateTimeOriginal")

            # 提取 XMP 標籤資訊
            self._extract_xmp_tags(meta, exif_data)

        except Exception as e:
            log.error(f"Error reading EXIF from {file_path}: {str(e)}")

        return exif_data

    def _extract_datetime(self, meta: Dict) -> Optional[datetime]:
        """從 exiftool metadata 中依優先順序提取日期時間"""
        for key in self._DATETIME_KEYS:
            value = meta.get(key)
            if not value:
                continue
            dt = self._parse_datetime_value(str(value))
            if dt:
                return dt
        return None

    def _parse_datetime_value(self, dt_str: str) -> Optional[datetime]:
        """嘗試多種格式解析日期時間字串"""
        if not dt_str:
            return None
        # 去掉尾巴的時區偏移 (如 +08:00)
        cleaned = re.sub(r"[+-]\d{2}:\d{2}$", "", dt_str.strip())
        for fmt in self._DT_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
        return None

    def _extract_xmp_tags(self, meta: Dict, exif_data: Dict):
        """
        提取 XMP 標籤資訊

        根據文件規格，從 HierarchicalSubject 中提取:
        - 1_Site ID -> Camera_ID, Site, Plot_ID
        - 2_Animal -> Group, Species
        - 3_Number -> Number
        """
        # exiftool 會直接回傳 list 或 string
        subject = meta.get("XMP:Subject")
        hierarchical_subject = meta.get("XMP:HierarchicalSubject")

        exif_data["Subject"] = subject
        exif_data["HierarchicalSubject"] = hierarchical_subject

        if hierarchical_subject:
            self._parse_hierarchical_subject(hierarchical_subject, exif_data)
        else:
            # 沒有 HierarchicalSubject -> 所有衍生欄位都缺失
            exif_data["missing_fields"].append("HierarchicalSubject")
            exif_data["missing_fields"].append("Camera_ID (1_Site ID)")
            exif_data["missing_fields"].append("Species (2_Animal)")

    def _parse_hierarchical_subject(self, hierarchical_subject, exif_data: Dict):
        """
        解析 HierarchicalSubject

        格式範例:
          list:   ["1_Site ID|JC38", "2_Animal|Artiodactyla|Muntiacus reevesi", "3_Number|1"]
          string: "1_Site ID|JC38, 2_Animal|Artiodactyla|Muntiacus reevesi, 3_Number|1"
        注意：可能有多個 2_Animal 標籤，需要產生多筆記錄
        """
        try:
            # 統一成 list
            if isinstance(hierarchical_subject, list):
                items = [str(s).strip() for s in hierarchical_subject]
            else:
                items = [s.strip() for s in str(hierarchical_subject).split(",")]

            animal_tags = []
            numbers = []
            found_site = False
            found_animal = False

            for item in items:
                if "1_Site ID|" in item or "1_SiteID|" in item or "1_Site_ID|" in item:
                    found_site = True
                    parts = item.split("|")
                    if len(parts) >= 2:
                        camera_id = parts[-1].strip()
                        exif_data["Camera_ID"] = camera_id
                        match = re.match(r"([A-Za-z]+)(\d+)", camera_id)
                        if match:
                            exif_data["Site"] = match.group(1)
                            exif_data["Plot_ID"] = match.group(2)

                elif "2_Animal|" in item:
                    found_animal = True
                    parts = item.split("|")
                    animal_info = {}
                    if len(parts) >= 3:
                        animal_info["Group"] = parts[-2].strip()
                        animal_info["Species"] = parts[-1].strip()
                    elif len(parts) == 2:
                        animal_info["Group"] = ""
                        animal_info["Species"] = parts[-1].strip()

                    if (
                        animal_info.get("Species")
                        and animal_info["Species"].lower() != "unknown"
                    ):
                        animal_tags.append(animal_info)

                elif "3_Number|" in item:
                    parts = item.split("|")
                    if len(parts) >= 2:
                        number_str = parts[-1].strip()
                        if number_str.startswith(">"):
                            number_str = number_str[1:]
                        try:
                            numbers.append(int(number_str))
                        except ValueError:
                            numbers.append(1)

            # 偵測缺失欄位
            if not found_site:
                exif_data["missing_fields"].append("Camera_ID (1_Site ID)")
            if not found_animal:
                exif_data["missing_fields"].append("Species (2_Animal)")
            elif not animal_tags:
                # 有 2_Animal 但全部是 unknown
                exif_data["missing_fields"].append("Species (all unknown)")

            # 處理動物標籤
            if len(animal_tags) > 1:
                exif_data["multiple_animals"] = animal_tags
                exif_data["has_multiple_animals"] = True
                for i, animal in enumerate(animal_tags):
                    animal["Number"] = numbers[i] if i < len(numbers) else 1
                log.info(f"Found {len(animal_tags)} animal tags in HierarchicalSubject")
            elif len(animal_tags) == 1:
                exif_data["Group"] = animal_tags[0].get("Group", "")
                exif_data["Species"] = animal_tags[0].get("Species", "")
                exif_data["Number"] = numbers[0] if numbers else 1
            else:
                exif_data["Number"] = numbers[0] if numbers else 1

        except Exception as e:
            log.warning(f"Error parsing HierarchicalSubject: {str(e)}")

    def scan_directory(self, directory: str) -> List[str]:
        """
        掃描目錄下所有支援的多媒體檔案

        Args:
            directory: 目錄路徑

        Returns:
            檔案路徑列表
        """
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if self.is_supported_file(file_path):
                    files.append(file_path)

        log.info(f"Found {len(files)} supported files in {directory}")
        return files
