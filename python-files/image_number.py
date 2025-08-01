from PIL import Image
import pytesseract
import re

# اگر ویندوز استفاده می‌کنی و Tesseract نصب شده، این خط را فعال کن و مسیر درست را وارد کن
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# مسیر فایل تصویر
image_path = 'number_image.png'

# باز کردن تصویر
image = Image.open(image_path)

# استخراج متن از تصویر
extracted_text = pytesseract.image_to_string(image, config='--psm 6 digits')

# پیدا کردن فقط اعداد از متن
numbers = re.findall(r'\d+', extracted_text)

# چاپ نتیجه
if numbers:
    print("عدد تشخیص داده شده:", numbers[0])
else:
    print("هیچ عددی تشخیص داده نشد.")
