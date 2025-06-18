import os
import sys
import time
import random
import platform
import datetime
import threading
import webbrowser
import psutil
import requests
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import tkinterweb as tkweb
import webview
import torch
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QFormLayout
from PyQt6.QtCore import Qt
import numpy as np
import GPUtil
import warp as wp
from numba import jit, njit
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import ctypes
import sys

def check_system_resources():
    try:
        system = platform.system()
        if system == "Windows":
            try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except: pass
        elif system == "Linux": ctk.set_widget_scaling(0.95)
        if sys.maxsize <= 2**32: ctk.set_default_color_theme("green")
    except Exception as e: print(f"System check error: {e}")

check_system_resources()

class ResourceManager:
    _instance = _cache = None
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_image(cls, path, size=None):
        key = f"{path}_{size}" if size else path
        if key not in cls._cache:
            try:
                from PIL import Image, ImageTk
                img = Image.open(path)
                if size: img.thumbnail(size)
                cls._cache[key] = ImageTk.PhotoImage(img)
            except Exception as e: print(f"Image load error: {e}")
        return cls._cache.get(key)
    
    @classmethod
    def clear_cache(cls): cls._cache.clear()

# GPU оптимизация
def request_high_performance_gpu():
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
            class D3DPRESENT_PARAMETERS(ctypes.Structure): _fields_ = []
            d3d9 = ctypes.WinDLL('d3d9')
            d3d = d3d9.Direct3DCreate9(0x900)
            if d3d:
                params, dev, result = D3DPRESENT_PARAMETERS(), ctypes.c_void_p(), ctypes.c_int()
                ctypes.windll.d3d9.Direct3D9Device_CreateDevice(d3d, 0, 1, 0, 0x40, ctypes.byref(params), ctypes.byref(dev))
                print("[INFO] Устройство Direct3D создано — GPU используется.")
        except Exception as e: print(f"[WARNING] Не удалось активировать NVIDIA GPU: {e}")

request_high_performance_gpu()

# Настройки устройства
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
torch.backends.cudnn.benchmark = device.type == 'cuda'

# Оптимизированные операции
class OptimizedTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer, self._buffer_limit = [], 1000
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._flush_buffer)
        self._update_timer.start(100)
    
    def appendOptimized(self, text):
        self._buffer.append(text)
        if len(self._buffer) > self._buffer_limit: self._flush_buffer()
    
    def _flush_buffer(self):
        if self._buffer:
            self.append('\n'.join(self._buffer))
            self._buffer.clear()
            self.moveCursor(QTextCursor.MoveOperation.End)

@njit(fastmath=True, parallel=True)
def numba_optimized_operations(data):
    result = np.zeros(data.shape[0])
    for i in range(data.shape[0]):
        result[i] = np.sqrt(data[i,0]**2 + data[i,1]**2 + data[i,2]**2)
    return result

# Кэширование документов
class CachedDocumentProcessor:
    _cache = {}
    @classmethod
    def process_document(cls, filename, content):
        if filename not in cls._cache:
            cls._cache[filename] = f"Processed: {content[:100]}..." if content else "Empty"
        return cls._cache[filename]

# Вспомогательные функции
def compute_values(s):
    from multiprocessing import Pool, cpu_count
    with Pool(cpu_count()) as pool:
        return pool.map(lambda x: x[0]+x[1], [(1,v) for v in np.asarray(s)])

def load_image(path, subsample=None):
    if path not in image_cache:
        image = tk.PhotoImage(file=path)
        image_cache[path] = image.subsample(*subsample) if subsample else image
    return image_cache[path]

# Warp инициализация
wp.init()
LARGE_FONT = ("Verdana", 15)
num_points = 1024

@wp.kernel
def length(points: wp.array(dtype=wp.vec3), lengths: wp.array(dtype=float)):
    tid = wp.tid()
    lengths[tid] = wp.length(points[tid])

points = wp.array(np.random.rand(num_points,3).astype(np.float32), dtype=wp.vec3)
lengths = wp.zeros(num_points, dtype=float)
wp.launch(kernel=length, dim=len(points), inputs=[points, lengths])
wp.synchronize()
print(lengths)

# Эмулятор CPU
@jit(nopython=True)
def execute(memory, acc, pc, plen):
    while pc < plen:
        instr = memory[pc]
        if instr == 1: acc += memory[pc+1]; pc += 2
        elif instr == 0: break
        else: pc += 1
    return acc, pc

class SimpleCPU:
    def __init__(self, mem_size=256):
        self.memory = np.zeros(mem_size, dtype=np.uint8)
        self.accumulator = self.program_counter = 0
    
    def execute_program(self, program):
        self.memory[:len(program)] = program
        self.accumulator, self.program_counter = execute(self.memory, self.accumulator, self.program_counter, len(program))
    
    def reset(self):
        self.accumulator = self.program_counter = 0
        self.memory[:] = 0

def optimized_operations():
    dtype = torch.float16 if device.type == 'cuda' else torch.float32
    return torch.norm(torch.rand(1024,3,device=device,dtype=dtype), p=2, dim=1)

# Data classes
@dataclass
class Process:
    pid: int
    name: str
    priority: int = 1
    status: str = "ready"
    memory_usage: int = 0
    created_at: float = field(default_factory=time.time)
    parent_pid: Optional[int] = None
    children: List[int] = field(default_factory=list)

@dataclass
class MemoryBlock:
    address: int
    size: int
    process_pid: Optional[int] = None
    is_free: bool = True

# Main
if __name__ == "__main__":
    start = time.time()
    try:
        data = parallel_processing()
        optimized_operations()
        check_hardware_state()
    except Exception as e: print(f"Error: {e}")
    finally: print(f"Total time: {time.time()-start:.4f} seconds")

ctk.set_appearance_mode("dark")  # Темная тема
ctk.set_default_color_theme("blue")  # Синяя цветовая схема

class DraggableWindow:
    def __init__(self, parent, title="Window", width=10, height=10):
        self.parent = parent
        self.window = ctk.CTkFrame(parent, width=width, height=height, corner_radius=10)
        self.window.place(x=100, y=100)  # Начальная позиция
        self.is_dragging = False
        
        # Заголовок окна
        self.title_bar = ctk.CTkFrame(self.window, height=30, fg_color="#2d2d2d")
        self.title_bar.pack(fill="x")
        ctk.CTkLabel(self.title_bar, text=title, font=("Arial", 12)).pack(side="left", padx=5)
        
        # Кнопка закрытия
        close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, command=self.close)
        close_btn.pack(side="right")
        
        # Содержимое окна
        self.content = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        self.content.pack(fill="both", expand=True, padx=1, pady=(3,1))
        
        # Drag & Drop
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
    
    def start_move(self, event):
        self.is_dragging = True
        self._x = event.x
        self._y = event.y
    
    def on_drag(self, event):
        if self.is_dragging:
            x = self.window.winfo_x() + (event.x - self._x)
            y = self.window.winfo_y() + (event.y - self._y)
            self.window.place(x=x, y=y)
    
    def stop_move(self, event):
        self.is_dragging = False
    
    def close(self):
        self.window.destroy()

class DraggableFileWindow:
    def __init__(self, parent, filename, content, file_manager):
        self.parent = parent
        self.filename = filename
        self.file_manager = file_manager
        
        # Создаем окно файла
        self.window = ctk.CTkToplevel(parent)
        self.window.title(filename)
        self.window.geometry("400x300")
        self.window.resizable(True, True)
        self.window.overrideredirect(True)  # Убираем стандартную рамку окна
        
        # Заголовок окна с именем файла
        self.title_bar = ctk.CTkFrame(self.window, height=30, fg_color="#2d2d2d")
        self.title_bar.pack(fill="x")
        
        ctk.CTkLabel(self.title_bar, text=filename, font=("Arial", 12)).pack(side="left", padx=5)
        
        # Кнопки управления
        close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, command=self.close)
        close_btn.pack(side="right")
        
        # Содержимое файла
        self.content_frame = ctk.CTkFrame(self.window)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_area = tk.Text(self.content_frame, font=("Arial", 12), wrap="word")
        self.text_area.pack(fill="both", expand=True)
        self.text_area.insert("1.0", content)
        
        # Панель инструментов
        self.toolbar = ctk.CTkFrame(self.window)
        self.toolbar.pack(fill="x", padx=5, pady=2)
        
        save_btn = ctk.CTkButton(self.toolbar, text="Сохранить", width=80, command=self.save_file)
        save_btn.pack(side="left", padx=5)
        
        # Настройки перемещения окна
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_drag)
        self.window.bind("<ButtonRelease-1>", self.stop_move)
        
        # Запрещаем закрытие окна при клике вне его
        self.window.attributes("-topmost", True)  # Окно всегда поверх других
        self.window.bind("<FocusOut>", lambda e: self.window.lift())  # Возвращаем фокус
        
        self._x = 0
        self._y = 0
        self.is_dragging = False
    
    def start_move(self, event):
        self.is_dragging = True
        self._x = event.x
        self._y = event.y
    
    def on_drag(self, event):
        if self.is_dragging:
            x = self.window.winfo_x() + (event.x - self._x)
            y = self.window.winfo_y() + (event.y - self._y)
            self.window.geometry(f"+{x}+{y}")
    
    def stop_move(self, event):
        self.is_dragging = False
    
    def save_file(self):
        content = self.text_area.get("1.0", "end-1c")
        self.file_manager.save_file(self.filename, content)
        messagebox.showinfo("Сохранено", f"Файл {self.filename} успешно сохранен", parent=self.window)
    
    def close(self):
        self.window.destroy()

class QfoxKernel:
    def __init__(self):
        self.version = "QfoxKernel 1.0"
        self.uptime = 0
        self.processes = []
        self.filesystem = {
            "~1:": {"Documents": [], "Pictures": [], "Downloads": []},
            "~2:": {"Games": [], "Music": []}
        }
    
    def start_process(self, name):
        self.processes.append(name)
    
    def kill_process(self, name):
        if name in self.processes:
            self.processes.remove(name)
    
    def update_uptime(self):
        while True:
            self.uptime += 1
            time.sleep(1)

# Основной класс ОС
class CosmicOS:
    def __init__(self):
        self.kernel = QfoxKernel()
        self.root = ctk.CTk()
        self.root.title("CosmicOS")
        self.root.geometry("1366x768")
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="circle")
        
        # Анимация загрузки
        self.boot_animation()
        
        # Основной интерфейс
        self.setup_desktop()
        
        # Запуск фоновых процессов
        threading.Thread(target=self.kernel.update_uptime, daemon=True).start()
    
    def boot_animation(self):
        self.root.withdraw()
        self.boot = ctk.CTkToplevel(self.root)
        self.boot.attributes("-fullscreen", True)
        self.boot.overrideredirect(True)
        self.boot.configure(fg_color="#000000")  # Черный фон
        self.boot.grab_set()
        self.boot.config(cursor="none")
    
        # Центральный контейнер
        center_frame = ctk.CTkFrame(self.boot, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Логотип с анимацией
        self.logo = ctk.CTkLabel(
            center_frame, 
            text="🌀", 
            font=("Arial", 72),
            text_color="#ffffff"
        )
        self.logo.pack(pady=20)
        
        # Текст загрузки
        ctk.CTkLabel(
            center_frame,
            text="CosmicOS",
            font=("Arial", 36, "bold"),
            text_color="#ffffff"
        ).pack()
        
        # Прогресс-бар в стиле macOS
        self.progress = ctk.CTkProgressBar(
            center_frame,
            width=300,
            height=4,
            progress_color="#007AFF",
            fg_color="#484848"
        )
        self.progress.pack(pady=30)
        self.progress.set(0)
        
        # Запуск анимации загрузки
        self.loading_stage = 0
        self.update_progress()
    
    def update_progress(self):
        stages = [0.49, 0.59, 0.69, 0.89, 1.0]
        
        if self.loading_stage < len(stages):
            target = stages[self.loading_stage]
            current = self.progress.get()
            
            if current < target:
                self.progress.set(current + 0.01)
                self.boot.after(20, self.update_progress)
            else:
                self.loading_stage += 1
                self.boot.after(50, self.update_progress)
        else:
            self.boot.destroy()
            self.root.deiconify()  
            self.root.focus_set()

    # Виртуальная файловая система
        self.virtual_filesystem = {
            "Documents": {},
            "Downloads": {},
            "Pictures": {}
        }
        
        # Открытые файлы
        self.open_files = {}
        
        # Текущий рабочий каталог
        self.current_directory = "Documents"

    def create_file(self, filename=None, content=None, filetype="txt", show_window=True):
        """Создает файл и автоматически открывает его в новом окне"""
        if filename is None:
            filename = f"Новый файл {len(self.virtual_filesystem[self.current_directory])+1}.{filetype}"
        
        if content is None:
            content = f"Файл создан: {datetime.datetime.now()}\nЭто файл, созданный в CosmicOS\n"
        
        # Сохраняем файл в виртуальной ФС
        self.virtual_filesystem[self.current_directory][filename] = {
            "content": content,
            "created": datetime.datetime.now(),
            "modified": datetime.datetime.now(),
            "type": filetype
        }
        
        # Автоматически открываем файл в новом окне
        if show_window:
            self.open_file_window(filename)
        
        return filename

    def open_file_window(self, filename):
        """Открывает файл в новом перемещаемом окне"""
        if filename in self.virtual_filesystem[self.current_directory]:
            content = self.virtual_filesystem[self.current_directory][filename]["content"]
            if filename not in self.open_files:
                self.open_files[filename] = DraggableFileWindow(
                    self.root, 
                    filename, 
                    content,
                    self
                )
            else:
                self.open_files[filename].window.lift()
    
    def save_file(self, filename, content):
        """Сохраняет содержимое файла"""
        if filename in self.virtual_filesystem[self.current_directory]:
            self.virtual_filesystem[self.current_directory][filename].update({
                "content": content,
                "modified": datetime.datetime.now()
            })
            return True
        return False

    def show_file_explorer(self):
        """Показывает проводник с файлами"""
        explorer = DraggableWindow(self.desktop, title="Проводник", width=600, height=400)
    
        # Дерево файлов
        tree_frame = ctk.CTkFrame(explorer.content)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
        # Создаем Treeview
        tree = ttk.Treeview(tree_frame)
        tree.pack(fill="both", expand=True, side="left")
    
        # Заполняем дерево файлами
        for dir_name, files in self.virtual_filesystem.items():
            dir_node = tree.insert("", "end", text=dir_name, values=[dir_name])
        for filename in files:
            tree.insert(dir_node, "end", text=filename, values=[filename])
    
            # Кнопка создания файла
            btn_frame = ctk.CTkFrame(explorer.content)
            btn_frame.pack(fill="x", padx=5, pady=5)
    
            create_btn = ctk.CTkButton(
                  btn_frame, 
                  text="Создать файл", 
                  command=lambda: self.create_file(show_window=True)
            )
            create_btn.pack(side="left", padx=5)

    def on_double_click(event):
        try:
           selected_item = tree.selection()
           if not selected_item:
              return
            
              selected_item = selected_item[0]
              item_data = tree.item(selected_item)
        
           if tree.parent(selected_item):
               filename = item_data["text"]
               directory = tree.item(tree.parent(selected_item))["text"]
            
               if directory in self.virtual_filesystem and filename in self.virtual_filesystem[directory]:
                   self.open_file_window(filename)
        except Exception as e:
            print(f"Error opening file: {e}")

    
    # Двойной клик для открытия файла
    def on_double_click(event):
        # Получаем выбранный элемент
        selected_item = explorer.tree.selection()[0]
        item_data = explorer.tree.item(selected_item)
        
        # Проверяем, является ли элемент файлом (имеет родителя)
        if explorer.tree.parent(selected_item):  # Если у элемента есть родитель - это файл
            filename = item_data["text"]
            directory = explorer.tree.item(explorer.tree.parent(selected_item))["text"]
            
            # Проверяем, существует ли файл в виртуальной файловой системе
            if directory in self.virtual_filesystem and filename in self.virtual_filesystem[directory]:
                self.open_file_window(filename)
    
            # Привязываем обработчик двойного клика
            explorer.tree.bind("<Double-1>", on_double_click)    

    def update_clock(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%a, %d %b")
        self.clock.configure(text=f"{time_str} • {date_str}")

        battery_info = psutil.sensors_battery()
        if battery_info and hasattr(battery_info, "percent"):
            battery_percent = battery_info.percent
            charging = "⚡" if battery_info.power_plugged else "⚡🔋"
            self.battery.configure(text=f"{charging} {battery_percent}%")
        else:
            self.battery.configure(text=f" ⚡🔋 {random.randint(10, 100)}%")        
            self.root.after(1000, self.update_clock)
    
    def setup_desktop(self):
        # Фон рабочего стола
        self.desktop = ctk.CTkFrame(
            self.root, 
            fg_color=("#f0f0f0", "#1a1a2e")  # Светлый/темный в зависимости от темы
        )
        self.desktop.pack(fill="both", expand=True)
        
        # Панель задач в стиле macOS (Dock)
        self.dock = ctk.CTkFrame(
            self.root, 
            height=70, 
            fg_color=("#f0f0f0", "#252525"),
            corner_radius=20
        )
        self.dock.pack(fill="x", side="bottom", padx=50, pady=10)
        self.dock.pack_propagate(False)
        
        # Центрированные иконки в Dock
        dock_icons = ctk.CTkFrame(self.dock, fg_color="transparent")
        dock_icons.pack(expand=True)
        
        apps = [
            ("Меню", "🌀", self.open_start_menu),
            ("Проводник", "📁", self.open_file_explorer),
            ("Браузер", "🌐", self.open_browser),
            ("Текстовый редактор", "📝", self.open_text_editor),
            ("Терминал", "⌨", self.open_terminal),
        ]
        
        for name, icon, cmd in apps:
            btn = ctk.CTkButton(
                dock_icons,
                text=icon,
                width=50,
                height=50,
                font=("Arial", 20),
                fg_color="transparent",
                hover_color=("#e0e0e0", "#353535"),
                command=cmd
            )
            btn.pack(side="left", padx=5)
        
        # Меню статуса (верхняя панель)
        self.menu_bar = ctk.CTkFrame(
            self.root,
            height=25,
            fg_color=("#f0f0f0", "#252525"),
            corner_radius=0
        )
        self.menu_bar.pack(fill="x", side="top")
        
        # Логотип Apple-like
        apple_menu = ctk.CTkLabel(
            self.menu_bar,
            text="🌀",
            font=("Arial", 16),
            text_color=("#000000", "#ffffff")
        )
        apple_menu.pack(side="left", padx=15)
        
        # Время и дата
        self.clock = ctk.CTkLabel(
            self.menu_bar,
            text="",
            font=("Arial", 13),
            text_color=("#000000", "#ffffff")
        )
        self.clock.pack(side="right", padx=15)
        
        # Батарея
        self.battery = ctk.CTkLabel(
            self.menu_bar,
            text="",
            font=("Arial", 13),
            text_color=("#000000", "#ffffff")
        )
        self.battery.pack(side="right", padx=5)
        
        self.update_clock()
        
        # Виджет системной информации
        self.setup_widgets()
    
    def setup_widgets(self):
        # Виджет системной информации
        sys_info = ctk.CTkFrame(self.desktop, width=200, height=150, fg_color=("#ffffff", "#16213e"), corner_radius=10)
        sys_info.place(x=20, y=20)
        
        ctk.CTkLabel(sys_info, text="System Info", font=("Arial", 14, "bold")).pack(pady=5)
        
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        
        ctk.CTkLabel(sys_info, text=f"CPU: {cpu_usage}%").pack()
        ctk.CTkLabel(sys_info, text=f"RAM: {ram_usage}%").pack()
        ctk.CTkLabel(sys_info, text=f"Uptime: {self.kernel.uptime}s").pack()

    def open_start_menu(self):
        menu = DraggableWindow(self.desktop, title="Меню CosmicOS", width=400, height=500)
        # Вкладки меню
        tabs = ctk.CTkTabview(menu.content)
        tabs.pack(fill="both", expand=True, padx=5, pady=5)
        tabs.add("Приложения")
        tabs.add("Файлы")
        tabs.add("Система")        

        # Вкладка "Файлы"
        files_frame = tabs.tab("Файлы")
        btn = ctk.CTkButton(files_frame, text="Создать файл", command=self.create_file)
        btn.pack(fill="x", padx=10, pady=5)

        # Вкладка "Приложения"
        apps_frame = tabs.tab("Приложения")
        apps = [
           ("Проводник", self.open_file_explorer),
           ("Терминал", self.open_terminal),
           ("Браузер", self.open_browser),
           ("Текстовый редактор", self.open_text_editor),
           ("Калькулятор", self.open_sub_window_calculator)
        ]
        for name, cmd in apps:
            btn = ctk.CTkButton(apps_frame, text=name, command=cmd)
            btn.pack(fill="x", padx=10, pady=5)
        
        sys_frame = tabs.tab("Система")
        sys_tools = [
           ("Диспетчер задач", self.open_task_manager),
           ("Информация о системе", self.show_system_info),
           ("Выключить", self.shutdown)
        ]
        for name, cmd in sys_tools:
            btn = ctk.CTkButton(sys_frame, text=name, command=cmd)
            btn.pack(fill="x", padx=10, pady=5)
    
    def launch_app(self, app):
        if app == "📁":
            self.open_file_explorer()
        elif app == "🌐":
            self.open_browser()
        elif app == "📝":
            self.open_text_editor()
        elif app == "⌨":
            self.open_terminal()
            
    # ===== Приложения =====
    def open_file_explorer(self):
        explorer = DraggableWindow(self.desktop, title="Проводник", width=800, height=600)

        # Панель инструментов
        toolbar = ctk.CTkFrame(explorer.content)
        toolbar.pack(fill="x", padx=5, pady=5)

        back_btn = ctk.CTkButton(toolbar, text="←", width=30)
        back_btn.pack(side="left", padx=2)

        forward_btn = ctk.CTkButton(toolbar, text="→", width=30)
        forward_btn.pack(side="left", padx=2)

        path_entry = ctk.CTkEntry(toolbar)
        path_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Дерево файлов
        tree_frame = ctk.CTkFrame(explorer.content)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tree = ttk.Treeview(tree_frame)
        tree.pack(fill="both", expand=True, side="left")

       # Заполнение дерева
        filesystem = {"~1:": ["Documents", "Pictures", "Music"], "~2:": ["Backup", "Projects"]}
        for drive in filesystem:
            drive_id = tree.insert("", "end", text=drive, values=[drive])
            for folder in filesystem[drive]:
                tree.insert(drive_id, "end", text=folder, values=[f"{drive}\\{folder}"])

        self.kernel.start_process("File Explorer")
    
    def open_terminal(self):
        # Создаем DraggableWindow для терминала
        terminal = DraggableWindow(self.desktop, title="Терминал CosmicOS", width=700, height=500)

        # Текстовая область
        output = tk.Text(terminal.content, bg="black", fg="white", font=("Consolas", 12))
        output.pack(fill="both", expand=True, padx=5, pady=5)

        # Панель ввода команд
        input_frame = ctk.CTkFrame(terminal.content)
        input_frame.pack(fill="x", padx=5, pady=5)

        prompt = ctk.CTkLabel(input_frame, text=">", width=10)
        prompt.pack(side="left")

        cmd_entry = ctk.CTkEntry(input_frame)
        cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Доступные команды (20 штук)
        commands = {
            "help": "Список команд",
            "clear": "Очистить терминал",
            "ls": "Показать файлы",
            "cd": "Сменить директорию",
            "mkdir": "Создать папку",
            "neofetch": "Информация о системе",
            "time": "Текущее время",
            "date": "Текущая дата",
            "uptime": "Время работы ОС",
            "ps": "Запущенные процессы",
            "kill": "Завершить процесс",
            "echo": "Вывести текст",
            "calc": "Открыть калькулятор",
            "browser": "Открыть браузер",
            "shutdown": "Выключить ОС",
            "reboot": "Перезагрузить ОС",
            "python": "Запустить Python",
            "ipconfig": "Информация о сети",
            "ping": "Проверить соединение",
            "exit": "Закрыть терминал"
        }
        
        def run_command(event=None):
            cmd = cmd_entry.get()
            cmd_entry.delete(0, "end")
            output.insert("end", f" > {cmd}\n")
            
            if cmd == "help":
                output.insert("end", "Доступные команды:\n")
                for name, desc in commands.items():
                    output.insert("end", f"  {name}: {desc}\n")
            elif cmd == "clear":
                output.delete(1.0, "end")
            elif cmd == "ls":
                output.insert("end", "~1:\n~2:\n")
            elif cmd == "neofetch":
                output.insert("end", f"CosmicOS (Kernel: {self.kernel.version})\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%\n")
            elif cmd == "time":
                output.insert("end", f"Время: {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            elif cmd == "date":
                output.insert("end", f"Дата: {datetime.datetime.now().strftime('%d/%m/%Y')}\n")
            elif cmd == "uptime":
                output.insert("end", f"Время работы: {self.kernel.uptime} сек\n")
            elif cmd == "ps":
                output.insert("end", "Процессы:\n")
                for proc in self.kernel.processes:
                    output.insert("end", f"- {proc}\n")
            elif cmd == "calc":
                self.open_sub_window_calculator()
                output.insert("end", "Калькулятор запущен\n")
            elif cmd == "browser":
                self.open_browser()
                output.insert("end", "Браузер запущен\n")
            elif cmd == "shutdown":
                self.shutdown()
            elif cmd == "exit":
                terminal.destroy()
            else:
                output.insert("end", f"Команда '{cmd}' не найдена. Введите 'help'.\n")
            
            output.see("end")
        
        cmd_entry.bind("<Return>", run_command)
        output.insert("end", "Добро пожаловать в терминал CosmicOS!\nВведите 'help' для списка команд.\n")
        
        self.kernel.start_process("Terminal")
    
    def open_browser(self):        
        try:
           # Используем webview для создания встроенного браузера          
           webview.create_window("CosmicBrowser", "https://google.com")
           webview.start()
        except Exception as e:
           # Если webview недоступен, используем системный браузер
           webbrowser.open("https://google.com")

        self.kernel.start_process("Browser")
    
    def open_text_editor(self):
        editor = DraggableWindow(self.desktop, title="Текстовый редактор", width=800, height=600)
        text_area = tk.Text(editor.content, font=("Arial", 12))
        text_area.pack(fill="both", expand=True, padx=5, pady=5)
    
        menu = tk.Menu(editor.content)
        editor.content.configure(menu = menu)  # Используем configure вместо config
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Новый")
        file_menu.add_command(label="Открыть")
        file_menu.add_command(label="Сохранить")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=editor.close)
        menu.add_cascade(label="Файл", menu=file_menu)
    
        self.kernel.start_process("Text Editor")
    
    def open_sub_window_calculator(self):
        # Создаем окно калькулятора
        calc = DraggableWindow(self.desktop, title="Калькулятор", width=300, height=400)
    
        # Создаем Tabview для вкладок калькулятора
        tab_control = ctk.CTkTabview(calc.content)
        tab_control.pack(expand=True, fill='both')
    
        # Вкладка текстового калькулятора
        text_tab = tab_control.add("Text Calculator")
        entry = ctk.CTkEntry(text_tab, width=200)
        entry.pack(pady=20)
    
        explanation_label = ctk.CTkLabel(text_tab, text="", wraplength=280)
        explanation_label.pack(pady=10)
        
        def calculate():  
            try:
                expression = entry.get()
                result = eval(expression)
                entry.delete(0, tk.END)
                entry.insert(0, str(result))
                explanation_label.configure(text=f"Решение: {expression} = {result}")
            except Exception as e:
                entry.delete(0, tk.END)
                entry.insert(0, "Ошибка")
                explanation_label.configure(text=f"Ошибка: {str(e)}")
        
        ctk.CTkButton(text_tab, text='Calculate', command=calculate).pack(pady=10)

        # Вкладка кнопочного калькулятора
        button_tab = tab_control.add("Button Calculator")
        button_frame = ctk.CTkFrame(button_tab)
        button_frame.pack(pady=10)
        
        buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+')
        ]
        
        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                btn = ctk.CTkButton(
                    button_frame,
                    text=btn_text,
                    width=50,
                    height=50,
                    command=lambda t=btn_text: self.on_calc_button_click(t, entry, calculate)
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
        
        clear_frame = ctk.CTkFrame(button_tab)
        clear_frame.pack(pady=5)
        
        ctk.CTkButton(
            clear_frame,
            text='C',
            width=100,
            command=lambda: entry.delete(0, tk.END)
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            clear_frame,
            text='CE',
            width=100,
            command=lambda: [entry.delete(0, tk.END), explanation_label.configure(text="")]
        ).pack(side='left', padx=5)
        
        self.kernel.start_process("Calculator")
    
    def on_calc_button_click(self, text, entry, calculate_func):
        if text == '=':
            calculate_func()
        else:
            entry.insert(tk.END, text)
    
    def open_task_manager(self):
        # Создаем DraggableWindow для диспетчера задач
        task_manager = DraggableWindow(self.desktop, title="Диспетчер задач", width=600, height=400)

        # Таблица процессов
        tree = ttk.Treeview(task_manager.content, columns=("Name", "PID", "CPU", "Memory"), show="headings")
        tree.heading("Name", text="Имя процесса")
        tree.heading("PID", text="PID")
        tree.heading("CPU", text="ЦП (%)")
        tree.heading("Memory", text="Память (%)")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Заполнение таблицы данными о процессах
        for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
               pid = process.info['pid']
               name = process.info['name']
               cpu = round(process.info['cpu_percent'], 2)
               memory = round(process.info['memory_percent'], 2)
               tree.insert("", "end", values=(name, pid, cpu, memory))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
               continue

               self.kernel.start_process("Task Manager")
    
    def kill_selected_process(self, tree):
        selected = tree.selection()
        if selected:
            item = tree.item(selected)
            proc_name = item["values"][1]
            self.kernel.kill_process(proc_name)
            tree.delete(selected)        
    
    def show_system_info(self):
        info = f"""
        CosmicOS 
        -------------------------
        Ядро: {self.kernel.version}
        Время работы: {self.kernel.uptime} сек
        Процессы: {len(self.kernel.processes)}
        
        Система: CosmicOS v.1.0
        Процессор: {platform.processor()}
        Память: {psutil.virtual_memory().percent}% использовано
        """
        messagebox.showinfo("Информация о системе", info.strip())
    
    def shutdown(self):
        if messagebox.askyesno("Выключение", "Вы уверены, что хотите выключить CosmicOS?"):
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    os = CosmicOS()
    os.run()
