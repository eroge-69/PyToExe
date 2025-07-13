import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import gspread
import json
import threading
import time
import random
import logging # Для логирования
from logging.handlers import RotatingFileHandler # Для ротации лог-файлов
import csv     # Для экспорта в CSV
import sys  # Добавьте этот импорт
import platform

# Остальной код...

import logging
import sys
import io

if sys.platform.startswith('win'):
    # Настройка вывода в UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
        # Добавьте другие обработчики, если нужно
    ]
)

# --- ГЛОБАЛЬНАЯ НАСТРОЙКА ЛОГИРОВАНИЯ ---
# Получаем корневой логгер
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO) # Устанавливаем минимальный уровень для всех обработчиков

# Форматтер для сообщений
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 1. Обработчик для записи всех активностей в файл (с ротацией)
activity_file_handler = RotatingFileHandler(
    'app_activity.log',
    maxBytes=10 * 1024 * 1024, # 10 МБ
    backupCount=5,             # Хранить до 5 старых лог-файлов
    encoding='utf-8'
)
activity_file_handler.setLevel(logging.INFO)
activity_file_handler.setFormatter(formatter)
root_logger.addHandler(activity_file_handler)

# 2. Обработчик для записи только ошибок в отдельный файл (с ротацией)
error_file_handler = RotatingFileHandler(
    'app_errors.log',
    maxBytes=5 * 1024 * 1024, # 5 МБ
    backupCount=3,            # Хранить до 3 старых лог-файлов
    encoding='utf-8'
)
error_file_handler.setLevel(logging.ERROR) # Только ERROR и CRITICAL
error_file_handler.setFormatter(formatter)
root_logger.addHandler(error_file_handler)

# 3. Обработчик для вывода в консоль (дублирует INFO и выше)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Теперь вместо print() и старых logging.basicConfig() мы будем использовать logging.info(), logging.error() и т.д.
# Для удобства, определим псевдоним для корневого логгера, который будет использоваться в коде.
# В файле main.py __name__ будет '__main__', поэтому это даст корневой логгер.
app_logger = logging.getLogger(__name__)

# --- Класс для работы с Google Sheets как базой данных ---
class GoogleSheetsDatabase:
    def __init__(self, spreadsheet_name, service_account_file='service_account.json'):
        self.spreadsheet_name = spreadsheet_name
        self.service_account_file = service_account_file
        self.gc = None
        self.spreadsheet = None

        self.workers_sheet = None
        self.work_entries_sheet = None # Для выработки по площади
        self.hourly_work_entries_sheet = None # НОВЫЙ ЛИСТ: для почасовых записей
        self.master_shifts_sheet = None
        self.settings_sheet = None

        # Кэширование данных
        self._cached_workers = []
        self._cached_work_entries = [] # По площади
        self._cached_hourly_work_entries = [] # НОВЫЙ КЭШ: почасовые
        self._cached_master_shifts = []
        self._cached_settings = {} # Будет словарем {setting_name: setting_value}

        self._expected_headers = {
            'workers': ['id', 'type', 'name', 'rate_per_sqm'],
            'work_entries': ['id', 'worker_id', 'operation_type', 'entry_datetime', 'width', 'length', 'quantity', 'area'],
            'hourly_work_entries': ['id', 'worker_id', 'work_type', 'entry_datetime', 'hours', 'payment_amount'], # НОВЫЕ ЗАГОЛОВКИ
            'master_shifts': ['id', 'start_time', 'end_time', 'duration_hours', 'master_salary', 'ra_output_sqm', 'up_output_sqm', 'ob_output_sqm', 'gr_output_sqm'],
            'settings': ['setting_name', 'setting_value']
        }

        self.app_root_ref = None # Ссылка на главное окно Tkinter
        self.status_indicator_ref = None # Ссылка на метку статуса соединения (после ее создания)

    def set_ui_references(self, app_root, status_indicator):
        """Устанавливает ссылки на Tkinter виджеты после их создания и когда они гарантированно существуют."""
        self.app_root_ref = app_root
        self.status_indicator_ref = status_indicator

    def _update_connection_status(self, status_text, color):
        """Обновляет метку статуса соединения, только если она существует и валидна."""
        # Проверяем, что ссылки установлены И что виджет все еще существует
        if self.app_root_ref and self.status_indicator_ref and self.status_indicator_ref.winfo_exists():
            self.app_root_ref.after(0, lambda: self.status_indicator_ref.config(text=status_text, fg=color))

    def connect(self):
        """Устанавливает соединение с Google Sheets. Выполняется в отдельном потоке."""
        try:
            app_logger.info("Попытка подключения к Google Sheets...")
            self.gc = gspread.service_account(filename=self.service_account_file)
            self.spreadsheet = self.gc.open(self.spreadsheet_name)

            self.workers_sheet = self.spreadsheet.worksheet('workers')
            self.work_entries_sheet = self.spreadsheet.worksheet('work_entries')
            self.hourly_work_entries_sheet = self.spreadsheet.worksheet('hourly_work_entries') # НОВЫЙ ЛИСТ
            self.master_shifts_sheet = self.spreadsheet.worksheet('master_shifts')
            self.settings_sheet = self.spreadsheet.worksheet('settings')

            # Проверка и создание заголовков, если нужно
            for sheet_name, headers in self._expected_headers.items():
                self._ensure_headers(getattr(self, f"{sheet_name}_sheet"), headers)

            app_logger.info(f"Успешно подключено к Google Таблице: '{self.spreadsheet_name}'")
            self._update_connection_status("Онлайн", "green")
            return True
        except Exception as e:
            app_logger.error(f"Ошибка подключения к Google Sheets: {e}")
            self._update_connection_status("Офлайн", "red")
            raise Exception(f"Ошибка подключения к Google Sheets: {e}\n"
                            "Убедитесь, что 'service_account.json' находится в той же папке, "
                            "таблица создана, названа правильно, и сервисный аккаунт имеет к ней доступ. "
                            "Также проверьте, что Google Drive API включен в Google Cloud Console.")

    def _ensure_headers(self, sheet, expected_headers):
        """Проверяет наличие заголовков и добавляет их, если лист пуст."""
        try:
            headers = sheet.row_values(1)
            current_headers = [str(h).strip() for h in headers] # Удаляем пробелы для сравнения

            if not any(current_headers) or current_headers != expected_headers:
                if not any(current_headers): # Если строка действительно пуста
                     sheet.insert_row(expected_headers, 1)
                     app_logger.info(f"Заголовки для листа '{sheet.title}' были добавлены: {expected_headers}")
                else:
                    app_logger.warning(f"Заголовки листа '{sheet.title}' не соответствуют ожидаемым. Ожидаются: {expected_headers}, Фактические: {current_headers}. Возможно, потребуется ручная корректировка.")

        except Exception as e:
            app_logger.error(f"Ошибка при проверке заголовков листа '{sheet.title}': {e}")
            self._update_connection_status("Офлайн", "red")


    def _get_col_index(self, sheet, col_name):
        """Вспомогательная функция для получения индекса колонки по имени."""
        headers = sheet.row_values(1)
        if col_name in headers:
            return headers.index(col_name) + 1
        raise ValueError(f"Колонка '{col_name}' не найдена в листе '{sheet.title}'.")

    def load_all_data_to_cache(self):
        """Загружает все данные из всех листов в локальные кэши."""
        try:
            app_logger.info("Загрузка данных из Google Sheets в кэш...")
            self._cached_workers = self.workers_sheet.get_all_records()
            self._cached_work_entries = self.work_entries_sheet.get_all_records()
            self._cached_hourly_work_entries = self.hourly_work_entries_sheet.get_all_records() # НОВЫЙ КЭШ
            self._cached_master_shifts = self.master_shifts_sheet.get_all_records()

            settings_records = self.settings_sheet.get_all_records()
            self._cached_settings = {rec['setting_name']: rec['setting_value'] for rec in settings_records if 'setting_name' in rec and 'setting_value' in rec}
            app_logger.info("Данные успешно загружены в кэш.")
            self._update_connection_status("Онлайн", "green")
        except Exception as e:
            app_logger.error(f"Ошибка загрузки данных в кэш из Google Sheets: {e}")
            self._update_connection_status("Офлайн", "red")
            raise Exception(f"Ошибка загрузки данных в кэш из Google Sheets: {e}")

    # --- Методы для чтения данных (используют кэш) ---
    def get_all_workers(self, worker_type=None):
        """Получает всех работников или работников определенного типа из кэша (как список словарей)."""
        if worker_type:
            return [d for d in self._cached_workers if d.get('type') == worker_type]
        return self._cached_workers

    def get_work_entries(self, operation_type=None, worker_id=None, start_datetime=None, end_datetime=None):
        """Получает записи о выработке по площади из кэша с фильтрацией."""
        filtered_entries = []
        for entry in self._cached_work_entries:
            match = True

            # Проверка наличия ключей, чтобы избежать KeyError
            if not all(key in entry for key in ['operation_type', 'worker_id', 'area', 'entry_datetime']):
                continue

            entry_datetime_str = entry.get('entry_datetime')

            try:
                entry_dt_obj = datetime.datetime.strptime(entry_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Попытка разобрать дату без времени, если формат не "%Y-%m-%d %H:%M:%S"
                try:
                    entry_dt_obj = datetime.datetime.strptime(entry_datetime_str, "%Y-%m-%d")
                except ValueError:
                    app_logger.warning(f"Некорректный формат даты/времени в записи в кэше: '{entry_datetime_str}'. Пропускаем запись.")
                    continue

            if operation_type and entry.get('operation_type') != operation_type:
                match = False
            if worker_id and entry.get('worker_id') != worker_id:
                match = False
            if start_datetime and entry_dt_obj < start_datetime:
                match = False
            if end_datetime and entry_dt_obj > end_datetime:
                match = False

            if match:
                filtered_entries.append(entry)
        return filtered_entries

    def get_hourly_work_entries(self, work_type=None, worker_id=None, start_datetime=None, end_datetime=None): # НОВЫЙ МЕТОД
        """Получает почасовые записи о работе из кэша с фильтрацией."""
        filtered_entries = []
        for entry in self._cached_hourly_work_entries:
            match = True

            if not all(key in entry for key in ['work_type', 'worker_id', 'hours', 'payment_amount', 'entry_datetime']):
                continue

            entry_datetime_str = entry.get('entry_datetime')
            try:
                entry_dt_obj = datetime.datetime.strptime(entry_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    entry_dt_obj = datetime.datetime.strptime(entry_datetime_str, "%Y-%m-%d")
                except ValueError:
                    app_logger.warning(f"Некорректный формат даты/времени в почасовой записи в кэше: '{entry_datetime_str}'. Пропускаем запись.")
                    continue

            if work_type and entry.get('work_type') != work_type:
                match = False
            if worker_id and entry.get('worker_id') != worker_id:
                match = False
            if start_datetime and entry_dt_obj < start_datetime:
                match = False
            if end_datetime and entry_dt_obj > end_datetime:
                match = False

            if match:
                filtered_entries.append(entry)
        return filtered_entries


    def get_master_shift_by_id(self, shift_id):
        """Получает данные о смене мастера по ID из кэша."""
        for row in self._cached_master_shifts:
            if row.get('id') == shift_id:
                return row
        return None

    def get_setting(self, setting_name, default_value=None):
        """Получает значение настройки по имени из кэша."""
        return self._cached_settings.get(setting_name, default_value)

    # --- Методы для записи данных (обновляют кэш и запускают фондовую запись) ---
    def _perform_async_write(self, target_sheet_name, update_func, success_callback, error_callback):
        """Вспомогательная функция для выполнения операций записи в отдельном потоке."""
        def run_write():
            try:
                self._update_connection_status("Сохранение...", "orange")
                result = update_func()
                self._update_connection_status("Онлайн", "green")
                if success_callback:
                    # Убедимся, что callback вызывается в основном потоке Tkinter И что app_root_ref еще существует
                    if self.app_root_ref and self.app_root_ref.winfo_exists():
                        self.app_root_ref.after(0, lambda: success_callback(result))
            except Exception as e:
                app_logger.error(f"Ошибка асинхронной записи в лист '{target_sheet_name}': {e}")
                self._update_connection_status("Ошибка сохранения", "red")
                if error_callback:
                    # Убедимся, что callback вызывается в основном потоке Tkinter И что app_root_ref еще существует
                    if self.app_root_ref and self.app_root_ref.winfo_exists():
                        self.app_root_ref.after(0, lambda: error_callback(e))
        threading.Thread(target=run_write).start()

    def add_worker(self, worker_type, name, rate_per_sqm, success_callback=None, error_callback=None):
        """Добавляет нового работника (сначала в кэш, затем асинхронно в GS)."""
        existing_ids = [d['id'] for d in self._cached_workers if 'id' in d]
        new_id = 1 if not existing_ids else max(existing_ids) + 1

        new_worker_data = {'id': new_id, 'type': worker_type, 'name': name, 'rate_per_sqm': rate_per_sqm}
        self._cached_workers.append(new_worker_data) # Обновляем кэш немедленно

        def update_gs():
            self.workers_sheet.append_row([new_id, worker_type, name, rate_per_sqm])
            return new_id

        self._perform_async_write('workers', update_gs, success_callback, error_callback)
        return new_id

    def update_worker_rate(self, worker_id, new_rate, success_callback=None, error_callback=None):
        """Обновляет ставку работника (сначала в кэш, затем асинхронно в GS)."""
        # Сначала найдем реальный row_index в Google Sheets, т.к. кэш может не совпадать из-за удалений/добавлений
        # Это не идеально, но нужно, чтобы update_cell работал точно.
        data_from_gs = self.workers_sheet.get_all_records()
        gs_row_index = -1
        for i, row in enumerate(data_from_gs):
            if row.get('id') == worker_id:
                gs_row_index = i + 2
                break

        if gs_row_index == -1:
            if error_callback: error_callback(ValueError("Работник не найден в Google Sheets для обновления."))
            return False

        # Обновляем кэш немедленно
        for i, row in enumerate(self._cached_workers):
            if row.get('id') == worker_id:
                self._cached_workers[i]['rate_per_sqm'] = new_rate
                break

        def update_gs():
            self.workers_sheet.update_cell(gs_row_index, self._get_col_index(self.workers_sheet, 'rate_per_sqm'), new_rate)
            return True

        self._perform_async_write('workers', update_gs, success_callback, error_callback)
        return True

    def delete_worker(self, worker_id, success_callback=None, error_callback=None):
        """Удаляет работника и все связанные записи о выработке (сначала из кэша, затем асинхронно из GS)."""
        # Удаляем из кэша work_entries
        self._cached_work_entries = [entry for entry in self._cached_work_entries if entry.get('worker_id') != worker_id]
        self._cached_hourly_work_entries = [entry for entry in self._cached_hourly_work_entries if entry.get('worker_id') != worker_id] # НОВОЕ: удаляем и почасовые записи

        # Удаляем из кэша workers
        worker_idx_to_delete = -1
        for i, row in enumerate(self._cached_workers):
            if row.get('id') == worker_id:
                worker_idx_to_delete = i
                break

        if worker_idx_to_delete != -1:
            del self._cached_workers[worker_idx_to_delete] # Обновляем кэш немедленно
        else:
            if error_callback: error_callback(ValueError("Работник не найден в кэше для удаления."))
            return False

        def update_gs():
            # Получаем актуальные данные для удаления из GS для work_entries (по площади)
            entries_data_from_gs = self.work_entries_sheet.get_all_records()
            rows_to_delete_entry = []
            for i, row in enumerate(entries_data_from_gs):
                if row.get('worker_id') == worker_id:
                    rows_to_delete_entry.append(i + 2)

            # Удаляем записи о выработке по площади в GS
            for row_idx in sorted(rows_to_delete_entry, reverse=True):
                self.work_entries_sheet.delete_rows(row_idx)

            # НОВОЕ: Удаляем почасовые записи в GS
            hourly_entries_data_from_gs = self.hourly_work_entries_sheet.get_all_records()
            hourly_rows_to_delete_entry = []
            for i, row in enumerate(hourly_entries_data_from_gs):
                if row.get('worker_id') == worker_id:
                    hourly_rows_to_delete_entry.append(i + 2)

            for row_idx in sorted(hourly_rows_to_delete_entry, reverse=True):
                self.hourly_work_entries_sheet.delete_rows(row_idx)


            # Удаляем работника в GS
            workers_data_from_gs = self.workers_sheet.get_all_records()
            worker_gs_row_index = -1
            for i, row in enumerate(workers_data_from_gs):
                if row.get('id') == worker_id:
                    worker_gs_row_index = i + 2
                    break

            if worker_gs_row_index != -1:
                self.workers_sheet.delete_rows(worker_gs_row_index)
            else:
                raise ValueError(f"Работник с ID {worker_id} не найден в Google Sheets для удаления.")

            return True

        self._perform_async_write('workers', update_gs, success_callback, error_callback)
        return True

    def add_work_entry(self, worker_id, operation_type, entry_datetime, width, length, quantity, area, success_callback=None, error_callback=None):
        """Добавляет запись о выработке по площади (сначала в кэш, затем асинхронно в GS)."""
        existing_ids = [d['id'] for d in self._cached_work_entries if 'id' in d]
        new_id = 1 if not existing_ids else max(existing_ids) + 1

        new_entry_data = {'id': new_id, 'worker_id': worker_id, 'operation_type': operation_type,
                          'entry_datetime': entry_datetime, 'width': width, 'length': length,
                          'quantity': quantity, 'area': area}
        self._cached_work_entries.append(new_entry_data) # Обновляем кэш немедленно

        def update_gs():
            self.work_entries_sheet.append_row([new_id, worker_id, operation_type, entry_datetime, width, length, quantity, area])
            return True

        self._perform_async_write('work_entries', update_gs, success_callback, error_callback)

    def add_hourly_work_entry(self, worker_id, work_type, entry_datetime, hours, payment_amount, success_callback=None, error_callback=None): # НОВЫЙ МЕТОД
        """Добавляет почасовую запись о работе (сначала в кэш, затем асинхронно в GS)."""
        existing_ids = [d['id'] for d in self._cached_hourly_work_entries if 'id' in d]
        new_id = 1 if not existing_ids else max(existing_ids) + 1

        new_entry_data = {'id': new_id, 'worker_id': worker_id, 'work_type': work_type,
                          'entry_datetime': entry_datetime, 'hours': hours, 'payment_amount': payment_amount}
        self._cached_hourly_work_entries.append(new_entry_data) # Обновляем кэш немедленно

        def update_gs():
            self.hourly_work_entries_sheet.append_row([new_id, worker_id, work_type, entry_datetime, hours, payment_amount])
            return True

        self._perform_async_write('hourly_work_entries', update_gs, success_callback, error_callback)

    def delete_work_entry(self, entry_id, is_hourly=False, success_callback=None, error_callback=None): # ИЗМЕНЕНО: добавлено is_hourly
        """Удаляет запись о выработке по ID (сначала из кэша, затем асинхронно из GS)."""

        target_cache = self._cached_hourly_work_entries if is_hourly else self._cached_work_entries
        target_sheet = self.hourly_work_entries_sheet if is_hourly else self.work_entries_sheet

        # Удаляем из кэша
        entry_idx_to_delete = -1
        for i, entry in enumerate(target_cache):
            if entry.get('id') == entry_id:
                entry_idx_to_delete = i
                break

        if entry_idx_to_delete != -1:
            del target_cache[entry_idx_to_delete] # Обновляем кэш немедленно
        else:
            if error_callback: error_callback(ValueError(f"Запись ID {entry_id} {'(почасовая)' if is_hourly else '(по площади)'} не найдена в кэше для удаления."))
            return False

        def update_gs():
            # Находим row_index в Google Sheets
            records_from_gs = target_sheet.get_all_records()
            gs_row_index = -1
            for i, record in enumerate(records_from_gs):
                if record.get('id') == entry_id:
                    gs_row_index = i + 2 # +2 для заголовка и 1-индексации
                    break

            if gs_row_index != -1:
                target_sheet.delete_rows(gs_row_index)
            else:
                raise ValueError(f"Запись ID {entry_id} {'(почасовая)' if is_hourly else '(по площади)'} не найдена в Google Sheets для удаления.")
            return True

        self._perform_async_write('work_entries' if not is_hourly else 'hourly_work_entries', update_gs, success_callback, error_callback)
        return True

    def add_master_shift(self, start_time, success_callback=None, error_callback=None):
        """Добавляет новую запись о начале смены мастера (сначала в кэш, затем асинхронно в GS)."""
        existing_ids = [d['id'] for d in self._cached_master_shifts if 'id' in d]
        new_id = 1 if not existing_ids else max(existing_ids) + 1

        new_shift_data = {'id': new_id, 'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
                          'end_time': '', 'duration_hours': '', 'master_salary': '',
                          'ra_output_sqm': '', 'up_output_sqm': '', 'ob_output_sqm': '', 'gr_output_sqm': ''}
        self._cached_master_shifts.append(new_shift_data) # Обновляем кэш немедленно

        def update_gs():
            self.master_shifts_sheet.append_row([new_id, new_shift_data['start_time'], "", "", "", "", "", "", ""])
            return new_id

        self._perform_async_write('master_shifts', update_gs, success_callback, error_callback)
        return new_id

    def update_master_shift_end_data(self, shift_id, end_time, duration_hours, master_salary,
                                     ra_output_sqm, up_output_sqm, ob_output_sqm, gr_output_sqm,
                                     success_callback=None, error_callback=None):
        """Обновляет запись о смене мастера данными о завершении (сначала в кэш, затем асинхронно в GS)."""
        # Находим row_index в Google Sheets
        data_from_gs = self.master_shifts_sheet.get_all_records()
        gs_row_index = -1
        for i, row in enumerate(data_from_gs):
            if row.get('id') == shift_id:
                gs_row_index = i + 2
                break

        if gs_row_index == -1:
            if error_callback: error_callback(ValueError("Смена мастера не найдена в Google Sheets для обновления."))
            return False

        # Обновляем кэш немедленно
        for i, row in enumerate(self._cached_master_shifts):
            if row.get('id') == shift_id:
                self._cached_master_shifts[i]['end_time'] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                self._cached_master_shifts[i]['duration_hours'] = f"{duration_hours:.2f}"
                self._cached_master_shifts[i]['master_salary'] = f"{master_salary:.2f}"
                self._cached_master_shifts[i]['ra_output_sqm'] = f"{ra_output_sqm:.2f}"
                self._cached_master_shifts[i]['up_output_sqm'] = f"{up_output_sqm:.2f}"
                self._cached_master_shifts[i]['ob_output_sqm'] = f"{ob_output_sqm:.2f}"
                self._cached_master_shifts[i]['gr_output_sqm'] = f"{gr_output_sqm:.2f}"
                break

        def update_gs():
            self.master_shifts_sheet.update(f'C{gs_row_index}:I{gs_row_index}', [[
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                f"{duration_hours:.2f}",
                f"{master_salary:.2f}",
                f"{ra_output_sqm:.2f}",
                f"{up_output_sqm:.2f}",
                f"{ob_output_sqm:.2f}",
                f"{gr_output_sqm:.2f}"
            ]])
            return True

        self._perform_async_write('master_shifts', update_gs, success_callback, error_callback)
        return True

    def update_setting(self, setting_name, new_value, success_callback=None, error_callback=None):
        """Обновляет или добавляет значение настройки (сначала в кэш, затем асинхронно в GS)."""

        # Обновляем кэш немедленно
        self._cached_settings[setting_name] = new_value

        # Придется получить актуальный список строк для поиска в GS, т.к. кэш может не совпадать
        records_from_gs = self.settings_sheet.get_all_records()
        row_index_in_gs = -1
        for i, record in enumerate(records_from_gs):
            if record.get('setting_name') == setting_name:
                row_index_in_gs = i + 2 # +2 для заголовка и 1-индексации
                break

        def update_gs():
            if row_index_in_gs != -1:
                self.settings_sheet.update_cell(row_index_in_gs, self._get_col_index(self.settings_sheet, 'setting_value'), new_value)
            else:
                self.settings_sheet.append_row([setting_name, new_value])
            return True

        self._perform_async_write('settings', update_gs, success_callback, error_callback)
        return True


# --- Основной класс приложения Tkinter ---
class WorkshopMasterApp:
    MASTER_HOURLY_RATE = 250.0
    DIRECTOR_NAME = "Брежнев А.А."

    DAILY_INSIGHTS = [
        "Мастер, сосредоточьтесь на качестве, а не на количестве! Иначе количество будет некачественным.",
        "Порядок на рабочем месте – залог эффективной работы. Начните с него!",
        "Делайте перерывы! Отдохнувший разум работает продуктивнее.",
        "Каждая маленькая победа ведет к большому успеху. Отмечайте их!",
        "Общайтесь с командой. Открытый диалог решает многие проблемы.",
        "Не откладывайте на завтра то, что можно сделать сегодня, особенно если это касается порядка.",
        "Будьте примером для своей команды. Ваш настрой влияет на всех.",
        "Измеряйте, чтобы управлять. Без цифр это просто мнение.",
        "Инновации начинаются с маленьких улучшений. Ищите их каждый день."
    ]

    def __init__(self, master):
        self.master = master
        master.title("ООО ПК Спектр Сводка Мастера")
        master.geometry("1000x700")
        master.resizable(True, True)

        self.db = GoogleSheetsDatabase("Мастер Цеха Данные") # Инициализируем DB объект здесь, ссылки на UI позже
        self.operation_types = ["Раскройщики", "Упаковщицы", "Обработка", "Грузчики"]
        self.hourly_work_types = ["Уборка", "Мойка"] # НОВЫЙ ТИПЫ РАБОТ
        self.worker_lists = {} # Будет заполняться из кэша DB

        self.current_theme = self._load_theme()
        self.font_size_scale = 1.0

        self.styles = {
            "light": {
                "bg": "#f0f0f0", "fg": "#333333", "menu_bg": "#333333", "menu_fg": "white",
                "button_bg": "#555555", "button_fg": "white", "label_fg": "#333333",
                "frame_bg": "#f0f0f0", "label_frame_bg": "#f0f0f0",
                "entry_bg": "white", "entry_fg": "black", "placeholder_fg": "grey"
            },
            "dark": {
                "bg": "#2c2c2c", "fg": "#ffffff", "menu_bg": "#1c1c1c", "menu_fg": "white",
                "button_bg": "#444444", "button_fg": "white", "label_fg": "#ffffff",
                "frame_bg": "#2c2c2c", "label_frame_bg": "#2c2c2c",
                "entry_bg": "#444444", "entry_fg": "white", "placeholder_fg": "darkgrey"
            }
        }

        self.current_screen_type = None

        # Настройка grid-лейаута для master
        self.master.grid_rowconfigure(0, weight=0) # Для top_bar_frame (фиксированная высота)
        self.master.grid_rowconfigure(1, weight=1) # Для main_content_area (растягивается)
        self.master.grid_columnconfigure(0, weight=0) # Для menu_frame (фиксированная ширина)
        self.master.grid_columnconfigure(1, weight=1) # Для top_bar_frame и main_content_area (растягивается)

        self.menu_frame = tk.Frame(master, width=200)
        self.menu_frame.grid(row=0, column=0, sticky="nswe", rowspan=2) # menu_frame занимает две строки
        self.menu_frame.grid_propagate(False) # Не позволяет фрейму сжиматься по содержимому

        self.top_bar_frame = tk.Frame(master) # Этот фрейм будет всегда сверху справа
        self.top_bar_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=0) # Прикреплен к row 0, col 1

        self.main_content_area = tk.Frame(master) # Этот фрейм будет очищаться и заполняться
        self.main_content_area.grid(row=1, column=1, sticky="nswe", padx=10, pady=10) # Прикреплен к row 1, col 1

        self.shift_status_file = "master_shift_status.json"
        self.current_master_shift = None

        self.master.config(bg=self.styles[self.current_theme]["bg"])
        self.menu_frame.config(bg=self.styles[self.current_theme]["menu_bg"])
        self.top_bar_frame.config(bg=self.styles[self.current_theme]["bg"])
        self.main_content_area.config(bg=self.styles[self.current_theme]["bg"])

        self.insight_frame_visible = True
        self.current_insight_index = random.randint(0, len(self.DAILY_INSIGHTS) - 1)

        self.screen_history = []
        self.current_history_index = -1
        self.is_history_navigation = False

        master.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Переменные для прокрутки индивидуальной выработки
        self.individual_output_canvas = None
        self.individual_output_frame_in_canvas = None # Переименовано для ясности
        self.individual_output_frame_window_id = None # ID окна, созданного в Canvas

        self.last_entry_info_label = None
        self.connection_status_label = None # Инициализируем здесь
        self.cache_refresh_job = None

        # Переменные для отслеживания состояния сворачиваемых секций
        self.is_area_input_collapsed = False # Начальное состояние: развернут
        self.is_hourly_input_collapsed = False # Начальное состояние: развернут

    def _get_scaled_font(self, base_size, style="normal"):
        """Возвращает масштабированный шрифт."""
        return ('Arial', int(base_size * self.font_size_scale), style)

    def _post_splash_setup(self):
        """
        Вызывается после того, как сплэш-экран исчезнет и данные будут загружены в кэш.
        Здесь происходит окончательная инициализация UI и связывание DB с UI элементами.
        """
        try:
            app_logger.info("Начало пост-инициализации приложения.")
            # Создаем top_bar. Он уже имеет свой постоянный фрейм: self.top_bar_frame
            self._create_top_bar()

            # Передаем ссылки на UI элементы в DB объект
            # self.connection_status_label гарантированно создан в _create_top_bar
            self.db.set_ui_references(self.master, self.connection_status_label)

            # Теперь, когда UI ссылки установлены и DB подключена/кэширована:
            loaded_scale = float(self.db.get_setting('font_size_scale', default_value="1.0"))
            self.font_size_scale = loaded_scale

            # Эти вызовы запускают асинхронную запись, UI не блокируется
            # При первом запуске или отсутствии настроек, они будут записаны со значениями по умолчанию.
            # Важно: здесь мы не требуем пароля для входа, но настройка 'password' может быть использована,
            # если в будущем будет включена функция блокировки при запуске.
            if self.db.get_setting('password') is None:
                self.db.update_setting('password', "533")
                app_logger.info("Пароль по умолчанию для входа установлен (но не используется при запуске).")
            if self.db.get_setting('salary_password') is None:
                self.db.update_setting('salary_password', "2025")
                app_logger.info("Пароль по умолчанию для зарплаты установлен.")
            if self.db.get_setting('font_size_scale') is None:
                self.db.update_setting('font_size_scale', "1.0")
                app_logger.info("Масштаб шрифта по умолчанию установлен.")
            # НОВЫЕ НАСТРОЙКИ ДЛЯ ЧАСОВОЙ ОПЛАТЫ
            if self.db.get_setting('cleaning_rate_per_hour') is None:
                self.db.update_setting('cleaning_rate_per_hour', "300.0")
                app_logger.info("Ставка уборки по умолчанию установлена.")
            if self.db.get_setting('washing_rate_per_hour') is None:
                self.db.update_setting('washing_rate_per_hour', "400.0")
                app_logger.info("Ставка мойки по умолчанию установлена.")

            self._load_all_workers_from_db_cache()
            self.current_master_shift = self._load_master_shift_status()

            # --- Вход в приложение теперь без пароля при старте ---
            app_logger.info("Приложение запускается без пароля на входе.")
            # Логика, которая была здесь для _show_login_dialog(), теперь пропущена.
            # --- Конец изменений ---

            self.apply_theme(self.current_theme) # apply_theme пересоздает меню, но не content_frame

            self.show_screen("Раскройщики", is_initial_load=False) # Теперь это обычный вызов, UI уже готов

            # Запускаем периодическое обновление кэша (каждые 5 минут)
            self._start_cache_refresh(300) # 300 секунд = 5 минут
            app_logger.info("Фоновое обновление кэша запущено.")

        except Exception as e:
            app_logger.critical(f"Критическая ошибка при пост-инициализации приложения: {e}")
            messagebox.showerror("Ошибка", f"Критическая ошибка базы данных при инициализации UI: {e}\nПриложение будет закрыто.", parent=self.master)
            self.master.destroy()

    # УДАЛЕНА функция _show_login_dialog(), так как она больше не используется.

    def _start_cache_refresh(self, interval_seconds):
        """Запускает периодическое обновление кэша."""
        def refresh_job():
            try:
                self.db.load_all_data_to_cache()
                app_logger.info(f"Кэш обновлен в фоне. Следующее обновление через {interval_seconds} секунд.")
            except Exception as e:
                app_logger.error(f"Ошибка фонового обновления кэша: {e}")
            finally:
                # Перезапускаем таймер, только если приложение еще не уничтожено
                if self.master.winfo_exists():
                    self.cache_refresh_job = self.master.after(interval_seconds * 1000, refresh_job)

        # Запускаем первый таймер
        if self.master.winfo_exists():
            self.cache_refresh_job = self.master.after(interval_seconds * 1000, refresh_job)

    def _on_closing(self):
        """Обработчик закрытия приложения, спрашивает о сохранении данных и завершает работу."""
        if messagebox.askyesno("Выход из приложения", "Вы уверены, что хотите выйти? Все данные, введенные сегодня, автоматически сохраняются в облаке.", parent=self.master):
            self._save_master_shift_status()
            if self.cache_refresh_job:
                self.master.after_cancel(self.cache_refresh_job) # Отменяем фоновое обновление
            app_logger.info("Приложение завершает работу.")
            self.master.destroy()
        # Если пользователь нажал "Нет", ничего не делаем, окно не закрывается.


    def _load_master_shift_status(self):
        """Загружает статус активной смены мастера из файла."""
        if os.path.exists(self.shift_status_file):
            try:
                with open(self.shift_status_file, "r") as f:
                    data = json.load(f)
                    if data and 'id' in data and 'start_time' in data:
                        if data['start_time']:
                            data['start_time'] = datetime.datetime.strptime(data['start_time'], "%Y-%m-%d %H:%M:%S")
                            app_logger.info(f"Статус активной смены мастера загружен из файла: ID={data['id']}, StartTime={data['start_time']}")
                            return data
            except (json.JSONDecodeError, ValueError) as e:
                app_logger.error(f"Ошибка чтения файла статуса смены '{self.shift_status_file}': {e}. Файл будет удален.")
                os.remove(self.shift_status_file) # Удаляем поврежденный файл
        app_logger.info("Файл статуса смены мастера не найден или пуст.")
        return None

    def _save_master_shift_status(self):
        """Сохраняет статус активной смены мастера в файл."""
        if self.current_master_shift and self.current_master_shift.get('start_time'):
            data = {
                'id': self.current_master_shift['id'],
                'start_time': self.current_master_shift['start_time'].strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                with open(self.shift_status_file, "w") as f:
                    json.dump(data, f)
                app_logger.info(f"Статус активной смены мастера сохранен в файл: ID={data['id']}")
            except IOError as e:
                app_logger.error(f"Ошибка сохранения статуса смены в файл '{self.shift_status_file}': {e}")
        elif os.path.exists(self.shift_status_file):
            try:
                os.remove(self.shift_status_file)
                app_logger.info(f"Файл статуса смены мастера '{self.shift_status_file}' удален (смена не активна).")
            except OSError as e:
                app_logger.error(f"Ошибка удаления файла статуса смены '{self.shift_status_file}': {e}")


    def _update_shift_buttons_state(self):
        """Обновляет состояние кнопок Начало/Конец смены."""
        if hasattr(self, 'start_shift_button') and hasattr(self, 'end_shift_button'):
            if self.current_master_shift:
                self.start_shift_button.config(state="disabled")
                self.end_shift_button.config(state="normal")
            else:
                self.start_shift_button.config(state="normal")
                self.end_shift_button.config(state="disabled")

    def _update_history_buttons_state(self):
        """Обновляет состояние кнопок Назад/Вперед."""
        if hasattr(self, 'back_button') and hasattr(self, 'forward_button'):
            self.back_button.config(state="normal" if self.current_history_index > 0 else "disabled")
            self.forward_button.config(state="normal" if self.current_history_index < len(self.screen_history) - 1 else "disabled")


    def _load_all_workers_from_db_cache(self):
        """Загружает списки работников из кэша Google Sheets."""
        for op_type in self.operation_types:
            self.worker_lists[op_type] = self.db.get_all_workers(op_type)
        # Для почасовых работ тоже нужно загрузить всех работников (без фильтра по типу)
        self.worker_lists['Почасовая'] = self.db.get_all_workers()
        app_logger.info("Списки работников загружены из кэша для использования в UI.")

    def _load_theme(self):
        try:
            with open("theme_settings.txt", "r") as f:
                theme = f.read().strip()
                if theme in ["light", "dark"]:
                    app_logger.info(f"Тема '{theme}' загружена из файла.")
                    return theme
        except FileNotFoundError:
            app_logger.info("Файл 'theme_settings.txt' не найден, используется тема по умолчанию (light).")
        except Exception as e:
            app_logger.error(f"Ошибка чтения файла темы 'theme_settings.txt': {e}. Используется тема по умолчанию (light).")
        return "light"

    def _save_theme(self):
        try:
            with open("theme_settings.txt", "w") as f:
                f.write(self.current_theme)
            app_logger.info(f"Тема '{self.current_theme}' сохранена в файл 'theme_settings.txt'.")
        except IOError as e:
            app_logger.error(f"Ошибка сохранения темы в файл 'theme_settings.txt': {e}")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        self._save_theme()
        app_logger.info(f"Применена тема: '{theme_name}'.")

        colors = self.styles[theme_name]

        self.master.config(bg=colors["bg"])
        self.menu_frame.config(bg=colors["menu_bg"])
        self.top_bar_frame.config(bg=colors["bg"]) # Обновляем цвет top_bar_frame
        self.main_content_area.config(bg=colors["bg"]) # Обновляем цвет main_content_area

        self.ttk_style = ttk.Style()
        self.ttk_style.theme_use("default")
        # Переопределяем стили для combobox и treeview, чтобы они использовали цвета темы
        self.ttk_style.configure("TCombobox",
                                 fieldbackground=colors["entry_bg"],
                                 background=colors["entry_bg"],
                                 foreground=colors["entry_fg"],
                                 font=self._get_scaled_font(12))
        self.ttk_style.map('TCombobox', fieldbackground=[('readonly', colors["entry_bg"])],
                                         selectbackground=[('readonly', colors["button_bg"])],
                                         selectforeground=[('readonly', colors["button_fg"])]) # Цвет текста при выборе

        self.ttk_style.configure("Treeview",
                                 background=colors["entry_bg"],
                                 foreground=colors["entry_fg"],
                                 fieldbackground=colors["entry_bg"],
                                 font=self._get_scaled_font(12))
        self.ttk_style.map('Treeview',
                           background=[('selected', '#347083' if self.current_theme == "light" else "#666666")],
                           foreground=[('selected', 'white' if self.current_theme == "light" else "#ffffff")]) # Цвет текста при выборе
        self.ttk_style.configure("Treeview.Heading",
                                 background=colors["button_bg"],
                                 foreground=colors["button_fg"],
                                 font=self._get_scaled_font(12, 'bold'))

        self.ttk_style.configure("TScrollbar",
                                 background=colors["button_bg"], # Фон скроллбара
                                 troughcolor=colors["entry_bg"], # Цвет желоба
                                 gripcount=0, # Количество "ручек" для перемещения
                                 relief="flat",
                                 arrowsize=0) # Размер стрелок (делаем 0, чтобы их не было)
        self.ttk_style.map("TScrollbar",
                           background=[('active', colors["button_bg"])]) # Цвет при наведении

        # Меню всегда пересоздается при смене темы
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        self._create_menu_buttons(self.menu_frame)
        self._update_shift_buttons_state()
        self._update_history_buttons_state()

        # Обновляем top_bar (его дочерние элементы) и текущий экран
        self._create_top_bar() # Пересоздаем элементы top_bar для применения темы
        if self.current_screen_type:
            temp_is_history_navigation = self.is_history_navigation
            self.is_history_navigation = True # Чтобы не добавлять в историю при смене темы
            self.show_screen(self.current_screen_type, is_initial_load=False)
            self.is_history_navigation = temp_is_history_navigation

        # Обновляем статус соединения для соответствия новой теме
        if self.db.status_indicator_ref and self.db.status_indicator_ref.winfo_exists():
            self.db.status_indicator_ref.config(bg=colors["bg"])


    def toggle_theme(self):
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def _create_menu_buttons(self, parent_frame):
        colors = self.styles[self.current_theme]
        main_button_width = 25
        main_button_height = 2
        main_button_font = self._get_scaled_font(12, 'bold') # Сделаем кнопки меню жирными
        main_button_style = {'fg': colors["menu_fg"],
                             'bg': colors["button_bg"],
                             'font': main_button_font, 'width': main_button_width, 'height': main_button_height,
                             'bd': 0, 'relief': 'flat', 'activebackground': '#777777' if self.current_theme == "light" else '#333333'} # Убираем стандартные границы, добавляем активный цвет

        tk.Label(parent_frame, text="ООО ПК Спектр", font=self._get_scaled_font(16, 'bold'),
                 bg=colors["menu_bg"], fg=colors["menu_fg"]).pack(pady=(20, 5), padx=10, fill='x')
        tk.Label(parent_frame, text="Мастер: Половых Е.", font=self._get_scaled_font(14, 'italic'),
                 bg=colors["menu_bg"], fg=colors["menu_fg"]).pack(pady=(0, 20), padx=10, fill='x')

        # Справка - отдельная, менее заметная кнопка
        tk.Button(parent_frame, text="Справка", command=lambda: self.show_screen("Справка"),
                  font=self._get_scaled_font(10), bg='#888888', fg='white',
                  width=main_button_width, height=1, bd=0, relief='flat', activebackground='#666666').pack(pady=(10, 5), padx=10, fill='x')


        # Кнопки операций
        tk.Button(parent_frame, text="Учет: Раскройщики", command=lambda: self.show_screen("Раскройщики"), **main_button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(parent_frame, text="Учет: Упаковщицы", command=lambda: self.show_screen("Упаковщицы"), **main_button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(parent_frame, text="Учет: Обработка", command=lambda: self.show_screen("Обработка"), **main_button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(parent_frame, text="Учет: Грузчики", command=lambda: self.show_screen("Грузчики"), **main_button_style).pack(pady=5, padx=10, fill='x')

        # Разделитель
        tk.Frame(parent_frame, height=2, bg=colors["fg"]).pack(pady=10, padx=10, fill='x')

        # Настройки
        tk.Button(parent_frame, text="Настройки", command=lambda: self.show_screen("Настройки"), **main_button_style).pack(pady=5, padx=10, fill='x')

        tk.Frame(parent_frame, bg=colors["menu_bg"], height=1).pack(expand=True, fill="both", pady=0) # Растягивающийся фрейм

        # Кнопки начала/конца смены
        self.start_shift_button = tk.Button(parent_frame, text="Начало смены", command=self._start_master_shift,
                                            font=self._get_scaled_font(12, 'bold'), bg='#4CAF50', fg='white',
                                            width=main_button_width, height=main_button_height, bd=0, relief='raised', activebackground='#3D8B40')
        self.start_shift_button.pack(pady=5, padx=10, fill='x')
        self.end_shift_button = tk.Button(parent_frame, text="Конец смены", command=self._end_master_shift,
                                          font=self._get_scaled_font(12, 'bold'), bg='#f44336', fg='white',
                                          width=main_button_width, height=main_button_height, bd=0, relief='raised', activebackground='#C4332A')
        self.end_shift_button.pack(pady=5, padx=10, fill='x')

        self._update_shift_buttons_state()

    def _start_master_shift(self):
        """Обработка начала смены мастера."""
        if self.current_master_shift and self.current_master_shift.get('start_time'):
            messagebox.showwarning("Ошибка", "Смена уже начата. Завершите текущую смену перед началом новой.", parent=self.master)
            app_logger.warning("Попытка начать смену, когда другая смена уже активна.")
            return

        confirm = messagebox.askyesno("Начало смены", "Начать смену для мастера?", parent=self.master)
        if confirm:
            start_time = datetime.datetime.now()
            def success_cb(shift_id):
                messagebox.showinfo("Смена начата", f"Смена мастера успешно начата в {start_time.strftime('%Y-%m-%d %H:%M:%S')}.\nНачисление зарплаты начато.", parent=self.master)
                self._update_shift_buttons_state()
                app_logger.info(f"Смена мастера успешно начата. ID смены: {shift_id}, Начало: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            def error_cb(e):
                messagebox.showerror("Ошибка БД", f"Не удалось начать смену мастера (асинхронная запись): {e}", parent=self.master)
                app_logger.error(f"Не удалось начать смену мастера (асинхронная запись): {e}")
                self.db.load_all_data_to_cache() # Попытка синхронизировать кэш обратно

            try:
                shift_id = self.db.add_master_shift(start_time, success_cb, error_cb)
                self.current_master_shift = {'id': shift_id, 'start_time': start_time}
                self._save_master_shift_status() # Это сохраняется локально
            except Exception as e:
                app_logger.error(f"Ошибка при старте смены (кэш): {e}")
                messagebox.showerror("Ошибка", f"Ошибка при старте смены (кэш): {e}", parent=self.master)


    def _end_master_shift(self):
        """Обработка конца смены мастера и отображение сводки."""
        if not self.current_master_shift or not self.current_master_shift.get('start_time'):
            messagebox.showwarning("Ошибка", "Смена не начата. Нажмите 'Начало смены' сначала.", parent=self.master)
            app_logger.warning("Попытка завершить смену, когда смена не была активна.")
            return

        confirm = messagebox.askyesno("Конец смены", "Завершить текущую смену мастера?", parent=self.master)
        if not confirm:
            return

        end_time = datetime.datetime.now()
        start_time = self.current_master_shift['start_time']

        duration = end_time - start_time
        duration_hours = duration.total_seconds() / 3600

        shift_ra_output = 0.0
        shift_up_output = 0.0
        shift_ob_output = 0.0
        shift_gr_output = 0.0

        try:
            # Получаем записи о выработке из КЭША
            all_work_entries_in_shift = self.db.get_work_entries(
                start_datetime=start_time,
                end_datetime=end_time
            )

            for entry in all_work_entries_in_shift:
                area = float(entry.get('area', 0.0))
                operation_type = entry.get('operation_type')

                if operation_type == "Раскройщики":
                    shift_ra_output += area
                elif operation_type == "Упаковщицы":
                    shift_up_output += area
                elif operation_type == "Обработка":
                    shift_ob_output += area
                elif operation_type == "Грузчики":
                    shift_gr_output += area
        except Exception as e:
            app_logger.error(f"Ошибка при расчете выработки за смену (из кэша): {e}")
            messagebox.showerror("Ошибка", f"Ошибка при расчете выработки за смену (из кэша): {e}", parent=self.master)
            shift_ra_output, shift_up_output, shift_ob_output, shift_gr_output = 0.0, 0.0, 0.0, 0.0

        master_salary = duration_hours * self.MASTER_HOURLY_RATE

        summary_message = (
            f"Смена завершена!\n"
            f"Начало: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Конец: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Длительность смены: {duration_hours:.2f} часов\n\n"
            f"Общая выработка за смену:\n"
            f" Раскройщики: {shift_ra_output:.2f} м²\n"
            f" Упаковщицы: {shift_up_output:.2f} м²\n"
            f" Обработка: {shift_ob_output:.2f} м²\n"
            f" Грузчики: {shift_gr_output:.2f} м²\n\n"
            f"Зарплата мастера за смену: {master_salary:.2f} руб."
        )

        messagebox.showinfo("Сводка смены", summary_message, parent=self.master)
        app_logger.info(f"Смена мастера завершена. Начало: {start_time}, Конец: {end_time}, Длительность: {duration_hours:.2f}ч, ЗП: {master_salary:.2f} руб.")
        app_logger.info(f"Выработка за смену - Раскройщики: {shift_ra_output:.2f} м², Упаковщицы: {shift_up_output:.2f} м², Обработка: {shift_ob_output:.2f} м², Грузчики: {shift_gr_output:.2f} м²")


        def success_cb(result):
            self._update_shift_buttons_state()
            self.db.load_all_data_to_cache() # Перезагружаем кэш после записи
            self._show_end_shift_export_dialog(start_time, end_time) # Вызов диалога экспорта
            app_logger.info("Данные о завершенной смене успешно сохранены в Google Sheets.")
        def error_cb(e):
            messagebox.showerror("Ошибка БД", f"Не удалось сохранить данные о смене в Google Sheets (асинхронная запись): {e}", parent=self.master)
            app_logger.error(f"Не удалось сохранить данные о смене в Google Sheets (асинхронная запись): {e}")
            self.db.load_all_data_to_cache() # Попытка синхронизировать кэш обратно

        try:
            # Обновляем в БД асинхронно
            self.db.update_master_shift_end_data(
                self.current_master_shift['id'],
                end_time,
                duration_hours,
                master_salary,
                shift_ra_output,
                shift_up_output,
                ob_output_sqm,
                gr_output_sqm,
                success_cb, error_cb
            )
            # Сразу очищаем текущую смену для UI
            self.current_master_shift = None
            self._save_master_shift_status()
            self._update_shift_buttons_state()
        except Exception as e:
            app_logger.error(f"Ошибка при завершении смены (кэш): {e}")
            messagebox.showerror("Ошибка", f"Ошибка при завершении смены (кэш): {e}", parent=self.master)

    def _show_end_shift_export_dialog(self, shift_start_time, shift_end_time):
        """Показывает диалог с опциями экспорта после завершения смены."""
        app_logger.info("Открыт диалог экспорта сводок после завершения смены.")
        export_window = tk.Toplevel(self.master)
        export_window.title("Экспорт сводок")
        export_window.transient(self.master)
        export_window.grab_set()

        colors = self.styles[self.current_theme]
        export_window.config(bg=colors["bg"])

        tk.Label(export_window, text="Сохранить сводку выработки?", font=self._get_scaled_font(14, 'bold'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=15)

        def export_shift_summary():
            self._export_shift_summary_to_csv(shift_start_time, shift_end_time)
            export_window.destroy()

        def export_weekly_summary():
            self._export_weekly_summary_to_csv()
            export_window.destroy()

        tk.Button(export_window, text="Экспорт сводки текущей смены (CSV)", command=export_shift_summary,
                  font=self._get_scaled_font(12), bg='#28A745', fg='white', bd=0, relief='raised', activebackground='#228B22').pack(pady=5, padx=20, fill='x')
        tk.Button(export_window, text="Экспорт сводки за последние 7 дней (CSV)", command=export_weekly_summary,
                  font=self._get_scaled_font(12), bg='#28A745', fg='white', bd=0, relief='raised', activebackground='#228B22').pack(pady=5, padx=20, fill='x')
        tk.Button(export_window, text="Закрыть", command=export_window.destroy,
                  font=self._get_scaled_font(12), bg='#FFC107', fg='white', bd=0, relief='raised', activebackground='#DBA700').pack(pady=10, padx=20, fill='x')

    def _export_to_csv(self, data, fieldnames, default_filename, title):
        """Универсальная функция для экспорта данных в CSV."""
        app_logger.info(f"Открыт диалог сохранения файла CSV: '{default_filename}'.")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename,
            title=title,
            parent=self.master
        )
        if not filepath:
            app_logger.info("Экспорт CSV отменен пользователем.")
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f: # utf-8-sig для Excel
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            messagebox.showinfo("Экспорт", f"Отчет успешно сохранен в файл:\n{os.path.abspath(filepath)}", parent=self.master)
            app_logger.info(f"Отчет успешно сохранен в файл: '{os.path.abspath(filepath)}'.")
        except Exception as e:
            app_logger.error(f"Ошибка при экспорте в CSV файл '{filepath}': {e}")
            messagebox.showerror("Ошибка экспорта", f"Не удалось сохранить файл CSV: {e}", parent=self.master)

    def _export_shift_summary_to_csv(self, start_time, end_time):
        """Собирает и экспортирует сводку за текущую смену."""
        app_logger.info(f"Начало экспорта сводки текущей смены (начало: {start_time}, конец: {end_time}).")
        export_data = []

        # Общая выработка по цехам за смену
        total_shift_output = {op_type: 0.0 for op_type in self.operation_types}

        # Индивидуальная выработка за смену (по площади и почасовая)
        individual_shift_output = {} # {worker_id: {'name': name, 'type': type, 'area': 0.0, 'hourly_payment': 0.0}}

        all_work_entries_in_shift = self.db.get_work_entries(
            start_datetime=start_time,
            end_datetime=end_time
        )
        all_hourly_work_entries_in_shift = self.db.get_hourly_work_entries( # НОВОЕ
            start_datetime=start_time,
            end_datetime=end_time
        )

        # Обработка записей по площади
        for entry in all_work_entries_in_shift:
            area = float(entry.get('area', 0.0))
            operation_type = entry.get('operation_type')
            worker_id = entry.get('worker_id')

            total_shift_output[operation_type] += area

            worker_name = ""
            for w_data in self.db.get_all_workers(): # ИЗМЕНЕНО: теперь w_data - это словарь
                if w_data.get('id') == worker_id:
                    worker_name = w_data.get('name')
                    break

            if worker_id not in individual_shift_output:
                individual_shift_output[worker_id] = {'name': worker_name, 'type': operation_type, 'area': 0.0, 'hourly_payment': 0.0}
            individual_shift_output[worker_id]['area'] += area

        # НОВОЕ: Обработка почасовых записей
        for entry in all_hourly_work_entries_in_shift:
            payment = float(entry.get('payment_amount', 0.0))
            work_type = entry.get('work_type') # Уборка/Мойка
            worker_id = entry.get('worker_id')

            # Для общей сводки по цехам можно добавить, если нужно, или отдельно вести
            # Для простоты, пока оставим общую выработку по цехам только по площади

            worker_name = ""
            for w_data in self.db.get_all_workers(): # ИЗМЕНЕНО: теперь w_data - это словарь
                if w_data.get('id') == worker_id:
                    worker_name = w_data.get('name')
                    break

            if worker_id not in individual_shift_output:
                 # Если работник выполнял только почасовую работу, его тоже надо добавить
                individual_shift_output[worker_id] = {'name': worker_name, 'type': work_type, 'area': 0.0, 'hourly_payment': 0.0}

            individual_shift_output[worker_id]['hourly_payment'] += payment
            # Также можно добавить выработку по типу почасовой работы к общей сумме, если это нужно для "цехов"
            # if work_type not in total_shift_output: total_shift_output[work_type] = 0.0
            # total_shift_output[work_type] += payment # Если хотим считать деньги как "выработку"


        # Записываем общие итоги по цехам (только площадь)
        export_data.append({"Категория/Работник": "Общая сводка за смену (по площади)", "Значение": ""})
        for op_type, total_area in total_shift_output.items():
            export_data.append({"Категория/Работник": f" Итого по цеху '{op_type}'", "Значение": f"{total_area:.2f} м²"})

        export_data.append({"Категория/Работник": "", "Значение": ""}) # Пустая строка для разделения

        # Записываем индивидуальную выработку (площадь и почасовая оплата)
        export_data.append({"Категория/Работник": "Индивидуальная выработка за смену:", "Значение": ""})
        sorted_individuals = sorted(individual_shift_output.values(), key=lambda x: (x['type'], x['name']))
        for worker_info in sorted_individuals:
            area_str = f"{worker_info['area']:.2f} м²" if worker_info['area'] > 0 else ""
            hourly_pay_str = f"{worker_info['hourly_payment']:.2f} руб. (почас.)" if worker_info['hourly_payment'] > 0 else ""

            combined_str = []
            if area_str: combined_str.append(area_str)
            if hourly_pay_str: combined_str.append(hourly_pay_str)

            if combined_str:
                export_data.append({"Категория/Работник": f" {worker_info['name']} ({worker_info['type']})",
                                    "Значение": " / ".join(combined_str)})

        fieldnames = ["Категория/Работник", "Значение"]
        filename = f"Сводка_смены_{start_time.strftime('%Y%m%d_%H%M%S')}.csv"
        self._export_to_csv(export_data, fieldnames, filename, "Сохранить сводку текущей смены")

    def _export_weekly_summary_to_csv(self):
        """Собирает и экспортирует сводку за последние 7 дней."""
        app_logger.info("Начало экспорта сводки за последние 7 дней.")
        export_data = []
        today = datetime.datetime.now()
        seven_days_ago_start = (today - datetime.timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Общая выработка по цехам за неделю
        total_weekly_output = {op_type: 0.0 for op_type in self.operation_types}

        # Индивидуальная выработка за неделю (площадь и почасовая)
        individual_weekly_output = {} # {worker_id: {'name': name, 'type': type, 'area': 0.0, 'hourly_payment': 0.0}}

        all_work_entries_in_week = self.db.get_work_entries(
            start_datetime=seven_days_ago_start,
            end_datetime=today_end
        )
        all_hourly_work_entries_in_week = self.db.get_hourly_work_entries( # НОВОЕ
            start_datetime=seven_days_ago_start,
            end_datetime=today_end
        )

        # Обработка записей по площади
        for entry in all_work_entries_in_week:
            area = float(entry.get('area', 0.0))
            operation_type = entry.get('operation_type')
            worker_id = entry.get('worker_id')

            total_weekly_output[operation_type] += area

            worker_name = ""
            for w_data in self.db.get_all_workers(): # ИЗМЕНЕНО: теперь w_data - это словарь
                if w_data.get('id') == worker_id:
                    worker_name = w_data.get('name')
                    break

            if worker_id not in individual_weekly_output:
                individual_weekly_output[worker_id] = {'name': worker_name, 'type': operation_type, 'area': 0.0, 'hourly_payment': 0.0}
            individual_weekly_output[worker_id]['area'] += area

        # НОВОЕ: Обработка почасовых записей
        for entry in all_hourly_work_entries_in_week:
            payment = float(entry.get('payment_amount', 0.0))
            work_type = entry.get('work_type')
            worker_id = entry.get('worker_id')

            worker_name = ""
            for w_data in self.db.get_all_workers(): # ИЗМЕНЕНО: теперь w_data - это словарь
                if w_data.get('id') == worker_id:
                    worker_name = w_data.get('name')
                    break

            if worker_id not in individual_weekly_output:
                individual_weekly_output[worker_id] = {'name': worker_name, 'type': work_type, 'area': 0.0, 'hourly_payment': 0.0}
            individual_weekly_output[worker_id]['hourly_payment'] += payment


        # Записываем общие итоги по цехам (только площадь)
        export_data.append({"Категория/Работник": "Общая сводка за неделю (по площади)", "Значение": ""})
        for op_type, total_area in total_weekly_output.items():
            export_data.append({"Категория/Работник": f" Итого по цеху '{op_type}'", "Значение": f"{total_area:.2f} м²"})

        export_data.append({"Категория/Работник": "", "Значение": ""})

        # Записываем индивидуальную выработку (площадь и почасовая оплата)
        export_data.append({"Категория/Работник": "Индивидуальная выработка за неделю:", "Значение": ""})
        sorted_individuals = sorted(individual_weekly_output.values(), key=lambda x: (x['type'], x['name']))
        for worker_info in sorted_individuals:
            area_str = f"{worker_info['area']:.2f} м²" if worker_info['area'] > 0 else ""
            hourly_pay_str = f"{worker_info['hourly_payment']:.2f} руб. (почас.)" if worker_info['hourly_payment'] > 0 else ""

            combined_str = []
            if area_str: combined_str.append(area_str)
            if hourly_pay_str: combined_str.append(hourly_pay_str)

            if combined_str:
                export_data.append({"Категория/Работник": f" {worker_info['name']} ({worker_info['type']})",
                                    "Значение": " / ".join(combined_str)})

        fieldnames = ["Категория/Работник", "Значение"]
        filename = f"Сводка_за_неделю_{seven_days_ago_start.strftime('%Y%m%d')}_по_{today.strftime('%Y%m%d')}.csv"
        self._export_to_csv(export_data, fieldnames, filename, "Сохранить сводку за неделю")


    def _clear_content_frame(self):
        """Очищает содержимое основной рабочей области (main_content_area)."""
        for widget in self.main_content_area.winfo_children(): # Изменено с content_frame
            widget.destroy()
        # Важно: обнуляем ссылки на уничтоженные виджеты, если они были в этой области
        self.individual_output_canvas = None # Сбросим ссылку на canvas
        self.individual_output_frame_in_canvas = None # Сбросим ссылку на внутренний фрейм
        self.individual_output_frame_window_id = None # Сбросим ID окна Canvas

        self.last_entry_info_label = None


    def show_screen(self, screen_type, is_initial_load=False):
        app_logger.info(f"Переключение на экран: {screen_type}")
        self._clear_content_frame()

        # Создание содержимого экрана в main_content_area
        if screen_type in self.operation_types:
            self._create_operation_input_frame_content(self.main_content_area, screen_type) # Изменено с content_frame
        elif screen_type == "Настройки":
            self._create_settings_frame_content(self.main_content_area) # Изменено с content_frame
        elif screen_type == "Справка":
            self._create_help_screen_content(self.main_content_area) # Изменено с content_frame
        elif screen_type == "УдалитьЗаписи":
            self._open_manage_entries_window()

        # Логика истории теперь здесь, после создания содержимого
        if not self.is_history_navigation:
            self.screen_history = self.screen_history[:self.current_history_index + 1]
            self.screen_history.append(screen_type)
            self.current_history_index = len(self.screen_history) - 1

        self.is_history_navigation = False
        self.current_screen_type = screen_type

        self._update_history_buttons_state()


    def _create_top_bar(self):
        """Создает верхнюю панель с часами, директором и статусом соединения."""
        colors = self.styles[self.current_theme]

        # Очищаем top_bar_frame перед пересозданием его содержимого (например, при смене темы)
        for widget in self.top_bar_frame.winfo_children():
            widget.destroy()

        nav_buttons_frame = tk.Frame(self.top_bar_frame, bg=colors["bg"])
        nav_buttons_frame.pack(side="left")

        self.back_button = tk.Button(nav_buttons_frame, text="←", command=self._go_back,
                                     font=self._get_scaled_font(18, 'bold'),
                                     bg=colors["button_bg"], fg=colors["button_fg"],
                                     width=2, height=1, bd=0, relief='flat', activebackground='#777777' if self.current_theme == "light" else '#333333') # Стилизация
        self.back_button.pack(side="left", padx=5)

        self.forward_button = tk.Button(nav_buttons_frame, text="→", command=self._go_forward,
                                        font=self._get_scaled_font(18, 'bold'),
                                        bg=colors["button_bg"], fg=colors["button_fg"],
                                        width=2, height=1, bd=0, relief='flat', activebackground='#777777' if self.current_theme == "light" else '#333333') # Стилизация
        self.forward_button.pack(side="left", padx=5)

        time_director_frame = tk.Frame(self.top_bar_frame, bg=colors["bg"])
        time_director_frame.pack(side="right")

        tk.Label(time_director_frame, text=f"Директор: {self.DIRECTOR_NAME}", font=self._get_scaled_font(14, 'bold'), bg=colors["bg"], fg=colors["fg"]).pack(side="left", padx=5)

        self.current_time_label = tk.Label(time_director_frame, text="", font=self._get_scaled_font(14, 'bold'), bg=colors["bg"], fg=colors["fg"])
        self.current_time_label.pack(side="right", padx=5)

        # Индикатор статуса соединения - создается ОДИН РАЗ при создании top_bar
        self.connection_status_label = tk.Label(time_director_frame, text="Загрузка...", font=self._get_scaled_font(10), bg=colors["bg"], fg="grey")
        self.connection_status_label.pack(side="right", padx=5)

        self._update_current_time()

    def _create_operation_input_frame_content(self, parent_frame, operation_type):
        colors = self.styles[self.current_theme]

        if self.insight_frame_visible:
            insight_frame = tk.Frame(parent_frame, bg=colors["frame_bg"], bd=2, relief="groove", padx=10, pady=10) # Добавим padding
            insight_frame.pack(pady=(10, 15), padx=20, fill="x") # Увеличим отступ снизу

            self.insight_label = tk.Label(insight_frame, text=self.DAILY_INSIGHTS[self.current_insight_index],
                                          font=self._get_scaled_font(12, 'italic'),
                                          bg=colors["frame_bg"], fg=colors["fg"], wraplength=400, justify="left")
            new_insight_button = tk.Button(insight_frame, text="Новый\nсовет", command=self._show_next_insight,
                                          font=self._get_scaled_font(10), bg='#008CBA', fg='white', width=6, height=2,
                                          bd=0, relief='raised', activebackground='#007799') # Стилизация
            new_insight_button.pack(side="right", padx=5, pady=5)

            dismiss_button = tk.Button(insight_frame, text="X", command=lambda: self._hide_insight_frame(insight_frame),
                                      font=self._get_scaled_font(10, 'bold'), bg='#ff6666', fg='white', width=3, height=1,
                                      bd=0, relief='raised', activebackground='#DD5555') # Стилизация
            dismiss_button.pack(side="right", padx=5, pady=5)

            self.insight_label.pack(side="left", padx=10, pady=5, expand=True, fill="x") # Moved pack after buttons


        tk.Label(parent_frame, text=f"Учет выработки: {operation_type}", font=self._get_scaled_font(20, 'bold'), # Увеличим размер заголовка
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=20)

        # --- Секция для ввода выработки по площади ---
        # Кнопка для сворачивания/разворачивания секции по площади
        self.toggle_area_button = tk.Button(parent_frame,
                                            text="Свернуть ввод (площадь)" if not self.is_area_input_collapsed else "Развернуть ввод (площадь)",
                                            command=self._toggle_area_input_frame,
                                            font=self._get_scaled_font(12, 'bold'),
                                            bg=colors["button_bg"], fg=colors["button_fg"],
                                            bd=0, relief='flat', activebackground='#777777' if self.current_theme == "light" else '#333333')
        self.toggle_area_button.pack(pady=(10, 5), padx=20, anchor="w") # Размещаем кнопку над фреймом

        self.input_group_frame_area = tk.LabelFrame(parent_frame, text="Ввод данных (по площади)", font=self._get_scaled_font(14, 'bold'),
                                          bg=colors["label_frame_bg"], fg=colors["fg"], padx=15, pady=10)
        self.input_group_frame_area.pack(pady=0, padx=20, fill="x") # Initial pack, pady=0 as it's controlled by button

        # Скрываем, если должна быть свернута
        if self.is_area_input_collapsed:
            self.input_group_frame_area.pack_forget()

        input_frame_area_content = tk.Frame(self.input_group_frame_area, bg=colors["label_frame_bg"])
        input_frame_area_content.pack(pady=10)
        input_frame_area_content.grid_columnconfigure(0, weight=1)
        input_frame_area_content.grid_columnconfigure(1, weight=1)

        tk.Label(input_frame_area_content, text="Работник:", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        worker_names_for_combobox = [d.get('name') for d in self.worker_lists[operation_type] if d.get('name')]

        self.worker_combobox_area = ttk.Combobox(input_frame_area_content, values=worker_names_for_combobox, state="readonly", width=30, font=self._get_scaled_font(12), style="TCombobox")
        self.worker_combobox_area.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        if worker_names_for_combobox:
            self.worker_combobox_area.set(worker_names_for_combobox[0])
        else:
            self.worker_combobox_area.set("Нет работников. Добавьте в Настройках.")
            self.worker_combobox_area['state'] = 'disabled'
            app_logger.warning(f"Не найдены работники для категории '{operation_type}'. Combobox 'Работник' для площади отключен.")


        labels_and_placeholders_area = [
            ("Ширина детали (см):", "0.00"),
            ("Длина детали (см):", "0.00"),
            ("Количество (шт):", "0")
        ]
        self.entry_vars_area = {}
        for i, (label_text, placeholder) in enumerate(labels_and_placeholders_area):
            tk.Label(input_frame_area_content, text=label_text, font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).grid(row=i+1, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Entry(input_frame_area_content, width=30, font=self._get_scaled_font(12), bg=colors["entry_bg"], fg=colors["placeholder_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="ew")
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self._on_entry_focus_in(e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self._on_entry_focus_out(e, p))
            self.entry_vars_area[label_text.split(' ')[0].lower()] = entry

        buttons_frame_area = tk.Frame(self.input_group_frame_area, bg=colors["label_frame_bg"])
        buttons_frame_area.pack(pady=(10,5))

        tk.Button(buttons_frame_area, text="Записать выработку (площадь)", command=lambda: self._save_operation_record_area(operation_type),
                  font=self._get_scaled_font(14, 'bold'), bg='#4CAF50', fg='white', bd=0, relief='raised', activebackground='#3D8B40',
                  padx=15, pady=8).pack(side='left', padx=10)
        tk.Button(buttons_frame_area, text="Очистить поля (площадь)", command=self._clear_input_fields_area_manual,
                  font=self._get_scaled_font(14, 'bold'), bg='#FFC107', fg='white', bd=0, relief='raised', activebackground='#DBA700',
                  padx=15, pady=8).pack(side='left', padx=10)

        # --- НОВАЯ Секция для ввода почасовой работы ---
        # Кнопка для сворачивания/разворачивания секции почасовой работы
        self.toggle_hourly_button = tk.Button(parent_frame,
                                            text="Свернуть ввод (почасовая)" if not self.is_hourly_input_collapsed else "Развернуть ввод (почасовая)",
                                            command=self._toggle_hourly_input_frame,
                                            font=self._get_scaled_font(12, 'bold'),
                                            bg=colors["button_bg"], fg=colors["button_fg"],
                                            bd=0, relief='flat', activebackground='#777777' if self.current_theme == "light" else '#333333')
        self.toggle_hourly_button.pack(pady=(20, 5), padx=20, anchor="w") # Отступ сверху и размещение

        self.input_group_frame_hourly = tk.LabelFrame(parent_frame, text="Ввод данных (почасовая работа)", font=self._get_scaled_font(14, 'bold'),
                                          bg=colors["label_frame_bg"], fg=colors["fg"], padx=15, pady=10)
        self.input_group_frame_hourly.pack(pady=0, padx=20, fill="x")

        if self.is_hourly_input_collapsed:
            self.input_group_frame_hourly.pack_forget()

        input_frame_hourly_content = tk.Frame(self.input_group_frame_hourly, bg=colors["label_frame_bg"])
        input_frame_hourly_content.pack(pady=10)
        input_frame_hourly_content.grid_columnconfigure(0, weight=1)
        input_frame_hourly_content.grid_columnconfigure(1, weight=1)

        tk.Label(input_frame_hourly_content, text="Работник:", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        worker_names_for_hourly_combobox = [d.get('name') for d in self.worker_lists['Почасовая'] if d.get('name')]
        self.worker_combobox_hourly = ttk.Combobox(input_frame_hourly_content, values=worker_names_for_hourly_combobox, state="readonly", width=30, font=self._get_scaled_font(12), style="TCombobox")
        self.worker_combobox_hourly.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # ДОБАВЛЕНО ИСПРАВЛЕНИЕ: Проверка на пустой список перед установкой значения
        if worker_names_for_hourly_combobox:
            self.worker_combobox_hourly.set(worker_names_for_hourly_combobox[0])
        else:
            self.worker_combobox_hourly.set("Нет работников. Добавьте в Настройках.")
            self.worker_combobox_hourly['state'] = 'disabled'
            app_logger.warning("Не найдены работники для почасовой работы. Combobox 'Работник' для почасовой работы отключен.")


        tk.Label(input_frame_hourly_content, text="Тип работы:", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.work_type_combobox_hourly = ttk.Combobox(input_frame_hourly_content, values=self.hourly_work_types, state="readonly", width=30, font=self._get_scaled_font(12), style="TCombobox")
        self.work_type_combobox_hourly.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        if self.hourly_work_types:
            self.work_type_combobox_hourly.set(self.hourly_work_types[0])
        else:
            app_logger.warning("Нет типов почасовой работы. Combobox 'Тип работы' отключен.")
            self.work_type_combobox_hourly.set("Нет типов работ")
            self.work_type_combobox_hourly['state'] = 'disabled'

        tk.Label(input_frame_hourly_content, text="Количество часов:", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.hours_combobox_hourly = ttk.Combobox(input_frame_hourly_content, values=list(range(1, 13)), state="readonly", width=30, font=self._get_scaled_font(12), style="TCombobox") # От 1 до 12 часов
        self.hours_combobox_hourly.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.hours_combobox_hourly.set("1") # По умолчанию 1 час

        buttons_frame_hourly = tk.Frame(self.input_group_frame_hourly, bg=colors["label_frame_bg"])
        buttons_frame_hourly.pack(pady=(10,5))

        tk.Button(buttons_frame_hourly, text="Записать почасовую работу", command=self._save_hourly_record,
                  font=self._get_scaled_font(14, 'bold'), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799',
                  padx=15, pady=8).pack(side='left', padx=10)
        # ИСПРАВЛЕНО: 'font=self._get_scaled_scaled_font(14, 'bold')' на 'font=self._get_scaled_font(14, 'bold')'
        tk.Button(buttons_frame_hourly, text="Очистить поля (почасовая)", command=self._clear_input_fields_hourly_manual,
                  font=self._get_scaled_font(14, 'bold'), bg='#FFC107', fg='white', bd=0, relief='raised', activebackground='#DBA700',
                  padx=15, pady=8).pack(side='left', padx=10)

        # Общий статус и последняя запись остаются
        self.status_label = tk.Label(parent_frame, text="", fg="blue", font=self._get_scaled_font(10), bg=colors["bg"])
        self.status_label.pack(pady=5)

        self.last_entry_info_label = tk.Label(parent_frame, text="Последняя запись: Нет", font=self._get_scaled_font(10, 'italic'),
                                               bg=colors["bg"], fg=colors["label_fg"], anchor="w", wraplength=600)
        self.last_entry_info_label.pack(pady=5, padx=20, fill="x")

        # Блок сводки выработки (м² и рубли)
        calculation_frame = tk.LabelFrame(parent_frame, text="Сводка выработки (м² и рубли)", font=self._get_scaled_font(14, 'bold'),
                                          bg=colors["label_frame_bg"], fg=colors["fg"], padx=15, pady=10)
        calculation_frame.pack(pady=20, fill="x", padx=20)

        self.daily_output_label = tk.Label(calculation_frame, text="За сегодня (площадь): 0 м²", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.daily_output_label.pack(fill="x", pady=2)
        self.five_day_output_label = tk.Label(calculation_frame, text="За 5 дней (площадь): 0 м²", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.five_day_output_label.pack(fill="x", pady=2)
        self.monthly_output_label = tk.Label(calculation_frame, text="За месяц (площадь): 0 м²", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.monthly_output_label.pack(fill="x", pady=2)

        # НОВОЕ: общие суммы почасовой оплаты
        tk.Frame(calculation_frame, height=1, bg='#cccccc' if self.current_theme == "light" else '#555555').pack(fill="x", pady=5, padx=10)
        self.daily_hourly_payment_label = tk.Label(calculation_frame, text="За сегодня (почасовая): 0 руб.", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.daily_hourly_payment_label.pack(fill="x", pady=2)
        self.five_day_hourly_payment_label = tk.Label(calculation_frame, text="За 5 дней (почасовая): 0 руб.", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.five_day_hourly_payment_label.pack(fill="x", pady=2)
        self.monthly_hourly_payment_label = tk.Label(calculation_frame, text="За месяц (почасовая): 0 руб.", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.monthly_hourly_payment_label.pack(fill="x", pady=2)


        # --- НАЧАЛО ИЗМЕНЕНИЙ ДЛЯ ПРОКРУТКИ ИНДИВИДУАЛЬНОЙ СВОДКИ ---
        # Контейнер для Canvas и Scrollbar
        scrollable_individual_output_container = tk.Frame(calculation_frame, bg=colors["label_frame_bg"])
        scrollable_individual_output_container.pack(pady=(10, 0), fill="both", expand=True)

        # Создаем Canvas (tk.Canvas вместо ttk.Canvas)
        self.individual_output_canvas = tk.Canvas(
            scrollable_individual_output_container,
            bg=colors["label_frame_bg"],
            highlightbackground=colors["label_frame_bg"], # Цвет границы при фокусе
            highlightthickness=0 # Толщина границы
        )
        self.individual_output_canvas.pack(side="left", fill="both", expand=True)

        # Создаем Scrollbar и связываем с Canvas
        individual_output_scrollbar = ttk.Scrollbar(
            scrollable_individual_output_container,
            orient="vertical",
            command=self.individual_output_canvas.yview,
            style="TScrollbar"
        )
        individual_output_scrollbar.pack(side="right", fill="y")
        self.individual_output_canvas.config(yscrollcommand=individual_output_scrollbar.set)

        # Создаем ФРЕЙМ ВНУТРИ CANVAS, который будет содержать элементы.
        # Это именно тот фрейм, куда будут добавляться метки выработки.
        self.individual_output_frame_in_canvas = tk.Frame(
            self.individual_output_canvas,
            bg=colors["label_frame_bg"]
        )
        # Добавляем этот фрейм как "окно" внутри Canvas
        self.individual_output_frame_window_id = self.individual_output_canvas.create_window(
            (0, 0), window=self.individual_output_frame_in_canvas, anchor="nw"
        )

        # Связываем изменение размера внутреннего фрейма с обновлением scrollregion Canvas
        self.individual_output_frame_in_canvas.bind("<Configure>", self._on_individual_output_frame_configure)
        # Также, связываем изменение размера Canvas с подстройкой ширины внутреннего фрейма,
        # чтобы он всегда занимал всю доступную ширину Canvas.
        self.individual_output_canvas.bind("<Configure>", self._on_individual_output_canvas_resize)

        # Добавляем привязки для прокрутки мышью и клавиатурой
        self.individual_output_canvas.bind("<MouseWheel>", self._on_mouse_wheel_individual_output) # Windows
        self.individual_output_canvas.bind("<Button-4>", self._on_mouse_wheel_individual_output) # Linux/macOS scroll up
        self.individual_output_canvas.bind("<Button-5>", self._on_mouse_wheel_individual_output) # Linux/macOS scroll down
        self.individual_output_canvas.bind("<Up>", lambda event: self.individual_output_canvas.yview_scroll(-1, "units"))
        self.individual_output_canvas.bind("<Down>", lambda event: self.individual_output_canvas.yview_scroll(1, "units"))
        self.individual_output_canvas.bind("<Prior>", lambda event: self.individual_output_canvas.yview_scroll(-1, "pages")) # Page Up
        self.individual_output_canvas.bind("<Next>", lambda event: self.individual_output_canvas.yview_scroll(1, "pages")) # Page Down
        self.individual_output_canvas.focus_set() # Сделаем Canvas фокусируемым для стрелок клавиатуры

        # --- КОНЕЦ ИЗМЕНЕНИЙ ДЛЯ ПРОКРУТКИ ИНДИВИДУАЛЬНОЙ СВОДКИ ---

        self._calculate_and_display_output(operation_type)

    def _on_individual_output_frame_configure(self, event):
        """Обновляет scrollregion Canvas при изменении размера внутреннего фрейма."""
        # Убедимся, что Canvas существует перед вызовом bbox("all")
        if self.individual_output_canvas and self.individual_output_canvas.winfo_exists():
            self.individual_output_canvas.config(scrollregion=self.individual_output_canvas.bbox("all"))

    def _on_individual_output_canvas_resize(self, event):
        """Подстраивает ширину внутреннего фрейма под ширину Canvas."""
        if self.individual_output_canvas and self.individual_output_frame_in_canvas and self.individual_output_frame_window_id:
            self.individual_output_canvas.itemconfig(self.individual_output_frame_window_id, width=event.width)

    def _on_mouse_wheel_individual_output(self, event):
        """Обрабатывает прокрутку колесиком мыши для Canvas индивидуальной выработки."""
        if self.individual_output_canvas:
            if event.delta: # Windows
                self.individual_output_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.num == 4: # Linux/macOS scroll up
                self.individual_output_canvas.yview_scroll(-1, "units")
            elif event.num == 5: # Linux/macOS scroll down
                self.individual_output_canvas.yview_scroll(1, "units")

    def _toggle_area_input_frame(self):
        """Сворачивает/разворачивает блок ввода по площади."""
        if self.input_group_frame_area.winfo_ismapped(): # Если видимый
            self.input_group_frame_area.pack_forget()
            self.is_area_input_collapsed = True
            self.toggle_area_button.config(text="Развернуть ввод (площадь)")
            app_logger.info("Блок ввода 'по площади' свернут.")
        else:
            self.input_group_frame_area.pack(pady=0, padx=20, fill="x") # pack back with original settings
            self.is_area_input_collapsed = False
            self.toggle_area_button.config(text="Свернуть ввод (площадь)")
            app_logger.info("Блок ввода 'по площади' развернут.")
        # Принудительно обновляем расположение других виджетов
        self.master.update_idletasks()

    def _toggle_hourly_input_frame(self):
        """Сворачивает/разворачивает блок ввода почасовой работы."""
        if self.input_group_frame_hourly.winfo_ismapped(): # Если видимый
            self.input_group_frame_hourly.pack_forget()
            self.is_hourly_input_collapsed = True
            self.toggle_hourly_button.config(text="Развернуть ввод (почасовая)")
            app_logger.info("Блок ввода 'почасовая работа' свернут.")
        else:
            self.input_group_frame_hourly.pack(pady=0, padx=20, fill="x") # pack back with original settings
            self.is_hourly_input_collapsed = False
            self.toggle_hourly_button.config(text="Свернуть ввод (почасовая)")
            app_logger.info("Блок ввода 'почасовая работа' развернут.")
        # Принудительно обновляем расположение других виджетов
        self.master.update_idletasks()


    def _on_entry_focus_in(self, entry_widget, placeholder):
        """Удаляет плейсхолдер при фокусе."""
        if entry_widget.get() == placeholder:
            entry_widget.delete(0, tk.END)
            entry_widget.config(fg=self.styles[self.current_theme]["entry_fg"])

    def _on_entry_focus_out(self, entry_widget, placeholder):
        """Возвращает плейсхолдер, если поле пусто."""
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
            entry_widget.config(fg=self.styles[self.current_theme]["placeholder_fg"])
        else: # Сбросим цвет, если что-то введено
            entry_widget.config(fg=self.styles[self.current_theme]["entry_fg"])

    def _show_next_insight(self):
        """Переключает на следующий совет из списка."""
        self.current_insight_index = (self.current_insight_index + 1) % len(self.DAILY_INSIGHTS)
        self.insight_label.config(text=self.DAILY_INSIGHTS[self.current_insight_index])
        app_logger.info(f"Показан новый совет: '{self.DAILY_INSIGHTS[self.current_insight_index]}'")

    def _hide_insight_frame(self, frame_to_hide):
        """Скрывает фрейм с советом на текущую сессию."""
        frame_to_hide.destroy()
        self.insight_frame_visible = False
        app_logger.info("Блок 'Совет дня' скрыт.")

    def _update_current_time(self):
        """Обновляет метку с текущим временем (подразумевается МСК, т.к. нет часовых поясов)."""
        now = datetime.datetime.now()
        self.current_time_label.config(text=now.strftime("%H:%M:%S (МСК)"))
        # Проверяем, что master еще существует перед планированием следующего вызова
        if self.master.winfo_exists():
            self.time_update_job_id = self.master.after(1000, self._update_current_time)


    def _save_operation_record_area(self, operation_type):
        selected_worker_name = self.worker_combobox_area.get()

        worker_id = None
        for d in self.worker_lists[operation_type]:
            if d.get('name') == selected_worker_name:
                worker_id = d.get('id')
                break

        if not worker_id:
            messagebox.showwarning("Ошибка ввода", "Пожалуйста, выберите работника из списка или добавьте его в Настройках.", parent=self.master)
            app_logger.warning(f"Попытка записать выработку по площади без выбранного работника для типа '{operation_type}'.")
            return

        try:
            width_str = self.entry_vars_area['ширина'].get().replace(',', '.')
            length_str = self.entry_vars_area['длина'].get().replace(',', '.')
            quantity_str = self.entry_vars_area['количество'].get()

            # Удаляем плейсхолдеры перед попыткой конвертации
            if width_str == "0.00": width_str = ""
            if length_str == "0.00": length_str = ""
            if quantity_str == "0": quantity_str = ""

            width = float(width_str)
            length = float(length_str)
            quantity = int(quantity_str)

            if width <= 0 or length <= 0 or quantity <= 0:
                raise ValueError("Все значения должны быть положительными.")
        except ValueError as e:
            messagebox.showwarning("Ошибка ввода", f"Ошибка ввода данных: {e}\nШирина и длина должны быть числами, Количество - целым числом больше нуля.", parent=self.master)
            app_logger.warning(f"Некорректный ввод данных для выработки по площади: {width_str}, {length_str}, {quantity_str}. Ошибка: {e}")
            return

        area = (width * length * quantity) / 10000
        now_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        app_logger.info(f"Запись выработки по площади для '{selected_worker_name}' ({operation_type}): {area:.2f} м². Локальное обновление.")
        self.status_label.config(text=f"Запись для {selected_worker_name} ({area:.2f} м²) добавлена в локальную сводку...", fg="orange")
        self._calculate_and_display_output(operation_type) # Обновляем UI немедленно из кэша
        self._update_last_entry_info(selected_worker_name, area, now_datetime_str, 'площадь') # НОВОЕ: тип записи
        self._clear_input_fields_area() # ИЗМЕНЕНО: вызываем очистку полей площади
        self.entry_vars_area['ширина'].focus_set() # Автофокус на первом поле

        def success_cb(result):
            messagebox.showinfo("Успех", f"Запись для {selected_worker_name} ({area:.2f} м²) успешно сохранена в Google Sheets!", parent=self.master)
            self.db.load_all_data_to_cache() # Перезагружаем кэш после успешной записи в GS
            app_logger.info(f"Запись выработки по площади для '{selected_worker_name}' ({operation_type}): {area:.2f} м² успешно сохранена в Google Sheets.")
        def error_cb(e):
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении данных по площади в Google Sheets: {e}", parent=self.master)
            app_logger.error(f"Ошибка при сохранении данных по площади для '{selected_worker_name}' ({operation_type}) в Google Sheets: {e}")
            self.db.load_all_data_to_cache() # Попытка синхронизировать кэш обратно

        try:
            self.db.add_work_entry(worker_id, operation_type, now_datetime_str, width, length, quantity, area, success_cb, error_cb)

        except Exception as e:
            app_logger.critical(f"Критическая ошибка при попытке записи по площади в кэш: {e}")
            self.status_label.config(text=f"Ошибка при добавлении по площади в локальный кэш: {e}", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка при попытке записи по площади в локальный кэш: {e}", parent=self.master)

    def _save_hourly_record(self): # НОВЫЙ МЕТОД
        selected_worker_name = self.worker_combobox_hourly.get()
        selected_work_type = self.work_type_combobox_hourly.get()
        selected_hours_str = self.hours_combobox_hourly.get()

        worker_id = None
        for d in self.worker_lists['Почасовая']: # Ищем среди всех работников
            if d.get('name') == selected_worker_name:
                worker_id = d.get('id')
                break

        if not worker_id:
            messagebox.showwarning("Ошибка ввода", "Пожалуйста, выберите работника для почасовой работы.", parent=self.master)
            app_logger.warning(f"Попытка записать почасовую работу без выбранного работника для типа '{selected_work_type}'.")
            return
        if not selected_work_type:
            messagebox.showwarning("Ошибка ввода", "Пожалуйста, выберите тип почасовой работы (Уборка/Мойка).", parent=self.master)
            app_logger.warning("Попытка записать почасовую работу без выбранного типа работы.")
            return
        try:
            hours = int(selected_hours_str)
            if hours <= 0:
                raise ValueError("Количество часов должно быть целым положительным числом.")
        except ValueError as e:
            messagebox.showwarning("Ошибка ввода", f"Ошибка ввода данных: {e}", parent=self.master)
            app_logger.warning(f"Некорректный ввод часов для почасовой работы ({selected_hours_str}). Ошибка: {e}")
            return

        rate = 0.0
        if selected_work_type == "Уборка":
            rate = float(self.db.get_setting('cleaning_rate_per_hour', default_value="0.0"))
        elif selected_work_type == "Мойка":
            rate = float(self.db.get_setting('washing_rate_per_hour', default_value="0.0"))

        if rate <= 0:
            messagebox.showwarning("Ошибка", f"Ставка для '{selected_work_type}' не установлена или равна нулю. Установите её в Настройках.", parent=self.master)
            app_logger.warning(f"Ставка для почасовой работы '{selected_work_type}' не установлена или равна нулю.")
            return

        payment_amount = hours * rate
        now_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        app_logger.info(f"Запись почасовой работы для '{selected_worker_name}' ({selected_work_type}): {hours} ч., {payment_amount:.2f} руб. Локальное обновление.")
        self.status_label.config(text=f"Запись для {selected_worker_name} ({hours} ч., {payment_amount:.2f} руб.) добавлена в локальную сводку...", fg="orange")
        self._calculate_and_display_output(self.current_screen_type) # Обновляем сводку текущего экрана
        self._update_last_entry_info(selected_worker_name, payment_amount, now_datetime_str, 'почасовая') # НОВОЕ: тип записи
        self._clear_input_fields_hourly() # Очищаем поля почасовой работы

        def success_cb(result):
            messagebox.showinfo("Успех", f"Почасовая запись для {selected_worker_name} ({payment_amount:.2f} руб.) успешно сохранена в Google Sheets!", parent=self.master)
            self.db.load_all_data_to_cache()
            app_logger.info(f"Почасовая запись для '{selected_worker_name}' ({selected_work_type}): {hours} ч., {payment_amount:.2f} руб. успешно сохранена в Google Sheets.")
        def error_cb(e):
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении почасовых данных в Google Sheets: {e}", parent=self.master)
            app_logger.error(f"Ошибка при сохранении почасовых данных для '{selected_worker_name}' ({selected_work_type}) в Google Sheets: {e}")
            self.db.load_all_data_to_cache()

        try:
            self.db.add_hourly_work_entry(worker_id, selected_work_type, now_datetime_str, hours, payment_amount, success_cb, error_cb)
        except Exception as e:
            app_logger.critical(f"Критическая ошибка при попытке записи почасовой работы в кэш: {e}")
            self.status_label.config(text=f"Ошибка при добавлении почасовой работы в локальный кэш: {e}", fg="red")
            messagebox.showerror("Ошибка", f"Произошла ошибка при попытке записи почасовой работы в локальный кэш: {e}", parent=self.master)


    def _clear_input_fields_area(self): # ИЗМЕНЕНО: очистка полей площади
        """Очищает поля ввода площади и восстанавливает плейсхолдеры."""
        for label_text, placeholder in [
            ("ширина", "0.00"),
            ("длина", "0.00"),
            ("количество", "0")
        ]:
            entry_widget = self.entry_vars_area[label_text]
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, placeholder)
            entry_widget.config(fg=self.styles[self.current_theme]["placeholder_fg"])
        app_logger.info("Поля ввода выработки по площади очищены.")

    def _clear_input_fields_hourly(self): # НОВЫЙ МЕТОД: очистка полей почасовой работы
        """Очищает поля ввода почасовой работы и восстанавливает плейсхолдеры."""
        if self.hourly_work_types:
            self.work_type_combobox_hourly.set(self.hourly_work_types[0])
        else:
            self.work_type_combobox_hourly.set("")
        self.hours_combobox_hourly.set("1")
        app_logger.info("Поля ввода почасовой работы очищены.")

    def _clear_input_fields_area_manual(self): # ИЗМЕНЕНО: ручная очистка площади
        """Очищает поля ввода площади вручную по кнопке."""
        self._clear_input_fields_area()
        self.status_label.config(text="Поля площади очищены.", fg="blue")
        self.entry_vars_area['ширина'].focus_set()
        app_logger.info("Поля ввода выработки по площади очищены вручную.")

    def _clear_input_fields_hourly_manual(self): # НОВЫЙ МЕТОД: ручная очистка почасовой работы
        """Очищает поля ввода почасовой работы вручную по кнопке."""
        self._clear_input_fields_hourly()
        self.status_label.config(text="Поля почасовой работы очищены.", fg="blue")
        if self.worker_combobox_hourly['values']:
            self.worker_combobox_hourly.set(self.worker_combobox_hourly['values'][0])
        self.worker_combobox_hourly.focus_set()
        app_logger.info("Поля ввода почасовой работы очищены вручную.")


    def _update_last_entry_info(self, worker_name, value, timestamp, entry_type):
        """Обновляет метку с информацией о последней записи, учитывая тип."""
        if self.last_entry_info_label:
            if entry_type == 'площадь':
                self.last_entry_info_label.config(text=f"Последняя запись: {worker_name} - {value:.2f} м² ({timestamp})")
            elif entry_type == 'почасовая':
                self.last_entry_info_label.config(text=f"Последняя запись: {worker_name} - {value:.2f} руб. (почас.) ({timestamp})")


    def _calculate_and_display_output(self, current_screen_operation_type): # ИЗМЕНЕНО: теперь принимает текущий тип операции
        colors = self.styles[self.current_theme]

        today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        five_days_ago_start = (today_start - datetime.timedelta(days=4))
        month_start_datetime = today_start.replace(day=1)

        total_daily_area = 0.0
        total_five_day_area = 0.0
        total_monthly_area = 0.0

        total_daily_hourly_payment = 0.0 # НОВОЕ
        total_five_day_hourly_payment = 0.0 # НОВОЕ
        total_monthly_hourly_payment = 0.0 # НОВОЕ


        # Инициализация для индивидуальной выработки
        worker_outputs = {}
        # Заполняем всех работников, чтобы у всех были начальные значения, включая тех, у кого пока нет записей
        for d in self.db.get_all_workers(): # d - это словарь
            worker_id = d.get('id')
            worker_name = d.get('name')
            worker_type = d.get('type') # 'Раскройщики', 'Упаковщицы' etc.
            if worker_id is not None: # Убедимся, что ID существует
                worker_outputs[worker_id] = {
                    'name': worker_name,
                    'type': worker_type, # Храним исходный тип работника
                    'daily_area': 0.0, '5days_area': 0.0, 'month_area': 0.0,
                    'daily_hourly_payment': 0.0, '5days_hourly_payment': 0.0, 'month_hourly_payment': 0.0
                }


        try:
            # Обработка записей по площади
            # Если текущий экран - это одна из операций по площади, то фильтруем по ней
            # Иначе (например, если на экране настроек), то не фильтруем по operation_type
            if current_screen_operation_type in self.operation_types:
                all_area_entries = self.db.get_work_entries(operation_type=current_screen_operation_type)
            else:
                # Если мы на экране, который не соответствует конкретной операции (например, настройки),
                # то для сводки по площади нужно получать все записи по площади,
                # или же решить не отображать сводку по площади на таких экранах.
                # Пока что оставлю для текущей операции (или пустой список, если current_screen_operation_type не в списке)
                all_area_entries = [] # Не показываем выработку по площади, если не на соответствующем экране

            for entry in all_area_entries:
                entry_dt_str = entry.get('entry_datetime', '')
                if not entry_dt_str: continue
                try:
                    entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try: entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d")
                    except ValueError: continue

                area = float(entry.get('area', 0.0))
                worker_id_for_entry = entry.get('worker_id')

                if today_start <= entry_dt_obj <= today_end:
                    total_daily_area += area
                    if worker_id_for_entry in worker_outputs: worker_outputs[worker_id_for_entry]['daily_area'] += area
                if five_days_ago_start <= entry_dt_obj <= today_end:
                    total_five_day_area += area
                    if worker_id_for_entry in worker_outputs: worker_outputs[worker_id_for_entry]['5days_area'] += area
                if month_start_datetime <= entry_dt_obj <= today_end:
                    total_monthly_area += area
                    if worker_id_for_entry in worker_outputs: worker_outputs[worker_id_for_entry]['month_area'] += area

            # НОВОЕ: Обработка почасовых записей (для всех типов, т.к. отображаем общую сводку на экране)
            # Почасовые записи не привязаны к "типам цехов", они общие
            all_hourly_entries = self.db.get_hourly_work_entries()
            for entry in all_hourly_entries:
                entry_dt_str = entry.get('entry_datetime', '')
                if not entry_dt_str: continue
                try:
                    entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try: entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d")
                    except ValueError: continue

                payment = float(entry.get('payment_amount', 0.0))
                worker_id_for_entry = entry.get('worker_id')

                if today_start <= entry_dt_obj <= today_end:
                    total_daily_hourly_payment += payment
                    if worker_id_for_entry in worker_outputs: worker_outputs[worker_id_for_entry]['daily_hourly_payment'] += payment
                if five_days_ago_start <= entry_dt_obj <= today_end:
                    total_five_day_hourly_payment += payment
                    if worker_id_for_entry in worker_outputs: worker_outputs[worker_id_for_entry]['5days_hourly_payment'] += payment
                if month_start_datetime <= entry_dt_obj <= today_end:
                    total_monthly_hourly_payment += payment
                    if worker_id_for_entry in worker_outputs: worker_outputs[worker_id_for_entry]['month_hourly_payment'] += payment


        except Exception as e:
            app_logger.error(f"Ошибка при расчете выработки для '{current_screen_operation_type}': {e}")
            messagebox.showerror("Ошибка", f"Ошибка при расчете выработки из кэша: {e}", parent=self.master)

        # Обновление меток общей выработки (площадь)
        self.daily_output_label.config(text=f"За сегодня (площадь): {total_daily_area:.2f} м²", font=self._get_scaled_font(12))
        self.five_day_output_label.config(text=f"За 5 дней (площадь): {total_five_day_area:.2f} м²", font=self._get_scaled_font(12))
        self.monthly_output_label.config(text=f"За месяц (площадь): {total_monthly_area:.2f} м²", font=self._get_scaled_font(12))

        # НОВОЕ: Обновление меток общей выработки (почасовая)
        self.daily_hourly_payment_label.config(text=f"За сегодня (почасовая): {total_daily_hourly_payment:.2f} руб.", font=self._get_scaled_font(12))
        self.five_day_hourly_payment_label.config(text=f"За 5 дней (почасовая): {total_five_day_hourly_payment:.2f} руб.", font=self._get_scaled_font(12))
        self.monthly_hourly_payment_label.config(text=f"За месяц (почасовая): {total_monthly_hourly_payment:.2f} руб.", font=self._get_scaled_font(12))


        # Очищаем только содержимое ФРЕЙМА ВНУТРИ CANVAS
        if self.individual_output_frame_in_canvas:
            for widget in self.individual_output_frame_in_canvas.winfo_children():
                widget.destroy()

        # Добавляем заголовок для индивидуальной выработки, только если есть работники
        if worker_outputs:
            tk.Label(self.individual_output_frame_in_canvas, text="Индивидуальная выработка:",
                     font=self._get_scaled_font(13, 'bold'),
                     bg=colors["label_frame_bg"], fg=colors["fg"], anchor="w").pack(fill="x", pady=(10, 5))

            # Отображение индивидуальной выработки
            # Сортируем работников для отображения по типу, затем по имени
            sorted_workers_display = sorted(worker_outputs.values(), key=lambda x: (x['type'], x['name']))

            for worker_data in sorted_workers_display:
                # Пропускаем работников, если у них нет ни площади, ни почасовой оплаты
                if (worker_data['daily_area'] == 0 and worker_data['5days_area'] == 0 and \
                   worker_data['month_area'] == 0) and (worker_data['daily_hourly_payment'] == 0 and \
                   worker_data['5days_hourly_payment'] == 0 and worker_data['month_hourly_payment'] == 0):
                   continue # Пропускаем, если нет активности

                tk.Label(self.individual_output_frame_in_canvas, text=f" {worker_data['name']} ({worker_data['type']}):",
                         font=self._get_scaled_font(11, 'bold'), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=10)

                # Показываем площадь, если есть
                if worker_data['daily_area'] > 0 or worker_data['5days_area'] > 0 or worker_data['month_area'] > 0:
                    tk.Label(self.individual_output_frame_in_canvas, text=f"    За сегодня (площадь): {worker_data['daily_area']:.2f} м²",
                             font=self._get_scaled_font(11), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=20)
                    tk.Label(self.individual_output_frame_in_canvas, text=f"    За 5 дней (площадь): {worker_data['5days_area']:.2f} м²",
                             font=self._get_scaled_font(11), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=20)
                    tk.Label(self.individual_output_frame_in_canvas, text=f"    За месяц (площадь): {worker_data['month_area']:.2f} м²",
                             font=self._get_scaled_font(11), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=20)

                # Показываем почасовую оплату, если есть
                if worker_data['daily_hourly_payment'] > 0 or worker_data['5days_hourly_payment'] > 0 or worker_data['month_hourly_payment'] > 0:
                    tk.Label(self.individual_output_frame_in_canvas, text=f"    За сегодня (почас.): {worker_data['daily_hourly_payment']:.2f} руб.",
                             font=self._get_scaled_font(11), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=20)
                    tk.Label(self.individual_output_frame_in_canvas, text=f"    За 5 дней (почас.): {worker_data['5days_hourly_payment']:.2f} руб.",
                             font=self._get_scaled_font(11), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=20)
                    tk.Label(self.individual_output_frame_in_canvas, text=f"    За месяц (почас.): {worker_data['month_hourly_payment']:.2f} руб.",
                             font=self._get_scaled_font(11), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w").pack(fill="x", pady=0, padx=20)

                tk.Frame(self.individual_output_frame_in_canvas, height=1, bg='#cccccc' if self.current_theme == "light" else '#555555').pack(fill="x", pady=5, padx=10)

        # После добавления/обновления содержимого, нужно принудительно обновить scrollregion Canvas
        if self.individual_output_canvas:
            self.individual_output_canvas.update_idletasks()
            self.individual_output_canvas.config(scrollregion=self.individual_output_canvas.bbox("all"))


    def _create_settings_frame_content(self, parent_frame):
        colors = self.styles[self.current_theme]
        app_logger.info("Открыт экран настроек.")

        tk.Label(parent_frame, text="Настройки: Управление", font=self._get_scaled_font(20, 'bold'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=20)

        tk.Label(parent_frame, text="Мастер: Половых Екатерина", font=self._get_scaled_font(14, 'italic'),
                 bg=colors["bg"], fg=colors["label_fg"]).pack(pady=10)

        settings_buttons_grid_frame = tk.Frame(parent_frame, bg=colors["bg"])
        settings_buttons_grid_frame.pack(pady=10, fill="both", expand=True, padx=20)
        settings_buttons_grid_frame.grid_columnconfigure(0, weight=1)
        settings_buttons_grid_frame.grid_columnconfigure(1, weight=1)
        settings_buttons_grid_row_count = 0

        button_style = {'font': self._get_scaled_font(12, 'bold'), 'width': 25, 'height': 2,
                        'bg': colors["button_bg"], 'fg': colors["button_fg"],
                        'bd': 0, 'relief': 'raised', 'activebackground': '#777777' if self.current_theme == "light" else '#333333'}

        # --- Группа: Управление работниками ---
        worker_management_frame = tk.LabelFrame(settings_buttons_grid_frame, text="Управление работниками",
                                                font=self._get_scaled_font(14, 'bold'),
                                                bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        worker_management_frame.grid(row=settings_buttons_grid_row_count, column=0, padx=10, pady=10, sticky="nsew")

        tk.Button(worker_management_frame, text="Управление Раскройщиками", command=lambda: self._open_manage_workers_window("Раскройщики"), **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(worker_management_frame, text="Управление Упаковщицами", command=lambda: self._open_manage_workers_window("Упаковщицы"), **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(worker_management_frame, text="Управление Обработчиками", command=lambda: self._open_manage_workers_window("Обработка"), **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(worker_management_frame, text="Управление Грузчиками", command=lambda: self._open_manage_workers_window("Грузчики"), **button_style).pack(pady=5, padx=10, fill='x')

        # --- Группа: Отчеты и статистика ---
        reporting_frame = tk.LabelFrame(settings_buttons_grid_frame, text="Отчеты и статистика",
                                        font=self._get_scaled_font(14, 'bold'),
                                        bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        reporting_frame.grid(row=settings_buttons_grid_row_count, column=1, padx=10, pady=10, sticky="nsew")
        settings_buttons_grid_row_count += 1

        tk.Button(reporting_frame, text="Рассчитать Заработную плату", command=self._show_salary_dialog, **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(reporting_frame, text="Статистика выработки", command=self._create_statistics_window, **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(reporting_frame, text="Удаление записей выработки", command=lambda: self.show_screen("УдалитьЗаписи"), **button_style).pack(pady=5, padx=10, fill='x')

        # НОВАЯ ГРУППА: Тарифы почасовой работы
        hourly_rates_frame = tk.LabelFrame(settings_buttons_grid_frame, text="Тарифы почасовой работы",
                                           font=self._get_scaled_font(14, 'bold'),
                                           bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        hourly_rates_frame.grid(row=settings_buttons_grid_row_count, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(hourly_rates_frame, text="Ставка Уборки (руб/час):", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).pack(pady=5, padx=5, anchor='w')
        self.cleaning_rate_entry = tk.Entry(hourly_rates_frame, font=self._get_scaled_font(12), bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.cleaning_rate_entry.pack(pady=2, padx=5, fill='x')

        tk.Label(hourly_rates_frame, text="Ставка Мойки (руб/час):", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).pack(pady=5, padx=5, anchor='w')
        self.washing_rate_entry = tk.Entry(hourly_rates_frame, font=self._get_scaled_font(12), bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.washing_rate_entry.pack(pady=2, padx=5, fill='x')

        tk.Button(hourly_rates_frame, text="Сохранить тарифы", command=self._save_hourly_rates,
                  font=self._get_scaled_font(12), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799').pack(pady=(10,5), padx=5, fill='x')

        # Загружаем текущие значения при создании (или пересоздании) экрана настроек
        self.cleaning_rate_entry.delete(0, tk.END)
        self.cleaning_rate_entry.insert(0, str(self.db.get_setting('cleaning_rate_per_hour', "0.0")))
        self.washing_rate_entry.delete(0, tk.END)
        self.washing_rate_entry.insert(0, str(self.db.get_setting('washing_rate_per_hour', "0.0")))

        # --- Группа: Оформление ---
        appearance_frame = tk.LabelFrame(settings_buttons_grid_frame, text="Оформление",
                                        font=self._get_scaled_font(14, 'bold'),
                                        bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        appearance_frame.grid(row=settings_buttons_grid_row_count, column=1, padx=10, pady=10, sticky="nsew") # ИЗМЕНЕНО: на ту же строку, что и почасовые тарифы

        tk.Button(appearance_frame, text="Сменить тему приложения", command=self.toggle_theme, **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(appearance_frame, text="Изменить размер букв", command=self._show_font_size_dialog, **button_style).pack(pady=5, padx=10, fill='x')

        settings_buttons_grid_row_count += 1 # Увеличиваем счетчик строки после почасовых тарифов и оформления

        # --- Группа: Безопасность ---
        security_frame = tk.LabelFrame(settings_buttons_grid_frame, text="Безопасность",
                                        font=self._get_scaled_font(14, 'bold'),
                                        bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        security_frame.grid(row=settings_buttons_grid_row_count, column=0, columnspan=2, padx=10, pady=10, sticky="nsew") # Растягиваем на 2 колонки
        settings_buttons_grid_row_count += 1

        tk.Button(security_frame, text="Изменить пароль входа", command=self._change_login_password, **button_style).pack(pady=5, padx=10, fill='x')
        tk.Button(security_frame, text="Изменить пароль ЗП", command=self._change_salary_password, **button_style).pack(pady=5, padx=10, fill='x')

        for i in range(settings_buttons_grid_row_count):
            settings_buttons_grid_frame.grid_rowconfigure(i, weight=1)

        tk.Frame(parent_frame, bg=colors["bg"], height=1).pack(expand=True, fill="both", pady=0)
        tk.Label(parent_frame, text="Личная библиотека Илья Устюжанцева", font=self._get_scaled_font(10, 'italic'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=10)

    def _save_hourly_rates(self): # НОВЫЙ МЕТОД
        try:
            cleaning_rate = float(self.cleaning_rate_entry.get().replace(',', '.'))
            washing_rate = float(self.washing_rate_entry.get().replace(',', '.'))

            if cleaning_rate < 0 or washing_rate < 0:
                raise ValueError("Ставки не могут быть отрицательными.")

            def success_cb(result):
                self.db.load_all_data_to_cache() # Обновим кэш
                messagebox.showinfo("Успех", "Тарифы почасовой работы успешно сохранены!", parent=self.master)
                app_logger.info(f"Тарифы почасовой работы сохранены: Уборка={cleaning_rate:.2f} руб/ч, Мойка={washing_rate:.2f} руб/ч.")
            def error_cb(e):
                app_logger.error(f"Ошибка сохранения тарифов почасовой работы: {e}")
                messagebox.showerror("Ошибка", f"Не удалось сохранить тарифы почасовой работы: {e}", parent=self.master)
                self.db.load_all_data_to_cache() # Попытка синхронизировать кэш обратно

            # Асинхронное обновление настроек
            self.db.update_setting('cleaning_rate_per_hour', str(cleaning_rate), success_cb, error_cb)
            self.db.update_setting('washing_rate_per_hour', str(washing_rate), success_cb, error_cb)

        except ValueError as e:
            app_logger.warning(f"Ошибка ввода тарифов почасовой работы: {e}")
            messagebox.showwarning("Ошибка ввода", f"Ставки должны быть числами: {e}", parent=self.master)
        except Exception as e:
            app_logger.error(f"Ошибка при сохранении почасовых тарифов (кэш): {e}")
            messagebox.showerror("Ошибка", f"Ошибка при сохранении почасовых тарифов (кэш): {e}", parent=self.master)

    def _show_font_size_dialog(self):
        """Открывает диалог для выбора размера шрифта."""
        app_logger.info("Открыт диалог изменения размера шрифта.")
        font_window = tk.Toplevel(self.master)
        font_window.title("Выбрать размер букв")
        font_window.transient(self.master)
        font_window.grab_set()

        colors = self.styles[self.current_theme]
        font_window.config(bg=colors["bg"])

        tk.Label(font_window, text="Выберите размер:", font=self._get_scaled_font(14, 'bold'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=15)

        font_scales = {
            "Маленький": 0.8,
            "Средний": 1.0,
            "Большой": 1.2,
            "Огромный": 1.4
        }
        current_font_name = next((name for name, scale in font_scales.items() if abs(scale - self.font_size_scale) < 0.001), "Средний")

        selected_scale_var = tk.StringVar(value=current_font_name)

        for name, scale_value in font_scales.items():
            rb = tk.Radiobutton(font_window, text=name, variable=selected_scale_var, value=name,
                                font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["fg"],
                                selectcolor=colors["button_bg"], activebackground=colors["bg"], activeforeground=colors["fg"])
            rb.pack(anchor="w", padx=20, pady=2)

        def apply_new_font_size():
            chosen_name = selected_scale_var.get()
            new_scale = font_scales.get(chosen_name, 1.0)

            if new_scale != self.font_size_scale:
                def success_cb(result):
                    messagebox.showinfo("Успех", f"Размер букв изменен на '{chosen_name}'.", parent=self.master)
                    app_logger.info(f"Размер шрифта изменен на: '{chosen_name}' ({new_scale}).")
                    self.apply_theme(self.current_theme) # Перезагрузка UI для применения нового масштаба
                    self.db.load_all_data_to_cache()
                def error_cb(e):
                    app_logger.error(f"Не удалось сохранить размер шрифта (асинхронная запись): {e}")
                    messagebox.showerror("Ошибка", f"Не удалось сохранить размер шрифта (асинхронная запись): {e}", parent=self.master)
                    self.db.load_all_data_to_cache()
                try:
                    self.db.update_setting('font_size_scale', str(new_scale), success_cb, error_cb)
                    self.font_size_scale = new_scale
                    self.apply_theme(self.current_theme) # Применяем тему заново, чтобы перерисовать все виджеты с новым масштабом
                except Exception as e:
                    app_logger.error(f"Не удалось обновить настройку размера шрифта (кэш): {e}")
                    messagebox.showerror("Ошибка", f"Не удалось обновить настройку размера шрифта (кэш): {e}", parent=self.master)
            font_window.destroy()

        tk.Button(font_window, text="Применить", command=apply_new_font_size,
                  font=self._get_scaled_font(12, 'bold'), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799').pack(pady=15)


    def _open_manage_workers_window(self, worker_type):
        app_logger.info(f"Открыто окно управления работниками для категории: '{worker_type}'.")
        manage_window = tk.Toplevel(self.master)
        manage_window.title(f"Управление: {worker_type}")
        manage_window.geometry("800x600")
        manage_window.transient(self.master)
        manage_window.grab_set()

        colors = self.styles[self.current_theme]
        manage_window.config(bg=colors["bg"])

        manage_window.grid_rowconfigure(0, weight=1)
        manage_window.grid_columnconfigure(0, weight=1)
        manage_window.grid_columnconfigure(1, weight=1)

        workers_list_frame = tk.LabelFrame(manage_window, text=f"Список {worker_type}", font=self._get_scaled_font(14, 'bold'),
                                            bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        workers_list_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        workers_list_frame.grid_rowconfigure(0, weight=1)
        workers_list_frame.grid_columnconfigure(0, weight=1)

        self.worker_listbox = tk.Listbox(workers_list_frame, font=self._get_scaled_font(12), height=15,
                                          bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid',
                                          selectbackground=self.ttk_style.lookup("Treeview", "selectbackground"),
                                          selectforeground=self.ttk_style.lookup("Treeview", "selectforeground"))

        self.worker_listbox.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.worker_listbox.bind('<<ListboxSelect>>', lambda event: self._display_worker_stats_and_rate(event, worker_type))

        scrollbar = ttk.Scrollbar(workers_list_frame, orient="vertical", command=self.worker_listbox.yview, style="TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=0, pady=5)
        self.worker_listbox.config(yscrollcommand=scrollbar.set)

        self._populate_worker_listbox(worker_type)

        buttons_frame = tk.Frame(workers_list_frame, bg=colors["label_frame_bg"])
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(buttons_frame, text="Добавить", command=lambda: self._add_worker_dialog(worker_type, manage_window),
                  font=self._get_scaled_font(12), bg='#4CAF50', fg='white', bd=0, relief='raised', activebackground='#3D8B40').pack(side="left", padx=5, pady=5)
        tk.Button(buttons_frame, text="Удалить", command=lambda: self._delete_worker(worker_type, manage_window),
                  font=self._get_scaled_font(12), bg='#f44336', fg='white', bd=0, relief='raised', activebackground='#C4332A').pack(side="left", padx=5, pady=5)

        stats_and_rate_frame = tk.LabelFrame(manage_window, text="Выработка и ставка работника", font=self._get_scaled_font(14, 'bold'),
                                              bg=colors["label_frame_bg"], fg=colors["fg"], padx=10, pady=10)
        stats_and_rate_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        self.worker_stats_labels = {}
        self.worker_stats_labels['today_area'] = tk.Label(stats_and_rate_frame, text="За сегодня (площадь): 0 м²", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.worker_stats_labels['today_area'].pack(fill="x", pady=2, padx=10)
        self.worker_stats_labels['5days_area'] = tk.Label(stats_and_rate_frame, text="За 5 дней (площадь): 0 m²", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.worker_stats_labels['5days_area'].pack(fill="x", pady=2, padx=10)
        self.worker_stats_labels['month_area'] = tk.Label(stats_and_rate_frame, text="За месяц (площадь): 0 m²", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.worker_stats_labels['month_area'].pack(fill="x", pady=2, padx=10)

        # НОВОЕ: метки для почасовой выработки в управлении работниками
        tk.Frame(stats_and_rate_frame, height=1, bg='#cccccc' if self.current_theme == "light" else '#555555').pack(fill="x", pady=5, padx=10)
        self.worker_stats_labels['today_hourly'] = tk.Label(stats_and_rate_frame, text="За сегодня (почас.): 0 руб.", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.worker_stats_labels['today_hourly'].pack(fill="x", pady=2, padx=10)
        self.worker_stats_labels['5days_hourly'] = tk.Label(stats_and_rate_frame, text="За 5 дней (почас.): 0 руб.", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.worker_stats_labels['5days_hourly'].pack(fill="x", pady=2, padx=10)
        self.worker_stats_labels['month_hourly'] = tk.Label(stats_and_rate_frame, text="За месяц (почас.): 0 руб.", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"], anchor="w")
        self.worker_stats_labels['month_hourly'].pack(fill="x", pady=2, padx=10)

        tk.Label(stats_and_rate_frame, text="Ставка за м²:", font=self._get_scaled_font(12), bg=colors["label_frame_bg"], fg=colors["label_fg"]).pack(fill="x", pady=(15, 2), padx=10)
        self.rate_entry = tk.Entry(stats_and_rate_frame, font=self._get_scaled_font(12), width=15,
                                   bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.rate_entry.pack(fill="x", pady=2, padx=10)
        tk.Button(stats_and_rate_frame, text="Сохранить ставку", command=lambda: self._save_worker_rate(worker_type, manage_window),
                  font=self._get_scaled_font(12), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799').pack(pady=(5, 10), padx=10)

        manage_window.protocol("WM_DELETE_WINDOW", lambda: self._on_manage_window_close(manage_window, worker_type))

    def _on_manage_window_close(self, window, worker_type):
        app_logger.info(f"Окно управления работниками для категории '{worker_type}' закрыто.")
        self._load_all_workers_from_db_cache() # Перезагружаем список работников из кэша
        window.destroy()
        # При закрытии окна управления работниками, просто перерисуем текущий экран
        # для обновления ComboBox и сводки. top_bar уже существует.
        if self.current_screen_type in self.operation_types: # Если текущий экран - это одна из операций
            self._clear_content_frame()
            self._create_operation_input_frame_content(self.main_content_area, self.current_screen_type)


    def _populate_worker_listbox(self, worker_type):
        self.worker_listbox.delete(0, tk.END)
        # ИЗМЕНЕНО: теперь d - это словарь, получаем имя по ключу 'name'
        for d in self.db.get_all_workers(worker_type=worker_type):
            self.worker_listbox.insert(tk.END, d.get('name', 'N/A'))
        app_logger.info(f"Список работников для категории '{worker_type}' обновлен в Listbox.")

    def _display_worker_stats_and_rate(self, event, worker_type):
        selected_index = self.worker_listbox.curselection()
        if not selected_index:
            self._reset_worker_stats_labels()
            self.rate_entry.delete(0, tk.END)
            app_logger.info("Выбор работника в Listbox сброшен.")
            return

        selected_worker_name = self.worker_listbox.get(selected_index[0])
        app_logger.info(f"Выбран работник '{selected_worker_name}' в Listbox для просмотра статистики.")

        selected_worker_info = None
        for d in self.db.get_all_workers(worker_type=worker_type):
            if d.get('name') == selected_worker_name:
                selected_worker_info = {'id': d.get('id'), 'rate': d.get('rate_per_sqm', 0.0)}
                break

        if not selected_worker_info:
            self._reset_worker_stats_labels()
            self.rate_entry.delete(0, tk.END)
            app_logger.warning(f"Информация для работника '{selected_worker_name}' не найдена в кэше.")
            return

        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, str(selected_worker_info['rate']))

        today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        five_days_ago_start = (today_start - datetime.timedelta(days=4))
        month_start_datetime = today_start.replace(day=1)

        worker_daily_area = 0.0
        worker_five_day_area = 0.0
        worker_monthly_area = 0.0
        worker_daily_hourly_payment = 0.0
        worker_five_day_hourly_payment = 0.0
        worker_monthly_hourly_payment = 0.0


        try:
            worker_area_entries = self.db.get_work_entries(worker_id=selected_worker_info['id'])
            for entry in worker_area_entries:
                entry_dt_str = entry.get('entry_datetime', '')
                if not entry_dt_str: continue
                try: entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try: entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d")
                    except ValueError: continue

                area = float(entry.get('area', 0.0))

                if today_start <= entry_dt_obj <= today_end: worker_daily_area += area
                if five_days_ago_start <= entry_dt_obj <= today_end: worker_five_day_area += area
                if month_start_datetime <= entry_dt_obj <= today_end: worker_monthly_area += area

            # НОВОЕ: расчет почасовой выработки
            worker_hourly_entries = self.db.get_hourly_work_entries(worker_id=selected_worker_info['id'])
            for entry in worker_hourly_entries:
                entry_dt_str = entry.get('entry_datetime', '')
                if not entry_dt_str: continue
                try: entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try: entry_dt_obj = datetime.datetime.strptime(entry_dt_str, "%Y-%m-%d")
                    except ValueError: continue

                payment = float(entry.get('payment_amount', 0.0))

                if today_start <= entry_dt_obj <= today_end: worker_daily_hourly_payment += payment
                if five_days_ago_start <= entry_dt_obj <= today_end: worker_five_day_hourly_payment += payment
                if month_start_datetime <= entry_dt_obj <= today_end: worker_monthly_hourly_payment += payment


        except Exception as e:
            app_logger.error(f"Ошибка при расчете выработки для работника '{selected_worker_name}': {e}")
            messagebox.showerror("Ошибка", f"Ошибка при расчете выработки для работника из кэша: {e}", parent=self.master)

        self.worker_stats_labels['today_area'].config(text=f"За сегодня (площадь): {worker_daily_area:.2f} м²", font=self._get_scaled_font(12))
        self.worker_stats_labels['5days_area'].config(text=f"За 5 дней (площадь): {worker_five_day_area:.2f} m²", font=self._get_scaled_font(12))
        self.worker_stats_labels['month_area'].config(text=f"За месяц (площадь): {worker_monthly_area:.2f} m²", font=self._get_scaled_font(12))

        # НОВОЕ: Обновление меток почасовой выработки
        self.worker_stats_labels['today_hourly'].config(text=f"За сегодня (почас.): {worker_daily_hourly_payment:.2f} руб.", font=self._get_scaled_font(12))
        self.worker_stats_labels['5days_hourly'].config(text=f"За 5 дней (почас.): {worker_five_day_hourly_payment:.2f} руб.", font=self._get_scaled_font(12))
        self.worker_stats_labels['month_hourly'].config(text=f"За месяц (почас.): {worker_monthly_hourly_payment:.2f} руб.", font=self._get_scaled_font(12))

    def _reset_worker_stats_labels(self):
        self.worker_stats_labels['today_area'].config(text="За сегодня (площадь): 0 м²", font=self._get_scaled_font(12))
        self.worker_stats_labels['5days_area'].config(text="За 5 дней (площадь): 0 м²", font=self._get_scaled_font(12))
        self.worker_stats_labels['month_area'].config(text="За месяц (площадь): 0 м²", font=self._get_scaled_font(12))
        self.worker_stats_labels['today_hourly'].config(text="За сегодня (почас.): 0 руб.", font=self._get_scaled_font(12))
        self.worker_stats_labels['5days_hourly'].config(text="За 5 дней (почас.): 0 руб.", font=self._get_scaled_font(12))
        self.worker_stats_labels['month_hourly'].config(text="За месяц (почас.): 0 руб.", font=self._get_scaled_font(12))


    def _save_worker_rate(self, worker_type, parent_window):
        selected_index = self.worker_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите работника для сохранения ставки.", parent=self.master)
            app_logger.warning("Попытка сохранить ставку без выбранного работника.")
            return

        worker_name = self.worker_listbox.get(selected_index[0])

        worker_id = None
        for d in self.db.get_all_workers(worker_type=worker_type):
            if d.get('name') == worker_name:
                worker_id = d.get('id')
                break

        if not worker_id:
            messagebox.showwarning("Ошибка", "Не удалось найти ID работника.", parent=self.master)
            app_logger.error(f"Не удалось найти ID работника '{worker_name}' для обновления ставки.")
            return

        try:
            new_rate = float(self.rate_entry.get().replace(',', '.'))
            if new_rate < 0:
                raise ValueError("Ставка не может быть отрицательной.")
        except ValueError as e:
            messagebox.showwarning("Ошибка ввода", f"Ставка должна быть числом: {e}", parent=self.master)
            app_logger.warning(f"Некорректный ввод ставки для '{worker_name}': '{self.rate_entry.get()}'. Ошибка: {e}")
            return

        def success_cb(result):
            messagebox.showinfo("Успех", f"Ставка для {worker_name} обновлена на {new_rate:.2f} руб./м².", parent=self.master)
            app_logger.info(f"Ставка для работника '{worker_name}' ({worker_type}) успешно обновлена на {new_rate:.2f} руб/м².")
            self._display_worker_stats_and_rate(None, worker_type)
            self.db.load_all_data_to_cache()
        def error_cb(e):
            app_logger.error(f"Не удалось обновить ставку для {worker_name} (асинхронная запись): {e}")
            messagebox.showerror("Ошибка", f"Не удалось обновить ставку для {worker_name} (асинхронная запись): {e}", parent=self.master)
            self.db.load_all_data_to_cache()

        try:
            self.db.update_worker_rate(worker_id, new_rate, success_cb, error_cb)
            self._display_worker_stats_and_rate(None, worker_type)
        except Exception as e:
            app_logger.error(f"Ошибка при попытке обновить ставку для '{worker_name}' (кэш): {e}")
            messagebox.showerror("Ошибка", f"Ошибка при попытке обновить ставку (кэш): {e}", parent=self.master)


    def _add_worker_dialog(self, worker_type, parent_window):
        app_logger.info(f"Открыт диалог добавления нового работника типа: '{worker_type}'.")
        new_worker_name = simpledialog.askstring("Добавить работника", f"Введите ФИО нового {worker_type.lower()}:",
                                                  parent=self.master)
        if new_worker_name and new_worker_name.strip():
            new_worker_name = new_worker_name.strip()

            # ИЗМЕНЕНО: Проверяем уникальность по имени среди ВСЕХ работников, независимо от типа
            existing_names_all = {d.get('name') for d in self.db.get_all_workers()}
            if new_worker_name in existing_names_all:
                messagebox.showwarning("Ошибка", "Работник с таким именем уже существует в базе данных.", parent=self.master)
                app_logger.warning(f"Попытка добавить существующего работника: '{new_worker_name}'.")
                return

            initial_rate = simpledialog.askfloat("Начальная ставка", f"Введите начальную ставку за 1 м² для {new_worker_name} (по умолчанию 0.0):",
                                                   initialvalue=0.0, parent=self.master)
            if initial_rate is None:
                app_logger.info("Добавление работника отменено на этапе ввода ставки.")
                return
            if initial_rate < 0:
                messagebox.showwarning("Ошибка", "Ставка не может быть отрицательной.", parent=self.master)
                app_logger.warning(f"Некорректный ввод начальной ставки ({initial_rate}) для нового работника: '{new_worker_name}'.")
                return

            def success_cb(result):
                messagebox.showinfo("Успех", f"{new_worker_name} добавлен в список {worker_type} со ставкой {initial_rate:.2f}.", parent=self.master)
                app_logger.info(f"Работник '{new_worker_name}' (ID: {result}, тип: {worker_type}) успешно добавлен со ставкой {initial_rate:.2f} руб/м².")
                self._populate_worker_listbox(worker_type)
                self.db.load_all_data_to_cache()
            def error_cb(e):
                app_logger.error(f"Ошибка при добавлении работника '{new_worker_name}' (асинхронная запись): {e}")
                messagebox.showerror("Ошибка БД", f"Ошибка при добавлении работника (асинхронная запись): {e}", parent=self.master)
                self.db.load_all_data_to_cache()

            try:
                self.db.add_worker(worker_type, new_worker_name, initial_rate, success_cb, error_cb)
                self._populate_worker_listbox(worker_type)
            except Exception as e:
                app_logger.error(f"Ошибка при попытке добавить работника '{new_worker_name}' (кэш): {e}")
                messagebox.showerror("Ошибка", f"Ошибка при попытке добавить работника (кэш): {e}", parent=self.master)


    def _delete_worker(self, worker_type, parent_window):
        selected_index = self.worker_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите работника для удаления.", parent=self.master)
            app_logger.warning("Попытка удалить работника без выбора в Listbox.")
            return

        worker_name_to_delete = self.worker_listbox.get(selected_index[0])

        worker_id_to_delete = None
        for d in self.db.get_all_workers(worker_type=worker_type):
            if d.get('name') == worker_name_to_delete:
                worker_id_to_delete = d.get('id')
                break

        if not worker_id_to_delete:
            messagebox.showwarning("Ошибка", "Работник не найден в базе данных (кэш).", parent=self.master)
            app_logger.error(f"Работник '{worker_name_to_delete}' не найден в кэше для удаления.")
            return

        if messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить {worker_name_to_delete} из списка {worker_type}?\nВсе связанные записи о выработке (по площади и почасовые) также будут удалены.", parent=self.master): # ИЗМЕНЕНО: текст подтверждения
            app_logger.info(f"Подтверждено удаление работника '{worker_name_to_delete}' (ID: {worker_id_to_delete}, тип: {worker_type}).")
            def success_cb(result):
                messagebox.showinfo("Успех", f"{worker_name_to_delete} удален из списка {worker_type}.", parent=self.master)
                app_logger.info(f"Работник '{worker_name_to_delete}' успешно удален из Google Sheets.")
                self._populate_worker_listbox(worker_type)
                self._reset_worker_stats_labels()
                self.rate_entry.delete(0, tk.END)
                self.db.load_all_data_to_cache()
            def error_cb(e):
                app_logger.error(f"Ошибка при удалении работника '{worker_name_to_delete}' (асинхронная запись): {e}")
                messagebox.showerror("Ошибка БД", f"Ошибка при удалении работника (асинхронная запись): {e}", parent=self.master)
                self.db.load_all_data_to_cache()

            try:
                if self.db.delete_worker(worker_id_to_delete, success_cb, error_cb):
                    self._populate_worker_listbox(worker_type)
                    self._reset_worker_stats_labels()
                    self.rate_entry.delete(0, tk.END)
                else:
                    app_logger.error(f"Не удалось удалить работника '{worker_name_to_delete}' (кэш), возможно, он не был найден.")
                    messagebox.showerror("Ошибка", f"Не удалось удалить работника {worker_name_to_delete} (кэш).", parent=self.master)
            except Exception as e:
                app_logger.error(f"Ошибка при попытке удаления работника '{worker_name_to_delete}' (кэш): {e}")
                messagebox.showerror("Ошибка", f"Ошибка при попытке удаления работника (кэш): {e}", parent=self.master)

    def _show_salary_dialog(self):
        app_logger.info("Попытка доступа к окну расчета зарплаты.")
        correct_salary_password = self.db.get_setting('salary_password', default_value="2025")
        password = simpledialog.askstring("Пароль", "Введите пароль для доступа к расчету зарплаты:", show='*', parent=self.master)

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Удаляем пробелы из введенного пароля ---
        if password is not None:
            password = password.strip()
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---

        if password == correct_salary_password:
            app_logger.info("Пароль для расчета зарплаты введен верно. Открытие окна расчета ЗП.")
            self._create_salary_calculation_window()
        elif password is not None: # Проверяем на None еще раз, чтобы отличить пустую строку от отмены
            messagebox.showerror("Ошибка", "Неверный пароль.", parent=self.master)
            app_logger.warning("Введен неверный пароль для доступа к расчету зарплаты.")
        else: # Пользователь нажал "Отмена"
            app_logger.info("Отмена ввода пароля для расчета зарплаты.")

    def _create_salary_calculation_window(self):
        app_logger.info("Открыто окно расчета заработной платы.")
        salary_window = tk.Toplevel(self.master)
        salary_window.title("Расчет Заработной Платы")
        salary_window.geometry("800x600")
        salary_window.transient(self.master)
        salary_window.grab_set()

        colors = self.styles[self.current_theme]
        salary_window.config(bg=colors["bg"])

        tk.Label(salary_window, text="Заработная плата", font=self._get_scaled_font(16, 'bold'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=15)

        # Диапазон дат
        date_range_frame = tk.Frame(salary_window, bg=colors["bg"])
        date_range_frame.pack(pady=5)
        tk.Label(date_range_frame, text="От:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.salary_start_date_entry = tk.Entry(date_range_frame, width=12, font=self._get_scaled_font(12),
                                                bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.salary_start_date_entry.pack(side="left", padx=5)
        tk.Label(date_range_frame, text="До:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.salary_end_date_entry = tk.Entry(date_range_frame, width=12, font=self._get_scaled_font(12),
                                              bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.salary_end_date_entry.pack(side="left", padx=5)

        today = datetime.date.today()
        five_days_ago = today - datetime.timedelta(days=4)
        self.salary_start_date_entry.insert(0, five_days_ago.strftime("%Y-%m-%d"))
        self.salary_end_date_entry.insert(0, today.strftime("%Y-%m-%d"))

        tk.Button(date_range_frame, text="Применить дату", command=self._populate_salary_table,
                  font=self._get_scaled_font(10), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799').pack(side="left", padx=10)

        export_button = tk.Button(date_range_frame, text="Экспорт в CSV", command=self._export_salary_to_csv,
                                  font=self._get_scaled_font(10), bg='#28A745', fg='white', bd=0, relief='raised', activebackground='#228B22')
        export_button.pack(side="left", padx=10)


        tree_frame = tk.Frame(salary_window, bg=colors["bg"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.salary_tree = ttk.Treeview(tree_frame, columns=("FIO", "Type", "AreaOutput", "AreaRate", "AreaSalary", "HourlyHours", "HourlyType", "HourlyPayment", "TotalSalary"), show="headings")
        self.salary_tree.pack(fill="both", expand=True)

        # ИСПРАВЛЕНИЕ: Увеличены ширины и добавлено stretch=tk.YES для колонок ФИО и Типа работника
        self.salary_tree.heading("FIO", text="ФИО Специалиста")
        self.salary_tree.heading("Type", text="Тип работника")
        self.salary_tree.heading("AreaOutput", text="Выработка (м²)")
        self.salary_tree.heading("AreaRate", text="Ставка (м²)")
        self.salary_tree.heading("AreaSalary", text="ЗП (м²)")
        self.salary_tree.heading("HourlyHours", text="Часы")
        self.salary_tree.heading("HourlyType", text="Почас. тип")
        self.salary_tree.heading("HourlyPayment", text="ЗП (почас.)")
        self.salary_tree.heading("TotalSalary", text="Общая ЗП (руб.)")

        # ИСПРАВЛЕНИЕ: Увеличены minwidth и width, добавлены stretch для ФИО и Типа
        self.salary_tree.column("FIO", width=int(200 * self.font_size_scale), minwidth=int(150 * self.font_size_scale), stretch=tk.YES, anchor="w")
        self.salary_tree.column("Type", width=int(120 * self.font_size_scale), minwidth=int(100 * self.font_size_scale), stretch=tk.YES, anchor="center")
        self.salary_tree.column("AreaOutput", width=int(90 * self.font_size_scale), stretch=tk.NO, anchor="e")
        self.salary_tree.column("AreaRate", width=int(90 * self.font_size_scale), stretch=tk.NO, anchor="e")
        self.salary_tree.column("AreaSalary", width=int(100 * self.font_size_scale), stretch=tk.NO, anchor="e")
        self.salary_tree.column("HourlyHours", width=int(60 * self.font_size_scale), stretch=tk.NO, anchor="e")
        self.salary_tree.column("HourlyType", width=int(100 * self.font_size_scale), stretch=tk.NO, anchor="center")
        self.salary_tree.column("HourlyPayment", width=int(100 * self.font_size_scale), stretch=tk.NO, anchor="e")
        self.salary_tree.column("TotalSalary", width=int(130 * self.font_size_scale), stretch=tk.NO, anchor="e")

        # Scrollbars
        tree_scrollbar_y = ttk.Scrollbar(self.salary_tree, orient="vertical", command=self.salary_tree.yview, style="TScrollbar")
        self.salary_tree.configure(yscrollcommand=tree_scrollbar_y.set)
        tree_scrollbar_y.pack(side="right", fill="y")
        tree_scrollbar_x = ttk.Scrollbar(self.salary_tree, orient="horizontal", command=self.salary_tree.xview, style="TScrollbar")
        self.salary_tree.configure(xscrollcommand=tree_scrollbar_x.set)
        tree_scrollbar_x.pack(side="bottom", fill="x")


        self._populate_salary_table()

    def _parse_date_input(self, date_string):
        try:
            return datetime.datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            app_logger.warning(f"Неверный формат даты: '{date_string}'. Ожидается ГГГГ-ММ-ДД.")
            messagebox.showerror("Ошибка даты", "Неверный формат даты. Используйте ГГГГ-ММ-ДД.", parent=self.master)
            return None

    def _populate_salary_table(self):
        for i in self.salary_tree.get_children():
            self.salary_tree.delete(i)

        start_date_str = self.salary_start_date_entry.get()
        end_date_str = self.salary_end_date_entry.get()

        start_dt = self._parse_date_input(start_date_str)
        end_dt = self._parse_date_input(end_date_str)

        if not start_dt or not end_dt:
            return

        # Учитываем полное время для диапазона
        start_datetime_filter = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime_filter = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        if start_datetime_filter > end_datetime_filter:
            messagebox.showwarning("Ошибка даты", "Дата начала не может быть позже даты окончания.", parent=self.master)
            app_logger.warning(f"Ошибка диапазона дат при расчете зарплаты: Дата начала ({start_datetime_filter}) позже даты окончания ({end_datetime_filter}).")
            return

        try:
            all_workers_data = self.db.get_all_workers()
            app_logger.info(f"Загрузка данных для таблицы зарплаты за период с {start_dt.strftime('%Y-%m-%d')} по {end_dt.strftime('%Y-%m-%d')}.")

            for worker_data in all_workers_data:
                worker_id = worker_data.get('id')
                worker_name = worker_data.get('name')
                area_rate = worker_data.get('rate_per_sqm', 0.0)
                worker_type = worker_data.get('type')

                if worker_id is None or worker_name is None:
                    app_logger.warning(f"Пропущен работник с неполными данными: ID={worker_id}, Name={worker_name}.")
                    continue

                # Выработка по площади
                worker_area_entries = self.db.get_work_entries(
                    worker_id=worker_id,
                    start_datetime=start_datetime_filter,
                    end_datetime=end_datetime_filter
                )
                total_area_output = sum(float(entry.get('area', 0.0)) for entry in worker_area_entries)
                total_area_salary = total_area_output * area_rate

                # НОВОЕ: Выработка почасовая
                worker_hourly_entries = self.db.get_hourly_work_entries(
                    worker_id=worker_id,
                    start_datetime=start_datetime_filter,
                    end_datetime=end_datetime_filter
                )
                total_hourly_sum_hours = sum(float(entry.get('hours', 0.0)) for entry in worker_hourly_entries)
                total_hourly_payment = sum(float(entry.get('payment_amount', 0.0)) for entry in worker_hourly_entries)

                total_salary = total_area_salary + total_hourly_payment

                self.salary_tree.insert("", "end", values=(
                    worker_name,
                    worker_type,
                    f"{total_area_output:.2f}",
                    f"{area_rate:.2f}",
                    f"{total_area_salary:.2f}",
                    f"{total_hourly_sum_hours:.1f}",
                    "Почасовая",
                    f"{total_hourly_payment:.2f}",
                    f"{total_salary:.2f}"
                ))
            app_logger.info("Таблица зарплаты успешно заполнена.")
        except Exception as e:
            app_logger.error(f"Ошибка при загрузке данных для зарплаты (из кэша): {e}")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных для зарплаты (из кэша): {e}", parent=self.master)

    def _export_salary_to_csv(self):
        app_logger.info("Запрошен экспорт отчета по зарплате в CSV.")
        # Собираем данные из Treeview
        data_to_export = []
        for child in self.salary_tree.get_children():
            values = self.salary_tree.item(child)['values']
            data_to_export.append({
                "ФИО Специалиста": values[0],
                "Тип работника": values[1],
                "Выработка (м²)": values[2],
                "Ставка (м²)": values[3],
                "ЗП (м²)": values[4],
                "Часы (почас.)": values[5],
                "Тип работы (почас.)": values[6],
                "ЗП (почас.)": values[7],
                "Общая ЗП (руб.)": values[8]
            })

        fieldnames = ["ФИО Специалиста", "Тип работника", "Выработка (м²)", "Ставка (м²)", "ЗП (м²)", "Часы (почас.)", "Тип работы (почас.)", "ЗП (почас.)", "Общая ЗП (руб.)"]
        filename = f"Зарплата_отчет_{self.salary_start_date_entry.get()}_до_{self.salary_end_date_entry.get()}.csv"
        self._export_to_csv(data_to_export, fieldnames, filename, "Экспорт отчета по зарплате")


    def _create_statistics_window(self):
        app_logger.info("Открыто окно статистики выработки.")
        stats_window = tk.Toplevel(self.master)
        stats_window.title("Статистика выработки")
        stats_window.geometry("900x700")
        stats_window.transient(self.master)
        stats_window.grab_set()

        colors = self.styles[self.current_theme]
        stats_window.config(bg=colors["bg"])

        tk.Label(stats_window, text="Статистика выработки по категориям", font=self._get_scaled_font(16, 'bold'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=15)

        control_frame = tk.Frame(stats_window, bg=colors["bg"])
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="Категория:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.stats_category_combobox = ttk.Combobox(control_frame, values=self.operation_types + ["Почасовая"], state="readonly", font=self._get_scaled_font(12), style="TCombobox", width=15)
        self.stats_category_combobox.pack(side="left", padx=5)
        self.stats_category_combobox.set(self.operation_types[0])

        tk.Label(control_frame, text="От:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.stats_start_date_entry = tk.Entry(control_frame, width=12, font=self._get_scaled_font(12),
                                               bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.stats_start_date_entry.pack(side="left", padx=5)
        tk.Label(control_frame, text="До:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.stats_end_date_entry = tk.Entry(control_frame, width=12, font=self._get_scaled_font(12),
                                             bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.stats_end_date_entry.pack(side="left", padx=5)

        today = datetime.date.today()
        month_start = today.replace(day=1)
        self.stats_start_date_entry.insert(0, month_start.strftime("%Y-%m-%d"))
        self.stats_end_date_entry.insert(0, today.strftime("%Y-%m-%d"))

        tk.Button(control_frame, text="Применить", command=self._update_statistics_chart,
                  font=self._get_scaled_font(10), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799').pack(side="left", padx=10)

        export_button = tk.Button(control_frame, text="Экспорт в CSV", command=self._export_statistics_to_csv,
                                  font=self._get_scaled_font(10), bg='#28A745', fg='white', bd=0, relief='raised', activebackground='#228B22')
        export_button.pack(side="left", padx=10)

        self.stats_category_combobox.bind("<<ComboboxSelected>>", self._update_statistics_chart)

        self.chart_frame = tk.Frame(stats_window, bg=colors["bg"])
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._update_statistics_chart(None) # Initial chart draw


    def _update_statistics_chart(self, event=None):
        selected_category = self.stats_category_combobox.get()

        start_date_str = self.stats_start_date_entry.get()
        end_date_str = self.stats_end_date_entry.get()

        start_dt = self._parse_date_input(start_date_str)
        end_dt = self._parse_date_input(end_date_str)

        if not start_dt or not end_dt:
            return

        start_datetime_filter = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime_filter = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        if start_datetime_filter > end_datetime_filter:
            messagebox.showwarning("Ошибка даты", "Дата начала не может быть позже даты окончания.", parent=self.master)
            app_logger.warning(f"Ошибка диапазона дат при построении статистики: Дата начала ({start_datetime_filter}) позже даты окончания ({end_datetime_filter}).")
            return

        app_logger.info(f"Построение статистики для категории '{selected_category}' за период с {start_dt.strftime('%Y-%m-%d')} по {end_dt.strftime('%Y-%m-%d')}.")


        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        workers_output = {}

        try:
            if selected_category == "Почасовая":
                workers_in_category = self.db.get_all_workers()
                for worker_data in workers_in_category:
                    name = worker_data.get('name')
                    worker_id = worker_data.get('id')
                    entries_for_worker = self.db.get_hourly_work_entries(
                        worker_id=worker_id,
                        start_datetime=start_datetime_filter,
                        end_datetime=end_datetime_filter
                    )
                    total_payment = sum(float(entry.get('payment_amount', 0.0)) for entry in entries_for_worker)
                    if total_payment > 0:
                        workers_output[name] = total_payment
                y_label = f"Выработка (руб.) за период {start_date_str} - {end_date_str}"
                title_text = f"Выработка по почасовой работе (по работникам)"
            else:
                workers_in_category = self.db.get_all_workers(worker_type=selected_category)
                for worker_data in workers_in_category:
                    name = worker_data.get('name')
                    worker_id = worker_data.get('id')
                    entries_for_worker = self.db.get_work_entries(
                        worker_id=worker_id,
                        start_datetime=start_datetime_filter,
                        end_datetime=end_datetime_filter
                    )
                    total_area = sum(float(entry.get('area', 0.0)) for entry in entries_for_worker)
                    if total_area > 0:
                        workers_output[name] = total_area
                y_label = f"Выработка (м²) за период {start_date_str} - {end_date_str}"
                title_text = f"Выработка {selected_category} (по работникам)"


        except Exception as e:
            app_logger.error(f"Ошибка при получении данных для статистики (из кэша): {e}")
            messagebox.showerror("Ошибка", f"Ошибка при получении данных для статистики (из кэша): {e}", parent=self.master)
            return

        if not workers_output:
            tk.Label(self.chart_frame, text="Нет данных для выбранной категории за указанный период.", font=self._get_scaled_font(14), bg=self.styles[self.current_theme]["bg"], fg=self.styles[self.current_theme]["fg"]).pack(pady=50)
            app_logger.info("Нет данных для построения графика статистики за выбранный период.")
            return

        sorted_workers = sorted(workers_output.items(), key=lambda item: item[1], reverse=True)
        names = [item[0] for item in sorted_workers]
        values = [item[1] for item in sorted_workers]

        fig, ax = plt.subplots(figsize=(8, 5))

        if self.current_theme == "dark":
            fig.patch.set_facecolor(self.styles["dark"]["bg"])
            ax.set_facecolor(self.styles["dark"]["frame_bg"])
            ax.tick_params(axis='x', colors=self.styles["dark"]["fg"])
            ax.tick_params(axis='y', colors=self.styles["dark"]["fg"])
            ax.xaxis.label.set_color(self.styles["dark"]["fg"])
            ax.yaxis.label.set_color(self.styles["dark"]["fg"])
            ax.title.set_color(self.styles["dark"]["fg"])
            ax.spines['bottom'].set_color(self.styles["dark"]["fg"])
            ax.spines['left'].set_color(self.styles["dark"]["fg"])
            ax.spines['top'].set_color(self.styles["dark"]["fg"])
            ax.spines['right'].set_color(self.styles["dark"]["fg"])
            bar_color = "#4CAF50"
        else:
            fig.patch.set_facecolor(self.styles["light"]["bg"])
            ax.set_facecolor(self.styles["light"]["frame_bg"])
            ax.tick_params(axis='x', colors=self.styles["light"]["fg"])
            ax.tick_params(axis='y', colors=self.styles["light"]["fg"])
            ax.xaxis.label.set_color(self.styles["light"]["fg"])
            ax.yaxis.label.set_color(self.styles["light"]["fg"])
            ax.title.set_color(self.styles["light"]["fg"])
            ax.spines['bottom'].set_color(self.styles["light"]["fg"])
            ax.spines['left'].set_color(self.styles["light"]["fg"])
            ax.spines['top'].set_color(self.styles["light"]["fg"])
            ax.spines['right'].set_color(self.styles["light"]["fg"])
            bar_color = "#007BFF"

        ax.bar(names, values, color=bar_color)
        ax.set_xlabel("Работник", font=self._get_scaled_font(12))
        ax.set_ylabel(y_label, font=self._get_scaled_font(12))
        ax.set_title(title_text, font=self._get_scaled_font(14, 'bold'))

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(int(plt.rcParams['font.size'] * self.font_size_scale * 0.8))
            if self.current_theme == "dark":
                label.set_color(self.styles["dark"]["fg"])
            else:
                label.set_color(self.styles["light"]["fg"])


        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.chart_frame)
        toolbar.update()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        app_logger.info(f"График статистики для категории '{selected_category}' успешно построен.")

    def _export_statistics_to_csv(self):
        app_logger.info("Запрошен экспорт статистики выработки в CSV.")
        # Собираем данные для экспорта
        selected_category = self.stats_category_combobox.get()
        start_date_str = self.stats_start_date_entry.get()
        end_date_str = self.stats_end_date_entry.get()

        start_dt = self._parse_date_input(start_date_str)
        end_dt = self._parse_date_input(end_date_str)
        if not start_dt or not end_dt: return

        start_datetime_filter = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_datetime_filter = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        data_to_export = []
        try:
            if selected_category == "Почасовая":
                workers_in_category = self.db.get_all_workers()
                fieldnames = ['Работник', 'Выработка (руб.)']
                for worker_data in workers_in_category:
                    name = worker_data.get('name')
                    worker_id = worker_data.get('id')
                    entries_for_worker = self.db.get_hourly_work_entries(
                        worker_id=worker_id,
                        start_datetime=start_datetime_filter,
                        end_datetime=end_datetime_filter
                    )
                    total_payment = sum(float(entry.get('payment_amount', 0.0)) for entry in entries_for_worker)
                    data_to_export.append({'Работник': name, 'Выработка (руб.)': f"{total_payment:.2f}"})
            else:
                workers_in_category = self.db.get_all_workers(worker_type=selected_category)
                fieldnames = ['Работник', 'Выработка (м²)']
                for worker_data in workers_in_category:
                    name = worker_data.get('name')
                    worker_id = worker_data.get('id')
                    entries_for_worker = self.db.get_work_entries(
                        worker_id=worker_id,
                        start_datetime=start_datetime_filter,
                        end_datetime=end_datetime_filter
                    )
                    total_area = sum(float(entry.get('area', 0.0)) for entry in entries_for_worker)
                    data_to_export.append({'Работник': name, 'Выработка (м²)': f"{total_area:.2f}"})

        except Exception as e:
            app_logger.error(f"Ошибка при сборе данных для экспорта статистики в CSV: {e}")
            messagebox.showerror("Ошибка экспорта", f"Не удалось собрать данные для экспорта: {e}", parent=self.master)
            return

        filename = f"Статистика_{selected_category}_{start_date_str}_до_{end_date_str}.csv"
        self._export_to_csv(data_to_export, fieldnames, filename, "Экспорт статистики выработки")


    def _change_login_password(self):
        """Функция для изменения пароля входа."""
        app_logger.info("Открыт диалог изменения пароля входа.")
        new_pass = simpledialog.askstring("Изменить пароль", "Введите новый пароль:", show='*', parent=self.master)
        if new_pass:
            new_pass = new_pass.strip() # Очищаем пробелы перед проверкой и сохранением
            confirm_pass = simpledialog.askstring("Изменить пароль", "Подтвердите новый пароль:", show='*', parent=self.master)
            if confirm_pass is not None: # Убедимся, что пользователь не нажал "Отмена" на втором диалоге
                confirm_pass = confirm_pass.strip() # Очищаем пробелы для сравнения
                if new_pass == confirm_pass:
                    def success_cb(result):
                        messagebox.showinfo("Успех", "Пароль входа успешно изменен! (Примечание: пароль для входа в приложение сейчас не запрашивается).", parent=self.master)
                        app_logger.info("Пароль входа успешно изменен.")
                        self.db.load_all_data_to_cache()
                    def error_cb(e):
                        app_logger.error(f"Не удалось изменить пароль входа (асинхронная запись): {e}")
                        messagebox.showerror("Ошибка", f"Не удалось изменить пароль (асинхронная запись): {e}", parent=self.master)
                        self.db.load_all_data_to_cache()
                    try:
                        self.db.update_setting('password', new_pass, success_cb, error_cb)
                    except Exception as e:
                        app_logger.error(f"Не удалось обновить пароль входа (кэш): {e}")
                        messagebox.showerror("Ошибка", f"Не удалось обновить пароль (кэш): {e}", parent=self.master)
                else:
                    messagebox.showwarning("Ошибка", "Пароли не совпадают.", parent=self.master)
                    app_logger.warning("Пароли для изменения пароля входа не совпали.")
            else:
                messagebox.showwarning("Отмена", "Изменение пароля отменено (подтверждение отменено).", parent=self.master)
                app_logger.info("Изменение пароля входа отменено пользователем на этапе подтверждения.")
        else:
            messagebox.showwarning("Отмена", "Изменение пароля отменено.", parent=self.master)
            app_logger.info("Изменение пароля входа отменено пользователем.")

    def _change_salary_password(self):
        """Функция для изменения пароля расчета ЗП."""
        app_logger.info("Открыт диалог изменения пароля для расчета ЗП.")
        new_pass = simpledialog.askstring("Изменить пароль ЗП", "Введите новый пароль для расчета зарплаты:", show='*', parent=self.master)
        if new_pass:
            new_pass = new_pass.strip() # Очищаем пробелы перед проверкой и сохранением
            confirm_pass = simpledialog.askstring("Изменить пароль ЗП", "Подтвердите новый пароль:", show='*', parent=self.master)
            if confirm_pass is not None: # Убедимся, что пользователь не нажал "Отмена" на втором диалоге
                confirm_pass = confirm_pass.strip() # Очищаем пробелы для сравнения
                if new_pass == confirm_pass:
                    def success_cb(result):
                        messagebox.showinfo("Успех", "Пароль расчета ЗП успешно изменен!", parent=self.master)
                        app_logger.info("Пароль для расчета ЗП успешно изменен.")
                        self.db.load_all_data_to_cache()
                    def error_cb(e):
                        app_logger.error(f"Не удалось изменить пароль ЗП (асинхронная запись): {e}")
                        messagebox.showerror("Ошибка", f"Не удалось изменить пароль ЗП (асинхронная запись): {e}", parent=self.master)
                        self.db.load_all_data_to_cache()
                    try:
                        self.db.update_setting('salary_password', new_pass, success_cb, error_cb)
                    except Exception as e:
                        app_logger.error(f"Не удалось обновить пароль ЗП (кэш): {e}")
                        messagebox.showerror("Ошибка", f"Не удалось обновить пароль ЗП (кэш): {e}", parent=self.master)
                else:
                    messagebox.showwarning("Ошибка", "Пароли не совпадают.", parent=self.master)
                    app_logger.warning("Пароли для изменения пароля ЗП не совпали.")
            else:
                messagebox.showwarning("Отмена", "Изменение пароля ЗП отменено (подтверждение отменено).", parent=self.master)
                app_logger.info("Изменение пароля для расчета ЗП отменено пользователем на этапе подтверждения.")
        else:
            messagebox.showwarning("Отмена", "Изменение пароля ЗП отменено.", parent=self.master)
            app_logger.info("Изменение пароля для расчета ЗП отменено пользователем.")

    def _open_manage_entries_window(self):
        """Открывает окно для просмотра и удаления записей выработки."""
        app_logger.info("Открыто окно управления записями выработки.")
        manage_entries_window = tk.Toplevel(self.master)
        manage_entries_window.title("Управление записями выработки")
        manage_entries_window.geometry("1000x700")
        manage_entries_window.transient(self.master)
        manage_entries_window.grab_set()

        colors = self.styles[self.current_theme]
        manage_entries_window.config(bg=colors["bg"])

        # Control frame for filters and buttons
        control_frame = tk.Frame(manage_entries_window, bg=colors["bg"])
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Категория:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.entry_filter_category_combobox = ttk.Combobox(control_frame, values=["Все"] + self.operation_types + self.hourly_work_types, state="readonly", font=self._get_scaled_font(12), style="TCombobox", width=15)
        self.entry_filter_category_combobox.set("Все")
        self.entry_filter_category_combobox.pack(side="left", padx=5)

        tk.Label(control_frame, text="Работник:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.entry_filter_worker_combobox = ttk.Combobox(control_frame, values=["Все"] + [w.get('name') for w in self.db.get_all_workers()], state="readonly", font=self._get_scaled_font(12), style="TCombobox", width=20)
        self.entry_filter_worker_combobox.set("Все")
        self.entry_filter_worker_combobox.pack(side="left", padx=5)

        tk.Label(control_frame, text="От:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.entry_filter_start_date_entry = tk.Entry(control_frame, width=12, font=self._get_scaled_font(12),
                                                      bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.entry_filter_start_date_entry.pack(side="left", padx=5)
        self.entry_filter_start_date_entry.insert(0, (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")) # по умолчанию за месяц

        tk.Label(control_frame, text="До:", font=self._get_scaled_font(12), bg=colors["bg"], fg=colors["label_fg"]).pack(side="left", padx=5)
        self.entry_filter_end_date_entry = tk.Entry(control_frame, width=12, font=self._get_scaled_font(12),
                                                    bg=colors["entry_bg"], fg=colors["entry_fg"], bd=1, relief='solid', insertbackground=colors["fg"])
        self.entry_filter_end_date_entry.pack(side="left", padx=5)
        self.entry_filter_end_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Button(control_frame, text="Показать записи", command=self._populate_entries_treeview,
                  font=self._get_scaled_font(10), bg='#008CBA', fg='white', bd=0, relief='raised', activebackground='#007799').pack(side="left", padx=10)

        # Treeview for displaying entries
        tree_frame = tk.Frame(manage_entries_window, bg=colors["bg"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.entries_tree = ttk.Treeview(tree_frame, columns=("ID", "Worker", "Type", "EntryType", "DateTime", "Width", "Length", "Quantity", "Area", "Hours", "Payment"), show="headings")
        self.entries_tree.pack(fill="both", expand=True)

        self.entries_tree.heading("ID", text="ID", anchor="center")
        self.entries_tree.heading("Worker", text="Работник", anchor="w")
        self.entries_tree.heading("Type", text="Цех/Тип", anchor="center")
        self.entries_tree.heading("EntryType", text="Тип записи", anchor="center")
        self.entries_tree.heading("DateTime", text="Дата/Время", anchor="center")
        self.entries_tree.heading("Width", text="Шир. (см)", anchor="center")
        self.entries_tree.heading("Length", text="Дл. (см)", anchor="center")
        self.entries_tree.heading("Quantity", text="Кол-во (шт)", anchor="center")
        self.entries_tree.heading("Area", text="Площадь (м²)", anchor="e")
        self.entries_tree.heading("Hours", text="Часы", anchor="center")
        self.entries_tree.heading("Payment", text="Оплата (руб.)", anchor="e")

        self.entries_tree.column("ID", width=50, stretch=tk.NO)
        self.entries_tree.column("Worker", width=120, stretch=tk.YES) # Stretch enabled
        self.entries_tree.column("Type", width=80, stretch=tk.NO)
        self.entries_tree.column("EntryType", width=80, stretch=tk.NO)
        self.entries_tree.column("DateTime", width=120, stretch=tk.NO)
        self.entries_tree.column("Width", width=60, stretch=tk.NO)
        self.entries_tree.column("Length", width=60, stretch=tk.NO)
        self.entries_tree.column("Quantity", width=60, stretch=tk.NO)
        self.entries_tree.column("Area", width=80, stretch=tk.NO)
        self.entries_tree.column("Hours", width=60, stretch=tk.NO)
        self.entries_tree.column("Payment", width=80, stretch=tk.NO)

        # Scrollbar for Treeview
        tree_scrollbar_y = ttk.Scrollbar(self.entries_tree, orient="vertical", command=self.entries_tree.yview, style="TScrollbar")
        self.entries_tree.configure(yscrollcommand=tree_scrollbar_y.set)
        tree_scrollbar_y.pack(side="right", fill="y")
        tree_scrollbar_x = ttk.Scrollbar(self.entries_tree, orient="horizontal", command=self.entries_tree.xview, style="TScrollbar")
        self.entries_tree.configure(xscrollcommand=tree_scrollbar_x.set)
        tree_scrollbar_x.pack(side="bottom", fill="x")

        # Delete button
        delete_button = tk.Button(manage_entries_window, text="Удалить выбранные записи", command=self._delete_selected_entries,
                                  font=self._get_scaled_font(12, 'bold'), bg='#f44336', fg='white', bd=0, relief='raised', activebackground='#C4332A')
        delete_button.pack(pady=10)

        self._populate_entries_treeview() # Initial populate

    def _populate_entries_treeview(self):
        """Заполняет Treeview записями выработки с учетом фильтров."""
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        selected_category = self.entry_filter_category_combobox.get()
        selected_worker_name = self.entry_filter_worker_combobox.get()
        start_date_str = self.entry_filter_start_date_entry.get()
        end_date_str = self.entry_filter_end_date_entry.get()
        app_logger.info(f"Обновление Treeview записей: Категория='{selected_category}', Работник='{selected_worker_name}', Дата='{start_date_str}' - '{end_date_str}'.")

        filter_operation_type = selected_category if selected_category in self.operation_types else None
        filter_work_type = selected_category if selected_category in self.hourly_work_types else None

        filter_worker_id = None
        if selected_worker_name != "Все":
            for w in self.db.get_all_workers():
                if w.get('name') == selected_worker_name:
                    filter_worker_id = w.get('id')
                    break
            if filter_worker_id is None: # Если имя работника выбрано, но ID не найден (ошибка)
                messagebox.showwarning("Ошибка фильтра", f"Работник '{selected_worker_name}' не найден.", parent=self.master)
                app_logger.warning(f"Ошибка фильтра: Работник '{selected_worker_name}' не найден для ID.")
                return

        start_dt_obj = self._parse_date_input(start_date_str)
        end_dt_obj = self._parse_date_input(end_date_str)

        if not start_dt_obj or not end_dt_obj:
            return

        start_dt_filter = start_dt_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt_filter = end_dt_obj.replace(hour=23, minute=59, second=59, microsecond=999999)

        all_entries_to_display = []

        # Получаем и обрабатываем записи по площади
        # Показываем только если выбрана "Все" категории, или конкретная категория по площади
        if selected_category == "Все" or selected_category in self.operation_types:
            filtered_area_entries = self.db.get_work_entries(
                operation_type=filter_operation_type,
                worker_id=filter_worker_id,
                start_datetime=start_dt_filter,
                end_datetime=end_dt_filter
            )
            for entry in filtered_area_entries:
                # Добавляем флаг is_hourly=False
                entry['is_hourly'] = False
                all_entries_to_display.append(entry)

        # Получаем и обрабатываем почасовые записи
        # Показываем только если выбрана "Все" категории, или конкретная почасовая категория
        if selected_category == "Все" or selected_category in self.hourly_work_types:
            filtered_hourly_entries = self.db.get_hourly_work_entries(
                work_type=filter_work_type,
                worker_id=filter_worker_id,
                start_datetime=start_dt_filter,
                end_datetime=end_dt_filter
            )
            for entry in filtered_hourly_entries:
                # Добавляем флаг is_hourly=True
                entry['is_hourly'] = True
                all_entries_to_display.append(entry)

        # Сортируем все записи по дате
        all_entries_to_display.sort(key=lambda x: datetime.datetime.strptime(x.get('entry_datetime'), "%Y-%m-%d %H:%M:%S") if 'entry_datetime' in x else datetime.datetime.min, reverse=True)


        try:
            worker_id_to_name_map = {w.get('id'): w.get('name') for w in self.db.get_all_workers()}

            for entry in all_entries_to_display:
                worker_name = worker_id_to_name_map.get(entry.get('worker_id'), "Неизвестный работник")

                if not entry.get('is_hourly'): # Запись по площади
                    self.entries_tree.insert("", "end", iid=entry['id'], tags=('area_entry',), values=(
                        entry.get('id'),
                        worker_name,
                        entry.get('operation_type'),
                        "Площадь",
                        entry.get('entry_datetime'),
                        f"{entry.get('width', 0.0):.2f}",
                        f"{entry.get('length', 0.0):.2f}",
                        entry.get('quantity', 0),
                        f"{entry.get('area', 0.0):.2f}",
                        "",
                        ""
                    ))
                else: # Почасовая запись
                    self.entries_tree.insert("", "end", iid=entry['id'], tags=('hourly_entry',), values=(
                        entry.get('id'),
                        worker_name,
                        entry.get('work_type'),
                        "Почасовая",
                        entry.get('entry_datetime'),
                        "",
                        "",
                        "",
                        "",
                        f"{entry.get('hours', 0):.1f}",
                        f"{entry.get('payment_amount', 0.0):.2f}"
                    ))
            app_logger.info(f"Treeview записей выработки заполнено. Отображено {len(all_entries_to_display)} записей.")
        except Exception as e:
            app_logger.error(f"Ошибка при заполнении таблицы записей выработки: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке записей выработки: {e}", parent=self.master)

    def _delete_selected_entries(self):
        """Удаляет выбранные записи выработки из базы данных."""
        selected_items_ids = self.entries_tree.selection()
        if not selected_items_ids:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите записи для удаления.", parent=self.master)
            app_logger.warning("Попытка удалить записи без выбора.")
            return

        if not messagebox.askyesno("Подтверждение удаления",
                                   f"Вы уверены, что хотите удалить {len(selected_items_ids)} выбранных записей?\nЭто действие необратимо.",
                                   parent=self.master):
            app_logger.info("Удаление записей отменено пользователем.")
            return

        app_logger.info(f"Подтверждено удаление {len(selected_items_ids)} записей выработки.")
        # Запускаем удаление в отдельном потоке, чтобы не блокировать UI
        def delete_thread_target():
            success_count = 0
            failed_count = 0
            for item_id in selected_items_ids:
                entry_id = int(item_id)
                # Определяем, является ли запись почасовой или по площади, используя теги
                item_tags = self.entries_tree.item(item_id, 'tags')
                is_hourly = 'hourly_entry' in item_tags

                def success_cb(result):
                    nonlocal success_count
                    success_count += 1
                    app_logger.info(f"Запись ID: {entry_id} (тип записи: {'почасовая' if is_hourly else 'по площади'}) успешно удалена из Google Sheets.")

                def error_cb(e):
                    nonlocal failed_count
                    failed_count += 1
                    app_logger.error(f"Ошибка удаления записи ID: {entry_id} (тип записи: {'почасовая' if is_hourly else 'по площади'}) из Google Sheets: {e}")
                    self.master.after(0, lambda: messagebox.showerror("Ошибка удаления", f"Не удалось удалить запись ID: {entry_id}\nОшибка: {e}", parent=self.master))

                try:
                    self.db.delete_work_entry(entry_id, is_hourly, success_cb, error_cb)
                except Exception as e:
                    app_logger.error(f"Ошибка при запросе на удаление записи ID: {entry_id} (тип записи: {'почасовая' if is_hourly else 'по площади'}) (кэш): {e}")
                    self.master.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при попытке удалить запись ID: {entry_id} (кэш): {e}", parent=self.master))
                    failed_count += 1
                time.sleep(0.1) # Небольшая задержка, чтобы не перегружать Google Sheets API

            # Обновляем UI и кэш после завершения всех операций удаления
            self.master.after(0, self._populate_entries_treeview)
            self.master.after(0, self.db.load_all_data_to_cache)
            self.master.after(0, lambda: messagebox.showinfo("Результаты удаления",
                                                         f"Удаление завершено.\nУспешно удалено: {success_count}\nНеудачно: {failed_count}",
                                                         parent=self.master))
            app_logger.info(f"Операция удаления записей завершена. Успешно: {success_count}, Неудачно: {failed_count}.")

        threading.Thread(target=delete_thread_target).start()
        messagebox.showinfo("Удаление запущено", "Записи удаляются в фоновом режиме. Пожалуйста, ожидайте.", parent=self.master)
        # Очищаем Treeview сразу после запуска удаления, чтобы визуально показать начало процесса
        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)


    def _create_help_screen_content(self, parent_frame):
        colors = self.styles[self.current_theme]
        app_logger.info("Открыт экран справки.")

        tk.Label(parent_frame, text="Справка по приложению «Мастер Цеха»", font=self._get_scaled_font(18, 'bold'),
                 bg=colors["bg"], fg=colors["fg"]).pack(pady=20)

        help_text_content = """
Это приложение создано для удобного учета выработки на производстве и управления данными о сотрудниках.

--- Основные функции ---

1. **Учет выработки (Раскройщики, Упаковщицы, Обработка, Грузчики):**
    *   Выберите категорию работника из меню слева.
    *   Выберите работника из выпадающего списка. Если работника нет, добавьте его в "Настройках".
    *   Введите ширину, длину детали (в см) и количество штук. Приложение автоматически рассчитает площадь в м².
    *   Нажмите "Записать выработку (площадь)", чтобы сохранить данные в Google Таблице.
    *   Вы можете видеть сводку выработки (м²) за сегодня, за 5 дней и за месяц, а также индивидуальную выработку по каждому сотруднику.
    *   **НОВОЕ: Почасовая работа (Уборка, Мойка):**
        *   В отдельном блоке "Ввод данных (почасовая работа)" выберите работника, тип работы и количество часов.
        *   Нажмите "Записать почасовую работу", чтобы сохранить данные в Google Таблице.
        *   Оплата рассчитывается автоматически на основе тарифов, установленных в "Настройках".
    *   **НОВОЕ: Сворачиваемые блоки ввода:** Над каждым блоком ввода данных (по площади и почасовой) появилась кнопка для его сворачивания/разворачивания, чтобы освободить место на экране. Состояние (свернут/развернут) сохраняется при переключении между экранами.

2. **Начало/Конец смены мастера:**
    *   В самом низу левого меню расположены кнопки "Начало смены" и "Конец смены".
    *   При нажатии "Начало смены" фиксируется время старта.
    *   При нажатии "Конец смены" фиксируется время завершения, рассчитывается длительность смены, суммируется вся выработка по категориям за этот период и начисляется зарплата мастера (исходя из фиксированной часовой ставки 250 руб/час). Все данные сохраняются в Google Таблице.
    *   После завершения смены предлагается **скачать сводки выработки** за смену и за последнюю неделю в формате CSV (совместимо с Excel). Сводки теперь включают как выработку по площади, так и почасовую оплату.

--- Настройки ---

Доступны через кнопку "Настройки" в левом меню.
*   **Управление работниками (по категориям):**
    *   Позволяет добавлять новых работников (ФИО, начальная ставка за м²).
    *   Удалять существующих работников (внимание: при удалении работника удаляются и все его записи о выработке **по площади и почасовые**!).
    *   Изменять ставку за м² для выбранного работника.
    *   Просматривать индивидуальную статистику выработки работника (за сегодня, за 5 дней, за месяц) - теперь включает **как площадь, так и почасовую оплату**.
*   **НОВОЕ: Тарифы почасовой работы:**
    *   Позволяет устанавливать ставки оплаты за час для "Уборки" и "Мойки". Нажмите "Сохранить тарифы" после изменения.
*   **Сменить тему приложения:** Переключает между светлой и темной темой оформления.
*   **Рассчитать Заработную плату:** Открывает окно с таблицей, показывающей выработку и расчет зарплаты для каждого работника за выбранный произвольный период. **Расчет теперь учитывает оба типа выработки (по площади и почасовую).** Есть возможность экспорта в CSV.
*   **Статистика выработки:** Открывает окно с графиками выработки по выбранным категориям работников за выбранный произвольный период. **Теперь можно просматривать статистику по "Почасовой" работе (в рублях).** Есть возможность экспорта в CSV.
*   **Удаление записей выработки:** Открывает окно для просмотра и **удаления отдельных записей** о выработке. Можно фильтровать по дате, категории и работнику. **Отображает как записи по площади, так и почасовые записи.**
*   **Изменить пароль входа:** Позволяет изменить пароль, который может быть запрошен при запуске приложения (если защита паролем будет включена в будущем).
*   **Изменить пароль ЗП:** Позволяет изменить пароль для доступа к расчету заработной платы.
*   **Изменить размер букв:** Открывает диалог для изменения масштаба шрифтов во всем приложении (Маленький, Средний, Большой, Огромный). Настройка сохраняется.

--- Дополнительные возможности ---

*   **Навигация "Назад/Вперед":** В верхней части основного экрана расположены кнопки со стрелками, позволяющие переходить между ранее открытыми экранами приложения (например, вернуться из "Настроек" на "Учет выработки").
*   **Совет дня:** На экране учета выработки отображается случайная мудрая мысль или совет. Вы можете нажать "Новый совет", чтобы получить другую мысль, или "X", чтобы скрыть этот блок на текущую сессию.
*   **Сохранение настроек:** Тема приложения, размер шрифта, а также пароли и **тарифы почасовой работы** сохраняются в Google Таблице, что обеспечивает их сохранность и доступность.
*   **Индикатор статуса соединения:** В правом верхнем углу приложения отображается текущий статус соединения с Google Sheets ("Онлайн", "Сохранение...", "Офлайн", "Ошибка сохранения").
*   **Автоматическое обновление данных:** Кэш данных из Google Таблиц обновляется автоматически каждые 5 минут, чтобы обеспечить актуальность данных.
*   **Логирование ошибок:** Все критические ошибки и предупреждения записываются в файл `app_errors.log` в папке приложения для удобства отладки.
*   **Плейсхолдеры и авто-фокус:** Поля ввода выработки содержат подсказки (примеры значений) и автоматически фокусируются на первом поле после записи для быстрого последовательного ввода.
*   **Кнопки "Очистить поля":** Быстрая очистка полей ввода выработки.
*   **НОВОЕ: Прокрутка списка выработки:** В блоке "Индивидуальная выработка" теперь можно прокручивать список с помощью колесика мыши и стрелок клавиатуры (клавиши "Вверх", "Вниз", "PageUp", "PageDown").

--- Важные примечания ---

*   Приложение требует активного подключения к интернету и правильно настроенного `service_account.json` для работы с Google Таблицами.
*   Все данные о выработке и сменах сохраняются в вашей Google Таблице, что обеспечивает их сохранность и доступность.
"""
        text_widget = tk.Text(parent_frame, wrap="word", font=self._get_scaled_font(11),
                              bg=colors["entry_bg"], fg=colors["entry_fg"],
                              bd=0, padx=10, pady=10, relief="flat")
        text_widget.insert(tk.END, help_text_content.strip())
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview, style="TScrollbar")
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")


    def _go_back(self):
        if self.current_history_index > 0:
            self.is_history_navigation = True
            self.current_history_index -= 1
            app_logger.info(f"Навигация: Назад к экрану '{self.screen_history[self.current_history_index]}'.")
            self.show_screen(self.screen_history[self.current_history_index])

    def _go_forward(self):
        if self.current_history_index < len(self.screen_history) - 1:
            self.is_history_navigation = True
            self.current_history_index += 1
            app_logger.info(f"Навигация: Вперед к экрану '{self.screen_history[self.current_history_index]}'.")
            self.show_screen(self.screen_history[self.current_history_index])

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- Функция для показа Splash-скрина и обработки запуска приложения ---
def show_splash_screen(root, app):
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    splash_width = 500
    splash_height = 250
    x = (screen_width / 2) - (splash_width / 2)
    y = (screen_height / 2) - (splash_height / 2)
    splash.geometry(f"{splash_width}x{splash_height}+{int(x)}+{int(y)}")

    splash.config(bg="blue")
    tk.Label(splash, text="ООО ПК Спектр", font=('Arial', 40, 'bold'), fg='white', bg="blue").pack(pady=50, expand=True)

    # Это временная метка статуса только для сплэш-экрана
    splash_status_label = tk.Label(splash, text="Подключение к базе данных...", font=('Arial', 12), fg='yellow', bg="blue")
    splash_status_label.pack(pady=10)

    def start_loading_thread_target():
        try:
            app_logger.info("Запуск потока загрузки данных приложения.")
            # Обновляем временную метку на сплэше (единственная, которая существует на этом этапе)
            root.after(0, lambda: splash_status_label.config(text="Подключение к Google Sheets...", fg='yellow'))

            # Предварительная инициализация DB для подключения и загрузки кэша
            # UI ссылки еще НЕ передаются в DB, так как основная метка статуса еще не создана
            temp_db = GoogleSheetsDatabase("Мастер Цеха Данные")
            # Для splash_status_label, чтобы видеть прогресс на сплэше (временно)
            temp_db.set_ui_references(root, splash_status_label)

            # Выполняем подключение и загрузку данных в фоновом потоке
            temp_db.connect()
            root.after(0, lambda: splash_status_label.config(text="Загрузка данных в кэш...", fg='yellow'))
            temp_db.load_all_data_to_cache()

            root.after(0, lambda: splash_status_label.config(text="Данные загружены. Запуск приложения...", fg='green'))
            app_logger.info("Данные успешно загружены в кэш, приложение готово к запуску UI.")

            # Передаем ссылку на уже подключенную DB в основной объект приложения
            app.db = temp_db

            # Запускаем дальнейшую инициализацию UI в основном потоке Tkinter
            root.after(100, app._post_splash_setup)

            # Закрываем сплэш-экран и показываем основное окно
            root.after(500, splash.destroy)
            root.after(500, root.deiconify)

        except Exception as e:
            error_message = f"Критическая ошибка при запуске: {e}"
            app_logger.critical(error_message)
            # Используем временную метку и сплэш для сообщения об ошибке
            root.after(0, lambda: messagebox.showerror("Ошибка", error_message + "\nПриложение будет закрыто.", parent=splash))
            root.after(3000, lambda: splash.destroy())
            root.after(3000, lambda: root.destroy())

    threading.Thread(target=start_loading_thread_target).start()

    splash.update_idletasks()

# --- Запуск приложения ---
if __name__ == "__main__":
    app_logger.info("Приложение 'Мастер Цеха' запускается.")
    root = tk.Tk()
    root.withdraw() # Скрываем основное окно до появления сплэш-скрина

    app = WorkshopMasterApp(root)

    show_splash_screen(root, app)

    root.mainloop()
    app_logger.info("Приложение 'Мастер Цеха' завершило работу.")