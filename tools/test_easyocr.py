from pathlib import Path

import easyocr

reader = easyocr.Reader(["ch_tra", "en"])  # 繁中+英文

folder_path = Path(r"D:\ws\datasets\nchu_forest_imgs\測試照片")
for file in folder_path.iterdir():
    if file.is_file():
        with open(file, 'rb') as f:
            img_bytes = f.read()

        # 直接傳入 bytes 給 readtext
        result = reader.readtext(img_bytes, detail=0)
        print(result)

# 使用re來匹配pattern, 例如找出日期
# date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}'
# for (bbox, text, conf) in result:
#     match = re.search(date_pattern, text)
#     if match:
#         print(match.group())  # 輸出如 2026年02月15日
