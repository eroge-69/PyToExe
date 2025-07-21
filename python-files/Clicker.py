import tkinter as tk
from tkinter import ttk, scrolledtext

class HoverButton(ttk.Button):
    def __init__(self, master=None, **kw):
        self.style_name = kw.pop('style', 'TButton')
        super().__init__(master=master, style=self.style_name, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress>", self.on_press)
        self.bind("<ButtonRelease>", self.on_release)

    def on_enter(self, e):
        style = ttk.Style()
        if self.style_name == 'Red.TButton':
            style.configure(self.style_name, background="#ee6666", foreground="white")
        else:
            style.configure(self.style_name, background="#555555", foreground="#eeeeee")

    def on_leave(self, e):
        style = ttk.Style()
        if self.style_name == 'Red.TButton':
            style.configure(self.style_name, background="#ff4444", foreground="white")
        else:
            style.configure(self.style_name, background="#2a2a2a", foreground="white")

    def on_press(self, e):
        style = ttk.Style()
        if self.style_name == 'Red.TButton':
            style.configure(self.style_name, background="#cc3333", foreground="white")
        else:
            style.configure(self.style_name, background="#444444", foreground="white")

    def on_release(self, e):
        style = ttk.Style()
        if self.style_name == 'Red.TButton':
            style.configure(self.style_name, background="#ee6666", foreground="white")
        else:
            style.configure(self.style_name, background="#555555", foreground="#eeeeee")

class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("42 CLIENT")
        self.geometry("760x560")
        self.resizable(False, False)

        self.theme = "dark"
        self.dark_bg = "#2a2a2a"
        self.dark_fg = "white"
        self.configure(bg=self.dark_bg)

        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        self.settings_visible = False
        self.create_widgets()
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('Red.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        background="#ff4444",
                        foreground='white',
                        borderwidth=0,
                        focusthickness=0,
                        padding=6)
        style.map('Red.TButton',
                  background=[('pressed', '#bb0000')],
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])

        style.configure('TButton',
                        font=('Segoe UI', 10),
                        background=self.dark_bg,
                        foreground=self.dark_fg,
                        borderwidth=0,
                        focusthickness=0,
                        padding=6)
        style.map('TButton',
                  background=[('pressed', '#222222')],
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])

        style.configure('TLabel', font=('Segoe UI', 10), background=self.dark_bg, foreground=self.dark_fg)
        style.configure('TCheckbutton', font=('Segoe UI', 10), background=self.dark_bg, foreground=self.dark_fg)
        style.configure('Red.TLabelframe.Label', foreground="#ff4444", font=('Segoe UI', 10, 'bold'))
        style.configure('Red.TLabelframe', background=self.dark_bg, borderwidth=2)

    def create_widgets(self):
        # Основное меню
        self.title_label = tk.Label(self, text="42 CLIENT", font=("Segoe UI", 20, "bold"), fg="#ff4444", bg=self.dark_bg)
        self.title_label.place(x=20, y=10)

        ttk.Label(self, text="Профиль:", background=self.dark_bg, foreground=self.dark_fg).place(x=20, y=50)
        self.profile_cb = ttk.Combobox(self, values=["FlugerNew", "Bro9I", "Custom..."], state="readonly")
        self.profile_cb.current(0)
        self.profile_cb.place(x=90, y=50, width=150)
        self.profile_cb.bind("<<ComboboxSelected>>", self.profile_changed)

        self.custom_nick_entry = ttk.Entry(self)
        self.custom_nick_entry.place(x=250, y=50, width=150)
        self.custom_nick_entry.insert(0, "Введите ник")
        self.custom_nick_entry.configure(state="disabled")

        self.version_label = ttk.Label(self, text="Версия:", background=self.dark_bg, foreground=self.dark_fg)
        self.version_label.place(x=420, y=50)

        self.version_cb = ttk.Combobox(self, values=["1.20.4", "1.19.2", "1.18.1", "1.16.5"], state="readonly")
        self.version_cb.current(0)
        self.version_cb.place(x=480, y=50, width=120)

        self.btn_launch = HoverButton(self, text="Запуск", style="Red.TButton", command=self.fake_launch)
        self.btn_launch.place(x=620, y=48, width=100)

        self.btn_settings = HoverButton(self, text="⚙ Настройки", style="TButton", command=self.toggle_settings)
        self.btn_settings.place(x=630, y=10)

        self.btn_theme = HoverButton(self, text="Сменить тему", style="TButton", command=self.switch_theme)
        self.btn_theme.place(x=520, y=10)

        self.sidebar = ttk.LabelFrame(self, text="Дополнения", style="Red.TLabelframe")
        self.sidebar.place(x=20, y=90, width=220, height=220)

        self.mods = {}
        for mod in ["Optifine", "Shaders", "Resource Pack", "Custom UI"]:
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(self.sidebar, text=mod, variable=var)
            chk.pack(anchor='w', padx=5, pady=2)
            self.mods[mod] = var

        self.log_box = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD,
                                                 bg="#1c1c1c", fg="white", insertbackground="white")
        self.log_box.place(x=260, y=100, width=470, height=180)
        self.log_box.insert(tk.END, "Добро пожаловать в 42 CLIENT!\n")
        self.log_box.configure(state='disabled')

        self.updates_frame = ttk.LabelFrame(self, text="Обновления чита", style="Red.TLabelframe")
        self.updates_frame.place(x=20, y=320, width=710, height=120)

        self.update_text = scrolledtext.ScrolledText(self.updates_frame, wrap=tk.WORD,
                                                     bg="#1c1c1c", fg="white", insertbackground="white")
        self.update_text.pack(expand=True, fill='both', padx=5, pady=5)
        self.update_text.insert(tk.END, "\n".join([
            "• [+] AutoClicker теперь обходит проверки Hypixel",
            "• [+] ESP поддерживает кастомные цвета",
            "• [+] FreeCam стал плавнее",
            "• [!] Фикс вылета на 1.16.5 с X-Ray",
            "• [+] KillAura Smart Mode добавлен",
            "• [+] [FunTime] FakeLeave теперь с задержкой",
            "• [+] [ReallyWorld] PacketFly стабилизирован",
            "• [+] [ReallyWorld] SmartBot — автоответчик на чате",
            "• [+] [FunTime] Быстрый Teleport к игрокам",
            "• [+] Velocity Bypass v2",
            "• [+] TimerHack обновлён",
            "• [+] AutoTotem улучшен",
            "• [+] AutoArmor с приоритетами",
            "• [+] AimAssist на основе Raycast",
            "• [+] NoFall для ReallyWorld",
            "• [+] Blink работает через фейковые чанки"
        ]))
        self.update_text.config(state='disabled')

        # Сохраним список всех основных виджетов для удобного скрытия/показа
        self.main_widgets = [
            self.title_label,
            self.profile_cb,
            self.custom_nick_entry,
            self.version_label,
            self.version_cb,
            self.btn_launch,
            self.btn_settings,
            self.btn_theme,
            self.sidebar,
            self.log_box,
            self.updates_frame
        ]

    def toggle_settings(self):
        if not self.settings_visible:
            # Скрываем все виджеты основного меню
            for w in self.main_widgets:
                w.place_forget()

            # Заголовок настроек лаунчера, размещён ниже чтобы полностью был виден
            self.settings_title = tk.Label(self, text="Настройки лаунчера", font=("Segoe UI", 18, "bold"), fg="#ff4444", bg=self["bg"])
            self.settings_title.place(x=20, y=10, width=300, height=40)

            # Заголовок настроек чита чуть ниже
            self.cheat_title = tk.Label(self, text="Настройки чита", font=("Segoe UI", 14, "bold"), fg="#ff4444", bg=self["bg"])
            self.cheat_title.place(x=20, y=60)

            # Кнопка закрытия настроек
            self.btn_close_settings = HoverButton(self, text="Закрыть настройки", style="Red.TButton", command=self.toggle_settings)
            self.btn_close_settings.place(x=620, y=10, width=120, height=30)

            # Создаем 42 настройки с названиями чит-функций
            cheat_functions = [
                "KillAura", "AutoClicker", "X-Ray", "ESP", "Fly", "NoFall", "SpeedHack", "Timer",
                "AutoTotem", "AutoArmor", "Scaffold", "FastPlace", "AimAssist", "Blink", "FreeCam",
                "ChestESP", "Tracers", "Velocity", "FastBreak", "FastEat", "FastBow", "Step", "Criticals",
                "NoSlow", "FastSwim", "AutoMine", "Sneak", "AntiAFK", "FastDrop", "AntiKnockback",
                "AutoFish", "FastSprint", "AutoSprint", "FastSwitch", "FastReload", "NoFallDamage",
                "SilentAim", "AntiBot", "AutoPotion", "AutoBuild", "SafeWalk"
            ]
            self.cheat_vars = []
            self.cheat_checkbuttons = []

            start_x = 20
            start_y = 100
            col_count = 3
            btn_width = 230
            btn_height = 25
            padding_x = 10
            padding_y = 5

            for i, name in enumerate(cheat_functions):
                var = tk.BooleanVar(value=False)
                x = start_x + (i % col_count) * (btn_width + padding_x)
                y = start_y + (i // col_count) * (btn_height + padding_y)
                chk = ttk.Checkbutton(self, text=name, variable=var)
                chk.place(x=x, y=y, width=btn_width, height=btn_height)
                self.cheat_vars.append(var)
                self.cheat_checkbuttons.append(chk)

            self.settings_visible = True
        else:
            # Скрываем настройки
            self.settings_title.destroy()
            self.cheat_title.destroy()
            self.btn_close_settings.destroy()
            for chk in self.cheat_checkbuttons:
                chk.destroy()

            # Показываем основной интерфейс заново
            self.title_label.place(x=20, y=10)
            ttk.Label(self, text="Профиль:", background=self.dark_bg, foreground=self.dark_fg).place(x=20, y=50)
            self.profile_cb.place(x=90, y=50, width=150)
            self.custom_nick_entry.place(x=250, y=50, width=150)
            self.version_label.place(x=420, y=50)
            self.version_cb.place(x=480, y=50, width=120)
            self.btn_launch.place(x=620, y=48, width=100)
            self.btn_settings.place(x=630, y=10)
            self.btn_theme.place(x=520, y=10)
            self.sidebar.place(x=20, y=90, width=220, height=220)
            self.log_box.place(x=260, y=100, width=470, height=180)
            self.updates_frame.place(x=20, y=320, width=710, height=120)

            self.settings_visible = False

    def profile_changed(self, event):
        if self.profile_cb.get() == "Custom...":
            self.custom_nick_entry.configure(state="normal")
            self.custom_nick_entry.delete(0, tk.END)
        else:
            self.custom_nick_entry.configure(state="disabled")
            self.custom_nick_entry.delete(0, tk.END)

    def switch_theme(self):
        # Простая смена цвета фона и текста (для примера)
        if self.theme == "dark":
            self.theme = "light"
            self.dark_bg = "white"
            self.dark_fg = "black"
        else:
            self.theme = "dark"
            self.dark_bg = "#2a2a2a"
            self.dark_fg = "white"
        self.configure(bg=self.dark_bg)
        for w in self.main_widgets:
            try:
                w.configure(background=self.dark_bg, foreground=self.dark_fg)
            except:
                pass
        self.title_label.configure(bg=self.dark_bg, fg="#ff4444")
        self.version_label.configure(background=self.dark_bg, foreground=self.dark_fg)
        self.log_box.configure(bg="#1c1c1c" if self.theme == "dark" else "white",
                               fg="white" if self.theme == "dark" else "black",
                               insertbackground="white" if self.theme == "dark" else "black")

    def fake_launch(self):
        self.log_box.configure(state='normal')
        self.log_box.insert(tk.END, "Запуск клиента...\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state='disabled')

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()














