import os
import re
import zipfile
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Pt
import shutil

# 1. Поиск zip-архива в текущей папке
current_dir = os.getcwd()
zip_files = [f for f in os.listdir(current_dir) if f.endswith('.zip')]

if not zip_files:
    print("Не найден zip-архив в текущей папке!")
    exit()

zip_filename = zip_files[0]  # Берем первый найденный архив
extract_dir = os.path.join(current_dir, 'ttmp')

# 2. Распаковка архива с обработкой ошибок
try:
    # Удаляем папку, если уже существует
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    
    os.makedirs(extract_dir)
    
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
except Exception as e:
    print(f"Ошибка при распаковке: {e}")
    shutil.rmtree(extract_dir, ignore_errors=True)
    exit()

# 3. Создание документа Word с нужным именем
today = datetime.now()
yesterday = today - timedelta(days=1)
doc_name = yesterday.strftime("%d.%m") + " - " + today.strftime("%d.%m.%y") + ".docx"
doc = Document()
table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'

# Заголовки таблицы
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Время'
hdr_cells[1].text = 'Сообщение'
hdr_cells[2].text = 'Файл'

# 4. Поиск текстовых файлов в распакованной папке
txt_files = [f for f in os.listdir(extract_dir) 
            if os.path.isfile(os.path.join(extract_dir, f)) and f.endswith('.txt')]

if not txt_files:
    print("Не найден текстовый файл в архиве!")
    shutil.rmtree(extract_dir)
    exit()

txt_path = os.path.join(extract_dir, txt_files[0])

# 5. Парсинг файла и заполнение таблицы
pattern = re.compile(r'(\d{2}\.\d{2}\.\d{2}), (\d{2}:\d{2}) - .*?([^ ]+\.(?:jpg|png|jpeg|gif)) \(файл вкладено\)')
current_message = []
last_time = None
last_file = None

with open(txt_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        
        # Проверка на новую запись с файлом
        match = pattern.search(line)
        if match:
            # Сохраняем предыдущее сообщение
            if last_time and current_message:
                row_cells = table.add_row().cells
                row_cells[0].text = last_time
                row_cells[1].text = '\n'.join(current_message)
                row_cells[2].text = last_file
            
            # Начинаем новое сообщение
            last_time = match.group(2)
            last_file = match.group(3)
            current_message = []
            continue
        
        # Проверка на новую дату (начало нового сообщения)
        if re.match(r'\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2} -', line):
            if last_time and current_message:
                row_cells = table.add_row().cells
                row_cells[0].text = last_time
                row_cells[1].text = '\n'.join(current_message)
                row_cells[2].text = last_file
                current_message = []
            last_time = None
            continue
        
        # Собираем строки сообщения
        if last_time and line:
            current_message.append(line)

# Добавляем последнее сообщение
if last_time and current_message:
    row_cells = table.add_row().cells
    row_cells[0].text = last_time
    row_cells[1].text = '\n'.join(current_message)
    row_cells[2].text = last_file

# 6. Сохранение документа
doc.save(doc_name)
print(f"Документ {doc_name} успешно создан!")

# 7. Удаление временной папки
shutil.rmtree(extract_dir)