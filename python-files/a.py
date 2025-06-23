import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import time
import threading
import pygame
from pygame import mixer

# Инициализация звуковой системы
pygame.init()
mixer.init()

class XONECrackPremium:
    def __init__(self, root):
        self.root = root
        self.root.title("XONE CRACK PREMIUM | CS2 ЧИТ")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a12")

        # Загрузка звуков
        try:
            self.click_sound = mixer.Sound("click.wav")
            self.success_sound = mixer.Sound("success.wav")
            self.error_sound = mixer.Sound("error.wav")
        except:
            self.click_sound = None
            self.success_sound = None
            self.error_sound = None

        self.show_welcome_screen()

    def play_sound(self, sound):
        if sound and mixer.get_init():
            sound.play()

    def create_back_button(self, window):
        btn_frame = tk.Frame(window, bg="#0a0a12")
        btn_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)
        
        btn = tk.Button(
            btn_frame,
            text="НАЗАД",
            font=("Segoe UI", 10, "bold"),
            bg="#ff5555",
            fg="#ffffff",
            activebackground="#ff0000",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            command=lambda: self.close_window(window),
            padx=15,
            pady=5,
            width=10
        )
        btn.pack(pady=5)
        btn.bind("<Enter>", lambda e: btn.config(bg="#ff0000"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#ff5555"))
        return btn

    def show_welcome_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#0a0a12")
        self.fade_in()

        self.welcome_frame = tk.Frame(self.root, bg="#0a0a12")
        self.welcome_frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.welcome_label = tk.Label(
            self.welcome_frame,
            text="XONE CRACK",
            font=("Consolas", 28, "bold"),
            fg="#00f0ff",
            bg="#0a0a12"
        )
        self.welcome_label.pack(pady=(10, 20))

        self.login_frame = tk.Frame(self.welcome_frame, bg="#0a0a12")
        self.login_frame.pack(pady=5)
        
        tk.Label(
            self.login_frame,
            text="Логин:",
            font=("Segoe UI", 10),
            fg="#ffffff",
            bg="#0a0a12"
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.login_entry = tk.Entry(
            self.login_frame,
            font=("Segoe UI", 10),
            bg="#1a1a2a",
            fg="#ffffff",
            insertbackground="#00f0ff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#333344",
            highlightcolor="#00f0ff",
            width=20
        )
        self.login_entry.pack(side=tk.LEFT, ipady=3)

        self.password_frame = tk.Frame(self.welcome_frame, bg="#0a0a12")
        self.password_frame.pack(pady=5)
        
        tk.Label(
            self.password_frame,
            text="Пароль:",
            font=("Segoe UI", 10),
            fg="#ffffff",
            bg="#0a0a12"
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.password_entry = tk.Entry(
            self.password_frame,
            font=("Segoe UI", 10),
            bg="#1a1a2a",
            fg="#ffffff",
            insertbackground="#00f0ff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#333344",
            highlightcolor="#00f0ff",
            width=20,
            show="*"
        )
        self.password_entry.pack(side=tk.LEFT, ipady=3)

        self.login_button = tk.Button(
            self.welcome_frame,
            text="ВОЙТИ",
            font=("Segoe UI", 12, "bold"),
            bg="#1a1a2a",
            fg="#00f0ff",
            activebackground="#00a0b0",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            command=self.check_credentials,
            padx=20,
            pady=5,
            width=15
        )
        self.login_button.pack(pady=20)

        tk.Label(
            self.welcome_frame,
            text="Логин: nedohackers | Пароль: nedohackerslite",
            font=("Segoe UI", 8),
            fg="#555555",
            bg="#0a0a12"
        ).pack()

        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg="#00a0b0", fg="#0a0a12"))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg="#1a1a2a", fg="#00f0ff"))

    def check_credentials(self):
        self.play_sound(self.click_sound)
        
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if login == "nedohackers" and password == "nedohackerslite":
            self.play_sound(self.success_sound)
            self.fade_out(self.init_main_interface)
        else:
            self.play_sound(self.error_sound)
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
            self.shake_window()

    def shake_window(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        for _ in range(3):
            for dx, dy in [(5,0), (-5,0), (5,5), (-5,-5)]:
                self.root.geometry(f"+{x+dx}+{y+dy}")
                self.root.update()
                time.sleep(0.02)
        self.root.geometry(f"+{x}+{y}")

    def fade_in(self):
        alpha = 0.0
        self.root.attributes('-alpha', alpha)
        for i in range(1, 11):
            alpha = i / 10
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(0.02)

    def fade_out(self, callback):
        alpha = 1.0
        for i in range(1, 11):
            alpha = 1.0 - i / 10
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(0.02)
        callback()
        self.root.attributes('-alpha', 1.0)

    def init_main_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.set_styles()

        self.main_frame = tk.Frame(self.root, bg="#0a0a12", padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")

        self.logo_frame = tk.Frame(self.main_frame, bg="#0a0a12")
        self.logo_frame.pack(pady=(0, 10))
        
        self.logo_label = tk.Label(
            self.logo_frame,
            text="XONE CRACK",
            font=("Consolas", 24, "bold"),
            fg="#00f0ff",
            bg="#0a0a12"
        )
        self.logo_label.pack()
        
        self.logo_underline = tk.Frame(
            self.logo_frame, 
            height=2, 
            bg="#00f0ff",
            bd=0
        )
        self.logo_underline.pack(fill="x", padx=50)

        self.nickname_frame = tk.Frame(self.main_frame, bg="#0a0a12", pady=10)
        self.nickname_frame.pack()
        
        self.nickname_label = tk.Label(
            self.nickname_frame,
            text="Ваш ник:",
            font=("Segoe UI", 10),
            fg="#ffffff",
            bg="#0a0a12"
        )
        self.nickname_label.pack(side=tk.LEFT, padx=(0, 5))

        self.nickname_entry = tk.Entry(
            self.nickname_frame,
            font=("Segoe UI", 10),
            bg="#1a1a2a",
            fg="#ffffff",
            insertbackground="#00f0ff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#333344",
            highlightcolor="#00f0ff",
            width=20
        )
        self.nickname_entry.pack(side=tk.LEFT, ipady=3)

        self.inject_button = tk.Button(
            self.main_frame,
            text="ИНЖЕКТ",
            font=("Segoe UI", 12, "bold"),
            bg="#1a1a2a",
            fg="#00f0ff",
            activebackground="#00a0b0",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            command=self.start_inject,
            padx=20,
            pady=5,
            width=15
        )
        self.inject_button.pack(pady=10)

        self.progress_frame = tk.Frame(self.main_frame, bg="#0a0a12")
        self.progress_frame.pack(pady=5, fill="x", padx=30)
        
        self.progress_style = ttk.Style()
        self.progress_style.theme_use("clam")
        self.progress_style.configure(
            "neon.Horizontal.TProgressbar",
            background="#00f0ff",
            troughcolor="#1a1a2a",
            bordercolor="#0a0a12",
            lightcolor="#00f0ff",
            darkcolor="#00a0b0",
            thickness=10
        )

        self.progress = ttk.Progressbar(
            self.progress_frame,
            style="neon.Horizontal.TProgressbar",
            orient="horizontal",
            length=250,
            mode="determinate"
        )
        self.progress.pack(side=tk.LEFT, expand=True)

        self.progress_label = tk.Label(
            self.progress_frame,
            text="0%",
            font=("Segoe UI", 10),
            fg="#ffffff",
            bg="#0a0a12",
            width=4
        )
        self.progress_label.pack(side=tk.LEFT, padx=5)
        self.progress_frame.pack_forget()

        self.play_button = tk.Button(
            self.main_frame,
            text="ИГРАТЬ",
            font=("Segoe UI", 12, "bold"),
            bg="#1a1a2a",
            fg="#00f0ff",
            activebackground="#00a0b0",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            command=self.launch_game,
            padx=20,
            pady=5,
            width=15
        )
        self.play_button.pack(pady=5)
        self.play_button.pack_forget()

        # Нижняя панель с центрированными кнопками
        self.bottom_frame = tk.Frame(self.main_frame, bg="#0a0a12", pady=10)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x")

        # Центрирующий фрейм
        self.center_buttons_frame = tk.Frame(self.bottom_frame, bg="#0a0a12")
        self.center_buttons_frame.pack()

        button_width = 12
        button_padx = 5

        self.functions_button = tk.Button(
            self.center_buttons_frame,
            text="ФУНКЦИИ",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a2a",
            fg="#00ff88",
            activebackground="#00a058",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            command=lambda: self.show_window(self.show_functions),
            padx=10,
            pady=3,
            width=button_width
        )
        self.functions_button.pack(side=tk.LEFT, padx=button_padx)

        self.settings_button = tk.Button(
            self.center_buttons_frame,
            text="НАСТРОЙКИ",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a2a",
            fg="#ffffff",
            activebackground="#00a0b0",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            command=lambda: self.show_window(self.show_settings),
            padx=10,
            pady=3,
            width=button_width
        )
        self.settings_button.pack(side=tk.LEFT, padx=button_padx)

        self.help_button = tk.Button(
            self.center_buttons_frame,
            text="ПОМОЩЬ",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a2a",
            fg="#ff5555",
            activebackground="#ff0000",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            command=lambda: self.show_window(self.show_support),
            padx=10,
            pady=3,
            width=button_width
        )
        self.help_button.pack(side=tk.LEFT, padx=button_padx)

        self.setup_hover_effects()

    def set_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TCombobox",
            fieldbackground="#1a1a2a",
            background="#1a1a2a",
            foreground="#ffffff",
            selectbackground="#00f0ff",
            selectforeground="#0a0a12",
            relief="flat",
            bordercolor="#333344",
            arrowcolor="#00f0ff",
            arrowsize=10,
            padding=5
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", "#1a1a2a")],
            selectbackground=[("readonly", "#00f0ff")],
            selectforeground=[("readonly", "#0a0a12")]
        )

    def setup_hover_effects(self):
        buttons = [
            (self.inject_button, "#00a0b0", "#0a0a12"),
            (self.play_button, "#00a0b0", "#0a0a12"),
            (self.functions_button, "#00a058", "#0a0a12"),
            (self.settings_button, "#00a0b0", "#0a0a12"),
            (self.help_button, "#ff0000", "#ffffff")
        ]

        for button, hover_bg, hover_fg in buttons:
            button.bind("<Enter>", lambda e, b=button, bg=hover_bg, fg=hover_fg: b.config(bg=bg, fg=fg))
            button.bind("<Leave>", lambda e, b=button, bg="#1a1a2a", fg=button.cget("fg"): b.config(bg=bg, fg=fg))

    def show_window(self, window_func):
        self.play_sound(self.click_sound)
        window_func()

    def start_inject(self):
        self.play_sound(self.click_sound)
        
        nickname = self.nickname_entry.get()
        if not nickname:
            self.play_sound(self.error_sound)
            messagebox.showerror("Ошибка", "Введите ваш ник!")
            return

        self.inject_button.config(state=tk.DISABLED)
        self.progress_frame.pack()
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

        threading.Thread(target=self.simulate_network_load).start()
        threading.Thread(target=self.simulate_inject).start()

    def simulate_network_load(self):
        for _ in range(10):
            time.sleep(0.5)
            if hasattr(self, "progress_frame") and self.progress_frame.winfo_ismapped():
                pass

    def simulate_inject(self):
        for i in range(101):
            time.sleep(0.03)
            self.progress["value"] = i
            self.progress_label.config(text=f"{i}%")
            self.root.update_idletasks()

        self.progress_frame.pack_forget()
        self.play_button.pack()
        self.play_sound(self.success_sound)
        messagebox.showinfo("Успех", "Чит успешно внедрен!")

    def launch_game(self):
        self.play_sound(self.click_sound)
        messagebox.showinfo("Запуск", "CS2 запущена с читом!")

    def show_support(self):
        support_window = tk.Toplevel(self.root)
        support_window.title("Поддержка")
        support_window.geometry("400x350")
        support_window.resizable(False, False)
        support_window.configure(bg="#0a0a12")

        self.animate_window(support_window)
        self.create_back_button(support_window)

        tk.Label(
            support_window,
            text="ПОДДЕРЖКА",
            font=("Consolas", 20, "bold"),
            fg="#ff5555",
            bg="#0a0a12",
            pady=20
        ).pack()

        contact_frame = tk.Frame(support_window, bg="#0a0a12", padx=20, pady=10)
        contact_frame.pack(fill="both", expand=True)

        contacts = [
            ("Telegram:", "@xone_support"),
            ("Email:", "support@xonecrack.com")
        ]

        for label, text in contacts:
            frame = tk.Frame(contact_frame, bg="#0a0a12")
            frame.pack(anchor="w", pady=5)

            tk.Label(
                frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                fg="#ffffff",
                bg="#0a0a12",
                width=10
            ).pack(side=tk.LEFT)

            tk.Label(
                frame,
                text=text,
                font=("Segoe UI", 10),
                fg="#00f0ff",
                bg="#0a0a12"
            ).pack(side=tk.LEFT)

    def show_functions(self):
        functions_window = tk.Toplevel(self.root)
        functions_window.title("Функции")
        functions_window.geometry("450x500")
        functions_window.resizable(False, False)
        functions_window.configure(bg="#0a0a12")

        self.animate_window(functions_window)
        self.create_back_button(functions_window)

        canvas = tk.Canvas(functions_window, bg="#0a0a12", highlightthickness=0)
        scrollbar = ttk.Scrollbar(functions_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0a12")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")

        tk.Label(
            scrollable_frame,
            text="ФУНКЦИИ",
            font=("Consolas", 20, "bold"),
            fg="#00ff88",
            bg="#0a0a12",
            pady=10
        ).pack()

        functions = [
            "Smart Aim",
            "Silent Aim",
            "Triggerbot",
            "ESP Игроков",
            "ESP Оружия",
            "Стены (X-Ray)",
            "No Flash",
            "No Smoke",
            "Bunny Hop",
            "Radar Hack",
            "Skin Changer"
        ]

        for func in functions:
            frame = tk.Frame(scrollable_frame, bg="#0a0a12")
            frame.pack(fill="x", padx=10, pady=2)

            var = tk.IntVar()
            cb = tk.Checkbutton(
                frame,
                text=func,
                font=("Segoe UI", 10),
                fg="#ffffff",
                bg="#0a0a12",
                activebackground="#0a0a12",
                activeforeground="#00ff88",
                selectcolor="#1a1a2a",
                variable=var,
                anchor="w",
                command=lambda: self.play_sound(self.click_sound)
            )
            cb.pack(fill="x")
            cb.var = var

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("450x500")
        settings_window.resizable(False, False)
        settings_window.configure(bg="#0a0a12")

        self.animate_window(settings_window)
        self.create_back_button(settings_window)

        canvas = tk.Canvas(settings_window, bg="#0a0a12", highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0a12")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")

        tk.Label(
            scrollable_frame,
            text="НАСТРОЙКИ",
            font=("Consolas", 20, "bold"),
            fg="#00f0ff",
            bg="#0a0a12",
            pady=10
        ).pack()

        settings = [
            ("ОЗУ (GB):", ["4", "8", "16"], "8"),
            ("FPS:", ["Без лимита", "144", "120", "60"], "Без лимита"),
            ("Графика:", ["Высокая", "Средняя", "Низкая"], "Высокая")
        ]

        for label, options, default in settings:
            frame = tk.Frame(scrollable_frame, bg="#0a0a12")
            frame.pack(fill="x", padx=10, pady=5)

            tk.Label(
                frame,
                text=label,
                font=("Segoe UI", 10),
                fg="#ffffff",
                bg="#0a0a12",
                width=15,
                anchor="w"
            ).pack(side=tk.LEFT)

            combobox = ttk.Combobox(
                frame,
                values=options,
                font=("Segoe UI", 10),
                state="readonly",
                width=15
            )
            combobox.pack(side=tk.LEFT)
            combobox.set(default)
            combobox.bind("<<ComboboxSelected>>", lambda e: self.play_sound(self.click_sound))

        checkboxes = [
            ("Автозапуск", 1),
            ("Скрытый режим", 0),
            ("Уведомления", 1)
        ]

        for text, default in checkboxes:
            frame = tk.Frame(scrollable_frame, bg="#0a0a12")
            frame.pack(fill="x", padx=10, pady=2)

            var = tk.IntVar(value=default)
            cb = tk.Checkbutton(
                frame,
                text=text,
                font=("Segoe UI", 10),
                fg="#ffffff",
                bg="#0a0a12",
                activebackground="#0a0a12",
                activeforeground="#00f0ff",
                selectcolor="#1a1a2a",
                variable=var,
                anchor="w",
                command=lambda: self.play_sound(self.click_sound)
            )
            cb.pack(fill="x")
            cb.var = var

    def animate_window(self, window):
        alpha = 0.0
        window.attributes('-alpha', alpha)
        for i in range(1, 11):
            alpha = i / 10
            window.attributes('-alpha', alpha)
            window.update()
            time.sleep(0.02)

    def close_window(self, window):
        self.play_sound(self.click_sound)
        window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = XONECrackPremium(root)
    root.mainloop()