import os
import sys
from PIL import Image, ImageDraw

# Поддерживаемые расширения
SUPPORTED_EXTS = {'.png', '.jpg', '.jpeg', '.bmp'}

def process_image(filepath):
    """Обрабатывает один файл изображения"""
    try:
        img = Image.open(filepath)
        # Обработка разных цветовых режимов
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode == 'P':
            img = img.convert('RGBA')
            background = Image.new('RGB', img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Закрашиваем верхние 50 пикселей
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, img.width, 50], fill='black')

        # Перезаписываем оригинал
        img.save(filepath, quality=95)
        print(f"✅ {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка с {os.path.basename(filepath)}: {e}")
        return False

def process_folder(folder):
    """Обрабатывает все подходящие файлы в папке"""
    processed = 0
    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext in SUPPORTED_EXTS:
            filepath = os.path.join(folder, filename)
            if process_image(filepath):
                processed += 1
    return processed

def main():
    if len(sys.argv) < 2:
        print("Перетащите сюда файлы или папки с изображениями.")
        input()
        return

    total_processed = 0
    for item in sys.argv[1:]:
        if os.path.isdir(item):
            print(f"\nОбрабатываю папку: {item}")
            count = process_folder(item)
            total_processed += count
        elif os.path.isfile(item):
            ext = os.path.splitext(item)[1].lower()
            if ext in SUPPORTED_EXTS:
                print(f"\nОбрабатываю файл: {item}")
                if process_image(item):
                    total_processed += 1
            else:
                print(f"⚠️ Пропущен (неподдерживаемый формат): {item}")
        else:
            print(f"⚠️ Не найдено: {item}")

    print(f"\nГотово! Всего обработано: {total_processed} файлов.")
    input("\nНажмите Enter, чтобы закрыть...")

if __name__ == "__main__":
    main()