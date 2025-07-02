import os
import re
from datetime import datetime

# Таблица транслитерации кириллицы на латиницу
translit_table = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 
    'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO', 'Ж': 'ZH', 'З': 'Z', 
    'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'KH', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
}

def transliterate_filename(filename):
    """Переводит имя файла из кириллицы в латиницу"""
    new_filename = ''
    for char in filename:
        new_filename += translit_table.get(char, char)
    new_filename = re.sub(r'\s+', '_', new_filename)
    return new_filename

def has_cyrillic(text):
    """Проверяет наличие кириллических символов"""
    return any('\u0400' <= char <= '\u04FF' for char in text)

def scan_music_files(directory="."):
    """Сканирует текущую директорию на наличие .ogg и .dat файлов"""
    music_files = []
    cyrillic_files = []
    
    # Сканируем только текущую директорию
    for file in os.listdir(directory):
        if file.lower().endswith(('.ogg', '.dat')):
            # Полный путь к файлу
            full_path = os.path.abspath(file).replace("\\", "/")
            # Путь для вывода в конфиг (от mods или от корня диска)
            mods_index = full_path.find("/mods/")
            if mods_index != -1:
                config_path = full_path[mods_index + 1:]  # Начинаем с mods/
            else:
                # Находим букву диска (например, C:/)
                drive_index = full_path.find(":")
                if drive_index != -1:
                    config_path = full_path[drive_index + 1:]  # Начинаем от корня диска
                else:
                    config_path = full_path
            music_files.append(config_path)
            # Проверяем кириллицу
            if has_cyrillic(file):
                cyrillic_files.append((full_path, file, config_path))
    
    return music_files, cyrillic_files

def rename_cyrillic_files(cyrillic_files, music_files):
    """Предлагает переименовать файлы с кириллицей"""
    if not cyrillic_files:
        return
    
    print("\nОбнаружены файлы с кириллическими символами:")
    for _, filename, config_path in cyrillic_files:
        print(f"- {filename} ({config_path})")
    
    response = input("\nПереименовать эти файлы, заменив кириллицу на латиницу? (y/n): ").lower()
    if response == 'y':
        for full_path, filename, config_path in cyrillic_files:
            new_filename = transliterate_filename(filename)
            new_full_path = os.path.join(os.path.dirname(full_path), new_filename).replace("\\", "/")
            try:
                os.rename(full_path, new_full_path)
                print(f"Переименован: {filename} -> {new_filename}")
                # Обновляем путь в music_files
                mods_index = new_full_path.find("/mods/")
                if mods_index != -1:
                    new_config_path = new_full_path[mods_index + 1:]
                else:
                    drive_index = new_full_path.find(":")
                    new_config_path = new_full_path[drive_index + 1:] if drive_index != -1 else new_full_path
                music_files[music_files.index(config_path)] = new_config_path
            except Exception as e:
                print(f"Ошибка при переименовании {filename}: {e}")

def get_exe_name():
    """Получает имя исполняемого файла без расширения"""
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.splitext(os.path.basename(sys.executable))[0]
    return "MyMusicScript"

def create_music_config(music_files):
    """Создает конфигурационный файл в указанном формате"""
    categories = [
        "ArcadeBattle", "BK", "Battle", "MC", "Nation", "PB", "Quest", 
        "RC", "Robot", "SB", "Song", "StarMap", "WB", "Win"
    ]
    nation_subcategories = ["Fei", "Gaal", "Maloc", "None", "Peleng"]
    
    exe_name = get_exe_name()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"MusicConfig_{timestamp}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Music ^ {\n")
        
        for category in categories:
            if category not in ["Nation", "Song"]:
                f.write(f"    {category} ^ {{\n")
                for music_file in music_files:
                    f.write(f"        {exe_name}Music1={music_file}\n")
                f.write("    }\n")
        
        if "Song" in categories:
            f.write(f"    Song ^ {{\n")
            for i, music_file in enumerate(music_files, 10):
                f.write(f"        {exe_name}Music{i}={music_file}\n")
            f.write("    }\n")
        
        if "Nation" in categories:
            f.write("    Nation ^ {\n")
            for subcategory in nation_subcategories:
                f.write(f"        {subcategory} ^ {{\n")
                for music_file in music_files:
                    f.write(f"            {exe_name}Music1={music_file}\n")
                f.write("        }\n")
            f.write("    }\n")
        
        f.write("}\n")
    
    print(f"\nФайл создан: {output_file}")

def main():
    print("Сканирование музыкальных файлов в текущей директории...")
    music_files, cyrillic_files = scan_music_files()
    if not music_files:
        print("Музыкальные файлы (.ogg или .dat) не найдены!")
        return
    print(f"Найдено {len(music_files)} музыкальных файлов")
    
    # Проверка и переименование файлов с кириллицей
    rename_cyrillic_files(cyrillic_files, music_files)
    
    # Создание конфигурационного файла
    create_music_config(music_files)

if __name__ == "__main__":
    main()
    input("Нажмите Enter для завершения...")