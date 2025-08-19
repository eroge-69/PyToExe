import os
import re
from datetime import datetime, timedelta

path = r"E:\UserData"
games_file = os.path.join(path, "games.txt")
MAX_VALID_INTERVAL = 3600 * 6  # 6 часов - максимальный допустимый интервал между парой скриншотов

def format_time(seconds):
    """Форматирует время в днях, часах, минутах и секундах"""
    td = timedelta(seconds=seconds)
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} дн")
    if hours > 0:
        parts.append(f"{hours} ч")
    if minutes > 0:
        parts.append(f"{minutes} мин")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} сек")
    
    return " ".join(parts)

def extract_time_from_filename(filename, full_path):
    """Извлекает время из имени файла или использует время создания"""
    try:
        # Пытаемся найти любую последовательность из 12 цифр в имени файла
        match = re.search(r"\d{12}", filename)
        if match:
            time_str = match.group(0)
            try:
                # Пробуем разобрать как время в формате ГГММДДЧЧММСС
                return datetime.strptime(time_str, "%y%m%d%H%M%S")
            except ValueError:
                pass
        
        # Если в имени нет 12 цифр или не удалось распарсить - используем время изменения файла
        mod_time = os.path.getmtime(full_path)
        return datetime.fromtimestamp(mod_time)
    except Exception as e:
        print(f"Ошибка при обработке файла {filename}: {e}")
        return None

def process_screenshots(screenshots_path):
    """Обрабатывает скриншоты в папке, вычисляя суммарное время с проверкой валидности интервалов"""
    try:
        valid_screenshots = []
        invalid_files = []
        
        # Собираем все файлы и их временные метки
        for f in os.listdir(screenshots_path):
            full_path = os.path.join(screenshots_path, f)
            if os.path.isfile(full_path) and f.lower().endswith('.bmp'):
                time = extract_time_from_filename(f, full_path)
                if time:
                    valid_screenshots.append((time, f))
                else:
                    invalid_files.append(f)
        
        # Сортируем по времени
        valid_screenshots.sort(key=lambda x: x[0])
        
        print(f"  Найдено файлов: {len(os.listdir(screenshots_path))}")
        print(f"  Валидных скриншотов: {len(valid_screenshots)}")
        if invalid_files:
            print(f"  Нераспознанные файлы: {', '.join(invalid_files[:3])}" + 
                  ("..." if len(invalid_files) > 3 else ""))
        
        if len(valid_screenshots) < 2:
            print("  Недостаточно валидных скриншотов для формирования пар")
            return 0
        
        total_time = 0
        pair_count = 0
        invalid_pairs = 0
        
        # Обрабатываем скриншоты последовательно, проверяя интервалы
        i = 0
        while i < len(valid_screenshots) - 1:
            time1, file1 = valid_screenshots[i]
            time2, file2 = valid_screenshots[i+1]
            
            diff = (time2 - time1).total_seconds()
            
            # Проверяем, что интервал не слишком большой и не отрицательный
            if 0 < diff <= MAX_VALID_INTERVAL:
                total_time += diff
                pair_count += 1
                print(f"  Пара {pair_count}: {file1} -> {file2}: {format_time(diff)}")
                i += 2  # Переходим к следующей паре
            else:
                if diff <= 0:
                    print(f"  Пропущена пара (неверный порядок времени): {file1} -> {file2}")
                else:
                    print(f"  Пропущена пара (слишком большой интервал {format_time(diff)}): {file1} -> {file2}")
                invalid_pairs += 1
                i += 1  # Пропускаем только один файл и пробуем следующую пару
        
        print(f"  Обработано валидных пар: {pair_count}")
        print(f"  Пропущено невалидных пар: {invalid_pairs}")
        print(f"  Непарных скриншотов: {len(valid_screenshots) - (pair_count * 2)}")
        
        return total_time
    except Exception as e:
        print(f"Ошибка при обработке папки {screenshots_path}: {e}")
        return 0

print(f"Проверяем путь: {path}")

if not os.path.exists(games_file):
    print(f"ОШИБКА: Файл {games_file} не найден!")
else:
    with open(games_file, "r", encoding="utf-8") as f:
        content = f.read()
        matches = re.findall(r'\{\s*"TitleID":\s*"([^"]+)",\s*"Title":\s*"([^"]+)"\s*\}[,\s]*', content)
        
        if not matches:
            print("ОШИБКА: Не найдено ни одной игры в файле!")
        else:
            games = {title_id: title for title_id, title in matches}
            print(f"\nНайдено игр в файле: {len(games)}")
            
            total_global_time = 0
            screenshot_folders_processed = 0
            games_without_screenshots = []
            
            for folder in os.listdir(path):
                if folder in games:
                    screenshots_path = os.path.join(path, folder, "Screenshots")
                    if os.path.exists(screenshots_path) and os.path.isdir(screenshots_path):
                        print(f"\nОбработка игры: {games[folder]} (ID: {folder})")
                        game_time = process_screenshots(screenshots_path)
                        print(f"Суммарное время между скриншотами: {format_time(game_time)}")

                        total_global_time += game_time
                        screenshot_folders_processed += 1
                    else:
                        print(f"\nДля игры {games[folder]} (ID: {folder}) папка Screenshots не найдена")
                        games_without_screenshots.append(games[folder])
            
            print(f"\nИтого обработано папок со скриншотами: {screenshot_folders_processed}")
            if games_without_screenshots:
                print(f"Игр без папки Screenshots: {len(games_without_screenshots)}")
                print(f"  {', '.join(games_without_screenshots)}")
            
            print(f"\nОбщее суммарное время между всеми скриншотами: {format_time(total_global_time)}")
            print(f"Это примерно {total_global_time/3600:.2f} часов")

input("\nПрограмма завершена. Нажмите Enter для выхода...")
