

import pandas as pd
import os
import re
import subprocess
import google.generativeai as genai
import json
from pdf2image import convert_from_path
from urllib import request as url_request
import sys
import shutil
from datetime import datetime
import time

# --- ГЛАВНЫЕ НАСТРОЙКИ ---
# 1. Сетевая папка, откуда будут браться исходные прайсы
SOURCE_DIRECTORY_TEMPLATE = r"E:\Shared\ОТДЕЛ ПРОДАЖ\Обмен Данными\Прайс листы и отчеты\{date_folder}"
# 2. Локальная папка, куда будут копироваться и где будут обрабатываться файлы
INPUT_FOLDER_NAME = "_INPUT_FILES"
# 3. Настройки планировщика
START_HOUR = 18
END_HOUR = 23
RETRY_DELAY_MINUTES = 10
# 4. Пути к внешним программам
POPPLER_PATH = r"C:\poppler\Library\bin"
LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

# --- НАСТРОЙКА PROXY и API ---
try:
    system_proxies = url_request.getproxies()
    if system_proxies.get('http'): os.environ['HTTP_PROXY'] = system_proxies['http']
    if system_proxies.get('https'): os.environ['HTTPS_PROXY'] = system_proxies['https']
    genai.configure(api_key="AIzaSyAnHlkC02cmAwjbR2uJcq5WctcPedL0_Zg")
    print("Конфигурация Gemini API завершена (с поддержкой системного прокси).")
except KeyError:
    print("="*60 + "\nОШИБКА: Переменная окружения GEMINI_API_KEY не найдена!\n" + "="*60)
    sys.exit()
except Exception as e:
    print(f"Не удалось настроить API или прокси: {e}.")
    sys.exit()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def normalize_product_name(name):
    name = str(name).upper()
    if 'ГОРБУША' in name: return 'АА_ГОРБУША'
    if 'ТЕРПУГ' in name: return 'АБ_ТЕРПУГ'
    if 'СКУМБРИЯ' in name: return 'АВ_СКУМБРИЯ'
    if 'СЕЛЬДЬ' in name or 'СЕЛЁДКИ' in name: return 'АГ_СЕЛЬДЬ'
    if 'ИВАСИ' in name: return 'АД_ИВАСИ'
    if 'САРДИНА' in name: return 'АЕ_САРДИНА'
    if 'КЕТА' in name: return 'АЖ_КЕТА'
    if 'КИЖУЧ' in name: return 'АЗ_КИЖУЧ'
    if 'ЛОСОСЬ' in name: return 'АИ_ЛОСОСЬ'
    if 'НЕРКА' in name: return 'АК_НЕРКА'
    if 'ПАЛТУС' in name: return 'АЛ_ПАЛТУС'
    if 'ТРЕСКА' in name: return 'АМ_ТРЕСКА'
    if 'МИНТАЙ' in name: return 'АН_МИНТАЙ'
    if 'КАМБАЛА' in name: return 'АО_КАМБАЛА'
    if 'МОЙВА' in name: return 'АП_МОЙВА'
    if 'НАВАГА' in name: return 'АР_НАВАГА'
    if 'ПУТАССУ' in name: return 'АС_ПУТАССУ'
    if 'КАЛЬМАР' in name: return 'АТ_КАЛЬМАР'
    if 'ФАРШ' in name: return 'БА_ФАРШ'
    return 'ЯЯ_' + name.split(' ')[0]

def convert_to_pdf(input_path, output_dir):
    if not os.path.exists(LIBREOFFICE_PATH): return False
    print(f"    -> Конвертация {os.path.basename(input_path)} в PDF...")
    try:
        subprocess.run(
            [LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, input_path],
            check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except Exception: return False

def convert_pdf_to_images(pdf_path):
    try: return convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    except Exception as e:
        print(f"    -! Ошибка конвертации PDF в изображения: {e}"); return []

# --- ГЛАВНАЯ AI ФУНКЦИЯ ---
def process_document_with_gemini_vision(images, filename, today_date_str):
    # Модель gemini-1.5-flash-latest - актуальное название для flash-модели
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # ★★★ САМЫЙ НОВЫЙ ПРОМПТ ★★★
    prompt_text = f"""
Ты — AI-аналитик, специализирующийся на извлечении данных из рыбных прайс-листов.
Твоя задача — внимательно изучить предоставленные изображения страниц (имя исходного файла: "{filename}") и извлечь ТОЛЬКО ТЕ товарные позиции, которые соответствуют списку ниже.

СПИСОК РАЗРЕШЕННЫХ ПРОДУКТОВ ДЛЯ ИЗВЛЕЧЕНИЯ:
- Терпуг, Горбуша, Скумбрию, Иваси, икра сельди/селёдки, Кальмар (филе и тушка), Сардина, Камбала, Сельдь, Кета, Кижуч, Лосось, Минтай, Мойва, Навага, Нерка, Палтус, Путассу, Треска, Филе трески, любой товар со словом "фарш".

СПИСОК РАЗРЕШЕННЫХ СКЛАДОВ:
- Екатеринбург (ЕКБ), Лакинск, Москва (МСК), СПБ, Березовский, Заречный, Владивосток.

ТРЕБОВАНИЯ К РЕЗУЛЬТАТУ:
1.  Твой ответ ДОЛЖЕН БЫТЬ ТОЛЬКО в формате одного валидного JSON-массива (списка).
2.  Каждый элемент в массиве — это JSON-объект, представляющий ОДНУ найденную товарную позицию.
3.  Каждый объект должен иметь ТОЛЬКО следующие 5 ключей: "Дата", "Поставщик", "Номенклатура", "Склад", "Цена".
4.  Если у товара несколько размеров с ценами через "/" (например, "355/355/357,5"), создай ОТДЕЛЬНЫЕ JSON-объекты для каждой цены.
5.  Если цена указана как диапазон ("395-400,00"), используй только минимальное значение ("395").
6.  Все даты приводи к формату ДД.ММ.ГГГГ. Если в дате нет месяца или год больше 2025, используй сегодняшнюю дату: {today_date_str}.
7.  Если найденный склад не похож ни на один из "СПИСКА РАЗРЕШЕННЫХ СКЛАДОВ", оставь поле "Склад" пустым. Ищи информацию о складе по всему документу.

ПРАВИЛА ЗАПОЛНЕНИЯ:
- "Поставщик": Определи название компании-поставщика по логотипу или тексту в документе.
- "Номенклатура": Включай сюда всю информацию о товаре.
- "Цена": Очищай от лишних символов, оставляй только число и, если есть, "₽".
- Игнорируй заголовки, контакты и всё, что не является разрешенным товаром.

Проанализируй эти страницы и верни JSON-массив только с разрешенными продуктами.
"""
    request_content = [prompt_text] + images
    try:
        response = model.generate_content(request_content, request_options={"timeout": 600})
        cleaned_response = re.sub(r'```json\s*|\s*```', '', response.text.strip())
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, Exception) as e:
        print(f"    -! Ошибка при обработке ответа от Gemini: {e}"); return []

# --- ОСНОВНЫЕ ФУНКЦИИ КОНВЕЙЕРА ---
def copy_files_from_source(input_folder_path, today_date_str):
    date_folder = today_date_str
    source_path = SOURCE_DIRECTORY_TEMPLATE.format(date_folder=date_folder)
    print(f"Проверка исходной папки: {source_path}")
    if not os.path.exists(source_path):
        print(" -> Исходная папка на сегодня не найдена. Пропускаем копирование.")
        return True # Возвращаем True, чтобы не считать это ошибкой и не запускать retry
    
    files_to_copy = os.listdir(source_path)
    if not files_to_copy:
        print(" -> Исходная папка пуста. Пропускаем копирование.")
        return True
        
    print(f"Найдено {len(files_to_copy)} файлов. Копирование в '{INPUT_FOLDER_NAME}'...")
    for filename in files_to_copy:
        shutil.copy(os.path.join(source_path, filename), input_folder_path)
    print(" -> Копирование завершено.")
    return True

def prepare_input_files(input_folder_path):
    print(f"\n--- ЭТАП 1: Подготовка файлов в папке '{INPUT_FOLDER_NAME}' ---")
    files_in_folder = os.listdir(input_folder_path)
    if not files_in_folder:
        print(" -> Папка для обработки пуста. Пропускаем этот этап.")
        return
        
    for filename in files_in_folder:
        if not filename.lower().endswith('.pdf'):
            original_file_path = os.path.join(input_folder_path, filename)
            if convert_to_pdf(original_file_path, input_folder_path):
                print(f"    -> Успешная конвертация. Удаление исходного файла: {filename}")
                os.remove(original_file_path)
            else:
                print(f"    -! Не удалось конвертировать {filename}. Файл пропущен.")
    return

def run_processing_pipeline(today_date_str):
    # 1. Создаем папку-обработчик и копируем туда файлы
    input_path = os.path.join(os.getcwd(), INPUT_FOLDER_NAME)
    os.makedirs(input_path, exist_ok=True)
    if not copy_files_from_source(input_path, today_date_str):
        raise Exception("Не удалось получить доступ к исходной папке.")

    # 2. Конвертируем все в PDF
    prepare_input_files(input_path)
    
    # 3. Основной цикл анализа PDF
    pdf_files_to_process = [f for f in os.listdir(input_path) if f.lower().endswith('.pdf')]
    if not pdf_files_to_process:
        print("\nВ папке-обработчике нет PDF файлов для анализа. Работа на сегодня завершена.")
        return
        
    print(f"\n--- ЭТАП 2: Найдено {len(pdf_files_to_process)} PDF для анализа ---")
    
    newly_extracted_data = []
    for filename in pdf_files_to_process:
        print(f"\n1. Обработка документа: {filename}")
        full_pdf_path = os.path.join(input_path, filename)
        
        print("2. Конвертация страниц в изображения...")
        images = convert_pdf_to_images(full_pdf_path)
        
        if images:
            print(f"3. Отправка {len(images)} стр. в Gemini Vision API для анализа...")
            parsed_data = process_document_with_gemini_vision(images, filename, today_date_str)
            if parsed_data:
                newly_extracted_data.extend(parsed_data)
                supplier_name = parsed_data[0].get('Поставщик', 'Н/Д')
                print(f"4. Успешно! Gemini извлек {len(parsed_data)} релевантных позиций от '{supplier_name}'.")
            else:
                print(f"4. ПРЕДУПРЕЖДЕНИЕ: Gemini не нашел релевантных позиций в '{filename}'.")
        else:
            print("   Пропуск файла из-за ошибки конвертации в изображения.")
    
    # 4. Формирование и дозапись в финальный Excel-файл
    if not newly_extracted_data:
        print("\n\nАнализ завершен. Новых данных для добавления в файл не найдено.")
        return
        
    print(f"\n--- ЭТАП 3: Обновление файла Excel ---")
    output_filename = 'Сводный_прайс_лист_ФИНАЛ.xlsx'
    
    # Считываем старые данные, если файл существует
    if os.path.exists(output_filename):
        print(f" -> Найден существующий файл '{output_filename}'. Чтение старых данных...")
        old_df = pd.read_excel(output_filename)
        new_df = pd.DataFrame(newly_extracted_data)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        print(f" -> Файл '{output_filename}' не найден. Будет создан новый.")
        combined_df = pd.DataFrame(newly_extracted_data)
        
    # Обработка и сортировка
    combined_df.rename(columns={'Номенклатура': 'наименование', 'Склад': 'Геолокация'}, inplace=True)
    
    print(" -> Удаление дубликатов и сортировка...")
    # Удаляем дубликаты на основе ключевых полей
    key_columns = ['Дата', 'Поставщик', 'наименование', 'Цена', 'Геолокация']
    for col in key_columns:
        if col not in combined_df.columns: combined_df[col] = ''
    combined_df.drop_duplicates(subset=key_columns, keep='last', inplace=True)
    
    combined_df['sort_group'] = combined_df['наименование'].apply(normalize_product_name)
    combined_df.sort_values(by='sort_group', kind='stable', inplace=True)
    
    # Финальная структура
    final_columns_order = ['Дата', 'Поставщик', 'Цена', 'Геолокация', 'наименование']
    for col in final_columns_order:
        if col not in combined_df.columns: combined_df[col] = ''
    
    final_output_df = combined_df[final_columns_order]
    final_output_df.to_excel(output_filename, sheet_name='Сводный прайс', index=False)
    
    print(f"\n\n--- АНАЛИЗ ЗАВЕРШЕН! ---")
    print(f"Результат сохранен в файле: {output_filename}")


# --- ПЛАНИРОВЩИК ---
if __name__ == "__main__":
    while True:
        now = datetime.now()
        today_date_str = now.strftime("%d.%m.%Y")
        
        # Проверяем, находимся ли мы в рабочем окне
        if START_HOUR <= now.hour < END_HOUR:
            print(f"[{now.strftime('%H:%M:%S')}] Начинаем обработку за {today_date_str}...")
            try:
                run_processing_pipeline(today_date_str)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Обработка успешно завершена. Скрипт завершает работу.")
                break # Успешный выход из цикла
            except Exception as e:
                print("="*60)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ПРОИЗОШЛА КРИТИЧЕСКАЯ ОШИБКА:")
                print(e)
                print(f"Повторная попытка через {RETRY_DELAY_MINUTES} минут...")
                print("="*60)
                time.sleep(RETRY_DELAY_MINUTES * 60)
        
        # Если рабочий день окончен
        elif now.hour >= END_HOUR:
            print(f"[{now.strftime('%H:%M:%S')}] Рабочее окно ({START_HOUR}:00 - {END_HOUR}:00) завершено. Скрипт завершает работу.")
            break
            
        # Если еще не время начинать
        else:
            wait_time = (datetime(now.year, now.month, now.day, START_HOUR, 0) - now).total_seconds()
            print(f"[{now.strftime('%H:%M:%S')}] Ожидание начала рабочего окна в {START_HOUR}:00. Сон на {int(wait_time // 60)} минут.")
            time.sleep(wait_time)