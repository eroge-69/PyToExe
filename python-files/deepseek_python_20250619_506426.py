import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import math

class TimeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("⏱️ Временной калькулятор")
        self.root.geometry("700x600")
        self.root.configure(bg="#0f1b2e")
        
        # Цветовая схема
        self.bg_color = "#0f1b2e"
        self.card_bg = "#1a2b4d"
        self.entry_bg = "#25375a"
        self.button_bg = "#4b6cb7"
        self.button_active = "#5a7bc7"
        self.text_color = "#e0f0ff"
        self.accent_color = "#5a7bc7"
        
        self.create_gui()
        
    def create_gui(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="⏱️ Временной калькулятор",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg="#ffffff"
        ).pack(pady=5)
        
        tk.Label(
            header_frame,
            text="Калькулятор между двумя датами",
            font=("Arial", 10),
            bg=self.bg_color,
            fg="#a0c0ff"
        ).pack()
        
        # Карта ввода
        input_card = tk.Frame(
            main_frame,
            bg=self.card_bg,
            bd=2,
            relief="groove",
            padx=20,
            pady=20
        )
        input_card.pack(fill="x", pady=10)
        
        # Первая дата
        date1_frame = tk.Frame(input_card, bg=self.card_bg)
        date1_frame.pack(fill="x", pady=8)
        
        tk.Label(
            date1_frame,
            text="Первая дата",
            font=("Arial", 10, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        self.entry1 = tk.Entry(
            date1_frame,
            width=25,
            font=("Arial", 11),
            bg=self.entry_bg,
            fg="#ffffff",
            insertbackground="white",
            relief="flat"
        )
        self.entry1.pack(side="right", fill="x", expand=True, ipady=4)
        self.entry1.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Вторая дата
        date2_frame = tk.Frame(input_card, bg=self.card_bg)
        date2_frame.pack(fill="x", pady=8)
        
        tk.Label(
            date2_frame,
            text="Вторая дата",
            font=("Arial", 10, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        ).pack(side="left", padx=(0, 10))
        
        self.entry2 = tk.Entry(
            date2_frame,
            width=25,
            font=("Arial", 11),
            bg=self.entry_bg,
            fg="#ffffff",
            insertbackground="white",
            relief="flat"
        )
        self.entry2.pack(side="right", fill="x", expand=True, ipady=4)
        self.entry2.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Кнопка расчета
        self.calculate_btn = tk.Button(
            main_frame,
            text="🔄 Нажать для высчитывания",
            command=self.calculate_hours,
            font=("Arial", 12, "bold"),
            bg=self.button_bg,
            fg="#ffffff",
            activebackground=self.button_active,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.calculate_btn.pack(pady=20)
        
        # Привязка событий для hover-эффекта
        self.calculate_btn.bind("<Enter>", lambda e: self.calculate_btn.config(bg=self.button_active))
        self.calculate_btn.bind("<Leave>", lambda e: self.calculate_btn.config(bg=self.button_bg))
        
        # Карта результата
        result_card = tk.Frame(
            main_frame,
            bg=self.card_bg,
            bd=2,
            relief="groove",
            padx=15,
            pady=15
        )
        result_card.pack(fill="both", expand=True)
        
        self.result_label = tk.Label(
            result_card,
            text="Поле для вычисления",
            font=("Arial", 11),
            bg=self.card_bg,
            fg=self.text_color,
            justify="left",
            anchor="nw"
        )
        self.result_label.pack(fill="both", expand=True)
        
        # Подсказки
        tk.Label(
            main_frame,
            text="Поддерживает форматы: ГОД-МЕСЯЦ-ДЕНЬ ЧАС:МИНУТЫ | ДЕНЬ.МЕСЯЦ.ГОД | ДЕНЬ/МЕСЯЦ/ГОД ЧАС:МИНУТЫ:СЕКУНДЫ",
            font=("Arial", 8),
            bg=self.bg_color,
            fg="#aaaaaa"
        ).pack(side="bottom", pady=10)
    
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
            # Временно меняем текст кнопки для индикации работы
            original_text = self.calculate_btn.cget("text")
            self.calculate_btn.config(text="⏳ Calculating...")
            self.root.update()
            
            date1_str = self.entry1.get()
            date2_str = self.entry2.get()
            
            dt1 = self.parse_datetime(date1_str)
            dt2 = self.parse_datetime(date2_str)
            
            time_diff = dt2 - dt1
            total_seconds = time_diff.total_seconds()
            
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
            
            # Визуализация
            bar_length = min(50, int(total_hours/10) + 1)
            result_text += "▰" * bar_length
            
            self.result_label.config(text=result_text)
            
        except Exception as e:
            messagebox.showerror(
                "Ошибка", 
                f"Неправильный формат даты!\n\nПримеры правильных форматов:\n"
                f"2025-03-15 14:30\n15.03.2025\n03/15/2025 08:45"
            )
            self.result_label.config(text="Enter dates and click CALCULATE")
        finally:
            # Восстанавливаем кнопку
            self.calculate_btn.config(text=original_text)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeCalculator(root)
    
    # Центрирование окна
    window_width = 700
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.mainloop()
