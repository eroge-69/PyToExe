# Название файла: mrd_interpreter.py

import sys
import os

# --- НАСТРОЙКА: ИМЯ ФАЙЛА ДЛЯ ЗАПУСКА ---
# Здесь ты можешь указать имя файла с твоим МРД-кодом,
# который будет запускаться ПО УМОЛЧАНИЮ, если ты не передал аргументы.
# Убедись, что этот файл (например, 'my_test_program.mrd') существует в той же папке!
DEFAULT_MRD_PROGRAM_FILE = "my_first_mrd_program.mrd" # Измени это на имя твоего файла, если нужно!
# ----------------------------------------

def run_mrd_code(file_path):
    """
    Эта функция читает МРД-код из файла и выполняет его.
    Она проверяет правила МРД-Языка, включая пустую строку после import.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            mrd_code_lines = file.readlines()
    except FileNotFoundError:
        # Теперь выводим более короткое сообщение об ошибке, если файл не найден
        print(f"Ошибка: Не удалось найти файл программы '{file_path}'.")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

    after_import_line = False
    
    line_number = 0
    for line in mrd_code_lines:
        line_number += 1
        original_line_content = line.strip('\n') 
        line_stripped = line.strip() 
        
        if after_import_line:
            if line_stripped != "": 
                print(f"Предупреждение в строке {line_number}: Рекомендуется оставить пустую строку после 'import mrdprint'.")
            after_import_line = False 
        
        if line_stripped.startswith("import mrdprint"):
            after_import_line = True 
            pass
        elif line_stripped == "" or line_stripped.startswith("#"): 
            if after_import_line and line_stripped == "":
                after_import_line = False 
            pass
        elif line_stripped.startswith("mrdprint("):
            if line_stripped.endswith(')'):
                text_to_print = line_stripped[len("mrdprint("):-1] 
                
                if text_to_print.startswith('"') and text_to_print.endswith('"'):
                    final_text = text_to_print[1:-1] 
                    print(final_text)
                else:
                    print(f"Ошибка в строке {line_number}: 'mrdprint' ожидает текст в кавычках. Пример: mrdprint(\"Привет\"). Строка: '{original_line_content}'")
            else:
                print(f"Ошибка в строке {line_number}: Не хватает закрывающей скобки ')' в 'mrdprint'. Строка: '{original_line_content}'")
        else:
            print(f"Ошибка в строке {line_number}: Неизвестная команда или неправильный синтаксис: '{original_line_content}'")

# --- Главная часть программы для запуска интерпретатора ---

if __name__ == "__main__":
    # Если аргументы переданы, используем их
    if len(sys.argv) > 1:
        provided_file_name = sys.argv[1]
    # Если аргументы не переданы, используем значение по умолчанию
    else:
        provided_file_name = DEFAULT_MRD_PROGRAM_FILE
        # print(f"Не указан файл для запуска. Используем файл по умолчанию: '{DEFAULT_MRD_PROGRAM_FILE}'") # Удалили или закомментировали
        # print("Чтобы запустить другой файл, укажите его как аргумент (например, в Pydroid 3 через поле 'Arguments').") # Удалили или закомментировали

    actual_file_path = provided_file_name

    # Проверяем и добавляем расширение .mrd, если его нет
    if not actual_file_path.lower().endswith(".mrd"):
        potential_path_with_mrd = actual_file_path + ".mrd"
        if os.path.exists(potential_path_with_mrd):
            actual_file_path = potential_path_with_mrd
        elif not os.path.exists(actual_file_path): 
            print(f"Ошибка: Не удалось найти файл программы '{provided_file_name}'.") # Сократили сообщение
            sys.exit(1)
    elif not os.path.exists(actual_file_path):
        print(f"Ошибка: Не удалось найти файл программы '{actual_file_path}'.") # Сократили сообщение
        sys.exit(1)

    # print(f"\n--- Запускаем '{actual_file_path}' с помощью МРД-Интерпретатора ---") # Удалили или закомментировали
    run_mrd_code(actual_file_path)
    # print("\n--- Завершено ---") # Удалили или закомментировали
