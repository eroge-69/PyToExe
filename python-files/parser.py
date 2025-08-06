import tkinter as tk
from tkinter import ttk
import threading
import requests
import re
import os
import pandas as pd
import base64
from typing import List, Dict, Optional, Any

# --- НАСТРОЙКИ (ЗАПОЛНИТЕ ЭТИ ДАННЫЕ) ---
BITRIX_WEBHOOK_URL = "https://fishriteylplyus-ru.bitrix24.ru/rest/33/dcsxol8ilcgfudtm/"
USER_ID_TO_NOTIFY = 33  # Замените на ID нужного пользователя
OUTPUT_FILENAME = "номера телефонов.xlsx"
# -------------------------------------------

class ProgressApp:
    """
    Класс для создания окна с прогресс-баром, работающего в отдельном потоке.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор отчета")
        self.root.geometry("400x120")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close) # Запрещаем закрывать окно вручную

        # Переменные для отслеживания прогресса
        self.progress_value = tk.DoubleVar()
        self.status_text = tk.StringVar()
        self.status_text.set("Подготовка к запуску...")

        # Создание виджетов
        ttk.Label(self.root, textvariable=self.status_text, font=('Helvetica', 10)).pack(pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_value, maximum=100, length=350)
        self.progress_bar.pack(pady=5)
        
        ttk.Label(self.root, textvariable=self.progress_value, font=('Helvetica', 10)).pack(pady=5)
        
        # Запуск основного рабочего процесса в отдельном потоке, чтобы GUI не зависал
        self.worker_thread = threading.Thread(target=self.run_workload, daemon=True)
        self.worker_thread.start()

    def update_progress(self, value, text):
        """Метод для обновления виджетов из основного потока."""
        self.progress_value.set(round(value, 2))
        self.status_text.set(text)
        self.root.update_idletasks()

    def run_workload(self):
        """Основная логика, выполняемая в фоновом потоке."""
        try:
            # --- Этап 1: Получение данных о компаниях ---
            self.update_progress(5, "Этап 1/6: Получение ID и телефонов...")
            companies_raw_data = get_company_ids_and_phones(BITRIX_WEBHOOK_URL)
            if not companies_raw_data:
                self.update_progress(100, "Ошибка: не удалось получить данные о компаниях.")
                self.schedule_close()
                return

            # --- Этап 2: Получение названий ---
            self.update_progress(20, "Этап 2/6: Получение названий компаний...")
            all_company_ids = [str(c['ID']) for c in companies_raw_data if 'ID' in c]
            titles_map = get_titles_in_batch(BITRIX_WEBHOOK_URL, all_company_ids)
            
            # --- Этап 3: Обработка данных ---
            self.update_progress(40, "Этап 3/6: Обработка данных...")
            final_data_for_export = process_data(companies_raw_data, titles_map)
            if not final_data_for_export:
                self.update_progress(100, "Нет данных для создания отчета.")
                self.schedule_close()
                return

            # --- Этап 4: Создание Excel файла ---
            self.update_progress(60, f"Этап 4/6: Создание файла '{OUTPUT_FILENAME}'...")
            pd.DataFrame(final_data_for_export).to_excel(OUTPUT_FILENAME, index=False)
            
            # --- Этап 5: Загрузка файла на Диск ---
            self.update_progress(75, "Этап 5/6: Загрузка файла на Диск Битрикс24...")
            file_id = upload_file_to_disk(BITRIX_WEBHOOK_URL, USER_ID_TO_NOTIFY, OUTPUT_FILENAME)
            if not file_id:
                self.update_progress(100, "Ошибка: не удалось загрузить файл на Диск.")
                self.schedule_close()
                return
            
            # --- Этап 6: Отправка системного уведомления со ссылкой ---
            self.update_progress(90, "Этап 6/6: Отправка уведомления...")
            file_link = get_file_link(BITRIX_WEBHOOK_URL, file_id)
            if file_link:
                message = f"Автоматический отчет '{OUTPUT_FILENAME}' готов. [URL={file_link}]Открыть файл[/URL]"
                send_system_notification(BITRIX_WEBHOOK_URL, USER_ID_TO_NOTIFY, message)
                self.update_progress(100, "Завершено! Файл загружен, уведомление отправлено.")
            else:
                self.update_progress(100, "Файл загружен, но не удалось получить ссылку.")

        except Exception as e:
            self.update_progress(100, f"Произошла критическая ошибка: {e}")
        
        finally:
            self.schedule_close()

    def schedule_close(self):
        """Планирует закрытие окна через 3 секунды."""
        self.root.after(3000, self.root.destroy)
        
    def disable_close(self):
        """Пустая функция, чтобы нельзя было закрыть окно крестиком."""
        pass

# --- БЛОК С ФУНКЦИЯМИ ДЛЯ РАБОТЫ С API БИТРИКС24 ---

def get_company_ids_and_phones(webhook_url: str) -> List[Dict]:
    # Эта функция остается без изменений
    method = 'crm.company.list'
    params = {'select': ["ID", "PHONE"], 'start': 0}
    all_companies = []
    while True:
        r = requests.get(f"{webhook_url}{method}", params=params)
        r.raise_for_status()
        data = r.json()
        if not data.get('result'): break
        all_companies.extend(data['result'])
        if 'next' in data: params['start'] = data['next']
        else: break
    return all_companies

def get_titles_in_batch(webhook_url: str, company_ids: List[str]) -> Dict:
    # Эта функция остается без изменений
    if not company_ids: return {}
    id_to_title_map = {}
    chunk_size = 50
    for i in range(0, len(company_ids), chunk_size):
        chunk_ids = company_ids[i:i + chunk_size]
        commands = {f'co_{cid}': f'crm.company.get?ID={cid}' for cid in chunk_ids}
        r = requests.post(f"{webhook_url}batch", json={'cmd': commands})
        r.raise_for_status()
        data = r.json()
        results = data.get('result', {}).get('result', {})
        for key, company_data in results.items():
            if isinstance(company_data, dict) and 'TITLE' in company_data:
                id_to_title_map[company_data['ID']] = company_data['TITLE']
    return id_to_title_map

def process_data(companies_raw, titles_map):
    # Новая функция для централизованной обработки
    final_data = []
    for company in companies_raw:
        company_id = company.get('ID')
        company_name = titles_map.get(str(company_id), 'Без названия')
        phone_data = company.get('PHONE')
        if not phone_data: continue
        for phone_item in phone_data:
            raw_phone = phone_item.get('VALUE')
            if raw_phone and (normalized_phone := normalize_phone_number(raw_phone)):
                final_data.append({'Компания': company_name, 'Телефон': normalized_phone})
    return final_data

def normalize_phone_number(raw_phone: str) -> Optional[str]:
    # Эта функция остается без изменений
    if not isinstance(raw_phone, str): return None
    cleaned_phone = re.sub(r'\D', '', raw_phone)
    if cleaned_phone.startswith('8') and len(cleaned_phone) == 11: return '7' + cleaned_phone[1:]
    elif cleaned_phone.startswith('7') and len(cleaned_phone) == 11: return cleaned_phone
    elif len(cleaned_phone) == 10: return '7' + cleaned_phone
    else: return None

def get_user_root_folder_id(webhook_url: str, user_id: int) -> Optional[int]:
    """Находит ID корневой папки на диске пользователя."""
    method = 'disk.storage.getlist'
    params = {'filter': {'ENTITY_TYPE': 'user', 'ENTITY_ID': user_id}}
    response = requests.post(f"{webhook_url}{method}", json=params)
    response.raise_for_status()
    result = response.json().get('result')
    if not result or 'ROOT_OBJECT_ID' not in result[0]:
        raise Exception(f"Не удалось найти ROOT_OBJECT_ID для пользователя {user_id}")
    return result[0]['ROOT_OBJECT_ID']

def upload_file_to_disk(webhook_url: str, user_id: int, local_filepath: str) -> Optional[int]:
    """Загружает файл на диск и возвращает его ID."""
    folder_id = get_user_root_folder_id(webhook_url, user_id)
    if not folder_id: return None

    with open(local_filepath, 'rb') as f:
        file_content_base64 = base64.b64encode(f.read()).decode('utf-8')

    method = 'disk.folder.uploadfile'
    params = {
        'id': folder_id,
        'data': {'NAME': os.path.basename(local_filepath)},
        'fileContent': file_content_base64,
        'generate_unique_name': 'Y'
    }
    response = requests.post(f"{webhook_url}{method}", json=params)
    response.raise_for_status()
    result = response.json()
    if 'result' in result:
        return result['result']['ID']
    raise Exception(f"Ошибка при загрузке файла: {result}")

def get_file_link(webhook_url, file_id):
    """Получает публичную ссылку на файл по его ID."""
    method = 'disk.file.get'
    params = {'id': file_id}
    response = requests.post(f"{webhook_url}{method}", json=params)
    response.raise_for_status()
    result = response.json().get('result')
    if result and 'DETAIL_URL' in result:
        return result['DETAIL_URL']
    return None

def send_system_notification(webhook_url, user_id, message):
    """Отправляет системное уведомление пользователю."""
    method = 'im.notify'
    params = {
        'to': user_id,
        'message': message,
        'type': 'SYSTEM'
    }
    requests.post(f"{webhook_url}{method}", json=params)

# --- ТОЧКА ВХОДА В ПРОГРАММУ ---

if __name__ == "__main__":
    # Проверяем, что права веб-хука достаточны
    # Для im.notify достаточно прав 'im' или 'imbot'
    
    root = tk.Tk()
    app = ProgressApp(root)
    root.mainloop()
