from pathlib import Path
import re
import subprocess
import ctypes

# Проверка на буквы
def contains_letter(folder_name):
    return bool(re.search(r'[а-яА-Яa-zA-Z]', folder_name))
# Проверка на посторонние символы
def contains_another_symbols(folder_name):
    return bool(re.fullmatch(r'!"№;%:_=-<>,@#&', folder_name))

# Разбивает папки на числовые компоненты по символам "_"
def parse_version(folder_name):
    return [int(part) for part in folder_name.split('_') if part.isdigit()]
# Находит папку с наибольшией версией
def find_latest_version(folders):
    if not folders:
        return None
    
    max_folder = folders[0]
    max_version = parse_version(max_folder.name)

    for folder in folders[1:]:
        current_version = parse_version(folder.name)
        # Сравниваем версии по компонентам
        for i in range(max(len(max_version), len(current_version))):
            # Если текуий компонент отсутствует, считаем его нулём
            max_part = max_version[i] if i < len(max_version) else 0
            current_part = current_version[i] if i < len(current_version) else 0

            if current_part > max_part:
                max_folder = folder
                max_version = current_version
                break
            elif current_part < max_part:
                break
            # Если компоненты равны, переходим к следующему
    return max_folder

def normalize(name):
    return name.replace("_", " ").replace(".", " ")

source_root = Path(r"\\maytea.com\ndfs\Сервисные папки\1C\Обновления\Платформа")
target_root = Path("C:/Program Files/1cv8")

if not source_root.exists():
    print(f"Сетевой путь недоступен: {source_root}")
    exit()

# Собираем все подходящие папки (без букви и иных символов)
valid_folders = []

# Проверяем сетевую папку
for source_folder in source_root.iterdir():
    if not source_folder.is_dir():
        continue

    # Пропускаем файлы с буквами
    if contains_letter(source_folder.name):
        print(f"Пропускаем файлы, содержащие буквы в названии: '{source_folder.name}'")
        continue
    # Пропускаем файлы с посторонними символами
    if contains_another_symbols(source_folder.name):
        print(f"Пропускаем файлы, содержащие любые символы кроме '_': '{source_folder.name}'")
        continue

    valid_folders.append(source_folder)

if not valid_folders:
    print("Нет подходящих папок для установки")
    exit()

#Находим папку с максимальной версией
latest_folder = find_latest_version(valid_folders)
print(f"Найдена последняя версия: '{latest_folder.name}'")

normalized_latest = normalize(latest_folder.name)

found_copy = False
for target_folder in target_root.iterdir():
    if target_folder.is_dir() and normalize(target_folder.name) == normalized_latest:
        found_copy = True
        break

if found_copy:
    print(f"Папка '{latest_folder.name}' ужесуществует в целевой диектории.")
    exit()

print(f"Копия для '{latest_folder.name}' не найдена. Запускаем установку.")

setup_file = None
for pattern in ["setup.exe"]:
    for file in latest_folder.glob(pattern):
        setup_file = file
        break
    if setup_file:
        break

if not setup_file:
    print(f"Не найден setup.exe файл в папке '{latest_folder.name}'")
    exit()

print(f"Установочный файл найден")

try:
    result=subprocess.run(
        [str(setup_file), "/S", "/v/qn", f'INSTALLDIR="{target_root}"', "ACCEPT_EULA=1", "/norestart"], 
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    print(f"Установка из '{latest_folder.name}' завершена.")
except subprocess.CalledProcessError as e:
    print(f"Ошибка при установке 1С: '{e.stderr}'")
except Exception as e:
    print(f"Неожиданная ошибка при установке '{latest_folder.name}': {e}")