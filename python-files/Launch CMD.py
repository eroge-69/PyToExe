import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import time
import requests
import threading
import os
from datetime import datetime
import math

class DMEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("DM Editor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#282828')
        
        # Состояния
        self.figure_exists = False
        self.figure_pose = "T"
        self.figure_shake = False
        self.walking = False
        self.walk_start_time = 0
        self.placing_hint_node = False
        self.hint_nodes = []
        self.camera_x, self.camera_y = 0, 0
        self.camera_speed = 5
        self.walk_cycle = 0
        self.walk_speed = 0.05
        
        # Цвета
        self.colors = {
            'dark_green': '#005000',
            'light_skin': '#f0c8a0',
            'brown_hair': '#654321',
            'dark_gray': '#282828',
            'medium_gray': '#505050',
            'light_gray': '#787878',
            'white': '#c8c8c8',
            'black': '#0a0a0a',
            'hint_node': '#dcdcdc'
        }
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        # Меню бар
        self.menu_bar = tk.Frame(self.root, bg=self.colors['medium_gray'], height=30)
        self.menu_bar.pack(fill=tk.X, side=tk.TOP)
        
        self.file_button = tk.Button(self.menu_bar, text="File", bg=self.colors['medium_gray'], 
                                    fg=self.colors['white'], relief=tk.RAISED, bd=1,
                                    command=self.toggle_file_menu)
        self.file_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Выпадающее меню File
        self.file_menu = tk.Frame(self.root, bg=self.colors['light_gray'], width=100, height=60)
        self.file_menu.place(x=10, y=30)
        self.file_menu.place_forget()
        
        self.open_btn = tk.Button(self.file_menu, text="Open", bg=self.colors['medium_gray'],
                                 fg='#ffa500', relief=tk.RAISED, bd=1, width=10,
                                 command=self.file_open)
        self.open_btn.place(x=2, y=2)
        
        self.new_btn = tk.Button(self.file_menu, text="New", bg=self.colors['medium_gray'],
                                fg=self.colors['white'], relief=tk.RAISED, bd=1, width=10,
                                command=self.file_new)
        self.new_btn.place(x=2, y=32)
        
        # Основная область
        main_frame = tk.Frame(self.root, bg=self.colors['dark_gray'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 3D область просмотра
        self.canvas_3d = tk.Canvas(main_frame, bg=self.colors['black'], width=680, height=550)
        self.canvas_3d.grid(row=0, column=0, padx=(0, 10), pady=(0, 10))
        
        # Панель инструментов
        tool_frame = tk.Frame(main_frame, bg=self.colors['medium_gray'], width=290, height=250)
        tool_frame.grid(row=0, column=1, sticky=tk.N)
        tool_frame.grid_propagate(False)
        
        # Заголовок панели
        title_label = tk.Label(tool_frame, text="", 
                              bg=self.colors['medium_gray'], fg='#ffa500',
                              font=('Courier', 0, 'bold'))
        title_label.pack(pady=0)
        
        # Кнопки
        self.create_btn = self.create_old_button(tool_frame, "CREATE", self.create_figure)
        self.create_btn.pack(pady=5)
        
        self.new_btn_main = self.create_old_button(tool_frame, "NEW", self.new_figure, False)
        self.new_btn_main.pack(pady=5)
        
        self.open_btn_main = self.create_old_button(tool_frame, "OPEN", self.open_figure)
        self.open_btn_main.pack(pady=5)
        
        self.hint_btn = self.create_old_button(tool_frame, "HINT NODE", self.hint_node)
        self.hint_btn.pack(pady=5)
        
        # Панель Hint Nodes
        self.hint_frame = tk.Frame(main_frame, bg=self.colors['medium_gray'], width=680, height=100)
        self.hint_frame.grid(row=1, column=0, sticky=tk.W+tk.E)
        self.hint_frame.grid_propagate(False)
        
        hint_title = tk.Label(self.hint_frame, text="HINT NODES", 
                             bg=self.colors['medium_gray'], fg='#ffa500',
                             font=('Courier', 12, 'bold'))
        hint_title.pack(anchor=tk.W, padx=10, pady=10)
        
        self.hint_list = tk.Label(self.hint_frame, text="No hint nodes placed", 
                                 bg=self.colors['medium_gray'], fg=self.colors['light_gray'],
                                 font=('Courier', 10), justify=tk.LEFT)
        self.hint_list.pack(anchor=tk.W, padx=20)
        
        # Статус бар
        self.status_bar = tk.Label(self.root, text="NO FIGURE LOADED", 
                                  bg=self.colors['medium_gray'], fg=self.colors['white'],
                                  font=('Courier', 10), anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Отрисовка начального состояния
        self.draw_3d_scene()
        
    def create_old_button(self, parent, text, command, active=True):
        bg = self.colors['light_gray'] if active else self.colors['dark_gray']
        fg = self.colors['white'] if active else self.colors['medium_gray']
        
        btn = tk.Button(parent, text=text, bg=bg, fg=fg, relief=tk.RAISED, bd=2,
                       width=20, height=2, font=('Courier', 10),
                       command=command, state=tk.NORMAL if active else tk.DISABLED)
        return btn
        
    def setup_bindings(self):
        self.root.bind('<Left>', lambda e: self.move_camera(-self.camera_speed, 0))
        self.root.bind('<Right>', lambda e: self.move_camera(self.camera_speed, 0))
        self.root.bind('<Up>', lambda e: self.move_camera(0, -self.camera_speed))
        self.root.bind('<Down>', lambda e: self.move_camera(0, self.camera_speed))
        self.root.bind('<space>', self.toggle_walk)
        self.root.bind('<Escape>', self.cancel_actions)
        
        self.canvas_3d.bind('<Button-1>', self.canvas_click)
        
    def move_camera(self, dx, dy):
        self.camera_x += dx
        self.camera_y += dy
        self.draw_3d_scene()
        self.update_status()
        
    def toggle_walk(self, event=None):
        if self.figure_exists and self.figure_pose == "human":
            self.walking = not self.walking
            self.draw_3d_scene()
            self.update_status()
            
    def cancel_actions(self, event=None):
        self.placing_hint_node = False
        self.file_menu.place_forget()
        self.update_status()
        
    def canvas_click(self, event):
        if self.placing_hint_node:
            world_x = event.x - 340 - self.camera_x
            world_y = event.y - 275 - self.camera_y
            self.hint_nodes.append((world_x, world_y))
            self.placing_hint_node = False
            self.update_hint_list()
            self.draw_3d_scene()
            
    def toggle_file_menu(self):
        if self.file_menu.winfo_ismapped():
            self.file_menu.place_forget()
        else:
            self.file_menu.place(x=10, y=30)
            
    def file_open(self):
        self.show_error("FATAL ERROR! CRASHING...")
        
    def file_new(self):
        if self.figure_exists:
            self.figure_pose = "human"
            self.figure_shake = True
            self.walk_start_time = time.time()
            self.walking = False
            self.draw_3d_scene()
            self.update_status()
        self.file_menu.place_forget()
        
    def create_figure(self):
        if not self.figure_exists:
            self.figure_exists = True
            self.figure_pose = "T"
            self.figure_shake = False
            self.walking = False
            self.new_btn_main.config(bg=self.colors['light_gray'], state=tk.NORMAL)
            self.draw_3d_scene()
            self.update_status()
            
    def new_figure(self):
        if self.figure_exists:
            self.figure_pose = "human"
            self.figure_shake = True
            self.walk_start_time = time.time()
            self.walking = False
            self.draw_3d_scene()
            self.update_status()
            
    def open_figure(self):
        if self.figure_exists:
            self.figure_exists = False
            self.figure_shake = False
            self.walking = False
            self.new_btn_main.config(bg=self.colors['dark_gray'], state=tk.DISABLED)
            self.draw_3d_scene()
            self.update_status()
        else:
            self.show_error("FATAL ERROR! CRASHING...")
            
    def hint_node(self):
        self.placing_hint_node = True
        self.update_status()
        
    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("ERROR")
        error_window.geometry("300x100")
        error_window.configure(bg='#b40000')
        error_window.transient(self.root)
        error_window.grab_set()
        
        error_label = tk.Label(error_window, text=message, bg='#b40000', fg='white',
                              font=('Courier', 12, 'bold'))
        error_label.pack(expand=True)
        
        # Закрытие программы через 3 секунды
        error_window.after(3000, lambda: [error_window.destroy(), self.root.destroy()])
        
    def update_hint_list(self):
        if self.hint_nodes:
            text = "\n".join([f"Node {i+1}: X={x} Y={y}" for i, (x, y) in enumerate(self.hint_nodes)])
            self.hint_list.config(text=text)
        else:
            self.hint_list.config(text="No hint nodes placed")
            
    def update_status(self):
        status = "NO FIGURE LOADED"
        if self.figure_exists:
            status = f"FIGURE: {self.figure_pose.upper()} POSE"
            if self.figure_shake:
                status += " [SHAKING]"
            if self.walking:
                status += " [WALKING]"
                
        status += f" | CAMERA: X:{self.camera_x} Y:{self.camera_y}"
        
        if self.placing_hint_node:
            status += " | PLACING HINT NODE"
            
        self.status_bar.config(text=status)
        
    def draw_3d_scene(self):
        self.canvas_3d.delete("all")
        
        # Рисуем псевдо-3D пол
        self.draw_3d_floor()
        
        # Рисуем Hint Nodes
        for x, y in self.hint_nodes:
            self.draw_hint_node(x, y)
            
        # Рисуем фигуру
        if self.figure_exists:
            self.draw_figure()
            
        # Рамка вокруг 3D области
        self.canvas_3d.create_rectangle(2, 2, 678, 548, outline=self.colors['light_gray'], width=2)
        
    def draw_3d_floor(self):
        center_x, center_y = 340, 275
        
        # Линии перспективы
        for i in range(0, 340, 20):
            # Горизонтальные линии
            y_pos = center_y + i + self.camera_y
            if 0 <= y_pos < 550:
                width_line = i * 1.5
                start_x = max(0, center_x - width_line + self.camera_x)
                end_x = min(680, center_x + width_line + self.camera_x)
                if start_x < end_x:
                    self.canvas_3d.create_line(start_x, y_pos, end_x, y_pos, fill=self.colors['medium_gray'])
            
            y_pos = center_y - i + self.camera_y
            if 0 <= y_pos < 550:
                width_line = i * 1.5
                start_x = max(0, center_x - width_line + self.camera_x)
                end_x = min(680, center_x + width_line + self.camera_x)
                if start_x < end_x:
                    self.canvas_3d.create_line(start_x, y_pos, end_x, y_pos, fill=self.colors['medium_gray'])
        
        # Вертикальные линии
        for i in range(-8, 9):
            x_pos = center_x + i * 40 + self.camera_x
            if 0 <= x_pos < 680:
                self.canvas_3d.create_line(x_pos, 0, x_pos, 550, fill=self.colors['light_gray'])
                
    def draw_hint_node(self, x, y):
        screen_x = 340 + x + self.camera_x
        screen_y = 275 + y + self.camera_y
        
        # Белый блок
        self.canvas_3d.create_rectangle(screen_x-15, screen_y-15, screen_x+15, screen_y+15, 
                                       fill=self.colors['hint_node'], outline=self.colors['black'], width=2)
        
        # Текст Hint Node
        self.canvas_3d.create_text(screen_x, screen_y-5, text="Hint Node", 
                                  fill=self.colors['black'], font=('Courier', 8))
        
    def draw_figure(self):
        center_x, center_y = 340 + self.camera_x, 275 + self.camera_y
        
        # Слабое дрожание
        if self.figure_shake and not self.walking:
            current_time = time.time()
            shake_x = math.sin(current_time * 5) * 0.3
            shake_y = math.cos(current_time * 3) * 0.2
            center_x += shake_x
            center_y += shake_y
            
        # Анимация ходьбы
        leg_offset = 0
        if self.walking:
            self.walk_cycle += self.walk_speed
            if math.sin(self.walk_cycle) > 0:
                leg_offset = 15
            else:
                leg_offset = -15
                
            # Автоматическое перемещение при ходьбе
            center_x += math.cos(self.walk_cycle) * 2
        
        if self.figure_pose == "T":
            # T-поза
            self.draw_t_pose(center_x, center_y)
        else:
            # Естественная поза
            self.draw_natural_pose(center_x, center_y, leg_offset)
            
    def draw_t_pose(self, x, y):
        # Голова с волосами
        self.canvas_3d.create_oval(x-12, y-70, x+12, y-40, fill=self.colors['light_skin'], outline='')
        self.canvas_3d.create_oval(x-14, y-72, x+14, y-57, fill=self.colors['brown_hair'], outline='')
        
        # Шея
        self.canvas_3d.create_rectangle(x-5, y-40, x+5, y-30, fill=self.colors['light_skin'], outline='')
        
        # Тело (футболка)
        self.canvas_3d.create_rectangle(x-20, y-30, x+20, y+20, fill=self.colors['dark_green'], outline='')
        
        # Руки
        self.canvas_3d.create_rectangle(x-25, y-25, x-15, y+15, fill=self.colors['light_skin'], outline='')
        self.canvas_3d.create_rectangle(x+15, y-25, x+25, y+15, fill=self.colors['light_skin'], outline='')
        
        # Ноги (штаны)
        self.canvas_3d.create_rectangle(x-20, y+20, x-5, y+60, fill=self.colors['dark_green'], outline='')
        self.canvas_3d.create_rectangle(x+5, y+20, x+20, y+60, fill=self.colors['dark_green'], outline='')
        
    def draw_natural_pose(self, x, y, leg_offset):
        # Голова с волосами
        self.canvas_3d.create_oval(x-15, y-65, x+15, y-30, fill=self.colors['light_skin'], outline='')
        self.canvas_3d.create_oval(x-16, y-70, x+16, y-45, fill=self.colors['brown_hair'], outline='')
        
        # Шея
        self.canvas_3d.create_rectangle(x-5, y-30, x+5, y-15, fill=self.colors['light_skin'], outline='')
        
        # Тело (футболка)
        self.canvas_3d.create_polygon([
            x-20, y-15,
            x+20, y-15,
            x+15, y+45,
            x-15, y+45
        ], fill=self.colors['dark_green'], outline='')
        
        # Руки
        self.canvas_3d.create_rectangle(x-25, y-10, x-15, y+30, fill=self.colors['light_skin'], outline='')
        self.canvas_3d.create_rectangle(x+15, y-10, x+25, y+30, fill=self.colors['light_skin'], outline='')
        
        # Ноги с анимацией ходьбы
        left_leg_x = x - 12 + (leg_offset if leg_offset < 0 else 0)
        right_leg_x = x + 2 + (leg_offset if leg_offset > 0 else 0)
        
        self.canvas_3d.create_rectangle(left_leg_x-5, y+45, left_leg_x+5, y+85, fill=self.colors['dark_green'], outline='')
        self.canvas_3d.create_rectangle(right_leg_x-5, y+45, right_leg_x+5, y+85, fill=self.colors['dark_green'], outline='')
        
        # Ступни
        self.canvas_3d.create_oval(left_leg_x-8, y+85, left_leg_x+8, y+93, fill='#1e1e1e', outline='')
        self.canvas_3d.create_oval(right_leg_x-8, y+85, right_leg_x+8, y+93, fill='#1e1e1e', outline='')
        
    def run(self):
        # Запуск анимации
        self.animate()
        self.root.mainloop()
        
    def animate(self):
        # Проверяем, нужно ли начать ходить автоматически
        if (self.figure_exists and self.figure_pose == "human" and 
            not self.walking and time.time() - self.walk_start_time > 10):
            self.walking = True
            
        # Перерисовываем сцену
        self.draw_3d_scene()
        self.update_status()
        
        # Следующий кадр анимации
        self.root.after(50, self.animate)

class ConsoleSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Command Processor")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Текстовое поле для вывода и ввода
        self.output_text = scrolledtext.ScrolledText(
            root, 
            bg='black', 
            fg='white', 
            font=('Consolas', 12),
            insertbackground='white'
        )
        self.output_text.pack(expand=True, fill='both')
        
        # Биндим обработчики клавиш
        self.output_text.bind('<Key>', self.on_key_press)
        self.output_text.bind('<Return>', self.on_enter)
        self.output_text.bind('<BackSpace>', self.on_backspace)
        
        # Доступные команды
        self.commands = {
            'help': 'Display help information',
            'cls': 'Clear the screen',
            'dir': 'Display list of files',
            'cd': 'Change directory',
            'type': 'Display content of text file',
            'copy': 'Copy files',
            'del': 'Delete files',
            'mkdir': 'Create directory',
            'rmdir': 'Remove directory',
            'echo': 'Display messages',
            'date': 'Display or set date',
            'time': 'Display or set time',
            'ver': 'Display version',
            'vol': 'Display disk volume',
            'path': 'Display path',
            'tree': 'Display directory tree',
            'find': 'Search for text in files',
            'sort': 'Sort input',
            'more': 'Display output one screen at a time',
            'ipconfig': 'Display IP configuration',
            'ping': 'Test network connectivity',
            'netstat': 'Display network statistics',
            'tasklist': 'Display running tasks',
            'systeminfo': 'Display system information',
            'whoami': 'Display current user',
            'shutdown': 'Shutdown computer'
        }
        
        # Текущий каталог
        self.current_dir = "C:\\Windows\\System32"
        
        # Позиция начала ввода (после промпта)
        self.input_start = 1.0
        self.current_input = ""
        
        self.show_welcome()
        self.show_prompt()
        
        # Фокусируемся на текстовом поле
        self.output_text.focus_set()
    
    def show_welcome(self):
        welcome_text = """Microsoft Windows [Version 10.0.19045.4291]
(c) Microsoft Corporation. All rights reserved.

"""
        self.output_text.insert(tk.END, welcome_text)
    
    def show_prompt(self):
        prompt = f"{self.current_dir}>"
        self.output_text.insert(tk.END, prompt)
        self.input_start = self.output_text.index(tk.INSERT)
        self.current_input = ""
    
    def on_key_press(self, event):
        # Запрещаем редактирование вне области ввода
        if self.output_text.compare(tk.INSERT, "<", self.input_start):
            self.output_text.mark_set(tk.INSERT, tk.END)
            return "break"
        
        # Разрешаем только печатные символы
        if len(event.char) == 1 and ord(event.char) >= 32:
            self.current_input += event.char
        return None
    
    def on_backspace(self, event):
        if len(self.current_input) > 0:
            self.current_input = self.current_input[:-1]
            # Удаляем последний символ из текстового поля
            current_pos = self.output_text.index(tk.INSERT)
            if self.output_text.compare(current_pos, ">", self.input_start):
                self.output_text.delete(f"{current_pos}-1c", current_pos)
        return "break"
    
    def on_enter(self, event):
        command = self.current_input.strip()
        self.output_text.insert(tk.END, "\n")
        
        # Разделяем команду и аргументы
        parts = command.split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Обработка команд
        if cmd == 'help':
            if args and args[0] in self.commands:
                self.output_text.insert(tk.END, f"{args[0]}: {self.commands[args[0]]}\n")
            else:
                self.output_text.insert(tk.END, "For more information on a specific command, type HELP command-name\n\n")
                for cmd_name in sorted(self.commands.keys()):
                    self.output_text.insert(tk.END, f"{cmd_name:<20} {self.commands[cmd_name]}\n")
                
        elif cmd == 'cls':
            self.output_text.delete(1.0, tk.END)
            self.show_welcome()
            
        elif cmd == 'echo':
            text = ' '.join(args) if args else ""
            self.output_text.insert(tk.END, text + "\n")
            
        elif cmd == 'dir':
            self.show_directory()
                
        elif cmd == 'cd':
            self.change_directory(args)
            
        elif cmd == 'type':
            self.type_file(args)
            
        elif cmd == 'copy':
            self.output_text.insert(tk.END, "        1 file(s) copied.\n")
            
        elif cmd == 'del':
            if args:
                self.output_text.insert(tk.END, f"Deleted file: {args[0]}\n")
            else:
                self.output_text.insert(tk.END, "The syntax of the command is incorrect.\n")
                
        elif cmd == 'mkdir':
            if args:
                self.output_text.insert(tk.END, f"Created directory: {args[0]}\n")
            else:
                self.output_text.insert(tk.END, "The syntax of the command is incorrect.\n")
                
        elif cmd == 'rmdir':
            if args:
                self.output_text.insert(tk.END, f"Removed directory: {args[0]}\n")
            else:
                self.output_text.insert(tk.END, "The syntax of the command is incorrect.\n")
                
        elif cmd == 'date':
            current_date = datetime.now().strftime("%a %m/%d/%Y")
            self.output_text.insert(tk.END, f"The current date is: {current_date}\n")
            self.output_text.insert(tk.END, "Enter the new date: (mm-dd-yy) \n")
            
        elif cmd == 'time':
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.output_text.insert(tk.END, f"The current time is: {current_time}\n")
            self.output_text.insert(tk.END, "Enter the new time: \n")
            
        elif cmd == 'ver':
            self.output_text.insert(tk.END, "Microsoft Windows [Version 10.0.19045.4291]\n")
            
        elif cmd == 'vol':
            self.output_text.insert(tk.END, " Volume in drive C has no label\n")
            self.output_text.insert(tk.END, " Volume Serial Number is 1234-5678\n")
            
        elif cmd == 'path':
            self.output_text.insert(tk.END, "PATH=C:\\Windows\\system32;C:\\Windows;C:\\Windows\\System32\\Wbem\n")
            
        elif cmd == 'tree':
            self.output_text.insert(tk.END, "Folder PATH listing\n")
            self.output_text.insert(tk.END, "Volume serial number is 00000001 1234:5678\n")
            self.output_text.insert(tk.END, "C:.\n")
            self.output_text.insert(tk.END, "├───Windows\n")
            self.output_text.insert(tk.END, "│   └───System32\n")
            self.output_text.insert(tk.END, "└───Users\n")
            
        elif cmd == 'find':
            if len(args) >= 2:
                self.output_text.insert(tk.END, f"---------- {args[-1]}\n")
                self.output_text.insert(tk.END, "Text found in file\n")
            else:
                self.output_text.insert(tk.END, "The syntax of the command is incorrect.\n")
                
        elif cmd == 'sort':
            self.output_text.insert(tk.END, "Sorted output would appear here\n")
            
        elif cmd == 'more':
            self.output_text.insert(tk.END, "Content would be displayed one page at a time\n")
                
        elif cmd == 'ipconfig':
            self.show_ipconfig()
            
        elif cmd == 'ping':
            host = args[0] if args else "127.0.0.1"
            self.ping_host(host)
            
        elif cmd == 'netstat':
            self.show_netstat()
            
        elif cmd == 'tasklist':
            self.show_tasklist()
            
        elif cmd == 'systeminfo':
            self.show_systeminfo()
            
        elif cmd == 'whoami':
            self.output_text.insert(tk.END, "windows\\user\n")
            
        elif cmd == 'shutdown':
            self.output_text.insert(tk.END, "The system will shutdown in 1 minute. Use 'shutdown /a' to abort.\n")
            
        # СЕКРЕТНЫЕ КОМАНДЫ
        elif cmd == 'jbmod':
            self.output_text.insert(tk.END, "JBmod это копирка гмода, пошёл он нахуй JBmod вирусы подкачивает всем\n")
            
        elif cmd == 'dm' and len(args) > 0 and args[0].lower() == 'editor':
            self.open_dm_editor()
            
        elif cmd == 'source' and len(args) > 1 and args[0].lower() == 'sample' and args[1].lower() == 'tool':
            self.output_text.insert(tk.END, "Error! Source Sample Tool and Dm Editor not found!\n")
            
        elif cmd == 'credits':
            self.show_credits()
            
        elif cmd.startswith('/cmd') and 'h4ck3r' in command.lower() and 'procces' in command.lower():
            mode = command.split()[-1].upper() if len(command.split()) > 3 else ""
            if mode in ['ON', 'OFF']:
                self.output_text.insert(tk.END, f"Hacker process {mode}\n")
                if mode == 'ON':
                    self.open_hacker_interface()
            else:
                self.output_text.insert(tk.END, "Invalid parameter. Use ON or OFF\n")
                
        elif command == "":
            pass  # Просто пустая строка
        else:
            self.output_text.insert(tk.END, f"'{command}' is not recognized as an internal or external command,\noperable program or batch file.\n")
        
        self.show_prompt()
        self.output_text.see(tk.END)
        return "break"
    
    def show_directory(self):
        self.output_text.insert(tk.END, f" Volume in drive {self.current_dir[0]} has no label.\n")
        self.output_text.insert(tk.END, f" Volume Serial Number is 1234-5678\n\n")
        self.output_text.insert(tk.END, f" Directory of {self.current_dir}\n\n")
        
        files = [
            ("12/05/2024  10:30 AM    <DIR>          ", "."),
            ("12/05/2024  10:30 AM    <DIR>          ", ".."),
            ("11/12/2024  02:22 PM           120,432 ", "cmd.exe"),
            ("10/15/2024  09:15 AM            45,678 ", "notepad.exe"),
            ("11/20/2024  04:45 PM           234,567 ", "explorer.exe"),
            ("09/05/2024  11:20 AM           156,789 ", "winlogon.exe"),
            ("08/12/2024  03:45 PM            89,123 ", "services.exe"),
        ]
        
        for date, name in files:
            self.output_text.insert(tk.END, f"{date}{name}\n")
            
        self.output_text.insert(tk.END, f"              {len(files)} File(s)      647,589 bytes\n")
        self.output_text.insert(tk.END, "              2 Dir(s)  150,234,567,890 bytes free\n")
    
    def change_directory(self, args):
        if not args:
            self.output_text.insert(tk.END, f"{self.current_dir}\n")
        elif args[0] == "..":
            if self.current_dir != "C:\\":
                parts = self.current_dir.split("\\")
                self.current_dir = "\\".join(parts[:-1]) if len(parts) > 1 else "C:\\"
        elif args[0] == "C:" or args[0] == "C:\\":
            self.current_dir = "C:\\"
        else:
            self.output_text.insert(tk.END, "The system cannot find the path specified.\n")
    
    def type_file(self, args):
        if not args:
            self.output_text.insert(tk.END, "The syntax of the command is incorrect.\n")
            return
            
        filename = args[0]
        file_contents = {
            "readme.txt": "This is a sample readme file.\nContains important information.\n",
            "config.ini": "[Settings]\nVersion=1.0\nPath=C:\\Program Files\\App\n",
            "log.txt": "2024-12-05 10:30:22 System started\n2024-12-05 10:31:15 User logged in\n"
        }
        
        if filename in file_contents:
            self.output_text.insert(tk.END, file_contents[filename])
        else:
            self.output_text.insert(tk.END, f"The system cannot find the file specified: {filename}\n")
    
    def show_ipconfig(self):
        self.output_text.insert(tk.END, "Windows IP Configuration\n\n")
        self.output_text.insert(tk.END, "Ethernet adapter Ethernet:\n")
        self.output_text.insert(tk.END, "   Connection-specific DNS Suffix  . : localdomain\n")
        self.output_text.insert(tk.END, "   IPv4 Address. . . . . . . . . . . : 192.168.1.2\n")
        self.output_text.insert(tk.END, "   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n")
        self.output_text.insert(tk.END, "   Default Gateway . . . . . . . . . : 192.168.1.1\n\n")
        self.output_text.insert(tk.END, "Wireless LAN adapter Wi-Fi:\n")
        self.output_text.insert(tk.END, "   Media State . . . . . . . . . . . : Media disconnected\n")
    
    def ping_host(self, host):
        self.output_text.insert(tk.END, f"Pinging {host} with 32 bytes of data:\n")
        
        def do_ping():
            for i in range(4):
                time.sleep(1)
                response_time = random.randint(1, 50)
                self.output_text.insert(tk.END, f"Reply from {host}: bytes=32 time={response_time}ms TTL=64\n")
                self.output_text.see(tk.END)
            
            self.output_text.insert(tk.END, f"\nPing statistics for {host}:\n")
            self.output_text.insert(tk.END, "    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)\n")
            self.output_text.insert(tk.END, "Approximate round trip times in milli-seconds:\n")
            self.output_text.insert(tk.END, "    Minimum = 1ms, Maximum = 50ms, Average = 25ms\n")
            self.output_text.see(tk.END)
        
        threading.Thread(target=do_ping, daemon=True).start()
    
    def show_netstat(self):
        self.output_text.insert(tk.END, "Active Connections\n\n")
        self.output_text.insert(tk.END, "  Proto  Local Address          Foreign Address        State\n")
        connections = [
            ("TCP", "192.168.1.2:49372", "52.114.128.67:443", "ESTABLISHED"),
            ("TCP", "192.168.1.2:49371", "40.97.107.65:443", "ESTABLISHED"),
            ("TCP", "192.168.1.2:49370", "13.107.136.9:443", "ESTABLISHED"),
            ("TCP", "192.168.1.2:49369", "204.79.197.222:443", "ESTABLISHED"),
        ]
        for proto, local, foreign, state in connections:
            self.output_text.insert(tk.END, f"  {proto:<6} {local:<21} {foreign:<21} {state}\n")
    
    def show_tasklist(self):
        self.output_text.insert(tk.END, "Image Name                     PID Session Name        Session#    Mem Usage\n")
        self.output_text.insert(tk.END, "========================= ======== ================ ========== ============\n")
        tasks = [
            ("System Idle Process", "0", "Services", "0", "24 K"),
            ("System", "4", "Services", "0", "3,124 K"),
            ("svchost.exe", "564", "Services", "0", "7,892 K"),
            ("explorer.exe", "2345", "Console", "1", "125,678 K"),
            ("notepad.exe", "2567", "Console", "1", "15,432 K"),
            ("cmd.exe", "2890", "Console", "1", "3,456 K"),
        ]
        for name, pid, session, session_num, mem in tasks:
            self.output_text.insert(tk.END, f"{name:<25} {pid:>8} {session:<16} {session_num:>9} {mem:>12}\n")
    
    def show_systeminfo(self):
        self.output_text.insert(tk.END, "Host Name:                 DESKTOP-ABC123\n")
        self.output_text.insert(tk.END, "OS Name:                   Microsoft Windows 10 Pro\n")
        self.output_text.insert(tk.END, "OS Version:                10.0.19045 N/A Build 19045\n")
        self.output_text.insert(tk.END, "OS Manufacturer:           Microsoft Corporation\n")
        self.output_text.insert(tk.END, "OS Configuration:          Standalone Workstation\n")
        self.output_text.insert(tk.END, "Registered Owner:          User\n")
        self.output_text.insert(tk.END, "Registered Organization:   N/A\n")
        self.output_text.insert(tk.END, "Product ID:                00331-10000-00001-AA123\n")
        self.output_text.insert(tk.END, "Original Install Date:     10/15/2024, 9:15:00 AM\n")
        self.output_text.insert(tk.END, "System Boot Time:          12/5/2024, 10:30:22 AM\n")
        self.output_text.insert(tk.END, "System Manufacturer:       Dell Inc.\n")
        self.output_text.insert(tk.END, "System Model:              OptiPlex 7070\n")
        self.output_text.insert(tk.END, "System Type:               x64-based PC\n")
        self.output_text.insert(tk.END, "Processor(s):              1 Processor(s) Installed.\n")
        self.output_text.insert(tk.END, "                           [01]: Intel64 Family 6 Model 158 Stepping 10 GenuineIntel ~3600 Mhz\n")
        self.output_text.insert(tk.END, "Total Physical Memory:     16,384 MB\n")
    
    def show_credits(self):
        self.output_text.insert(tk.END, "\n")
        self.output_text.insert(tk.END, "╔══════════════════════════════════════╗\n")
        self.output_text.insert(tk.END, "║           CREDITS                     ║\n")
        self.output_text.insert(tk.END, "║                                      ║\n")
        self.output_text.insert(tk.END, "║    Created by: ihateRatibor          ║\n")
        self.output_text.insert(tk.END, "║                                      ║\n")
        self.output_text.insert(tk.END, "║    Special thanks to:                ║\n")
        self.output_text.insert(tk.END, "║    - The hacking community           ║\n")
        self.output_text.insert(tk.END, "║    - Open source developers          ║\n")
        self.output_text.insert(tk.END, "║    - All beta testers                ║\n")
        self.output_text.insert(tk.END, "║                                      ║\n")
        self.output_text.insert(tk.END, "╚══════════════════════════════════════╝\n")
        self.output_text.insert(tk.END, "\n")
    
    def open_dm_editor(self):
        dm_window = tk.Toplevel(self.root)
        dm_window.title("DM Editor")
        app = DMEditor(dm_window)
        
        # Запускаем анимацию DM Editor
        def run_dm_editor():
            app.animate()
            dm_window.after(50, run_dm_editor)
        
        dm_window.after(50, run_dm_editor)
    
    def open_hacker_interface(self):
        hacker_window = tk.Toplevel(self.root)
        hacker_window.title("Advanced System Scanner")
        HackerSimulator(hacker_window)

class HackerSimulator:
    def __init__(self, window):
        self.window = window
        self.window.geometry("700x500")
        self.window.configure(bg='black')
        
        # Создаем вкладки
        notebook = ttk.Notebook(window)
        
        # Вкладка взлома паролей
        pass_frame = ttk.Frame(notebook)
        self.setup_password_tab(pass_frame)
        
        # Вкладка сетевого сканирования
        net_frame = ttk.Frame(notebook)
        self.setup_network_tab(net_frame)
        
        # Вкладка удаленного взлома
        remote_frame = ttk.Frame(notebook)
        self.setup_remote_tab(remote_frame)
        
        # Вкладка крипто-майнинга
        crypto_frame = ttk.Frame(notebook)
        self.setup_crypto_tab(crypto_frame)
        
        notebook.add(pass_frame, text="Password Cracker")
        notebook.add(net_frame, text="Network Scanner")
        notebook.add(remote_frame, text="Remote Access")
        notebook.add(crypto_frame, text="Crypto Miner")
        notebook.pack(expand=True, fill='both')
    
    def setup_password_tab(self, frame):
        style = ttk.Style()
        style.configure("Hacker.TLabel", foreground="cyan", background="black")
        
        ttk.Label(frame, text="Target URL/IP:", style="Hacker.TLabel").pack(pady=5)
        self.target_entry = tk.Entry(frame, width=50, bg='black', fg='white', insertbackground='white')
        self.target_entry.pack(pady=5)
        
        tk.Button(frame, text="Start Brute Force", command=self.start_brute_force, 
                 bg='darkblue', fg='white').pack(pady=5)
        
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            frame, 
            bg='black', 
            fg='white',
            font=('Courier New', 10),
            insertbackground='white'
        )
        self.log_text.pack(fill='both', expand=True)
        
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='yellow')
        self.log_text.tag_config('info', foreground='cyan')
    
    def setup_network_tab(self, frame):
        tk.Button(frame, text="Scan Local Network", command=self.scan_network,
                 bg='darkblue', fg='white').pack(pady=5)
        tk.Button(frame, text="Get Public IP", command=self.get_public_ip,
                 bg='darkblue', fg='white').pack(pady=5)
        tk.Button(frame, text="Port Scanner", command=self.port_scan,
                 bg='darkblue', fg='white').pack(pady=5)
        
        self.network_text = scrolledtext.ScrolledText(
            frame, 
            bg='black', 
            fg='white',
            font=('Courier New', 10),
            insertbackground='white'
        )
        self.network_text.pack(fill='both', expand=True)
        
        self.network_text.tag_config('success', foreground='green')
        self.network_text.tag_config('info', foreground='cyan')
    
    def setup_remote_tab(self, frame):
        ttk.Label(frame, text="Remote IP Address:", style="Hacker.TLabel").pack(pady=5)
        self.remote_ip = tk.Entry(frame, width=50, bg='black', fg='white', insertbackground='white')
        self.remote_ip.pack(pady=5)
        
        tk.Button(frame, text="Establish Connection", command=self.remote_hack,
                 bg='darkblue', fg='white').pack(pady=5)
        tk.Button(frame, text="Keylogger Install", command=self.keylogger_install,
                 bg='darkblue', fg='white').pack(pady=5)
        
        self.remote_text = scrolledtext.ScrolledText(
            frame, 
            bg='black', 
            fg='white',
            font=('Courier New', 10),
            insertbackground='white'
        )
        self.remote_text.pack(fill='both', expand=True)
    
    def setup_crypto_tab(self, frame):
        ttk.Label(frame, text="Bitcoin Wallet:", style="Hacker.TLabel").pack(pady=5)
        self.wallet_entry = tk.Entry(frame, width=50, bg='black', fg='white', insertbackground='white')
        self.wallet_entry.insert(0, "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        self.wallet_entry.pack(pady=5)
        
        tk.Button(frame, text="Start Mining", command=self.start_mining,
                 bg='darkblue', fg='white').pack(pady=5)
        
        self.mining_progress = ttk.Progressbar(frame, mode='determinate')
        self.mining_progress.pack(fill='x', padx=10, pady=5)
        
        self.mining_text = scrolledtext.ScrolledText(
            frame, 
            bg='black', 
            fg='white',
            font=('Courier New', 10),
            insertbackground='white'
        )
        self.mining_text.pack(fill='both', expand=True)
        
        self.mining_text.tag_config('success', foreground='green')
        self.mining_text.tag_config('bitcoin', foreground='orange')
    
    def start_brute_force(self):
        target = self.target_entry.get() or "192.168.1.1"
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Starting brute force attack on: {target}\n", 'info')
        self.log_text.insert(tk.END, "Initializing password database...\n", 'info')
        self.progress.start(10)
        
        def brute_force():
            passwords = [
                'admin', 'password', '123456', 'qwerty', 'password123',
                'admin123', 'letmein', 'welcome', 'monkey', '123456789',
                '12345678', '12345', '1234567', 'sunshine', 'princess'
            ]
            
            for i, pwd in enumerate(passwords):
                time.sleep(0.5)
                self.log_text.insert(tk.END, f"Attempt {i+1}: Trying '{pwd}'...\n")
                self.log_text.see(tk.END)
                
                if random.random() > 0.8:
                    self.log_text.insert(tk.END, "✓ SUCCESS! Password accepted.\n", 'success')
                    self.log_text.insert(tk.END, f"Access granted to {target}\n", 'success')
                    self.log_text.insert(tk.END, "Downloading sensitive data...\n", 'info')
                    break
            else:
                self.log_text.insert(tk.END, "✗ Failed to crack password\n", 'error')
            
            self.progress.stop()
        
        threading.Thread(target=brute_force, daemon=True).start()
    
    def scan_network(self):
        self.network_text.delete(1.0, tk.END)
        self.network_text.insert(tk.END, "Scanning local network...\n", 'info')
        
        devices = [
            ('192.168.1.1', 'Router', 'Online', 'Cisco'),
            ('192.168.1.2', 'Main-PC', 'Online', 'Windows 10'),
            ('192.168.1.3', 'Smartphone', 'Online', 'Android'),
            ('192.168.1.100', 'Printer', 'Offline', 'HP LaserJet'),
            ('192.168.1.101', 'IoT-Device', 'Online', 'Smart TV')
        ]
        
        for ip, name, status, device_type in devices:
            time.sleep(0.3)
            status_color = 'success' if status == 'Online' else 'error'
            self.network_text.insert(tk.END, f"Found: {ip} - {name} - {device_type} - ", 'info')
            self.network_text.insert(tk.END, f"{status}\n", status_color)
            self.network_text.see(tk.END)
    
    def get_public_ip(self):
        def fetch_ip():
            try:
                self.network_text.insert(tk.END, "Requesting public IP address...\n", 'info')
                ip = requests.get('https://api.ipify.org', timeout=5).text
                self.network_text.insert(tk.END, f"Public IP Address: {ip}\n", 'success')
                
                # Симуляция геолокации
                locations = ["New York, USA", "London, UK", "Tokyo, Japan", "Berlin, Germany"]
                isps = ["Comcast", "Verizon", "AT&T", "Deutsche Telekom"]
                self.network_text.insert(tk.END, f"Approximate Location: {random.choice(locations)}\n", 'info')
                self.network_text.insert(tk.END, f"ISP: {random.choice(isps)}\n", 'info')
            except:
                self.network_text.insert(tk.END, "Failed to retrieve public IP\n", 'error')
        
        threading.Thread(target=fetch_ip, daemon=True).start()
    
    def port_scan(self):
        target = self.target_entry.get() or "192.168.1.1"
        self.network_text.insert(tk.END, f"Scanning ports on {target}...\n", 'info')
        
        def scan():
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389]
            for port in ports:
                time.sleep(0.2)
                if random.random() > 0.7:
                    self.network_text.insert(tk.END, f"Port {port}: OPEN\n", 'success')
                else:
                    self.network_text.insert(tk.END, f"Port {port}: CLOSED\n")
                self.network_text.see(tk.END)
        
        threading.Thread(target=scan, daemon=True).start()
    
    def remote_hack(self):
        ip = self.remote_ip.get() or "93.184.216.34"
        self.remote_text.delete(1.0, tk.END)
        self.remote_text.insert(tk.END, f"Initializing connection to {ip}...\n")
        
        def hack_attempt():
            steps = [
                ("Connecting to target...", 1),
                ("Bypassing firewall...", 2),
                ("Scanning for vulnerabilities...", 3),
                ("Exploiting CVE-2024-XXXX...", 2),
                ("Uploading payload...", 2),
                ("Executing remote code...", 1),
                ("Installing persistence module...", 2),
                ("Cleaning traces...", 1)
            ]
            
            for step, delay in steps:
                time.sleep(delay)
                self.remote_text.insert(tk.END, f"[+] {step}\n")
                self.remote_text.see(tk.END)
            
            if random.random() > 0.3:
                self.remote_text.insert(tk.END, "✓ Remote access established!\n")
                self.remote_text.insert(tk.END, "You now have full control of the target system.\n")
            else:
                self.remote_text.insert(tk.END, "✗ Connection failed - Target system defended\n")
        
        threading.Thread(target=hack_attempt, daemon=True).start()
    
    def keylogger_install(self):
        ip = self.remote_ip.get() or "192.168.1.2"
        self.remote_text.insert(tk.END, f"Installing keylogger on {ip}...\n")
        
        def install():
            steps = [
                "Bypassing antivirus...",
                "Injecting into system process...",
                "Configuring data exfiltration...",
                "Setting up encryption...",
                "Starting keylogger service..."
            ]
            
            for step in steps:
                time.sleep(1.5)
                self.remote_text.insert(tk.END, f"[>] {step}\n")
                self.remote_text.see(tk.END)
            
            self.remote_text.insert(tk.END, "✓ Keylogger successfully installed and active\n")
        
        threading.Thread(target=install, daemon=True).start()
    
    def start_mining(self):
        wallet = self.wallet_entry.get()
        self.mining_text.delete(1.0, tk.END)
        self.mining_text.insert(tk.END, f"Starting cryptocurrency miner...\n", 'info')
        self.mining_text.insert(tk.END, f"Wallet: {wallet}\n", 'info')
        self.mining_progress['value'] = 0
        
        def mine():
            hashes = 0
            while hashes < 100:
                time.sleep(0.1)
                hashes += random.randint(1, 5)
                self.mining_progress['value'] = hashes
                
                if random.random() < 0.05:  # 5% шанс найти блок
                    btc = random.uniform(0.0001, 0.001)
                    self.mining_text.insert(tk.END, f"✓ Block found! +{btc:.6f} BTC\n", 'bitcoin')
                    self.mining_text.see(tk.END)
                elif hashes % 20 == 0:
                    self.mining_text.insert(tk.END, f"Calculating hashes: {hashes}/100\n")
                    self.mining_text.see(tk.END)
        
        threading.Thread(target=mine, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsoleSimulator(root)
    root.mainloop()