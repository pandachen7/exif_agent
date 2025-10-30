# -*- coding: utf-8 -*-
"""
Access DB 資料庫操作模組
"""
import os
from datetime import datetime
from typing import List, Dict
import pyodbc
from src.utils.logger import get_logger


logger = get_logger()


class AccessDB:
    """Access 資料庫管理類別"""

    def __init__(self, db_path: str):
        """
        初始化 Access DB

        Args:
            db_path: Access DB 檔案路徑
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.logger = logger

    def connect(self):
        """連接到 Access 資料庫"""
        try:
            # 如果資料庫不存在，建立新的
            if not os.path.exists(self.db_path):
                self._create_new_database()

            # 建立連接字串
            conn_str = (
                r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
                f'DBQ={self.db_path};'
            )

            self.connection = pyodbc.connect(conn_str)
            self.cursor = self.connection.cursor()
            self.logger.info(f"Connected to Access DB: {self.db_path}")

            # 確保資料表存在
            self._ensure_tables_exist()

        except pyodbc.Error as e:
            self.logger.error(f"Failed to connect to Access DB: {str(e)}")
            raise

    def _create_new_database(self):
        """建立新的 Access 資料庫"""
        try:
            # 使用 ADOX 建立新資料庫
            import win32com.client
            adox = win32com.client.Dispatch('ADOX.Catalog')
            adox.Create(f'Provider=Microsoft.ACE.OLEDB.12.0;Data Source={self.db_path}')
            self.logger.info(f"Created new Access DB: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to create Access DB: {str(e)}")
            # 如果 win32com 不可用，記錄警告
            self.logger.warning("Please create an empty .accdb file manually")
            raise

    def _ensure_tables_exist(self):
        """確保所有需要的資料表都存在"""
        # 檢查 file_record 表是否存在
        try:
            self.cursor.execute("SELECT TOP 1 * FROM file_record")
        except pyodbc.Error:
            # 表不存在，建立它
            self._create_file_record_table()

    def _create_file_record_table(self):
        """建立 file_record 資料表"""
        create_table_sql = """
        CREATE TABLE file_record (
            ID AUTOINCREMENT PRIMARY KEY,
            SourceFile VARCHAR(50),
            DateTimeOriginal DATETIME,
            [Date] DATETIME,
            [Time] DATETIME,
            Site VARCHAR(6),
            Plot_ID VARCHAR(6),
            Camera_ID VARCHAR(6),
            [Group] VARCHAR(20),
            Species VARCHAR(30),
            [Number] INTEGER,
            Note VARCHAR(100),
            IndependentPhoto INTEGER,
            CreateDate DATETIME,
            period_start DATETIME,
            period_end DATETIME
        )
        """
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            self.logger.info("Created file_record table")
        except pyodbc.Error as e:
            self.logger.error(f"Failed to create file_record table: {str(e)}")

    def insert_record(self, record: Dict):
        """
        插入一筆記錄

        Args:
            record: 記錄字典
        """
        try:
            # 準備插入語句
            sql = """
            INSERT INTO file_record
            (SourceFile, DateTimeOriginal, [Date], [Time], Site, Plot_ID, Camera_ID,
             [Group], Species, [Number], Note, IndependentPhoto, CreateDate,
             period_start, period_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # 準備資料
            values = (
                record.get('SourceFile'),
                record.get('DateTimeOriginal'),
                record.get('Date'),
                record.get('Time'),
                record.get('Site'),
                record.get('Plot_ID'),
                record.get('Camera_ID'),
                record.get('Group'),
                record.get('Species'),
                record.get('Number', 1),
                record.get('Note', ''),
                record.get('IndependentPhoto', 0),
                datetime.now(),  # CreateDate
                record.get('period_start'),
                record.get('period_end')
            )

            self.cursor.execute(sql, values)
            self.connection.commit()

        except pyodbc.Error as e:
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

        self.logger.info(f"Inserted {len(records)} records")

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
        except pyodbc.Error as e:
            self.logger.error(f"Failed to clear table {table_name}: {str(e)}")

    def close(self):
        """關閉資料庫連接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.logger.info("Closed Access DB connection")

    def __enter__(self):
        """支援 with 語句"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支援 with 語句"""
        self.close()
