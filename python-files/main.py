import os
from PIL import Image

# Настройки
DPI = 200
PHOTO_WIDTH_CM = 9
PHOTO_HEIGHT_CM = 13

# Размеры в пикселях
PHOTO_WIDTH_PX = int(PHOTO_WIDTH_CM / 2.54 * DPI)
PHOTO_HEIGHT_PX = int(PHOTO_HEIGHT_CM / 2.54 * DPI)
OUTPUT_WIDTH_PX = PHOTO_WIDTH_PX * 2

# Папка с exe (или py) файлом
folder = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(folder, 'output')
os.makedirs(output_folder, exist_ok=True)

# Получаем все изображения
images = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
images.sort()  # Сортируем для предсказуемости

# Обрабатываем парами
for i in range(0, len(images), 2):
    img1 = Image.open(os.path.join(folder, images[i])).resize((PHOTO_WIDTH_PX, PHOTO_HEIGHT_PX))

    if i + 1 < len(images):
        img2 = Image.open(os.path.join(folder, images[i + 1])).resize((PHOTO_WIDTH_PX, PHOTO_HEIGHT_PX))
    else:
        # Если нечетное количество, вторая половина будет пустой
        img2 = Image.new("RGB", (PHOTO_WIDTH_PX, PHOTO_HEIGHT_PX), color="white")

    # Создаем новый холст
    combined = Image.new("RGB", (OUTPUT_WIDTH_PX, PHOTO_HEIGHT_PX), color="white")
    combined.paste(img1, (0, 0))
    combined.paste(img2, (PHOTO_WIDTH_PX, 0))

    # Сохраняем
    output_path = os.path.join(output_folder, f'combined_{i//2 + 1}.jpg')
    combined.save(output_path, dpi=(DPI, DPI))

print("Готово. Все объединённые изображения находятся в папке 'output'")
