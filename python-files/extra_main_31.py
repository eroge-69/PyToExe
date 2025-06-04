import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import io, sys, subprocess, threading, tempfile, os, json, math, ast
from PIL import Image, ImageTk
import numpy as np
# Add these for SVG processing:
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from math import sin, cos, radians, atan2, degrees
import asyncio, httpx, re
import hashlib
import shutil
import time
from rapidfuzz import fuzz, process
# --- Cache Management ---
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".block_connector_cache")

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_file_hash(file_path):
    """Generate a unique hash for the file content"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def cache_file(file_path, project_path=None):
    """Cache a file and return its cache info"""
    ensure_cache_dir()
    
    # Generate cache info
    file_hash = get_file_hash(file_path)
    file_name = os.path.basename(file_path)
    
    # Определяем путь к кешу
    if project_path:
        project_dir = os.path.dirname(project_path)
        project_name = os.path.splitext(os.path.basename(project_path))[0]
        cache_path = os.path.join(project_dir, f"{project_name}.tmp")
    else:
        cache_path = os.path.join(CACHE_DIR, f"{file_hash}_{file_name}")
    
    # Если это проект, обрабатываем tmp файл
    if project_path:
        # Читаем содержимое файла
        with open(file_path, 'rb') as src_file:
            file_content = src_file.read()
        
        # Записываем в tmp файл
        with open(cache_path, 'wb') as tmp_file:
            # Записываем размер имени
            name_bytes = file_name.encode('utf-8')
            tmp_file.write(len(name_bytes).to_bytes(4, 'big'))
            # Записываем имя
            tmp_file.write(name_bytes)
            # Записываем размер содержимого
            tmp_file.write(len(file_content).to_bytes(4, 'big'))
            # Записываем содержимое
            tmp_file.write(file_content)
    
    cache_info = {
        "file_name": file_name,
        "hash": file_hash,
        "cached_path": cache_path,
        "offset": 0,
        "size": os.path.getsize(file_path)
    }
    
    return cache_info

def get_cached_file(cache_info):
    """Get file from cache or return None if not found"""
    if not cache_info or "cached_path" not in cache_info:
        return None
    
    cached_path = cache_info["cached_path"]
    if not os.path.exists(cached_path):
        return None
        
    # Если это обычный кеш, просто возвращаем путь
    if "offset" not in cache_info:
        return cached_path
        
    # Если это tmp файл, извлекаем нужный файл
    try:
        with open(cached_path, 'rb') as tmp_file:
            # Читаем размер имени
            name_size_bytes = tmp_file.read(4)
            if not name_size_bytes:
                return None
            name_size = int.from_bytes(name_size_bytes, 'big')
            
            # Читаем имя файла
            name_bytes = tmp_file.read(name_size)
            if not name_bytes:
                return None
            try:
                file_name = name_bytes.decode('utf-8')
            except:
                return None
            
            # Читаем размер содержимого
            content_size_bytes = tmp_file.read(4)
            if not content_size_bytes:
                return None
            content_size = int.from_bytes(content_size_bytes, 'big')
            
            # Читаем содержимое
            file_content = tmp_file.read(content_size)
            if not file_content:
                return None
            
            # Создаем файл в той же директории, что и проект
            project_dir = os.path.dirname(cached_path)
            file_path = os.path.join(project_dir, file_name)
            
            # Записываем содержимое в файл
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return file_path
    except Exception as e:
        print(f"Error extracting file from tmp: {e}")
        return None

def save_cache_info(workspace, cache_info):
    """Save cache info to workspace state"""
    if not hasattr(workspace, "file_cache"):
        workspace.file_cache = {}
    
    if cache_info:
        # Используем хеш файла как ключ вместо оригинального пути
        workspace.file_cache[cache_info["hash"]] = cache_info

def load_cache_info(workspace, file_hash):
    """Load cache info from workspace state"""
    if not hasattr(workspace, "file_cache"):
        workspace.file_cache = {}
    
    return workspace.file_cache.get(file_hash)

# --- MoveController для плавного перемещения блока ---
class MoveController:
    def __init__(self, block):
        self.block = block
    def __getitem__(self, key):
        if key == "x":
            return self.block.world_x
        elif key == "y":
            return self.block.world_y
        else:
            raise KeyError("Invalid move key: " + key)
    def __setitem__(self, key, value):
        try:
            target = float(value)
        except ValueError:
            raise ValueError("Значение должно быть числом")
        duration = 1.0  # длительность перемещения по умолчанию (в секундах)
        if key == "x":
            self.block.move_to(target, self.block.world_y, duration)
        elif key == "y":
            self.block.move_to(self.block.world_x, target, duration)
        else:
            raise KeyError("Invalid move key: " + key)

# --- Кастомные диалоги ---
class CustomStringDialog(simpledialog.Dialog):
    def __init__(self, parent, title, prompt, initialvalue=""):
        self.prompt = prompt; self.initialvalue = initialvalue; self.result = None
        super().__init__(parent, title)
    def body(self, master):
        master.configure(bg="#2B2B2B")
        if hasattr(master, 'wm_resizable'): master.wm_resizable(True, True)
        tk.Label(master, text=self.prompt, bg="#2B2B2B", fg="#FFD700", font=("Consolas", 10))\
          .grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry = tk.Entry(master, bg="#1E1E1E", fg="#FFD700", insertbackground="#FFD700", font=("Consolas", 10))
        self.entry.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        master.grid_rowconfigure(1, weight=1); master.grid_columnconfigure(0, weight=1)
        self.entry.insert(0, self.initialvalue)
        return self.entry
    def apply(self):
        self.result = self.entry.get()

def ask_custom_string(parent, title, prompt, initialvalue=""):
    return CustomStringDialog(parent, title, prompt, initialvalue).result

class CustomMultiLineDialog(simpledialog.Dialog):
    def __init__(self, parent, title, prompt, initialvalue=""):
        self.prompt = prompt; self.initialvalue = initialvalue; self.result = None
        super().__init__(parent, title)
    def body(self, master):
        master.configure(bg="#2B2B2B")
        if hasattr(master, 'wm_resizable'): master.wm_resizable(True, True)
        tk.Label(master, text=self.prompt, bg="#2B2B2B", fg="#FFD700", font=("Consolas", 10))\
          .pack(padx=5, pady=5, anchor="w")
        self.text = tk.Text(master, bg="#1E1E1E", fg="#FFD700", insertbackground="#FFD700", 
                             font=("Consolas", 10), wrap="word")
        self.text.pack(padx=5, pady=5, fill="both", expand=True)
        self.text.insert("1.0", self.initialvalue)
        return self.text
    def buttonbox(self):
        box = tk.Frame(self, bg="#2B2B2B")
        tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE,
                  bg="#333333", fg="#FFD700", font=("Consolas", 10)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Отмена", width=10, command=self.cancel,
                  bg="#333333", fg="#FFD700", font=("Consolas", 10)).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok); self.bind("<Escape>", self.cancel)
        box.pack()
    def apply(self):
        self.result = self.text.get("1.0", "end-1c")

def ask_custom_multiline(parent, title, prompt, initialvalue=""):
    return CustomMultiLineDialog(parent, title, prompt, initialvalue).result

# --- Инструкции по умолчанию для скриптов ---
DEFAULT_SCRIPT_INSTRUCTIONS = '''# Пример скрипта блока:
# Доступны переменные: prev, self, next, app
#
# Примеры использования:
#   app.connect[(<id1>, <id2>)] = 1
#   value = self["имя_параметра"]
#   self["имя_параметра"] = "новое_значение"
#
# Доп. команды:
#   change['<system_id>']['<параметр>'] = новое значение
#   create['<тип блока>']['<параметр>'] = значение
#       допустимые типы: normal, system, slider, autorun, nodescript, switch, html
#   remove['<system_id>'][любое_значение] = _
#
# Для перемещения:
#    self.move['x'] = значение
#    self.move['y'] = значение
# Контроллеры: create, change, remove, read, store
#
# Пример:
#   print(app.read['id_of_block']['parameter'])
#
# API:
#   GET http://localhost:8080/get_param?system_id=<system_id>&param=<имя_параметра>
#   GET http://localhost:8080/set_param?system_id=<system_id>&param=<имя_параметра>&value=<новое значение>
#
# Работа с файлами:
#   print(app.read_sys_files())  # Вывод списка всех файлов в проекте
#   print(app.read_sys_path())   # Вывод путей к файлам в проекте
#
# Пример вывода файлов:
#   Workspace: Interface 1
#   Block: FileBlock 1
#   File: example.txt
#   Size: 1024 bytes
#   Hash: abc123...
#   ---
#
# Пример вывода путей:
#   Workspace: Interface 1
#   Block: FileBlock 1
#   File: example.txt
#   Temp path: C:\\path\\to\\temp\\file.txt
#   Cache path: C:\\path\\to\\cache\\file.txt
#   ---
'''

# --- Кодовый редактор ---
class CodeEditor(tk.Frame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.linenumbers = tk.Canvas(self, width=40, bg="black")
        self.linenumbers.pack(side="left", fill="y")
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(side="right", fill="both", expand=True)
        self.text = tk.Text(self.text_frame, undo=True, wrap="none",
                            bg="#1E1E1E", fg="#FFD700", insertbackground="#FFD700", font=("Consolas", 10))
        self.text.insert("1.0", text); self.text.edit_reset()
        self.vsb = tk.Scrollbar(self.text_frame, orient="vertical", command=self.text.yview)
        self.hsb = tk.Scrollbar(self.text_frame, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.pack(side="right", fill="y"); self.hsb.pack(side="bottom", fill="x")
        self.text.pack(side="left", fill="both", expand=True)
        for ev, handler in [("<KeyRelease>", self.on_key_release), ("<MouseWheel>", self._on_mousewheel),
                             ("<Button-1>", self.update_linenumbers), ("<Configure>", self.update_linenumbers)]:
            self.text.bind(ev, handler)
        self.text.bind("<Control-z>", lambda e: (self.text.edit_undo(), "break"))
        self.text.bind("<Control-y>", lambda e: (self.text.edit_redo(), "break"))
        self.linenumbers.bind("<Button-1>", self.on_linenumber_click)
        self.folded_regions = {}
        self.update_linenumbers()
    def on_key_release(self, event=None):
        self.update_linenumbers()
    def _on_mousewheel(self, event):
        self.text.yview_scroll(int(-1*(event.delta/120)), "units"); self.update_linenumbers()
        return "break"
    def update_linenumbers(self, event=None):
        self.linenumbers.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None: break
            y = dline[1]; line_number = str(i).split(".")[0]
            self.linenumbers.create_text(2, y, anchor="nw", text=line_number, fill="#FFD700", font=("Consolas", 10))
            line_text = self.text.get(f"{line_number}.0", f"{line_number}.end")
            if line_text.lstrip().startswith(("def ", "if ", "for ", "while ", "class ")):
                self.linenumbers.create_polygon(25, y+5, 35, y+5, 30, y+15, fill="#FFD700", outline="#FFD700", tags=("fold", line_number))
            i = self.text.index(f"{i}+1line")
    def on_linenumber_click(self, event):
        x, y = event.x, event.y
        clicked = self.linenumbers.find_closest(x, y)
        tags = self.linenumbers.gettags(clicked)
        if "fold" in tags: self.toggle_fold(int(tags[1]))
    def toggle_fold(self, start_line):
        index = f"{start_line}.0"
        line_text = self.text.get(index, f"{start_line}.end")
        indent = len(line_text) - len(line_text.lstrip())
        start_index = self.text.index(f"{start_line+1}.0"); end_line = start_line; folded_text = ""
        while True:
            curr_index = self.text.index(f"{end_line+1}.0")
            if curr_index == self.text.index("end-1c"): break
            curr_line = self.text.get(curr_index, f"{curr_index} lineend")
            curr_indent = len(curr_line) - len(curr_line.lstrip())
            if curr_line.strip() == "":
                folded_text += "\n"; end_line += 1; continue
            if curr_indent <= indent: break
            folded_text += curr_line + "\n"; end_line += 1
        if start_line in self.folded_regions:
            placeholder_index = f"{start_line+1}.0"
            self.text.delete(placeholder_index, f"{start_line+1}.end")
            self.text.insert(placeholder_index, self.folded_regions[start_line][1])
            del self.folded_regions[start_line]
        else:
            if folded_text:
                fold_start = f"{start_line+1}.0"; fold_end = f"{end_line+1}.0"
                self.folded_regions[start_line] = (end_line, self.text.get(fold_start, fold_end))
                self.text.delete(fold_start, fold_end); self.text.insert(fold_start, "    ...\n")
        self.update_linenumbers()
    def get_text(self):
        return self.text.get("1.0", "end-1c")

# --- BlockWrapper и обёртки для связи блоков ---

# --- GradientBlock ---
# Класс для создания блоков с градиентным текстом и анимацией
class GradientBlock(tk.Frame):
    def __init__(self, master, text="Градиентный Блок", **kwargs):
        super().__init__(master, bd=3, relief="ridge", bg="#222", **kwargs)
        self.text = text
        self.font_size = 16
        self.text_widget = tk.Text(self, font=("Consolas", self.font_size, "bold"), bg="#1E1E1E", fg="#FFD700", bd=0, highlightthickness=0, wrap="none", state="disabled")
        self.text_widget.pack(fill="both", expand=True, padx=8, pady=8)
        self.colors = self.generate_gradient(len(self.text.replace('\n', '')))
        self.offset = 0
        self.animate()
        self.text_widget.bind("<Double-Button-1>", self.on_double_click)
        self.bind("<ButtonPress-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag_motion)
        self.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.bind("<Button-3>", self.on_right_click)
        self.drag_data = {"x": 0, "y": 0}
        self.world_x = 0
        self.world_y = 0
        self.base_width = 160
        self.base_height = 48

        self.resize_handle = tk.Frame(self, width=12, height=12, bg="#FFD700", cursor="bottom_right_corner")
        self.resize_handle.place(relx=1.0, rely=1.0, anchor="se")
        self.resize_handle.bind("<ButtonPress-1>", self.on_resize_start)
        self.resize_handle.bind("<B1-Motion>", self.on_resizing)
        self.resize_handle.bind("<ButtonRelease-1>", self.on_resize_stop)
        self.resizing = False
        
        # Добавляем атрибуты для сохранения/загрузки
        self.system_id = f"gradient_{id(self)}"
        self.block_type = "gradient"
        self.params = {"text": text, "font_size": self.font_size}
        self.params["width"] = self.base_width
        self.params["height"] = self.base_height
        
        # Добавляем атрибут для плавного перемещения
        self.move = MoveController(self)
        
        # Добавляем атрибут для хранения ID анимации
        self._animation_after_id = None

    def on_right_click(self, event):
        # Dialog for font size
        new_font_size = simpledialog.askinteger("Размер шрифта", "Введите размер шрифта:", 
                                                initialvalue=self.font_size, minvalue=1, maxvalue=72,
                                                parent=self) # Ensure dialog is child of self
        if new_font_size:
            self.font_size = new_font_size
            self.text_widget.config(font=("Consolas", self.font_size, "bold"))
            self.params["font_size"] = self.font_size

        # Dialog for width
        new_width = simpledialog.askfloat("Ширина блока", "Введите новую ширину блока:",
                                          initialvalue=self.base_width, minvalue=20,
                                          parent=self) # Ensure dialog is child of self
        if new_width:
            self.base_width = new_width
            self.params["width"] = self.base_width

        # Dialog for height
        new_height = simpledialog.askfloat("Высота блока", "Введите новую высоту блока:",
                                           initialvalue=self.base_height, minvalue=20,
                                           parent=self) # Ensure dialog is child of self
        if new_height:
            self.base_height = new_height
            self.params["height"] = self.base_height

        # Update block's appearance if width or height changed
        if new_width or new_height or new_font_size: # Check if any value was actually changed
            zoom = getattr(self.master, 'current_scale', 1.0) if hasattr(self.master, 'current_scale') else getattr(self.master, 'zoom', 1.0)
            if zoom == 0:
                zoom = 1.0
            self.update_position_and_size(zoom)
            # If text or font size changed, gradient might need regeneration
            if new_font_size or (self.params.get("text") != self.text): # self.text might be old if changed via double click
                 # Re-generate gradient if text/font changed, similar to on_double_click
                text_length = len(self.text.replace('\n', ''))
                self.colors = self.generate_gradient(text_length)
                self.offset = 0
                if hasattr(self, "_animation_after_id") and self._animation_after_id:
                    self.after_cancel(self._animation_after_id)
                self.animate() # Restart animation

    def set_world_position(self, x, y):
        self.world_x = x
        self.world_y = y

    def update_position_and_size(self, zoom):
        self.place(x=int(self.world_x * zoom), y=int(self.world_y * zoom),
                   width=int(self.base_width * zoom), height=int(self.base_height * zoom))
        self.resize_handle.place(relx=1.0, rely=1.0, anchor="se")

    def on_resize_start(self, event):
        self.resizing = True
        self.resize_start_x = event.x
        self.resize_start_y = event.y
        self.start_width = self.base_width
        self.start_height = self.base_height

    def on_resizing(self, event):
        if not self.resizing:
            return
        dx = event.x - self.resize_start_x
        dy = event.y - self.resize_start_y
        zoom = getattr(self.master, 'current_scale', 1.0) if hasattr(self.master, 'current_scale') else getattr(self.master, 'zoom', 1.0)
        if zoom == 0:
            zoom = 1.0
        new_width = max(60, self.start_width + dx / zoom)
        new_height = max(24, self.start_height + dy / zoom)
        self.base_width = new_width
        self.base_height = new_height
        self.update_position_and_size(zoom)

    def on_resize_stop(self, event):
        self.resizing = False
        self.params["width"] = self.base_width
        self.params["height"] = self.base_height

    def generate_gradient(self, length):
        colors = []
        # Ограничиваем максимальное количество цветов для оптимизации
        max_colors = min(length, 100)  # Ограничиваем до 100 цветов
        for i in range(max_colors):
            # Используем синусоидальную функцию для плавного перехода
            ratio = (math.sin(i / max_colors * 2 * math.pi) + 1) / 2
            r = 255
            g = int(255 * ratio)
            b = 0
            colors.append(f"#{r:02x}{g:02x}{b:02x}")
        return colors

    def animate(self):
        flat_text = self.text.replace('\n', '')
        n = len(flat_text)
        if n == 0:
            return
            
        # Проверяем, что у нас есть достаточно цветов для градиента
        if not hasattr(self, 'colors') or len(self.colors) < 2:
            self.colors = self.generate_gradient(max(100, n))
            
        # Получаем количество цветов в градиенте
        color_count = len(self.colors)
        
        # Устанавливаем постоянную скорость анимации
        # Используем абсолютное смещение во времени вместо смещения относительно длины текста
        current_time = int(time.time() * 1000)  # Текущее время в миллисекундах
        
        # Инициализируем время последнего обновления, если его нет
        if not hasattr(self, 'last_update_time'):
            self.last_update_time = current_time
            self.absolute_offset = 0.0
        
        # Вычисляем прошедшее время с последнего обновления
        elapsed_time = current_time - self.last_update_time
        
        # Обновляем абсолютное смещение (пикселей в секунду)
        animation_speed = 5.0  # символов в секунду
        self.absolute_offset += (animation_speed * elapsed_time) / 1000.0
        
        # Обновляем время последнего обновления
        self.last_update_time = current_time
        
        # Преобразуем абсолютное смещение в индекс цвета
        # Используем модуль для цикличности
        self.offset = int(self.absolute_offset) % color_count
        
        # Обновляем текст с новыми цветами
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        
        # Вставляем текст с применением тегов для цветов
        for i, char in enumerate(self.text):
            if char == '\n':
                self.text_widget.insert("end", char)
                continue
                
            # Вычисляем индекс цвета для текущего символа
            color_index = (i + self.offset) % color_count
            tag_name = f"color_{color_index}"
            
            # Создаем тег, если его еще нет
            if not tag_name in self.text_widget.tag_names():
                self.text_widget.tag_configure(tag_name, foreground=self.colors[color_index])
                
            # Вставляем символ с соответствующим тегом
            self.text_widget.insert("end", char, tag_name)
            
        self.text_widget.config(state="disabled")
        
        # Планируем следующее обновление и сохраняем ID для возможной отмены
        self._animation_after_id = self.after(50, self.animate)  # Обновляем каждые 50 мс для плавности

    def on_double_click(self, event):
        new_text = ask_custom_multiline(self.master, "Изменить надпись", "Введите новый текст:", initialvalue=self.text)
        if new_text:
            self.text = new_text
            self.params["text"] = new_text  # Обновляем параметры для сохранения
            # Сбрасываем флаг анимации при изменении текста
            if hasattr(self, "animation_disabled"):
                self.animation_disabled = False
            # Генерируем новые цвета с ограничением
            text_length = len(new_text.replace('\n', ''))
            self.colors = self.generate_gradient(text_length)
            self.offset = 0
            # Перезапускаем анимацию
            self.deactivate()

    def on_drag_start(self, event):
        """Начало перетаскивания блока"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def on_drag_motion(self, event):
        """Перетаскивание блока"""
        if self.resizing:
            return
            
        # Получаем текущий масштаб из мастера
        zoom = getattr(self.master, 'current_scale', 1.0) if hasattr(self.master, 'current_scale') else getattr(self.master, 'zoom', 1.0)
        if zoom == 0:
            zoom = 1.0
            
        # Вычисляем смещение с учетом масштаба
        dx = (event.x - self.drag_data["x"]) / zoom
        dy = (event.y - self.drag_data["y"]) / zoom
        
        # Обновляем мировые координаты
        self.world_x += dx
        self.world_y += dy
        
        # Обновляем положение блока
        self.update_position_and_size(zoom)
        
        # Обновляем начальные координаты для следующего движения
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def on_drag_stop(self, event):
        """Окончание перетаскивания блока"""
        pass
        
    def move_to(self, target_x, target_y, duration=1.0):
        """Плавное перемещение блока к указанным координатам"""
        start_x, start_y = self.world_x, self.world_y
        dx, dy = target_x - start_x, target_y - start_y
        
        # Количество шагов анимации
        steps = int(duration * 30)  # 30 кадров в секунду
        if steps <= 0:
            steps = 1
            
        def animate_step(step):
            if step > steps:
                return
                
            # Вычисляем текущее положение с использованием функции плавности
            progress = step / steps
            # Функция плавности (ease-in-out)
            smooth_progress = 0.5 - 0.5 * math.cos(math.pi * progress)
            
            # Обновляем положение
            self.world_x = start_x + dx * smooth_progress
            self.world_y = start_y + dy * smooth_progress
            
            # Получаем текущий масштаб
            zoom = getattr(self.master, 'current_scale', 1.0) if hasattr(self.master, 'current_scale') else 1.0
            if zoom == 0:
                zoom = 1.0
                
            # Обновляем положение блока
            self.update_position_and_size(zoom)
            
            # Планируем следующий шаг
            self.after(33, lambda: animate_step(step + 1))
            
        # Запускаем анимацию
        animate_step(0)
    
    # Методы для сериализации/десериализации
    def get_save_data(self):
        """Возвращает данные для сохранения блока"""
        return {
            "type": "gradient",
            "system_id": self.system_id,
            "x": self.world_x,
            "y": self.world_y,
            "width": self.base_width,
            "height": self.base_height,
            "params": self.params
        }
        
    def activate(self):
        # Отключаем анимацию и устанавливаем золотой цвет
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("end", self.text)
        self.text_widget.tag_configure("gold", foreground="#FFD700")
        self.text_widget.tag_add("gold", "1.0", "end")
        self.text_widget.config(state="disabled")
        # Останавливаем анимацию
        if hasattr(self, "_animation_after_id") and self._animation_after_id:
            self.after_cancel(self._animation_after_id)
            self._animation_after_id = None
    
    def deactivate(self):
        # Возобновляем анимацию
        self.offset = 0
        if hasattr(self, "_animation_after_id") and self._animation_after_id:
            self.after_cancel(self._animation_after_id)
        self.animate()
    
    @classmethod
    def from_save_data(cls, master, data):
        """Создает блок из сохраненных данных"""
        # Initialize with default text, will be overwritten if params exist
        block = cls(master, text=data.get("params", {}).get("text", "Градиентный Блок"))
        block.system_id = data.get("system_id", f"gradient_{id(block)}")
        block.world_x = data.get("x", 0)
        block.world_y = data.get("y", 0)
        
        # Restore base_width and base_height from top-level data
        block.base_width = data.get("width", 160)
        block.base_height = data.get("height", 48)
        
        # Restore params dictionary
        loaded_params = data.get("params", {})
        block.text = loaded_params.get("text", block.text) # Update text from params
        block.font_size = loaded_params.get("font_size", block.font_size) # Update font_size from params
        
        # Ensure params in the instance are updated with all loaded values,
        # including width and height from base_width/height
        block.params["text"] = block.text
        block.params["font_size"] = block.font_size
        block.params["width"] = block.base_width
        block.params["height"] = block.base_height

        block.text_widget.config(font=("Consolas", block.font_size, "bold"))
        
        # Update position and size based on loaded values
        zoom = getattr(master, 'current_scale', 1.0) if hasattr(master, 'current_scale') else 1.0
        block.update_position_and_size(zoom)
        
        return block

# Пример добавления блока в интерфейс:
# gradient_block = GradientBlock(root, text="Градиентный Блок")
# gradient_block.pack()

# Пример функции для добавления градиентного блока в интерфейс
def add_gradient_block(app, x=100, y=100, text="Градиентный Блок"):
    block = GradientBlock(app.canvas, text=text)
    block.set_world_position(x, y)
    block.update_position_and_size(getattr(app, 'current_scale', 1.0))
    block.place(x=x, y=y)
    # Если у вас есть список blocks или аналогичная структура:
    if hasattr(app, 'blocks'):
        app.blocks.append(block)
    return block

# Пример вызова (например, при нажатии кнопки):
# add_gradient_block(self, x=200, y=200, text="Привет, мир!")

class BlockWrapper:
    def __init__(self, block):
        super().__setattr__('block', block)
    def __getitem__(self, key):
        key = str(key)
        if key == "system_params": return getattr(self.block, "system_params", {})
        if key in self.block.io_params: return self.block.io_params[key]
        
        if key == "connections":
            for name, val_str in self.block.parameters:
                if name == "connections":
                    try:
                        return ast.literal_eval(val_str)
                    except (ValueError, SyntaxError):
                        print(f"Error parsing 'connections' parameter value: {val_str}. Returning empty list.")
                        return []
            return [] # Should ideally be found if initialized correctly

        for name, value_param in self.block.parameters:
            if name == key:
                try:
                    parsed_value = ast.literal_eval(value_param)
                    if isinstance(parsed_value, (list, dict)): return parsed_value
                except Exception:
                    pass
                return value_param
        return None

    def __setitem__(self, key, value):
        if key == "type":
            self.block.set_block_type(value); return
        if key == "move":
            if isinstance(value, list) and len(value)==3:
                target_x, target_y, duration = value
                if isinstance(target_x, str):
                    if target_x.lower() == "prev":
                        for conn in self.block.app.connections:
                            if self.block.top_circle in conn:
                                other = self.block.app.find_block_by_circle(
                                    conn[0] if conn[1] == self.block.top_circle else conn[1])
                                if other: target_x = other.world_x; break
                        else: target_x = self.block.world_x
                    elif target_x.lower() == "next":
                        for conn in self.block.app.connections:
                            if self.block.bottom_circle in conn:
                                other = self.block.app.find_block_by_circle(
                                    conn[0] if conn[1] == self.block.bottom_circle else conn[1])
                                if other: target_x = other.world_x; break
                        else: target_x = self.block.world_x
                if isinstance(target_y, str):
                    if target_y.lower() == "prev":
                        for conn in self.block.app.connections:
                            if self.block.top_circle in conn:
                                other = self.block.app.find_block_by_circle(
                                    conn[0] if conn[1] == self.block.top_circle else conn[1])
                                if other: target_y = other.world_y; break
                        else: target_y = self.block.world_y
                    elif target_y.lower() == "next":
                        for conn in self.block.app.connections:
                            if self.block.bottom_circle in conn:
                                other = self.block.app.find_block_by_circle(
                                    conn[0] if conn[1] == self.block.bottom_circle else conn[1])
                                if other: target_y = other.world_y; break
                        else: target_y = self.block.world_y
                try: duration = float(duration)
                except Exception: duration = 1.0
                self.block.move_to(target_x, target_y, duration)
            return
        key = str(key)
        if key == "system_params":
            self.block.system_params = value; self.block.update_text(); return
        if key in self.block.io_params:
            self.block.io_params[key] = str(value); return

        param_value_to_set = value
        if key == "connections":
            if isinstance(value, list):
                param_value_to_set = str(value)
            elif isinstance(value, str):
                # Optional: Validate if string is a list representation, for now, store as is
                try:
                    ast.literal_eval(value) # Try parsing to check format
                except (ValueError, SyntaxError):
                    print(f"Warning: Setting 'connections' with a string that is not a valid list representation: {value}")
                    # Decide on behavior: store as is, or default, or raise error. Storing as is for now.
            else:
                print(f"Warning: Invalid type for 'connections' parameter: {type(value)}. Storing as empty list string.")
                param_value_to_set = "[]"
        
        with self.block.param_lock:
            updated = False; new_params = []
            for name, val in self.block.parameters:
                if name == key:
                    new_params.append((name, str(param_value_to_set))); updated = True
                else:
                    new_params.append((name, val))
            if not updated: new_params.append((key, str(param_value_to_set)))
            self.block.parameters = new_params
        if key == "light":
            if str(value) == "1": self.block.activate()
            else: self.block.deactivate()
        self.block.update_text()
        if key == "run" and str(value) == "1":
            self.block.run_script(None, auto_run=True)
    def __getattr__(self, attr):
        if attr == "system_params": return getattr(self.block, "system_params", {})
        if attr == "move": 
            return self.block.move
        return self.__getitem__(attr)
    def __setattr__(self, attr, value):
        if attr in ("block",):
            super().__setattr__(attr, value)
        elif attr == "system_params":
            self.block.system_params = value; self.block.update_text()
        else:
            self.__setitem__(attr, value)
    def __repr__(self):
        return f"BlockWrapper({self.block.block_name})"

class NextBlocksWrapper:
    def __init__(self, block):
        self.block = block
    def _get_blocks(self):
        blocks = []
        for conn in self.block.app.connections:
            if self.block.bottom_circle in conn[:2]:
                other = conn[0] if conn[1] == self.block.bottom_circle else conn[1]
                candidate = self.block.app.find_block_by_circle(other)
                if candidate and candidate != self.block and candidate not in blocks:
                    blocks.append(candidate)
        return blocks
    def __getitem__(self, key):
        return [BlockWrapper(b)[key] for b in self._get_blocks()]
    def __setitem__(self, key, value):
        for b in self._get_blocks():
            BlockWrapper(b)[key] = value
    def __repr__(self):
        return f"NextBlocksWrapper({[b.block_name for b in self._get_blocks()]})"

class PrevBlocksWrapper:
    def __init__(self, block):
        self.block = block
    def _get_blocks(self):
        blocks = []
        for conn in self.block.app.connections:
            if self.block.top_circle in conn[:2]:
                other = conn[0] if conn[1] == self.block.top_circle else conn[1]
                candidate = self.block.app.find_block_by_circle(other)
                if candidate and candidate != self.block and candidate not in blocks:
                    blocks.append(candidate)
        return blocks
    def __getitem__(self, key):
        return [BlockWrapper(b)[key] for b in self._get_blocks()]
    def __setitem__(self, key, value):
        for b in self._get_blocks():
            BlockWrapper(b)[key] = value
    def __repr__(self):
        return f"PrevBlocksWrapper({[b.block_name for b in self._get_blocks()]})"

# --- API-сервер ---
class APIServerHandler(BaseHTTPRequestHandler):
    app = None
    def log_message(self, format, *args): return
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            if parsed.path == '/set_param':
                qs = parse_qs(parsed.query)
                system_id = qs.get("system_id", [None])[0]
                param = qs.get("param", [None])[0]
                value = qs.get("value", [None])[0]
                if None in (system_id, param, value):
                    self.send_response(400); self.end_headers(); self.wfile.write(b"Missing parameters"); return
                block = None
                for ws in APIServerHandler.app.workspaces.values():
                    for b in ws.blocks:
                        for key, val in b.parameters:
                            if key == "system_id" and val == system_id:
                                block = b; break
                        if block: break
                    if block: break
                if block is None:
                    self.send_response(404); self.end_headers(); self.wfile.write(b"Block not found"); return
                BlockWrapper(block)[param] = value
                self.send_response(200); self.end_headers(); self.wfile.write(b"Parameter updated")
            elif parsed.path == '/get_param':
                qs = parse_qs(parsed.query)
                system_id = qs.get("system_id", [None])[0]
                param = qs.get("param", [None])[0]
                if None in (system_id, param):
                    self.send_response(400); self.end_headers(); self.wfile.write(b"Missing parameters"); return
                block = None
                for ws in APIServerHandler.app.workspaces.values():
                    for b in ws.blocks:
                        for key, val in b.parameters:
                            if key == "system_id" and val == system_id:
                                block = b; break
                        if block: break
                    if block: break
                if block is None:
                    self.send_response(404); self.end_headers(); self.wfile.write(b"Block not found"); return
                value = BlockWrapper(block)[param]
                self.send_response(200); self.end_headers(); self.wfile.write(str(value).encode())
            else:
                self.send_response(404); self.end_headers(); self.wfile.write(b"Not Found")
        except Exception as e:
            self.send_response(500); self.end_headers(); self.wfile.write(f"Internal Server Error: {e}".encode())

def start_api_server(app, host="localhost", port=8080):
    APIServerHandler.app = app
    server = HTTPServer((host, port), APIServerHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

# --- ConnectorMapping ---
class ConnectorMapping:
    def __init__(self, app): self.app = app
    def __setitem__(self, key, value):
        if not (isinstance(key, tuple) and len(key)==2):
            raise ValueError("Ключ должен быть кортежем (id1, id2)")
        id1, id2 = key; app = self.app; block1 = block2 = None
        for block in app.blocks:
            if block.id == id1: block1 = block
            if block.id == id2: block2 = block
        if block1 is None or block2 is None:
            print(f"Ошибка: блок с id {id1} или {id2} не найден"); return
        upper_block, lower_block = (block1, block2) if block1.world_y <= block2.world_y else (block2, block1)
        circle_out, circle_in = upper_block.bottom_circle, lower_block.top_circle
        if value == 1:
            if not app.is_already_connected(circle_out, circle_in):
                coords1 = app.canvas.coords(circle_out); coords2 = app.canvas.coords(circle_in)
                sx, sy = (coords1[0]+coords1[2])/2, (coords1[1]+coords1[3])/2
                ex, ey = (coords2[0]+coords2[2])/2, (coords2[1]+coords2[3])/2
                line = app.canvas.create_line(sx, sy, ex, ey, fill="#FFD700", width=2, dash=(4,2), tags="line")
                app.canvas.tag_bind(line, "<Button-3>", lambda e, l=line: app.delete_connection(e, l))
                app.connections.append((circle_out, circle_in, line))
                print(f"Создано соединение: блок {upper_block.id} -> блок {lower_block.id}")
            else:
                print("Соединение между блоками уже существует")
        elif value == 0:
            removed = False
            for conn in list(app.connections):
                if (conn[0]==circle_out and conn[1]==circle_in) or (conn[0]==circle_in and conn[1]==circle_out):
                    app.canvas.delete(conn[2]); app.connections.remove(conn); removed = True
                    print(f"Удалено соединение: блок {upper_block.id} -> блок {lower_block.id}")
            if not removed: print("Соединения не найдено")
    def __getitem__(self, key):
        if not (isinstance(key, tuple) and len(key)==2):
            raise ValueError("Ключ должен быть кортежем (id1, id2)")
        id1, id2 = key; app = self.app; block1 = block2 = None
        for block in app.blocks:
            if block.id == id1: block1 = block
            if block.id == id2: block2 = block
        if block1 is None or block2 is None: return 0
        upper_block, lower_block = (block1, block2) if block1.world_y<=block2.world_y else (block2, block1)
        circle_out, circle_in = upper_block.bottom_circle, lower_block.top_circle
        for conn in app.connections:
            if (conn[0]==circle_out and conn[1]==circle_in) or (conn[0]==circle_in and conn[1]==circle_out):
                return 1
        return 0
    def __call__(self, id1, id2, value=1):
        self[(id1, id2)] = value

# --- Базовый перетаскиваемый блок ---
class DraggableBlock:
    def __init__(self, canvas, x, y, id, app):
        self.canvas = canvas; self.app = app; self.id = id
        self.world_x = x; self.world_y = y; self.world_width = 120; self.world_height = 70
        self.block_name = f"Block {id}"
        self.parameters = [("system_id", str(self.id)), ("light", "0"), ("TEXTBOX_LABEL", self.block_name),
                           ("run", "0"), ("FONT_SIZE", "12"), ("dependence", "1"),
                           ("opacity", "100"), ("color", "#404040"), ("background_color", "#404040"), ("color_text", "#ffd500")]
        # Ensure "ui", "glow", and "writing_now" are present
        param_keys = [p[0] for p in self.parameters]
        if "ui" not in param_keys:
            self.parameters.append(("ui", "1"))
        if "glow" not in param_keys:
            self.parameters.append(("glow", "0"))
        if "writing_now" not in param_keys:
            self.parameters.append(("writing_now", "0"))
        if "buttons" not in param_keys:
            self.parameters.append(("buttons", "1"))
        # Добавляем новые параметры для позиции
        self.parameters.append(("x", str(self.world_x)))
        self.parameters.append(("y", str(self.world_y)))
        if not any(param[0]=="angle" for param in self.parameters): self.parameters.append(("angle", "0"))
        if not any(param[0]=="connections" for param in self.parameters): self.parameters.append(("connections", "[]"))
        if not any(param[0]=="collided" for param in self.parameters): self.parameters.append(("collided", "[]"))
        self.parameters.append(("type", "normal"))
        self.io_params = {"input": "", "output": ""}
        self.code_output = ""
        self.script_code = DEFAULT_SCRIPT_INSTRUCTIONS + "\nprint(\"Скрипт выполнен\")\n"
        self.running = False; self.x = self.world_x; self.y = self.world_y; self.base_font_size = 12
        self.angle = float(self.get_parameter("angle")); self.selected = False; self.param_lock = threading.Lock()
        common_tag = f"block_all_{self.id}"
        self.block = canvas.create_polygon(self.get_rotated_coords(), fill="#2B2B2B", outline="#555555", width=2, tags=("block", common_tag))
        self.text = canvas.create_text(0, 0, text=self.get_parameter("TEXTBOX_LABEL"), fill="#888888", tags=(common_tag,))
        self.top_circle = canvas.create_oval(0, 0, 0, 0, fill="#FFD700", tags=(f"circle_{id}", "circle", "yellow_top", common_tag))
        self.bottom_circle = canvas.create_oval(0, 0, 0, 0, fill="#FFC107", tags=(f"circle_{id}", "circle", "yellow_bottom", common_tag))
        self.plus_button = canvas.create_oval(0, 0, 0, 0, fill="#444444", outline="#FFD700", width=1, tags=(f"plus_{id}", "plus_button", common_tag))
        self.plus_text = canvas.create_text(0, 0, text="+", fill="#888888", font=("Consolas", 10, "bold"), tags=(f"plus_{id}", "plus_text", common_tag))
        self.run_button = canvas.create_rectangle(0, 0, 0, 0, fill="#444444", outline="#FFD700", width=1, tags=(f"run_{id}", "run_button", common_tag))
        self.run_button_text = canvas.create_text(0, 0, text="▶", fill="#888888", font=("Consolas", 10, "bold"), tags=(f"run_{id}", "run_button_text", common_tag))
        self.edit_code_button = canvas.create_rectangle(0, 0, 0, 0, fill="#444444", outline="#FFD700", width=1, tags=(f"edit_{id}", "edit_button", common_tag))
        self.edit_code_button_text = canvas.create_text(0, 0, text="E", fill="#888888", font=("Consolas", 10, "bold"), tags=(f"edit_{id}", "edit_button_text", common_tag))
        self.output_toggle_button = canvas.create_rectangle(0, 0, 0, 0, fill="#444444", outline="#FFD700", width=1, tags=(f"output_{self.id}", "output_toggle", common_tag))
        self.output_toggle_text = canvas.create_text(0, 0, text="O", fill="#888888", font=("Consolas", 10, "bold"), tags=(f"output_{self.id}", "output_toggle_text", common_tag))
        for item in [self.block, self.text]: # self.text already has common_tag
            for ev, handler in [("<ButtonPress-1>", self.start_drag), ("<B1-Motion>", self.drag),
                                ("<ButtonRelease-1>", self.stop_drag), ("<Enter>", self.on_hover), ("<Leave>", self.on_hover_leave)]:
                canvas.tag_bind(item, ev, handler)
        for circle in [self.top_circle, self.bottom_circle]:
            for ev, handler in [("<ButtonPress-1>", self.start_line), ("<B1-Motion>", self.draw_line), ("<ButtonRelease-1>", self.end_line)]:
                canvas.tag_bind(circle, ev, handler)
        for item in [self.plus_button, self.plus_text]:
            canvas.tag_bind(item, "<Button-1>", self.add_parameter)
        canvas.tag_bind(self.text, "<Double-Button-1>", self.rename_block)
        for item in [self.block, self.text]:
            canvas.tag_bind(item, "<Button-3>", self.manage_parameters)
        for item in [self.run_button, self.run_button_text]:
            canvas.tag_bind(item, "<ButtonRelease-1>", self.run_script)
        for item in [self.edit_code_button, self.edit_code_button_text]:
            canvas.tag_bind(item, "<Button-1>", self.edit_script)
        canvas.tag_bind(self.output_toggle_button, "<Button-1>", self.toggle_output)
        canvas.tag_bind(self.output_toggle_text, "<Button-1>", self.toggle_output)
        self.drag_data = {"x": 0, "y": 0}; self.current_line = None; self.line_start_circle = None; self.connected_lines = []
        self.output_window = self.output_frame = self.output_text = None; self.output_drag_data = {}; self.output_modified = False
        self.resizing = False; self.system_params = {"width": str(self.world_width), "height": str(self.world_height)}
        # Ensure common_tag is applied, it was already there from previous step
        self.resize_handle = canvas.create_rectangle(0,0,0,0, fill="#FFD700", outline="#FFD700", tags=("resize_handle", f"resize_{id}", common_tag))
        canvas.tag_bind(self.resize_handle, "<ButtonPress-1>", self.start_resize)
        canvas.tag_bind(self.resize_handle, "<B1-Motion>", self.do_resize)
        canvas.tag_bind(self.resize_handle, "<ButtonRelease-1>", self.stop_resize)
        # Ensure common_tag is applied, it was already there from previous step
        self.rotate_handle = canvas.create_oval(0,0,0,0, fill="#FFD700", outline="#FFD700", tags=("rotate_handle", f"rotate_{id}", common_tag))
        canvas.tag_bind(self.rotate_handle, "<ButtonPress-1>", self.start_rotate)
        canvas.tag_bind(self.rotate_handle, "<B1-Motion>", self.do_rotate)
        canvas.tag_bind(self.rotate_handle, "<ButtonRelease-1>", self.stop_rotate)
        self.current_edit_entry = None  # Initialize current_edit_entry
        self.shadow_shapes = [] # For storing shadow polygon IDs
        self._current_rgb_fill_color = None # Initialize for color state management
        self.update_text()

    @staticmethod
    def is_valid_hex_color(color_string: str) -> bool:
        if not isinstance(color_string, str):
            return False
        match = re.fullmatch(r'#[0-9a-fA-F]{6}', color_string)
        return bool(match)

    @staticmethod
    def darken_hex_color(hex_color: str, factor: float = 0.5) -> str:
        if not DraggableBlock.is_valid_hex_color(hex_color):
            return hex_color 
        
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))

        return f"#{r:02x}{g:02x}{b:02x}"

    @property
    def move(self):
        return MoveController(self)
    def get_parameter(self, key):
        for name, value in self.parameters:
            if name == key: return value
        return None
    def get_rotated_coords(self):
        angle_rad = math.radians(self.angle); w = self.world_width; h = self.world_height
        cx = self.world_x + w/2; cy = self.world_y + h/2
        corners = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
        rotated = []
        for (dx, dy) in corners:
            rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            rotated.append((cx + rx, cy + ry))
        return [coord for point in rotated for coord in point]

    def get_bounding_box(self):
        rotated_coords = self.get_rotated_coords()
        
        x_coords = [rotated_coords[i] for i in range(0, 8, 2)]
        y_coords = [rotated_coords[i] for i in range(1, 8, 2)]
        
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)
        
        return (min_x, min_y, max_x, max_y)

    def start_resize(self, event):
        self.resizing = True; self.resize_data = {"x": event.x, "y": event.y, "init_width": self.world_width, "init_height": self.world_height}
    def do_resize(self, event):
        if not self.resizing: return
        dx = event.x - self.resize_data["x"]; dy = event.y - self.resize_data["y"]
        new_width = max(50, self.resize_data["init_width"] + dx/self.app.current_scale)
        new_height = max(30, self.resize_data["init_height"] + dy/self.app.current_scale)
        self.world_width, self.world_height = new_width, new_height
        self.system_params["width"], self.system_params["height"] = str(int(new_width)), str(int(new_height))
        # Update self.parameters as well
        updated_params = []
        width_found = False
        height_found = False
        for name, val in self.parameters:
            if name == "width":
                updated_params.append(("width", str(int(new_width))))
                width_found = True
            elif name == "height":
                updated_params.append(("height", str(int(new_height))))
                height_found = True
            else:
                updated_params.append((name, val))
        if not width_found:
            updated_params.append(("width", str(int(new_width))))
        if not height_found:
            updated_params.append(("height", str(int(new_height))))
        self.parameters = updated_params
        self.update_text()
    def stop_resize(self, event):
        if self.app.active_workspace: self.app.active_workspace.check_all_collisions()
        self.resizing = False; self.app.save_undo_state("Изменён размер блока")
    def serialize(self):
        return {"type": self.__class__.__name__, "id": self.id, "x": self.world_x, "y": self.world_y,
                "block_name": self.block_name, "width": self.world_width, "height": self.world_height,
                "parameters": self.parameters, "io_params": self.io_params, "script_code": self.script_code,
                "angle": self.angle}
    def activate(self):
        color_val = self.get_parameter("color")
        is_color_valid = False

        if color_val: # Check if color_val is not None and not an empty string
            try:
                # Attempt to get RGB values; this validates the color string (hex or named)
                self.canvas.winfo_rgb(color_val) 
                # If no error, color_val is a valid Tkinter color (hex or named)
                self._current_rgb_fill_color = color_val
                is_color_valid = True
            except tk.TclError: # Handle cases where the color string is invalid
                is_color_valid = False
        
        if not is_color_valid:
            self._current_rgb_fill_color = "#FFFF00"  # Default active color if param is invalid or missing
        
        # Get text_color parameter
        text_color_param = self.get_parameter("color_text")
        final_text_color = "#FFD700" # Default active text color
        if text_color_param:
            try:
                self.canvas.winfo_rgb(text_color_param) # Validate color
                final_text_color = text_color_param # Use valid custom color
            except tk.TclError:
                pass # Invalid color, use default
        
        # Set main text color
        self.canvas.itemconfigure(self.text, fill=final_text_color)
        # Set other internal elements to active colors (black for contrast)
        for item_id in [self.plus_text, self.run_button_text, self.edit_code_button_text, self.output_toggle_text]:
            if self.canvas.winfo_exists():
                all_items = self.canvas.find_all()
                if item_id in all_items:
                    self.canvas.itemconfigure(item_id, fill="#000000")

    def deactivate(self):
        # Determine inactive RGB color and store it for update_text
        color_val = self.get_parameter("color")
        if DraggableBlock.is_valid_hex_color(color_val):
            self._current_rgb_fill_color = DraggableBlock.darken_hex_color(color_val, factor=0.7)
        else:
            self._current_rgb_fill_color = "#2B2B2B"  # Default inactive

        # Set text color for inactive state
        self.canvas.itemconfigure(self.text, fill="#888888")
        # Set other internal elements to inactive colors
        for item_id in [self.plus_text, self.run_button_text, self.edit_code_button_text, self.output_toggle_text]:
            if self.canvas.winfo_exists():
                all_items = self.canvas.find_all()
                if item_id in all_items:
                    self.canvas.itemconfigure(item_id, fill="#888888")

    def blink(self, times=6, interval=300):
        # Blink will now respect the glow parameter via update_text calls triggered by light param changes
        if times <= 0:
            BlockWrapper(self)["light"] = "0" # This will trigger update_text
            return
        
        current_light_val = "1" if times % 2 == 1 else "0"
        BlockWrapper(self)["light"] = current_light_val # This will trigger update_text
        
        self.canvas.after(interval, lambda: self.blink(times - 1, interval))
    def start_drag(self, event):
        if self.selected:
            group = [b for b in self.app.active_workspace.blocks if getattr(b, "selected", False)]
            self.drag_group = group; self.group_drag_start = (event.x, event.y)
            for b in group: b.drag_start_x = b.world_x; b.drag_start_y = b.world_y
        else:
            self.drag_data["x"], self.drag_data["y"] = event.x, event.y
    def drag(self, event):
        if hasattr(self, "drag_group"):
            dx = (event.x - self.group_drag_start[0]) / self.app.current_scale
            dy = (event.y - self.group_drag_start[1]) / self.app.current_scale
            for b in self.drag_group:
                b.world_x = b.drag_start_x + dx; b.world_y = b.drag_start_y + dy; b.update_text()
            self.app.update_all_connections(); self.app.coord_label.config(text=f"X: {int(self.world_x)} , Y: {int(self.world_y)}")
        else:
            original_x = self.world_x
            original_y = self.world_y

            dx = event.x - self.drag_data["x"]; dy = event.y - self.drag_data["y"]
            world_dx = dx / self.app.current_scale; world_dy = dy / self.app.current_scale
            
            self.world_x += world_dx
            self.world_y += world_dy
            
            actual_ddx = self.world_x - original_x
            actual_ddy = self.world_y - original_y
            
            self.drag_data["x"], self.drag_data["y"] = event.x, event.y
            self.update_text() 

            connections_str = self.get_parameter("connections")
            connected_block_ids = []
            if connections_str:
                try:
                    parsed_connections = ast.literal_eval(connections_str)
                    if isinstance(parsed_connections, list):
                        connected_block_ids = [int(bid) for bid in parsed_connections] # Ensure IDs are integers
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing connections string '{connections_str}': {e}")

            if connected_block_ids:
                for block_id_to_move in connected_block_ids:
                    for b in self.app.active_workspace.blocks:
                        if b.id == block_id_to_move and b.id != self.id:
                            b.world_x += actual_ddx
                            b.world_y += actual_ddy
                            b.update_text()
                            break 
            
            self.app.update_all_connections()
            self.app.coord_label.config(text=f"X: {int(self.world_x)} , Y: {int(self.world_y)}")

    def stop_drag(self, event):
        if self.app.active_workspace: self.app.active_workspace.check_all_collisions()
        self.app.update_all_connections(); self.app.update_idletasks(); self.app.save_undo_state("Перемещение блока завершено")
        if hasattr(self, "drag_group"):
            del self.drag_group; del self.group_drag_start
    def update_line_coords(self, line):
        conn = next((c for c in self.app.connections if c[2]==line), None)
        if conn:
            s = self.canvas.coords(conn[0]); e = self.canvas.coords(conn[1])
            sx, sy = (s[0]+s[2])/2, (s[1]+s[3])/2; ex, ey = (e[0]+e[2])/2, (e[1]+e[3])/2
            self.canvas.coords(line, sx, sy, ex, ey)
    def start_line(self, event):
        self.line_start_circle = self.canvas.find_withtag("current")[0]
        coords = self.canvas.coords(self.line_start_circle)
        self.line_start = ((coords[0]+coords[2])/2, (coords[1]+coords[3])/2)
        self.current_line = self.canvas.create_line(*self.line_start, *self.line_start, fill="#FFD700", width=2, dash=(4,2), tags="line")
    def draw_line(self, event):
        if self.current_line:
            x = self.canvas.canvasx(event.x); y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.current_line, self.line_start[0], self.line_start[1], x, y)
    def end_line(self, event):
        if self.current_line:
            x = self.canvas.canvasx(event.x); y = self.canvas.canvasy(event.y)
            for item in self.canvas.find_overlapping(x, y, x, y):
                if item != self.line_start_circle and "circle" in self.canvas.gettags(item):
                    if self.canvas.itemcget(self.line_start_circle, "fill") != self.canvas.itemcget(item, "fill"):
                        if self.app.is_already_connected(self.line_start_circle, item): break
                        coords = self.canvas.coords(item)
                        ex, ey = (coords[0]+coords[2])/2, (coords[1]+coords[3])/2
                        self.canvas.coords(self.current_line, self.line_start[0], self.line_start[1], ex, ey)
                        self.app.connections.append((self.line_start_circle, item, self.current_line))
                        self.connected_lines.append(self.current_line)
                        self.canvas.tag_bind(self.current_line, "<Button-3>", lambda e, l=self.current_line: self.app.delete_connection(e, l))
                        block_a = self.app.find_block_by_circle(self.line_start_circle)
                        block_b = self.app.find_block_by_circle(item)
                        if block_a and block_b:
                            if getattr(block_a, "is_system", False) and not getattr(block_b, "is_system", False):
                                self.app.remove_block(block_b); self.current_line = None; self.app.save_undo_state("Соединение создано (удалён блок)"); return
                            elif getattr(block_b, "is_system", False) and not getattr(block_a, "is_system", False):
                                self.app.remove_block(block_a); self.current_line = None; self.app.save_undo_state("Соединение создано (удалён блок)"); return
                        self.current_line = None; self.line_start_circle = None; self.app.save_undo_state("Соединение создано"); return
            if self.current_line:
                self.canvas.delete(self.current_line); self.current_line = None; self.line_start_circle = None
    def add_parameter(self, event):
        name = ask_custom_string(self.app, "Добавить параметр", "Введите имя параметра:")
        if name is None or name=="system_id":
            messagebox.showwarning("Ошибка", "Нельзя добавлять или изменять системный параметр system_id"); return
        value = ask_custom_string(self.app, "Добавить параметр", "Введите значение параметра:")
        if value is None: return
        self.parameters.append((name, value)); self.update_text(); self.app.save_undo_state("Добавлен параметр")

    def rename_block(self, event):
        if self.current_edit_entry and self.current_edit_entry.winfo_exists():
            return

        # Get properties of the existing text item
        text_coords = self.canvas.coords(self.text)
        text_bbox = self.canvas.bbox(self.text) # x1, y1, x2, y2
        font = self.canvas.itemcget(self.text, "font")
        current_name = self.get_parameter("TEXTBOX_LABEL")

        if not text_bbox: # Should not happen if text exists
            return

        entry_x = text_coords[0]
        entry_y = text_coords[1]
        
        # Approximate width and height from bbox. Add some padding.
        entry_width = text_bbox[2] - text_bbox[0] + 10 
        entry_height = text_bbox[3] - text_bbox[1] + 5

        # Create the Entry widget
        entry_widget = tk.Entry(self.canvas, font=font, bg="#1E1E1E", fg="#FFD700",
                                insertbackground="#FFD700", borderwidth=0, highlightthickness=0)
        entry_widget.insert(0, current_name)
        entry_widget.select_range(0, tk.END)
        BlockWrapper(self)["writing_now"] = "1" # Set writing_now to "1"
        entry_widget.focus_set()

        # Store the entry widget
        self.current_edit_entry = entry_widget
        
        # Place the Entry widget on the canvas using create_window
        # We use the center of the text_bbox for anchoring the window
        # to better align with how canvas text items are placed.
        canvas_window_x = (text_bbox[0] + text_bbox[2]) / 2
        canvas_window_y = (text_bbox[1] + text_bbox[3]) / 2
        
        # Create the window and lift the entry widget
        entry_canvas_window_id = self.canvas.create_window(canvas_window_x, canvas_window_y,
                                   window=entry_widget, anchor=tk.CENTER,
                                   width=entry_width, height=entry_height,
                                   tags="entry_widget")
        entry_widget.lift()


        # Temporarily hide the original text item
        self.canvas.itemconfigure(self.text, state=tk.HIDDEN)

        # Bind events
        entry_widget.bind("<Return>", self._save_block_name)
        entry_widget.bind("<Escape>", self._cancel_rename_block)
        # FocusOut is still useful for tabbing away or other focus changes not caught by canvas click
        entry_widget.bind("<FocusOut>", self._save_block_name)

    def _save_block_name(self, event=None):
        if not self.current_edit_entry or not self.current_edit_entry.winfo_exists():
            return

        new_name = self.current_edit_entry.get()
        if new_name:
            updated = False
            new_params = []
            for name, val in self.parameters:
                if name == "TEXTBOX_LABEL":
                    new_params.append((name, new_name))
                    updated = True
                else:
                    new_params.append((name, val))
            if not updated:
                new_params.append(("TEXTBOX_LABEL", new_name))
            
            self.parameters = new_params
            self.block_name = new_name
            self.update_text()
            self.app.save_undo_state("Переименован блок")
            self.app.update_layers_listbox() # Update layers listbox after renaming
        
        BlockWrapper(self)["writing_now"] = "0" # Set writing_now to "0"
        self._cleanup_rename_entry()

    def _cancel_rename_block(self, event=None):
        BlockWrapper(self)["writing_now"] = "0" # Set writing_now to "0"
        self._cleanup_rename_entry()

    def _cleanup_rename_entry(self):
        if self.current_edit_entry and self.current_edit_entry.winfo_exists():
            self.current_edit_entry.destroy()
        self.current_edit_entry = None
        
        # Delete the canvas window item
        self.canvas.delete("entry_widget") # Assuming "entry_widget" is the tag for the canvas window

        # Restore visibility of the original text item
        self.canvas.itemconfigure(self.text, state=tk.NORMAL)

    def get_tooltip_parameters_text(self):
        lines = [f"{n}: {v}" for n, v in self.parameters]
        lines.append(f"Размер: {self.system_params['width']}x{self.system_params['height']}")
        lines.append(f'IO: in="{self.io_params["input"]}", out="{self.io_params["output"]}"')
        return "\n".join(lines)
    def update_text(self):
        # Read width and height from parameters
        new_world_width = None
        new_world_height = None
        try:
            width_param = self.get_parameter("width")
            if width_param is not None:
                new_world_width = float(width_param)
        except (ValueError, TypeError):
            pass # Invalid width parameter, ignore

        try:
            height_param = self.get_parameter("height")
            if height_param is not None:
                new_world_height = float(height_param)
        except (ValueError, TypeError):
            pass # Invalid height parameter, ignore

        if new_world_width is not None and new_world_width > 0:
            self.world_width = new_world_width
            self.system_params["width"] = str(int(new_world_width))

        if new_world_height is not None and new_world_height > 0:
            self.world_height = new_world_height
            self.system_params["height"] = str(int(new_world_height))
        scale = self.app.current_scale
        # Обновляем параметры "x" и "y" согласно текущей позиции
        new_params = []
        found_x = False
        found_y = False
        for name, val in self.parameters:
            if name=="x":
                new_params.append(("x", str(int(self.world_x)))); found_x = True
            elif name=="y":
                new_params.append(("y", str(int(self.world_y)))); found_y = True
            else:
                new_params.append((name, val))
        if not found_x:
            new_params.append(("x", str(int(self.world_x))))
        if not found_y:
            new_params.append(("y", str(int(self.world_y))))
        self.parameters = new_params

        try: base_font_size = int(self.get_parameter("FONT_SIZE"))
        except: base_font_size = self.base_font_size
        effective_font_size = max(1, int(base_font_size*scale))
        coords = self.get_rotated_coords(); scaled_coords = [c*scale for c in coords]
        self.canvas.coords(self.block, *scaled_coords)
        cx = (self.world_x+self.world_width/2)*scale; cy = (self.world_y+self.world_height/2)*scale
        max_width = (self.world_width-20)*scale
        self.canvas.itemconfigure(self.text, text=self.get_parameter("TEXTBOX_LABEL"), font=("Consolas", effective_font_size), width=max_width)
        self.canvas.coords(self.text, cx, cy-10*scale)
        angle_rad = math.radians(self.angle)
        top_dx = -self.world_height/2 * math.sin(angle_rad)
        top_dy = -self.world_height/2 * math.cos(angle_rad)
        top_cx, top_cy = cx+top_dx*scale, cy+top_dy*scale; r = 5*scale
        self.canvas.coords(self.top_circle, top_cx-r, top_cy-r, top_cx+r, top_cy+r)
        bot_dx = self.world_height/2 * math.sin(angle_rad)
        bot_dy = self.world_height/2 * math.cos(angle_rad)
        bot_cx, bot_cy = cx+bot_dx*scale, cy+bot_dy*scale
        self.canvas.coords(self.bottom_circle, bot_cx-r, bot_cy-r, bot_cx+r, bot_cy+r)
        tr_dx = self.world_width/2; tr_dy = -self.world_height/2
        tr_rx = tr_dx*math.cos(angle_rad)-tr_dy*math.sin(angle_rad)
        tr_ry = tr_dx*math.sin(angle_rad)+tr_dy*math.cos(angle_rad)
        tr_cx, tr_cy = cx+tr_rx*scale, cy+tr_ry*scale; offset = 10
        self.canvas.coords(self.plus_button, tr_cx-offset-10, tr_cy-offset, tr_cx-offset, tr_cy-offset+10)
        self.canvas.coords(self.plus_text, tr_cx-offset-5, tr_cy-offset+5)
        bl_dx = -self.world_width/2; bl_dy = self.world_height/2 - 25/scale
        bl_rx = bl_dx*math.cos(angle_rad)-bl_dy*math.sin(angle_rad)
        bl_ry = bl_dx*math.sin(angle_rad)+bl_dy*math.cos(angle_rad)
        bl_cx, bl_cy = cx+bl_rx*scale, cy+bl_ry*scale
        self.canvas.coords(self.run_button, bl_cx-10, bl_cy-7.5, bl_cx+10, bl_cy+7.5)
        self.canvas.coords(self.run_button_text, bl_cx, bl_cy)
        self.canvas.coords(self.edit_code_button, bl_cx+20, bl_cy-7.5, bl_cx+40, bl_cy+7.5)
        self.canvas.coords(self.edit_code_button_text, bl_cx+30, bl_cy)
        br_dx = self.world_width/2; br_dy = self.world_height/2 - 25/scale
        br_rx = br_dx*math.cos(angle_rad)-br_dy*math.sin(angle_rad)
        br_ry = br_dx*math.sin(angle_rad)+br_dy*math.cos(angle_rad)
        br_cx, br_cy = cx+br_rx*scale, cy+br_ry*scale
        self.canvas.coords(self.output_toggle_button, br_cx-10, br_cy-7.5, br_cx+10, br_cy+7.5)
        self.canvas.coords(self.output_toggle_text, br_cx, br_cy)
        br_dx = self.world_width/2; br_dy = self.world_height/2
        br_rx = br_dx*math.cos(angle_rad)-br_dy*math.sin(angle_rad)
        br_ry = br_dx*math.sin(angle_rad)+br_dy*math.cos(angle_rad)
        br_cx, br_cy = cx+br_rx*scale, cy+br_ry*scale
        self.canvas.coords(self.resize_handle, br_cx-10, br_cy-10, br_cx, br_cy)
        self.canvas.coords(self.rotate_handle, top_cx-r, top_cy-20-r, top_cx-r+2*r, top_cy-20+r)
        new_params = []
        found = False
        for name, val in self.parameters:
            if name=="angle": new_params.append(("angle", str(int(self.angle)))); found = True
            else: new_params.append((name, val))
        if not found: new_params.append(("angle", str(int(self.angle))))
        self.parameters = new_params
        for conn in self.app.connections:
            if self.top_circle in conn[:2] or self.bottom_circle in conn[:2]:
                self.update_line_coords(conn[2])

        # Glow and active state logic
        raw_glow_param = self.get_parameter("glow")
        raw_light_param = self.get_parameter("light")

        is_glowing = str(raw_glow_param).strip() == "1"
        is_active = str(raw_light_param).strip() == "1"

        # Clear existing shadow shapes
        for item_id in self.shadow_shapes:
            if self.canvas.winfo_exists() and item_id in self.canvas.find_all():
                self.canvas.delete(item_id)
        self.shadow_shapes = []

        outline_color, outline_width, text_color_val = "", 0, ""
        scaled_coords = [c * self.app.current_scale for c in self.get_rotated_coords()]


        if is_glowing:
            num_layers = 5
            offset_step = 1.0 * self.app.current_scale # Pixel offset, scaled
            shadow_base_color = "#FFD700" # Base color for shadow, can be adjusted

            for i in range(num_layers, 0, -1): # Draw from farthest to nearest
                dx = i * offset_step
                dy = i * offset_step
                
                shadow_layer_coords = []
                for k in range(0, len(scaled_coords), 2):
                    shadow_layer_coords.extend([scaled_coords[k] + dx, scaled_coords[k+1] + dy])
                
                # For a yellow shadow, we might use slightly different shades or just solid yellow
                # Using a slightly darker/desaturated yellow for outer layers could be an option
                # For simplicity, using a consistent shadow color first.
                # Example: shade = f"#{int(0xFF*(1-0.05*i)):02x}{int(0xEA*(1-0.05*i)):02x}{int(0x00*(1-0.05*i)):02x}"
                # This is complex; let's use a consistent less intense yellow for now.
                layer_shadow_color = "#E0C000" # A bit darker/desaturated yellow

                shadow_id = self.canvas.create_polygon(
                    shadow_layer_coords,
                    fill=layer_shadow_color, # Use the chosen shadow color
                    outline="", # No outline for shadow parts
                    tags=("shadow_part", f"shadow_{self.id}")
                )
                self.shadow_shapes.append(shadow_id)
                self.canvas.tag_lower(shadow_id) # Lower each shadow part as it's created

            # Adjust main block outline when glowing
            if is_active:
                outline_color, outline_width = "#FFC107", 2 # Darker orange/yellow for active glow
                # Determine text_color_val based on color_text parameter
                color_text_param = self.get_parameter("color_text")
                text_color_val = "#FFD700" # Default active text color
                if color_text_param:
                    try:
                        self.canvas.winfo_rgb(color_text_param) # Validate color
                        text_color_val = color_text_param # Use valid custom color
                    except tk.TclError:
                        pass # Invalid color, use default
            else: # Not active, but glowing
                outline_color, outline_width = "#B3A100", 1 # Dark yellow outline for inactive glow
                text_color_val = "#888888" # Standard text color for inactive block
        
        elif is_active:  # Not glowing, but active
            outline_color, outline_width = "#FF8C00", 3
            # Determine text_color_val based on color_text parameter
            color_text_param = self.get_parameter("color_text")
            text_color_val = "#FFD700" # Default active text color
            if color_text_param:
                try:
                    self.canvas.winfo_rgb(color_text_param) # Validate color
                    text_color_val = color_text_param # Use valid custom color
                except tk.TclError:
                    pass # Invalid color, use default
        else:  # Not glowing, not active (inactive)
            outline_color, outline_width = "#555555", 2
            text_color_val = "#888888"
        
        self.canvas.itemconfigure(self.block, outline=outline_color, width=outline_width)
        self.canvas.itemconfigure(self.text, fill=text_color_val)

        # Determine and apply the #RRGGBB fill color
        final_fill_rgb = ""
        color_param = self.get_parameter("color")
        bg_color_param = self.get_parameter("background_color")

        is_bg_color_valid = DraggableBlock.is_valid_hex_color(bg_color_param)
        
        is_color_param_valid_tkinter = False
        if color_param:
            try:
                self.canvas.winfo_rgb(color_param) # Validate named or hex color for color_param
                is_color_param_valid_tkinter = True
            except tk.TclError:
                is_color_param_valid_tkinter = False

        if hasattr(self, '_current_rgb_fill_color') and self._current_rgb_fill_color is not None:
            final_fill_rgb = self._current_rgb_fill_color
        elif is_active: # Active state logic (remains unchanged)
            # This uses color_param, which is now fetched earlier.
            # is_color_param_valid_tkinter is also determined earlier.
            if is_color_param_valid_tkinter: # Use the Tkinter-validated one for 'color'
                final_fill_rgb = color_param
            else:
                final_fill_rgb = "#FFFF00" # Default active color
        elif is_glowing: # Glowing but not active state logic (remains unchanged)
            # This uses color_param, which is now fetched earlier.
            hex_color_for_darken = None
            if is_color_param_valid_tkinter: # Use the Tkinter-validated one
                # Convert color_param (potentially named) to hex for darken_hex_color
                rgb_tuple = self.canvas.winfo_rgb(color_param)
                hex_color_for_darken = f"#{rgb_tuple[0]//256:02x}{rgb_tuple[1]//256:02x}{rgb_tuple[2]//256:02x}"
            else: # color_param is invalid or None
                hex_color_for_darken = "#FFFF00" # Default to yellow for darkening if color_param is bad
            final_fill_rgb = DraggableBlock.darken_hex_color(hex_color_for_darken, factor=0.7)
        else:  # Not active and not glowing - REFACTORED LOGIC
            # bg_color_param, color_param, is_bg_color_valid, and is_color_param_valid_tkinter
            # have been determined earlier.

            if is_bg_color_valid:
                final_fill_rgb = bg_color_param
            elif is_color_param_valid_tkinter:
                # Fallback to 'color' parameter if 'background_color' is invalid.
                # 'color_param' is the direct fallback if 'background_color' isn't set.
                final_fill_rgb = color_param
            else:
                # Ultimate fallback if both background_color and color are invalid.
                final_fill_rgb = "#606060"
        
        # Final conversion to #RRGGBB hex format for consistency.
        # This ensures that if a named color was validly used (e.g. for neutral state),
        # it's converted to hex before stippling or other operations that might expect hex.
        try:
            rgb_tuple_final = self.canvas.winfo_rgb(final_fill_rgb)
            final_fill_rgb = f"#{rgb_tuple_final[0]//256:02x}{rgb_tuple_final[1]//256:02x}{rgb_tuple_final[2]//256:02x}"
        except tk.TclError:
            final_fill_rgb = "#2B2B2B" # Ultimate fallback if final_fill_rgb is somehow still invalid

        # Apply the determined base RGB fill color first.
        # The stipple or full transparency logic below might override parts of this.
        self.canvas.itemconfigure(self.block, fill=final_fill_rgb) 

        # Stipple-based Opacity Handling (Final Version)
        opacity_str = self.get_parameter("opacity")
        alpha_float = 1.0  # Default to fully opaque
        try:
            opacity_value_100_scale = float(opacity_str)
            # Normalize from 0-100 scale to 0.0-1.0 scale
            alpha_float = opacity_value_100_scale / 100.0
            # Clamp to the range [0.0, 1.0]
            alpha_float = max(0.0, min(1.0, alpha_float))
        except (ValueError, TypeError):
            # If conversion fails, keep alpha_float at its default (1.0)
            pass

        stipple_pattern = ""
        # outline_color is already determined by the glow/active logic earlier in update_text

        if alpha_float == 0.0: # Fully transparent
            # Override fill and outline, set no stipple
            self.canvas.itemconfigure(self.block, fill="", outline="", stipple="")
        else:
            # For any non-zero alpha, ensure the outline determined by glow/active state is present.
            # The fill is already set by final_fill_rgb. Now apply stipple if needed.
            self.canvas.itemconfigure(self.block, outline=outline_color) # Ensure outline is correct
            
            if alpha_float == 1.0: # Fully opaque
                stipple_pattern = ""
            elif alpha_float >= 0.75: # Opacity from 0.75 up to (but not including) 1.0
                stipple_pattern = "gray75"
            elif alpha_float >= 0.50: # Opacity from 0.50 up to (but not including) 0.75
                stipple_pattern = "gray50"
            elif alpha_float >= 0.25: # Opacity from 0.25 up to (but not including) 0.50
                stipple_pattern = "gray25"
            else: # Opacity > 0.0 and < 0.25
                stipple_pattern = "gray12"
            
            self.canvas.itemconfigure(self.block, stipple=stipple_pattern)
        
        # Reset _current_rgb_fill_color after its potential use in this update cycle.
        self._current_rgb_fill_color = None 
            
        # Opacity (alpha channel) logic has been removed. Stippling will be used later if needed.

        # Ensure all shadow parts are beneath the main block after all operations
        for shadow_id in self.shadow_shapes:
             if self.canvas.winfo_exists() and shadow_id in self.canvas.find_all():
                self.canvas.tag_lower(shadow_id, self.block)


        # Control UI element visibility based on "ui" parameter
        ui_param_val = self.get_parameter("ui")
        
        # Determine visibility for general UI elements (circles, handles, plus button/text)
        # These are ONLY affected by the "ui" parameter.
        general_ui_visible = str(ui_param_val).strip() != "0"
        general_ui_target_state = "normal" if general_ui_visible else "hidden"

        general_ui_elements_to_toggle = [
            self.top_circle,
            self.bottom_circle,
            self.resize_handle,
            self.rotate_handle,
            self.plus_button, 
            self.plus_text
        ]
        
        for element_id in general_ui_elements_to_toggle:
            if self.canvas.winfo_exists():
                all_items = self.canvas.find_all()
                if element_id in all_items:
                    self.canvas.itemconfigure(element_id, state=general_ui_target_state)

        # Control operational button visibility (run, edit, output buttons/texts)
        # These are affected by BOTH "ui" AND "buttons" parameters.
        buttons_param_val = self.get_parameter("buttons")
        
        # Visible if general UI is visible AND buttons parameter is not "0"
        operational_buttons_are_visible = general_ui_visible and (str(buttons_param_val).strip() != "0")
        operational_buttons_target_state = "normal" if operational_buttons_are_visible else "hidden"

        operational_button_elements_to_toggle = [
            self.run_button,
            self.run_button_text,
            self.edit_code_button,
            self.edit_code_button_text,
            self.output_toggle_button,
            self.output_toggle_text
        ]

        for item_id in operational_button_elements_to_toggle:
            if self.canvas.winfo_exists():
                all_items = self.canvas.find_all()
                if item_id in all_items:
                    self.canvas.itemconfigure(item_id, state=operational_buttons_target_state)

    def move_to(self, target_x, target_y, duration):
        steps = max(1, int(duration/0.05))
        delta_x = (target_x - self.world_x)/steps; delta_y = (target_y - self.world_y)/steps
        self._animate_move(steps, delta_x, delta_y)
    def _animate_move(self, steps, delta_x, delta_y):
        if steps<=0: return
        self.world_x += delta_x; self.world_y += delta_y; self.update_text(); self.app.update_all_connections()
        self.canvas.after(50, lambda: self._animate_move(steps-1, delta_x, delta_y))
    def is_connected(self):
        return any(self.top_circle in conn[:2] or self.bottom_circle in conn[:2] for conn in self.app.connections)
    def on_hover(self, event):
        self.app.coord_label.config(text=f"X: {int(self.world_x)} , Y: {int(self.world_y)}")
    def on_hover_leave(self, event):
        self.app.coord_label.config(text="")
    def manage_parameters(self, event):
        win = tk.Toplevel(self.app)
        win.title("Управление параметрами")
        win.configure(bg="#2B2B2B")
        win.resizable(True, True)
        win.transient(self.app)
        # Создаём скроллируемую область для параметров
        container = tk.Frame(win, bg="#2B2B2B")
        container.pack(padx=10, pady=10, fill="both", expand=True)
        canvas_frame = tk.Canvas(container, bg="#2B2B2B", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas_frame.yview)
        scrollable_frame = tk.Frame(canvas_frame, bg="#2B2B2B")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
        )
        canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_frame.configure(yscrollcommand=scrollbar.set)
        canvas_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        if not self.parameters:
            tk.Label(scrollable_frame, text="Нет параметров", bg="#2B2B2B", fg="#FFD700", font=("Consolas", 10)).pack(pady=5)
        else:
            for i, (name, value) in enumerate(self.parameters):
                subframe = tk.Frame(scrollable_frame, bg="#2B2B2B")
                subframe.pack(fill="x", pady=2)
                if name=="system_id":
                    tk.Label(subframe, text=f"{name}: {value} (system)", anchor="w", bg="#2B2B2B", fg="#FFD700", font=("Consolas", 10), wraplength=300)\
                      .grid(row=0, column=0, sticky="w")
                else:
                    tk.Label(subframe, text=f"{name}: {value}", anchor="w", bg="#2B2B2B", fg="#FFD700", font=("Consolas", 10), wraplength=300)\
                      .grid(row=0, column=0, sticky="w")
                    tk.Button(subframe, text="Редактировать", command=lambda i=i: self.edit_parameter(i, win),
                              bg="#333333", fg="#FFD700", font=("Consolas", 10)).grid(row=0, column=1, padx=5)
                    tk.Button(subframe, text="Удалить", command=lambda i=i: self.delete_parameter(i, win),
                              bg="#333333", fg="#FFD700", font=("Consolas", 10)).grid(row=0, column=2, padx=5)
        tk.Button(win, text="Закрыть", command=win.destroy, bg="#333333", fg="#FFD700", font=("Consolas", 10)).pack(pady=5)
    def edit_parameter(self, index, win):
        param_name, param_value = self.parameters[index]
        new_value = ask_custom_multiline(win, "Редактировать параметр", f"Новое значение для {param_name}:", initialvalue=param_value)
        if new_value is not None:
            self.parameters[index] = (param_name, new_value); self.update_text(); self.app.save_undo_state("Изменён параметр")
    def delete_parameter(self, index, win):
        if self.parameters[index][0]=="system_id":
            messagebox.showwarning("Ошибка", "Нельзя удалять системный параметр system_id"); return
        del self.parameters[index]; self.update_text(); self.app.save_undo_state("Удалён параметр")
    def edit_script(self, event):
        self.app.save_undo_state("Редактирование кода")
        win = tk.Toplevel(self.app); win.title(f"Редактирование кода блока {self.block_name}")
        editor = CodeEditor(win, text=self.script_code); editor.pack(fill=tk.BOTH, expand=True)
        def save_and_close():
            self.script_code = editor.get_text(); self.app.save_undo_state("Изменён скрипт"); win.destroy()
        tk.Button(win, text="Сохранить", command=save_and_close, bg="#333333", fg="#FFD700", font=("Consolas", 10))\
          .pack(pady=5)
    def run_script(self, event, auto_run=False):
        if self.running: return
        current_prev = PrevBlocksWrapper(self)._get_blocks(); current_next = NextBlocksWrapper(self)._get_blocks()
        dependence = self.get_parameter("dependence") or "1"
        if not auto_run and dependence=="1" and (not current_prev or not current_next):
            messagebox.showwarning("Запуск скрипта", "Для запуска скрипта блок должен иметь соединения с обеих сторон (предыдущий и следующий блок).")
            (self.activate() if self.get_parameter("light")=="1" else self.deactivate()); return
        self.running = True
        env = {"prev": PrevBlocksWrapper(self), "self": BlockWrapper(self), "next": NextBlocksWrapper(self),
               "app": self.app, "asyncio": asyncio, "httpx": httpx, "json": json, "re": re, "__name__": "__main__"}
        def script_thread():
            stdout_backup, stderr_backup = sys.stdout, sys.stderr
            output_capture = io.StringIO()
            sys.stdout = sys.stderr = output_capture
            try: exec(self.script_code, env)
            except Exception as e: output_capture.write("\nException: "+str(e))
            finally:
                sys.stdout, sys.stderr = stdout_backup, stderr_backup
                self.canvas.after(0, lambda: self.finish_script_run(output_capture.getvalue()))
        t = threading.Thread(target=script_thread); t.daemon = True; t.start()
    def finish_script_run(self, output):
        self.code_output = output; self.running = False
        (self.activate() if self.get_parameter("light")=="1" else self.deactivate())
        for nb in NextBlocksWrapper(self)._get_blocks():
            if nb.get_parameter("run")=="1":
                BlockWrapper(nb)["run"] = "0"; self.canvas.after(0, lambda b=nb: b.run_script(None))
    def toggle_output(self, event):
        if self.output_window is None:
            self.output_frame = tk.Frame(self.canvas, bg="#1E1E1E", bd=2, relief="ridge")
            v_scroll = tk.Scrollbar(self.output_frame, orient=tk.VERTICAL)
            h_scroll = tk.Scrollbar(self.output_frame, orient=tk.HORIZONTAL)
            self.output_text = tk.Text(self.output_frame, width=80, height=15, bg="#1E1E1E", fg="#FFD700",
                                        font=("Consolas", 10), insertbackground="#FFD700", wrap="none",
                                        yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            v_scroll.config(command=self.output_text.yview); h_scroll.config(command=self.output_text.xview)
            v_scroll.pack(side="right", fill="y"); h_scroll.pack(side="bottom", fill="x"); self.output_text.pack(fill="both", expand=True)
            self.output_text.delete("1.0", tk.END); self.output_text.insert(tk.END, self.code_output)
            # Располагаем окно вывода в центре видимой области канвы
            self.canvas.update_idletasks()
            width = self.canvas.winfo_width(); height = self.canvas.winfo_height()
            center_x = self.canvas.canvasx(width/2); center_y = self.canvas.canvasy(height/2)
            self.output_window = self.canvas.create_window(center_x, center_y, window=self.output_frame, anchor="center",
                                                            tags=(f"output_window_{self.id}",))
            self.output_frame.bind("<ButtonPress-1>", self.start_output_drag)
            self.output_frame.bind("<B1-Motion>", self.do_output_drag)
            self.output_text.bind("<Key>", lambda e: setattr(self, "output_modified", True)); self.output_modified = False
        else:
            self.canvas.delete(self.output_window); self.output_window = self.output_frame = self.output_text = None
    def start_output_drag(self, event):
        self.output_drag_data = {"x": self.canvas.canvasx(event.x_root), "y": self.canvas.canvasy(event.y_root)}
        self.output_drag_data["win_x"], self.output_drag_data["win_y"] = self.canvas.coords(self.output_window)
    def do_output_drag(self, event):
        new_x = self.output_drag_data["win_x"] + (self.canvas.canvasx(event.x_root)-self.output_drag_data["x"])
        new_y = self.output_drag_data["win_y"] + (self.canvas.canvasy(event.y_root)-self.output_drag_data["y"])
        self.canvas.coords(self.output_window, new_x, new_y)
    def start_rotate(self, event):
        scale = self.app.current_scale; cx = (self.world_x+self.world_width/2)*scale; cy = (self.world_y+self.world_height/2)*scale
        self._rotate_center = (cx, cy); dx = event.x - cx; dy = event.y - cy
        self._initial_rotate_angle = degrees(atan2(dy, dx)); self._initial_block_angle = self.angle
    def do_rotate(self, event):
        cx, cy = self._rotate_center; dx = event.x - cx; dy = event.y - cy
        delta = degrees(atan2(dy, dx)) - self._initial_rotate_angle
        self.angle = (self._initial_block_angle + delta) % 360; self.update_text()
    def stop_rotate(self, event):
        self.app.save_undo_state("Поворот блока завершён")
    def set_block_type(self, new_type):
        mapping = {"normal": DraggableBlock, "switch": SwitchBlock}
        new_params = [(("type", new_type) if key.lower()=="type" else (key, val)) for key, val in self.parameters]
        self.parameters = new_params; self.block_name = f"SwitchBlock {self.id}" if new_type.lower()=="switch" else f"Block {self.id}"
        self.update_text()

# --- SwitchBlock ---
class SwitchBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        super().__init__(canvas, x, y, id, app)
        self.block_name = f"SwitchBlock {id}"; self.is_on = False
        common_tag = f"block_all_{self.id}" # Ensure common_tag is available for SwitchBlock elements
        self.toggle_button = self.canvas.create_rectangle(self.x+10, self.y+10, self.x+30, self.y+30,
                                                           fill="#444444", outline="#FFD700", width=1,
                                                           tags=(f"toggle_{id}", "toggle_button", common_tag))
        self.toggle_text = self.canvas.create_text(self.x+20, self.y+20, text="OFF", fill="#888888",
                                                    font=("Consolas", 10, "bold"), tags=(f"toggle_{id}", "toggle_text", common_tag))
        self.canvas.tag_bind(self.toggle_button, "<Button-1>", self.toggle_state)
        self.canvas.tag_bind(self.toggle_text, "<Button-1>", self.toggle_state)
        self.update_text()
    def toggle_state(self, event):
        self.is_on = not self.is_on
        if self.is_on:
            BlockWrapper(self)["run"] = "1"; BlockWrapper(self)["light"] = "1"
            self.canvas.itemconfigure(self.toggle_text, text="ON", fill="#FFD700"); self.run_script(None)
        else:
            BlockWrapper(self)["run"] = "0"; BlockWrapper(self)["light"] = "0"
            self.canvas.itemconfigure(self.toggle_text, text="OFF", fill="#888888"); self.deactivate()
    def update_text(self):
        super().update_text()
        scale = self.app.current_scale; cx = (self.world_x+self.world_width/2)*scale; cy = (self.world_y+self.world_height/2)*scale
        run_button_x = (self.world_x + self.world_width - 40) * scale
        run_button_y = (self.world_y + 10) * scale
        if hasattr(self, 'toggle_button'):
            # Position toggle near the run button with an offset
            self.canvas.coords(self.toggle_button, run_button_x - 30, run_button_y, run_button_x, run_button_y + 20)
        if hasattr(self, 'toggle_text'):
            self.canvas.coords(self.toggle_text, run_button_x - 15, run_button_y + 10)
            if self.get_parameter("light")=="1":
                self.canvas.itemconfigure(self.toggle_text, text="ON", fill="#FFD700"); self.is_on = True
            else:
                self.canvas.itemconfigure(self.toggle_text, text="OFF", fill="#888888"); self.is_on = False

# --- FileBlock ---
class FileBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        super().__init__(canvas, x, y, id, app)
        self.block_name = f"FileBlock {id}"
        self.block_type = "file"
        self.base_font_size = 12
        self.world_width = 100
        self.world_height = 60
        common_tag = f"block_all_{self.id}" # Ensure common_tag for FileBlock elements

        # Создаем только один набор элементов
        self.file_button = self.canvas.create_rectangle(x-45, y-20, x+45, y, fill="#333333", outline="#FFD700", width=2, tags=(f"file_{id}", "file_button", "block", common_tag))
        self.file_text = self.canvas.create_text(x, y-10, text="Select file", fill="#888888", font=("Consolas", 10, "bold"), tags=(f"file_{id}", "file_text", "block", common_tag))
        self.filename_text = self.canvas.create_text(x+55, y+40, text="", fill="#888888", font=("Consolas", 8), tags=(f"file_{id}", "filename_text", "block", common_tag))
        
        # Добавляем привязки событий
        for item in [self.file_button, self.file_text]: # These items already have common_tag
            self.canvas.tag_bind(item, "<Button-1>", self.select_file)
        
        self.cache_info = None
        self.previous_file = None
        self.update_text()
        
    def update_text(self):
        super().update_text()
        scale = self.app.current_scale
        cx = (self.world_x+self.world_width/2)*scale
        cy = (self.world_y+self.world_height/2)*scale
        
        # Получаем базовый размер шрифта
        try:
            base_font_size = int(self.get_parameter("FONT_SIZE"))
        except:
            base_font_size = self.base_font_size
            
        # Вычисляем эффективный размер шрифта
        effective_font_size = max(1, int(base_font_size * scale))
        
        # Обновляем позиции кнопки и текста
        if hasattr(self, 'file_button'):
            self.canvas.coords(self.file_button, 
                             cx-45, cy-20,  # левый верхний угол
                             cx+45, cy)     # правый нижний угол
                             
        if hasattr(self, 'file_text'):
            self.canvas.coords(self.file_text, cx, cy-10)
            self.canvas.itemconfigure(self.file_text, font=("Consolas", effective_font_size, "bold"))
            if self.get_parameter("light")=="1":
                self.canvas.itemconfigure(self.file_text, text="Select file", fill="#FFD700")
            else:
                self.canvas.itemconfigure(self.file_text, text="Select file", fill="#888888")
                
        if hasattr(self, 'filename_text'):
            self.canvas.coords(self.filename_text, cx, cy+10)
            # Используем размер шрифта на 2 пункта меньше основного
            filename_font_size = max(1, int((base_font_size - 2) * scale))
            self.canvas.itemconfigure(self.filename_text, font=("Consolas", filename_font_size))
            if self.cache_info:
                self.canvas.itemconfigure(self.filename_text, text=self.cache_info["file_name"])
            else:
                self.canvas.itemconfigure(self.filename_text, text="")
    
    def select_file(self, event):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Текстовые файлы", "*.txt"),
                ("JSON файлы", "*.json"),
                ("Python файлы", "*.py")
            ]
        )
        if file_path:
            # Если есть предыдущий файл, удаляем его из sys
            if hasattr(self, 'previous_file') and self.previous_file:
                try:
                    sys_path = os.path.join("sys", self.previous_file)
                    if os.path.exists(sys_path):
                        os.remove(sys_path)
                except Exception as e:
                    print(f"Error deleting previous file: {e}")
            
            # Копируем новый файл в sys
            file_name = os.path.basename(file_path)
            sys_path = os.path.join("sys", file_name)
            try:
                shutil.copy2(file_path, sys_path)
                self.previous_file = file_name  # Обновляем предыдущий файл
            except Exception as e:
                print(f"Error copying file to sys: {e}")
                return
            
            # Кешируем файл
            self.cache_info = cache_file(file_path, self.app.active_workspace.current_project_path)
            save_cache_info(self.app.active_workspace, self.cache_info)
            
            # Обновляем параметры блока
            BlockWrapper(self)["file_name"] = self.cache_info["file_name"]
            BlockWrapper(self)["file_hash"] = self.cache_info["hash"]
            BlockWrapper(self)["cache_info"] = json.dumps(self.cache_info)
            BlockWrapper(self)["run"] = "1"
            BlockWrapper(self)["light"] = "1"
            
            # Обновляем sys_path в приложении
            self.app.update_sys_path(self.cache_info["file_name"], sys_path)
            
            # Обновляем отображение
            self.canvas.itemconfigure(self.filename_text, text=self.cache_info["file_name"])
            self.run_script(None)
    
    def get_file_path(self):
        """Get the actual file path from cache"""
        if not self.cache_info:
            # Пытаемся восстановить информацию о кеше из параметров
            file_hash = self.get_parameter("file_hash")
            if file_hash:
                self.cache_info = load_cache_info(self.app.active_workspace, file_hash)
            
        if self.cache_info:
            cached_path = get_cached_file(self.cache_info)
            if cached_path:
                return cached_path
                
        return None

# --- SystemBlock ---
class SystemBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        super().__init__(canvas, x, y, id, app)
        self.canvas.itemconfigure(self.block, fill="#FF0000") # Ensure red fill from the start
            
        self.block_name = f"SystemBlock {id}" # Ensure block_name is set
        # self.canvas.itemconfigure(self.block, outline="#FF0000") # Outline can be managed by parent or here if needed
        # print("Системный блок выполнен") # Optional: keep for debugging
        self.script_code = DEFAULT_SCRIPT_INSTRUCTIONS + "\nprint(\"Системный блок\")\n"
        self.is_system = True
        self.update_text() # Call update_text to apply initial state correctly

    def update_text(self):
        super().update_text() # Call parent's update_text
        
        # Always ensure the SystemBlock is red after parent updates
        if hasattr(self, 'block') and self.block is not None:
             if self.canvas.winfo_exists() and self.canvas.type(self.block): # Check if block item is valid
                self.canvas.itemconfigure(self.block, fill="#FF0000")

    def stop_drag(self, event):
        self.app.update_all_connections(); self.app.update_idletasks()

# --- Рабочее пространство ---
class Workspace(tk.Frame):
    def __init__(self, parent, ws_id):
        super().__init__(parent, bg="#111111")
        self.ws_id = ws_id; self.current_scale = 1.0; self.undo_stack = []; self.redo_stack = []
        self.selected_gif_path = None  # Initialize selected_gif_path
        self.gif_frames = []
        self.current_gif_frame_index = 0
        self.gif_animation_after_id = None
        self.is_gif_playing = False
        self.gif_image_info = {} # To store GIF metadata like duration
        self.gif_pil_frames = [] # For storing original PIL Image objects
        self.canvas_update_blocks = []
        self.control_frame = tk.Frame(self, bg="#111111"); self.control_frame.pack(pady=5, fill=tk.X)
        btn_params = dict(bg="#333333", fg="#FFD700", activebackground="#555555",
                           activeforeground="#FFD700", bd=0, highlightthickness=0, font=("Consolas", 10, "bold"))
        tk.Button(self.control_frame, text="Добавить блок", command=self.add_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Switch блок", command=self.add_switch_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Системный блок", command=self.add_system_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="File блок", command=self.add_file_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Tkinter блок", command=self.add_tkinter_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Градиентный блок", command=self.add_gradient_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="GIF Block", command=self.add_gif_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="SVG Block", command=self.add_svg_block, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Сохранить", command=self.save_state, **btn_params).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Загрузить", command=self.load_state, **btn_params).pack(side=tk.LEFT, padx=5)
        self.grid_toggle_button = tk.Button(self.control_frame, text="Grid: ON", command=self.toggle_grid_visibility, **btn_params)
        self.grid_toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Add Select GIF button
        self.select_gif_button = tk.Button(self.control_frame, text="Select GIF", command=self.select_and_play_gif, **btn_params)
        self.select_gif_button.pack(side=tk.LEFT, padx=5)
        
        # Добавляем поле поиска и кнопку
        search_frame = tk.Frame(self.control_frame, bg="#111111")
        search_frame.pack(side=tk.RIGHT, padx=5)
        self.search_entry = tk.Entry(search_frame, bg="#1E1E1E", fg="#FFD700", insertbackground="#FFD700", font=("Consolas", 10), width=15)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        # Удаляем кнопку поиска и добавляем обработчик события изменения текста для поиска в реальном времени
        self.search_entry.bind("<KeyRelease>", self.search_blocks)
        self.search_entry.bind("<Return>", self.search_blocks)
        self.canvas = tk.Canvas(self, bg="#111111", highlightthickness=0); self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.configure(scrollregion=(-5000, -5000, 5000, 5000))
        self.canvas.bind("<Configure>", self.on_canvas_configure) # Original configure for scrollregion
        self.canvas.bind("<Configure>", self.on_canvas_resize_for_gif, add="+") # For GIF label resizing
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        # Modified original ButtonPress-1 to distinguish between selection and unfocus click
        self.canvas.bind("<ButtonPress-1>", self.handle_canvas_click_dispatcher) 
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        self.selection_rect = None; self.selection_start = None
        self.coord_label = tk.Label(self.canvas, text="", fg="#FFD700", bg="#111111", font=("Consolas", 12))
        self.coord_label.place(relx=1.0, rely=0, anchor="ne")
        self.blocks = []; self.connections = []; self.block_id = 1; self.connect = ConnectorMapping(self)
        self.current_project_path = None  # Добавляем путь к текущему проекту
        self.grid_visible = True # Default grid visibility
        self.gif_label = tk.Label(self.canvas, text="", bg="#111111") # Create GIF label
        self.gif_label_window_id = None # Initialize window ID for GIF label
        self.gif_label.bind("<Button-1>", self.stop_gif_playback) # Bind click to stop
        self.draw_grid() # Initial grid draw
        # Bind Escape key globally to stop GIF playback
        # Using add="+" to not override other Escape bindings, though it might be the only global one.
        self.winfo_toplevel().bind_all("<Escape>", self.stop_gif_playback, add="+")

    def __getattr__(self, name): return getattr(self.app, name)

    def stop_gif_playback(self, event=None):
        if not self.is_gif_playing:
            return

        self.is_gif_playing = False
        if self.gif_animation_after_id:
            self.canvas.after_cancel(self.gif_animation_after_id)
            self.gif_animation_after_id = None

        if self.gif_label_window_id:
            try:
                if self.canvas.type(self.gif_label_window_id): # Check if item exists
                    self.canvas.itemconfigure(self.gif_label_window_id, state='hidden')
            except tk.TclError: # Item might have been deleted
                pass
            self.gif_label.config(image='') 
        
        self.gif_frames.clear()
        self.gif_pil_frames.clear() # Clear PIL frames as well
        self.current_gif_frame_index = 0
        self.gif_image_info = {} # Clear image info
        self.gif_label.image = None # Clear image reference

        # No longer need to restore elements as they are not hidden
        # self.draw_grid() # Redraw grid (respects self.grid_visible) # This can be kept if needed
        print("GIF playback stopped.")

    def _resize_and_display_current_gif_frame(self):
        if not self.is_gif_playing or not self.gif_pil_frames or self.gif_label_window_id is None:
            return

        try:
            # Check if the canvas window item still exists
            if not self.canvas.type(self.gif_label_window_id):
                self.gif_label_window_id = None # It was deleted elsewhere
                return
        except tk.TclError:
            self.gif_label_window_id = None
            return

        original_pil_frame = self.gif_pil_frames[self.current_gif_frame_index]
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1: # Canvas not ready
            return

        image_width = original_pil_frame.width
        image_height = original_pil_frame.height

        if image_width == 0 or image_height == 0: # Invalid image
            return

        canvas_aspect = canvas_width / canvas_height
        image_aspect = image_width / image_height

        if canvas_aspect > image_aspect:  # Canvas is wider than image
            new_width = canvas_width
            new_height = int(canvas_width / image_aspect)
        else:  # Canvas is taller than image (or same aspect)
            new_height = canvas_height
            new_width = int(canvas_height * image_aspect)
        
        if new_width <= 0 or new_height <= 0: # Avoid issues with zero/negative dimensions
            return

        resized_image = original_pil_frame.resize((new_width, new_height), Image.LANCZOS)
        new_photo_image = ImageTk.PhotoImage(resized_image)

        self.gif_label.config(image=new_photo_image)
        self.gif_label.image = new_photo_image # Keep a reference


    def on_canvas_resize_for_gif(self, event):
        """Handles resizing of the GIF display area when the canvas is resized."""
        if self.is_gif_playing and self.gif_label_window_id is not None:
            # Update the coordinates to keep it centered and covering full canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            center_x = self.canvas.canvasx(canvas_width / 2)
            center_y = self.canvas.canvasy(canvas_height / 2)
            
            try:
                # Check if the canvas window item still exists
                if not self.canvas.type(self.gif_label_window_id):
                    self.gif_label_window_id = None 
                    return
                self.canvas.coords(self.gif_label_window_id, center_x, center_y)
                self.canvas.itemconfigure(self.gif_label_window_id, width=canvas_width, height=canvas_height)
            except tk.TclError:
                self.gif_label_window_id = None
                return

            self._resize_and_display_current_gif_frame()


    def select_and_play_gif(self):
        """Opens a file dialog to select a GIF file, loads it, and starts animation."""
        if self.is_gif_playing:
            self.stop_gif_playback()

        filepath = filedialog.askopenfilename(
            title="Select GIF file",
            filetypes=[("GIF files", "*.gif")]
        )
        if filepath:
            self.selected_gif_path = filepath
            print(f"Selected GIF file: {self.selected_gif_path}")
            
            self.gif_frames.clear() # Clear old PhotoImage frames
            self.gif_pil_frames.clear() # Clear old PIL frames

            try:
                gif_image = Image.open(self.selected_gif_path)
                self.gif_image_info = gif_image.info
                
                while True:
                    try:
                        gif_image.seek(len(self.gif_pil_frames)) 
                        frame_image_pil = gif_image.copy()
                        self.gif_pil_frames.append(frame_image_pil)
                        # self.gif_frames list is no longer needed here as PhotoImage is generated on the fly
                    except EOFError:
                        break 
            except Exception as e:
                messagebox.showerror("GIF Error", f"Could not load GIF file: {e}")
                self.selected_gif_path = None
                return

            if not self.gif_pil_frames:
                messagebox.showerror("GIF Error", "No frames found in GIF file.")
                self.selected_gif_path = None
                return

            self.canvas.update_idletasks()
            
            item_exists = False
            if self.gif_label_window_id is not None:
                try:
                    self.canvas.coords(self.gif_label_window_id) 
                    item_exists = True
                except tk.TclError:
                    item_exists = False
                    self.gif_label_window_id = None

            if not item_exists:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                center_x = self.canvas.canvasx(canvas_width / 2)
                center_y = self.canvas.canvasy(canvas_height / 2)
                
                self.gif_label_window_id = self.canvas.create_window(
                    center_x, center_y,
                    window=self.gif_label,
                    anchor=tk.CENTER,
                    width=canvas_width, 
                    height=canvas_height
                )
            
            if self.gif_label_window_id:
                 self.canvas.itemconfigure(self.gif_label_window_id, state='normal')
                 self.canvas.tag_lower(self.gif_label_window_id) # Lower it once
                 # Optionally, lower below specific known item types if they might overlap
                 # self.canvas.tag_lower(self.gif_label_window_id, "block")
                 # self.canvas.tag_lower(self.gif_label_window_id, "grid_line")


            # --- Elements are NO LONGER HIDDEN ---

            self.is_gif_playing = True
            self.current_gif_frame_index = 0 # Start from the first frame
            self._resize_and_display_current_gif_frame() # Display the first frame correctly sized
            self.animate_gif_frame() # Start animation loop
            self.canvas.focus_set()

        else: 
            self.selected_gif_path = None 
            print("No GIF file selected.")
            if self.is_gif_playing:
                 self.stop_gif_playback()

            if self.gif_label_window_id:
                # self.canvas.delete(self.gif_label_window_id) # Or just hide it
                self.canvas.itemconfigure(self.gif_label_window_id, state='hidden')
                # self.gif_label_window_id = None # Keep it for reuse
                self.gif_label.config(image=None)
                self.gif_label.image = None


    def animate_gif_frame(self):
        if not self.is_gif_playing or not self.gif_pil_frames:
            # Ensure animation stops if conditions are not met
            if self.gif_animation_after_id:
                self.canvas.after_cancel(self.gif_animation_after_id)
                self.gif_animation_after_id = None
            return
        
        # Advance frame index first
        self.current_gif_frame_index = (self.current_gif_frame_index + 1) % len(self.gif_pil_frames)
        # Then resize and display the new current frame
        self._resize_and_display_current_gif_frame() 
        
        duration = self.gif_image_info.get('duration', 100) 
        if duration <= 0: # Ensure sensible duration
            duration = 100
        
        self.gif_animation_after_id = self.canvas.after(duration, self.animate_gif_frame)

    def toggle_grid_visibility(self):
        self.grid_visible = not self.grid_visible
        self.draw_grid() 
        new_text = "Grid: ON" if self.grid_visible else "Grid: OFF"
        if hasattr(self, 'grid_toggle_button'): 
            self.grid_toggle_button.config(text=new_text)

    def handle_canvas_click_dispatcher(self, event):
        # First, attempt to handle unfocusing of an active entry
        handled_by_unfocus = self.handle_canvas_click_for_unfocus(event)
        # If the click was not to unfocus an active entry, proceed with selection
        if not handled_by_unfocus:
            # Check if the click is on an existing block or UI element before starting selection
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for item_id in items:
                tags = self.canvas.gettags(item_id)
                # If click is on any part of a block or its interactive elements, let block's own bindings handle it.
                if "block" in tags or "circle" in tags or "plus_button" in tags or "run_button" in tags or \
                   "edit_button" in tags or "output_toggle" in tags or "resize_handle" in tags or "rotate_handle" in tags:
                    return 
            self.start_selection(event)


    def handle_canvas_click_for_unfocus(self, event):
        for block in self.blocks:
            if hasattr(block, 'current_edit_entry') and \
               block.current_edit_entry and \
               block.current_edit_entry.winfo_viewable() and \
               block.get_parameter("writing_now") == "1":
                
                entry = block.current_edit_entry
                entry_x = entry.winfo_x()
                entry_y = entry.winfo_y()
                entry_width = entry.winfo_width()
                entry_height = entry.winfo_height()

                # Check if the click is outside the entry widget
                if not (entry_x <= event.x <= entry_x + entry_width and \
                        entry_y <= event.y <= entry_y + entry_height):
                    block._save_block_name(event=None) # Pass None or event as needed
                    return True # Click was handled by unfocusing
        return False # Click was not handled by unfocusing


    def draw_grid(self):
        # Check visibility flag first
        if not hasattr(self, 'grid_visible') or not self.grid_visible:
            self.canvas.delete("grid_line") # Clear any existing grid lines if toggled off
            return

        self.canvas.delete("grid_line") # Clear old lines before drawing new ones (if visible)
        grid_color = "#333333"
        
        # Use the fixed scroll region for grid boundaries
        min_x, min_y, max_x, max_y = -5000, -5000, 5000, 5000

        base_spacing = 50  # World units
        
        # Adjust world_spacing based on current_scale to maintain visual density
        world_spacing = base_spacing
        # Ensure on-screen spacing is not too small (target around 25-50 pixels)
        while world_spacing * self.current_scale < 25 and world_spacing < max_x: # Added max_x to prevent infinite loop
            world_spacing *= 2
        # Ensure on-screen spacing is not too large, introduce subdivisions if needed
        while world_spacing * self.current_scale > 100 and world_spacing > base_spacing / 4: # Allow subdivision down to base_spacing / 4
            world_spacing /= 2
        
        # Corrected calculation for start/end points based on world_spacing
        # Ensure we cover the entire scroll region
        start_x_world = math.floor(min_x / world_spacing) * world_spacing
        end_x_world = math.ceil(max_x / world_spacing) * world_spacing
        start_y_world = math.floor(min_y / world_spacing) * world_spacing
        end_y_world = math.ceil(max_y / world_spacing) * world_spacing

        # Draw vertical lines
        current_x_world = start_x_world
        while current_x_world <= end_x_world:
            x_canvas = current_x_world * self.current_scale
            self.canvas.create_line(x_canvas, min_y * self.current_scale, x_canvas, max_y * self.current_scale, fill=grid_color, tags="grid_line")
            current_x_world += world_spacing

        # Draw horizontal lines
        current_y_world = start_y_world
        while current_y_world <= end_y_world:
            y_canvas = current_y_world * self.current_scale
            self.canvas.create_line(min_x * self.current_scale, y_canvas, max_x * self.current_scale, y_canvas, fill=grid_color, tags="grid_line")
            current_y_world += world_spacing
            
        self.canvas.tag_lower("grid_line", "all")

    def on_canvas_configure(self, event): self.canvas.configure(scrollregion=(-5000, -5000, 5000, 5000))
    def start_pan(self, event): self.canvas.scan_mark(event.x, event.y)
    def do_pan(self, event): 
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.update_canvas_blocks()
        self.draw_grid() # Redraw grid after panning
    def zoom(self, event):
        old_scale = self.current_scale
        factor = 1.1 if event.delta > 0 else 0.9
        new_scale = old_scale * factor
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        world_x = mouse_x / old_scale
        world_y = mouse_y / old_scale
        self.current_scale = new_scale
        for block in self.blocks:
            block.update_text()
        # --- Масштабируем GradientBlock и другие дополнительные блоки ---
        if hasattr(self, '_extra_blocks'):
            for extra_block in self._extra_blocks:
                if hasattr(extra_block, 'update_position_and_size'):
                    extra_block.update_position_and_size(self.current_scale)
        # Обновляем все зарегистрированные блоки
        self.update_canvas_blocks()
        self.update_all_connections()
        self.draw_grid() # Redraw grid after zooming
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        new_mouse_x = world_x * new_scale
        new_mouse_y = world_y * new_scale
        dx = new_mouse_x - mouse_x
        dy = new_mouse_y - mouse_y
        bbox = self.canvas.bbox("all")
        if bbox:
            x_min, y_min, x_max, y_max = bbox
            total_width = x_max - x_min
            total_height = y_max - y_min
            xview = self.canvas.xview()
            yview = self.canvas.yview()
            new_x_frac = xview[0] + dx / total_width
            new_y_frac = yview[0] + dy / total_height
            self.canvas.xview_moveto(new_x_frac)
            self.canvas.yview_moveto(new_y_frac)
    def _get_center_coords(self, default_width, default_height):
        """Получаем координаты центра видимой области канвы"""
        # Получаем координаты центра видимой области
        center_x = self.canvas.canvasx(self.canvas.winfo_width() / 2)
        center_y = self.canvas.canvasy(self.canvas.winfo_height() / 2)
        
        # Преобразуем в мировые координаты с учетом масштаба
        world_x = center_x / self.current_scale
        world_y = center_y / self.current_scale
        
        return world_x - default_width/2, world_y - default_height/2
    def start_selection(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            if "block" in self.canvas.gettags(item):
                return
        self.selection_start = (x, y)
        self.selection_rect = self.canvas.create_rectangle(x, y, x, y, outline="#FFD700", dash=(2, 2))
    def update_selection(self, event):
        if self.selection_rect:
            x0, y0 = self.selection_start
            x1 = self.canvas.canvasx(event.x)
            y1 = self.canvas.canvasy(event.y)
            self.canvas.coords(self.selection_rect, x0, y0, x1, y1)
    def end_selection(self, event):
        if self.selection_rect:
            x0, y0, x1, y1 = self.canvas.coords(self.selection_rect)
            xmin, xmax = min(x0, x1), max(x0, x1); ymin, ymax = min(y0, y1), max(y0, y1)
            selected_blocks = []
            for block in self.blocks:
                bbox = self.canvas.bbox(block.block)
                if bbox:
                    bx0, by0, bx1, by1 = bbox
                    if bx0>=xmin and by0>=ymin and bx1<=xmax and by1<=ymax:
                        selected_blocks.append(block); self.canvas.itemconfigure(block.block, outline="#FF0000"); block.selected = True
                    else:
                        self.canvas.itemconfigure(block.block, outline="#555555"); block.selected = False
            self.canvas.delete(self.selection_rect); self.selection_rect = self.selection_start = None
            if selected_blocks: print("Selected block ids:", [block.id for block in selected_blocks])
            
    def search_blocks(self, event=None):
        """Поиск блоков по нескольким критериям с использованием нечеткого сравнения"""
        search_text = self.search_entry.get().strip().lower()
        
        # Сначала деактивируем все блоки
        for block in self.blocks:
            block.deactivate()
            block.selected = False
        
        if not search_text:
            return
            
        # Разбиваем поисковый запрос на отдельные слова
        search_terms = search_text.split()
        
        # Ищем блоки, соответствующие всем критериям поиска
        found_blocks = []
        for block in self.blocks:
            block_name = block.block_name.lower()
            block_type = getattr(block, 'block_type', '').lower()
            block_params = ' '.join(str(param[1]).lower() for param in getattr(block, 'parameters', []))
            
            # Проверяем каждое слово из поискового запроса
            matches_all_terms = True
            for term in search_terms:
                # Проверяем совпадение с именем блока
                name_ratio = fuzz.partial_ratio(term, block_name)
                # Проверяем совпадение с типом блока
                type_ratio = fuzz.partial_ratio(term, block_type)
                # Проверяем совпадение с параметрами блока
                param_ratio = fuzz.partial_ratio(term, block_params)
                
                # Если ни один из критериев не дает достаточного совпадения
                if max(name_ratio, type_ratio, param_ratio) < 70:  # Порог совпадения
                    matches_all_terms = False
                    break
            
            if matches_all_terms:
                found_blocks.append(block)
            # Проверяем содержимое блока
            elif isinstance(block, FileBlock) and block.cache_info:
                if search_text in block.cache_info['file_name'].lower():
                    found_blocks.append(block)
            # Проверяем параметры блока
            else:
                for name, value in getattr(block, 'parameters', []):
                    if search_text in str(value).lower():
                        found_blocks.append(block)
                        break
            
            # Если блок найден, активируем его
            if block in found_blocks:
                block.activate()
                block.selected = True
                # Прокручиваем к первому найденному блоку
                if len(found_blocks) == 1:
                    self.scroll_to_block(block)
        
        # Выводим информацию о найденных блоках
        if found_blocks:
            print(f"Найдено блоков: {len(found_blocks)}")
            for block in found_blocks:
                print(f"- {block.block_name} (тип: {getattr(block, 'block_type', 'неизвестный')})")
        else:
            print("Блоки не найдены")
    
    def scroll_to_block(self, block):
        """Прокрутка канвы к указанному блоку"""
        # Получаем координаты блока
        x = block.world_x * self.current_scale
        y = block.world_y * self.current_scale
        
        # Получаем размеры видимой области канвы
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Вычисляем новые координаты прокрутки, чтобы блок был в центре
        bbox = self.canvas.bbox("all")
        if bbox:
            x_min, y_min, x_max, y_max = bbox
            total_width = x_max - x_min
            total_height = y_max - y_min
            
            # Вычисляем новые доли прокрутки
            new_x_frac = (x - canvas_width/2) / total_width
            new_y_frac = (y - canvas_height/2) / total_height
            
            # Ограничиваем значения, чтобы они были в допустимом диапазоне [0, 1]
            new_x_frac = max(0, min(1, new_x_frac))
            new_y_frac = max(0, min(1, new_y_frac))
            
            # Прокручиваем канву
            # self.canvas.xview_moveto(new_x_frac) # Disabled
            # self.canvas.yview_moveto(new_y_frac) # Disabled
    def capture_state(self):
        state = self.get_state(); return json.loads(json.dumps(state))
    def get_state(self):
        state = {"blocks": [], "connections": [], "gradient_blocks": []}
        
        # Сохраняем блоки с учетом кеша файлов
        for block in self.blocks:
            block_data = block.serialize()
            
            # Для FileBlock сохраняем дополнительную информацию
            if isinstance(block, FileBlock):
                if block.cache_info:
                    # Сохраняем информацию о кеше
                    block_data["cache_info"] = block.cache_info
                    # Сохраняем имя файла для отображения
                    block_data["display_filename"] = block.cache_info["file_name"]
            
            state["blocks"].append(block_data)
            
        # Сохраняем градиентные блоки
        if hasattr(self, '_extra_blocks'):
            for block in self._extra_blocks:
                if isinstance(block, GradientBlock):
                    state["gradient_blocks"].append(block.get_save_data())
            
        # Сохраняем соединения
        for conn in self.connections:
            block1 = self.find_block_by_circle(conn[0])
            block2 = self.find_block_by_circle(conn[1])
            if block1 and block2:
                point1 = "top" if block1.top_circle==conn[0] else "bottom"
                point2 = "top" if block2.top_circle==conn[1] else "bottom"
                state["connections"].append({
                    "block1": block1.id,
                    "point1": point1,
                    "block2": block2.id,
                    "point2": point2
                })
        
        # Сохраняем информацию о кеше файлов
        if hasattr(self, "file_cache"):
            state["file_cache"] = self.file_cache

        # Save Z-order
        if hasattr(self.app, 'layers_listbox'):
            listbox_items_with_id = self.app.layers_listbox.get(0, tk.END)
            z_order_ids = []
            for item_text in listbox_items_with_id:
                try:
                    block_id_str = item_text.split("::", 1)[0]
                    z_order_ids.append(block_id_str) # Storing as string, consistent with id_to_block_map keys
                except IndexError:
                    print(f"Warning: Could not parse block ID for Z-order from listbox item: {item_text}")
            state["z_order"] = z_order_ids
            
        return state
    def restore_state(self, state):
        if self.is_gif_playing:
            self.stop_gif_playback() # Stop GIF if playing before restoring state
        # Очищаем текущее состояние
        for block in self.blocks:
            self.canvas.delete(block.block)
            self.canvas.delete(block.text)
            self.canvas.delete(block.top_circle)
            self.canvas.delete(block.bottom_circle)
            self.canvas.delete(block.plus_button)
            self.canvas.delete(block.plus_text)
            self.canvas.delete(block.run_button)
            self.canvas.delete(block.run_button_text)
            self.canvas.delete(block.edit_code_button)
            self.canvas.delete(block.edit_code_button_text)
            self.canvas.delete(block.output_toggle_button)
            self.canvas.delete(block.output_toggle_text)
            
        # Удаляем градиентные блоки
        if hasattr(self, '_extra_blocks'):
            for block in self._extra_blocks:
                if isinstance(block, GradientBlock):
                    block.destroy()
            self._extra_blocks = []
            
        for conn in self.connections:
            self.canvas.delete(conn[2])
            
        self.blocks = []
        self.connections = []
        self.block_id = 1
        block_map = {}
        
        # Восстанавливаем кеш файлов
        if "file_cache" in state:
            self.file_cache = state["file_cache"]
        else:
            self.file_cache = {}
            
        # Восстанавливаем блоки (шаг 1: создать все блоки из save state)
        raw_blocks_from_state = []
        for block_data in state.get("blocks", []):
            if block_data.get("type") == "EmptyBlock":
                continue
            block = self.create_block_from_data(block_data)
            raw_blocks_from_state.append(block) # Keep them in order of creation for now
            block_map[block.id] = block
            if block.id >= self.block_id:
                self.block_id = block.id + 1

            if isinstance(block, FileBlock) and "cache_info" in block_data:
                block.cache_info = block_data["cache_info"]
                if "display_filename" in block_data:
                    block.canvas.itemconfigure(block.filename_text, text=block_data["display_filename"])
                if block.cache_info:
                    cached_path = get_cached_file(block.cache_info)
                    if cached_path:
                        BlockWrapper(block)["file_path"] = cached_path
                        BlockWrapper(block)["cache_info"] = json.dumps(block.cache_info)

        # Восстанавливаем Z-order (шаг 2: упорядочить self.blocks)
        saved_z_order_ids = state.get("z_order", []) # List of block IDs (strings)
        ordered_blocks_from_z = []
        processed_ids = set()

        if saved_z_order_ids: # Only if z_order exists in save
            for block_id_str in saved_z_order_ids:
                block = block_map.get(int(block_id_str)) # block_map keys are int IDs
                if block:
                    ordered_blocks_from_z.append(block)
                    processed_ids.add(block.id)
        
        # Add any blocks not in saved_z_order (e.g., from older save or new blocks)
        # These will be appended after the Z-ordered blocks.
        # We iterate through block_map which has all loaded blocks.
        for block_id_int, block_instance in block_map.items():
            if block_id_int not in processed_ids:
                ordered_blocks_from_z.append(block_instance)
        
        self.blocks = ordered_blocks_from_z # self.blocks is now correctly ordered

        # Восстанавливаем градиентные блоки
        if not hasattr(self, '_extra_blocks'):
            self._extra_blocks = []
        for block_data in state.get("gradient_blocks", []):
            if block_data.get("type") == "gradient":
                gradient_block = GradientBlock.from_save_data(self.canvas, block_data)
                self._extra_blocks.append(gradient_block)
        
        # Восстанавливаем соединения
        for conn_data in state.get("connections", []):
            id1 = conn_data["block1"]
            id2 = conn_data["block2"]
            point1 = conn_data["point1"]
            point2 = conn_data["point2"]
            
            block1 = block_map.get(id1)
            block2 = block_map.get(id2)
            
            if block1 and block2:
                circle1 = block1.top_circle if point1=="top" else block1.bottom_circle
                circle2 = block2.top_circle if point2=="top" else block2.bottom_circle
                
                coords1 = self.canvas.coords(circle1)
                coords2 = self.canvas.coords(circle2)
                
                sx, sy = (coords1[0]+coords1[2])/2, (coords1[1]+coords1[3])/2
                ex, ey = (coords2[0]+coords2[2])/2, (coords2[1]+coords2[3])/2
                
                line = self.canvas.create_line(sx, sy, ex, ey, fill="#FFD700", width=2, dash=(4,2), tags="line")
                self.canvas.tag_bind(line, "<Button-3>", lambda e, l=line: self.delete_connection(e, l))
                self.connections.append((circle1, circle2, line))
        
        # After self.blocks is correctly ordered and all elements are restored:
        # 1. Update the layers listbox based on the new self.blocks order.
        if hasattr(self.app, 'update_layers_listbox'):
            self.app.update_layers_listbox() 
        # 2. Update the canvas Z-order based on the now-updated layers listbox.
        # This might be implicitly called if update_layers_listbox always triggers it,
        # or it might need an explicit call if the goal is direct canvas update from self.blocks order.
        # However, update_block_z_order reads from the listbox. So the sequence is:
        # self.blocks (ordered) -> update_layers_listbox (populates listbox in order) -> update_block_z_order (reads listbox and updates canvas)
        if hasattr(self.app, 'update_block_z_order'):
             self.app.update_block_z_order()

        messagebox.showinfo("Загрузка", "Состояние загружено")

    def save_undo_state(self, description=""):
        self.undo_stack.append((self.capture_state(), description)); self.redo_stack.clear()
    def perform_undo(self):
        if not self.undo_stack: return
        current_state = self.capture_state(); self.redo_stack.append((current_state, ""))
        state, desc = self.undo_stack.pop(); self.restore_state(state) # restore_state will call update_layers_listbox
        self.app.show_notification(f"Отмена: {desc}" if desc else "Отмена: Неизвестное действие")
    def perform_redo(self):
        if not self.redo_stack: return
        current_state = self.capture_state(); self.undo_stack.append((current_state, ""))
        state, desc = self.redo_stack.pop(); self.restore_state(state) # restore_state will call update_layers_listbox
        self.app.show_notification(f"Возврат: {desc}" if desc else "Возврат: Неизвестное действие")
    def add_block(self):
        x, y = self._get_center_coords(120, 70)
        block = DraggableBlock(self.canvas, x, y, self.block_id, self); self.blocks.append(block)
        self.block_id += 1; self.app._last_block = block; self.save_undo_state("Добавлен блок")
        self.app.update_layers_listbox()
    def add_switch_block(self):
        x, y = self._get_center_coords(120, 70)
        block = SwitchBlock(self.canvas, x, y, self.block_id, self); self.blocks.append(block)
        self.block_id += 1; self.app._last_block = block; self.save_undo_state("Добавлен Switch блок")
        self.app.update_layers_listbox()
    def add_system_block(self):
        x, y = self._get_center_coords(120, 70)
        block = SystemBlock(self.canvas, x, y, self.block_id, self); self.blocks.append(block)
        self.block_id += 1; self.app._last_block = block; self.save_undo_state("Добавлен системный блок")
        self.app.update_layers_listbox()
    def add_file_block(self):
        x, y = self._get_center_coords(120, 70)
        block = FileBlock(self.canvas, x, y, self.block_id, self); self.blocks.append(block)
        self.block_id += 1; self.app._last_block = block; self.save_undo_state("Добавлен File блок")
        self.app.update_layers_listbox()
    def add_tkinter_block(self):
        x, y = self._get_center_coords(120, 70)
        block = TkinterBlock(self.canvas, x, y, self.block_id, self)
        self.blocks.append(block)
        self.block_id += 1
        self.app._last_block = block
        self.save_undo_state("Добавлен Tkinter блок")
        self.app.update_layers_listbox()

    def add_gradient_block(self):
        # Добавляет GradientBlock в интерфейс
        x, y = self._get_center_coords(120, 70)
        gradient_block = GradientBlock(self.canvas, text="Градиентный Блок")
        # Устанавливаем мировые координаты
        gradient_block.set_world_position(x, y)
        # Устанавливаем позицию и размер с учетом текущего масштаба
        zoom = getattr(self, 'current_scale', 1.0)
        gradient_block.update_position_and_size(zoom)
        # Для совместимости с системой блоков, можно добавить gradient_block в список блоков, если потребуется
        # self.blocks.append(gradient_block) # Not adding to self.blocks to avoid duplicate listing if it's handled elsewhere
        # Сохраняем ссылку на gradient_block для масштабирования
        if not hasattr(self, '_extra_blocks'):
            self._extra_blocks = []
        self._extra_blocks.append(gradient_block)
        self.save_undo_state("Добавлен Gradient блок")
        # GradientBlock is not a standard block, so it might not be listed in layers,
        # or it needs a specific handling in update_layers_listbox if it should be.
        # For now, not calling update_layers_listbox here.

    def add_gif_block(self):
        x, y = self._get_center_coords(120, 70) # Or appropriate default size
        block = GIFBlock(self.canvas, x, y, self.block_id, self)
        self.blocks.append(block)
        self.block_id += 1
        self.app._last_block = block
        self.save_undo_state("Добавлен GIF блок")
        self.app.update_layers_listbox()

    def add_svg_block(self):
        x, y = self._get_center_coords(120, 70) 
        block = SVGBlock(self.canvas, x, y, self.block_id, self)
        self.blocks.append(block)
        self.block_id += 1
        self.app._last_block = block
        self.save_undo_state("Добавлен SVG блок")
        self.app.update_layers_listbox()

    def update_all_connections(self):
        for start_circle, end_circle, line in self.connections:
            s = self.canvas.coords(start_circle); e = self.canvas.coords(end_circle)
            sx, sy = (s[0]+s[2])/2, (s[1]+s[3])/2; ex, ey = (e[0]+e[2])/2, (e[1]+e[3])/2
            self.canvas.coords(line, sx, sy, ex, ey)
    def delete_connection(self, event, line):
        self.save_undo_state("Удалено соединение")
        conn = next((c for c in self.connections if c[2]==line), None)
        if conn: self.connections.remove(conn); self.canvas.delete(conn[2])
    def is_already_connected(self, start_circle, end_circle):
        return any((c[0]==start_circle and c[1]==end_circle) or (c[0]==end_circle and c[1]==start_circle) for c in self.connections)
    def find_block_by_circle(self, circle_id):
        for block in self.blocks:
            if block.top_circle==circle_id or block.bottom_circle==circle_id: return block
        return None
    def remove_block(self, block):
        self.save_undo_state("Удалён блок")
        if hasattr(block, "is_system") and block.is_system: return

        # Delete all canvas items associated with the block using the common tag
        self.canvas.delete(f"block_all_{block.id}")

        if block in self.blocks: self.blocks.remove(block)
        
        # Remove connections associated with the block
        for conn in list(self.connections):
            if block.top_circle in conn[:2] or block.bottom_circle in conn[:2]:
                self.canvas.delete(conn[2]); self.connections.remove(conn)
        
        self.app.update_layers_listbox()
    def create_block_from_data(self, data):
        block_type = data.get("type", "DraggableBlock")
        x = data.get("x", 50)
        y = data.get("y", 50)
        id = data.get("id", self.block_id)
        
        # Choose the correct block class, always using 'id' not 'id_val'
        if block_type == "DraggableBlock":
            block = DraggableBlock(self.canvas, x, y, id, self)
        elif block_type == "SwitchBlock":
            block = SwitchBlock(self.canvas, x, y, id, self)
        elif block_type == "SystemBlock":
            block = SystemBlock(self.canvas, x, y, id, self)
        elif block_type == "FileBlock":
            block = FileBlock(self.canvas, x, y, id, self)
        elif block_type == "TkinterBlock":
            block = TkinterBlock(self.canvas, x, y, id, self)
        elif block_type == "gifblock":  # Match the type set in GIFBlock.__init__
            block = GIFBlock(self.canvas, x, y, id, self)
        elif block_type == "svgblock": # Added for SVGBlock
            block = SVGBlock(self.canvas, x, y, id, self)
        else:  # Fallback for unknown types
            block = DraggableBlock(self.canvas, x, y, id, self)
        
        block.parameters = data.get("parameters", block.parameters)
        
        # Ensure "background_color" parameter is present
        current_params = block.parameters
        if not any(param[0] == "background_color" for param in current_params):
            current_params.append(("background_color", "#303030"))
        block.parameters = current_params
        
        # Ensure "ui", "glow", "writing_now", and "buttons" parameters are present for loaded blocks
        param_keys = [p[0] for p in block.parameters]
        if "ui" not in param_keys:
            block.parameters.append(("ui", "1"))
        if "glow" not in param_keys:
            block.parameters.append(("glow", "0"))
        if "writing_now" not in param_keys:
            block.parameters.append(("writing_now", "0"))
        if "buttons" not in param_keys:
            block.parameters.append(("buttons", "1"))
        
        # Ensure "connections" parameter is present
        if not any(param[0] == "connections" for param in block.parameters):
            block.parameters.append(("connections", "[]"))
        # Ensure "collided" parameter is present and defaults to "[]" if missing
        if not any(param[0] == "collided" for param in block.parameters):
            block.parameters.append(("collided", "[]"))
        if not any(param[0] == "dependence" for param in block.parameters):
            block.parameters.append(("dependence", "1"))
        
        # Set block_name from TEXTBOX_LABEL
        for param, value in block.parameters:
            if param == "TEXTBOX_LABEL":
                block.block_name = value
                break
        
        block.io_params = data.get("io_params", block.io_params)
        block.script_code = data.get("script_code", block.script_code)
        block.world_width = data.get("width", block.world_width)
        block.world_height = data.get("height", block.world_height)
        block.world_x = data.get("x", block.world_x)
        block.world_y = data.get("y", block.world_y)
        block.system_params["width"] = str(int(block.world_width))
        block.system_params["height"] = str(int(block.world_height))
        block.angle = float(data.get("angle", 0))
        
        # GIFBlock specific deserialization logic
        if block_type == "gifblock":  # Check type again for safety
            loaded_gif_path = data.get("selected_gif_path")  # Get the saved path

            if loaded_gif_path:
                block.selected_gif_path = loaded_gif_path

                # Update TEXTBOX_LABEL parameter in block.parameters
                new_params_for_label = []
                label_updated = False
                for name, val in block.parameters:  # Iterate current block.parameters
                    if name == "TEXTBOX_LABEL":
                        new_params_for_label.append(("TEXTBOX_LABEL", f"GIFBlock {block.id}: {os.path.basename(block.selected_gif_path)}"))
                        label_updated = True
                    else:
                        new_params_for_label.append((name, val))
                if not label_updated:  # If TEXTBOX_LABEL wasn't in params
                    new_params_for_label.append(("TEXTBOX_LABEL", f"GIFBlock {block.id}: {os.path.basename(block.selected_gif_path)}"))
                block.parameters = new_params_for_label

                # Schedule the GIF to be loaded and displayed
                self.canvas.after(100, block.load_and_display_gif)
        elif block_type == "svgblock": # Added for SVGBlock
            loaded_svg_path = data.get("selected_svg_path")
            if loaded_svg_path:
                block.selected_svg_path = loaded_svg_path
                # Update TEXTBOX_LABEL for SVGBlock
                new_params_svg_label = []
                svg_label_updated = False
                for name, val in block.parameters:
                    if name == "TEXTBOX_LABEL":
                        new_params_svg_label.append(("TEXTBOX_LABEL", f"SVGBlock {block.id}: {os.path.basename(block.selected_svg_path)}"))
                        svg_label_updated = True
                    else:
                        new_params_svg_label.append((name,val))
                if not svg_label_updated:
                    new_params_svg_label.append(("TEXTBOX_LABEL", f"SVGBlock {block.id}: {os.path.basename(block.selected_svg_path)}"))
                block.parameters = new_params_svg_label
                self.canvas.after(100, block.load_and_display_svg)
            else:
                # If no path, ensure TEXTBOX_LABEL reflects "No file" for SVGBlock
                new_params_svg_no_file = []
                svg_label_updated_no_file = False
                for name, val in block.parameters:
                    if name == "TEXTBOX_LABEL":
                        new_params_svg_no_file.append(("TEXTBOX_LABEL", f"SVGBlock {block.id}: (No file)"))
                        svg_label_updated_no_file = True
                    else:
                        new_params_svg_no_file.append((name,val))
                if not svg_label_updated_no_file:
                     new_params_svg_no_file.append(("TEXTBOX_LABEL", f"SVGBlock {block.id}: (No file)"))
                block.parameters = new_params_svg_no_file
        # The following 'else' was extraneous and incorrectly handled non-GIF/SVG blocks.
        # It duplicated the "No file" logic for GIFBlock.
        # Correct behavior is to fall through to block.update_text() for blocks
        # that don't have specific path loading logic (like DraggableBlock, SwitchBlock, etc.)
        # or for GIF/SVG blocks if their specific path logic was already handled above.

        block.update_text()  # Call update_text after all parameters are set
        # No direct call to self.app.update_layers_listbox() here,
        # it will be called by restore_state after all blocks are processed.
        return block

    def save_state(self):
        """Save state to a file"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
            
        # Сохраняем состояние в JSON файл
        state = self.get_state()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
            
        # Создаем отдельный временный файл для sys
        tmp_path = os.path.splitext(file_path)[0] + ".tmp"
        with open(tmp_path, 'wb') as tmp_file:
            # Сохраняем все файлы из sys
            sys_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sys")
            if os.path.exists(sys_dir):
                for file_name in os.listdir(sys_dir):
                    file_path = os.path.join(sys_dir, file_name)
                    if os.path.isfile(file_path):
                        # Записываем размер имени файла
                        name_size = len(file_name.encode('utf-8'))
                        tmp_file.write(name_size.to_bytes(4, 'big'))
                        # Записываем имя файла
                        tmp_file.write(file_name.encode('utf-8'))
                        # Читаем содержимое файла
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        # Записываем размер содержимого
                        tmp_file.write(len(content).to_bytes(4, 'big'))
                        # Записываем содержимое
                        tmp_file.write(content)
        
        self.app.show_notification(f"Project saved to {file_path} and {tmp_path}")
        
    def load_state(self):
        """Load state from a file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Load Project",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
            
        # Проверяем наличие временного файла
        tmp_path = os.path.splitext(file_path)[0] + ".tmp"
        if os.path.exists(tmp_path):
            # Очищаем sys директорию перед загрузкой
            sys_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sys")
            if os.path.exists(sys_dir):
                for file in os.listdir(sys_dir):
                    file_path = os.path.join(sys_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
            
            # Загружаем файлы из .tmp в sys
            with open(tmp_path, 'rb') as tmp_file:
                while True:
                    try:
                        # Читаем размер имени
                        name_size_bytes = tmp_file.read(4)
                        if not name_size_bytes:  # Конец файла
                            break
                        name_size = int.from_bytes(name_size_bytes, 'big')
                        # Читаем имя файла
                        file_name = tmp_file.read(name_size).decode('utf-8')
                        # Читаем размер содержимого
                        content_size = int.from_bytes(tmp_file.read(4), 'big')
                        # Читаем содержимое
                        content = tmp_file.read(content_size)
                        # Записываем в sys
                        sys_path = os.path.join("sys", file_name)
                        with open(sys_path, 'wb') as sys_file:
                            sys_file.write(content)
                    except Exception as e:
                        print(f"Error extracting file from tmp: {e}")
                        break
        
        # Восстанавливаем состояние
        with open(file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        self.restore_state(state)
        self.app.update_layers_listbox() # Update layers after full state restoration
        
        self.app.show_notification(f"Project loaded from {file_path}")

    def update_sys_path(self, file_name, file_path):
        """Update the sys_path dictionary with a new file path"""
        self.sys_path[file_name] = file_path

    def check_all_collisions(self):
        new_collisions_map = {}

        # Initialize map for all blocks
        for block in self.blocks:
            # Assuming all blocks in self.blocks are DraggableBlock or compatible
            # and have get_parameter and get_bounding_box methods.
            block_id_str = block.get_parameter("system_id")
            if block_id_str: # Ensure block_id_str is not None
                 new_collisions_map[block_id_str] = set()

        # Check for collisions between unique pairs of blocks
        for i in range(len(self.blocks)):
            block_a = self.blocks[i]
            # Ensure block_a and its ID are valid before proceeding
            id_a_str = block_a.get_parameter("system_id")
            if not id_a_str or not hasattr(block_a, 'get_bounding_box'):
                continue

            for j in range(i + 1, len(self.blocks)):
                block_b = self.blocks[j]
                # Ensure block_b and its ID are valid
                id_b_str = block_b.get_parameter("system_id")
                if not id_b_str or not hasattr(block_b, 'get_bounding_box'):
                    continue

                bbox_a = block_a.get_bounding_box()
                bbox_b = block_b.get_bounding_box()

                # Check for overlap
                # bbox_a: (min_x_a, min_y_a, max_x_a, max_y_a)
                # bbox_b: (min_x_b, min_y_b, max_x_b, max_y_b)
                overlap = (bbox_a[0] < bbox_b[2] and  # min_x_a < max_x_b
                           bbox_a[2] > bbox_b[0] and  # max_x_a > min_x_b
                           bbox_a[1] < bbox_b[3] and  # min_y_a < max_y_b
                           bbox_a[3] > bbox_b[1])     # max_y_a > min_y_b

                if overlap:
                    new_collisions_map[id_a_str].add(id_b_str)
                    new_collisions_map[id_b_str].add(id_a_str)

        # Update the 'collided' parameter for each block
        for block in self.blocks:
            block_id_str = block.get_parameter("system_id")
            if not block_id_str: # Skip if ID is somehow missing
                continue

            collided_ids_set = new_collisions_map.get(block_id_str, set())
            # Store as a string representation of a sorted list
            new_collided_list_as_str = str(sorted(list(collided_ids_set)))

            # Update the parameter in block.parameters
            updated = False
            new_params_for_block = []
            for name, val in block.parameters:
                if name == "collided":
                    new_params_for_block.append((name, new_collided_list_as_str))
                    updated = True
                else:
                    new_params_for_block.append((name, val))
            
            if not updated: # This case should not be reached if 'collided' is always initialized
                new_params_for_block.append(("collided", new_collided_list_as_str))
            
            block.parameters = new_params_for_block
            # No direct call to block.update_text() here, as this method
            # will be called by drag/resize which already handle text updates.

    def read_sys_files(self):
        """Возвращает список всех файлов, загруженных в проекте"""
        files_info = []
        
        # Проверяем все рабочие пространства
        for ws_id, workspace in self.workspaces.items():
            # Проверяем все блоки в рабочем пространстве
            for block in workspace.blocks:
                if isinstance(block, FileBlock) and block.cache_info:
                    file_info = {
                        "workspace": f"Interface {ws_id}",
                        "block_name": block.block_name,
                        "file_name": block.cache_info["file_name"],
                        "file_hash": block.cache_info["hash"],
                        "file_size": block.cache_info["size"]
                    }
                    files_info.append(file_info)
        
        # Форматируем вывод
        if not files_info:
            return "No files found in the project"
            
        result = []
        for file in files_info:
            result.append(f"Workspace: {file['workspace']}")
            result.append(f"Block: {file['block_name']}")
            result.append(f"File: {file['file_name']}")
            result.append(f"Size: {file['file_size']} bytes")
            result.append(f"Hash: {file['file_hash']}")
            result.append("---")
            
        return "\n".join(result)

    def read_sys_path(self):
        """Возвращает пути к системным файлам проекта"""
        paths_info = []
        
        # Проверяем все рабочие пространства
        for ws_id, workspace in self.workspaces.items():
            # Проверяем все блоки в рабочем пространстве
            for block in workspace.blocks:
                if isinstance(block, FileBlock) and block.cache_info:
                    # Получаем путь к файлу
                    file_path = block.get_file_path()
                    if file_path:
                        path_info = {
                            "workspace": f"Interface {ws_id}",
                            "block_name": block.block_name,
                            "file_name": block.cache_info["file_name"],
                            "file_path": file_path,
                            "cache_path": block.cache_info["cached_path"]
                        }
                        paths_info.append(path_info)
        
        # Форматируем вывод
        if not paths_info:
            return "No files found in the project"
            
        result = []
        for path in paths_info:
            result.append(f"Workspace: {path['workspace']}")
            result.append(f"Block: {path['block_name']}")
            result.append(f"File: {path['file_name']}")
            result.append(f"Temp path: {path['file_path']}")
            result.append(f"Cache path: {path['cache_path']}")
            result.append("---")
            
        return "\n".join(result)
        
    def register_block_for_canvas_update(self, block):
        """Регистрирует блок для обновления при перемещении холста"""
        if block not in self.canvas_update_blocks:
            self.canvas_update_blocks.append(block)
            
    def update_canvas_blocks(self):
        """Обновляет позиции всех зарегистрированных блоков"""
        zoom = getattr(self, 'current_scale', 1.0)
        for block in self.canvas_update_blocks:
            if hasattr(block, 'winfo_exists') and block.winfo_exists():  # Проверяем, что виджет все еще существует
                block.update_position_and_size(zoom)
            elif hasattr(block, 'update_position_and_size'):
                block.update_position_and_size(zoom)

# --- Контроллеры ---
class _ChangeBlockWrapper:
    def __init__(self, block_id):
        self.block_id = block_id; import __main__; self.app = __main__.app; self.block = None
        if str(self.block_id).lower()=="last":
            self.block = self.app._last_block
        else:
            for ws in self.app.workspaces.values():
                for b in ws.blocks:
                    if b.get_parameter("system_id")==str(self.block_id):
                        self.block = b; break
                if self.block: break
    def __getitem__(self, key):
        if self.block: return BlockWrapper(self.block)[key]
        raise KeyError("Block not found")
    def __setitem__(self, key, value):
        if self.block: BlockWrapper(self.block)[key] = value
        else: raise KeyError("Block not found")
class ChangeController:
    def __getitem__(self, block_id):
        return _ChangeBlockWrapper(block_id)
class _CreateBlockWrapper:
    def __init__(self, block_type):
        self.block_type = block_type.lower(); import __main__; self.app = __main__.app; self.created_block = None; self.pending_params = {}
    def __setitem__(self, param, value):
        self.pending_params[param.lower()] = value
        if self.created_block is None:
            mapping = {"normal": DraggableBlock, "switch": SwitchBlock, "file": FileBlock}
            block_class = mapping.get(value.lower(), DraggableBlock) if param.lower()=="type" else mapping.get("normal")
            ws = self.app.active_workspace or next(iter(self.app.workspaces.values()))
            x, y = ws._get_center_coords(120, 70)
            self.created_block = block_class(ws.canvas, x, y, ws.block_id, ws)
            ws.blocks.append(self.created_block); ws.block_id += 1; self.app._last_block = self.created_block
            for key_pending, val in self.pending_params.items():
                BlockWrapper(self.created_block)[key_pending] = val
            ws.save_undo_state(f"Создан блок {BlockWrapper(self.created_block)['type']} с параметрами {self.pending_params}")
        else:
            BlockWrapper(self.created_block)[param] = value
class CreateController:
    def __getitem__(self, block_type):
        return _CreateBlockWrapper(block_type)
class _RemoveBlockWrapper:
    def __init__(self, block_id):
        self.block_id = block_id; import __main__; self.app = __main__.app; self.block = None; self.workspace = None
        if str(self.block_id).lower()=="last":
            self.block = self.app._last_block
            for ws in self.app.workspaces.values():
                if self.block in ws.blocks:
                    self.workspace = ws; break
        else:
            for ws in self.app.workspaces.values():
                for b in ws.blocks:
                    if b.get_parameter("system_id")==str(self.block_id):
                        self.block = b; self.workspace = ws; break
                if self.block: break
    def __getitem__(self, key):
        return self
    def __setitem__(self, key, value):
        if self.block and self.workspace:
            self.workspace.remove_block(self.block)
        else:
            raise KeyError("Block not found")
class RemoveController:
    def __getitem__(self, block_id):
        return _RemoveBlockWrapper(block_id)
class _ReadBlockWrapper:
    def __init__(self, block_id):
        self.block_id = block_id; import __main__; self.app = __main__.app; self.block = None
        if str(self.block_id).lower()=="last":
            self.block = self.app._last_block
        else:
            for ws in self.app.workspaces.values():
                for b in ws.blocks:
                    if b.get_parameter("system_id")==str(self.block_id):
                        self.block = b; break
                if self.block: break
    def __getitem__(self, key):
        if self.block: return BlockWrapper(self.block)[key]
        raise KeyError("Block not found")
class ReadController:
    def __getitem__(self, block_id):
        return _ReadBlockWrapper(block_id)
class StoreController:
    def __getitem__(self, param):
        import __main__; app = __main__.app; results = []
        for ws in app.workspaces.values():
            for b in ws.blocks:
                for key, value in b.parameters:
                    if key==param:
                        try: sid = int(b.get_parameter("system_id"))
                        except: sid = b.get_parameter("system_id")
                        results.append(sid); break
        return results

change = ChangeController(); create = CreateController(); remove = RemoveController(); read = ReadController(); store = StoreController()

# --- Основное приложение ---
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        # Clear sys directory on startup
        ensure_sys_dir()
        
        self.title("Z-K-Z-G")
        self.geometry("800x600")
        self.configure(bg="#111111")
        
        # Initialize sys_path dictionary for storing file paths
        self.sys_path = {}
        
        # Create notification frame
        self.notification_frame = tk.Frame(self, bg="#111111")
        self.notification_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Create tab bar
        self.tab_bar = tk.Frame(self, bg="#333333")
        self.tab_bar = tk.Frame(self, bg="#333333")
        self.tab_bar.pack(side=tk.TOP, fill=tk.X)
        self.tab_frames = []
        self.workspace_container = tk.Frame(self, bg="#111111")
        self.workspace_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Pack to the left

        # Layers Menu Frame
        self.layers_menu_frame = tk.Frame(self, bg="#2B2B2B", width=200) # Adjusted background
        self.layers_menu_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Layers Listbox
        self.layers_listbox = tk.Listbox(
            self.layers_menu_frame,
            bg="#1E1E1E",  # Dark background
            fg="#FFD700",  # Light text (gold)
            selectbackground="#333333", # Darker selection
            selectforeground="#FFFFFF", # White selected text
            highlightthickness=0,
            bd=0,
            font=("Consolas", 10)
        )
        self.layers_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.layers_listbox.bind("<ButtonPress-1>", self.on_layers_listbox_drag_start)
        self.layers_listbox.bind("<B1-Motion>", self.on_layers_listbox_drag_motion)
        self.layers_listbox.bind("<ButtonRelease-1>", self.on_layers_listbox_drag_release)

        self.dragged_item_index = None
        self.drag_start_y = None

        self.workspaces = {}
        self.active_workspace = None
        self.next_ws_id = 1
        tk.Button(self.tab_bar, text="+", command=self.add_new_workspace, bg="#444444", fg="#FFD700", bd=0, font=("Consolas", 12, "bold"))\
          .pack(side=tk.RIGHT, padx=2, pady=2)
        self.add_new_workspace()
        start_api_server(self, host="localhost", port=8080)
        self.tab_drag_data = None
        self.update_layers_listbox() # Initial population for the first workspace
        self.bind_all("<Control-z>", self.undo_event)
        self.bind_all("<Control-Z>", self.undo_event)
        self.bind_all("<Control-Shift-z>", self.redo_event)
        self.bind_all("<Control-Shift-Z>", self.redo_event)
        self.notification_frame = tk.Frame(self, bg="#111111")
        self.notification_frame.place(relx=1.0, y=10, anchor="ne")
        self.create = CreateController()
        self.change = ChangeController()
        self.remove = RemoveController()
        self.read = ReadController()
        self.store = StoreController()
        self._last_block = None

    def on_tab_press(self, event):
        widget = event.widget if isinstance(event.widget, tk.Frame) else event.widget.master
        self.tab_drag_data = {"tab": widget, "start_x": event.x_root, "orig_index": self.tab_frames.index(widget)}
    def on_tab_motion(self, event):
        if not self.tab_drag_data: return
        pointer_x = event.x_root - self.tab_bar.winfo_rootx()
        new_index = self.tab_drag_data["orig_index"]
        for idx, tab in enumerate(self.tab_frames):
            if tab == self.tab_drag_data["tab"]: continue
            if pointer_x < tab.winfo_x() + tab.winfo_width()/2:
                new_index = idx; break
            else:
                new_index = idx + 1
        current_index = self.tab_frames.index(self.tab_drag_data["tab"])
        if new_index != current_index:
            tab = self.tab_frames.pop(current_index)
            self.tab_frames.insert(new_index, tab)
            for tab in self.tab_frames: tab.pack_forget()
            for tab in self.tab_frames: tab.pack(side=tk.LEFT, padx=2, pady=2)
            self.tab_drag_data["orig_index"] = new_index
    def on_tab_release(self, event):
        if self.tab_drag_data is not None:
            dx = event.x_root - self.tab_drag_data["start_x"]
            if abs(dx) < 5:
                widget = self.tab_drag_data["tab"]
                if hasattr(widget, "ws_id"):
                    self.switch_workspace(widget.ws_id)
        self.tab_drag_data = None
    def undo_event(self, event):
        if self.active_workspace: self.active_workspace.perform_undo()
    def redo_event(self, event):
        if self.active_workspace: self.active_workspace.perform_redo()
    def add_new_workspace(self):
        ws_id = self.next_ws_id; self.next_ws_id += 1
        workspace = Workspace(self.workspace_container, ws_id); workspace.app = self; self.workspaces[ws_id] = workspace
        tab_frame = tk.Frame(self.tab_bar, bg="#555555", bd=1, relief=tk.RAISED); tab_frame.pack(side=tk.LEFT, padx=2, pady=2)
        tab_frame.ws_id = ws_id
        self.tab_frames.append(tab_frame)
        tab_label = tk.Label(tab_frame, text=f"Interface {ws_id}", bg="#555555", fg="#FFD700", font=("Consolas", 10))
        tab_label.ws_id = ws_id
        tab_label.pack(side=tk.LEFT, padx=5)
        close_button = tk.Button(tab_frame, text="x", bg="#FF5555", fg="white", bd=0, font=("Consolas", 8),
                                  command=lambda ws_id=ws_id, tf=tab_frame: self.close_workspace(ws_id, tf))
        close_button.pack(side=tk.RIGHT, padx=2)
        for widget in (tab_frame, tab_label):
            widget.bind("<ButtonPress-1>", self.on_tab_press)
            widget.bind("<B1-Motion>", self.on_tab_motion)
            widget.bind("<ButtonRelease-1>", self.on_tab_release)
        workspace.tab_frame = tab_frame; workspace.pack_forget(); self.switch_workspace(ws_id)
    def switch_workspace(self, ws_id):
        if self.active_workspace:
            self.active_workspace.pack_forget()
            self.active_workspace.tab_frame.config(bg="#555555")
            for child in self.active_workspace.tab_frame.winfo_children():
                child.config(bg="#555555")
        self.active_workspace = self.workspaces.get(ws_id)
        if self.active_workspace:
            self.active_workspace.pack(fill=tk.BOTH, expand=True)
            self.active_workspace.tab_frame.config(bg="#777777")
            for child in self.active_workspace.tab_frame.winfo_children():
                child.config(bg="#777777")
        self.update_layers_listbox() # Update layers when switching workspace

    def close_workspace(self, ws_id, tab_frame):
        if not messagebox.askyesno("Закрыть вкладку", "Вы уверены, что хотите закрыть эту вкладку?"): return
        
        workspace_to_close = self.workspaces.get(ws_id)
        if workspace_to_close and workspace_to_close.is_gif_playing:
            workspace_to_close.stop_gif_playback()

        if self.active_workspace and self.active_workspace.ws_id == ws_id:
            self.active_workspace.pack_forget(); self.active_workspace = None
        
        workspace = self.workspaces.pop(ws_id, None) # Use the already fetched workspace_to_close if needed, but pop is fine
        if workspace: 
            workspace.destroy()
            
        if tab_frame in self.tab_frames: 
            self.tab_frames.remove(tab_frame)
            tab_frame.destroy()
            
        if self.active_workspace is None and self.workspaces:
            self.switch_workspace(next(iter(self.workspaces)))
        self.update_layers_listbox() # Update layers after closing a workspace
            
    def show_notification(self, text):
        label = tk.Label(self.notification_frame, text=text, fg="#FFD700", bg="#111111", font=("Consolas", 10))
        label.pack()
        self.after(3000, label.destroy)

    def update_layers_listbox(self):
        """Populates the layers listbox with items from the active workspace."""
        self.layers_listbox.delete(0, tk.END)  # Clear existing items
        if self.active_workspace:
            # Add blocks to the listbox
            for block in self.active_workspace.blocks:
                # Attempt to get a display name for the block
                display_name = getattr(block, 'block_name', f"Block {block.id}")
                # You might want to get a more specific name if available, e.g., from parameters
                try:
                    name_param = next(p[1] for p in block.parameters if p[0] == "TEXTBOX_LABEL")
                    if name_param:
                        display_name = name_param
                except StopIteration:
                    pass # Use default if TEXTBOX_LABEL not found
                except AttributeError: # If block.parameters doesn't exist or is not iterable
                    pass

                # Store ID and display name, separated by "::"
                self.layers_listbox.insert(tk.END, f"{block.id}::{display_name}")

            # Add other canvas items if necessary (e.g., specific shapes, images)
            # For now, we'll just list blocks.
            # Example for listing all canvas items (might be too verbose):
            # for item_id in self.active_workspace.canvas.find_all():
            #    item_type = self.active_workspace.canvas.type(item_id)
            #    self.layers_listbox.insert(tk.END, f"{item_type.capitalize()}: {item_id}")
        self.layers_listbox.update_idletasks() # Ensure listbox updates immediately

    def on_layers_listbox_drag_start(self, event):
        self.dragged_item_index = self.layers_listbox.nearest(event.y)
        self.drag_start_y = event.y
        # Optionally, visually indicate the start of a drag
        # self.layers_listbox.itemconfig(self.dragged_item_index, {'bg': '#444444'}) # Example: change background

    def on_layers_listbox_drag_motion(self, event):
        if self.dragged_item_index is None:
            return

        current_y = event.y
        # For visual feedback during drag, activate item under cursor
        current_item_index = self.layers_listbox.nearest(current_y)
        if current_item_index != self.layers_listbox.curselection():
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(current_item_index)
            self.layers_listbox.activate(current_item_index)

    def on_layers_listbox_drag_release(self, event):
        if self.dragged_item_index is None:
            return

        drop_item_index = self.layers_listbox.nearest(event.y)

        if drop_item_index != self.dragged_item_index:
            dragged_item_text = self.layers_listbox.get(self.dragged_item_index)
            
            # Adjust drop_item_index if dragging downwards and item is removed before insertion point
            # This is tricky with tk.Listbox direct manipulation if not careful.
            # A common approach is to remove then insert.
            
            self.layers_listbox.delete(self.dragged_item_index)
            self.layers_listbox.insert(drop_item_index, dragged_item_text)
            
            # Update selection to the new position
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(drop_item_index)
            self.layers_listbox.activate(drop_item_index)

            # Placeholder for updating Z-order on canvas
            self.update_block_z_order() 

        # Reset drag state
        # self.layers_listbox.itemconfig(self.dragged_item_index, {'bg': '#1E1E1E'}) # Reset visual indication
        self.dragged_item_index = None
        self.drag_start_y = None
        # self.app.update_layers_listbox() # Refresh listbox to ensure correct display. This might be redundant if update_block_z_order handles it or if it's called after z-order
        # update_layers_listbox is primarily for populating/repopulating. Z-order is a consequence of reordering.
        # Let's rely on the call in on_layers_listbox_drag_release after update_block_z_order if needed.
        # For now, the primary concern is that update_block_z_order itself correctly reads the listbox.

    def update_block_z_order(self):
        """
        Updates the Z-order of blocks on the canvas based on their order
        in the layers_listbox. Blocks at the top of the listbox appear
        on top of other blocks on the canvas.
        """
        if not self.active_workspace:
            return

        listbox_items = self.layers_listbox.get(0, tk.END)
        if not listbox_items:
            return

        # Create a mapping from block_id to block instance for efficient lookup
        id_to_block_map = {str(block.id): block for block in self.active_workspace.blocks}

        ordered_blocks = []
        for item_text in listbox_items:
            try:
                block_id_str = item_text.split("::", 1)[0]
                block = id_to_block_map.get(block_id_str)
                if block:
                    ordered_blocks.append(block)
                else:
                    print(f"Warning: Could not find block for listbox item ID: {block_id_str} in item: {item_text}")
            except IndexError:
                print(f"Warning: Could not parse block ID from listbox item: {item_text}")

        # Raise blocks in reverse order of the listbox
        # (item at index 0 in listbox should be raised last, thus on top)
        for block in reversed(ordered_blocks):
            common_tag = f"block_all_{block.id}"
            self.active_workspace.canvas.tag_raise(common_tag)
            # To ensure grid lines are always at the bottom if they exist
            self.active_workspace.canvas.tag_lower("grid_line")


        # After reordering, it's good practice to update the canvas
        self.active_workspace.canvas.update_idletasks()
        # No need to call self.update_layers_listbox() here as the listbox order is the source of truth.


class TkinterBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        # Инициализируем атрибуты для UI до вызова super().__init__
        self.ui_frame = None
        self.ui_window = None
        self.base_font_size = 10  # Базовый размер шрифта для UI элементов
        self.resize_handle = None  # Дескриптор для изменения размера
        self.close_button = None  # Кнопка закрытия
        self.standalone_window = None  # Отдельное окно, если запущено отдельно
        
        super().__init__(canvas, x, y, id, app)
        self.block_name = f"TkinterBlock {id}"
        
        common_tag = f"block_all_{self.id}" # Ensure common_tag for TkinterBlock elements
        # Создаем элементы блока
        self.tkinter_button = self.canvas.create_rectangle(x+10, y+10, x+100, y+30,
                                                      fill="#444444", outline="#FFD700", width=1,
                                                      tags=(f"tkinter_{id}", "tkinter_button", "block", common_tag))
        self.tkinter_text = self.canvas.create_text(x+55, y+20, text="Tkinter UI", fill="#888888",
                                               font=("Consolas", 10, "bold"), tags=(f"tkinter_{id}", "tkinter_text", "block", common_tag))
        
        # Добавляем привязки событий
        for item in [self.tkinter_button, self.tkinter_text]: # These items already have common_tag
            self.canvas.tag_bind(item, "<Button-1>", self.edit_tkinter_ui)
        
        # Устанавливаем базовый код для Tkinter UI
        self.script_code = DEFAULT_SCRIPT_INSTRUCTIONS + '''
# Пример Tkinter UI внутри блока:
def create_ui(parent, tk):
    # Создаем фрейм для интерфейса с отступами
    frame = tk.Frame(parent, bg="#333333", padx=10, pady=10)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Добавляем виджеты
    label = tk.Label(frame, text="Встроенный Tkinter UI", bg="#333333", fg="#FFD700", font=("Consolas", 12))
    label.pack(pady=10)
    
    entry = tk.Entry(frame, bg="#444444", fg="#FFD700", insertbackground="#FFD700")
    entry.pack(pady=5, fill=tk.X)
    
    def on_button_click():
        text = entry.get()
        if text:
            label.config(text="Введено: " + text)
        else:
            label.config(text="Введите текст")
    
    button = tk.Button(frame, text="Нажми меня", bg="#555555", fg="#FFD700", 
                      command=on_button_click)
    button.pack(pady=5)
    
    # Добавляем текстовое поле
    text = tk.Text(frame, height=5, bg="#444444", fg="#FFD700", insertbackground="#FFD700")
    text.pack(pady=5, fill=tk.BOTH, expand=True)
    text.insert("1.0", "Это встроенный Tkinter интерфейс\\nвнутри блока.")

create_ui(parent, tk)
'''
        self.update_text()
        
    def update_text(self):
        # Сначала вызываем родительский метод
        super().update_text()
        
        # Затем обновляем наши элементы
        scale = self.app.current_scale
        cx = (self.world_x+self.world_width/2)*scale
        cy = (self.world_y+self.world_height/2)*scale
        
        # Получаем базовый размер шрифта
        try:
            base_font_size = int(self.get_parameter("FONT_SIZE"))
        except:
            base_font_size = self.base_font_size
            
        # Вычисляем эффективный размер шрифта
        effective_font_size = max(1, int(base_font_size * scale))
        
        # Обновляем позиции кнопки и текста
        if hasattr(self, 'tkinter_button'):
            self.canvas.coords(self.tkinter_button, 
                             cx-45, cy-20,  # левый верхний угол
                             cx+45, cy)     # правый нижний угол
                             
        if hasattr(self, 'tkinter_text'):
            self.canvas.coords(self.tkinter_text, cx, cy-10)
            self.canvas.itemconfigure(self.tkinter_text, font=("Consolas", effective_font_size, "bold"))
            if self.get_parameter("light")=="1":
                self.canvas.itemconfigure(self.tkinter_text, text="Tkinter UI", fill="#FFD700")
            else:
                self.canvas.itemconfigure(self.tkinter_text, text="Tkinter UI", fill="#888888")
        
        # Обновляем позицию UI фрейма, если он существует
        if hasattr(self, 'ui_window') and self.ui_window is not None:
            # Обновляем размер контейнера с учетом размера блока
            self.update_container_size()
            
            # Перемещаем кнопки управления ниже интерфейса
            self.update_control_buttons_position()
            
            # Обновляем позицию дескриптора изменения размера
            self.update_resize_handle()
            
            # Обновляем позицию кнопки закрытия
            self.update_close_button()
    
    def update_resize_handle(self):
        """Обновляет позицию и размер дескриптора изменения размера"""
        if not hasattr(self, 'ui_window') or self.ui_window is None:
            return
            
        scale = self.app.current_scale
        block_x = self.world_x * scale
        block_y = self.world_y * scale
        block_width = self.world_width * scale
        block_height = self.world_height * scale
        
        # Вычисляем позицию для дескриптора изменения размера
        handle_y = block_y + block_height + 30 * scale  # Ниже кнопок управления
        
        # Если дескриптор еще не создан, создаем его
        if self.resize_handle is None:
            common_tag = f"block_all_{self.id}" # Ensure common_tag
            # Создаем невидимый дескриптор для изменения размера
            self.resize_handle = self.canvas.create_rectangle(
                block_x + block_width/2 - 20, handle_y,
                block_x + block_width/2 + 20, handle_y + 10,
                fill="", outline="", width=0,  # Делаем дескриптор невидимым
                tags=(f"tkinter_{self.id}", "resize_handle", "block", common_tag)
            )
            
            # Добавляем привязки событий для изменения размера
            self.canvas.tag_bind(self.resize_handle, "<Button-1>", self.start_resize)
            self.canvas.tag_bind(self.resize_handle, "<B1-Motion>", self.do_resize)
            self.canvas.tag_bind(self.resize_handle, "<ButtonRelease-1>", self.stop_resize)
            
            # Добавляем привязку для изменения курсора при наведении
            self.canvas.tag_bind(self.resize_handle, "<Enter>", lambda e: self.canvas.config(cursor="size"))
            self.canvas.tag_bind(self.resize_handle, "<Leave>", lambda e: self.canvas.config(cursor=""))
        else:
            # Обновляем позицию существующего дескриптора
            self.canvas.coords(
                self.resize_handle,
                block_x + block_width/2 - 20, handle_y,
                block_x + block_width/2 + 20, handle_y + 10
            )
    
    def start_resize(self, event):
        """Начало изменения размера блока"""
        self.app.save_undo_state("Начало изменения размера Tkinter блока")
        self.canvas.config(cursor="size")
        self.resize_start_x = event.x
        self.resize_start_y = event.y
        self.resize_start_width = self.world_width
        self.resize_start_height = self.world_height
    
    def do_resize(self, event):
        """Изменение размера блока"""
        # Вычисляем изменение размеров
        delta_x = (event.x - self.resize_start_x) / self.app.current_scale
        delta_y = (event.y - self.resize_start_y) / self.app.current_scale
        
        # Вычисляем новые размеры
        new_width = max(100, self.resize_start_width + delta_x)
        new_height = max(100, self.resize_start_height + delta_y)
        
        # Обновляем размеры блока
        self.world_width = new_width
        self.world_height = new_height
        
        # Обновляем отображение блока
        self.update_text()
    
    def stop_resize(self, event):
        """Завершение изменения размера блока"""
        self.canvas.config(cursor="")
        self.app.save_undo_state("Изменение размера Tkinter блока")
    
    def update_control_buttons_position(self):
        """Обновляет позицию кнопок управления, размещая их ниже интерфейса"""
        if not hasattr(self, 'ui_window') or self.ui_window is None:
            return
            
        scale = self.app.current_scale
        block_x = self.world_x * scale
        block_y = self.world_y * scale
        block_height = self.world_height * scale
        
        # Вычисляем позицию для кнопок управления (ниже интерфейса)
        buttons_y = block_y + block_height + 10 * scale
        
        # Размеры кнопок
        button_width = 40 * scale
        button_height = 20 * scale
        button_spacing = 10 * scale
        
        # Обновляем позиции кнопок управления
        if hasattr(self, 'edit_button'):
            self.canvas.coords(self.edit_button, 
                             block_x + 10, buttons_y, 
                             block_x + 10 + button_width, buttons_y + button_height)
        if hasattr(self, 'run_button'):
            self.canvas.coords(self.run_button, 
                             block_x + 10 + button_width + button_spacing, buttons_y, 
                             block_x + 10 + button_width * 2 + button_spacing, buttons_y + button_height)
        if hasattr(self, 'output_button'):
            self.canvas.coords(self.output_button, 
                             block_x + 10 + button_width * 2 + button_spacing * 2, buttons_y, 
                             block_x + 10 + button_width * 3 + button_spacing * 2, buttons_y + button_height)
        if hasattr(self, 'delete_button'):
            self.canvas.coords(self.delete_button, 
                             block_x + 10 + button_width * 3 + button_spacing * 3, buttons_y, 
                             block_x + 10 + button_width * 4 + button_spacing * 3, buttons_y + button_height)
    
    def edit_tkinter_ui(self, event):
        self.app.save_undo_state("Редактирование Tkinter UI")
        win = tk.Toplevel(self.app)
        win.title(f"Редактирование Tkinter UI блока {self.block_name}")
        editor = CodeEditor(win, text=self.script_code)
        editor.pack(fill=tk.BOTH, expand=True)
        
        def save_and_close():
            self.script_code = editor.get_text()
            self.app.save_undo_state("Изменён Tkinter UI")
            win.destroy()
            
        tk.Button(win, text="Сохранить", command=save_and_close, 
                 bg="#333333", fg="#FFD700", font=("Consolas", 10)).pack(pady=5)
    
    def run_script(self, event=None, auto_run=False):
        # Удаляем старый UI, если есть
        if self.ui_frame is not None:
            self.ui_frame.destroy()
            self.ui_frame = None
        if self.ui_window is not None:
            self.canvas.delete(self.ui_window)
            self.ui_window = None
        
        # Закрываем отдельное окно, если оно было открыто
        if self.standalone_window is not None:
            try:
                self.standalone_window.destroy()
            except:
                pass
            self.standalone_window = None
        
        # Создаем контейнер для UI
        scale = self.app.current_scale
        
        # Создаем фрейм для UI
        self.ui_frame = tk.Frame(self.canvas, bg="#222222")
        
        # Создаем окно внутри блока с учетом его границ
        block_x = self.world_x * scale
        block_y = self.world_y * scale
        block_width = self.world_width * scale
        block_height = self.world_height * scale
        
        # Создаем окно с учетом границ блока
        self.ui_window = self.canvas.create_window(
            block_x + block_width/2,  # x координата центра блока
            block_y + block_height/2,  # y координата центра блока
            window=self.ui_frame,
            anchor="center",
            width=block_width,  # Устанавливаем ширину равной ширине блока
            height=block_height  # Устанавливаем высоту равной высоте блока
        )
        
        # Готовим окружение для пользовательского кода
        env = {
            "tk": tk,
            "parent": self.ui_frame,
            "__name__": "__main__",
            "scale": scale,  # Передаем текущий масштаб в пользовательский код
            "base_font_size": self.base_font_size  # Передаем базовый размер шрифта
        }
        
        try:
            # Выполняем код в отдельном потоке, чтобы не блокировать основной интерфейс
            def run_code():
                try:
                    # Добавляем функцию для создания виджетов с учетом масштаба
                    def create_scaled_widget(widget_class, *args, **kwargs):
                        # Если есть параметр font, масштабируем его
                        if 'font' in kwargs:
                            font_parts = kwargs['font'].split()
                            if len(font_parts) >= 2:
                                try:
                                    size = int(font_parts[1])
                                    # Компенсируем масштаб для размера шрифта
                                    scaled_size = int(size / scale)
                                    font_parts[1] = str(scaled_size)
                                    kwargs['font'] = ' '.join(font_parts)
                                except:
                                    pass
                        return widget_class(*args, **kwargs)
                    
                    # Добавляем функцию в окружение
                    env['create_scaled_widget'] = create_scaled_widget
                    
                    # Выполняем пользовательский код
                    exec(self.script_code, env)
                    
                    # После выполнения кода обновляем размер контейнера
                    self.app.after(100, self.update_container_size)
                except Exception as e:
                    # Создаем метку с ошибкой в основном потоке
                    self.app.after(0, lambda: self.show_error(str(err)))
            
            threading.Thread(target=run_code, daemon=True).start()
        except Exception as e:
            self.show_error(str(e))
    
    def run_standalone(self):
        """Запускает Tkinter UI в отдельном окне"""
        # Закрываем UI в блоке, если он был открыт
        self.close_tkinter_ui(None)
        
        # Создаем отдельное окно
        self.standalone_window = tk.Toplevel(self.app)
        self.standalone_window.title(f"Tkinter UI - {self.block_name}")
        
        # Устанавливаем протокол закрытия окна
        self.standalone_window.protocol("WM_DELETE_WINDOW", self.on_standalone_close)
        
        # Создаем фрейм для UI
        self.ui_frame = tk.Frame(self.standalone_window, bg="#222222")
        self.ui_frame.pack(fill=tk.BOTH, expand=True)
        
        # Готовим окружение для пользовательского кода
        env = {
            "tk": tk,
            "parent": self.ui_frame,
            "__name__": "__main__",
            "scale": 1.0,  # В отдельном окне масштаб всегда 1.0
            "base_font_size": self.base_font_size
        }
        
        try:
            # Выполняем код в отдельном потоке
            def run_code():
                try:
                    # Добавляем функцию для создания виджетов
                    def create_scaled_widget(widget_class, *args, **kwargs):
                        return widget_class(*args, **kwargs)
                    
                    # Добавляем функцию в окружение
                    env['create_scaled_widget'] = create_scaled_widget
                    
                    # Выполняем пользовательский код
                    exec(self.script_code, env)
                except Exception as e:
                    # Показываем ошибку в основном потоке
                    self.app.after(0, lambda: self.show_error(str(e)))
            
            threading.Thread(target=run_code, daemon=True).start()
        except Exception as e:
            self.show_error(str(e))
    
    def on_standalone_close(self):
        """Обработчик закрытия отдельного окна"""
        # Закрываем окно
        if self.standalone_window is not None:
            self.standalone_window.destroy()
            self.standalone_window = None
        
        # Симулируем нажатие кнопки закрытия
        self.close_tkinter_ui(None)
    
    def close_tkinter_ui(self, event):
        """Закрывает Tkinter UI"""
        # Удаляем UI фрейм
        if self.ui_frame is not None:
            self.ui_frame.destroy()
            self.ui_frame = None
        
        # Удаляем окно
        if self.ui_window is not None:
            self.canvas.delete(self.ui_window)
            self.ui_window = None
        
        # Удаляем кнопку закрытия
        if self.close_button is not None:
            self.canvas.delete(self.close_button)
            self.close_button = None
        
        # Удаляем текст кнопки закрытия
        if hasattr(self, 'close_text'):
            self.canvas.delete(self.close_text)
            delattr(self, 'close_text')
        
        # Обновляем отображение блока
        self.update_text()
    
    def update_container_size(self):
        """Обновляет размер контейнера в зависимости от размера блока"""
        if self.ui_frame is not None and self.ui_window is not None:
            # Получаем размер блока с учетом масштаба
            scale = self.app.current_scale
            block_width = int(self.world_width * scale)
            block_height = int(self.world_height * scale)
            
            # Обновляем размер окна
            self.canvas.itemconfigure(self.ui_window, width=block_width, height=block_height)
            
            # Обновляем размер фрейма
            self.ui_frame.configure(width=block_width, height=block_height)
            
            # Обновляем позицию окна
            block_x = self.world_x * scale
            block_y = self.world_y * scale
            self.canvas.coords(
                self.ui_window,
                block_x + block_width/2,  # x координата центра блока
                block_y + block_height/2   # y координата центра блока
            )
            
            # Принудительно обновляем виджеты
            self.ui_frame.update_idletasks()
            
            # Обновляем позицию кнопок управления
            self.update_control_buttons_position()
    
    def show_error(self, error_message):
        """Показывает ошибку в UI фрейме"""
        if self.ui_frame is not None:
            # Очищаем фрейм
            for widget in self.ui_frame.winfo_children():
                widget.destroy()
            
            # Создаем метку с ошибкой
            label = tk.Label(self.ui_frame, text=f"Ошибка: {error_message}", 
                           fg="red", bg="#222222", wraplength=200)
            label.pack(pady=10)
    
    def update_close_button(self):
        """Обновляет позицию и размер кнопки закрытия"""
        if not hasattr(self, 'ui_window') or self.ui_window is None:
            return
            
        scale = self.app.current_scale
        block_x = self.world_x * scale
        block_y = self.world_y * scale
        block_width = self.world_width * scale
        block_height = self.world_height * scale
        
        # Размеры кнопки закрытия
        button_width = 60 * scale
        button_height = 20 * scale
        
        # Вычисляем позицию для кнопки закрытия (под блоком)
        button_y = block_y + block_height + 40 * scale  # Ниже кнопок управления
        
        # Если кнопка закрытия еще не создана, создаем ее
        if self.close_button is None:
            # Создаем кнопку закрытия под блоком
            common_tag = f"block_all_{self.id}" # Ensure common_tag
            # Создаем кнопку закрытия под блоком
            self.close_button = self.canvas.create_rectangle(
                block_x + block_width/2 - button_width/2, button_y,
                block_x + block_width/2 + button_width/2, button_y + button_height,
                fill="#FF5555", outline="#FFD700", width=1,
                tags=(f"tkinter_{self.id}", "close_button", "block", common_tag)
            )
            
            # Создаем текст "Закрыть" на кнопке
            self.close_text = self.canvas.create_text(
                block_x + block_width/2, button_y + button_height/2,
                text="Закрыть", fill="#FFFFFF", font=("Consolas", int(10 * scale), "bold"),
                tags=(f"tkinter_{self.id}", "close_text", "block", common_tag)
            )
            
            # Добавляем привязки событий для кнопки закрытия
            for item in [self.close_button, self.close_text]: # These items already have common_tag
                self.canvas.tag_bind(item, "<Button-1>", self.close_tkinter_ui)
                self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.itemconfigure(self.close_button, fill="#FF7777"))
                self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.itemconfigure(self.close_button, fill="#FF5555"))
        else:
            # Обновляем позицию существующей кнопки закрытия
            self.canvas.coords(
                self.close_button,
                block_x + block_width/2 - button_width/2, button_y,
                block_x + block_width/2 + button_width/2, button_y + button_height
            )
            
            # Обновляем позицию текста
            self.canvas.coords(
                self.close_text,
                block_x + block_width/2, button_y + button_height/2
            )
            
            # Обновляем размер шрифта
            self.canvas.itemconfigure(self.close_text, font=("Consolas", int(10 * scale), "bold"))
    
    def close_tkinter_ui(self, event):
        """Закрывает Tkinter UI"""
        # Удаляем UI фрейм
        if self.ui_frame is not None:
            self.ui_frame.destroy()
            self.ui_frame = None
        
        # Удаляем окно
        if self.ui_window is not None:
            self.canvas.delete(self.ui_window)
            self.ui_window = None
        
        # Удаляем кнопку закрытия
        if self.close_button is not None:
            self.canvas.delete(self.close_button)
            self.close_button = None
        
        # Удаляем текст кнопки закрытия
        if hasattr(self, 'close_text'):
            self.canvas.delete(self.close_text)
            delattr(self, 'close_text')
        
        # Обновляем отображение блока
        self.update_text()

# --- GIFBlock ---
class GIFBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        # Initialize GIF-specific attributes before super().__init__
        self.gif_pil_frames = []
        self.gif_image_info = {}
        self.current_gif_frame_index = 0
        self.gif_animation_after_id = None
        self.selected_gif_path = None
        self.gif_label = None  # Will be a tk.Label widget
        self.gif_label_window_id = None # ID from canvas.create_window
        self.is_gif_playing = False

        super().__init__(canvas, x, y, id, app)
        
        self.block_name = f"GIFBlock {self.id}"

        # Update parameters: remove old 'type' and 'TEXTBOX_LABEL', add new ones
        new_params = []
        for name, val in self.parameters:
            if name.lower() == "type":
                continue 
            if name == "TEXTBOX_LABEL":
                continue
            new_params.append((name, val))
        
        new_params.append(("type", "gifblock"))
        new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: (No file)"))
        
        self.parameters = new_params
        
        self.update_text()
        # Changed to Double-Button-1 to avoid conflict with dragging
        self.canvas.tag_bind(self.block, "<Double-Button-1>", self.select_gif_file)

    def serialize(self):
        data = super().serialize()  # Get data from DraggableBlock.serialize
        data["type"] = "gifblock"  # Explicitly set type for deserialization
        data["selected_gif_path"] = self.selected_gif_path
        return data

    def select_gif_file(self, event):
        filepath = filedialog.askopenfilename(
            title="Select GIF file",
            filetypes=[("GIF files", "*.gif")]
        )
        if filepath:
            self.selected_gif_path = filepath
            
            new_params = []
            textbox_label_found = False
            for name, val in self.parameters:
                if name == "TEXTBOX_LABEL":
                    new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: {os.path.basename(self.selected_gif_path)}"))
                    textbox_label_found = True
                else:
                    new_params.append((name, val))
            
            if not textbox_label_found: # Should always be found due to __init__
                new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: {os.path.basename(self.selected_gif_path)}"))
            
            self.parameters = new_params
            self.update_text() # Update text first to reflect new label
            self.load_and_display_gif() # Then load and display
        # If no file is selected, do nothing

    def load_and_display_gif(self):
        if self.is_gif_playing:
            self.stop_gif_animation()

        self.gif_pil_frames.clear()
        self.gif_image_info = {} # Cleared, was using .clear() which is for dicts

        if not self.selected_gif_path:
            # This case should ideally be handled by select_gif_file not calling this
            # or by UI preventing this call if no path.
            # However, as a safeguard:
            self.update_text() # Ensure label is updated if path is somehow None
            return

        try:
            gif_image = Image.open(self.selected_gif_path)
            self.gif_image_info = gif_image.info # info is a dict, not a method
            while True:
                try:
                    gif_image.seek(len(self.gif_pil_frames))
                    self.gif_pil_frames.append(gif_image.copy())
                except EOFError:
                    break
        except Exception as e:
            print(f"Error loading GIF {self.selected_gif_path}: {e}")
            self.selected_gif_path = None
            # Update TEXTBOX_LABEL parameter
            new_params = []
            for name, val in self.parameters:
                if name == "TEXTBOX_LABEL":
                    new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: (No file)"))
                else:
                    new_params.append((name, val))
            self.parameters = new_params
            self.update_text()
            return

        if not self.gif_pil_frames:
            print(f"No frames found in GIF: {self.selected_gif_path}")
            self.selected_gif_path = None # Reset path
            # Update TEXTBOX_LABEL parameter
            new_params = []
            for name, val in self.parameters:
                if name == "TEXTBOX_LABEL":
                    new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: (No file)"))
                else:
                    new_params.append((name, val))
            self.parameters = new_params
            self.update_text()
            return

        if self.gif_label is None:
            self.gif_label = tk.Label(self.canvas, bg="#000000") # Black background for GIF label

        self.is_gif_playing = True # Set before calling update_gif_label_window
        self.update_gif_label_window() # Create/update canvas window item for the label

        self.current_gif_frame_index = 0
        self.animate_gif_frame()

    def animate_gif_frame(self):
        if not self.is_gif_playing or not self.gif_pil_frames or \
           not self.gif_label or not self.gif_label_window_id or \
           not self.canvas.winfo_exists():
            # If canvas doesn't exist, animation should stop.
            if self.gif_animation_after_id:
                 self.canvas.after_cancel(self.gif_animation_after_id)
                 self.gif_animation_after_id = None
            return

        try: # Check if canvas item still exists
            self.canvas.itemcget(self.gif_label_window_id, "state") 
        except tk.TclError:
            self.gif_label_window_id = None # It was deleted
            if self.gif_animation_after_id:
                 self.canvas.after_cancel(self.gif_animation_after_id)
                 self.gif_animation_after_id = None
            return

        pil_frame = self.gif_pil_frames[self.current_gif_frame_index]

        padding = 10 * self.app.current_scale 
        # Ensure padding doesn't make target width/height negative
        target_width = max(1, self.world_width * self.app.current_scale - padding)
        target_height = max(1, self.world_height * self.app.current_scale - padding)


        if target_width <= 1 or target_height <= 1: # Use 1x1 placeholder if too small
            # Consider hiding or showing a placeholder if size is too small
            # For now, let's try to resize to at least 1x1
            resized_frame = pil_frame.resize((1, 1), Image.LANCZOS)
        else:
            resized_frame = pil_frame.resize((int(target_width), int(target_height)), Image.LANCZOS)
        
        photo_image = ImageTk.PhotoImage(resized_frame)
        self.gif_label.image = photo_image # Keep a reference
        self.gif_label.config(image=photo_image)

        self.current_gif_frame_index = (self.current_gif_frame_index + 1) % len(self.gif_pil_frames)
        
        duration = self.gif_image_info.get('duration', 100)
        if not isinstance(duration, (int, float)) or duration <= 0: # Validate duration
            duration = 100
        
        self.gif_animation_after_id = self.canvas.after(int(duration), self.animate_gif_frame)

    def stop_gif_animation(self):
        self.is_gif_playing = False
        if self.gif_animation_after_id:
            if self.canvas.winfo_exists(): # Check canvas existence before calling after_cancel
                self.canvas.after_cancel(self.gif_animation_after_id)
            self.gif_animation_after_id = None
        
        if self.gif_label:
            self.gif_label.config(image='') # Clear image from label
            self.gif_label.image = None # Remove reference
        
        if self.gif_label_window_id:
            if self.canvas.winfo_exists():
                try: # Check if canvas item still exists
                    if self.canvas.type(self.gif_label_window_id):
                         self.canvas.itemconfigure(self.gif_label_window_id, state='hidden')
                except tk.TclError:
                    self.gif_label_window_id = None # It was deleted

    def update_gif_label_window(self):
        if not self.gif_label: # Label not created yet
            return

        padding = 5 * self.app.current_scale # Reduced padding slightly
        target_width = self.world_width * self.app.current_scale - padding
        target_height = self.world_height * self.app.current_scale - padding

        if target_width <= 0 or target_height <= 0:
            if self.gif_label_window_id:
                 if self.canvas.winfo_exists():
                    try:
                        if self.canvas.type(self.gif_label_window_id):
                            self.canvas.itemconfigure(self.gif_label_window_id, state='hidden')
                    except tk.TclError:
                        self.gif_label_window_id = None
            return

        block_cx = (self.world_x + self.world_width / 2) * self.app.current_scale
        block_cy = (self.world_y + self.world_height / 2) * self.app.current_scale
        
        item_exists = False
        if self.gif_label_window_id is not None:
            if self.canvas.winfo_exists():
                try:
                    self.canvas.coords(self.gif_label_window_id) # Check if item exists by trying to get coords
                    item_exists = True
                except tk.TclError: # Item does not exist or canvas is gone
                    item_exists = False
                    self.gif_label_window_id = None # Reset ID
            else: # Canvas doesn't exist
                self.gif_label_window_id = None 
                return


        if self.gif_label_window_id is None:
            if self.canvas.winfo_exists(): # Ensure canvas exists before creating window
                self.gif_label_window_id = self.canvas.create_window(
                    block_cx, block_cy, 
                    window=self.gif_label, 
                    anchor=tk.CENTER, 
                    width=int(target_width), 
                    height=int(target_height)
                )
        else: # Window item exists, update its properties
            if self.canvas.winfo_exists():
                self.canvas.coords(self.gif_label_window_id, block_cx, block_cy)
                self.canvas.itemconfigure(self.gif_label_window_id, 
                                          width=int(target_width), 
                                          height=int(target_height))
        
        if self.gif_label_window_id and self.canvas.winfo_exists(): # Ensure window ID is valid
            try:
                current_state = 'normal' if self.is_gif_playing and self.gif_pil_frames else 'hidden'
                if self.canvas.type(self.gif_label_window_id): # Final check
                    self.canvas.itemconfigure(self.gif_label_window_id, state=current_state)
                    # Lower GIF label behind the block's main polygon and text
                    self.canvas.tag_lower(self.gif_label_window_id, self.block)
                    if self.text: # self.text might not exist if block is very minimal
                        self.canvas.tag_lower(self.gif_label_window_id, self.text)
            except tk.TclError:
                 self.gif_label_window_id = None


    def update_text(self):
        super().update_text() # Call parent's update_text
        self.update_gif_label_window()

        if self.is_gif_playing and self.gif_pil_frames:
            # If animation was running, ensure it continues/restarts correctly scaled
            if self.gif_animation_after_id:
                if self.canvas.winfo_exists():
                    self.canvas.after_cancel(self.gif_animation_after_id)
                self.gif_animation_after_id = None
            
            # Restart animation for the current frame, correctly scaled.
            # animate_gif_frame will then schedule the next frame.
            if self.canvas.winfo_exists(): # Check before starting new animation loop
                 self.animate_gif_frame() 

    def cleanup_gif_elements(self):
        self.stop_gif_animation() # This already handles hiding the window and clearing label image

# --- SVGBlock ---
class SVGBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        # Initialize SVG-specific attributes before super().__init__
        self.selected_svg_path = None
        self.svg_label = None  # Will be a tk.Label widget
        self.svg_label_window_id = None # ID from canvas.create_window
        self.is_svg_displayed = False # Changed from is_svg_playing
        self._pil_image = None # Renamed from _placeholder_image, stores the PIL Image object

        super().__init__(canvas, x, y, id, app)
        
        self.block_name = f"SVGBlock {self.id}"

        # Update parameters: remove old 'type' and 'TEXTBOX_LABEL', add new ones
        new_params = []
        for name, val in self.parameters:
            if name.lower() == "type":
                continue 
            if name == "TEXTBOX_LABEL":
                continue
            new_params.append((name, val))
        
        new_params.append(("type", "svgblock"))
        new_params.append(("TEXTBOX_LABEL", f"SVGBlock {self.id}: (No file)"))
        
        self.parameters = new_params
        
        self.update_text()
        # Changed to Double-Button-1 to avoid conflict with dragging
        self.canvas.tag_bind(self.block, "<Double-Button-1>", self.select_svg_file)

    def serialize(self):
        data = super().serialize()
        data["type"] = "svgblock"
        data["selected_svg_path"] = self.selected_svg_path
        return data

    def select_svg_file(self, event):
        filepath = filedialog.askopenfilename(
            title="Select SVG file",
            filetypes=[("SVG files", "*.svg")] # Changed filetype
        )
        if filepath:
            self.selected_svg_path = filepath
            
            new_params = []
            textbox_label_found = False
            for name, val in self.parameters:
                if name == "TEXTBOX_LABEL":
                    new_params.append(("TEXTBOX_LABEL", f"SVGBlock {self.id}: {os.path.basename(self.selected_svg_path)}"))
                    textbox_label_found = True
                else:
                    new_params.append((name, val))
            
            if not textbox_label_found:
                new_params.append(("TEXTBOX_LABEL", f"SVGBlock {self.id}: {os.path.basename(self.selected_svg_path)}"))
            
            self.parameters = new_params
            self.update_text() 
            self.load_and_display_svg()

    def load_and_display_svg(self):
        if self.is_svg_displayed:
            self.clear_svg_display()

        try:
            if not self.selected_svg_path:
                # Handle case where path might be None unexpectedly
                self.update_text() # Update label to show "No file" or error
                return

            # Convert SVG to ReportLab Drawing
            drawing = svg2rlg(self.selected_svg_path)

            if drawing:
                # Create an in-memory buffer for the PNG image
                img_buffer = io.BytesIO()
                # Draw the ReportLab Drawing to the buffer as PNG
                renderPM.drawToFile(drawing, img_buffer, fmt="PNG")
                img_buffer.seek(0)
                # Open the PNG image from the buffer using PIL
                pil_image = Image.open(img_buffer)
                # Convert to RGBA to ensure transparency is handled if present
                self._pil_image = pil_image.convert("RGBA") 
            else:
                # Fallback if drawing is None (conversion failed silently)
                print(f"SVG conversion failed for {self.selected_svg_path}, drawing was None.")
                # Create a simple error placeholder image
                error_img = Image.new('RGBA', (100, 100), (255, 0, 0, 180)) # Reddish placeholder
                self._pil_image = error_img

        except Exception as e:
            print(f"Error loading or processing SVG {self.selected_svg_path}: {e}")
            self.selected_svg_path = None # Reset path on error
             # Create a simple error placeholder image
            error_img = Image.new('RGBA', (100, 100), (255, 0, 0, 180)) # Reddish placeholder
            self._pil_image = error_img
            
            # Update TEXTBOX_LABEL parameter to show error
            new_params = []
            for name, val in self.parameters:
                if name == "TEXTBOX_LABEL":
                    new_params.append(("TEXTBOX_LABEL", f"SVGBlock {self.id}: (Error)"))
                else:
                    new_params.append((name, val))
            self.parameters = new_params
            # No call to self.update_text() here, it's called by the caller or select_svg_file
            # No call to self.load_and_display_svg() to prevent recursion
            # The caller (select_svg_file) will call update_text and load_and_display_svg again if needed
            # For now, just ensure is_svg_displayed is false and clear display
            self.is_svg_displayed = False
            self.clear_svg_display() # Clear any previous display
            self.update_text() # Update text to show error in label
            return # Important to return after error

        # If successful or fallback error image is created:
        if self.svg_label is None:
            self.svg_label = tk.Label(self.canvas, bg="#000000") 

        self.is_svg_displayed = True 
        self.update_svg_label_window() 
        self.display_static_svg()

    def display_static_svg(self): 
        if not self.is_svg_displayed or not self._pil_image or \
           not self.svg_label or not self.svg_label_window_id or \
           not self.canvas.winfo_exists():
            return

        try: 
            self.canvas.itemcget(self.svg_label_window_id, "state") 
        except tk.TclError:
            self.svg_label_window_id = None 
            return

        padding = 10 * self.app.current_scale
        target_width = max(1, int(self.world_width * self.app.current_scale - padding))
        target_height = max(1, int(self.world_height * self.app.current_scale - padding))

        if self._pil_image:
            try:
                resized_pil_image = self._pil_image.resize((target_width, target_height), Image.LANCZOS)
                photo_image = ImageTk.PhotoImage(resized_pil_image)
                self.svg_label.image = photo_image
                self.svg_label.config(image=photo_image)
            except Exception as e:
                print(f"Error resizing/displaying SVG: {e}")
                # Optionally, display a specific error image on the label itself
                # For now, if resize fails, it might show nothing or old image.
        
        # No self.canvas.after call, as this is static display.

    def clear_svg_display(self): 
        self.is_svg_displayed = False 
        
        if self.svg_label:
            self.svg_label.config(image='') 
            self.svg_label.image = None 
        
        if self.svg_label_window_id:
            if self.canvas.winfo_exists():
                try: 
                    if self.canvas.type(self.svg_label_window_id):
                         self.canvas.itemconfigure(self.svg_label_window_id, state='hidden')
                except tk.TclError:
                    self.svg_label_window_id = None
        self._pil_image = None


    def update_svg_label_window(self): 
        if not self.svg_label: 
            return

        padding = 5 * self.app.current_scale 
        target_width = self.world_width * self.app.current_scale - padding
        target_height = self.world_height * self.app.current_scale - padding

        if target_width <= 0 or target_height <= 0:
            if self.svg_label_window_id:
                 if self.canvas.winfo_exists():
                    try:
                        if self.canvas.type(self.svg_label_window_id):
                            self.canvas.itemconfigure(self.svg_label_window_id, state='hidden')
                    except tk.TclError:
                        self.svg_label_window_id = None
            return

        block_cx = (self.world_x + self.world_width / 2) * self.app.current_scale
        block_cy = (self.world_y + self.world_height / 2) * self.app.current_scale
        
        item_exists = False
        if self.svg_label_window_id is not None:
            if self.canvas.winfo_exists():
                try:
                    self.canvas.coords(self.svg_label_window_id) 
                    item_exists = True
                except tk.TclError: 
                    item_exists = False
                    self.svg_label_window_id = None 
            else: 
                self.svg_label_window_id = None 
                return


        if self.svg_label_window_id is None:
            if self.canvas.winfo_exists(): 
                self.svg_label_window_id = self.canvas.create_window(
                    block_cx, block_cy, 
                    window=self.svg_label, 
                    anchor=tk.CENTER, 
                    width=int(target_width), 
                    height=int(target_height)
                )
        else: 
            if self.canvas.winfo_exists():
                self.canvas.coords(self.svg_label_window_id, block_cx, block_cy)
                self.canvas.itemconfigure(self.svg_label_window_id, 
                                          width=int(target_width), 
                                          height=int(target_height))
        
        if self.svg_label_window_id and self.canvas.winfo_exists(): 
            try:
                # Changed condition from is_svg_playing and svg_pil_frames to is_svg_displayed
                current_state = 'normal' if self.is_svg_displayed and self._pil_image else 'hidden'
                if self.canvas.type(self.svg_label_window_id): 
                    self.canvas.itemconfigure(self.svg_label_window_id, state=current_state)
                    self.canvas.tag_lower(self.svg_label_window_id, self.block)
                    if self.text: 
                        self.canvas.tag_lower(self.svg_label_window_id, self.text)
            except tk.TclError:
                 self.svg_label_window_id = None


    def update_text(self):
        super().update_text() 
        self.update_svg_label_window()

        if self.is_svg_displayed and self._pil_image: # Check if displayed and image exists
            if self.canvas.winfo_exists(): 
                 self.display_static_svg() # Refresh display

    def cleanup_svg_elements(self): 
        self.clear_svg_display() 

        if self.svg_label and hasattr(self.svg_label, 'winfo_exists') and self.svg_label.winfo_exists():
            self.svg_label.destroy()
        self.svg_label = None

        if self.svg_label_window_id and self.canvas and hasattr(self.canvas, 'winfo_exists') and self.canvas.winfo_exists():
            try:
                if self.canvas.type(self.svg_label_window_id):
                    self.canvas.delete(self.svg_label_window_id)
            except tk.TclError:
                pass 
        self.svg_label_window_id = None
        
        self.selected_svg_path = None
        self._pil_image = None


        if self.gif_label and hasattr(self.gif_label, 'winfo_exists') and self.gif_label.winfo_exists():
            self.gif_label.destroy()
        self.gif_label = None

        if self.gif_label_window_id and self.canvas and hasattr(self.canvas, 'winfo_exists') and self.canvas.winfo_exists():
            try:
                # Check if item still exists by trying to get its type
                # If it doesn't exist or canvas is gone, TclError will be raised
                if self.canvas.type(self.gif_label_window_id):
                    self.canvas.delete(self.gif_label_window_id)
            except tk.TclError:
                pass # Item might have been deleted already or canvas is gone
        self.gif_label_window_id = None
        
        self.selected_gif_path = None
        self.gif_pil_frames = []
        self.gif_image_info = {}
        # self.current_svg_frame_index is already reset by stop_svg_animation or not critical if frames are cleared
        # self.is_svg_playing is already set to False by stop_svg_animation


def ensure_sys_dir():
    """Create sys directory if it doesn't exist and clear it if it does"""
    sys_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sys")
    if os.path.exists(sys_dir):
        # Clear the directory
        for file in os.listdir(sys_dir):
            file_path = os.path.join(sys_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        # Create the directory
        os.makedirs(sys_dir)

if __name__ == "__main__":
    app = Application()
    import __main__
    __main__.connect = app.workspaces[app.active_workspace.ws_id].connect if app.active_workspace else None
    app.mainloop()


# --- GIFBlock ---
class GIFBlock(DraggableBlock):
    def __init__(self, canvas, x, y, id, app):
        super().__init__(canvas, x, y, id, app)
        
        self.gif_pil_frames = []
        self.gif_image_info = {}
        self.current_gif_frame_index = 0
        self.gif_animation_after_id = None
        self.selected_gif_path = None
        self.gif_label = None  # Will be a tk.Label widget
        self.gif_label_window_id = None # ID from canvas.create_window
        self.is_gif_playing = False
        
        self.block_name = f"GIFBlock {self.id}"

        # Update parameters: remove old 'type' and 'TEXTBOX_LABEL', add new ones
        new_params = []
        textbox_label_found = False
        for name, val in self.parameters:
            if name.lower() == "type":
                continue # Skip old type
            if name == "TEXTBOX_LABEL":
                new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: (No file)"))
                textbox_label_found = True
                continue
            new_params.append((name, val))
        
        new_params.append(("type", "gifblock"))
        if not textbox_label_found:
             new_params.append(("TEXTBOX_LABEL", f"GIFBlock {self.id}: (No file)"))
        
        self.parameters = new_params
        
        self.update_text()
