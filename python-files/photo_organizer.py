import os
import shutil
import csv
from pathlib import Path


def parse_photo_csv(csv_path):
    """
    Парсит CSV-таблицу с фотографиями.
    Возвращает словарь {ФИ: [список фото]}
    """
    people_photos = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Пропускаем заголовок
        for row in reader:
            if len(row) >= 3 and row[1].strip():  # Проверяем, что есть ФИ
                name = row[1].strip()
                photos = []
                if row[2].strip():  # Если есть фотографии
                    # Разделяем по пробелам, удаляем пустые строки и пробелы
                    photos = [p.strip() for p in row[2].split() if p.strip()]
                people_photos[name] = photos
    return people_photos


def copy_photos_for_people(people_photos, source_dir, target_dir, photo_ext='.jpg'):
    """
    Копирует фотографии для каждого человека из исходной в целевую папку
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # Создаем целевую папку, если ее нет
    target_path.mkdir(parents=True, exist_ok=True)

    for name, photos in people_photos.items():
        if not photos:  # Пропускаем людей без фото
            print(f"Нет фото для: {name}")
            continue

        # Создаем подпапку для каждого человека (заменяем запрещенные символы)
        safe_name = name.replace('/', '_').replace('\\', '_')
        person_folder = target_path / safe_name
        person_folder.mkdir(exist_ok=True)

        copied = 0
        for photo in photos:
            # Добавляем расширение, если его нет
            photo_name = photo if '.' in photo else f"{photo}{photo_ext}"
            src_file = source_path / photo_name
            dst_file = person_folder / photo_name

            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                copied += 1
                print(f"Скопировано: {src_file} -> {dst_file}")
            else:
                print(f"Файл не найден: {src_file}")

        print(f"Для {name} скопировано {copied}/{len(photos)} фото")


if __name__ == "__main__":
    # Настройки
    csv_path = "фото.csv"  # Путь к CSV-файлу
    source_directory = "./"  # Папка с исходными фото
    target_directory = "output"  # Целевая папка
    photo_extension = ".JPG"  # Расширение фото (можно изменить на .png и др.)

    print("Начинаем обработку...")

    # Парсим CSV
    try:
        people_data = parse_photo_csv(csv_path)
        print(f"Найдено {len(people_data)} человек с фотографиями")

        # Копируем фотографии
        copy_photos_for_people(people_data, source_directory, target_directory, photo_extension)

        print("\nГотово! Обработаны следующие люди:")
        for name in people_data:
            print(f"- {name}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")