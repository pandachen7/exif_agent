# -*- coding: utf-8 -*-
"""
PyQt6 主視窗介面
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QFileDialog, QMessageBox, QProgressBar, QSpinBox, QGroupBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from src.utils.config import Config
from src.utils.logger import get_logger


logger = get_logger()


class ProcessThread(QThread):
    """處理執行緒"""
    progress = pyqtSignal(str)  # 進度訊息
    finished = pyqtSignal(bool, str)  # 完成訊號 (成功, 訊息)

    def __init__(self, processor, input_path, output_path, access_db_path, excel_path, csv_path):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
        self.access_db_path = access_db_path
        self.excel_path = excel_path
        self.csv_path = csv_path

    def run(self):
        """執行處理"""
        try:
            self.progress.emit(f"開始處理目錄: {self.input_path}")

            # 處理照片
            records = self.processor.process_directory(self.input_path)

            if not records:
                self.finished.emit(False, "沒有找到任何可處理的檔案")
                return

            self.progress.emit(f"找到 {len(records)} 筆記錄")

            # 儲存到 CSV
            from src.database.csv_excel_writer import CSVExcelWriter
            writer = CSVExcelWriter()

            self.progress.emit("儲存到 CSV...")
            writer.write_to_csv(records, self.csv_path)

            # 儲存到 Excel
            self.progress.emit("儲存到 Excel...")
            writer.write_to_excel(records, self.excel_path)

            # 儲存到 Access DB
            try:
                from src.database.access_db import AccessDB
                self.progress.emit("儲存到 Access DB...")

                with AccessDB(self.access_db_path) as db:
                    db.insert_records_batch(records)

                self.progress.emit("Access DB 儲存完成")
            except Exception as e:
                self.progress.emit(f"Access DB 儲存失敗: {str(e)}")
                self.progress.emit("請確認已安裝 Microsoft Access Database Engine")

            # 顯示警告訊息
            warnings = self.processor.get_warnings()
            if warnings:
                self.progress.emit("\n===== 警告訊息 =====")
                for warning in warnings[:10]:  # 只顯示前 10 個警告
                    self.progress.emit(warning)
                if len(warnings) > 10:
                    self.progress.emit(f"... 還有 {len(warnings) - 10} 個警告")

            self.finished.emit(True, f"處理完成！共處理 {len(records)} 筆記錄")

        except Exception as e:
            logger.error(f"處理失敗: {str(e)}", exc_info=True)
            self.finished.emit(False, f"處理失敗: {str(e)}")


class MainWindow(QMainWindow):
    """主視窗"""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.process_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化介面"""
        self.setWindowTitle("EXIF Agent - 照片資訊管理系統")
        self.setGeometry(100, 100, 900, 700)

        # 主要 widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 路徑設定區
        path_group = QGroupBox("路徑設定")
        path_layout = QVBoxLayout()
        path_group.setLayout(path_layout)

        # 輸入路徑
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("輸入資料夾:"))
        self.input_path_edit = QLineEdit(self.config.path_input)
        input_layout.addWidget(self.input_path_edit)
        self.input_browse_btn = QPushButton("瀏覽...")
        self.input_browse_btn.clicked.connect(self.browse_input_path)
        input_layout.addWidget(self.input_browse_btn)
        path_layout.addLayout(input_layout)

        # 輸出路徑
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("輸出資料夾:"))
        self.output_path_edit = QLineEdit(self.config.path_output)
        output_layout.addWidget(self.output_path_edit)
        self.output_browse_btn = QPushButton("瀏覽...")
        self.output_browse_btn.clicked.connect(self.browse_output_path)
        output_layout.addWidget(self.output_browse_btn)
        path_layout.addLayout(output_layout)

        layout.addWidget(path_group)

        # 處理設定區
        settings_group = QGroupBox("處理設定")
        settings_layout = QHBoxLayout()
        settings_group.setLayout(settings_layout)

        # 時間間隔
        settings_layout.addWidget(QLabel("時間間隔 (分鐘):"))
        self.time_interval_spin = QSpinBox()
        self.time_interval_spin.setMinimum(1)
        self.time_interval_spin.setMaximum(1440)  # 最大 24 小時
        self.time_interval_spin.setValue(self.config.time_interval)
        self.time_interval_spin.setToolTip("用於計算有效照片數的時間間隔")
        settings_layout.addWidget(self.time_interval_spin)

        # OCR 引擎選擇
        settings_layout.addWidget(QLabel("OCR 引擎:"))
        self.ocr_combo = QComboBox()
        self.ocr_combo.addItems(["paddle", "tesseract"])
        self.ocr_combo.setCurrentText(self.config.ocr_engine)
        self.ocr_combo.setToolTip("選擇 OCR 辨識引擎")
        settings_layout.addWidget(self.ocr_combo)

        settings_layout.addStretch()
        layout.addWidget(settings_group)

        # 控制按鈕區
        button_layout = QHBoxLayout()

        self.run_btn = QPushButton("開始處理")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.start_processing)
        button_layout.addWidget(self.run_btn)

        self.clear_btn = QPushButton("清空資料表")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_database)
        button_layout.addWidget(self.clear_btn)

        self.save_config_btn = QPushButton("儲存設定")
        self.save_config_btn.setMinimumHeight(40)
        self.save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_config_btn)

        layout.addLayout(button_layout)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 訊息顯示區
        layout.addWidget(QLabel("處理訊息:"))
        self.message_text = QTextEdit()
        self.message_text.setReadOnly(True)
        layout.addWidget(self.message_text)

        # 狀態列
        self.statusBar().showMessage("就緒")

    def browse_input_path(self):
        """選擇輸入資料夾"""
        path = QFileDialog.getExistingDirectory(
            self,
            "選擇輸入資料夾",
            self.input_path_edit.text()
        )
        if path:
            self.input_path_edit.setText(path)

    def browse_output_path(self):
        """選擇輸出資料夾"""
        path = QFileDialog.getExistingDirectory(
            self,
            "選擇輸出資料夾",
            self.output_path_edit.text()
        )
        if path:
            self.output_path_edit.setText(path)

    def save_config(self):
        """儲存設定"""
        self.config.path_input = self.input_path_edit.text()
        self.config.path_output = self.output_path_edit.text()
        self.config.time_interval = self.time_interval_spin.value()
        self.config.ocr_engine = self.ocr_combo.currentText()
        self.config.save_config()

        QMessageBox.information(self, "成功", "設定已儲存")
        self.statusBar().showMessage("設定已儲存", 3000)

    def start_processing(self):
        """開始處理"""
        input_path = self.input_path_edit.text()
        output_path = self.output_path_edit.text()

        # 驗證輸入
        if not input_path:
            QMessageBox.warning(self, "錯誤", "請選擇輸入資料夾")
            return

        if not output_path:
            QMessageBox.warning(self, "錯誤", "請選擇輸出資料夾")
            return

        # 準備處理
        import os
        os.makedirs(output_path, exist_ok=True)

        # 建立輸出檔案路徑
        access_db_path = os.path.join(output_path, self.config.access_db_name)
        excel_path = os.path.join(output_path, self.config.excel_file_name)
        csv_path = os.path.join(output_path, self.config.csv_file_name)

        # 建立處理器
        from src.processor import PhotoProcessor
        processor = PhotoProcessor(
            time_interval=self.time_interval_spin.value(),
            ocr_engine=self.ocr_combo.currentText()
        )

        # 清空訊息
        self.message_text.clear()

        # 建立並啟動執行緒
        self.process_thread = ProcessThread(
            processor, input_path, output_path,
            access_db_path, excel_path, csv_path
        )
        self.process_thread.progress.connect(self.update_progress)
        self.process_thread.finished.connect(self.processing_finished)

        # 禁用按鈕
        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不確定的進度

        self.statusBar().showMessage("處理中...")
        self.process_thread.start()

    def update_progress(self, message: str):
        """更新進度訊息"""
        self.message_text.append(message)
        # 自動捲動到底部
        self.message_text.verticalScrollBar().setValue(
            self.message_text.verticalScrollBar().maximum()
        )

    def processing_finished(self, success: bool, message: str):
        """處理完成"""
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "完成", message)
            self.statusBar().showMessage("處理完成", 5000)
        else:
            QMessageBox.critical(self, "錯誤", message)
            self.statusBar().showMessage("處理失敗", 5000)

        self.update_progress(f"\n{message}")

    def clear_database(self):
        """清空資料表"""
        reply = QMessageBox.question(
            self,
            "確認",
            "確定要清空所有資料表嗎？此操作無法復原！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                import os
                output_path = self.output_path_edit.text()
                access_db_path = os.path.join(output_path, self.config.access_db_name)

                if os.path.exists(access_db_path):
                    from src.database.access_db import AccessDB
                    with AccessDB(access_db_path) as db:
                        db.clear_table("file_record")

                    QMessageBox.information(self, "成功", "資料表已清空")
                    self.statusBar().showMessage("資料表已清空", 3000)
                else:
                    QMessageBox.warning(self, "警告", "找不到資料庫檔案")

            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"清空失敗: {str(e)}")

    def closeEvent(self, event):
        """關閉視窗事件"""
        if self.process_thread and self.process_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "確認",
                "處理尚未完成，確定要關閉嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

            self.process_thread.terminate()

        event.accept()
