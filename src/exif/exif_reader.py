# -*- coding: utf-8 -*-
"""
EXIF 資訊讀取模組
"""
import os
import re
from datetime import datetime
from typing import Dict, Optional, List
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
from src.utils.logger import get_logger


logger = get_logger()


class ExifReader:
    """EXIF 資訊讀取器"""

    # 支援的圖片格式
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}
    # 支援的影片格式
    VIDEO_EXTENSIONS = {'.avi', '.mov', '.mp4', '.mpg', '.mpeg'}

    def __init__(self):
        self.logger = logger

    def is_supported_file(self, file_path: str) -> bool:
        """檢查檔案是否為支援的格式"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.IMAGE_EXTENSIONS or ext in self.VIDEO_EXTENSIONS

    def read_exif(self, file_path: str) -> Dict:
        """
        讀取檔案的 EXIF 資訊

        Args:
            file_path: 檔案路徑

        Returns:
            包含 EXIF 資訊的字典
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return {}

        exif_data = {
            'SourceFile': os.path.basename(file_path),
            'FilePath': file_path,
            'DateTimeOriginal': None,
            'CreateDate': None,
            'Subject': None,
            'HierarchicalSubject': None,
            'Camera_ID': None,
            'Site': None,
            'Plot_ID': None,
            'Group': None,
            'Species': None,
            'Number': 1
        }

        try:
            # 使用 exifread 讀取更完整的 EXIF 資訊
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)

            # 提取日期時間
            datetime_original = self._extract_datetime(tags)
            if datetime_original:
                exif_data['DateTimeOriginal'] = datetime_original
                exif_data['CreateDate'] = datetime_original

            # 提取 XMP 標籤資訊
            self._extract_xmp_tags(tags, exif_data)

        except Exception as e:
            self.logger.error(f"Error reading EXIF from {file_path}: {str(e)}")

        return exif_data

    def _extract_datetime(self, tags: Dict) -> Optional[datetime]:
        """提取日期時間資訊"""
        # 嘗試多個可能的日期時間標籤
        datetime_tags = [
            'EXIF DateTimeOriginal',
            'EXIF DateTimeDigitized',
            'Image DateTime',
            'EXIF DateTime'
        ]

        for tag_name in datetime_tags:
            if tag_name in tags:
                try:
                    dt_str = str(tags[tag_name])
                    # 將 EXIF 格式轉換為標準格式
                    # 格式: 2020:03:15 15:38:10
                    dt = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
                    return dt
                except ValueError:
                    continue

        return None

    def _extract_xmp_tags(self, tags: Dict, exif_data: Dict):
        """
        提取 XMP 標籤資訊

        根據文件規格，從 HierarchicalSubject 中提取:
        - 1_Site ID -> Camera_ID, Site, Plot_ID
        - 2_Animal -> Group, Species
        - 3_Number -> Number
        """
        # 尋找 Subject 和 HierarchicalSubject
        subject = None
        hierarchical_subject = None

        for tag_key in tags.keys():
            tag_str = str(tag_key).lower()
            if 'subject' in tag_str:
                if 'hierarchical' in tag_str:
                    hierarchical_subject = str(tags[tag_key])
                else:
                    subject = str(tags[tag_key])

        exif_data['Subject'] = subject
        exif_data['HierarchicalSubject'] = hierarchical_subject

        # 解析 HierarchicalSubject
        if hierarchical_subject:
            self._parse_hierarchical_subject(hierarchical_subject, exif_data)

    def _parse_hierarchical_subject(self, hierarchical_subject: str, exif_data: Dict):
        """
        解析 HierarchicalSubject 字串

        格式範例: "1_Site ID|JC38, 2_Animal|Human|Researcher, 3_Number|1"
        """
        try:
            # 分割各個項目
            items = [item.strip() for item in hierarchical_subject.split(',')]

            for item in items:
                if '1_Site ID|' in item or '1_SiteID|' in item:
                    # 提取 Camera ID
                    parts = item.split('|')
                    if len(parts) >= 2:
                        camera_id = parts[1].strip()
                        exif_data['Camera_ID'] = camera_id
                        # 分割 Site 和 Plot_ID
                        # 例如 JC38 -> Site=JC, Plot_ID=38
                        match = re.match(r'([A-Za-z]+)(\d+)', camera_id)
                        if match:
                            exif_data['Site'] = match.group(1)
                            exif_data['Plot_ID'] = match.group(2)

                elif '2_Animal|' in item:
                    # 提取 Group 和 Species
                    parts = item.split('|')
                    if len(parts) >= 3:
                        exif_data['Group'] = parts[1].strip()
                        exif_data['Species'] = parts[2].strip()
                    elif len(parts) == 2:
                        exif_data['Species'] = parts[1].strip()

                elif '3_Number|' in item:
                    # 提取 Number
                    parts = item.split('|')
                    if len(parts) >= 2:
                        number_str = parts[1].strip()
                        # 處理 >N 的情況
                        if number_str.startswith('>'):
                            number_str = number_str[1:]
                        try:
                            exif_data['Number'] = int(number_str)
                        except ValueError:
                            exif_data['Number'] = 1

        except Exception as e:
            self.logger.warning(f"Error parsing HierarchicalSubject: {str(e)}")

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

        self.logger.info(f"Found {len(files)} supported files in {directory}")
        return files
