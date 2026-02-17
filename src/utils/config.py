# -*- coding: utf-8 -*-
"""
配置模組 — 使用 Pydantic BaseModel 多階層定義，模組層級單一實例 cfg
"""
import os

from pydantic import BaseModel
from ruamel.yaml import YAML

CONFIG_FILE = "cfg/config.yaml"


# ── 子層 Model ──────────────────────────────────────────────

class PathConfig(BaseModel):
    input: str = ""
    output: str = "./output"


class ProcessingConfig(BaseModel):
    default_time_interval: int = 30
    ocr_engine: str = "easyocr"
    oi_max_one: bool = True


class DatabaseConfig(BaseModel):
    save_access_db: bool = True
    save_sqlite: bool = True
    access_db_name: str = "exif_data.accdb"
    sqlite_db_name: str = "exif_data.sqlite"
    excel_file_name: str = "exif_data.xlsx"
    csv_file_name: str = "exif_data.csv"


# ── 頂層 Model ──────────────────────────────────────────────

class AppConfig(BaseModel):
    path: PathConfig = PathConfig()
    processing: ProcessingConfig = ProcessingConfig()
    database: DatabaseConfig = DatabaseConfig()

    # ── I/O ──

    def save(self, config_file: str = CONFIG_FILE):
        """儲存配置到 YAML 檔案"""
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        yaml = YAML()
        yaml.default_flow_style = False
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f)

    def reload(self, config_file: str = CONFIG_FILE):
        """從 YAML 重新載入配置（就地更新）"""
        fresh = _load_from_yaml(config_file)
        # 用新值覆蓋所有欄位
        for field in self.__class__.model_fields:
            setattr(self, field, getattr(fresh, field))


# ── 載入邏輯 ────────────────────────────────────────────────

def _load_from_yaml(config_file: str = CONFIG_FILE) -> AppConfig:
    """從 YAML 檔案載入，若檔案不存在則建立預設值"""
    if os.path.exists(config_file):
        yaml = YAML()
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.load(f) or {}
        return AppConfig.model_validate(data)

    # 檔案不存在 → 建立預設
    config = AppConfig()
    config.save(config_file)
    return config


# ── 模組層級單一實例 ─────────────────────────────────────────

cfg: AppConfig = _load_from_yaml()
