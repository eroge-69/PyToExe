import sys
import os
import requests
import subprocess
import time
import socket
import threading
import pystray
import ctypes
import tkinter as tk
from tkinter import messagebox, font
from queue import Queue, Empty
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image, ImageDraw

# Функция для корректного определения путей при упаковке в EXE
def resource_path(relative_path):
    """Получает правильный путь к ресурсам для PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # Временная папка PyInstaller
    else:
        base_path = os.path.abspath(".")  # Обычный путь при разработке
    return os.path.join(base_path, relative_path)

# Конфигурационные параметры
SUBNET = ".21"
CHECK_URL_PORT = ":8000/hw_proxy/status"
CHECK_INTERVAL = 10 
ERROR_RETRY_DELAY = 20 
UNI_LOGIN = "uni"
UNI_PASSWORD = "unI2O3"
SERVICE_CMD = "sudo service unibox restart"
HTML_SAVE_FOLDER = "status_pages"
FILE_DELAY_DELETE = 5
LOG_FILE = "monitor_log.txt"
LOG_CLEAN_INTERVAL = 120
MAX_LOG_SIZE = 1024 * 1024
REQUEST_TIMEOUT = 10
PORT_CHECK_TIMEOUT = 5
ERROR_TITLE = "ОШИБКА ПОДКЛЮЧЕНИЯ"
ERROR_MESSAGE = """Ошибка Odoo, невозможно выдать чек
Коллеги, сейчас провести продажу не получится, сначала нужно перезапустить микроПК
МикроПк обычно находится под ресепшеном и выглядит как коробочка размером с ладонь, ОБЯЗАТЕЛЬНО имеет два провода сзади и один сбоку.
Нужно вытащить и вставить провод сбоку, после чего подождать 1-5 минут, если значок в odoo стал зелёным - можно работать дальше.
Кнопка "Показать пример" откроет фотографию с подробной инструкцией
Если у вас что-то не получается/не знаете где микроПК/Не понимаете что делать - оставьте заявку в IT отдел"""
PRIMER_IMAGE = resource_path("primer.png")  # Используем функцию для определения пути

PUTTY_PATHS = [
    os.path.join(os.environ["PROGRAMFILES"], "PuTTY", "plink.exe"),
    os.path.join(os.environ["PROGRAMFILES(X86)"], "PuTTY", "plink.exe"),
    "plink.exe",
]

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def hide_console():
    """Скрываем консоль"""
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, 0)

def play_sound():
    """Воспроизведение звукового сигнала"""
    if sys.platform == 'win32':
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except:
            pass

class ErrorWindow:
    def __init__(self):
        self.root = None
        self.queue = Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.last_status = None
    
    def _run(self):
        """Основной цикл обработки окон"""
        while True:
            try:
                action = self.queue.get(timeout=0.1)
                if action == "show":
                    self._show_window()
                elif action == "close":
                    self._close_window()
            except Empty:
                if self.root and self.root.winfo_exists():
                    self.root.update()
    
    def _show_window(self):
        """Показать окно ошибки"""
        if self.root and self.root.winfo_exists():
            self.root.destroy()
        
        play_sound()
        
        self.root = tk.Tk()
        self.root.title(ERROR_TITLE)
        self.root.configure(bg='#2c3e50')
        self.root.attributes('-topmost', True)
        
        border_frame = tk.Frame(self.root, bg='#e74c3c', padx=3, pady=3)
        border_frame.pack(padx=10, pady=10)
        
        content_frame = tk.Frame(border_frame, bg='#34495e')
        content_frame.pack(padx=2, pady=2)
        
        icon_label = tk.Label(
            content_frame, 
            text="⚠", 
            font=('Arial', 24),
            bg='#34495e', 
            fg='#e74c3c'
        )
        icon_label.pack(pady=(10, 0))
        
        error_font = font.Font(family='Arial', size=11, weight='bold')
        label = tk.Label(
            content_frame, 
            text=ERROR_MESSAGE, 
            font=error_font,
            bg='#34495e', 
            fg='#ecf0f1',
            padx=20,
            pady=10,
            justify=tk.LEFT
        )
        label.pack()
        
        buttons_frame = tk.Frame(content_frame, bg='#34495e')
        buttons_frame.pack(pady=(0, 15))
        
        button_ok = tk.Button(
            buttons_frame, 
            text="ПОНЯТНО", 
            command=self._on_close,
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            font=font.Font(family='Arial', size=10, weight='bold'),
            width=15,
            height=1,
            bd=0,
            relief=tk.FLAT
        )
        button_ok.pack(side=tk.LEFT, padx=5)
        button_ok.bind("<Enter>", lambda e: button_ok.config(bg='#c0392b'))
        button_ok.bind("<Leave>", lambda e: button_ok.config(bg='#e74c3c'))
        
        if os.path.exists(PRIMER_IMAGE):
            button_primer = tk.Button(
                buttons_frame, 
                text="ОТКРЫТЬ ПРИМЕР", 
                command=self._open_primer,
                bg='#3498db',
                fg='white',
                activebackground='#2980b9',
                activeforeground='white',
                font=font.Font(family='Arial', size=10, weight='bold'),
                width=15,
                height=1,
                bd=0,
                relief=tk.FLAT
            )
            button_primer.pack(side=tk.LEFT, padx=5)
            button_primer.bind("<Enter>", lambda e: button_primer.config(bg='#2980b9'))
            button_primer.bind("<Leave>", lambda e: button_primer.config(bg='#3498db'))
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        self.root.attributes('-alpha', 0)
        for i in range(0, 101, 10):
            self.root.attributes('-alpha', i/100)
            self.root.update()
            time.sleep(0.02)
    
    def _open_primer(self):
        """Открыть файл примера"""
        try:
            if os.path.exists(PRIMER_IMAGE):
                os.startfile(PRIMER_IMAGE)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
    
    def _close_window(self):
        """Закрыть окно ошибки"""
        if self.root and self.root.winfo_exists():
            self.root.destroy()
            self.root = None
    
    def _on_close(self):
        """Обработчик закрытия окна"""
        self._close_window()
    
    def show(self):
        """Запрос на показ окна"""
        self.queue.put("show")
    
    def close(self):
        """Запрос на закрытие окна"""
        self.queue.put("close")

class MonitorApp:
    def __init__(self):
        self.running = True
        self.last_status = None
        self.setup_environment()
        self.plink_path = None
        self.ip = None
        self.last_log_clean = time.time()
        self.error_window = ErrorWindow()
        self.init_status_history()
        self.tray_icon = self.create_tray_icon()
        
    def setup_environment(self):
        """Настройка окружения"""
        if not os.path.exists(HTML_SAVE_FOLDER):
            os.makedirs(HTML_SAVE_FOLDER)
        open(LOG_FILE, 'a').close()
    
    def init_status_history(self):
        """Инициализация истории статусов"""
        self.status_history = []
        self.max_history = 100
    
    def add_status_record(self, status, timestamp=None):
        """Добавление записи в историю"""
        if timestamp is None:
            timestamp = time.time()
        self.status_history.append((timestamp, status))
        if len(self.status_history) > self.max_history:
            self.status_history.pop(0)
    
    def clean_log_file(self):
        """Очистка лог-файла"""
        try:
            current_time = time.time()
            
            if current_time - self.last_log_clean >= LOG_CLEAN_INTERVAL:
                with open(LOG_FILE, 'w'):
                    pass
                self.last_log_clean = current_time
                return
            
            if os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
                with open(LOG_FILE, 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    f.seek(0)
                    f.truncate()
                    f.writelines(lines[-100:])
                
        except Exception as e:
            print(f"Ошибка очистки лога: {e}")
    
    def log_message(self, message):
        """Запись сообщения в лог"""
        self.clean_log_file()
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    
    def create_tray_icon(self):
        """Создание иконки в системном трее"""
        image = self.create_status_icon('init')
        
        menu = pystray.Menu(
            pystray.MenuItem(
                lambda text: f"Статус: {'ONLINE' if self.last_status else 'OFFLINE'}",
                None,
                enabled=False
            ),
            pystray.MenuItem('Проверить сейчас', self.force_check),
            pystray.MenuItem('Открыть лог', self.open_log),
            pystray.MenuItem('Выход', self.exit_app)
        )
        
        return pystray.Icon("micropc_monitor", image, "МикроПК Монитор", menu)
    
    def create_status_icon(self, status):
        """Создание иконки статуса"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        for i in range(size):
            gray = int(255 * i / size)
            dc.line((0, i, size, i), fill=(gray, gray, gray, 255))
        
        if status == 'ok':
            check_color = (0, 255, 0, 255)
            dc.line((16, 32, 30, 46), fill=check_color, width=6)
            dc.line((30, 46, 48, 18), fill=check_color, width=6)
        else:
            cross_color = (255, 0, 0, 255)
            dc.line((16, 16, 48, 48), fill=cross_color, width=6)
            dc.line((48, 16, 16, 48), fill=cross_color, width=6)
        
        return image
    
    def update_tray_icon(self, status):
        """Обновление иконки в трее"""
        image = self.create_status_icon(status)
        self.tray_icon.icon = image
        self.last_status = status == 'ok'
    
    def open_log(self, icon=None, item=None):
        """Открытие файла лога"""
        if os.path.exists(LOG_FILE):
            os.startfile(LOG_FILE)
    
    def force_check(self, icon=None, item=None):
        """Принудительная проверка статуса"""
        self.log_message("Запущена принудительная проверка")
        threading.Thread(target=self.check_micro_pc, daemon=True).start()
    
    def exit_app(self, icon=None, item=None):
        """Завершение работы приложения"""
        self.running = False
        self.error_window.close()
        self.tray_icon.stop()
        os._exit(0)
    
    def find_plink(self):
        """Поиск plink.exe"""
        for path in PUTTY_PATHS:
            if os.path.exists(path):
                self.log_message(f"Найден plink.exe: {path}")
                return path
        self.log_message("Ошибка: plink.exe не найден")
        self.error_window.show()
        return None
        
    def find_micro_pc_ip(self):
        """Поиск IP микропк"""
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            network_prefix = ".".join(local_ip.split(".")[:3])
            
            for i in range(1, 255):
                ip = f"{network_prefix}.{i}"
                if ip.endswith(SUBNET):
                    self.log_message(f"Найден IP микропк: {ip}")
                    return ip
        except Exception as e:
            self.log_message(f"Ошибка поиска IP: {e}")
        return None
    
    def is_port_open(self, ip, port=8000, timeout=PORT_CHECK_TIMEOUT):
        """Проверка доступности порта"""
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError) as e:
            self.log_message(f"Порт {port} недоступен: {type(e).__name__}")
            return False
        except Exception as e:
            self.log_message(f"Ошибка проверки порта: {type(e).__name__}: {e}")
            return False
    
    def delayed_file_delete(self, filepath):
        """Удаление файла с задержкой"""
        time.sleep(FILE_DELAY_DELETE)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                self.log_message(f"Удален файл: {os.path.basename(filepath)}")
        except Exception as e:
            self.log_message(f"Ошибка удаления файла: {e}")
    
    def save_html(self, ip, content):
        """Сохранение HTML файла"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"status_{ip}_{timestamp}.html"
        filepath = os.path.join(HTML_SAVE_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        size_kb = os.path.getsize(filepath) / 1024
        self.log_message(f"Сохранен файл {filename} ({size_kb:.2f} KB)")
        
        threading.Thread(
            target=self.delayed_file_delete,
            args=(filepath,),
            daemon=True
        ).start()
    
    def check_status(self, ip):
        """Проверка статуса подключения с обработкой таймаутов"""
        # Сначала проверяем доступность порта
        if not self.is_port_open(ip):
            return False

        url = f"https://{ip}{CHECK_URL_PORT}"
        try:
            response = requests.get(url, verify=False, timeout=REQUEST_TIMEOUT)
            self.save_html(ip, response.text)
            
            if response.status_code != 200:
                self.log_message(f"HTTP ошибка: {response.status_code}")
                return False
                
            if "pwi : connected" not in response.text:
                self.log_message("Строка статуса не найдена в ответе")
                return False
                
            error_indicators = [
                "error",
                "exception",
                "not found",
                "unavailable",
                "502 Bad Gateway",
                "503 Service Unavailable"
            ]
            
            if any(indicator.lower() in response.text.lower() for indicator in error_indicators):
                self.log_message("Обнаружен индикатор ошибки в ответе")
                return False
                
            return True
            
        except requests.exceptions.Timeout:
            self.log_message(f"Таймаут при подключении к {url}")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_message(f"Ошибка соединения: {str(e)}")
            return False
        except requests.exceptions.RequestException as e:
            self.log_message(f"Ошибка запроса: {type(e).__name__}: {str(e)}")
            return False
        except Exception as e:
            self.log_message(f"Неожиданная ошибка: {type(e).__name__}: {str(e)}")
            return False
    
    def restart_service(self, plink_path, ip):
        """Перезапуск сервиса"""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                [plink_path, "-ssh", f"{UNI_LOGIN}@{ip}", "-pw", UNI_PASSWORD, "-batch", SERVICE_CMD],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=20,
                startupinfo=startupinfo
            )
            
            if result.returncode == 0:
                self.log_message("Сервис успешно перезапущен")
                return True
            else:
                self.log_message(f"Ошибка выполнения plink (код {result.returncode})")
                if result.stderr:
                    self.log_message(f"Ошибка plink: {result.stderr.decode('utf-8', errors='ignore')}")
        except subprocess.TimeoutExpired:
            self.log_message("Таймаут при выполнении plink")
        except Exception as e:
            self.log_message(f"Ошибка выполнения plink: {str(e)}")
        
        self.error_window.show()
        return False
    
    def check_micro_pc(self):
        """Проверка состояния микропк с подтверждением ошибки"""
        self.update_tray_icon('checking')
        
        if not self.plink_path:
            self.plink_path = self.find_plink()
            if not self.plink_path:
                time.sleep(ERROR_RETRY_DELAY)
                return
                
        if not self.ip:
            self.ip = self.find_micro_pc_ip()
            if not self.ip:
                time.sleep(ERROR_RETRY_DELAY)
                return
        
        # Двойная проверка с интервалом
        status_ok = self.check_status(self.ip)
        if not status_ok:
            time.sleep(5)
            status_ok = self.check_status(self.ip)
        
        self.add_status_record('ok' if status_ok else 'error')
        
        if status_ok:
            self.update_tray_icon('ok')
            self.error_window.close()
        else:
            self.update_tray_icon('error')
            self.log_message("Подтверждена проблема с подключением")
            if not self.restart_service(self.plink_path, self.ip):
                time.sleep(ERROR_RETRY_DELAY)
                if not self.check_status(self.ip):
                    self.error_window.show()
            else:
                time.sleep(10)
                if self.check_status(self.ip):
                    self.error_window.close()
    
    def run(self):
        """Основной цикл программы"""
        self.log_message("Программа запущена")
        
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        self.tray_icon.run()

    def monitor_loop(self):
        """Цикл мониторинга"""
        while self.running:
            self.check_micro_pc()
            time.sleep(CHECK_INTERVAL)

def main():
    hide_console()
    app = MonitorApp()
    app.run()

if __name__ == "__main__":
    if sys.executable.endswith("pythonw.exe"):
        main()
    else:
        import subprocess
        subprocess.Popen([sys.executable.replace("python.exe", "pythonw.exe"), sys.argv[0]])
        sys.exit()