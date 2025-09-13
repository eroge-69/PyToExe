import tkinter as tk
from tkinter import scrolledtext
import random

class StarkOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Stark OS v1.0")
        self.root.configure(bg="#1a1a1a")
        
        # Создание панели терминала
        self.terminal_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание области вывода
        self.output = scrolledtext.ScrolledText(
            self.terminal_frame,
            bg="#1a1a1a",
            fg="#03a9f4",
            font=("Courier New", 12),
            highlightthickness=0,
            borderwidth=0,
            insertbackground="#ff6d00"
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Создание панели отладки
        self.debug_panel = tk.Frame(self.root, bg="#222222")
        self.debug_panel.pack(fill=tk.Y, side=tk.RIGHT)
        
        # Создание поля ввода
        self.input_frame = tk.Frame(self.terminal_frame, bg="#1a1a1a")
        self.input_frame.pack(fill=tk.X)
        
        self.input_var = tk.StringVar()
        self.input_field = tk.Entry(
            self.input_frame,
            bg="#1a1a1a",
            fg="#ff6d00",
            font=("Courier New", 12),
            textvariable=self.input_var,
            highlightthickness=0,
            borderwidth=0
        )
        self.input_field.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопка отправки
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            bg="#1a1a1a",
            fg="#03a9f4",
            borderwidth=0,
            command=self.send_command
        )
        self.send_button.pack(padx=5, pady=5)
        
        # Логотип
        self.output.insert(tk.END, "\n\n")
        self.output.insert(tk.END, "Stark OS v1.0\n\n", ("header",))
        self.output.tag_config("header", foreground="#ff6d00", font=("Courier New", 16, "bold"))
        
        # Курсор
        self.cursor = tk.Label(
            self.input_frame,
            text="|",
            fg="#03a9f4",
            font=("Courier New", 12)
        )
        self.cursor.pack(side=tk.LEFT)
        self.blink_cursor()
        
        # Привязка клавиш
        self.root.bind('<Return>', self.send_command)
        
        # Отладочные данные
        self.update_debug_panel()
        
    def blink_cursor(self):
        if self.cursor.cget("text") == "|":
            self.cursor.config(text=" ")
        else:
            self.cursor.config(text="|")
        self.root.after(500, self.blink_cursor)
    
    def update_debug_panel(self):
        # Обновление данных отладки
        self.debug_panel.destroy()
        self.debug_panel = tk.Frame(self.root, bg="#222222")
        self.debug_panel.pack(fill=tk.Y, side=tk.RIGHT)
        
        tk.Label(
            self.debug_panel,
            text="JARVIS Debug Panel",
            fg="#ff6d