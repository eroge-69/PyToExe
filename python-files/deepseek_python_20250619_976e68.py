import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
import math

# Упрощенная версия без сложных градиентов
class TimeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("⏱️ TimeSpan Calculator")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        self.root.configure(bg="#1e3b5a")
        
        # Стили
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настройка цветов
        self.bg_color = "#1e3b5a"
        self.entry_bg = "#2a4b6e"
        self.button_color = "#4b6cb7"
        self.result_bg = "#2a4b6e"
        
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=15, fill="x", padx=20)
        
        header_label = tk.Label(
            header_frame, 
            text="⏱️ CALCULATE TIME SPAN",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_color,
            fg="#ffffff"
        )
        header_label.pack()
        
        subheader_label = tk.Label(
            header_frame, 
            text="Calculate exact time between two dates",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="#a0c0ff"
        )
        subheader_label.pack(pady=5)
        
        # Поля ввода
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=30, pady=15)
        
        # Первая дата
        date1_frame = ttk.Frame(input_frame)
        date1_frame.pack(fill="x", pady=10)
        
        tk.Label(
            date1_frame, 
            text="START DATE & TIME:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg="#ffffff"
        ).pack(side="left", anchor="w", padx=(0, 10))
        
        self.entry1 = tk.Entry(
            date1_frame, 
            width=30,
            font=("Segoe UI", 11),
            bg=self.entry_bg,
            fg="#ffffff",
            insertbackground="white",
            relief="flat"
        )
        self.entry1.pack(side="right", fill="x", expand=True, ipady=4)
        self.entry1.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Вторая дата
        date2_frame = ttk.Frame(input_frame)
        date2_frame.pack(fill="x", pady=10)
        
        tk.Label(
            date2_frame, 
            text="END DATE & TIME:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg="#ffffff"
        ).pack(side="left", anchor="w", padx=(0, 10))
        
        self.entry2 = tk.Entry(
            date2_frame, 
            width=30,
            font=("Segoe UI", 11),
            bg=self.entry_bg,
            fg="#ffffff",
            insertbackground="white",
            relief="flat"
        )
        self.entry2.pack(side="right", fill="x", expand=True, ipady=4)
        self.entry2.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Кнопка расчета
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.calculate_btn = tk.Button(
            button_frame,
            text="🔄 CALCULATE TIME DIFFERENCE",
            command=self.calculate_hours,
            font=("Segoe UI", 12, "bold"),
            bg=self.button_color,
            fg="#ffffff",
            activebackground="#5a7bc7",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.calculate_btn.pack()
        
        # Поле результата
        self.result_frame = tk.Frame(
            self.root,
            bg=self.result_bg,
            bd=2,
            relief="solid"
        )
        self.result_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        self.result_label = tk.Label(
            self.result_frame,
            text="Enter dates and click CALCULATE",
            font=("Segoe UI", 11),
            bg=self.result_bg,
            fg="#f0f0f0",
            justify="left",
            anchor="nw"
        )
        self.result_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Подсказки
        footer_label = tk.Label(
            self.root,
            text="Supported formats: YYYY-MM-DD HH:MM | DD.MM.YYYY | DD/MM/YYYY HH:MM:SS",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg="#aaaaaa"
        )
        footer_label.pack(side="bottom", pady=10)
    
    def parse_datetime(self, input_str):
        formats = [
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M",
            "%d.%m.%Y %H:%M:%S", "%d.%m.%Y", "%d.%m.%Y %H:%M",
            "%H:%M %d.%m.%Y", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"
        ]
        
        input_str = input_str.strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(input_str, fmt)
            except ValueError:
                continue
        
        raise ValueError("Invalid date format")
    
    def calculate_hours(self):
        try:
            date1_str = self.entry1.get()
            date2_str = self.entry2.get()
            
            dt1 = self.parse_datetime(date1_str)
            dt2 = self.parse_datetime(date2_str)
            
            time_diff = dt2 - dt1
            total_seconds = time_diff.total_seconds()
            
            # Показать индикатор загрузки
            self.result_label.config(text="Calculating...")
            self.root.update()
            
            if total_seconds >= 0:
                direction = "прошло"
            else:
                direction = "осталось"
                total_seconds = abs(total_seconds)
            
            total_hours = total_seconds / 3600
            total_days = total_hours / 24
            total_weeks = total_days / 7
            
            # Форматируем результат
            result_text = f"🕒 Между датами {direction}:\n\n"
            result_text += f"• {total_seconds:,.0f} секунд\n"
            result_text += f"• {total_seconds/60:,.0f} минут\n"
            result_text += f"• {total_hours:,.2f} часов\n"
            result_text += f"• {total_days:,.2f} дней\n"
            result_text += f"• {total_weeks:,.2f} недель\n\n"
            
           