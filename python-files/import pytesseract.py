import pytesseract
from PIL import Image
import re
import os

# Путь к папке с изображениями
image_folder = 'path/to/your/images'

# Убедитесь, что tesseract установлен и указан путь к нему
# Например: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Функция для извлечения количества
def extract_quantity_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='rus')
    match = re.search(r'Вы можете купить:\s*(\d+)\s*шт', text)
    if match:
        return int(match.group(1))
    return None

# Пройтись по всем изображениям
for filename in os.listdir(image_folder):
    if filename.endswith((".png", ".jpg", ".jpeg")):
        full_path = os.path.join(image_folder, filename)
        quantity = extract_quantity_from_image(full_path)
        print(f"{filename}: {quantity}")
