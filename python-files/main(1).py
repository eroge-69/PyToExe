import os
from datetime import datetime

def scan_music_files(directory="."):
    """Сканирует директорию на наличие .ogg и .dat файлов"""
    music_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.ogg', '.dat')):
                # Получаем относительный путь от текущей директории
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                music_files.append(rel_path.replace("\\", "/"))
    return music_files

def get_exe_name():
    """Получает имя исполняемого файла без расширения"""
    import sys
    if getattr(sys, 'frozen', False):
        # Если запущен как .exe
        return os.path.splitext(os.path.basename(sys.executable))[0]
    return "MyMusicScript"  # Значение по умолчанию для разработки

def create_music_config(music_files):
    """Создает конфигурационный файл в указанном формате"""
    categories = [
        "ArcadeBattle", "BK", "Battle", "MC", "Nation", "PB", "Quest", 
        "RC", "Robot", "SB", "Song", "StarMap", "WB", "Win"
    ]
    
    # Подкатегории для Nation
    nation_subcategories = ["Fei", "Gaal", "Maloc", "None", "Peleng"]
    
    exe_name = get_exe_name()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"MusicConfig_{timestamp}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Music ^ {\n")
        
        # Обычные категории (кроме Nation и Song)
        for category in categories:
            if category not in ["Nation", "Song"]:
                f.write(f"    {category} ^ {{\n")
                for music_file in music_files:
                    f.write(f"        {exe_name}Music1={music_file}\n")
                f.write("    }\n")
        
        # Специальная обработка для Song
        if "Song" in categories:
            f.write(f"    Song ^ {{\n")
            for i, music_file in enumerate(music_files, 10):
                f.write(f"        {exe_name}Music{i}={music_file}\n")
            f.write("    }\n")
        
        # Специальная обработка для Nation
        if "Nation" in categories:
            f.write("    Nation ^ {\n")
            for subcategory in nation_subcategories:
                f.write(f"        {subcategory} ^ {{\n")
                for music_file in music_files:
                    f.write(f"            {exe_name}Music1={music_file}\n")
                f.write("        }\n")
            f.write("    }\n")
        
        f.write("}\n")
    
    print(f"Файл создан: {output_file}")

def main():
    print("Сканирование музыкальных файлов...")
    music_files = scan_music_files()
    if not music_files:
        print("Музыкальные файлы (.ogg или .dat) не найдены!")
        return
    print(f"Найдено {len(music_files)} музыкальных файлов")
    create_music_config(music_files)

if __name__ == "__main__":
    main()
    input("Нажмите Enter для завершения...")