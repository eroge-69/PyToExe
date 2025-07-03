import customtkinter as ctk
import threading
import time
import keyboard
from pynput.mouse import Button, Controller
from PIL import Image
import os
import sys

# Настройка темы
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

class RASDclicker:
    def __init__(self, root):
        self.root = root
        self.root.title("RASDclicker v3.0")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        # Иконка приложения (замените rasd_icon.ico на свой файл)
        try:
            self.root.iconbitmap("rasd_icon.ico")
        except:
            pass
        
        self.mouse = Controller()
        self.clicking = False
        self.delay = 100
        self.total_clicks = 0
        self.click_type = "left"  # left/right/middle
        
        # Стиль
        self.accent_color = "#00FFAA"
        self.danger_color = "#FF5555"
        
        self.setup_ui()
        self.setup_keyboard_listener()
        self.update_ui()

    def setup_ui(self):
        # Главный контейнер
        self.main_frame = ctk.CTkFrame(
            self.root, 
            corner_radius=20,
            border_width=2,
            border_color=self.accent_color
        )
        self.main_frame.pack(pady=25, padx=25, fill="both", expand=True)
        
        # Заголовок с неоновым эффектом
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="RASDclicker",
            font=("Impact", 28),
            text_color=self.accent_color
        )
        self.title_label.pack(pady=(20, 15))
        
        # Блок управления
        control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        control_frame.pack(pady=10, padx=20, fill="x")
        
        # Выбор типа клика
        self.click_type_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["Левый клик", "Правый клик", "Средняя кнопка"],
            command=self.change_click_type,
            fg_color="#1E1E2E",
            button_color=self.accent_color,
            dropdown_fg_color="#1E1E2E"
        )
        self.click_type_menu.pack(side="left", padx=(0, 10))
        
        # Кнопка экстренной остановки
        self.emergency_btn = ctk.CTkButton(
            control_frame,
            text="ЭКСТРЕННАЯ ОСТАНОВКА (F7)",
            command=self.emergency_stop,
            fg_color=self.danger_color,
            hover_color="#FF0000",
            font=("Arial", 10, "bold")
        )
        self.emergency_btn.pack(side="right")
        
        # Слайдер задержки
        self.delay_slider = ctk.CTkSlider(
            self.main_frame,
            from_=10,
            to=1000,
            number_of_steps=99,
            command=self.update_delay,
            progress_color=self.accent_color,
            button_color=self.accent_color,
            button_hover_color="#00CC88"
        )
        self.delay_slider.set(self.delay)
        self.delay_slider.pack(pady=(15, 5), padx=40, fill="x")
        
        self.delay_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Интервал: {self.delay} мс",
            font=("Arial", 12),
            text_color="#AAAAAA"
        )
        self.delay_label.pack()
        
        # Основная кнопка
        self.main_button = ctk.CTkButton(
            self.main_frame,
            text="▶ ЗАПУСК (F6)",
            command=self.toggle_clicking,
            font=("Arial", 16, "bold"),
            fg_color=self.accent_color,
            hover_color="#00CC88",
            height=45,
            corner_radius=12,
            border_width=2,
            border_color="#FFFFFF"
        )
        self.main_button.pack(pady=20, fill="x", padx=60)
        
        # Статистика
        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.pack(pady=10)
        
        self.clicks_label = ctk.CTkLabel(
            stats_frame,
            text="Всего кликов: 0",
            font=("Arial", 12, "bold"),
            text_color=self.accent_color
        )
        self.clicks_label.pack(side="left", padx=10)
        
        # Статус
        self.status_indicator = ctk.CTkLabel(
            self.main_frame,
            text="■ СТОП",
            font=("Arial", 12),
            text_color=self.danger_color
        )
        self.status_indicator.pack(pady=(0, 20))

    def change_click_type(self, choice):
        self.click_type = {
            "Левый клик": "left",
            "Правый клик": "right",
            "Средняя кнопка": "middle"
        }[choice]

    def update_delay(self, value):
        self.delay = int(value)
        self.delay_label.configure(text=f"Интервал: {self.delay} мс")

    def setup_keyboard_listener(self):
        keyboard.add_hotkey('f6', self.toggle_clicking)
        keyboard.add_hotkey('f7', self.emergency_stop)

    def toggle_clicking(self):
        self.clicking = not self.clicking
        
        if self.clicking:
            self.main_button.configure(
                text="■ СТОП (F6)",
                fg_color=self.danger_color,
                hover_color="#FF3333"
            )
            self.status_indicator.configure(
                text="▶ ВЫПОЛНЯЕТСЯ",
                text_color="#00FFAA"
            )
            threading.Thread(target=self.click_loop, daemon=True).start()
        else:
            self.main_button.configure(
                text="▶ ЗАПУСК (F6)",
                fg_color=self.accent_color,
                hover_color="#00CC88"
            )
            self.status_indicator.configure(
                text="■ СТОП",
                text_color=self.danger_color
            )

    def emergency_stop(self):
        if self.clicking:
            self.toggle_clicking()
            self.status_indicator.configure(
                text="⚠ АВАРИЙНАЯ ОСТАНОВКА",
                text_color="#FFAA00"
            )
            self.root.after(2000, lambda: self.status_indicator.configure(
                text="■ СТОП",
                text_color=self.danger_color
            ))

    def click_loop(self):
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        
        while self.clicking:
            self.mouse.click(button_map[self.click_type])
            self.total_clicks += 1
            self.clicks_label.configure(text=f"Всего кликов: {self.total_clicks}")
            time.sleep(self.delay / 1000)

    def update_ui(self):
        # Анимация заголовка
        def pulse_title():
            for color in ["#00FFAA", "#00FF88", "#00FFAA", "#00CCFF"]:
                self.title_label.configure(text_color=color)
                self.root.update()
                time.sleep(0.3)
            self.root.after(0, pulse_title)
        
        pulse_title()

if __name__ == "__main__":
    root = ctk.CTk()
    app = RASDclicker(root)
    root.mainloop()