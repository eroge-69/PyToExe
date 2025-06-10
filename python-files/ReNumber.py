import os
import argparse

def main():
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description='Переименование файлов в 5-значные номера (00001, 00002...)')
    parser.add_argument('-s', '--start', type=int, default=1,
                      help='Начальный номер (по умолчанию: 1)')
    args = parser.parse_args()

    # Получаем список файлов (исключая папки и сам скрипт)
    files = [f for f in os.listdir() if os.path.isfile(f) and f != os.path.basename(__file__)]
    
    if not files:
        print("Файлы для переименования не найдены.")
        return

    # Сортируем файлы по имени
    files.sort()

    # Показываем план переименования
    print("План переименования:")
    for i, filename in enumerate(files, start=args.start):
        print(f"{filename} -> {i:05d}{os.path.splitext(filename)[1]}")

    # Подтверждение
    if input("\nПродолжить? (y/n): ").lower() != 'y':
        print("Отменено.")
        return

    # Выполняем переименование
    success = 0
    for i, filename in enumerate(files, start=args.start):
        new_name = f"{i:05d}{os.path.splitext(filename)[1]}"
        
        try:
            os.rename(filename, new_name)
            print(f"{filename} -> {new_name}")
            success += 1
        except Exception as e:
            print(f"Ошибка: {filename} не переименован ({str(e)})")

    print(f"\nГотово! Переименовано {success} из {len(files)} файлов.")

if __name__ == "__main__":
    main()