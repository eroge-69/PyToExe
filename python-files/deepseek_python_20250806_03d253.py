import tkinter as tk
from tkinter import font
import pyautogui
import keyboard
from threading import Thread, Lock
import time
import random
import math
import sys

class DiscoClicker:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("DISCO CLICKER v3.3 (Геометрическая Тьма)")
        self.window.geometry("550x600")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.safe_exit)

        # Состояния
        self.running = False
        self.lock = Lock()
        self.current_speed = 10
        self.total_clicks = 0
        self.anti_detect = False
        self.clone_mode = False
        self.clone_multiplier = 5

        # Цвета
        self.bg_color = "#0a0a0a"
        self.text_color = "#ffffff"
        self.accent_color = "#00ffff"
        self.warning_color = "#ff00ff"
        self.success_color = "#00ff00"
        self.error_color = "#ff0000"

        # Создаём интерфейс
        self.setup_ui()

        # Горячие клавиши
        keyboard.add_hotkey('f8', self.start_clicking)
        keyboard.add_hotkey('f9', self.stop_clicking, suppress=True)
        keyboard.add_hotkey('f11', self.toggle_anti_detect)

    def setup_ui(self):
        # Главный холст
        self.canvas = tk.Canvas(self.window, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Рисуем геометрический фон
        self.draw_background()

        # Основной фрейм
        main_frame = tk.Frame(self.canvas, bg=self.bg_color)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Логотип
        logo_font = font.Font(family="Impact", size=24)
        tk.Label(main_frame, 
                text="DISCO CLICKER v3.3", 
                font=logo_font, 
                fg=self.accent_color, 
                bg=self.bg_color).pack(pady=(0, 20))

        # Управление скоростью
        speed_frame = tk.Frame(main_frame, bg=self.bg_color)
        speed_frame.pack(pady=5)

        tk.Label(speed_frame, 
                text="СКОРОСТЬ (CPS):", 
                font=("Arial", 10), 
                fg=self.text_color, 
                bg=self.bg_color).pack()

        btn_frame = tk.Frame(speed_frame, bg=self.bg_color)
        btn_frame.pack()

        self.speed_btn_minus = tk.Button(btn_frame, 
                                       text="-", 
                                       font=("Arial", 12), 
                                       width=3,
                                       bg="#333333", 
                                       fg=self.text_color,
                                       command=lambda: self.change_speed(-1))
        self.speed_btn_minus.pack(side="left", padx=5)

        self.speed_label = tk.Label(btn_frame, 
                                   text="10", 
                                   font=("Arial", 14), 
                                   fg=self.accent_color, 
                                   bg=self.bg_color)
        self.speed_label.pack(side="left", padx=5)

        self.speed_btn_plus = tk.Button(btn_frame, 
                                       text="+", 
                                       font=("Arial", 12), 
                                       width=3,
                                       bg="#333333", 
                                       fg=self.text_color,
                                       command=lambda: self.change_speed(1))
        self.speed_btn_plus.pack(side="left", padx=5)

        # Множитель кликов
        multiplier_frame = tk.Frame(main_frame, bg=self.bg_color)
        multiplier_frame.pack(pady=5)

        tk.Label(multiplier_frame, 
                text="МНОЖИТЕЛЬ КЛИКОВ:", 
                font=("Arial", 10), 
                fg=self.text_color, 
                bg=self.bg_color).pack()

        btn_mult_frame = tk.Frame(multiplier_frame, bg=self.bg_color)
        btn_mult_frame.pack()

        self.mult_btn_minus = tk.Button(btn_mult_frame, 
                                       text="-", 
                                       font=("Arial", 12), 
                                       width=3,
                                       bg="#333333", 
                                       fg=self.text_color,
                                       command=lambda: self.change_multiplier(-1))
        self.mult_btn_minus.pack(side="left", padx=5)

        self.multiplier_label = tk.Label(btn_mult_frame, 
                                        text="5", 
                                        font=("Arial", 14), 
                                        fg=self.warning_color, 
                                        bg=self.bg_color)
        self.multiplier_label.pack(side="left", padx=5)

        self.mult_btn_plus = tk.Button(btn_mult_frame, 
                                      text="+", 
                                      font=("Arial", 12), 
                                      width=3,
                                      bg="#333333", 
                                      fg=self.text_color,
                                      command=lambda: self.change_multiplier(1))
        self.mult_btn_plus.pack(side="left", padx=5)

        # Счётчик кликов
        self.clicks_label = tk.Label(main_frame, 
                                   text="Кликов: 0", 
                                   font=("Arial", 12), 
                                   fg=self.success_color, 
                                   bg=self.bg_color)
        self.clicks_label.pack(pady=10)

        # Кнопки режимов
        mode_frame = tk.Frame(main_frame, bg=self.bg_color)
        mode_frame.pack(pady=10)

        self.anti_btn = tk.Button(mode_frame, 
                                text="Тень Зеты (F11)", 
                                font=("Arial", 10), 
                                bg="#330033", 
                                fg=self.text_color,
                                command=self.toggle_anti_detect)
        self.anti_btn.grid(row=0, column=0, padx=5)

        self.clone_btn = tk.Button(mode_frame, 
                                 text="Режим Клонов", 
                                 font=("Arial", 10), 
                                 bg="#003300", 
                                 fg=self.text_color,
                                 command=self.toggle_clone_mode)
        self.clone_btn.grid(row=0, column=1, padx=5)

        # Кнопки управления
        ctrl_frame = tk.Frame(main_frame, bg=self.bg_color)
        ctrl_frame.pack(pady=10)

        self.start_btn = tk.Button(ctrl_frame, 
                                 text="СТАРТ (F8)", 
                                 font=("Arial", 10), 
                                 bg="#006600", 
                                 fg=self.text_color,
                                 command=self.start_clicking)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = tk.Button(ctrl_frame, 
                                text="СТОП (F9)", 
                                font=("Arial", 10), 
                                bg="#660000", 
                                fg=self.text_color,
                                command=self.stop_clicking)
        self.stop_btn.grid(row=0, column=1, padx=5)

        # Статус
        self.status = tk.Label(main_frame, 
                             text="Готов к работе", 
                             font=("Arial", 10), 
                             fg=self.success_color, 
                             bg=self.bg_color)
        self.status.pack(pady=10)

    def draw_background(self):
        """Рисуем геометрический фон на холсте"""
        width = 550
        height = 600
        
        # Вертикальные линии
        for x in range(0, width, 20):
            self.canvas.create_line(x, 0, x, height, fill="#111111", width=1)
        
        # Горизонтальные линии
        for y in range(0, height, 20):
            self.canvas.create_line(0, y, width, y, fill="#111111", width=1)
        
        # Центральный круг
        self.canvas.create_oval(200, 200, 350, 350, outline="#1a1a1a", width=2)

    def change_speed(self, delta):
        self.current_speed = max(1, min(30, self.current_speed + delta))
        self.speed_label.config(text=str(self.current_speed))

    def change_multiplier(self, delta):
        self.clone_multiplier = max(1, min(20, self.clone_multiplier + delta))
        self.multiplier_label.config(text=str(self.clone_multiplier))
        if self.clone_mode:
            self.status.config(text=f"Клоны: ВКЛ (x{self.clone_multiplier})")

    def toggle_anti_detect(self):
        self.anti_detect = not self.anti_detect
        color = self.warning_color if self.anti_detect else "#330033"
        self.anti_btn.config(bg=color)
        self.status.config(text="Тень Зеты: ВКЛ" if self.anti_detect else "Тень Зеты: ВЫКЛ")

    def toggle_clone_mode(self):
        self.clone_mode = not self.clone_mode
        color = self.success_color if self.clone_mode else "#003300"
        self.clone_btn.config(bg=color)
        self.status.config(text=f"Клоны: ВКЛ (x{self.clone_multiplier})" if self.clone_mode else "Клоны: ВЫКЛ")

    def start_clicking(self):
        with self.lock:
            if not self.running:
                self.running = True
                mode = "Тень Зеты" if self.anti_detect else "Обычный"
                self.status.config(text=f"АКТИВНО | {mode} | {self.current_speed} CPS", fg=self.warning_color)
                Thread(target=self.click_loop, daemon=True).start()

    def click_loop(self):
        try:
            delay = 1 / self.current_speed if self.current_speed > 0 else 0
            last_time = time.time()
            spiral_radius = 0

            while self.running:
                x, y = pyautogui.position()
                clicks_to_do = self.clone_multiplier if self.clone_mode else 1

                for _ in range(clicks_to_do):
                    if self.anti_detect:
                        spiral_radius += 0.5
                        offset_x = int(math.sin(spiral_radius) * 10)
                        offset_y = int(math.cos(spiral_radius) * 10)
                        pyautogui.moveTo(x + offset_x, y + offset_y, duration=0.1)

                    pyautogui.click()
                    self.total_clicks += 1
                    self.clicks_label.config(text=f"Кликов: {self.total_clicks}")

                    if self.anti_detect:
                        time.sleep(random.uniform(0.01, 0.05))

                now = time.time()
                elapsed = now - last_time
                if elapsed < delay:
                    time.sleep(delay - elapsed + random.uniform(-0.005, 0.005))
                last_time = now

        except Exception as e:
            self.status.config(text=f"ОШИБКА: {str(e)}", fg=self.error_color)

    def stop_clicking(self):
        with self.lock:
            self.running = False
            self.status.config(text="ОСТАНОВЛЕНО", fg=self.error_color)

    def safe_exit(self):
        self.running = False
        self.window.destroy()
        sys.exit()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    try:
        app = DiscoClicker()
        app.run()
    except ImportError as e:
        print(f"Ошибка: Не установлены зависимости - {e}")
        print("Установите: pip install pyautogui keyboard")
    except Exception as e:
        print(f"Критическая ошибка: {e}")