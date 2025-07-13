import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math
from tkinter import font as tkfont

# Конфигурация
BG_COLOR = "#0d0208"  # Фон
TEXT_COLOR = "#00ff41"  # Основной текст
ACCENT_COLOR = "#ff0090"  # Акценты
FONT_NAME = "Courier New"  # Шрифт
EXIT_PASSWORD = "1234"  # Пароль для выхода
LOCK_PASSWORD = "3310"  # Пароль для разблокировки винлокера

class WinLocker:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.attributes("-fullscreen", True)
        self.setup_window()
        self.create_matrix_effect()
        self.create_main_ui()
        self.setup_animations()
        
        # Блокируем родительское окно
        parent.withdraw()

    def setup_window(self):
        self.root.configure(bg=BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
        self.root.bind("<Escape>", self.prevent_close)
        self.root.bind("<Alt-F4>", self.prevent_close)
        self.root.config(cursor="arrow")

    def create_matrix_effect(self):
        """Фон с цифровым дождём"""
        self.matrix_canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.matrix_canvas.pack(fill="both", expand=True)
        
        # Создаём колонки с падающими символами
        self.matrix_columns = []
        cols = self.root.winfo_screenwidth() // 20
        for i in range(cols):
            x = i * 20 + random.randint(-5, 5)
            speed = random.uniform(1, 3)
            length = random.randint(5, 15)
            self.matrix_columns.append({
                'x': x,
                'speed': speed,
                'text_ids': [],
                'positions': [-random.randint(20, 100) for _ in range(length)],
                'chars': [random.choice("01") for _ in range(length)]
            })
        
        self.animate_matrix()

    def animate_matrix(self):
        """Анимация фона"""
        for col in self.matrix_columns:
            for text_id in col['text_ids']:
                self.matrix_canvas.delete(text_id)
            col['text_ids'] = []
            
            for i, (y, char) in enumerate(zip(col['positions'], col['chars'])):
                green = min(255, 50 + int(205 * (i / len(col['positions']))))
                color = f"#00{green:02x}00"
                
                text_id = self.matrix_canvas.create_text(
                    col['x'], y,
                    text=char,
                    fill=color,
                    font=(FONT_NAME, 16),
                    anchor="nw"
                )
                col['text_ids'].append(text_id)
                col['positions'][i] += col['speed']
                
                if col['positions'][i] > self.root.winfo_screenheight():
                    col['positions'][i] = -20
                    col['chars'][i] = random.choice("01")
        
        self.root.after(50, self.animate_matrix)

    def create_main_ui(self):
        """Основной интерфейс"""
        self.main_frame = tk.Frame(self.matrix_canvas, bg=BG_COLOR)
        self.window_id = self.matrix_canvas.create_window(
            self.root.winfo_screenwidth() // 2,
            self.root.winfo_screenheight() // 2,
            window=self.main_frame
        )

        # Заголовок
        self.title_label = tk.Label(
            self.main_frame,
            text="SYSTEM LOCKED",
            font=(FONT_NAME, 42, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.title_label.pack(pady=(40, 20))

        # Иконка
        self.icon_label = tk.Label(
            self.main_frame,
            text="⌾",
            font=(FONT_NAME, 72),
            fg=ACCENT_COLOR,
            bg=BG_COLOR
        )
        self.icon_label.pack(pady=10)

        # Сообщение
        tk.Label(
            self.main_frame,
            text="UNAUTHORIZED ACCESS DETECTED\n\n"
                 "ENTER DECRYPTION KEY TO CONTINUE",
            font=(FONT_NAME, 14),
            fg="#aaaaaa",
            bg=BG_COLOR,
            justify="center"
        ).pack(pady=20)

        # Поле ввода пароля
        self.pass_entry = ttk.Entry(
            self.main_frame,
            font=(FONT_NAME, 18),
            width=15,
            justify="center",
            show="*"
        )
        self.pass_entry.pack(pady=10, ipady=5)

        # Кнопка
        style = ttk.Style()
        style.configure("Cyber.TButton", 
                      foreground="black",
                      background=ACCENT_COLOR,
                      font=(FONT_NAME, 12, "bold"))
        
        ttk.Button(
            self.main_frame,
            text="UNLOCK",
            style="Cyber.TButton",
            command=self.check_password
        ).pack(pady=20)

        # Таймер
        self.timer_label = tk.Label(
            self.main_frame,
            text="",
            font=(FONT_NAME, 14),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.timer_label.pack(pady=(10, 20))
        self.update_timer(300)

    def setup_animations(self):
        """Анимация заголовка"""
        def pulse_title():
            for i in range(0, 100, 5):
                alpha = math.sin(i/100 * math.pi) * 0.3 + 0.7
                color = self.color_with_alpha(TEXT_COLOR, alpha)
                self.title_label.config(fg=color)
                self.root.update()
                time.sleep(0.03)
            self.root.after(100, pulse_title)
        
        pulse_title()

    def color_with_alpha(self, color, alpha):
        """Создаёт цвет с прозрачностью"""
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_timer(self, seconds):
        """Таймер обратного отсчёта"""
        if seconds > 0:
            mins, secs = divmod(seconds, 60)
            self.timer_label.config(
                text=f"TIME REMAINING: {mins:02d}:{secs:02d}"
            )
            self.root.after(1000, lambda: self.update_timer(seconds - 1))
        else:
            self.timer_label.config(text="SYSTEM PERMANENTLY LOCKED")

    def check_password(self):
        """Проверка пароля"""
        if self.pass_entry.get() == LOCK_PASSWORD:
            messagebox.showinfo(
                "ACCESS GRANTED",
                "SYSTEM UNLOCKED\n\n"
                "This was a cybersecurity demonstration!",
                parent=self.root
            )
            self.root.destroy()
            self.parent.deiconify()  # Восстанавливаем родительское окно
        else:
            messagebox.showerror(
                "ACCESS DENIED",
                "INCORRECT PASSWORD",
                parent=self.root
            )
            self.pass_entry.delete(0, tk.END)

    def prevent_close(self, event=None):
        """Блокировка закрытия"""
        return "break"

class CheatMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_matrix_effect()
        self.create_main_ui()
        self.setup_animations()
        self.root.mainloop()

    def setup_window(self):
        # Установка размеров окна (800x600)
        self.root.geometry("800x600")
        self.root.title("Cheat fortnite v1.37")
        self.root.configure(bg=BG_COLOR)
        
        # Блокировка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
        self.root.bind("<Alt-F4>", self.prevent_close)
        
        # Центрирование окна
        self.center_window()
        self.root.config(cursor="arrow")

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def prevent_close(self, event=None):
        """Блокировка закрытия окна"""
        return "break"

    def create_matrix_effect(self):
        """Фон с цифровым дождём"""
        self.matrix_canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.matrix_canvas.pack(fill="both", expand=True)
        
        # Создаём колонки с падающими символами
        self.matrix_columns = []
        cols = 40  # Фиксированное количество колонок для окна 800x600
        for i in range(cols):
            x = i * 20 + random.randint(-5, 5)
            speed = random.uniform(1, 3)
            length = random.randint(5, 15)
            self.matrix_columns.append({
                'x': x,
                'speed': speed,
                'text_ids': [],
                'positions': [-random.randint(20, 100) for _ in range(length)],
                'chars': [random.choice("01") for _ in range(length)]
            })
        
        self.animate_matrix()

    def animate_matrix(self):
        """Анимация фона"""
        for col in self.matrix_columns:
            for text_id in col['text_ids']:
                self.matrix_canvas.delete(text_id)
            col['text_ids'] = []
            
            for i, (y, char) in enumerate(zip(col['positions'], col['chars'])):
                green = min(255, 50 + int(205 * (i / len(col['positions']))))
                color = f"#00{green:02x}00"
                
                text_id = self.matrix_canvas.create_text(
                    col['x'], y,
                    text=char,
                    fill=color,
                    font=(FONT_NAME, 16),
                    anchor="nw"
                )
                col['text_ids'].append(text_id)
                col['positions'][i] += col['speed']
                
                # Используем высоту окна вместо высоты экрана
                if col['positions'][i] > self.root.winfo_height():
                    col['positions'][i] = -20
                    col['chars'][i] = random.choice("01")
        
        self.root.after(50, self.animate_matrix)

    def create_main_ui(self):
        """Основной интерфейс читов"""
        self.main_frame = tk.Frame(self.matrix_canvas, bg=BG_COLOR)
        self.window_id = self.matrix_canvas.create_window(
            self.root.winfo_width() // 2,
            self.root.winfo_height() // 2,
            window=self.main_frame
        )

        # Заголовок
        self.title_label = tk.Label(
            self.main_frame,
            text="CHEAT FORTNITE v1.37",
            font=(FONT_NAME, 36, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.title_label.pack(pady=(20, 10))

        # Иконка
        self.icon_label = tk.Label(
            self.main_frame,
            text="⚡",
            font=(FONT_NAME, 48),
            fg=ACCENT_COLOR,
            bg=BG_COLOR
        )
        self.icon_label.pack(pady=5)

        # Разделитель
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)

        # Контейнер для кнопок
        button_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        button_frame.pack(pady=10, padx=20)

        # Стиль для кнопок
        style = ttk.Style()
        style.configure("Cheat.TButton", 
                      foreground="black",
                      background=ACCENT_COLOR,
                      font=(FONT_NAME, 12, "bold"),
                      padding=10)

        # Кнопки читов - все запускают винлокер
        cheats = [
            ("INFINITE HEALTH", self.launch_winlocker),
            ("UNLIMITED AMMO", self.launch_winlocker),
            ("ONE HIT KILL", self.launch_winlocker),
            ("NO CLIP MODE", self.launch_winlocker),
            ("SUPER SPEED", self.launch_winlocker)
        ]

        for text, command in cheats:
            btn = ttk.Button(
                button_frame,
                text=text,
                style="Cheat.TButton",
                command=command
            )
            btn.pack(fill='x', pady=5, ipady=5)

        # Кнопка выхода (с защитой паролем)
        ttk.Button(
            button_frame,
            text="выйти",
            style="Cheat.TButton",
            command=self.secure_exit
        ).pack(fill='x', pady=(15, 5), ipady=5)

        # Статус бар
        self.status_var = tk.StringVar(value="статус: готов [System Secured]")
        status_bar = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            font=(FONT_NAME, 10),
            fg="#aaaaaa",
            bg=BG_COLOR,
            anchor='w'
        )
        status_bar.pack(fill='x', padx=20, pady=(10, 5))

    def setup_animations(self):
        """Анимация заголовка"""
        def pulse_title():
            for i in range(0, 100, 5):
                alpha = math.sin(i/100 * math.pi) * 0.3 + 0.7
                color = self.color_with_alpha(TEXT_COLOR, alpha)
                self.title_label.config(fg=color)
                self.root.update()
                time.sleep(0.03)
            self.root.after(100, pulse_title)
        
        pulse_title()

    def color_with_alpha(self, color, alpha):
        """Создаёт цвет с прозрачностью"""
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f"#{r:02x}{g:02x}{b:02x}"

    def launch_winlocker(self):
        """Запускает встроенный винлокер"""
        self.status_var.set("Status: WinLocker activated")
        WinLocker(self.root)  # Передаем родительское окно
        self.root.withdraw()  # Скрываем текущее окно

    def show_cheat_alert(self, message):
        """Показывает сообщение об активации чита"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Cheat Activated")
        alert_window.configure(bg=BG_COLOR)
        alert_window.attributes("-topmost", True)
        alert_window.geometry("400x150")
        alert_window.resizable(False, False)
        
        # Центрирование окна
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 150) // 2
        alert_window.geometry(f"400x150+{x}+{y}")
        
        # Блокировка закрытия
        alert_window.protocol("WM_DELETE_WINDOW", lambda: None)
        alert_window.bind("<Alt-F4>", lambda e: None)
        
        # Содержимое окна
        tk.Label(
            alert_window,
            text="✓ SUCCESS",
            font=(FONT_NAME, 18, "bold"),
            fg="#00ff00",
            bg=BG_COLOR
        ).pack(pady=(20, 5))
        
        tk.Label(
            alert_window,
            text=message,
            font=(FONT_NAME, 12),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=5)
        
        ttk.Button(
            alert_window,
            text="ACKNOWLEDGE",
            command=alert_window.destroy,
            style="Cheat.TButton"
        ).pack(pady=15)

    def secure_exit(self):
        """Защищенный выход с проверкой пароля"""
        password = self.get_password_input("SECURE EXIT PROTOCOL", "Enter security clearance code:")
        if password == EXIT_PASSWORD:
            self.root.destroy()
        elif password is not None:  # None означает отмену ввода
            messagebox.showerror(
                "ACCESS DENIED",
                "Invalid security clearance!\n\n"
                "This attempt has been logged.",
                parent=self.root
            )

    def get_password_input(self, title, prompt):
        """Создает защищенное окно ввода пароля"""
        pw_window = tk.Toplevel(self.root)
        pw_window.title(title)
        pw_window.configure(bg=BG_COLOR)
        pw_window.geometry("400x200")
        pw_window.resizable(False, False)
        pw_window.attributes("-topmost", True)
        
        # Центрирование
        pw_window.update_idletasks()
        width = pw_window.winfo_width()
        height = pw_window.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        pw_window.geometry(f"400x200+{x}+{y}")
        
        # Блокировка закрытия
        pw_window.protocol("WM_DELETE_WINDOW", lambda: None)
        pw_window.bind("<Alt-F4>", lambda e: None)
        
        # Содержимое окна
        tk.Label(
            pw_window,
            text=prompt,
            font=(FONT_NAME, 12),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=(20, 10))
        
        password_var = tk.StringVar()
        entry = ttk.Entry(
            pw_window,
            font=(FONT_NAME, 14),
            show="*",
            textvariable=password_var,
            width=20
        )
        entry.pack(pady=10, ipady=5)
        entry.focus_set()
        
        btn_frame = tk.Frame(pw_window, bg=BG_COLOR)
        btn_frame.pack(pady=10)
        
        result = [None]  # Используем список для хранения результата
        
        def submit():
            result[0] = password_var.get()
            pw_window.destroy()
        
        def cancel():
            pw_window.destroy()
        
        ttk.Button(
            btn_frame,
            text="SUBMIT",
            style="Cheat.TButton",
            command=submit
        ).pack(side="left", padx=10)
        
        ttk.Button(
            btn_frame,
            text="CANCEL",
            style="Cheat.TButton",
            command=cancel
        ).pack(side="right", padx=10)
        
        # Ожидание закрытия окна
        pw_window.wait_window()
        return result[0]

if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    app = CheatMenu()