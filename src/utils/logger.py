# -*- coding: utf-8 -*-
"""
日誌記錄模組
"""
import logging
import sys
from datetime import datetime


class Logger:
    """日誌管理類別"""

    def __init__(self, name: str = "ExifAgent", log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 清除既有的 handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 設定格式
        formatter = logging.Formatter(
            '%(asctime)s %(name)s:%(lineno)d %(levelname)s  %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (如果有指定 log 檔案)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)


# 全域 logger 實例
_global_logger = None


def get_logger(name: str = "ExifAgent") -> Logger:
    """取得全域 logger 實例"""
    global _global_logger
    if _global_logger is None:
        log_file = f"exif_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        _global_logger = Logger(name, log_file)
    return _global_logger
