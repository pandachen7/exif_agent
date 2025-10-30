# -*- coding: utf-8 -*-
"""
CSV 和 Excel 資料寫入模組
"""
import os
from typing import List, Dict
import pandas as pd
from src.utils.logger import get_logger


logger = get_logger()


class CSVExcelWriter:
    """CSV 和 Excel 資料寫入器"""

    def __init__(self):
        self.logger = logger

    def write_to_csv(self, records: List[Dict], csv_path: str):
        """
        寫入資料到 CSV 檔案

        Args:
            records: 記錄列表
            csv_path: CSV 檔案路徑
        """
        try:
            if not records:
                self.logger.warning("No records to write to CSV")
                return

            # 轉換為 DataFrame
            df = pd.DataFrame(records)

            # 確保目錄存在
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            # 寫入 CSV
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"Written {len(records)} records to CSV: {csv_path}")

        except Exception as e:
            self.logger.error(f"Failed to write CSV: {str(e)}")
            raise

    def write_to_excel(self, records: List[Dict], excel_path: str):
        """
        寫入資料到 Excel 檔案

        Args:
            records: 記錄列表
            excel_path: Excel 檔案路徑
        """
        try:
            if not records:
                self.logger.warning("No records to write to Excel")
                return

            # 轉換為 DataFrame
            df = pd.DataFrame(records)

            # 確保目錄存在
            os.makedirs(os.path.dirname(excel_path), exist_ok=True)

            # 寫入 Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='file_record', index=False)

            self.logger.info(f"Written {len(records)} records to Excel: {excel_path}")

        except Exception as e:
            self.logger.error(f"Failed to write Excel: {str(e)}")
            raise

    def append_to_csv(self, records: List[Dict], csv_path: str):
        """
        追加資料到 CSV 檔案

        Args:
            records: 記錄列表
            csv_path: CSV 檔案路徑
        """
        try:
            if not records:
                return

            df_new = pd.DataFrame(records)

            # 如果檔案存在，讀取並合併
            if os.path.exists(csv_path):
                df_existing = pd.read_csv(csv_path, encoding='utf-8-sig')
                df = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df = df_new

            # 寫入
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"Appended {len(records)} records to CSV: {csv_path}")

        except Exception as e:
            self.logger.error(f"Failed to append to CSV: {str(e)}")
            raise

    def read_csv_datetime(self, csv_path: str) -> Dict[str, str]:
        """
        從 CSV 檔案讀取檔名與時間的對應

        Args:
            csv_path: CSV 檔案路徑

        Returns:
            檔名 -> CreateDate 的對應字典
        """
        try:
            if not os.path.exists(csv_path):
                return {}

            df = pd.read_csv(csv_path, encoding='utf-8-sig')

            # 尋找 Filename 和 CreateDate 欄位
            filename_col = None
            datetime_col = None

            for col in df.columns:
                col_lower = col.lower()
                if 'filename' in col_lower or '檔名' in col_lower:
                    filename_col = col
                if 'createdate' in col_lower or 'datetime' in col_lower or '時間' in col_lower:
                    datetime_col = col

            if not filename_col or not datetime_col:
                self.logger.warning(f"CSV {csv_path} missing required columns")
                return {}

            # 建立對應字典
            result = {}
            for _, row in df.iterrows():
                filename = str(row[filename_col])
                datetime_str = str(row[datetime_col])
                if filename and datetime_str and datetime_str != 'nan':
                    result[filename] = datetime_str

            self.logger.info(f"Read {len(result)} datetime entries from CSV: {csv_path}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to read CSV: {str(e)}")
            return {}
