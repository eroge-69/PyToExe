import os
from PIL import Image

def combine_photos(input_folder):
    # Параметры изображений (в сантиметрах и DPI)
    single_width_cm = 9
    total_width_cm = 18
    height_cm = 13
    dpi = 200
    
    # Конвертация размеров в пиксели
    cm_to_inch = 2.54
    single_width_px = int(single_width_cm / cm_to_inch * dpi)
    total_width_px = int(total_width_cm / cm_to_inch * dpi)
    height_px = int(height_cm / cm_to_inch * dpi)
    
    # Поддерживаемые форматы изображений
    image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    # Получаем список изображений в папке
    image_files = [
        f for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f)) and 
        f.lower().endswith(image_exts)
    ]
    image_files.sort()
    
    # Обрабатываем изображения попарно
    for i in range(0, len(image_files), 2):
        if i + 1 >= len(image_files):
            break  # Пропускаем последний файл, если нечетное количество
            
        # Загрузка изображений
        img1 = Image.open(os.path.join(input_folder, image_files[i]))
        img2 = Image.open(os.path.join(input_folder, image_files[i+1]))
        
        # Изменение размера с сохранением пропорций
        img1 = resize_with_padding(img1, single_width_px, height_px)
        img2 = resize_with_padding(img2, single_width_px, height_px)
        
        # Создание нового изображения
        new_img = Image.new('RGB', (total_width_px, height_px), (255, 255, 255))
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (single_width_px, 0))
        
        # Сохранение результата
        output_path = os.path.join(input_folder, f'combined_{i//2 + 1}.jpg')
        new_img.save(output_path, 'JPEG', dpi=(dpi, dpi))
        print(f'Created: {output_path}')

def resize_with_padding(img, target_width, target_height):
    # Создаем новое изображение с белым фоном
    new_img = Image.new('RGB', (target_width, target_height), (255, 255, 255))
    
    # Масштабируем с сохранением пропорций
    img.thumbnail((target_width, target_height))
    
    # Вычисляем позицию для центрирования
    x = (target_width - img.width) // 2
    y = (target_height - img.height) // 2
    
    # Вставляем изображение по центру
    new_img.paste(img, (x, y))
    return new_img

if __name__ == '__main__':
    combine_photos(os.path.dirname(os.path.abspath(__file__)))
    print("Processing completed! Press Enter to exit...")
    input()