# -*- coding: utf-8 -*-
"""
SQLite 資料庫操作模組
"""
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from src.utils.logger import getUniqueLogger

logger = getUniqueLogger()


class SQLiteDB:
    """SQLite 資料庫管理類別"""

    def __init__(self, db_path: str):
        """
        初始化 SQLite DB

        Args:
            db_path: SQLite DB 檔案路徑
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.logger = logger

    def connect(self):
        """連接到 SQLite 資料庫"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.logger.info(f"Connected to SQLite DB: {self.db_path}")

            # 確保資料表存在
            self._ensure_tables_exist()

        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect to SQLite DB: {str(e)}")
            raise

    def _ensure_tables_exist(self):
        """確保所有需要的資料表都存在"""
        self._create_file_record_table()

    def _create_file_record_table(self):
        """建立 file_record 資料表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS file_record (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            SourceFile TEXT,
            DateTimeOriginal TEXT,
            Date TEXT,
            Time TEXT,
            Site TEXT,
            Plot_ID TEXT,
            Camera_ID TEXT,
            "Group" TEXT,
            Species TEXT,
            Number INTEGER,
            Note TEXT,
            IndependentPhoto INTEGER,
            CreateDate TEXT,
            period_start TEXT,
            period_end TEXT
        )
        """
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create file_record table: {str(e)}")

    def insert_record(self, record: Dict):
        """
        插入一筆記錄

        Args:
            record: 記錄字典
        """
        try:
            sql = """
            INSERT INTO file_record
            (SourceFile, DateTimeOriginal, Date, Time, Site, Plot_ID, Camera_ID,
             "Group", Species, Number, Note, IndependentPhoto, CreateDate,
             period_start, period_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            values = (
                record.get("SourceFile"),
                self._format_datetime(record.get("DateTimeOriginal")),
                self._format_datetime(record.get("Date")),
                self._format_datetime(record.get("Time")),
                record.get("Site"),
                record.get("Plot_ID"),
                record.get("Camera_ID"),
                record.get("Group"),
                record.get("Species"),
                record.get("Number", 1),
                record.get("Note", ""),
                record.get("IndependentPhoto", 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self._format_datetime(record.get("period_start")),
                self._format_datetime(record.get("period_end")),
            )

            self.cursor.execute(sql, values)
            self.connection.commit()

        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert record: {str(e)}")
            raise

    def insert_records_batch(self, records: List[Dict]):
        """
        批次插入多筆記錄

        Args:
            records: 記錄列表
        """
        for record in records:
            self.insert_record(record)

        self.logger.info(f"Inserted {len(records)} records into SQLite")

    def clear_table(self, table_name: str = "file_record"):
        """
        清空資料表

        Args:
            table_name: 資料表名稱
        """
        try:
            sql = f"DELETE FROM {table_name}"
            self.cursor.execute(sql)
            self.connection.commit()
            self.logger.info(f"Cleared table: {table_name}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to clear table {table_name}: {str(e)}")

    def close(self):
        """關閉資料庫連接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.logger.info("Closed SQLite DB connection")

    def __enter__(self):
        """支援 with 語句"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支援 with 語句"""
        self.close()

    @staticmethod
    def _format_datetime(dt) -> str:
        """將 datetime 物件轉換為字串"""
        if dt is None:
            return None
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return str(dt)
