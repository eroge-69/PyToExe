import time
import socket
from datetime import datetime
from pynput import mouse, keyboard
import psycopg2
from psycopg2 import sql
import logging
import threading
import sys
import win32process
import psutil
import win32gui
import winreg
import uuid

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('afk_monitor.log'),
        logging.StreamHandler()
    ]
)

# Параметры подключения к БД
DB_PARAMS = {
    'dbname': 'awdb',
    'user': 'aw',
    'password': 'ytre45998',
    'host': '10.90.250.25',
    'port': 5432
}
# файл для кеширования
CACHE_FILE = 'failed_entries.log'
RETRY_INTERVAL = 30  # секунд между попытками отправки кэша

COMPUTER_NAME = socket.gethostname()

# Глобальные переменные
last_activity_time = datetime.now()
last_status_change = datetime.now()
current_status = "NOT-AFK"
last_active_window_title = "UNKNOWN"
last_active_app_name = "UNKNOWN"


# получение UUID
def get_machine_guid():
    try:
        reg_path = r"SOFTWARE\Microsoft\Cryptography"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            return machine_guid
    except Exception as e:
        logging.error(f"Не удалось получить MachineGuid: {e}")
        return None
# получение MAC
def get_mac_address():
    mac = uuid.getnode()
    mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    return mac_str
# уникальный ID на основе UUID+MAC
def get_pc_unique_id():
    machine_guid = get_machine_guid() or "UNKNOWN_GUID"
    mac_address = get_mac_address()
    return f"{machine_guid}_{mac_address}"

pc_id = get_pc_unique_id()

# отаравка данных из кеша и его очистка
def retry_failed_entries():
    while True:
        time.sleep(RETRY_INTERVAL)
        try:
            with open(CACHE_FILE, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            continue  # Файл не существует — пропускаем итерацию
        except Exception as e:
            logging.error(f"Ошибка при чтении кеша: {str(e)}")
            continue

        if not lines:
            continue  # Файл пустой — ничего не делаем

        success_lines = []
        fail_lines = []

        for line in lines:
            try:
                if not line.strip():
                    continue
                parts = line.strip().split('|')

                if len(parts) == 6:
                    ts_str, status, dur_str, window_title, app_name, pc_id = parts
                elif len(parts) == 5:
                    ts_str, status, dur_str, window_title, app_name = parts
                    pc_id = "UNKNOWN"
                elif len(parts) == 4:
                    ts_str, status, dur_str, window_title = parts
                    app_name = "UNKNOWN"
                    pc_id = "UNKNOWN"
                elif len(parts) == 3:
                    ts_str, status, dur_str = parts
                    window_title = "UNKNOWN"
                    app_name = "UNKNOWN"
                    pc_id = "UNKNOWN"
                else:
                    raise ValueError(f"Некорректный формат строки: {line.strip()}")

                timestamp = datetime.fromisoformat(ts_str)
                duration = float(dur_str)

                if send_to_postgres(timestamp, status, duration, window_title, app_name, pc_id):
                    success_lines.append(line)
                else:
                    fail_lines.append(line)

            except Exception as e:
                logging.error(f"Ошибка обработки кеш-записи '{line.strip()}': {str(e)}")
                fail_lines.append(line)

        # Перезаписываем кеш-файл только неудачными строками
        try:
            with open(CACHE_FILE, 'w') as f:
                f.writelines(fail_lines)
        except Exception as e:
            logging.error(f"Ошибка при записи кеша: {str(e)}")


def send_to_postgres(timestamp, status, duration, window_title, app_name, pc_id):
    """Отправка данных в PostgreSQL"""
    status_value = 0 if status == "AFK" else 1

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        insert_query = sql.SQL("""
            INSERT INTO user_activity (timestamp, status, status_value, duration_sec, host, window_title, app_name, pc_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """)

        cursor.execute(insert_query, (
            timestamp,
            status,
            status_value,
            round(duration, 1),
            COMPUTER_NAME,
            window_title,
            app_name,
            pc_id
        ))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Данные успешно записаны в PostgreSQL")
        return True

    except Exception as e:
        logging.error(f"Ошибка записи в PostgreSQL: {e}")
        save_failed_entry(timestamp, status, duration, window_title, app_name, pc_id)
        return False


def save_failed_entry(timestamp, status, duration, window_title="UNKNOWN", app_name="UNKNOWN", pc_id="UNKNOWN"):
    """Сохранение в файл при ошибке"""
    try:
        with open('failed_entries.log', 'a') as f:
            f.write(f"{timestamp.isoformat()}|{status}|{duration:.1f}|{window_title}|{app_name}|{pc_id}\n")
    except Exception as e:
        logging.error(f"Не удалось сохранить в файл: {str(e)}")

# сохраняем заголовок текущего окна
def on_activity():
    global last_activity_time, last_active_window_title, last_active_app_name
    last_activity_time = datetime.now()
    last_active_window_title, last_active_app_name = get_active_window_info()

def check_afk():
    global last_activity_time, current_status, last_status_change, last_active_window_title, last_active_app_name

    while True:
        time.sleep(1)
        now = datetime.now()
        inactive_duration = (now - last_activity_time).total_seconds()

        if inactive_duration > 300 and current_status == "NOT-AFK":
            # Вычисляем длительность текущего статуса
            real_duration = (now - last_status_change).total_seconds()

            # Отправляем данные с текущим статусом перед сменой
            if send_to_postgres(now, "NOT-AFK", real_duration, last_active_window_title, last_active_app_name, pc_id):

                # Меняем статус и время последнего изменения
                current_status = "AFK"
                last_status_change = now
                logging.info(f"{COMPUTER_NAME} | {now} | AFK | {real_duration:.1f} сек | Окно: {last_active_window_title} | Приложение: {last_active_app_name}")



        elif inactive_duration <= 300 and current_status == "AFK":
            # Вычисляем длительность текущего статуса
            real_duration = (now - last_status_change).total_seconds()
            window_title, app_name = get_active_window_info()  # Получаем и окно и приложение
            # Отправляем данные с текущим статусом перед сменой
            if send_to_postgres(now, "AFK", real_duration, window_title, app_name, pc_id):

                # Меняем статус и время последнего изменения
                current_status = "NOT-AFK"
                last_status_change = now
                logging.info(f"{COMPUTER_NAME} | {now} | NOT-AFK | {real_duration:.1f} сек | Окно: {window_title} | Приложение: {app_name}")


def get_active_window_info():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            # Нет активного окна в данный момент
            return "UNKNOWN", "UNKNOWN"

        title = win32gui.GetWindowText(hwnd) or "UNKNOWN"

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid <= 0:
            return title, "UNKNOWN"

        try:
            process = psutil.Process(pid)
            process_name = process.name() or "UNKNOWN"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_name = "UNKNOWN"

        return title, process_name

    except Exception as e:
        logging.error(f"Не удалось получить информацию об активном окне: {e}")
        return "UNKNOWN", "UNKNOWN"

def start_monitoring():
    mouse_listener = mouse.Listener(
        on_move=lambda x, y: on_activity(),
        on_click=lambda x, y, b, p: on_activity()
    )

    keyboard_listener = keyboard.Listener(
        on_press=lambda k: on_activity()
    )

    mouse_listener.start()
    keyboard_listener.start()

    logging.info(f"Мониторинг активности на '{COMPUTER_NAME}' запущен. Ctrl+C для остановки.")

    # Запуск retry_failed_entries в отдельном фоновом потоке (демоне),
    retry_thread = threading.Thread(target=retry_failed_entries, daemon=True)
    retry_thread.start()

    try:
        check_afk()
    except KeyboardInterrupt:
        logging.info("Прерывание пользователем.")
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}")
    finally:
        mouse_listener.stop()
        keyboard_listener.stop()
        logging.info("Мониторинг остановлен.")


if __name__ == "__main__":
    start_monitoring()
