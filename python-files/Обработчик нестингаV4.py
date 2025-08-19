import os
import re
from tkinter import Tk, filedialog, Button, Label, messagebox

# Параметры обработки
TRIM_WIDTH = 5.0  # Ширина торцевания в мм
TABLE_WIDTH = 1220.0  # Ширина стола (X)
TABLE_HEIGHT = 2800.0  # Высота стола (Y)
TOOL_T1_SETUP = [
    "M06 T1",
    "M03 S18000",
    "G43 H1",
    "G0 Z28.0"
]

def parse_gcode_line(line):
    """Извлекает координаты из строки G-кода"""
    x_match = re.search(r'X([\d.]+)', line)
    y_match = re.search(r'Y([\d.]+)', line)
    x = float(x_match.group(1)) if x_match else None
    y = float(y_match.group(1)) if y_match else None
    return x, y

def remove_initial_commands(content):
    """Удаление начальных команд N10-N40 для всех файлов"""
    filtered_lines = []
    skip_initial = True
    
    for line in content.split('\n'):
        line_stripped = line.strip()
        
        # Пропускаем начальные команды N10-N40
        if skip_initial and any(line_stripped.startswith(f'N{i}') for i in range(10, 50, 10)):
            continue
        else:
            skip_initial = False
            filtered_lines.append(line)
    
    return filtered_lines

def add_facing_operation(content):
    """Добавление операции торцевания перед завершающими командами"""
    filtered_lines = remove_initial_commands(content)
    
    # Находим позицию для вставки торцевания (перед завершающими командами)
    insert_index = len(filtered_lines)
    for i in range(len(filtered_lines)-1, -1, -1):
        if "M05" in filtered_lines[i] or "M30" in filtered_lines[i]:
            insert_index = i
    
    # Добавляем команды для инструмента T1 и торцевание
    facing_lines = TOOL_T1_SETUP + [
        f"G0 X2.0 Y2.0",
        "G1 Z-0.1 F10000",
        f"G1 X{TABLE_WIDTH-2.0:.1f} Y2.0 F10000",
        f"G1 X{TABLE_WIDTH-2.0:.1f} Y{TABLE_HEIGHT-2.0:.1f} F10000",
        "G0 Z28.0"
    ]
    
    # Вставляем торцевание перед завершающими командами
    return filtered_lines[:insert_index] + facing_lines + filtered_lines[insert_index:]

def apply_coordinate_offset(content):
    """Применение смещения координат и удаление торцевых операций"""
    filtered_lines = remove_initial_commands(content)
    
    # Смещение координат и удаление торцевых операций
    result = []
    for line in filtered_lines:
        x, y = parse_gcode_line(line)
        
        # Удаляем операции на торцевых краях (уже обработанных)
        if (x is not None and (abs(x - 2.0) < 0.1 or abs(x - (TABLE_WIDTH-2.0)) < 0.1)) or \
           (y is not None and (abs(y - 2.0) < 0.1 or abs(y - (TABLE_HEIGHT-2.0)) < 0.1)):
            continue
            
        # Применяем смещение координат (вниз и влево)
        if x is not None or y is not None:
            new_line = line
            if x is not None:
                new_x = x - TRIM_WIDTH
                new_line = re.sub(r'X([\d.]+)', f'X{new_x:.1f}', new_line)
            if y is not None:
                new_y = y - TRIM_WIDTH
                new_line = re.sub(r'Y([\d.]+)', f'Y{new_y:.1f}', new_line)
            result.append(new_line)
        else:
            result.append(line)
    
    return result

def process_file(input_path, output_path):
    """Обработка файла в зависимости от типа"""
    # Определяем имя файла без пути
    file_name = os.path.basename(input_path)
    file_name_lower = file_name.lower()
    
    # Чтение с определением кодировки
    for encoding in ['utf-8', 'cp1251', 'latin1']:
        try:
            with open(input_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    # Определяем тип обработки по имени файла
    if '_1' in file_name_lower:
        # Файлы вида X_1 (первая обработка - отверстия, пазы + торцевание)
        processed_lines = add_facing_operation(content)
    elif '_2' in file_name_lower:
        # Файлы вида X_2 (вторая обработка - раскрой со смещением)
        processed_lines = apply_coordinate_offset(content)
    else:
        # Одиночные файлы (только удаление начальных команд)
        processed_lines = remove_initial_commands(content)
    
    # Сохранение результата
    with open(output_path, 'w', encoding='utf-8') as f_out:
        f_out.write('\n'.join(processed_lines))

def process_folder():
    """Основная функция обработки папки"""
    folder = filedialog.askdirectory(title="Выберите папку с файлами ЧПУ")
    if not folder:
        return
    
    # Создание папки для результатов
    output_folder = os.path.join(folder, "переработано")
    os.makedirs(output_folder, exist_ok=True)
    
    # Обработка файлов
    processed_files = []
    
    for file in os.listdir(folder):
        file_lower = file.lower()
        # Обрабатываем все CNC/NC файлы и файлы без расширения
        if (file_lower.endswith(('.cnc', '.nc')) or 
            '_1' in file_lower or 
            '_2' in file_lower or
            file.isdigit() or  # Для файлов типа "1", "2"
            re.match(r'^\d+$', os.path.splitext(file)[0])):  # Для файлов "1.txt", "2.cnc"
            
            input_path = os.path.join(folder, file)
            output_path = os.path.join(output_folder, file)
            
            try:
                process_file(input_path, output_path)
                processed_files.append(file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обработки {file}:\n{str(e)}")
    
    # Формирование отчета
    if processed_files:
        messagebox.showinfo(
            "Обработка завершена!",
            f"Успешно обработано файлов: {len(processed_files)}\n"
            f"Результаты сохранены в папке:\n{output_folder}\n\n"
            "Типы обработки:\n"
            "1. Файлы _1 (первая обработка):\n"
            "   - Отверстия и пазы\n"
            "   - Торцевание перед завершающими командами\n"
            "   - Команды для инструмента T1\n\n"
            "2. Файлы _2 (вторая обработка):\n"
            "   - Смещение координат (X-5мм, Y-5мм)\n"
            "   - Удаление операций на торцевых краях\n\n"
            "3. Одиночные файлы (1, 2, 3...):\n"
            "   - Только удаление начальных команд N10-N40"
        )
    else:
        messagebox.showinfo(
            "Файлы не найдены",
            "Не найдено подходящих файлов для обработки"
        )

# Создание графического интерфейса
root = Tk()
root.title("ЧПУ: Универсальный обработчик v2.0")
root.geometry("750x450")

# Заголовок
Label(root, text="Универсальный обработчик G-кода для ЧПУ", 
      font=('Arial', 14, 'bold')).pack(pady=15)

# Описание процесса
process_desc = """
Правильный порядок обработки:

1. Файлы с суффиксом _1 (например, 4_1.CNC):
   - Первая обработка листа
   - Отверстия и пазы
   - Торцевание краев (добавляется в конце программы)
   - Используется инструмент T1 для торцевания

2. Файлы с суффиксом _2 (например, 4_2.CNC):
   - Вторая обработка (после переворота листа)
   - Раскрой деталей
   - Смещение координат (X-5мм, Y-5мм)
   - Удаление операций на торцевых краях

3. Одиночные файлы (например, 1.CNC, 2):
   - Только удаление начальных команд N10-N40
   - Без дополнительных изменений

Важно: Торцевание добавляется только в файлах _1 и выполняется в конце программы.
"""
Label(root, text=process_desc, justify='left', font=('Arial', 10)).pack(pady=10, padx=20)

# Кнопка запуска
Button(root, text="Выбрать папку и начать обработку", 
       command=process_folder, height=2, width=35,
       bg="#4CAF50", fg="white", font=('Arial', 10, 'bold')).pack(pady=20)

# Параметры
params = (f"Текущие параметры: Ширина торцевания = {TRIM_WIDTH}мм, "
          f"Стол = {TABLE_WIDTH}x{TABLE_HEIGHT}мм")
Label(root, text=params, font=('Arial', 9), fg="gray", wraplength=700).pack(side='bottom', pady=10)

root.mainloop()