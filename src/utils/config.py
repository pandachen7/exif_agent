# -*- coding: utf-8 -*-
"""
配置檔案讀取模組
"""
import os
import configparser
from typing import Dict, Any


class Config:
    """配置管理類別"""

    def __init__(self, config_file: str = "config.txt"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """讀取配置檔案"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self.create_default_config()

    def create_default_config(self):
        """建立預設配置檔案"""
        self.config['Path'] = {
            'PathInput': '',
            'PathOutput': './output'
        }

        self.config['Processing'] = {
            'DefaultTimeInterval': '30',
            'OCREngine': 'paddle',
            'DebugMode': 'False'
        }

        self.config['Database'] = {
            'AccessDBName': 'exif_data.accdb',
            'ExcelFileName': 'exif_data.xlsx',
            'CSVFileName': 'exif_data.csv'
        }

        self.save_config()

    def save_config(self):
        """儲存配置到檔案"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """取得配置值"""
        return self.config.get(section, key, fallback=fallback)

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """取得整數配置值"""
        return self.config.getint(section, key, fallback=fallback)

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """取得布林配置值"""
        return self.config.getboolean(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: str):
        """設定配置值"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)

    @property
    def path_input(self) -> str:
        return self.get('Path', 'PathInput', '')

    @path_input.setter
    def path_input(self, value: str):
        self.set('Path', 'PathInput', value)

    @property
    def path_output(self) -> str:
        return self.get('Path', 'PathOutput', './output')

    @path_output.setter
    def path_output(self, value: str):
        self.set('Path', 'PathOutput', value)

    @property
    def time_interval(self) -> int:
        return self.get_int('Processing', 'DefaultTimeInterval', 30)

    @time_interval.setter
    def time_interval(self, value: int):
        self.set('Processing', 'DefaultTimeInterval', str(value))

    @property
    def ocr_engine(self) -> str:
        return self.get('Processing', 'OCREngine', 'paddle')

    @ocr_engine.setter
    def ocr_engine(self, value: str):
        self.set('Processing', 'OCREngine', value)

    @property
    def debug_mode(self) -> bool:
        return self.get_bool('Processing', 'DebugMode', False)

    @property
    def access_db_name(self) -> str:
        return self.get('Database', 'AccessDBName', 'exif_data.accdb')

    @property
    def excel_file_name(self) -> str:
        return self.get('Database', 'ExcelFileName', 'exif_data.xlsx')

    @property
    def csv_file_name(self) -> str:
        return self.get('Database', 'CSVFileName', 'exif_data.csv')
