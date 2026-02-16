# -*- coding: utf-8 -*-
"""
配置檔案讀取模組
"""
import os
from typing import Any

from ruamel.yaml import YAML


class Config:
    """配置管理類別"""

    def __init__(self, config_file: str = "cfg/config.yaml"):
        self.config_file = config_file
        self.config = {}
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.load_config()

    def load_config(self):
        """讀取配置檔案"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = self.yaml.load(f) or {}
        else:
            self.create_default_config()

    def create_default_config(self):
        """建立預設配置檔案"""
        self.config = {
            "path": {"input": "", "output": "./output"},
            "processing": {
                "default_time_interval": 30,
                "ocr_engine": "easyocr",
                "debug_mode": False,
            },
            "database": {
                "save_access_db": True,
                "save_sqlite": True,
                "access_db_name": "exif_data.accdb",
                "sqlite_db_name": "exif_data.sqlite",
                "excel_file_name": "exif_data.xlsx",
                "csv_file_name": "exif_data.csv",
            },
        }
        self.save_config()

    def save_config(self):
        """儲存配置到檔案"""
        # 確保 cfg 資料夾存在
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            self.yaml.dump(self.config, f)

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """取得配置值"""
        return self.config.get(section, {}).get(key, fallback)

    def set(self, section: str, key: str, value: Any):
        """設定配置值"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    @property
    def path_input(self) -> str:
        return self.get("path", "input", "")

    @path_input.setter
    def path_input(self, value: str):
        self.set("path", "input", value)

    @property
    def path_output(self) -> str:
        return self.get("path", "output", "./output")

    @path_output.setter
    def path_output(self, value: str):
        self.set("path", "output", value)

    @property
    def time_interval(self) -> int:
        return int(self.get("processing", "default_time_interval", 30))

    @time_interval.setter
    def time_interval(self, value: int):
        self.set("processing", "default_time_interval", int(value))

    @property
    def ocr_engine(self) -> str:
        return self.get("processing", "ocr_engine", "easyocr")

    @ocr_engine.setter
    def ocr_engine(self, value: str):
        self.set("processing", "ocr_engine", value)

    @property
    def debug_mode(self) -> bool:
        return bool(self.get("processing", "debug_mode", False))

    @property
    def save_access_db(self) -> bool:
        return bool(self.get("database", "save_access_db", True))

    @save_access_db.setter
    def save_access_db(self, value: bool):
        self.set("database", "save_access_db", bool(value))

    @property
    def save_sqlite(self) -> bool:
        return bool(self.get("database", "save_sqlite", True))

    @save_sqlite.setter
    def save_sqlite(self, value: bool):
        self.set("database", "save_sqlite", bool(value))

    @property
    def access_db_name(self) -> str:
        return self.get("database", "access_db_name", "exif_data.accdb")

    @property
    def sqlite_db_name(self) -> str:
        return self.get("database", "sqlite_db_name", "exif_data.sqlite")

    @property
    def excel_file_name(self) -> str:
        return self.get("database", "excel_file_name", "exif_data.xlsx")

    @property
    def csv_file_name(self) -> str:
        return self.get("database", "csv_file_name", "exif_data.csv")
