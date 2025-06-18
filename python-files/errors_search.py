import re
import os

# Путь к текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, 'translations.txt')
output_file = os.path.join(current_dir, 'errors.txt')

# Регулярка для поиска запрещённых символов
# Разрешено: латиница (a-zA-Z), цифры (0-9), точка, дефис, подчёркивание
pattern = re.compile(r'[^a-zA-Z0-9._-]')

# Чтение строк из файла
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Удаляем каждую вторую строку (оставляем строки с чётными индексами)
filtered_lines = lines[::2]

# Из каждой строки удаляем последний символ (если строка не пустая)
processed_lines = [line.rstrip('\n')[:-1] if line.strip() else '' for line in filtered_lines]

# Находим строки с ошибками
errors = [line for line in processed_lines if pattern.search(line)]

# Записываем ошибки в файл
with open(output_file, 'w', encoding='utf-8') as f:
    for err in errors:
        f.write(err + '\n')

print(f"Готово. Найдено {len(errors)} строк с ошибками. Сохранено в errors.txt.")
