import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import win32api
import win32con
import win32ui
from ctypes import windll

def extract_icon(exe_path, size=(32, 32)):
    """Извлекает иконку из исполняемого файла"""
    try:
        # Получаем handle иконки
        large, small = win32api.ExtractIconEx(exe_path, 0)
        win32api.DestroyIcon(small[0])
        
        # Создаем DC и битмап для иконки
        hdc = win32ui.CreateDCFromHandle(win32api.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, size[0], size[1])
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        
        # Рисуем иконку
        hdc.DrawIcon((0, 0), large[0])
        
        # Конвертируем в формат, понятный PIL
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        icon_image = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        
        # Очищаем ресурсы
        win32api.DestroyIcon(large[0])
        return ImageTk.PhotoImage(icon_image)
    except:
        # Возвращаем стандартную иконку в случае ошибки
        return None

class ProgramLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Запуск программ")
        self.root.geometry("800x600")
        
        # Переменные
        self.program_folder = tk.StringVar()
        self.icons = {}  # Кэш иконок
        
        # Создание интерфейса
        self.create_widgets()
        
        # Установка начальной папки (по умолчанию - рабочий стол)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.program_folder.set(desktop_path)
        self.load_programs()
    
    def create_widgets(self):
        # Фрейм для выбора папки
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(folder_frame, text="Папка с программами:").pack(side=tk.LEFT)
        ttk.Entry(folder_frame, textvariable=self.program_folder, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Обзор", command=self.browse_folder).pack(side=tk.LEFT)
        ttk.Button(folder_frame, text="Обновить", command=self.load_programs).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для списка программ
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаем Treeview с колонками
        self.tree = ttk.Treeview(list_frame, columns=("name", "path"), show="tree headings")
        self.tree.heading("#0", text="Иконка")
        self.tree.heading("name", text="Название программы")
        self.tree.heading("path", text="Путь")
        
        # Настраиваем колонки
        self.tree.column("#0", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("path", width=400, anchor=tk.W)
        
        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязываем двойной клик для запуска программы
        self.tree.bind("<Double-1>", self.launch_selected)
        
        # Кнопка запуска
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Запустить выбранную программу", 
                  command=self.launch_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.program_folder.get())
        if folder:
            self.program_folder.set(folder)
            self.load_programs()
    
    def load_programs(self):
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        folder = self.program_folder.get()
        if not os.path.exists(folder):
            messagebox.showerror("Ошибка", "Указанная папка не существует!")
            return
        
        # Ищем исполняемые файлы
        exe_extensions = ('.exe', '.bat', '.cmd', '.msi')
        programs = []
        
        for root_dir, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(exe_extensions):
                    full_path = os.path.join(root_dir, file)
                    programs.append((file, full_path))
        
        # Добавляем программы в список
        for name, path in programs:
            # Получаем иконку
            icon = extract_icon(path)
            if icon:
                self.icons[path] = icon  # Сохраняем ссылку на иконку
                item = self.tree.insert("", "end", image=icon, values=(name, path))
            else:
                item = self.tree.insert("", "end", values=(name, path))
    
    def launch_selected(self, event=None):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите программу для запуска!")
            return
        
        item_values = self.tree.item(selected_item)
        program_path = item_values['values'][1]
        
        try:
            # Запускаем программу
            os.startfile(program_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить программу:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProgramLauncher(root)
    root.mainloop()