# -*- coding: utf-8 -*-
"""
EXIF Agent 主程式
照片 EXIF 資訊管理系統
"""
import os
import sys

# 將 src 目錄加入路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.logger import getUniqueLogger


def main():
    """主程式入口"""
    # 初始化 logger
    logger = getUniqueLogger()
    logger.info("=" * 50)
    logger.info("EXIF Agent 啟動")
    logger.info("=" * 50)

    # 建立應用程式
    app = QApplication(sys.argv)
    app.setApplicationName("EXIF Agent")

    # 建立主視窗
    window = MainWindow()
    window.show()

    # 執行應用程式
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"應用程式錯誤: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
