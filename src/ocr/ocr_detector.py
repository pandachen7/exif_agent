# -*- coding: utf-8 -*-
"""
OCR 日期偵測模組
支援 PaddleOCR 和 Tesseract
"""
import re
from datetime import datetime
from typing import Optional

from src.utils.logger import getUniqueLogger

logger = getUniqueLogger()


class OCRDetector:
    """OCR 日期偵測器"""

    def __init__(self, engine: str = "paddle"):
        """
        初始化 OCR 偵測器

        Args:
            engine: OCR 引擎，可選 'paddle' 或 'tesseract'
        """
        self.engine = engine.lower()
        self.logger = logger
        self.ocr = None

        if self.engine == "paddle":
            self._init_paddle()
        elif self.engine == "tesseract":
            self._init_tesseract()
        else:
            self.logger.warning(f"Unknown OCR engine: {engine}, using paddle")
            self.engine = "paddle"
            self._init_paddle()

    def _init_paddle(self):
        """初始化 PaddleOCR"""
        try:
            from paddleocr import PaddleOCR

            # 使用英文模型，因為日期主要是數字和英文
            self.ocr = PaddleOCR(
                use_angle_cls=True, lang="en", use_gpu=False, show_log=False
            )
            self.logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            self.ocr = None

    def _init_tesseract(self):
        """初始化 Tesseract OCR"""
        try:
            import pytesseract

            self.ocr = pytesseract
            self.logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tesseract: {str(e)}")
            self.ocr = None

    def detect_datetime_from_image(self, image_path: str) -> Optional[datetime]:
        """
        從圖片中偵測日期時間

        Args:
            image_path: 圖片路徑

        Returns:
            偵測到的日期時間，若失敗則返回 None
        """
        if self.ocr is None:
            self.logger.error("OCR engine not initialized")
            return None

        try:
            if self.engine == "paddle":
                return self._detect_with_paddle(image_path)
            elif self.engine == "tesseract":
                return self._detect_with_tesseract(image_path)
        except Exception as e:
            self.logger.error(f"OCR detection failed for {image_path}: {str(e)}")
            return None

        return None

    def _detect_with_paddle(self, image_path: str) -> Optional[datetime]:
        """使用 PaddleOCR 偵測日期時間"""
        try:
            result = self.ocr.ocr(image_path, cls=True)

            if not result or len(result) == 0:
                return None

            # 收集所有識別到的文字
            text_lines = []
            for line in result[0]:
                if line and len(line) > 1:
                    text = line[1][0]  # line[1][0] 是識別的文字
                    text_lines.append(text)

            # 合併文字並嘗試解析日期
            full_text = " ".join(text_lines)
            self.logger.debug(f"OCR detected text: {full_text}")

            # 嘗試從文字中提取日期時間
            detected_dt = self._parse_datetime_from_text(full_text)

            if detected_dt:
                self.logger.info(f"OCR detected datetime: {detected_dt}")
            else:
                self.logger.warning(
                    f"Could not parse datetime from OCR text: {full_text}"
                )

            return detected_dt

        except Exception as e:
            self.logger.error(f"PaddleOCR detection error: {str(e)}")
            return None

    def _detect_with_tesseract(self, image_path: str) -> Optional[datetime]:
        """使用 Tesseract 偵測日期時間"""
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)

            self.logger.debug(f"OCR detected text: {text}")

            # 嘗試從文字中提取日期時間
            detected_dt = self._parse_datetime_from_text(text)

            if detected_dt:
                self.logger.info(f"OCR detected datetime: {detected_dt}")
            else:
                self.logger.warning(f"Could not parse datetime from OCR text: {text}")

            return detected_dt

        except Exception as e:
            self.logger.error(f"Tesseract detection error: {str(e)}")
            return None

    def _parse_datetime_from_text(self, text: str) -> Optional[datetime]:
        """
        從文字中解析日期時間

        支援多種日期格式:
        - 2020/03/15 15:38:10
        - 2020-03-15 15:38:10
        - 2020/3/15 15:38:10
        - 2020.03.15 15:38:10
        """
        # 常見的日期時間格式
        patterns = [
            # 完整格式: 年/月/日 時:分:秒
            r"(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})",
            # 沒有秒: 年/月/日 時:分
            r"(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})\s+(\d{1,2}):(\d{1,2})",
            # 只有日期: 年/月/日
            r"(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    groups = match.groups()
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])

                    hour = int(groups[3]) if len(groups) > 3 else 0
                    minute = int(groups[4]) if len(groups) > 4 else 0
                    second = int(groups[5]) if len(groups) > 5 else 0

                    dt = datetime(year, month, day, hour, minute, second)

                    # 驗證日期是否合理 (1990-2100 年之間)
                    if 1990 <= dt.year <= 2100:
                        return dt

                except ValueError as e:
                    self.logger.debug(f"Invalid datetime from pattern: {str(e)}")
                    continue

        return None

    def switch_engine(self, engine: str):
        """切換 OCR 引擎"""
        if engine != self.engine:
            self.engine = engine.lower()
            if self.engine == "paddle":
                self._init_paddle()
            elif self.engine == "tesseract":
                self._init_tesseract()
            self.logger.info(f"Switched OCR engine to: {self.engine}")
