import os
import shutil
import time

# Путь к папке на телефоне
source_path = '/storage/emulated/0/DCIM/Camera/'

# Путь к папке на компьютере
destination_path = 'C:\Users\Ilkin222\Videos'

# Проверка существования папки на компьютере
if not os.path.exists(destination_path):
    os.makedirs(destination_path)

# Бесконечный цикл для мониторинга папки на телефоне
while True:
    # Получение списка файлов в папке на телефоне
    files = os.listdir(source_path)

    # Проверка наличия новых файлов
    for file in files:
        # Проверка расширения файла
        if file.endswith('.mp4') or file.endswith('.mov'):
            # Путь к файлу на телефоне
            source_file = os.path.join(source_path, file)

            # Путь к файлу на компьютере
            destination_file = os.path.join(destination_path, file)

            # Копирование файла
            shutil.copy2(source_file, destination_file)

            # Удаление файла с телефона (опционально)
            os.remove(source_file)

    # Пауза перед следующей итерацией
    time.sleep(5)