import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import os
import sys
import numpy as np  # Явный импорт для pandas

# Функция для корректного определения путей в EXE-сборке
def resource_path(relative_path):
    """Возвращает корректный путь для ресурсов при работе из EXE"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MacConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер MAC-адресов")
        self.root.geometry("800x600")
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TLabel', padding=6)
        
        # Основные фреймы
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель управления
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(self.top_frame, text="Открыть файл", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_frame, text="Сохранить passwords.txt", command=self.save_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_frame, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Область ввода/вывода
        self.io_frame = ttk.Frame(self.main_frame)
        self.io_frame.pack(fill=tk.BOTH, expand=True)
        
        # Входные данные
        ttk.Label(self.io_frame, text="Входные данные:").pack(anchor=tk.W)
        self.input_text = ScrolledText(self.io_frame, height=10, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Результат
        ttk.Label(self.io_frame, text="Результат:").pack(anchor=tk.W)
        self.output_text = ScrolledText(self.io_frame, height=10, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def open_file(self):
        filetypes = (
            ('Excel файлы', '*.xlsx *.xls'),
            ('Текстовые файлы', '*.txt'),
            ('Все файлы', '*.*')
        )
        
        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=filetypes
        )
        
        if not filepath:
            return
            
        try:
            if filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath, header=None)
                input_data = '\n'.join(' '.join(str(cell) for cell in row if pd.notna(cell)) for row in df.values)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    input_data = f.read()
            
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, input_data)
            self.process_data()
            self.status_var.set(f"Файл загружен: {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            self.status_var.set("Ошибка загрузки файла")
    
    def save_result(self):
        result = self.output_text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
            
        # Запрашиваем папку для сохранения
        folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not folder:
            return
            
        filepath = os.path.join(folder, "passwords.txt")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result)
            self.status_var.set(f"Файл сохранён: {filepath}")
            messagebox.showinfo("Успех", f"Файл успешно сохранён как:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            self.status_var.set("Ошибка сохранения файла")
    
    def clear_all(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Готово")
    
    def process_data(self):
        input_data = self.input_text.get(1.0, tk.END)
        if not input_data.strip():
            return
            
        lines = input_data.split('\n')
        results = []
        
        for line in lines:
            if not line.strip():
                continue
                
            formatted = self.process_mac_password(line)
            if formatted:
                results.append(formatted)
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, '\n'.join(results))
        self.status_var.set(f"Обработано {len(results)} строк")
    
    def process_mac_password(self, input_str):
        parts = re.split(r'[\s\t,;]+', input_str.strip())
        mac, password = None, None

        for part in parts:
            # Проверяем MAC в формате 505B1D15A734 (без разделителей)
            if re.match(r'^[0-9A-Fa-f]{12}$', part):
                mac = part.upper()
            # Проверяем MAC с двоеточиями (50:5B:1D:15:A7:34) или дефисами (F8-F0-82-11-19-67)
            elif re.match(r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$', part):
                mac = part.replace(':', '').replace('-', '').upper()
            # Проверяем пароль (00594dae или bd054494)
            elif re.match(r'^[0-9A-Fa-f]{6,8}$', part):
                password = part.lower()

        if not mac or not password:
            return None

        # Форматируем MAC в 50:5B:1D:15:A7:34 (или F8:F0:82:11:19:67)
        formatted_mac = f"{mac[0:2]}:{mac[2:4]}:{mac[4:6]}:{mac[6:8]}:{mac[8:10]}:{mac[10:12]}"
        return f"{formatted_mac}:{password}"

if __name__ == "__main__":
    try:
        root = tk.Tk()
        # Пытаемся загрузить иконку
        try:
            icon_path = resource_path('app.ico')
            root.iconbitmap(icon_path)
        except:
            pass
        app = MacConverterApp(root)
        root.mainloop()
    except Exception as e:
        # Запись ошибки в лог
        error_log = os.path.join(os.path.expanduser("~"), "mac_converter_error.log")
        with open(error_log, 'w') as f:
            f.write(str(e))
        messagebox.showerror("Критическая ошибка", 
            f"Программа завершилась с ошибкой.\nПодробности в файле:\n{error_log}")