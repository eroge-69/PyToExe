import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
import hashlib
import os
import threading
import time
from pathlib import Path
import ctypes
from ctypes import wintypes
import requests
import json
from datetime import datetime

# === Firebase Настройки ===
FIREBASE_API_KEY = "AIzaSyBqTdueiJcAtaGulmveTiF6REHqCdjtbEY"  # 🔥 ЗАМЕНИ НА СВОЙ
FIREBASE_PROJECT_ID = "cybershield-av-77194"  # 🔥 ЗАМЕНИ НА СВОЙ
DATABASE_URL = f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com"

DATABASE_PATH = Path(__file__).parent / "database.txt"
SUSPICIOUS_DIRS = [str(Path.home() / "Downloads"), str(Path.home() / "Desktop"), "C:\\Windows\\Temp"]
QUICK_SCAN_EXTENSIONS = {'.exe', '.bat', '.py', '.vbs'}


class FirebaseAuth:
    def __init__(self):
        self.api_key = FIREBASE_API_KEY
        self.project_id = FIREBASE_PROJECT_ID
        self.db_url = DATABASE_URL

    def register_user(self, login, password, secret_question, secret_answer):
        try:
            response = requests.get(f"{self.db_url}/users/{login}.json")
            if response.json() is not None:
                return False, "Пользователь уже существует"

            user_data = {
                "password": password,
                "secret_question": secret_question,
                "secret_answer": secret_answer,
                "registered_at": int(time.time()),
                "scan_count": 0,
                "last_scan": 0
            }
            response = requests.put(f"{self.db_url}/users/{login}.json", data=json.dumps(user_data))
            if response.status_code == 200:
                return True, "Регистрация успешна"
            else:
                return False, f"Ошибка сервера: {response.text}"
        except Exception as e:
            return False, f"Ошибка подключения: {str(e)}"

    def login_user(self, login, password):
        try:
            response = requests.get(f"{self.db_url}/users/{login}.json")
            data = response.json()
            if data is None:
                return False, "Пользователь не найден", None
            if data.get("password") == password:
                return True, "Вход выполнен", data
            else:
                return False, "Неверный пароль", None
        except Exception as e:
            return False, f"Ошибка подключения: {str(e)}", None

    def recover_password(self, login, secret_answer):
        try:
            response = requests.get(f"{self.db_url}/users/{login}.json")
            data = response.json()
            if data is None:
                return False, "Пользователь не найден", None
            if data.get("secret_answer") == secret_answer:
                return True, "Пароль: " + data.get("password"), data
            else:
                return False, "Неверный ответ на секретный вопрос", None
        except Exception as e:
            return False, f"Ошибка: {str(e)}", None

    def update_user_data(self, login, data):
        try:
            response = requests.put(f"{self.db_url}/users/{login}.json", data=json.dumps(data))
            return response.status_code == 200
        except:
            return False


class AntivirusApp:
    def __init__(self, root, username, user_data, firebase):
        self.root = root
        self.username = username
        self.user_data = user_data
        self.firebase = firebase
        self.root.title(f"🛡️ CyberShield — {username}")
        self.root.geometry("950x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")
        self.root.bind("<F11>", lambda event: "break")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6, background="#3b3b5a", foreground="white")
        style.map("TButton", background=[("active", "#5a5a80")])

        # Меню пользователя
        menu_frame = tk.Frame(root, bg="#1e1e2e")
        menu_frame.pack(fill=tk.X, pady=5)

        self.user_label = tk.Label(menu_frame, text=f"👤 Пользователь: {username}", font=("Segoe UI", 12),
                                   bg="#1e1e2e", fg="#00ff9d")
        self.user_label.pack(side=tk.LEFT, padx=20)

        self.btn_profile = ttk.Button(menu_frame, text="🎁 Профиль", command=self.show_profile_window, width=12)
        self.btn_profile.pack(side=tk.RIGHT, padx=5)

        self.btn_logout = ttk.Button(menu_frame, text="🎭 Сменить пользователя", command=self.logout, width=20)
        self.btn_logout.pack(side=tk.RIGHT, padx=5)

        # Заголовок
        title_frame = tk.Frame(root, bg="#1e1e2e")
        title_frame.pack(fill=tk.X, pady=10)
        title_label = tk.Label(title_frame, text="🛡️ CyberShield Антивирус", font=("Segoe UI", 22, "bold"),
                               bg="#1e1e2e", fg="#00ff9d")
        title_label.pack(pady=5)

        # Кнопки
        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=10)

        self.btn_system = ttk.Button(button_frame, text="О системе", command=self.show_system_info, width=22)
        self.btn_system.grid(row=0, column=0, padx=5, pady=5)

        self.btn_full_scan = ttk.Button(button_frame, text="Полное сканирование", command=self.start_full_scan, width=22)
        self.btn_full_scan.grid(row=0, column=1, padx=5, pady=5)

        self.btn_quick_scan = ttk.Button(button_frame, text="Быстрое сканирование", command=self.start_quick_scan, width=22)
        self.btn_quick_scan.grid(row=0, column=2, padx=5, pady=5)

        self.realtime_active = False
        self.realtime_thread = None
        self.btn_realtime = ttk.Button(button_frame, text="🛡️ Включить защиту", command=self.toggle_realtime_protection, width=25)
        self.btn_realtime.grid(row=0, column=3, padx=5, pady=5)

        # Прогресс-бар
        progress_frame = tk.Frame(root, bg="#1e1e2e")
        progress_frame.pack(fill=tk.X, padx=30, pady=5)
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=890, mode="determinate")
        self.progress.pack(fill=tk.X)

        # Лог
        log_label = tk.Label(root, text="📝 Лог сканирования:", font=("Segoe UI", 13, "bold"), bg="#1e1e2e", fg="white")
        log_label.pack(anchor="w", padx=30, pady=(10, 5))

        log_frame = tk.Frame(root, bg="#1e1e2e")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, bg="#2e2e3e", fg="#00ff9d",
                                                  font=("Consolas", 10), insertbackground="#00ff9d",
                                                  relief="flat", borderwidth=0)
        self.log_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.last_infected_file = None
        self.scanned_files_cache = set()
        self.virus_hashes = self.load_database()

    def load_database(self):
        if not DATABASE_PATH.exists():
            with open(DATABASE_PATH, "w", encoding="utf-8") as f:
                pass
            self.log("✅ Создан новый файл database.txt")
            return set()

        try:
            with open(DATABASE_PATH, "r", encoding="utf-8") as f:
                hashes = {line.strip().lower() for line in f if line.strip()}
            self.log(f"✅ Загружено {len(hashes)} сигнатур вирусов.")
            return hashes
        except Exception as e:
            self.log(f"❌ Ошибка загрузки базы: {e}")
            return set()

    def log(self, message):
        """Выводит сообщение в лог-область приложения"""
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    # ============ WinAPI СИСТЕМНАЯ ИНФОРМАЦИЯ ============

    def get_cpu_usage_ctypes(self):
        try:
            class FILETIME(ctypes.Structure):
                _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]
            idle_time = FILETIME(); kernel_time = FILETIME(); user_time = FILETIME()
            success = ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle_time), ctypes.byref(kernel_time), ctypes.byref(user_time))
            if not success: return 0
            def ft2u64(ft): return (ft.dwHighDateTime << 32) + ft.dwLowDateTime
            idle, kernel, user = ft2u64(idle_time), ft2u64(kernel_time), ft2u64(user_time)
            total = kernel + user
            return int(100.0 * (total - idle) / total) if total > 0 else 0
        except: return 0

    def get_ram_usage_ctypes(self):
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [('dwLength', wintypes.DWORD), ('dwMemoryLoad', wintypes.DWORD),
                            ('ullTotalPhys', wintypes.c_ulonglong), ('ullAvailPhys', wintypes.c_ulonglong),
                            ('ullTotalPageFile', wintypes.c_ulonglong), ('ullAvailPageFile', wintypes.c_ulonglong),
                            ('ullTotalVirtual', wintypes.c_ulonglong), ('ullAvailVirtual', wintypes.c_ulonglong),
                            ('ullAvailExtendedVirtual', wintypes.c_ulonglong)]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.dwMemoryLoad
        except: return 0

    def get_disk_usage_ctypes(self):
        try:
            free_bytes = wintypes.ULARGE_INTEGER()
            total_bytes = wintypes.ULARGE_INTEGER()
            total_free_bytes = wintypes.ULARGE_INTEGER()
            drive = "C:\\"
            success = ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(drive),
                ctypes.byref(free_bytes), ctypes.byref(total_bytes), ctypes.byref(total_free_bytes))
            if not success: return 0
            free, total = free_bytes.value, total_bytes.value
            return int((total - free) / total * 100) if total > 0 else 0
        except: return 0

    def get_gpu_info(self):
        return "NVIDIA / AMD / Intel (поддержка DirectX)"

    def show_system_info(self):
        self.log("🔍 Получение информации о системе через WinAPI...")
        info = f"""
📊 СИСТЕМА:
   🖥️  ЦП: {self.get_cpu_usage_ctypes()}%
   🧠  ОЗУ: {self.get_ram_usage_ctypes()}%
   💾  Диск C:: {self.get_disk_usage_ctypes()}%
   🎮  Видеокарта: {self.get_gpu_info()}
        """
        self.log(info)

    # ============ СКАНИРОВАНИЕ ФАЙЛОВ ============

    def calculate_file_hash(self, filepath):
        try:
            sha1 = hashlib.sha1()
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha1.update(chunk)
            return sha1.hexdigest().lower()
        except Exception as e:
            self.log(f"⚠️ Ошибка чтения {filepath}: {e}")
            return None

    def scan_file(self, filepath):
        if filepath in self.scanned_files_cache: return
        file_hash = self.calculate_file_hash(filepath)
        if not file_hash: return
        if file_hash in self.virus_hashes:
            msg = f"🔴 ВИРУС ОБНАРУЖЕН: {filepath}"
            self.log(msg)
            self.last_infected_file = filepath
            self.add_delete_button(filepath)
        else:
            self.log(f"✅ Чисто: {filepath}")
        self.scanned_files_cache.add(filepath)

    def add_delete_button(self, filepath):
        if hasattr(self, 'delete_btn') and self.delete_btn.winfo_exists():
            self.delete_btn.destroy()
        self.delete_btn = ttk.Button(self.root, text=f"🗑️ Удалить вирус: {Path(filepath).name}",
                                     command=lambda: self.delete_infected_file(filepath))
        self.delete_btn.pack(pady=5)

    def delete_infected_file(self, filepath):
        try:
            os.remove(filepath)
            self.log(f"✅ Файл удалён: {filepath}")
            if hasattr(self, 'delete_btn'): self.delete_btn.destroy()
            self.last_infected_file = None
            if filepath in self.scanned_files_cache: self.scanned_files_cache.remove(filepath)
        except Exception as e:
            self.log(f"❌ Не удалось удалить файл: {e}")

    def scan_directory(self, directory, extensions=None):
        if not os.path.exists(directory):
            self.log(f"⚠️ Папка не найдена: {directory}")
            return
        files, skipped = [], 0
        try:
            for root, dirs, filenames in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in ("$Recycle.Bin", "System Volume Information", "Recovery")]
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    if extensions and Path(filepath).suffix.lower() not in extensions: continue
                    if not os.access(filepath, os.R_OK): skipped += 1; continue
                    files.append(filepath)
        except Exception as e:
            self.log(f"❌ Ошибка при обходе папки {directory}: {e}")
        total = len(files)
        self.progress["maximum"] = total or 1
        scanned = 0  # ← ИСПРАВЛЕНО: БЫЛО scan_out — теперь scanned
        for i, filepath in enumerate(files, 1):
            try:
                self.scan_file(filepath)
                scanned += 1
            except Exception as e:
                self.log(f"⚠️ Ошибка сканирования файла {filepath}: {e}")
            self.progress["value"] = i
            self.root.update_idletasks()
        self.log(f"✅ Сканирование завершено. Проверено файлов: {scanned}")

        # Обновляем статистику пользователя
        self.user_data["scan_count"] += 1
        self.user_data["last_scan"] = int(time.time())
        self.firebase.update_user_data(self.username, self.user_data)

        if skipped > 0: self.log(f"⚠️ Пропущено файлов (нет доступа): {skipped}")

    def start_full_scan(self):
        self.log_area.delete(1.0, tk.END)
        self.log("🚀 Запуск ПОЛНОГО сканирования диска C:\\")
        threading.Thread(target=self._full_scan_worker, daemon=True).start()

    def _full_scan_worker(self):
        try:
            self.scan_directory("C:\\", extensions=None)
        except Exception as e:
            self.log(f"❌ Ошибка при сканировании: {e}")
        finally:
            self.progress["value"] = 0

    def start_quick_scan(self):
        self.log_area.delete(1.0, tk.END)
        self.log("⚡ Запуск БЫСТРОГО сканирования подозрительных папок...")
        threading.Thread(target=self._quick_scan_worker, daemon=True).start()

    def _quick_scan_worker(self):
        try:
            for folder in SUSPICIOUS_DIRS:
                if os.path.exists(folder):
                    self.log(f"📂 Сканирование: {folder}")
                    self.scan_directory(folder, extensions=QUICK_SCAN_EXTENSIONS)
                else:
                    self.log(f"⚠️ Папка не существует: {folder}")
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
        finally:
            self.progress["value"] = 0

    # ============ ЗАЩИТА В РЕАЛЬНОМ ВРЕМЕНИ ============

    def toggle_realtime_protection(self):
        if self.realtime_active:
            self.stop_realtime_protection()
        else:
            self.start_realtime_protection()

    def start_realtime_protection(self):
        self.realtime_active = True
        self.btn_realtime.config(text="🛑 Выключить защиту")
        self.log("✅ Защита в реальном времени ВКЛЮЧЕНА (проверка каждые 5 секунд)")
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def _monitor_loop(self):
        while self.realtime_active:
            for folder in SUSPICIOUS_DIRS:
                if not os.path.exists(folder): continue
                try:
                    for filename in os.listdir(folder):
                        filepath = os.path.join(folder, filename)
                        if not os.path.isfile(filepath): continue
                        if Path(filepath).suffix.lower() not in QUICK_SCAN_EXTENSIONS: continue
                        if not os.access(filepath, os.R_OK): continue
                        if filepath not in self.scanned_files_cache:
                            self.log(f"🔍 [РЕАЛЬНОЕ ВРЕМЯ] Проверка нового файла: {filepath}")
                            self.scan_file(filepath)
                except Exception as e:
                    self.log(f"⚠️ Ошибка мониторинга папки {folder}: {e}")
            time.sleep(5)

    def stop_realtime_protection(self):
        self.realtime_active = False
        self.btn_realtime.config(text="🛡️ Включить защиту")
        self.log("⏹️ Защита в реальном времени ВЫКЛЮЧЕНА")

    # ============ ПРОФИЛЬ В ОТДЕЛЬНОМ ОКНЕ ============

    def show_profile_window(self):
        profile_win = tk.Toplevel(self.root)
        profile_win.title("🎁 Профиль пользователя")
        profile_win.geometry("500x400")
        profile_win.resizable(False, False)
        profile_win.configure(bg="#1e1e2e")
        profile_win.grab_set()  # Модальное окно

        tk.Label(profile_win, text=f"Профиль: {self.username}", font=("Segoe UI", 18, "bold"),
                 bg="#1e1e2e", fg="#00ff9d").pack(pady=20)

        frame = tk.Frame(profile_win, bg="#2e2e3e", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        registered_at = datetime.fromtimestamp(self.user_data.get("registered_at", 0)).strftime("%Y-%m-%d %H:%M")
        scan_count = self.user_data.get("scan_count", 0)
        last_scan = self.user_data.get("last_scan", 0)
        last_scan_str = datetime.fromtimestamp(last_scan).strftime("%Y-%m-%d %H:%M") if last_scan else "Никогда"

        info = f"""
📅 Дата регистрации:   {registered_at}
🔍 Всего сканирований: {scan_count}
🕒 Последнее:          {last_scan_str}

🔐 Секретный вопрос:
   {self.user_data.get('secret_question', 'Не задан')}
        """

        tk.Label(frame, text=info, font=("Consolas", 11), bg="#2e2e3e", fg="white", justify=tk.LEFT).pack(anchor="w")

        ttk.Button(profile_win, text="Закрыть", command=profile_win.destroy, width=20).pack(pady=20)

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        login_app = LoginWindow(root)
        root.mainloop()


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ CyberShield — Вход")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.firebase = FirebaseAuth()

        # Заголовок
        title_label = tk.Label(root, text="🔐 Добро пожаловать!", font=("Segoe UI", 20, "bold"),
                               bg="#1e1e2e", fg="#00ff9d")
        title_label.pack(pady=20)

        # Логин
        tk.Label(root, text="Логин:", bg="#1e1e2e", fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.login_entry = tk.Entry(root, font=("Segoe UI", 12), width=30)
        self.login_entry.pack(pady=5)

        # Пароль
        tk.Label(root, text="Пароль:", bg="#1e1e2e", fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.password_entry = tk.Entry(root, font=("Segoe UI", 12), width=30, show="*")
        self.password_entry.pack(pady=5)

        # Метка для ошибок
        self.error_label = tk.Label(root, text="", bg="#1e1e2e", fg="red", font=("Segoe UI", 11))
        self.error_label.pack(pady=5)

        # Кнопки
        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=20)

        self.btn_login = ttk.Button(button_frame, text="Войти", command=self.login)
        self.btn_login.grid(row=0, column=0, padx=10, pady=5)

        self.btn_register = ttk.Button(button_frame, text="Зарегистрироваться", command=self.open_register_window)
        self.btn_register.grid(row=0, column=1, padx=10, pady=5)

        self.btn_recover = ttk.Button(root, text="🔄 Забыли пароль?", command=self.recover_password)
        self.btn_recover.pack(pady=10)

    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            self.error_label.config(text="❌ Заполните все поля")
            return

        success, message, user_data = self.firebase.login_user(login, password)
        self.error_label.config(text=message, fg="green" if success else "red")

        if success:
            self.root.destroy()
            self.open_main_app(login, user_data)

    def open_register_window(self):
        reg_window = tk.Toplevel(self.root)
        reg_window.title("📝 Регистрация")
        reg_window.geometry("400x500")
        reg_window.configure(bg="#1e1e2e")
        reg_window.resizable(False, False)

        tk.Label(reg_window, text="Логин:", bg="#1e1e2e", fg="white", font=("Segoe UI", 12)).pack(pady=(20, 5))
        login_entry = tk.Entry(reg_window, font=("Segoe UI", 12), width=25)
        login_entry.pack()

        tk.Label(reg_window, text="Пароль:", bg="#1e1e2e", fg="white", font=("Segoe UI", 12)).pack(pady=(15, 5))
        password_entry = tk.Entry(reg_window, font=("Segoe UI", 12), width=25, show="*")
        password_entry.pack()

        tk.Label(reg_window, text="Секретный вопрос:", bg="#1e1e2e", fg="white", font=("Segoe UI", 12)).pack(pady=(15, 5))
        secret_question_entry = tk.Entry(reg_window, font=("Segoe UI", 12), width=30)
        secret_question_entry.pack()

        tk.Label(reg_window, text="Ответ:", bg="#1e1e2e", fg="white", font=("Segoe UI", 12)).pack(pady=(15, 5))
        secret_answer_entry = tk.Entry(reg_window, font=("Segoe UI", 12), width=30)
        secret_answer_entry.pack()

        # Метка ошибок
        error_label_reg = tk.Label(reg_window, text="", bg="#1e1e2e", fg="red", font=("Segoe UI", 11))
        error_label_reg.pack(pady=10)

        def register():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            question = secret_question_entry.get().strip()
            answer = secret_answer_entry.get().strip()

            if not all([login, password, question, answer]):
                error_label_reg.config(text="❌ Заполните все поля")
                return

            success, message = self.firebase.register_user(login, password, question, answer)
            error_label_reg.config(text=message, fg="green" if success else "red")

            if success:
                reg_window.destroy()

        ttk.Button(reg_window, text="✅ Зарегистрироваться", command=register).pack(pady=30)

    def recover_password(self):
        login = simpledialog.askstring("Восстановление пароля", "Введите ваш логин:")
        if not login: return

        try:
            response = requests.get(f"{DATABASE_URL}/users/{login}.json")
            data = response.json()
            if data is None:
                self.error_label.config(text="❌ Пользователь не найден", fg="red")
                return

            question = data.get("secret_question", "Секретный вопрос не задан")
            answer = simpledialog.askstring("Восстановление пароля", f"Вопрос: {question}\nВведите ответ:")
            if not answer: return

            success, message, _ = self.firebase.recover_password(login, answer)
            self.error_label.config(text=message, fg="green" if success else "red")

        except Exception as e:
            self.error_label.config(text=f"❌ Ошибка: {e}", fg="red")

    def open_main_app(self, username, user_data):
        root = tk.Tk()
        app = AntivirusApp(root, username, user_data, self.firebase)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()