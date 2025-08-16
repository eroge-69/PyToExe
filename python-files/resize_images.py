from PIL import Image
import os

# Создаем выходную директорию, если её нет
output_dir = "outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Получаем все файлы изображений из текущей директории
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
image_files = []
for file in os.listdir('.'):
    if any(file.lower().endswith(ext) for ext in image_extensions) and os.path.isfile(file):
        image_files.append(file)

# Обрабатываем каждое изображение
for i, file in enumerate(image_files):
    try:
        # Открываем изображение
        img = Image.open(file)
        
        # Принудительно конвертируем в RGB (убираем прозрачность)
        img = img.convert('RGB')
        
        # Получаем размеры изображения
        width, height = img.size
        
        # Определяем новые размеры, сохраняя соотношение сторон
        if width > height:
            # Если ширина больше высоты, устанавливаем ширину = 1024
            new_width = 1024
            new_height = int(height * (new_width / width))
        else:
            # Если высота больше ширины, устанавливаем высоту = 1024
            new_height = 1024
            new_width = int(width * (new_height / height))
        
        # Изменяем размер изображения с сохранением пропорций
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Сохраняем с порядковым номером в формате PNG с максимальным качеством
        output_path = os.path.join(output_dir, f"{i+1:03d}.png")
        resized_img.save(output_path, format='PNG', optimize=True, compress_level=0)
        
        print(f"Обработано {file} -> {output_path} ({new_width}x{new_height})")
        
    except Exception as e:
        print(f"Ошибка при обработке {file}: {e}")

print(f"Завершена обработка {len(image_files)} изображений.")