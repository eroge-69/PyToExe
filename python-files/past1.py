import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import ctypes
import sys
import re

class JaCartaManager:
    def __init__(self, root):
        self.root = root
        self.root.title("JaCarta SF-ГОСТ Manager")
        self.root.geometry("800x900")
        
        # Путь к серверу (по умолчанию)
        self.server_path = tk.StringVar()
        self.server_path.set("C:\Program Files\JaCarta SF-ГОСТ\JcSfSrv\jcsfserviceconf.exe")
        
        # Переменные для путей и порта
        self.container_path = tk.StringVar()
        self.port = tk.StringVar()
        self.port.set("2000")
        
        # Переменная для хранения пароля
        self.password = tk.StringVar()
        
        # Переменная для списка контейнеров
        self.containers_list = []
        self.containers_dict = {}  # Для хранения полной информации о контейнерах
        
        self.create_widgets()
    
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="JaCarta SF-ГОСТ Manager", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Фрейм для выбора пути к серверу
        server_frame = tk.LabelFrame(self.root, text="Путь к серверу", padx=10, pady=10)
        server_frame.pack(pady=5, padx=10, fill='x')
        
        path_frame = tk.Frame(server_frame)
        path_frame.pack(fill='x')
        
        tk.Entry(path_frame, textvariable=self.server_path, width=70).pack(side='left', fill='x', expand=True)
        tk.Button(path_frame, text="Обзор", command=self.browse_server).pack(side='right', padx=(5,0))
        
        # Фрейм для выбора контейнера
        container_frame = tk.LabelFrame(self.root, text="Путь к контейнеру", padx=10, pady=10)
        container_frame.pack(pady=5, padx=10, fill='x')
        
        container_path_frame = tk.Frame(container_frame)
        container_path_frame.pack(fill='x')
        
        tk.Entry(container_path_frame, textvariable=self.container_path, width=70).pack(side='left', fill='x', expand=True)
        tk.Button(container_path_frame, text="Обзор", command=self.browse_container).pack(side='right', padx=(5,0))
        
        # Фрейм для порта
        port_frame = tk.LabelFrame(self.root, text="Порт", padx=10, pady=10)
        port_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(port_frame, text="Порт:").pack(side='left')
        tk.Entry(port_frame, textvariable=self.port, width=10).pack(side='left', padx=(5,0))
        
        # Фрейм для пароля
        password_frame = tk.LabelFrame(self.root, text="Пароль", padx=10, pady=10)
        password_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(password_frame, text="Пароль:").pack(side='left')
        password_entry = tk.Entry(password_frame, textvariable=self.password, width=30, show='*')
        password_entry.pack(side='left', padx=(5,0))
        self.password_entry = password_entry  # Сохраняем ссылку для переключения видимости
        
        tk.Button(password_frame, text="Показать/Скрыть", command=self.toggle_password_visibility).pack(side='left', padx=(5,0))
        
        # Фрейм для кнопок команд
        commands_frame = tk.LabelFrame(self.root, text="Команды", padx=10, pady=10)
        commands_frame.pack(pady=5, padx=10, fill='x')
        
        # Кнопки отдельных команд
        btn_frame1 = tk.Frame(commands_frame)
        btn_frame1.pack(fill='x', pady=2)
        
        tk.Button(btn_frame1, text="1. Загрузить контейнер", command=self.load_container, 
                 width=25, bg='#4CAF50', fg='white').pack(side='left', padx=2)
        
        btn_frame2 = tk.Frame(commands_frame)
        btn_frame2.pack(fill='x', pady=2)
        
        tk.Button(btn_frame2, text="2. Задать порт", command=self.set_port, 
                 width=25, bg='#2196F3', fg='white').pack(side='left', padx=2)
        
        btn_frame3 = tk.Frame(commands_frame)
        btn_frame3.pack(fill='x', pady=2)
        
        tk.Button(btn_frame3, text="3. Проверить контейнеры", command=self.list_containers, 
                 width=25, bg='#FF9800', fg='white').pack(side='left', padx=2)
        
        btn_frame4 = tk.Frame(commands_frame)
        btn_frame4.pack(fill='x', pady=2)
        
        tk.Button(btn_frame4, text="4A. Остановить сервер", command=self.stop_server, 
                 width=25, bg='#f44336', fg='white').pack(side='left', padx=2)
        tk.Button(btn_frame4, text="4B. Запустить сервер", command=self.start_server, 
                 width=25, bg='#4CAF50', fg='white').pack(side='left', padx=2)
        
        # Фрейм для удаления контейнера
        delete_frame = tk.LabelFrame(self.root, text="Удаление контейнера", padx=10, pady=10)
        delete_frame.pack(pady=5, padx=10, fill='x')
        
        # Выбор контейнера для удаления
        self.container_to_delete = tk.StringVar()
        container_delete_frame = tk.Frame(delete_frame)
        container_delete_frame.pack(fill='x', pady=2)
        
        tk.Label(container_delete_frame, text="Выберите контейнер:").pack(side='left')
        # Изначально пустой список контейнеров
        self.container_dropdown = tk.OptionMenu(container_delete_frame, self.container_to_delete, "")
        self.container_dropdown.pack(side='left', padx=(5,0))
        
        tk.Button(container_delete_frame, text="5. Удалить контейнер", command=self.delete_container, 
                 width=20, bg='#f44336', fg='white').pack(side='left', padx=2)
        
        # Область вывода результатов
        output_frame = tk.LabelFrame(self.root, text="Результаты выполнения", padx=10, pady=10)
        output_frame.pack(pady=5, padx=10, fill='both', expand=True)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.pack(fill='both', expand=True)
        
        # Кнопка очистки вывода
        tk.Button(output_frame, text="Очистить вывод", command=self.clear_output).pack(pady=5)
    
    def toggle_password_visibility(self):
        """Переключение видимости пароля"""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def browse_server(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл сервера",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.server_path.set(filename)
    
    def browse_container(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл контейнера",
            filetypes=[("Container files", "*.*"), ("All files", "*.*")]
        )
        if filename:
            # Преобразуем слеши в Windows формат
            windows_path = filename.replace('/', '\\')
            self.container_path.set(windows_path)
    
    def run_command(self, command, description=""):
        """Основной метод выполнения команд"""
        try:
            self.output_text.insert(tk.END, f"\n--- {description} ---\n")
            self.output_text.insert(tk.END, f"Команда: {command}\n")
            self.output_text.insert(tk.END, "-" * 50 + "\n")
            self.output_text.see(tk.END)
            self.root.update()
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result:
                self.output_text.insert(tk.END, result.stderr)
                # Если это команда списка контейнеров, парсим результат
                if "-l" in command:
                    self.parse_containers_list(result.stderr)
#            if result:
#                print(result.stderr)
#                self.output_text.insert(tk.END, f"ОШИБКА: {result.stderr}")
            
            self.output_text.insert(tk.END, f"\nКод возврата: {result.returncode}\n")
            self.output_text.see(tk.END)
            self.root.update()
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.output_text.insert(tk.END, "Ошибка: Команда превысила время ожидания\n")
            return False
        except Exception as e:
            self.output_text.insert(tk.END, f"Ошибка выполнения команды: {str(e)}\n")
            return False
    
    def parse_containers_list(self, output):
        """Парсит список контейнеров из вывода команды -l"""
        self.containers_list = []
        self.containers_dict = {}
        
        lines = output.split('\n')
        
        # Ищем строки с информацией о контейнерах
        for line in lines:
            line = line.strip()
            
            # Формат: S/N : "..." | K/N: "..."
            sn_kn_pattern = r'[Ss]/[Nn]\s*:\s*"([^"]+)"\s*\|\s*[Kk]/[Nn]\s*:\s*"([^"]+)"'
            match = re.search(sn_kn_pattern, line)
            
            if match:
                sn = match.group(1)
                kn = match.group(2)
                # Формируем строку для удаления: S/N K/N
                delete_info = f"{sn} {kn}"
                display_info = f"S/N: {sn} | K/N: {kn}"
                
                self.containers_list.append(display_info)
                self.containers_dict[display_info] = delete_info
                continue
            print(self.containers_list)
            
            # Альтернативный формат поиска
            if 'S/N' in line.upper() and 'K/N' in line.upper() and '"' in line:
                # Ищем значения в кавычках
                quotes = re.findall(r'"([^"]+)"', line)
                if len(quotes) >= 2:
                    sn = quotes[0]
                    kn = quotes[1]
                    delete_info = f"{sn} {kn}"
                    display_info = f"S/N: {sn} | K/N: {kn}"
                    
                    self.containers_list.append(display_info)
                    self.containers_dict[display_info] = delete_info
        
        # Обновляем dropdown меню
        self.update_container_dropdown()
    
    def update_container_dropdown(self):
        """Обновляет dropdown меню с контейнерами"""
        # Удаляем старое меню
        self.container_dropdown.destroy()
        
        # Создаем новое меню
        if self.containers_list:
            print(self.containers_list)
            menu = tk.OptionMenu(self.container_dropdown.master, self.container_to_delete, *self.containers_list)
        else:
            # Если контейнеров нет, показываем пустой список
            menu = tk.OptionMenu(self.container_dropdown.master, self.container_to_delete, "Нет контейнеров для удаления")
        
        menu.pack(side='left', padx=(5,0))
        self.container_dropdown = menu
        
        # Если есть контейнеры, выбираем первый
        if self.containers_list:
            self.container_to_delete.set(self.containers_list[0])
    
    def load_container(self):
        if not os.path.exists(self.server_path.get()):
            messagebox.showerror("Ошибка", "Файл сервера не найден!")
            return
        
        if not self.container_path.get():
            messagebox.showwarning("Предупреждение", "Выберите путь к контейнеру!")
            return
        
        if not os.path.exists(self.container_path.get()):
            messagebox.showwarning("Предупреждение", "Файл контейнера не найден!")
            return
        
        if not self.password.get():
            messagebox.showwarning("Предупреждение", "Введите пароль!")
            return
        
        # Используем echo для передачи пароля
        command = f'echo {self.password.get()} | "{self.server_path.get()}" -c "{self.container_path.get()}"'
        self.run_command(command, "Загрузка контейнера")
    
    def set_port(self):
        if not os.path.exists(self.server_path.get()):
            messagebox.showerror("Ошибка", "Файл сервера не найден!")
            return
        
        if not self.port.get():
            messagebox.showwarning("Предупреждение", "Введите порт!")
            return
        
        command = f'"{self.server_path.get()}" -d {self.port.get()}'
        self.run_command(command, "Задание порта")
    
    def list_containers(self):
        if not os.path.exists(self.server_path.get()):
            messagebox.showerror("Ошибка", "Файл сервера не найден!")
            return
        
        # Очищаем списки перед новым поиском
        self.containers_list = []
        self.containers_dict = {}
        
        command = f'"{self.server_path.get()}" -l'
        self.run_command(command, "Проверка загруженных контейнеров")
    
    def stop_server(self):
        if not os.path.exists(self.server_path.get()):
            messagebox.showerror("Ошибка", "Файл сервера не найден!")
            return
        
        command = f'"{self.server_path.get()}" -t'
        self.run_command(command, "Остановка сервера")
    
    def start_server(self):
        if not os.path.exists(self.server_path.get()):
            messagebox.showerror("Ошибка", "Файл сервера не найден!")
            return
        
        command = f'"{self.server_path.get()}" -s'
        self.run_command(command, "Запуск сервера")
    
    def delete_container(self):
        if not os.path.exists(self.server_path.get()):
            messagebox.showerror("Ошибка", "Файл сервера не найден!")
            return
        
        selected_container = self.container_to_delete.get()
        if not selected_container or selected_container == "Нет контейнеров для удаления":
            messagebox.showwarning("Предупреждение", "Нет контейнеров для удаления!")
            return
        
        # Получаем информацию для удаления
        if selected_container in self.containers_dict:
            delete_info = self.containers_dict[selected_container]
        else:
            messagebox.showerror("Ошибка", "Не удалось получить информацию для удаления!")
            return
        
        result = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить контейнер:\n{selected_container}?")
        if not result:
            return
        
        # Формируем команду удаления: путь_к_серверу -e S/N K/N
        command = f'"{self.server_path.get()}" -e {delete_info}'
        self.run_command(command, "Удаление контейнера")
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if is_admin():
        root = tk.Tk()
        app = JaCartaManager(root)
        root.mainloop()
    else:
        # Перезапуск скрипта с правами администратора
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )

if __name__ == "__main__":
    run_as_admin()