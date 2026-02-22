"""
EXIF 資訊載入工具 - 使用 exiftool 讀取完整的 EXIF / XMP / IPTC 資訊

輸出欄位對應 file_record 資料表:
  SourceFile, DateTimeOriginal, Date, Time,
  Site, Plot_ID, Camera_ID, Group, Species, Number, Note
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import exiftool

# 支援的檔案格式
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
VIDEO_EXTENSIONS = {".avi", ".mov", ".mp4", ".mpg", ".mpeg"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


# ---------------------------------------------------------------------------
# 核心: 使用 exiftool 讀取完整 metadata
# ---------------------------------------------------------------------------


def get_full_metadata(image_path: str) -> dict:
    """使用 exiftool 讀取完整 metadata (回傳原始 dict)"""
    with exiftool.ExifToolHelper(encoding="utf-8") as et:
        meta = et.get_metadata(image_path)[0]
    return meta


# ---------------------------------------------------------------------------
# DateTimeOriginal 提取
# ---------------------------------------------------------------------------

_DATETIME_KEYS = [
    "EXIF:DateTimeOriginal",
    "EXIF:CreateDate",
    "EXIF:DateTimeDigitized",
    "XMP:DateTimeOriginal",
    "XMP:CreateDate",
    "File:FileModifyDate",
]

_DT_FORMATS = [
    "%Y:%m:%d %H:%M:%S",  # 2020:03:15 15:38:10
    "%Y-%m-%d %H:%M:%S",  # 2020-03-15 15:38:10
    "%Y/%m/%d %H:%M:%S",  # 2020/03/15 15:38:10
    "%Y:%m:%d %H:%M:%S%z",  # with timezone
    "%Y-%m-%dT%H:%M:%S",  # ISO
    "%Y-%m-%dT%H:%M:%S%z",  # ISO with tz
]


def _parse_datetime(dt_str: str) -> Optional[datetime]:
    """嘗試多種日期格式解析"""
    if not dt_str:
        return None
    # 去掉尾巴的時區偏移 (如 +08:00) 以便 strptime
    cleaned = re.sub(r"[+-]\d{2}:\d{2}$", "", dt_str.strip())
    for fmt in _DT_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def extract_datetime(meta: dict) -> Optional[datetime]:
    """從 metadata 中依優先順序提取 DateTimeOriginal"""
    for key in _DATETIME_KEYS:
        value = meta.get(key)
        if value:
            dt = _parse_datetime(str(value))
            if dt:
                return dt
    return None


# ---------------------------------------------------------------------------
# HierarchicalSubject 解析 (Camera_ID, Site, Plot_ID, Group, Species, Number)
# ---------------------------------------------------------------------------


def _parse_hierarchical_subject(hierarchical_subject) -> dict:
    """
    解析 XMP:HierarchicalSubject

    格式範例:
      ["1_Site ID|JC38", "2_Animal|Artiodactyla|Muntiacus reevesi", "3_Number|1"]
      或逗號分隔字串:
      "1_Site ID|JC38, 2_Animal|Artiodactyla|Muntiacus reevesi, 3_Number|1"

    回傳: {
        "Camera_ID": str, "Site": str, "Plot_ID": str,
        "animal_tags": [{"Group": str, "Species": str, "Number": int}, ...],
        "has_multiple_animals": bool,
    }
    """
    result = {
        "Camera_ID": None,
        "Site": None,
        "Plot_ID": None,
        "animal_tags": [],
        "has_multiple_animals": False,
    }

    # 統一成 list
    if isinstance(hierarchical_subject, str):
        items = [s.strip() for s in hierarchical_subject.split(",")]
    elif isinstance(hierarchical_subject, list):
        items = [str(s).strip() for s in hierarchical_subject]
    else:
        return result

    animal_tags: list[dict] = []
    numbers: list[int] = []

    for item in items:
        # --- 1_Site ID ---
        if "1_Site ID|" in item or "1_SiteID|" in item or "1_Site_ID|" in item:
            parts = item.split("|")
            if len(parts) >= 2:
                camera_id = parts[-1].strip()  # 取最後一段
                result["Camera_ID"] = camera_id
                # Site = 前面的英文字母, Plot_ID = 後面的數字
                match = re.match(r"([A-Za-z]+)(\d+)", camera_id)
                if match:
                    result["Site"] = match.group(1)
                    result["Plot_ID"] = match.group(2)

        # --- 2_Animal ---
        elif "2_Animal|" in item:
            parts = item.split("|")
            animal_info: dict = {}
            if len(parts) >= 3:
                animal_info["Group"] = parts[-2].strip()
                animal_info["Species"] = parts[-1].strip()
            elif len(parts) == 2:
                animal_info["Group"] = ""
                animal_info["Species"] = parts[-1].strip()

            # 過濾 unknown
            species = animal_info.get("Species", "")
            if species and species.lower() != "unknown":
                animal_tags.append(animal_info)

        # --- 3_Number ---
        elif "3_Number|" in item:
            parts = item.split("|")
            if len(parts) >= 2:
                num_str = parts[-1].strip()
                if num_str.startswith(">"):
                    num_str = num_str[1:]
                try:
                    numbers.append(int(num_str))
                except ValueError:
                    numbers.append(1)

    # 將 Number 分配給對應的 animal
    for i, animal in enumerate(animal_tags):
        animal["Number"] = numbers[i] if i < len(numbers) else 1

    result["animal_tags"] = animal_tags
    result["has_multiple_animals"] = len(animal_tags) > 1
    return result


# ---------------------------------------------------------------------------
# Keywords / Tags 提取
# ---------------------------------------------------------------------------

_TAG_KEYS = [
    "IPTC:Keywords",
    "XMP:Subject",
    "XMP:TagsList",
    "EXIF:XPKeywords",
]


def extract_keywords(meta: dict) -> list[str]:
    """從 metadata 中提取 keyword tags"""
    for key in _TAG_KEYS:
        value = meta.get(key)
        if value:
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                return [t.strip() for t in value.split(";") if t.strip()]
    return []


# ---------------------------------------------------------------------------
# 組合: 產生 file_record 等級的結構化資訊
# ---------------------------------------------------------------------------


def build_file_record(image_path: str) -> list[dict]:
    """
    讀取單一檔案, 回傳 file_record 等級的結構化資料.
    如果有多個動物標籤, 會回傳多筆 dict (每個動物一筆).

    回傳欄位:
      SourceFile, DateTimeOriginal, Date, Time,
      Site, Plot_ID, Camera_ID, Group, Species, Number,
      Note, Keywords, HierarchicalSubject (raw)
    """
    meta = get_full_metadata(image_path)

    # --- 日期時間 ---
    dt = extract_datetime(meta)

    # --- HierarchicalSubject ---
    hs_raw = meta.get("XMP:HierarchicalSubject")
    hs_parsed = (
        _parse_hierarchical_subject(hs_raw)
        if hs_raw
        else {
            "Camera_ID": None,
            "Site": None,
            "Plot_ID": None,
            "animal_tags": [],
            "has_multiple_animals": False,
        }
    )

    # --- Keywords ---
    keywords = extract_keywords(meta)

    # --- 基本共用欄位 ---
    base = {
        "SourceFile": Path(image_path).name,
        "DateTimeOriginal": dt,
        "Date": dt.date() if dt else None,
        "Time": dt.time() if dt else None,
        "Site": hs_parsed["Site"],
        "Plot_ID": hs_parsed["Plot_ID"],
        "Camera_ID": hs_parsed["Camera_ID"],
        "Keywords": keywords,
        "HierarchicalSubject": hs_raw,
        "Note": "",
    }

    # --- 依動物標籤展開成多筆記錄 ---
    animals = hs_parsed["animal_tags"]
    if not animals:
        # 沒有有效動物標籤
        record = {**base, "Group": None, "Species": None, "Number": 1}
        return [record]

    records = []
    for animal in animals:
        record = {
            **base,
            "Group": animal.get("Group", ""),
            "Species": animal.get("Species", ""),
            "Number": animal.get("Number", 1),
        }
        records.append(record)

    if hs_parsed["has_multiple_animals"]:
        base["Note"] = f"Multiple animals ({len(animals)})"

    return records


# ---------------------------------------------------------------------------
# 輸出格式化
# ---------------------------------------------------------------------------


def _fmt_record(rec: dict) -> str:
    """格式化單筆 record 為可讀字串"""
    lines = []
    lines.append(f"  SourceFile       : {rec['SourceFile']}")
    lines.append(f"  DateTimeOriginal : {rec['DateTimeOriginal']}")
    lines.append(f"  Date             : {rec['Date']}")
    lines.append(f"  Time             : {rec['Time']}")
    lines.append(f"  Camera_ID        : {rec['Camera_ID']}")
    lines.append(f"  Site             : {rec['Site']}")
    lines.append(f"  Plot_ID          : {rec['Plot_ID']}")
    lines.append(f"  Group            : {rec['Group']}")
    lines.append(f"  Species          : {rec['Species']}")
    lines.append(f"  Number           : {rec['Number']}")
    if rec.get("Note"):
        lines.append(f"  Note             : {rec['Note']}")
    if rec.get("Keywords"):
        lines.append(f"  Keywords         : {rec['Keywords']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 資料夾批次處理
# ---------------------------------------------------------------------------


def treat_files(input_path: str):
    """掃描資料夾, 輸出每個檔案的完整 EXIF 結構化資訊"""
    folder_path = Path(input_path)
    print(f"\n{'='*60}")
    print(f"  Scanning: {folder_path}")
    print(f"{'='*60}\n")

    total_files = 0
    total_records = 0
    warnings: list[str] = []

    for file in sorted(folder_path.iterdir()):
        if not file.is_file():
            continue
        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        total_files += 1
        print(f"--- [{total_files}] {file.name} ---")

        try:
            records = build_file_record(str(file))
            for i, rec in enumerate(records):
                if len(records) > 1:
                    print(f"  [Record {i+1}/{len(records)}]")
                print(_fmt_record(rec))
                total_records += 1

            # 警告: 多動物標籤
            if len(records) > 1:
                msg = f"WARN: {file.name} has {len(records)} animal tags -> {len(records)} records"
                warnings.append(msg)
                print(f"  ** {msg}")

            # 警告: 缺少 Camera_ID
            if records and not records[0].get("Camera_ID"):
                msg = f"WARN: {file.name} has no Camera_ID tag"
                warnings.append(msg)
                print(f"  ** {msg}")

            # 警告: 缺少日期時間
            if records and not records[0].get("DateTimeOriginal"):
                msg = f"WARN: {file.name} has no DateTimeOriginal"
                warnings.append(msg)
                print(f"  ** {msg}")

            # 警告: 無有效動物標籤
            if records and not records[0].get("Species"):
                msg = f"WARN: {file.name} has no valid Species tag (will be skipped in DB)"
                warnings.append(msg)
                print(f"  ** {msg}")

        except Exception as e:
            msg = f"ERROR: {file.name} -> {e}"
            warnings.append(msg)
            print(f"  ** {msg}")

        print()

    # --- Summary ---
    print(f"{'='*60}")
    print("  Summary")
    print(f"{'='*60}")
    print(f"  Files scanned : {total_files}")
    print(f"  Records built : {total_records}")
    print(f"  Warnings      : {len(warnings)}")
    if warnings:
        print()
        for w in warnings:
            print(f"  {w}")
    print()


# ---------------------------------------------------------------------------
# 原始 metadata 傾印 (除錯用)
# ---------------------------------------------------------------------------


def dump_raw_metadata(image_path: str):
    """印出完整的 exiftool metadata (除錯用)"""
    meta = get_full_metadata(image_path)
    print(f"\n--- Raw metadata: {Path(image_path).name} ---")
    for key in sorted(meta.keys()):
        print(f"  {key}: {meta[key]}")
    print()


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    input_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else r"D:\ws\datasets\nchu_forest_imgs\測試照片"
    )
    path = Path(input_path)

    if path.is_dir():
        treat_files(input_path)
    elif path.is_file():
        # 單檔模式: 印出結構化資訊 + 原始 metadata
        records = build_file_record(input_path)
        for i, rec in enumerate(records):
            if len(records) > 1:
                print(f"[Record {i+1}/{len(records)}]")
            print(_fmt_record(rec))
            print()
        dump_raw_metadata(input_path)
    else:
        print(f"Path not found: {input_path}")
        sys.exit(1)
