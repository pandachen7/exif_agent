# -*- coding: utf-8 -*-
"""
OCR 日期偵測模組
預設使用 EasyOCR，備用 Tesseract
"""
import re
from datetime import datetime
from typing import Optional

import cv2
import numpy as np

from utils.logger import getUniqueLogger

OCR_ALLOWLIST = "0123456789/-:. APMapm"

log = getUniqueLogger(__file__)


class OCRDetector:
    """OCR 日期偵測器"""

    def __init__(self, engine: str = "easyocr"):
        """
        初始化 OCR 偵測器

        Args:
            engine: OCR 引擎，可選 'easyocr' 或 'tesseract'
        """
        self.engine = engine.lower()
        self.ocr = None

        if self.engine == "easyocr":
            self._init_easyocr()
        elif self.engine == "tesseract":
            self._init_tesseract()
        else:
            log.warning(f"Unknown OCR engine: {engine}, using easyocr")
            self.engine = "easyocr"
            self._init_easyocr()

    def _init_easyocr(self):
        """初始化 EasyOCR"""
        try:
            import easyocr

            self.ocr = easyocr.Reader(["en"], gpu=self._check_gpu())
            log.info("EasyOCR initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize EasyOCR: {str(e)}")
            self.ocr = None

    def _check_gpu(self) -> bool:
        """檢查是否有可用的 NVIDIA GPU"""
        try:
            import torch

            available = torch.cuda.is_available()
            if available:
                log.info(f"CUDA GPU detected: {torch.cuda.get_device_name(0)}")
            else:
                log.info("No CUDA GPU detected, using CPU")
            return available
        except ImportError:
            log.info("torch not installed, using CPU")
            return False

    def _init_tesseract(self):
        """初始化 Tesseract OCR"""
        try:
            import pytesseract

            self.ocr = pytesseract
            log.info("Tesseract OCR initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize Tesseract: {str(e)}")
            self.ocr = None

    @staticmethod
    def _preprocess_image(image_path: str) -> list[np.ndarray]:
        """裁切圖片上下 10% 區域，回傳 [bottom_strip, top_strip]"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        h, w = img.shape[:2]

        # 等比縮小到高度 1500
        if h > 1500:
            scale = 1500 / h
            img = cv2.resize(img, (int(w * scale), 1500))
            h, w = img.shape[:2]

        strip_h = max(int(h * 0.1), 50)

        bottom_strip = img[h - strip_h : h, :, :]
        top_strip = img[0:strip_h, :, :]

        return [bottom_strip, top_strip]

    @staticmethod
    def _clean_ocr_text(text: str) -> str:
        """清理 OCR 文字：修正常見錯字、移除無關字元、正規化空白"""
        # OCR 常見錯字修正
        text = text.replace("=", "9")
        text = text.replace("#", ":")

        # 只保留數字、日期時間分隔符、AM/PM 字母
        text = re.sub(r"[^0-9/\-:. APMapm]", "", text)

        # 正規化冒號周圍空白: "02: 50" → "02:50", "09 :30" → "09:30"
        text = re.sub(r"\s*:\s*", ":", text)

        # 壓縮多餘空白
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def detect_datetime_from_image(self, image_path: str) -> Optional[datetime]:
        """
        從圖片中偵測日期時間

        Args:
            image_path: 圖片路徑

        Returns:
            偵測到的日期時間，若失敗則返回 None
        """
        if self.ocr is None:
            log.error("OCR engine not initialized")
            return None

        try:
            if self.engine == "easyocr":
                return self._detect_with_easyocr(image_path)
            elif self.engine == "tesseract":
                return self._detect_with_tesseract(image_path)
        except Exception as e:
            log.error(f"OCR detection failed for {image_path}: {str(e)}")
            return None

        return None

    def _detect_with_easyocr(self, image_path: str) -> Optional[datetime]:
        """使用 EasyOCR 偵測日期時間（裁切上下 10% + 限制字元集）"""
        try:
            strips = self._preprocess_image(image_path)
        except Exception as e:
            log.error(f"Image preprocessing failed: {e}")
            return None

        for idx, strip in enumerate(strips):
            try:
                result = self.ocr.readtext(
                    strip,
                    allowlist=OCR_ALLOWLIST,
                    detail=1,
                    paragraph=False,
                )
                if not result:
                    continue

                text_items = [item[1] for item in result]
                log.debug(f"OCR strip {idx} raw items: {text_items}")

                # 策略 A：逐項解析
                detected_dt = self._parse_datetime_from_items(text_items)
                if detected_dt:
                    log.info(f"OCR detected datetime (items): {detected_dt}")
                    return detected_dt

                # 策略 B：合併 + 清理後整段解析
                cleaned = self._clean_ocr_text(" ".join(text_items))
                detected_dt = self._parse_datetime_from_text(cleaned)
                if detected_dt:
                    log.info(f"OCR detected datetime (joined): {detected_dt}")
                    return detected_dt

            except Exception as e:
                log.error(f"EasyOCR detection error on strip {idx}: {e}")
                continue

        log.warning(f"Could not parse datetime from any strip: {image_path}")
        return None

    def _detect_with_tesseract(self, image_path: str) -> Optional[datetime]:
        """使用 Tesseract 偵測日期時間"""
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)

            log.debug(f"OCR detected text: {text}")

            # 嘗試從文字中提取日期時間
            detected_dt = self._parse_datetime_from_text(text)

            if detected_dt:
                log.info(f"OCR detected datetime: {detected_dt}")
            else:
                log.warning(f"Could not parse datetime from OCR text: {text}")

            return detected_dt

        except Exception as e:
            log.error(f"Tesseract detection error: {str(e)}")
            return None

    def _parse_datetime_from_items(
        self, text_items: list[str]
    ) -> Optional[datetime]:
        """
        從多個 OCR 文字項中解析日期+時間。

        日期和時間可能分屬不同 OCR 文字框，逐一 clean 後分別搜尋。
        """
        # YYYY[-/]MM[-/]DD
        date_ymd = re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})")
        # MM/DD/YYYY
        date_mdy = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
        # 12h: HH:MM[:SS] AM/PM
        time_12h = re.compile(
            r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)", re.IGNORECASE
        )
        # 24h: HH:MM:SS or HH:MM
        time_24h = re.compile(r"(\d{1,2}):(\d{2})(?::(\d{2}))?")

        found_date: Optional[tuple[int, int, int]] = None
        found_time: Optional[tuple[int, int, int]] = None

        for raw in text_items:
            cleaned = self._clean_ocr_text(raw)

            # --- 找日期 ---
            if found_date is None:
                m = date_ymd.search(cleaned)
                if m:
                    found_date = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                else:
                    m = date_mdy.search(cleaned)
                    if m:
                        found_date = (
                            int(m.group(3)),
                            int(m.group(1)),
                            int(m.group(2)),
                        )

            # --- 找時間 ---
            if found_time is None:
                m = time_12h.search(cleaned)
                if m:
                    h = int(m.group(1))
                    mi = int(m.group(2))
                    s = int(m.group(3)) if m.group(3) else 0
                    period = m.group(4).upper()
                    if period == "PM" and h != 12:
                        h += 12
                    elif period == "AM" and h == 12:
                        h = 0
                    found_time = (h, mi, s)
                else:
                    m = time_24h.search(cleaned)
                    if m:
                        found_time = (
                            int(m.group(1)),
                            int(m.group(2)),
                            int(m.group(3)) if m.group(3) else 0,
                        )

        if found_date is None:
            return None

        year, month, day = found_date
        hour, minute, second = found_time if found_time else (0, 0, 0)

        try:
            dt = datetime(year, month, day, hour, minute, second)
            if 1990 <= dt.year <= 2100:
                return dt
        except ValueError as e:
            log.debug(f"Invalid datetime from items: {e}")

        return None

    def _parse_datetime_from_text(self, text: str) -> Optional[datetime]:
        """
        從文字中解析日期時間

        支援多種日期格式:
        - 2020/03/15 15:38:10
        - 2020-03-15 15:38:10
        - MM/DD/YYYY HH:MM:SS AM/PM
        """
        # 先嘗試 item-based 解析
        result = self._parse_datetime_from_items([text])
        if result:
            return result

        # fallback: 原始 regex（向後相容）
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
                    log.debug(f"Invalid datetime from pattern: {str(e)}")
                    continue

        return None

    def switch_engine(self, engine: str):
        """切換 OCR 引擎"""
        if engine != self.engine:
            self.engine = engine.lower()
            if self.engine == "easyocr":
                self._init_easyocr()
            elif self.engine == "tesseract":
                self._init_tesseract()
            log.info(f"Switched OCR engine to: {self.engine}")
