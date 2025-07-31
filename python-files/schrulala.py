import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import json
import threading
import time
import zipfile
import rarfile
import py7zr
from pathlib import Path
import re
from datetime import datetime
from PIL import Image, ImageTk
import configparser

class ModernArchiveAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Archive Cookie Analyzer Pro")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Конфигурация
        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"
        self.passwords_file = "passwords.txt"
        self.results_file = "results.txt"
        
        # Переменные
        self.current_language = tk.StringVar(value="ru")
        self.current_theme = tk.StringVar(value="dark")
        self.background_image = None
        self.found_cookies = []
        self.stats = {"processed_archives": 0, "found_cookies": 0, "total_files": 0}
        
        # Загрузка конфигурации
        self.load_config()
        
        # Словари для локализации
        self.translations = {
            "ru": {
                "title": "Анализатор архивов - Pro версия",
                "select_file": "Выбрать файл",
                "settings": "Настройки",
                "results": "Результаты",
                "statistics": "Статистика",
                "language": "Язык:",
                "theme": "Тема:",
                "background": "Фон:",
                "load_bg": "Загрузить фон",
                "remove_bg": "Удалить фон",
                "start_analysis": "Начать анализ",
                "stop_analysis": "Остановить",
                "progress": "Прогресс:",
                "status": "Готов к работе",
                "processing": "Обработка...",
                "completed": "Завершено",
                "found": "Найдено:",
                "processed": "Обработано:",
                "files": "файлов",
                "archives": "архивов",
                "cookies": "cookies"
            },
            "en": {
                "title": "Archive Analyzer - Pro Version",
                "select_file": "Select File",
                "settings": "Settings",
                "results": "Results",
                "statistics": "Statistics",
                "language": "Language:",
                "theme": "Theme:",
                "background": "Background:",
                "load_bg": "Load Background",
                "remove_bg": "Remove Background",
                "start_analysis": "Start Analysis",
                "stop_analysis": "Stop",
                "progress": "Progress:",
                "status": "Ready",
                "processing": "Processing...",
                "completed": "Completed",
                "found": "Found:",
                "processed": "Processed:",
                "files": "files",
                "archives": "archives",
                "cookies": "cookies"
            }
        }
        
        # Темы
        self.themes = {
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "select_bg": "#404040",
                "button_bg": "#0078d4",
                "button_fg": "#ffffff",
                "entry_bg": "#404040",
                "frame_bg": "#363636"
            },
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#e3f2fd",
                "button_bg": "#2196f3",
                "button_fg": "#ffffff",
                "entry_bg": "#f5f5f5",
                "frame_bg": "#f0f0f0"
            },
            "blue": {
                "bg": "#1e3a8a",
                "fg": "#ffffff",
                "select_bg": "#3b82f6",
                "button_bg": "#06b6d4",
                "button_fg": "#ffffff",
                "entry_bg": "#1e40af",
                "frame_bg": "#1d4ed8"
            }
        }
        
        self.setup_ui()
        self.apply_theme()
        self.center_window()
        
    def setup_ui(self):
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть архив", command=self.select_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Создание notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка анализа
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Анализ")
        self.setup_main_tab()
        
        # Вкладка настроек
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Настройки")
        self.setup_settings_tab()
        
        # Вкладка результатов
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Результаты")
        self.setup_results_tab()
        
        # Статус бар
        self.status_frame = tk.Frame(self.root, height=30)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Готов к работе", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side="right", padx=10, pady=5)
    
    def setup_main_tab(self):
        # Фоновое изображение
        self.bg_label = tk.Label(self.main_frame)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Главная рамка
        main_container = tk.Frame(self.main_frame, bg="#2b2b2b", relief="raised", bd=2)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = tk.Label(main_container, text="🔍 Archive Cookie Analyzer Pro", 
                              font=("Arial", 24, "bold"), fg="#0078d4", bg="#2b2b2b")
        title_label.pack(pady=20)
        
        # Область выбора файла
        file_frame = tk.Frame(main_container, bg="#363636", relief="groove", bd=2)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        file_label = tk.Label(file_frame, text="📁 Выберите архив для анализа", 
                             font=("Arial", 14), fg="#ffffff", bg="#363636")
        file_label.pack(pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, 
                             font=("Arial", 12), width=50, bg="#404040", fg="#ffffff")
        file_entry.pack(pady=5)
        
        file_btn = tk.Button(file_frame, text="🔍 Выбрать файл", 
                            command=self.select_file, font=("Arial", 12, "bold"),
                            bg="#0078d4", fg="#ffffff", relief="flat", padx=20, pady=5)
        file_btn.pack(pady=10)
        
        # Область управления
        control_frame = tk.Frame(main_container, bg="#363636", relief="groove", bd=2)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        self.start_btn = tk.Button(control_frame, text="🚀 Начать анализ", 
                                  command=self.start_analysis, font=("Arial", 14, "bold"),
                                  bg="#28a745", fg="#ffffff", relief="flat", padx=30, pady=10)
        self.start_btn.pack(side="left", padx=20, pady=20)
        
        self.stop_btn = tk.Button(control_frame, text="⏹ Остановить", 
                                 command=self.stop_analysis, font=("Arial", 14, "bold"),
                                 bg="#dc3545", fg="#ffffff", relief="flat", padx=30, pady=10,
                                 state="disabled")
        self.stop_btn.pack(side="left", padx=10, pady=20)
        
        # Информационная панель
        info_frame = tk.Frame(main_container, bg="#363636", relief="groove", bd=2)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        info_label = tk.Label(info_frame, text="📊 Статистика", 
                             font=("Arial", 16, "bold"), fg="#ffffff", bg="#363636")
        info_label.pack(pady=10)
        
        stats_frame = tk.Frame(info_frame, bg="#363636")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_labels = {}
        stats_items = [
            ("Обработано архивов:", "processed_archives"),
            ("Найдено cookies:", "found_cookies"),
            ("Всего файлов:", "total_files")
        ]
        
        for i, (text, key) in enumerate(stats_items):
            frame = tk.Frame(stats_frame, bg="#404040", relief="raised", bd=1)
            frame.pack(fill="x", pady=5)
            
            tk.Label(frame, text=text, font=("Arial", 12), 
                    fg="#ffffff", bg="#404040").pack(side="left", padx=10, pady=5)
            
            self.stats_labels[key] = tk.Label(frame, text="0", font=("Arial", 12, "bold"), 
                                             fg="#0078d4", bg="#404040")
            self.stats_labels[key].pack(side="right", padx=10, pady=5)
    
    def setup_settings_tab(self):
        settings_container = tk.Frame(self.settings_frame, bg="#2b2b2b")
        settings_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок настроек
        title = tk.Label(settings_container, text="⚙️ Настройки приложения", 
                        font=("Arial", 20, "bold"), fg="#0078d4", bg="#2b2b2b")
        title.pack(pady=20)
        
        # Языковые настройки
        lang_frame = tk.LabelFrame(settings_container, text="🌐 Язык", 
                                  font=("Arial", 14), fg="#ffffff", bg="#363636")
        lang_frame.pack(fill="x", pady=10)
        
        lang_options = [("Русский", "ru"), ("English", "en")]
        for text, value in lang_options:
            tk.Radiobutton(lang_frame, text=text, variable=self.current_language, 
                          value=value, font=("Arial", 12), fg="#ffffff", bg="#363636",
                          selectcolor="#0078d4", command=self.change_language).pack(side="left", padx=20, pady=10)
        
        # Настройки темы
        theme_frame = tk.LabelFrame(settings_container, text="🎨 Тема оформления", 
                                   font=("Arial", 14), fg="#ffffff", bg="#363636")
        theme_frame.pack(fill="x", pady=10)
        
        theme_options = [("Тёмная", "dark"), ("Светлая", "light"), ("Синяя", "blue")]
        for text, value in theme_options:
            tk.Radiobutton(theme_frame, text=text, variable=self.current_theme, 
                          value=value, font=("Arial", 12), fg="#ffffff", bg="#363636",
                          selectcolor="#0078d4", command=self.apply_theme).pack(side="left", padx=20, pady=10)
        
        # Настройки фона
        bg_frame = tk.LabelFrame(settings_container, text="🖼️ Фоновое изображение", 
                                font=("Arial", 14), fg="#ffffff", bg="#363636")
        bg_frame.pack(fill="x", pady=10)
        
        bg_btn_frame = tk.Frame(bg_frame, bg="#363636")
        bg_btn_frame.pack(pady=10)
        
        load_bg_btn = tk.Button(bg_btn_frame, text="📁 Загрузить фон", 
                               command=self.load_background, font=("Arial", 12),
                               bg="#0078d4", fg="#ffffff", relief="flat", padx=20, pady=5)
        load_bg_btn.pack(side="left", padx=10)
        
        remove_bg_btn = tk.Button(bg_btn_frame, text="🗑️ Удалить фон", 
                                 command=self.remove_background, font=("Arial", 12),
                                 bg="#dc3545", fg="#ffffff", relief="flat", padx=20, pady=5)
        remove_bg_btn.pack(side="left", padx=10)
        
        # Настройки паролей
        pwd_frame = tk.LabelFrame(settings_container, text="🔐 Настройки паролей", 
                                 font=("Arial", 14), fg="#ffffff", bg="#363636")
        pwd_frame.pack(fill="x", pady=10)
        
        pwd_btn = tk.Button(pwd_frame, text="📝 Редактировать список паролей", 
                           command=self.edit_passwords, font=("Arial", 12),
                           bg="#28a745", fg="#ffffff", relief="flat", padx=20, pady=10)
        pwd_btn.pack(pady=10)
    
    def setup_results_tab(self):
        results_container = tk.Frame(self.results_frame, bg="#2b2b2b")
        results_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title = tk.Label(results_container, text="📋 Результаты анализа", 
                        font=("Arial", 20, "bold"), fg="#0078d4", bg="#2b2b2b")
        title.pack(pady=20)
        
        # Текстовое поле для результатов
        text_frame = tk.Frame(results_container, bg="#363636", relief="groove", bd=2)
        text_frame.pack(fill="both", expand=True, pady=10)
        
        # Создание Treeview для красивого отображения результатов
        columns = ("Время", "Архив", "Путь", "Cookie")
        self.results_tree = ttk.Treeview(text_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.results_tree.heading("Время", text="Время")
        self.results_tree.heading("Архив", text="Архив")
        self.results_tree.heading("Путь", text="Путь к файлу")
        self.results_tree.heading("Cookie", text="Найденный Cookie")
        
        # Настройка ширины колонок
        self.results_tree.column("Время", width=150)
        self.results_tree.column("Архив", width=200)
        self.results_tree.column("Путь", width=300)
        self.results_tree.column("Cookie", width=400)
        
        # Добавление скроллбара
        scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_tree.yview)
        scrollbar_x = ttk.Scrollbar(text_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Кнопки управления результатами
        btn_frame = tk.Frame(results_container, bg="#2b2b2b")
        btn_frame.pack(fill="x", pady=10)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Очистить результаты", 
                             command=self.clear_results, font=("Arial", 12),
                             bg="#dc3545", fg="#ffffff", relief="flat", padx=20, pady=5)
        clear_btn.pack(side="left", padx=10)
        
        export_btn = tk.Button(btn_frame, text="💾 Экспорт в файл", 
                              command=self.export_results, font=("Arial", 12),
                              bg="#28a745", fg="#ffffff", relief="flat", padx=20, pady=5)
        export_btn.pack(side="left", padx=10)
    
    def select_file(self):
        filetypes = [
            ("Архивы", "*.zip;*.rar;*.7z"),
            ("ZIP файлы", "*.zip"),
            ("RAR файлы", "*.rar"),
            ("7Z файлы", "*.7z"),
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Выберите архив для анализа",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.update_status(f"Выбран файл: {os.path.basename(filename)}")
    
    def start_analysis(self):
        if not self.file_path_var.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите файл для анализа")
            return
        
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.analysis_thread = threading.Thread(target=self.analyze_archive)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop_analysis(self):
        self.stop_btn.config(state="disabled")
        self.start_btn.config(state="normal")
        self.update_status("Анализ остановлен пользователем")
    
    def analyze_archive(self):
        try:
            archive_path = self.file_path_var.get()
            self.update_status("Начинаем анализ архива...")
            
            # Определение типа архива и попытка открытия
            archive = self.open_archive(archive_path)
            if not archive:
                return
            
            self.stats["processed_archives"] += 1
            self.update_stats()
            
            # Поиск cookies в архиве
            self.search_cookies_in_archive(archive, archive_path)
            
            archive.close()
            self.update_status("Анализ завершен успешно")
            
        except Exception as e:
            self.update_status(f"Ошибка при анализе: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
    
    def open_archive(self, archive_path):
        file_ext = os.path.splitext(archive_path)[1].lower()
        
        try:
            if file_ext == '.zip':
                return self.open_zip_archive(archive_path)
            elif file_ext == '.rar':
                return self.open_rar_archive(archive_path)
            elif file_ext == '.7z':
                return self.open_7z_archive(archive_path)
            else:
                messagebox.showerror("Ошибка", "Неподдерживаемый формат архива")
                return None
        except Exception as e:
            if "password" in str(e).lower() or "wrong password" in str(e).lower():
                return self.try_passwords(archive_path, file_ext)
            else:
                raise e
    
    def open_zip_archive(self, path, password=None):
        if password:
            return zipfile.ZipFile(path, 'r', pwd=password.encode())
        else:
            return zipfile.ZipFile(path, 'r')
    
    def open_rar_archive(self, path, password=None):
        archive = rarfile.RarFile(path, 'r')
        if password:
            archive.setpassword(password)
        return archive
    
    def open_7z_archive(self, path, password=None):
        if password:
            return py7zr.SevenZipFile(path, mode='r', password=password)
        else:
            return py7zr.SevenZipFile(path, mode='r')
    
    def try_passwords(self, archive_path, file_ext):
        passwords = self.load_passwords()
        
        for password in passwords:
            try:
                self.update_status(f"Пробуем пароль: {password}")
                if file_ext == '.zip':
                    archive = self.open_zip_archive(archive_path, password)
                elif file_ext == '.rar':
                    archive = self.open_rar_archive(archive_path, password)
                elif file_ext == '.7z':
                    archive = self.open_7z_archive(archive_path, password)
                
                # Проверим, что архив действительно открылся
                if file_ext == '.zip':
                    archive.testzip()
                
                self.update_status(f"Пароль найден: {password}")
                return archive
                
            except:
                continue
        
        # Если ни один пароль не подошел, запрашиваем у пользователя
        password = simpledialog.askstring("Пароль", "Введите пароль для архива:", show='*')
        if password:
            try:
                if file_ext == '.zip':
                    archive = self.open_zip_archive(archive_path, password)
                elif file_ext == '.rar':
                    archive = self.open_rar_archive(archive_path, password)
                elif file_ext == '.7z':
                    archive = self.open_7z_archive(archive_path, password)
                
                # Добавляем новый пароль в список
                self.add_password(password)
                return archive
                
            except:
                messagebox.showerror("Ошибка", "Неверный пароль")
                return None
        
        return None
    
    def search_cookies_in_archive(self, archive, archive_path):
        target_string = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhAB"
        
        try:
            if hasattr(archive, 'namelist'):
                file_list = archive.namelist()
            else:
                file_list = archive.getnames()
            
            total_files = len(file_list)
            self.stats["total_files"] += total_files
            
            for i, file_path in enumerate(file_list):
                if self.stop_btn.cget('state') == 'disabled':  # Проверка на остановку
                    break
                
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                self.update_status(f"Обрабатываем файл: {os.path.basename(file_path)}")
                
                # Проверяем, что это файл в папке Cookies
                if 'cookies' in file_path.lower() and not file_path.endswith('/'):
                    try:
                        # Читаем содержимое файла
                        if hasattr(archive, 'read'):
                            file_content = archive.read(file_path)
                        else:
                            file_content = archive.extractall(file_path)
                        
                        if isinstance(file_content, bytes):
                            file_content = file_content.decode('utf-8', errors='ignore')
                        
                        # Ищем целевую строку
                        if target_string in file_content:
                            self.found_cookies.append({
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'archive': os.path.basename(archive_path),
                                'path': file_path,
                                'cookie': target_string[:50] + "..."
                            })
                            
                            self.stats["found_cookies"] += 1
                            self.update_results_display()
                            self.save_result_to_file(archive_path, file_path, target_string)
                            
                    except Exception as e:
                        print(f"Ошибка при чтении файла {file_path}: {e}")
                        continue
            
            self.progress_var.set(100)
            self.update_stats()
            
        except Exception as e:
            self.update_status(f"Ошибка при поиске: {str(e)}")
    
    def load_passwords(self):
        if not os.path.exists(self.passwords_file):
            # Создаем файл с базовыми паролями
            default_passwords = [
                "123456", "password", "123456789", "12345678", "12345",
                "111111", "1234567", "sunshine", "qwerty", "iloveyou",
                "admin", "welcome", "monkey", "login", "abc123",
                "starwars", "123123", "dragon", "passw0rd", "master"
            ]
            with open(self.passwords_file, 'w', encoding='utf-8') as f:
                for pwd in default_passwords:
                    f.write(pwd + '\n')
            return default_passwords
        
        with open(self.passwords_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    
    def add_password(self, password):
        with open(self.passwords_file, 'a', encoding='utf-8') as f:
            f.write(password + '\n')
    
    def save_result_to_file(self, archive_path, file_path, cookie_data):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.results_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {archive_path} | {file_path} | {cookie_data}\n")
    
    def update_results_display(self):
        # Обновляем отображение результатов в таблице
        if self.found_cookies:
            latest_result = self.found_cookies[-1]
            self.results_tree.insert("", "end", values=(
                latest_result['time'],
                latest_result['archive'],
                latest_result['path'],
                latest_result['cookie']
            ))
    
    def update_stats(self):
        for key, label in self.stats_labels.items():
            label.config(text=str(self.stats[key]))
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def clear_results(self):
        if messagebox.askyesno("Подтверждение", "Очистить все результаты?"):
            self.results_tree.delete(*self.results_tree.get_children())
            self.found_cookies.clear()
            self.stats = {"processed_archives": 0, "found_cookies": 0, "total_files": 0}
            self.update_stats()
    
    def export_results(self):
        if not self.found_cookies:
            messagebox.showinfo("Информация", "Нет результатов для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("CSV файлы", "*.csv")]
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Результаты анализа архивов\n")
                f.write("=" * 50 + "\n\n")
                for result in self.found_cookies:
                    f.write(f"Время: {result['time']}\n")
                    f.write(f"Архив: {result['archive']}\n")
                    f.write(f"Путь: {result['path']}\n")
                    f.write(f"Cookie: {result['cookie']}\n")
                    f.write("-" * 30 + "\n")
            
            messagebox.showinfo("Успех", f"Результаты экспортированы в {filename}")
    
    def edit_passwords(self):
        # Создание окна редактирования паролей
        pwd_window = tk.Toplevel(self.root)
        pwd_window.title("Редактор паролей")
        pwd_window.geometry("500x600")
        pwd_window.grab_set()
        
        tk.Label(pwd_window, text="Список паролей", font=("Arial", 16, "bold")).pack(pady=10)
        
        text_frame = tk.Frame(pwd_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        password_text = tk.Text(text_frame, font=("Arial", 12))
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=password_text.yview)
        password_text.configure(yscrollcommand=scrollbar.set)
        
        password_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Загружаем текущие пароли
        passwords = self.load_passwords()
        password_text.insert("1.0", "\n".join(passwords))
        
        def save_passwords():
            content = password_text.get("1.0", "end-1c")
            passwords = [line.strip() for line in content.split('\n') if line.strip()]
            
            with open(self.passwords_file, 'w', encoding='utf-8') as f:
                for pwd in passwords:
                    f.write(pwd + '\n')
            
            messagebox.showinfo("Успех", "Пароли сохранены")
            pwd_window.destroy()
        
        btn_frame = tk.Frame(pwd_window)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(btn_frame, text="Сохранить", command=save_passwords,
                 bg="#28a745", fg="white", font=("Arial", 12)).pack(side="right", padx=5)
        tk.Button(btn_window, text="Отмена", command=pwd_window.destroy,
                 bg="#dc3545", fg="white", font=("Arial", 12)).pack(side="right", padx=5)
    
    def apply_theme(self):
        theme = self.themes[self.current_theme.get()]
        
        # Применяем тему к основным элементам
        self.root.configure(bg=theme["bg"])
        
        # Обновляем стили ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TNotebook', background=theme["bg"])
        style.configure('TNotebook.Tab', background=theme["frame_bg"], 
                       foreground=theme["fg"], padding=[20, 10])
        style.configure('TFrame', background=theme["bg"])
        style.configure('TLabelframe', background=theme["bg"], 
                       foreground=theme["fg"])
        style.configure('TLabelframe.Label', background=theme["bg"], 
                       foreground=theme["fg"])
        
        self.save_config()
    
    def change_language(self):
        # Здесь можно добавить логику смены языка
        self.save_config()
        messagebox.showinfo("Информация", "Перезапустите приложение для применения изменений")
    
    def load_background(self):
        filename = filedialog.askopenfilename(
            title="Выберите фоновое изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if filename:
            try:
                image = Image.open(filename)
                # Изменяем размер под окно
                image = image.resize((1200, 800), Image.Resampling.LANCZOS)
                self.background_image = ImageTk.PhotoImage(image)
                self.bg_label.configure(image=self.background_image)
                
                # Сохраняем путь к фону в конфиг
                self.config.set('DEFAULT', 'background_image', filename)
                self.save_config()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
    
    def remove_background(self):
        self.background_image = None
        self.bg_label.configure(image="")
        if self.config.has_option('DEFAULT', 'background_image'):
            self.config.remove_option('DEFAULT', 'background_image')
        self.save_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            
            # Загружаем настройки
            if self.config.has_option('DEFAULT', 'language'):
                self.current_language.set(self.config.get('DEFAULT', 'language'))
            
            if self.config.has_option('DEFAULT', 'theme'):
                self.current_theme.set(self.config.get('DEFAULT', 'theme'))
            
            if self.config.has_option('DEFAULT', 'background_image'):
                bg_path = self.config.get('DEFAULT', 'background_image')
                if os.path.exists(bg_path):
                    try:
                        image = Image.open(bg_path)
                        image = image.resize((1200, 800), Image.Resampling.LANCZOS)
                        self.background_image = ImageTk.PhotoImage(image)
                    except:
                        pass
    
    def save_config(self):
        self.config.set('DEFAULT', 'language', self.current_language.get())
        self.config.set('DEFAULT', 'theme', self.current_theme.get())
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    app = ModernArchiveAnalyzer()
    app.run()