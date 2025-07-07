import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import os
import ctypes
import threading
import queue
import sys

# Проверка прав администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
    sys.exit()

# Основные настройки
DOMAIN_ACCOUNT = "avenir-s.ru\\cosa"
PROGRAMS = [
    {"name": "1C Предприятие", "path": r"\\192.168.100.115\d\00_Дистрибутивы\01-1С дистрибутив\windows64full_8_3_25_1374\setup.exe", "args": []},
    {"name": "WinRAR", "path": r"\\192.168.100.115\d\01_Установочные для ПК\winrar-x64-624ru.exe", "args": ["/S"]},
    {"name": "TightVNC", "path": r"\\192.168.100.115\d\01_Установочные для ПК\tightvnc-2.8.81-gpl-setup-64bit.msi", "args": ["/qn"]},
    {"name": "AnyDesk", "path": r"\\192.168.100.115\d\01_Установочные для ПК\anydesk-6-1-4.exe", "args": ["--install", "/silent"]},
    {"name": "Microsoft Teams", "path": r"\\192.168.100.115\d\01_Установочные для ПК\MSTeamsSetup.exe", "args": ["-s"]},
    {"name": "Yandex Browser", "path": r"\\192.168.100.115\d\01_Установочные для ПК\Yandex.exe", "args": ["--silent"]}
]

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Установщик ПО")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Переменные
        self.password = tk.StringVar()
        self.selected_programs = []
        self.custom_programs = []
        self.log_queue = queue.Queue()
        
        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм аутентификации
        auth_frame = ttk.LabelFrame(main_frame, text="Аутентификация", padding=10)
        auth_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(auth_frame, text=f"Учетная запись: {DOMAIN_ACCOUNT}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(auth_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W)
        password_entry = ttk.Entry(auth_frame, textvariable=self.password, show="*", width=30)
        password_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Фрейм выбора ПО
        programs_frame = ttk.LabelFrame(main_frame, text="Программы для установки", padding=10)
        programs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview для программ
        self.tree = ttk.Treeview(programs_frame, columns=("path"), show="headings")
        self.tree.heading("#0", text="Программа")
        self.tree.heading("path", text="Путь установщика")
        
        vsb = ttk.Scrollbar(programs_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(programs_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Добавление стандартных программ
        for program in PROGRAMS:
            self.tree.insert("", "end", text=program["name"], values=(program["path"]))
        
        # Кнопки управления
        buttons_frame = ttk.Frame(programs_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        ttk.Button(buttons_frame, text="Добавить программу", 
                  command=self.add_custom_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Удалить выбранное", 
                  command=self.remove_program).pack(side=tk.LEFT, padx=5)
        
        # Фрейм логов
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка установки
        install_button = ttk.Button(main_frame, text="Начать установку", 
                                  command=self.start_installation)
        install_button.pack(pady=10)

    def add_custom_program(self):
        name = simpledialog.askstring("Добавить программу", "Название программы:")
        if not name:
            return
            
        path = filedialog.askopenfilename(
            title="Выберите установочный файл",
            filetypes=(("Исполняемые файлы", "*.exe *.msi"), ("Все файлы", "*.*"))
        )
        
        if path:
            args = simpledialog.askstring(
                "Аргументы установки", 
                f"Аргументы командной строки для {name} (если нужны):",
                initialvalue=""
            )
            self.custom_programs.append({"name": name, "path": path, "args": args.split() if args else []})
            self.tree.insert("", "end", text=name, values=(path))

    def remove_program(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_text = self.tree.item(selected_item)["text"]
            
            # Удаление из кастомных программ
            self.custom_programs = [p for p in self.custom_programs if p["name"] != item_text]
            
            # Удаление из дерева
            self.tree.delete(selected_item)

    def log_message(self, message):
        self.log_queue.put(message)

    def check_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.configure(state="disabled")
            self.log_text.see(tk.END)
        self.root.after(100, self.check_queue)

    def disable_defender(self):
        try:
            commands = [
                'Set-MpPreference -DisableRealtimeMonitoring $true',
                'Set-MpPreference -DisableBehaviorMonitoring $true',
                'Set-MpPreference -DisableBlockAtFirstSeen $true',
                'Set-MpPreference -DisableIOAVProtection $true'
            ]
            
            for cmd in commands:
                subprocess.run(
                    ["powershell", "-Command", cmd],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            self.log_message(">>> Защитник Windows отключен")
            return True
        except subprocess.CalledProcessError as e:
            self.log_message(f"!!! Ошибка отключения Защитника: {e.stderr}")
            return False

    def enable_defender(self):
        try:
            commands = [
                'Set-MpPreference -DisableRealtimeMonitoring $false',
                'Set-MpPreference -DisableBehaviorMonitoring $false',
                'Set-MpPreference -DisableBlockAtFirstSeen $false',
                'Set-MpPreference -DisableIOAVProtection $false'
            ]
            
            for cmd in commands:
                subprocess.run(
                    ["powershell", "-Command", cmd],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            self.log_message(">>> Защитник Windows включен")
            return True
        except subprocess.CalledProcessError as e:
            self.log_message(f"!!! Ошибка включения Защитника: {e.stderr}")
            return False

    def run_installation(self):
        # Проверка пароля
        password = self.password.get()
        if not password:
            self.log_message("!!! Ошибка: Пароль не введен")
            return
        
        # Отключение защитника
        self.log_message(">>> Отключаю Защитник Windows...")
        if not self.disable_defender():
            self.log_message("!!! Установка прервана из-за ошибки Защитника")
            return
        
        try:
            # Сбор всех программ для установки
            all_programs = PROGRAMS + self.custom_programs
            
            # Установка выбранных программ
            for item in self.tree.get_children():
                program_name = self.tree.item(item)["text"]
                program = next((p for p in all_programs if p["name"] == program_name), None)
                
                if not program:
                    continue
                    
                self.log_message(f">>> Начинаю установку: {program_name}")
                
                try:
                    # Для MSI-файлов используем msiexec
                    if program["path"].lower().endswith(".msi"):
                        cmd = ["msiexec", "/i", program["path"]] + program["args"]
                    else:
                        cmd = [program["path"]] + program["args"]
                    
                    result = subprocess.run(
                        cmd,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="cp866"
                    )
                    self.log_message(f">>> Успешно установлено: {program_name}")
                    
                except subprocess.CalledProcessError as e:
                    self.log_message(f"!!! Ошибка установки {program_name}: {e.stderr}")
                except Exception as e:
                    self.log_message(f"!!! Критическая ошибка при установке {program_name}: {str(e)}")
            
            self.log_message(">>> Все программы установлены!")
            
        finally:
            # Всегда включаем защитник обратно
            self.log_message(">>> Включаю Защитник Windows...")
            self.enable_defender()

    def start_installation(self):
        if not self.tree.get_children():
            messagebox.showwarning("Ошибка", "Не выбраны программы для установки")
            return
            
        if not self.password.get():
            messagebox.showwarning("Ошибка", "Введите пароль учетной записи")
            return
            
        # Запуск в отдельном потоке
        threading.Thread(target=self.run_installation, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()