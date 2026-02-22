from pathlib import Path

import easyocr

from ocr.ocr_detector import OCRDetector


def use_easyocr(input_path: str):
    reader = easyocr.Reader(["ch_tra", "en"])  # 繁中+英文

    print("\n=== 原easyOCR測試 ===")

    folder_path = Path(input_path)
    for file in folder_path.iterdir():
        if not file.is_file():
            continue

        with open(file, "rb") as f:
            img_bytes = f.read()
        # 直接傳入 bytes 給 readtext
        result = reader.readtext(img_bytes, detail=0)
        print(result)


def ocr_for_camera_trap(input_path: str):
    detector = OCRDetector(engine="easyocr")

    print("\n=== OCR 偵測策略測試 ===")
    folder_path = Path(input_path)
    for file in folder_path.iterdir():
        if not file.is_file():
            continue
        dt = detector.detect_datetime_from_image(str(file))
        print(f"{file.name}: {dt}")


if __name__ == "__main__":
    input_path = r"D:\ws\datasets\nchu_forest_imgs\測試照片"
    use_easyocr(input_path)
    ocr_for_camera_trap(input_path)
