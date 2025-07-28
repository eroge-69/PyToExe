import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import webbrowser
from datetime import datetime
import shutil
import subprocess
import psutil
from PIL import Image, ImageTk, ImageDraw, ImageFont
from typing import Any
import re
import sys
import ctypes
import tkinter.messagebox as messagebox
import hashlib

DEFAULT_DATA_FILE = "config.json"
CONFIG_FILE = "config.json"
PASSWORD = "maknau80"  # Основной пароль для входа
SECOND_PASSWORD = "526203"  # Дополнительный пароль для входа

def get_code_version():
    """Получает хеш текущего кода для отслеживания изменений"""
    try:
        with open(__file__, 'rb') as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()[:8]  # Первые 8 символов хеша
    except Exception:
        return "unknown"

def show_update_info():
    """Показывает окно с информацией об обновлении"""
    update_window = tk.Toplevel()
    update_window.title("Обновление системы")
    update_window.geometry("500x500")
    update_window.resizable(False, False)
    
    # Центрируем окно
    update_window.update_idletasks()
    x = (update_window.winfo_screenwidth() // 2) - (500// 2)
    y = (update_window.winfo_screenheight() // 2) - (600// 2)
    update_window.geometry(f"500x600+{x}+{y}")
    
    # Загружаем иконку
    try:
        icon_img = tk.PhotoImage(file=resource_path("logo2.png"))
        update_window.iconphoto(False, icon_img)
    except Exception:
        pass
    
    # Основной контейнер
    main_frame = tk.Frame(update_window, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Иконка обновления
    try:
        logo_img = tk.PhotoImage(file=resource_path("logo2.png"))
        logo_img = logo_img.subsample(3, 3)  # Уменьшаем размер
        logo_label = tk.Label(main_frame, image=logo_img, bg="white")
        logo_label.image = logo_img
        logo_label.pack(pady=(0, 20))
    except Exception:
        pass
    
    # Заголовок
    title_label = tk.Label(main_frame, text="AOM обновлен", 
                          font=("Arial", 16, "bold"), bg="white", fg="#0078d7")
    title_label.pack(pady=(0, 15))
    
    # Текст сообщения
    message_text = """Версия программы была обновлена на сервере и автоматически загружена на ваш компьютер.

Новые функции и улучшения:
• Улучшенный интерфейс
• Исправлены ошибки
  -Исправлен полноэкранный режим
  -Исправлены ошибки ввода
  -Исправолены размеры полей ввода запчастей
  -Исправлено отображение лого в чеке заказа
• Добавлены новые возможности
  -Добавлен столбец с мастером
  -Добавлена сортировка по мастеру
  -Добавлена автоматическая проверка обновлений
• Добавлена поддержка новых форматов заказа

Система готова к работе, спасибо за использование AOM!"""
    
    message_label = tk.Label(main_frame, text=message_text, 
                           font=("Arial", 11), bg="white", 
                           justify="left", wraplength=450)
    message_label.pack(pady=(0, 30))
    
    # Кнопка "OK"
    def close_update_window():
        update_window.destroy()
    
    ok_button = ttk.Button(main_frame, text="OK", 
                          command=close_update_window, 
                          style="My.TButton")
    ok_button.pack(pady=10)
    
    # Привязываем Enter к кнопке
    update_window.bind('<Return>', lambda e: close_update_window())
    update_window.focus_set()
    
    # Модальное окно
    update_window.transient()
    update_window.grab_set()
    update_window.wait_window()

class Order:
    def __init__(self, client="", phone="", email="", master="", model="", issue="", work_price="", price="", parts="", comment="", date="", ready=False, warranty=""):
        self.client = client
        self.phone = phone
        self.email = email
        self.master = master
        self.model = model
        self.issue = issue
        self.work_price = work_price
        self.price = price
        self.parts = parts
        self.comment = comment
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M")
        self.ready = ready
        self.warranty = warranty
    
    def to_dict(self):
        return {
            "client": self.client,
            "phone": self.phone,
            "email": self.email,
            "master": self.master,
            "model": self.model,
            "issue": self.issue,
            "work_price": self.work_price,
            "price": self.price,
            "parts": self.parts,
            "comment": self.comment,
            "date": self.date,
            "ready": self.ready,
            "warranty": self.warranty
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            client=data.get("client", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            master=data.get("master", ""),
            model=data.get("model", ""),
            issue=data.get("issue", ""),
            work_price=data.get("work_price", ""),
            price=data.get("price", ""),
            parts=data.get("parts", ""),
            comment=data.get("comment", ""),
            date=data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M")),
            ready=data.get("ready", False),
            warranty=data.get("warranty", "")
        )

class EyeButton(tk.Canvas):
    def __init__(self, parent, command=None, size=30, bg_color="#f0f0f0", fg_color="black"):
        super().__init__(parent, width=size, height=size, bg=bg_color, highlightthickness=0)
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.command = command
        self.size = size
        self.showing = False
        
        self.draw_eye()
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self.config(bg="#e0e0e0"))
        self.bind("<Leave>", lambda e: self.config(bg=self.bg_color))

    def draw_eye(self):
        self.delete("all")
        self.create_oval(5, 5, self.size-5, self.size-5, outline=self.fg_color, width=2)
        
        if self.showing:
            # Глаз открыт
            self.create_oval(self.size//2-3, self.size//2-3, self.size//2+3, self.size//2+3, fill=self.fg_color, outline="")
        else:
            # Глаз закрыт
            self.create_line(5, self.size//2, self.size-5, self.size//2, fill=self.fg_color, width=2)

    def _on_click(self, event):
        self.showing = not self.showing
        self.draw_eye()
        if self.command:
            self.command(self.showing)

class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width=300, height=40, corner_radius=12, bg_color="white", fg_color="black", font=None, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, **kwargs)
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font = font or ("Arial", 18)
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self, bd=0, relief="flat", textvariable=self.entry_var, font=self.font, justify="center", fg=self.fg_color, bg=self.bg_color, show="*")
        self.entry.place(x=corner_radius, y=0, width=width - 2 * corner_radius, height=height)
        self.draw_rounded_rect()
        self.blink_cursor()

    def draw_rounded_rect(self):
        w = int(self["width"])
        h = int(self["height"])
        r = self.corner_radius
        self.delete("rect")
        self.create_arc((0, 0, r * 2, r * 2), start=90, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rect")
        self.create_arc((w - r * 2, 0, w, r * 2), start=0, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rect")
        self.create_arc((0, h - r * 2, r * 2, h), start=180, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rect")
        self.create_arc((w - r * 2, h - r * 2, w, h), start=270, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rect")
        self.create_rectangle((r, 0, w - r, h), fill=self.bg_color, outline=self.bg_color, tags="rect")
        self.create_rectangle((0, r, w, h - r), fill=self.bg_color, outline=self.bg_color, tags="rect")

    def blink_cursor(self):
        if not hasattr(self, "_cursor_on"):
            self._cursor_on = True
        self.entry.configure(insertbackground="black" if self._cursor_on else self.bg_color)
        self._cursor_on = not self._cursor_on
        self.after(600, self.blink_cursor)

    def get(self):
        return self.entry_var.get()

    def set(self, value):
        self.entry_var.set(value)

    def focus(self):
        self.entry.focus_set()

    def show_password(self, show):
        self.entry.config(show="" if show else "*")

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=200, height=40, corner_radius=12, 
                 bg_color="#f0f0f0", fg_color="black", hover_color="#e0e0e0", font=None):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.font = font or ("Arial", 12)
        self.command = command
        self.text_value = text

        self.draw_button(self.bg_color)

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def draw_button(self, color):
        self.delete("all")
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        r = self.corner_radius

        self.create_arc((0, 0, r * 2, r * 2), start=90, extent=90, fill=color, outline=color)
        self.create_arc((w - r * 2, 0, w, r * 2), start=0, extent=90, fill=color, outline=color)
        self.create_arc((0, h - r * 2, r * 2, h), start=180, extent=90, fill=color, outline=color)
        self.create_arc((w - r * 2, h - r * 2, w, h), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle((r, 0, w - r, h), fill=color, outline=color)
        self.create_rectangle((0, r, w, h - r), fill=color, outline=color)

        self.create_text(w // 2, h // 2, text=self.text_value, fill=self.fg_color, font=self.font)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.draw_button(self.hover_color)

    def _on_leave(self, event):
        self.draw_button(self.bg_color)

class LinkLabel(tk.Label):
    def __init__(self, parent, text, url, font=None):
        super().__init__(parent, text=text, fg="blue", cursor="hand2", font=font or ("Arial", 12), bg=parent["bg"])
        self.url = url
        self.bind("<Enter>", lambda e: self.config(fg="purple", underline=1))
        self.bind("<Leave>", lambda e: self.config(fg="blue", underline=0))
        self.bind("<Button-1>", self.open_link)

    def open_link(self, event=None):
        try:
            webbrowser.open(self.url)
        except Exception:
            messagebox.showerror("Ошибка", f"Не удалось открыть ссылку:\n{self.url}")

class AsbestApp(tk.Tk):
    def __init__(self):
        # --- DPI-AWARENESS для Windows ---
        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        super().__init__()
        # --- Автоматическое уменьшение scaling в зависимости от DPI дисплея (Windows) ---
        def get_windows_scaling():
            try:
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                dpi = user32.GetDpiForSystem()
                if dpi <= 96:
                    return self.winfo_fpixels('1i') / 72.0
                else:
                    return 1.0
            except Exception:
                return 1.0
        if sys.platform == "win32":
            self.tk.call('tk', 'scaling', get_windows_scaling())
        self.withdraw()
        self.orders_current = []
        self.orders_done = []
        self.orders_canceled = []
        self.orders_assigned = []  # <--- Новая вкладка
        # Инициализация основных настроек по умолчанию до входа
        self.data_file = DEFAULT_DATA_FILE
        self.backup_bat_path = ""
        self.sort_var_value = "date_desc"
        self.backup_bat_var = None  # Для корректной работы build_settings_ui
        # self.load_config()  # УБРАНО: профильные настройки загружаются после входа
        self.load_data()
        self.title("AOM")
        self.show_splash()
        
        if hasattr(self, 'backup_bat_path') and self.backup_bat_path:
            try:
                bat_dir = os.path.dirname(os.path.abspath(self.backup_bat_path))
                subprocess.Popen([self.backup_bat_path], cwd=bat_dir, shell=True)
            except Exception as e:
                print(f"Ошибка при запуске bat-файла: {e}")

        # В начало класса AsbestApp (после __init__):
        self.current_user = None

    def load_config(self):
        # Инициализируем current_user если его нет
        if not hasattr(self, 'current_user'):
            self.current_user = "maknau80"
        
        config_file = f"config_{self.current_user}.json" if self.current_user else CONFIG_FILE
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.data_file = cfg.get("data_file", DEFAULT_DATA_FILE)
                self.backup_bat_path = cfg.get("backup_bat_path", "")
                self.sort_var_value = cfg.get("sort_var", "date_desc")
                # Загружаем информацию о версии кода
                self.last_code_version = cfg.get("last_code_version", "")
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                self.data_file = DEFAULT_DATA_FILE
                self.backup_bat_path = ""
                self.sort_var_value = "date_desc"
                self.last_code_version = ""
        else:
            self.data_file = DEFAULT_DATA_FILE
            self.backup_bat_path = ""
            self.sort_var_value = "date_desc"
            self.last_code_version = ""
        # Синхронизация sort_var с профилем после загрузки
        if hasattr(self, 'sort_var'):
            self.sort_var.set(self.sort_var_value)
        else:
            self.sort_var = tk.StringVar(value=self.sort_var_value)

    def save_config(self):
        config_file = f"config_{self.current_user}.json" if self.current_user else CONFIG_FILE
        try:
            config = {
                "data_file": self.data_file, 
                "backup_bat_path": self.backup_bat_path, 
                "sort_var": self.sort_var.get() if hasattr(self, 'sort_var') else self.sort_var_value,
                "last_code_version": get_code_version()  # Сохраняем текущую версию кода
            }
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")

    def check_for_updates(self):
        """Проверяет, нужно ли показать окно обновления"""
        current_version = get_code_version()
        if self.last_code_version and self.last_code_version != current_version:
            # Версия изменилась, показываем окно обновления после логотипа
            self.after(2500, lambda: self.show_update_after_splash())
            # Сохраняем новую версию
            self.save_config()
        else:
            # Если обновлений нет, показываем окно входа через 2 секунды
            self.after(2000, lambda: self.show_login(self.splash_window))
    
    def show_update_after_splash(self):
        """Показывает окно обновления после splash screen"""
        show_update_info()
        # После закрытия окна обновления показываем окно входа
        self.show_login(self.splash_window)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.orders_current = self.convert_old_format(data.get("current", []))
                self.orders_done = self.convert_old_format(data.get("done", []))
                self.orders_canceled = self.convert_old_format(data.get("canceled", []))
                self.orders_assigned = self.convert_old_format(data.get("assigned", [])) if "assigned" in data else []
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")
                self.orders_current = []
                self.orders_done = []
                self.orders_canceled = []
                self.orders_assigned = []
        else:
            self.orders_current = []
            self.orders_done = []
            self.orders_canceled = []
            self.orders_assigned = []

    def convert_old_format(self, orders):
        converted = []
        for order in orders:
            if isinstance(order, dict):
                # Если нет поля ready, добавляем False
                if "ready" not in order:
                    order["ready"] = False
                # Если нет поля warranty, добавляем пустую строку
                if "warranty" not in order:
                    order["warranty"] = ""
                converted.append(Order.from_dict(order).to_dict())
            elif isinstance(order, list):
                if len(order) == 7:
                    converted_order = {
                        "client": order[0],
                        "phone": "",
                        "email": "",
                        "master": "",
                        "model": order[1],
                        "issue": "",
                        "warranty": "",
                        "work_price": "",
                        "price": order[2],
                        "parts": order[3],
                        "comment": "",
                        "date": order[4] if len(order) > 4 else datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "ready": False
                    }
                elif len(order) == 9:
                    converted_order = {
                        "client": order[0],
                        "phone": order[1],
                        "email": order[2],
                        "master": order[3],
                        "model": order[4],
                        "issue": order[5],
                        "warranty": "",
                        "work_price": "",
                        "price": order[6],
                        "parts": order[7],
                        "comment": "",
                        "date": order[8] if len(order) > 8 else datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "ready": False
                    }
                else:
                    continue
                converted.append(converted_order)
        return converted

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({
                    "current": self.orders_current, 
                    "done": self.orders_done,
                    "canceled": self.orders_canceled,
                    "assigned": self.orders_assigned
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{e}")

    def center_window(self, window):
        window.update_idletasks()
        w = window.winfo_width()
        h = window.winfo_height()
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        window.geometry(f'{w}x{h}+{x}+{y}')

    def show_splash(self):
        splash = tk.Toplevel(self)
        splash.title("")
        splash.configure(bg='white')
        
        # Сохраняем ссылку на splash window
        self.splash_window = splash
        
        # Загружаем иконку приложения после создания splash окна
        try:
            self.iconphoto(False, tk.PhotoImage(file=resource_path("logo2.png")))
        except Exception as e:
            print(f"Ошибка загрузки иконки logo2.png: {e}")
        
        try:
            logo = tk.PhotoImage(file=resource_path("logo.png"))
            logo = logo.subsample(4)  # subsample принимает только один аргумент
        except Exception as e:
            print(f"Ошибка загрузки logo.png (splash): {e}")
            logo = None
        
        # Настраиваем размер и позицию окна
        if logo:
            w, h = logo.width(), logo.height()
            splash.geometry(f"{w}x{h}")
        else:
            w, h = 300, 150
            splash.geometry(f"{w}x{h}")
        
        splash.overrideredirect(True)
        self.center_window(splash)
        
        if logo:
            logo_label = tk.Label(splash, image=logo, bg='white')
            logo_label.image = logo  # type: ignore[attr-defined]
            logo_label.pack(expand=True)
        else:
            tk.Label(splash, text="Asbest", font=("Arial", 24), bg='white').pack(expand=True)

        # Загружаем конфигурацию для проверки обновлений
        self.load_config()
        
        # Проверяем обновления после показа логотипа
        self.check_for_updates()

    def show_login(self, splash):
        if splash is not None:
            splash.destroy()
        login = tk.Toplevel()
        login.title("Вход")
        login.attributes('-fullscreen', True)
        container = tk.Frame(login)
        container.pack(expand=True)

        try:
            logo = tk.PhotoImage(file=resource_path("logo.png"))
            logo = logo.subsample(4)  # subsample принимает только один аргумент
        except Exception as e:
            print(f"Ошибка загрузки logo.png (login): {e}")
            logo = None
        if logo:
            logo_label = tk.Label(container, image=logo)
            logo_label.image = logo  # type: ignore[attr-defined]
            logo_label.pack(pady=40)

        tk.Label(container, text="Введите пароль:", font=("Arial", 16)).pack(pady=10)

        # --- Центрирование поля пароля и глазика ---
        password_outer = tk.Frame(container)
        password_outer.pack(pady=5, anchor='center')
        password_entry = RoundedEntry(password_outer, width=300, height=40, corner_radius=12, bg_color="white", fg_color="black", font=("Arial", 18))
        password_entry.pack(anchor='center')
        password_entry.focus()
        # --- ЯЗЫК РАСКЛАДКИ ---
        def get_current_layout():
            if sys.platform == "win32":
                user32 = ctypes.WinDLL('user32', use_last_error=True)
                klid = user32.GetKeyboardLayout(0)
                lid = klid & (2**16 - 1)
                if lid == 0x419:
                    return "RU"
                elif lid == 0x409:
                    return "EN"
                else:
                    return hex(lid)
            return "?"
        layout_var = tk.StringVar(value=get_current_layout())
        # Размещаем поверх поля справа
        layout_label = tk.Label(password_outer, textvariable=layout_var, font=("Arial", 12), bg="white", fg="#888", width=4, anchor='e')
        layout_label.place(in_=password_entry, relx=1.0, x=-8, rely=0.5, anchor='e')
        def update_layout(event=None):
            layout_var.set(get_current_layout())
        password_entry.entry.bind('<KeyRelease>', update_layout)
        password_entry.entry.bind('<FocusIn>', update_layout)
        password_entry.entry.bind('<FocusOut>', update_layout)
        # --- КОНЕЦ ЯЗЫКА ---
        show_password = [False]
        def toggle_password():
            show_password[0] = not show_password[0]
            password_entry.entry.config(show='' if show_password[0] else '*')
        # Глазик поверх поля, в левой части
        eye_btn = tk.Button(password_outer, text='👁', font=("Arial", 16), relief='flat', bd=0, command=toggle_password, cursor='hand2', bg="white", activebackground="white", highlightthickness=0)
        eye_btn.place(in_=password_entry, relx=0.0, x=8, rely=0.5, anchor='w')

        def check_password():
            entered = password_entry.get()
            if entered == PASSWORD:
                self.current_user = "maknau80"
            elif entered == SECOND_PASSWORD:
                self.current_user = "Karre_Dagenhard"
            else:
                messagebox.showerror("Ошибка", "Неверный пароль")
                return
            login.destroy()
            self.deiconify()
            self.load_config()  # загрузить настройки профиля
            self.load_data()   # подгрузить заказы и путь к данным
            self.build_ui()    # создать интерфейс и таблицы
            self.reload_trees() # обновить таблицы
            
            messagebox.showinfo(
                "Информация",
                f"Вы вошли в профиль {self.current_user}\nВсе настройки сохраняются автоматически в ваш профиль"
            )
            if self.backup_bat_path:
                try:
                    bat_dir = os.path.dirname(os.path.abspath(self.backup_bat_path))
                    subprocess.Popen([self.backup_bat_path], cwd=bat_dir, shell=True)
                except Exception as e:
                    print(f"Ошибка при запуске bat-файла: {e}")

        style = ttk.Style()
        style.configure("My.TButton", font=("Arial", 14), padding=10)

        btn_enter = ttk.Button(container, text="Войти", style="My.TButton", command=check_password)
        btn_enter.pack(pady=20)

        def quit_app():
            self.quit()
        btn_quit = ttk.Button(container, text="Выйти", style="My.TButton", command=quit_app)
        btn_quit.pack(pady=(0, 20))

        login.bind('<Return>', lambda event: check_password())

    def build_ui(self):
        self.state('zoomed')
        # Синхронизация sort_var с профилем
        if hasattr(self, 'sort_var'):
            self.sort_var.set(self.sort_var_value)
        else:
            self.sort_var = tk.StringVar(value=self.sort_var_value)
        self.sort_var.trace_add('write', lambda *a: self.apply_sorting())
        # self.apply_sorting()  # УБРАНО отсюда, чтобы не было ошибки

        try:
            logo = tk.PhotoImage(file=resource_path("logo.png"))
            w, h = logo.width(), logo.height()
            max_w, max_h = 400, 125
            scale_w = w / max_w if w > max_w else 1
            scale_h = h / max_h if h > max_h else 1
            scale = max(scale_w, scale_h)
            if scale > 1:
                logo = logo.subsample(int(scale))  # subsample принимает только один аргумент
            self.small_logo = logo
        except Exception as e:
            print(f"Ошибка загрузки logo.png (build_ui): {e}")
            self.small_logo = None

        if self.small_logo:
            logo_label = tk.Label(self, image=self.small_logo)
            logo_label.pack(pady=(10, 0))

        self.tab_control = ttk.Notebook(self)
        self.tab_current = ttk.Frame(self.tab_control)
        self.tab_done = ttk.Frame(self.tab_control)
        self.tab_canceled = ttk.Frame(self.tab_control)
        self.tab_assigned = ttk.Frame(self.tab_control)
        self.tab_settings = ttk.Frame(self.tab_control)
        self.tab_sort = ttk.Frame(self.tab_control)
        self.tab_info = ttk.Frame(self.tab_control)

        # Добавляем эмодзи к названиям вкладок
        self.tab_control.add(self.tab_current, text='⭕ Текущие')
        self.tab_control.add(self.tab_done, text='✔️ Выполненные')
        self.tab_control.add(self.tab_canceled, text='❌ Отмененные')
        self.tab_control.add(self.tab_assigned, text='➕ Присвоено')
        self.tab_control.add(self.tab_settings, text='⚙️ Настройки')
        self.tab_control.add(self.tab_sort, text='❗ Сортировка')
        self.tab_control.add(self.tab_info, text='❓ Информация')
        self.tab_control.pack(expand=1, fill="both", pady=10)

        # Создаем фрейм для боковой панели и таблицы
        self.main_frame_current = ttk.Frame(self.tab_current)
        self.main_frame_current.pack(fill="both", expand=True)

        self.main_frame_done = ttk.Frame(self.tab_done)
        self.main_frame_done.pack(fill="both", expand=True)

        self.main_frame_canceled = ttk.Frame(self.tab_canceled)
        self.main_frame_canceled.pack(fill="both", expand=True)

        # Боковая панель для текущих заказов
        self.sidebar_current = ttk.Frame(self.main_frame_current, width=200, style="Sidebar.TFrame")
        self.sidebar_current.pack(side="left", fill="y", padx=5, pady=5)
        self.sidebar_current.pack_propagate(False)
        self.sidebar_label_current = ttk.Label(self.sidebar_current, text="Нет выбранных заказов", style="Sidebar.TLabel")
        self.sidebar_label_current.pack(pady=10)
        self.sidebar_btn_frame_current = ttk.Frame(self.sidebar_current, style="Sidebar.TFrame")
        self.sidebar_btn_frame_current.pack(fill="x", padx=5, pady=5)
        # Кнопки действий
        ttk.Button(self.sidebar_btn_frame_current, text="Открыть", command=self.open_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_current, text="Изменить", command=self.edit_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_current, text="Удалить", command=self.delete_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_current, text="Выполнен", command=self.mark_done, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_current, text="Отменить", command=self.cancel_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_current, text="Присвоить", command=self.assign_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_current, text="Чек", command=self.show_check, style="Sidebar.TButton").pack(fill="x", pady=2)
        # Кнопки 'Добавить' и 'Обновить' в самом низу боковой панели (текущие)
        self.sidebar_btn_frame_current_bottom = ttk.Frame(self.sidebar_current, style="Sidebar.TFrame")
        self.sidebar_btn_frame_current_bottom.pack(side="bottom", fill="x", padx=5, pady=0)
        self.add_button = ttk.Button(self.sidebar_btn_frame_current_bottom, text="➕ Добавить", style="My.TButton", command=self.add_order)
        self.add_button.pack(fill="x", pady=2)
        self.refresh_button = ttk.Button(self.sidebar_btn_frame_current_bottom, text="🔍 Обновить", style="My.TButton", command=self.manual_reload_trees)
        self.refresh_button.pack(fill="x", pady=2)
        # Таблица для текущих заказов
        self.table_frame_current = ttk.Frame(self.main_frame_current, style="Sidebar.TFrame")
        self.table_frame_current.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        cols = ("Клиент", "Мастер", "Модель", "Цена работы", "Стоимость", "Дата", "Статус")
        self.tree_current = ttk.Treeview(
            self.table_frame_current,
            columns=cols,
            show='headings',
            selectmode="browse"
        )
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background="#f0f0f0",
                        fieldbackground="#f0f0f0",
                        bordercolor="#e1e1e1",
                        borderwidth=0,
                        relief="flat",
                        font=('Arial', 12))
        style.configure("Custom.Treeview.Heading",
                        background="#f0f0f0",
                        font=('Arial', 12, 'bold'))
        self.tree_current.configure(style="Custom.Treeview")

        # Убираю столбец #0
        self.tree_current.column('#0', width=0, stretch=False)
        for i, col in enumerate(cols):
            self.tree_current.heading(col, text=col)
            if col == "Дата":
                self.tree_current.column(col, width=150, anchor='center', stretch=True)  # шире
            elif col == "Модель":
                self.tree_current.column(col, width=240, anchor='center', stretch=True)  # шире
            elif col in ("Клиент", "Мастер"):
                self.tree_current.column(col, width=200, anchor='center', stretch=True)
            elif col == "Стоимость":
                self.tree_current.column(col, width=115, anchor='center', stretch=True)
            elif col == "Цена работы":
                self.tree_current.column(col, width=120, anchor='center', stretch=True)
            elif col == "Статус":
                self.tree_current.column(col, width=120, anchor='center', stretch=True)
            else:
                self.tree_current.column(col, width=120, anchor='center', stretch=True)

        self.tree_current.pack(expand=True, fill="both", padx=0, pady=0)

        # Удаляю все Canvas и связанные с ними функции

        # Боковая панель для выполненных заказов
        self.sidebar_done = ttk.Frame(self.main_frame_done, width=200, style="Sidebar.TFrame")
        self.sidebar_done.pack(side="left", fill="y", padx=5, pady=5)
        self.sidebar_done.pack_propagate(False)

        # Без рамки для боковой панели выполненных
        self.sidebar_label_done = ttk.Label(self.sidebar_done, text="Нет выбранных заказов", style="Sidebar.TLabel")
        self.sidebar_label_done.pack(pady=10)

        self.sidebar_btn_frame_done = ttk.Frame(self.sidebar_done, style="Sidebar.TFrame")
        self.sidebar_btn_frame_done.pack(fill="x", padx=5, pady=5)

        ttk.Button(self.sidebar_btn_frame_done, text="Открыть", command=self.open_done_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_done, text="Вернуть", command=self.return_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_done, text="Чек", command=self.show_done_check, style="Sidebar.TButton").pack(fill="x", pady=2)
        # Кнопка 'Обновить' в самом низу боковой панели (выполненные)
        self.sidebar_btn_frame_done_bottom = ttk.Frame(self.sidebar_done, style="Sidebar.TFrame")
        self.sidebar_btn_frame_done_bottom.pack(side="bottom", fill="x", padx=5, pady=0)
        self.refresh_button_done = ttk.Button(self.sidebar_btn_frame_done_bottom, text="🔍 Обновить", style="My.TButton", command=self.manual_reload_trees)
        self.refresh_button_done.pack(fill="x", pady=2)
        # Таблица для выполненных заказов
        self.table_frame_done = ttk.Frame(self.main_frame_done)
        self.table_frame_done.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Без рамки вокруг таблицы выполненных
        self.tree_done = ttk.Treeview(self.table_frame_done, columns=cols, show='headings', selectmode="browse")
        # Убираю столбец #0
        self.tree_done.column('#0', width=0, stretch=False)
        for i, col in enumerate(cols):
            self.tree_done.heading(col, text=col)
            if col == "Дата":
                self.tree_done.column(col, width=150, anchor='center', stretch=True)
            elif col == "Модель":
                self.tree_done.column(col, width=240, anchor='center', stretch=True)
            elif col in ("Клиент", "Мастер"):
                self.tree_done.column(col, width=200, anchor='center', stretch=True)
            elif col == "Стоимость":
                self.tree_done.column(col, width=115, anchor='center', stretch=True)
            elif col == "Цена работы":
                self.tree_done.column(col, width=120, anchor='center', stretch=True)
            elif col == "Неисправность":
                self.tree_done.column(col, width=60, anchor='center', stretch=True)
            elif col == "Статус":
                self.tree_done.column(col, width=120, anchor='center', stretch=True)
            else:
                self.tree_done.column(col, width=120, anchor='center', stretch=True)
        self.tree_done.pack(expand=True, fill="both")

        # Блокировка изменения ширины столбцов (удаление разделителей)
        def block_column_resize_done(event):
            region = self.tree_done.identify_region(event.x, event.y)
            if region == 'separator':
                return 'break'
        self.tree_done.bind('<Button-1>', block_column_resize_done, add='+')

        # Боковая панель для отмененных заказов
        self.sidebar_canceled = ttk.Frame(self.main_frame_canceled, width=200, style="Sidebar.TFrame")
        self.sidebar_canceled.pack(side="left", fill="y", padx=5, pady=5)
        self.sidebar_canceled.pack_propagate(False)

        # Без рамки для боковой панели отменённых
        self.sidebar_label_canceled = ttk.Label(self.sidebar_canceled, text="Нет выбранных заказов", style="Sidebar.TLabel")
        self.sidebar_label_canceled.pack(pady=10)

        self.sidebar_btn_frame_canceled = ttk.Frame(self.sidebar_canceled, style="Sidebar.TFrame")
        self.sidebar_btn_frame_canceled.pack(fill="x", padx=5, pady=5)

        ttk.Button(self.sidebar_btn_frame_canceled, text="Открыть", command=self.open_canceled_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_canceled, text="Вернуть", command=self.return_canceled_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_canceled, text="Чек", command=self.show_canceled_check, style="Sidebar.TButton").pack(fill="x", pady=2)
        # Кнопка 'Обновить' в самом низу боковой панели (отменённые)
        self.sidebar_btn_frame_canceled_bottom = ttk.Frame(self.sidebar_canceled, style="Sidebar.TFrame")
        self.sidebar_btn_frame_canceled_bottom.pack(side="bottom", fill="x", padx=5, pady=0)
        self.refresh_button_canceled = ttk.Button(self.sidebar_btn_frame_canceled_bottom, text="�� Обновить", style="My.TButton", command=self.manual_reload_trees)
        self.refresh_button_canceled.pack(fill="x", pady=2)
        # Таблица для отменённых заказов
        self.table_frame_canceled = ttk.Frame(self.main_frame_canceled)
        self.table_frame_canceled.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Без рамки вокруг таблицы отменённых
        self.tree_canceled = ttk.Treeview(self.table_frame_canceled, columns=cols, show='headings', selectmode="browse")
        # Убираю столбец #0
        self.tree_canceled.column('#0', width=0, stretch=False)
        for i, col in enumerate(cols):
            self.tree_canceled.heading(col, text=col)
            if col == "Дата":
                self.tree_canceled.column(col, width=150, anchor='center', stretch=True)
            elif col == "Модель":
                self.tree_canceled.column(col, width=240, anchor='center', stretch=True)
            elif col in ("Клиент", "Мастер"):
                self.tree_canceled.column(col, width=200, anchor='center', stretch=True)
            elif col == "Стоимость":
                self.tree_canceled.column(col, width=115, anchor='center', stretch=True)
            elif col == "Цена работы":
                self.tree_canceled.column(col, width=120, anchor='center', stretch=True)
            elif col == "Неисправность":
                self.tree_canceled.column(col, width=60, anchor='center', stretch=True)
            elif col == "Статус":
                self.tree_canceled.column(col, width=120, anchor='center', stretch=True)
            else:
                self.tree_canceled.column(col, width=120, anchor='center', stretch=True)
        self.tree_canceled.pack(expand=True, fill="both")

        # Блокировка изменения ширины столбцов (удаление разделителей)
        def block_column_resize_canceled(event):
            region = self.tree_canceled.identify_region(event.x, event.y)
            if region == 'separator':
                return 'break'
        self.tree_canceled.bind('<Button-1>', block_column_resize_canceled, add='+')

        # Боковая панель для присвоенных заказов
        self.main_frame_assigned = ttk.Frame(self.tab_assigned)
        self.main_frame_assigned.pack(fill="both", expand=True)
        self.sidebar_assigned = ttk.Frame(self.main_frame_assigned, width=200, style="Sidebar.TFrame")
        self.sidebar_assigned.pack(side="left", fill="y", padx=5, pady=5)
        self.sidebar_assigned.pack_propagate(False)
        self.sidebar_label_assigned = ttk.Label(self.sidebar_assigned, text="Нет выбранных заказов", style="Sidebar.TLabel")
        self.sidebar_label_assigned.pack(pady=10)
        self.sidebar_btn_frame_assigned = ttk.Frame(self.sidebar_assigned, style="Sidebar.TFrame")
        self.sidebar_btn_frame_assigned.pack(fill="x", padx=5, pady=5)
        ttk.Button(self.sidebar_btn_frame_assigned, text="Открыть", command=self.open_assigned_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_assigned, text="Вернуть", command=self.return_assigned_order, style="Sidebar.TButton").pack(fill="x", pady=2)
        ttk.Button(self.sidebar_btn_frame_assigned, text="Чек", command=self.show_assigned_check, style="Sidebar.TButton").pack(fill="x", pady=2)
        # Кнопка 'Обновить' в самом низу боковой панели (присвоено)
        self.sidebar_btn_frame_assigned_bottom = ttk.Frame(self.sidebar_assigned, style="Sidebar.TFrame")
        self.sidebar_btn_frame_assigned_bottom.pack(side="bottom", fill="x", padx=5, pady=0)
        self.refresh_button_assigned = ttk.Button(self.sidebar_btn_frame_assigned_bottom, text="🔍 Обновить", style="My.TButton", command=self.manual_reload_trees)
        self.refresh_button_assigned.pack(fill="x", pady=2)
        # Таблица для присвоенных заказов
        cols = ("Клиент", "Мастер", "Модель", "Цена работы", "Стоимость", "Дата", "Статус")
        self.table_frame_assigned = ttk.Frame(self.main_frame_assigned)
        self.table_frame_assigned.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.tree_assigned = ttk.Treeview(self.table_frame_assigned, columns=cols, show='headings', selectmode="browse")
        self.tree_assigned.column('#0', width=0, stretch=False)
        for i, col in enumerate(cols):
            self.tree_assigned.heading(col, text=col)
            if col == "Дата":
                self.tree_assigned.column(col, width=150, anchor='center', stretch=True)
            elif col == "Модель":
                self.tree_assigned.column(col, width=240, anchor='center', stretch=True)
            elif col in ("Клиент", "Мастер"):
                self.tree_assigned.column(col, width=200, anchor='center', stretch=True)
            elif col == "Стоимость":
                self.tree_assigned.column(col, width=115, anchor='center', stretch=True)
            elif col == "Цена работы":
                self.tree_assigned.column(col, width=120, anchor='center', stretch=True)
            elif col == "Неисправность":
                self.tree_assigned.column(col, width=60, anchor='center', stretch=True)
            elif col == "Статус":
                self.tree_assigned.column(col, width=120, anchor='center', stretch=True)
            else:
                self.tree_assigned.column(col, width=120, anchor='center', stretch=True)
        self.tree_assigned.pack(expand=True, fill="both")
        def block_column_resize_assigned(event):
            region = self.tree_assigned.identify_region(event.x, event.y)
            if region == 'separator':
                return 'break'
        self.tree_assigned.bind('<Button-1>', block_column_resize_assigned, add='+')

        # Стили для интерфейса
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#f0f0f0")
        style.configure("Sidebar.TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Sidebar.TButton", background="#f0f0f0", borderwidth=0)
        style.configure("Border.TFrame", background="#e1e1e1")
        style.configure("Treeview", rowheight=25, font=('Arial', 12), background="#f0f0f0", fieldbackground="#f0f0f0")
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), background="#f0f0f0")
        style.map("Treeview", background=[('selected', '#0078d7')])
        style.configure("Custom.TFrame", background="#f0f0f0")

        # Контекстное меню
        self.context_menu_current = tk.Menu(self, tearoff=0)
        self.context_menu_current.add_command(label="Открыть", command=self.open_order)
        self.context_menu_current.add_command(label="Изменить", command=self.edit_order)
        self.context_menu_current.add_command(label="Удалить", command=self.delete_order)
        self.context_menu_current.add_command(label="Отметить как выполненный", command=self.mark_done)
        self.context_menu_current.add_command(label="Отменить заказ", command=self.cancel_order)
        self.context_menu_current.add_command(label="Присвоить", command=self.assign_order)
        self.context_menu_current.add_command(label="Чек", command=self.show_check)

        self.context_menu_done = tk.Menu(self, tearoff=0)
        self.context_menu_done.add_command(label="Открыть", command=self.open_done_order)
        self.context_menu_done.add_command(label="Вернуть в текущие", command=self.return_order)
        self.context_menu_done.add_command(label="Чек", command=self.show_done_check)

        self.context_menu_canceled = tk.Menu(self, tearoff=0)
        self.context_menu_canceled.add_command(label="Открыть", command=self.open_canceled_order)
        self.context_menu_canceled.add_command(label="Вернуть в текущие", command=self.return_canceled_order)
        self.context_menu_canceled.add_command(label="Чек", command=self.show_canceled_check)

        self.context_menu_assigned = tk.Menu(self, tearoff=0)
        self.context_menu_assigned.add_command(label="Открыть", command=self.open_assigned_order)
        self.context_menu_assigned.add_command(label="Вернуть в текущие", command=self.return_assigned_order)
        self.context_menu_assigned.add_command(label="Чек", command=self.show_assigned_check)

        self.tree_current.bind("<Button-3>", self.show_context_menu_current)
        self.tree_done.bind("<Button-3>", self.show_context_menu_done)
        self.tree_canceled.bind("<Button-3>", self.show_context_menu_canceled)
        self.tree_assigned.bind("<Button-3>", self.show_context_menu_assigned)

        # Привязка событий выбора
        self.tree_current.bind("<<TreeviewSelect>>", self.on_current_select)
        self.tree_done.bind("<<TreeviewSelect>>", self.on_done_select)
        self.tree_canceled.bind("<<TreeviewSelect>>", self.on_canceled_select)
        self.tree_assigned.bind("<<TreeviewSelect>>", self.on_assigned_select)

        # --- Вкладка настройки ---
        def build_settings_ui():
            print('build_settings_ui called')
            for child in self.tab_settings.winfo_children():
                child.destroy()
            # Определяем размеры экрана и делаем окно настроек компактным
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            min_width = min(700, int(screen_width * 0.9))
            min_height = min(500, int(screen_height * 0.8))
            self.tab_settings.update_idletasks()
            self.tab_settings.winfo_toplevel().minsize(min_width, min_height)
            settings_frame = ttk.Frame(self.tab_settings)
            settings_frame.pack(fill="both", expand=True, padx=40, pady=16)
            inner_frame = ttk.Frame(settings_frame)
            inner_frame.pack(fill='both', expand=True, padx=40, pady=0)
            data_management_frame = ttk.LabelFrame(inner_frame, text="Управление данными")
            data_management_frame.pack(side='top', pady=2, padx=2, fill='x', expand=True)
            # Удаляю попытку установить font для LabelFrame, это не поддерживается
            # for widget in data_management_frame.winfo_children():
            #     try:
            #         widget.configure(font=("Arial", 10))
            #     except Exception:
            #         pass
            paths_frame = ttk.LabelFrame(inner_frame, text="Настройки путей")
            paths_frame.pack(side='top', pady=2, padx=2, fill='x', expand=True)
            data_path_var = tk.StringVar(value=self.data_file)
            self.backup_bat_var = tk.StringVar(value=self.backup_bat_path)  # теперь это атрибут класса
            dropbox_frame = ttk.LabelFrame(inner_frame, text="Информация о ASBESTserver")
            dropbox_frame.pack(side='top', pady=2, padx=2, fill='x', expand=True)
            dropbox_info_label = ttk.Label(dropbox_frame, text="")
            dropbox_info_label.pack(pady=5)
            dropbox_usage_frame = ttk.Frame(dropbox_frame)
            dropbox_usage_frame.pack(pady=5)
            dropbox_used_label = ttk.Label(dropbox_usage_frame, text="0 MB")
            dropbox_used_label.pack(side="left")
            dropbox_usage_bar = ttk.Progressbar(dropbox_usage_frame, orient="horizontal", length=200, mode="determinate")
            dropbox_usage_bar.pack(side="left", expand=True, fill="x", padx=5)
            dropbox_total_label = ttk.Label(dropbox_usage_frame, text="25600 MB")
            dropbox_total_label.pack(side="left")
            def get_dropbox_folder_size():
                import os
                total_size = 0
                dropbox_path = None
                data_path = data_path_var.get()
                if data_path.lower().startswith("c:/asbestserver") or data_path.lower().startswith("/asbestserver"):
                    parts = data_path.replace("\\", "/").split("/")
                    for i, part in enumerate(parts):
                        if part.lower() == "asbestserver":
                            dropbox_path = "/".join(parts[:i+1])
                            break
                if dropbox_path and os.path.exists(dropbox_path):
                    for dirpath, dirnames, filenames in os.walk(dropbox_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            try:
                                total_size += os.path.getsize(fp)
                            except Exception:
                                pass
                return total_size // (1024*1024)  # MB
            def update_dropbox_info():
                used_mb = get_dropbox_folder_size()
                # Проверяем, существует ли виджет перед обновлением
                if dropbox_info_label.winfo_exists():
                    dropbox_info_label.config(text=f"Занято в ASBESTserver: {used_mb} MB из 25600 MB")
                    dropbox_usage_bar["value"] = min(used_mb / 25600 * 100, 100)
                    dropbox_used_label.config(text=f"{used_mb} MB")
                    dropbox_total_label.config(text="25600 MB")
                    self.after(60000, update_dropbox_info)
            update_dropbox_info()
            # --- Путь к файлу данных ---
            ttk.Label(paths_frame, text="Путь к файлу данных:").pack(anchor="center", pady=(2,0))
            data_path_entry = ttk.Entry(paths_frame, textvariable=data_path_var, width=60)
            data_path_entry.pack(padx=2, pady=2, fill='x', expand=True)
            ttk.Button(paths_frame, text="Выбрать файл", style="My.TButton", command=self.choose_data_file).pack(pady=2, ipadx=10)
            # --- Путь к .bat ---
            ttk.Label(paths_frame, text="Путь к .bat-файлу автосохранения (.bat):").pack(anchor="center", pady=(6,0))
            backup_bat_entry = ttk.Entry(paths_frame, textvariable=self.backup_bat_var, width=60)
            backup_bat_entry.pack(padx=2, pady=2, fill='x', expand=True)
            ttk.Button(paths_frame, text="Выбрать файл", style="My.TButton", command=self.choose_backup_bat).pack(pady=2, ipadx=10)
        self.build_settings_ui = build_settings_ui
        self.build_settings_ui()
        # Добавляю обработчик для обновления настроек при переключении вкладки
        def on_tab_changed(event):
            if self.tab_control.nametowidget(self.tab_control.select()) is self.tab_settings:
                self.build_settings_ui()
                if self.backup_bat_var is not None:
                    self.backup_bat_var.set(self.backup_bat_path)  # синхронизируем значение при каждом открытии вкладки
        self.tab_control.bind('<<NotebookTabChanged>>', on_tab_changed)

        # Вкладка сортировки
        sort_frame = ttk.Frame(self.tab_sort)
        sort_frame.pack(fill="both", expand=True, padx=10, pady=10)

        sort_label = ttk.Label(sort_frame, text="Сортировка заказов", font=("Arial", 14))
        sort_label.pack(pady=10)

        sort_options_frame = ttk.Frame(sort_frame)
        sort_options_frame.pack(pady=10)

        self.sort_var = tk.StringVar(value=self.sort_var_value if hasattr(self, 'sort_var_value') else "date_desc")

        ttk.Radiobutton(
            sort_options_frame,
            text="По дате (новые сверху)",
            variable=self.sort_var,
            value="date_desc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По дате (старые сверху)",
            variable=self.sort_var,
            value="date_asc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По клиенту (А-Я)",
            variable=self.sort_var,
            value="client_asc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По клиенту (Я-А)",
            variable=self.sort_var,
            value="client_desc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По мастеру (А-Я)",
            variable=self.sort_var,
            value="master_asc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По мастеру (Я-А)",
            variable=self.sort_var,
            value="master_desc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По стоимости (дорогие сверху)",
            variable=self.sort_var,
            value="price_desc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По стоимости (дешевые сверху)",
            variable=self.sort_var,
            value="price_asc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По готовности (готовые сверху)",
            variable=self.sort_var,
            value="ready_desc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            sort_options_frame,
            text="По готовности (не готовые сверху)",
            variable=self.sort_var,
            value="ready_asc",
            command=self.apply_sorting
        ).pack(anchor="w", pady=5)

        # Информация
        info_frame = tk.Frame(self.tab_info)
        info_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Красивый заголовок и информация по центру
        tk.Label(info_frame, text="Asbest Order Manager", font=("Arial", 18, "bold"), fg="#0078d7").pack(pady=(10, 2), anchor="center")
        tk.Label(info_frame, text="AOM Version: 5.2.0", font=("Arial", 12)).pack(anchor="center")
        tk.Label(info_frame, text="Version Release Date: 28.07.2025", font=("Arial", 12)).pack(anchor="center")
        tk.Label(info_frame, text="Made for Asbest Repair Group", font=("Arial", 12)).pack(anchor="center")
        tk.Label(info_frame, text="AOM Creator: maknau80", font=("Arial", 12)).pack(anchor="center")
        tk.Label(info_frame, text="Asbest Order Manager ©", font=("Arial", 12)).pack(anchor="center", pady=(0, 10))

        # --- Профиль пользователя ---
        profile_text = f"Профиль: {self.current_user if self.current_user else '-'}"
        tk.Label(info_frame, text=profile_text, font=("Arial", 13, "bold"), fg="#0078d7").pack(pady=(0, 16), anchor="center")

        btns_frame = tk.Frame(info_frame)
        btns_frame.pack(pady=10)
        def change_profile():
            self.clear_ui()
            self.withdraw()
            self.show_login(None)
        change_profile_btn = ttk.Button(btns_frame, text="Сменить профиль", style="My.TButton", command=change_profile)
        change_profile_btn.pack(side="left", padx=10)
        def open_asbest_site():
            try:
                webbrowser.open("https://asbestrepairteam.github.io/Asbest/")
            except Exception:
                messagebox.showerror("Ошибка", "Не удалось открыть сайт")
        site_button = ttk.Button(btns_frame, text="Открыть сайт Asbest Repair", style="My.TButton", command=open_asbest_site)
        site_button.pack(side="left", padx=10)

        self.reload_trees()
        # self.tree_current.bind('<Configure>', lambda e: self.set_equal_column_widths(self.tree_current, ("Клиент", "Модель", "Цена работы", "Стоимость", "Запчасти", "Дата", "Статус")))
        # self.tree_done.bind('<Configure>', lambda e: self.set_equal_column_widths(self.tree_done, ("Клиент", "Модель", "Цена работы", "Стоимость", "Запчасти", "Дата", "Статус")))
        # self.tree_canceled.bind('<Configure>', lambda e: self.set_equal_column_widths(self.tree_canceled, ("Клиент", "Модель", "Цена работы", "Стоимость", "Запчасти", "Дата", "Статус")))
        # self.tree_assigned.bind('<Configure>', lambda e: self.set_equal_column_widths(self.tree_assigned, ("Клиент", "Модель", "Цена работы", "Стоимость", "Запчасти", "Дата", "Статус")))

        # В КОНЦЕ build_ui вызываем сортировку и заполнение таблиц
        self.apply_sorting()

    def extract_price(self, price_str):
        # Извлекает первое число (целое или с точкой/запятой) из строки
        if not isinstance(price_str, str):
            return 0.0
        match = re.search(r"[\d,.]+", price_str.replace(',', '.'))
        if match:
            try:
                return float(match.group().replace(',', '.'))
            except Exception:
                return 0.0
        return 0.0

    def apply_sorting(self):
        sort_type = self.sort_var.get() if hasattr(self, 'sort_var') else self.sort_var_value
        self.save_config()  # Сохраняем сортировку при каждом изменении
        try:
            if sort_type == "date_desc":
                self.orders_current.sort(key=lambda x: x.get("date", ""), reverse=True)
            elif sort_type == "date_asc":
                self.orders_current.sort(key=lambda x: x.get("date", ""))
            elif sort_type == "client_asc":
                self.orders_current.sort(key=lambda x: x.get("client", "").lower())
            elif sort_type == "client_desc":
                self.orders_current.sort(key=lambda x: x.get("client", "").lower(), reverse=True)
            elif sort_type == "master_asc":
                self.orders_current.sort(key=lambda x: x.get("master", "").lower())
            elif sort_type == "master_desc":
                self.orders_current.sort(key=lambda x: x.get("master", "").lower(), reverse=True)
            elif sort_type == "price_desc":
                self.orders_current.sort(key=lambda x: self.extract_price(x.get("price", 0)), reverse=True)
            elif sort_type == "price_asc":
                self.orders_current.sort(key=lambda x: self.extract_price(x.get("price", 0)))
            elif sort_type == "ready_desc":
                self.orders_current.sort(key=lambda x: x.get("ready", False), reverse=True)
            elif sort_type == "ready_asc":
                self.orders_current.sort(key=lambda x: x.get("ready", False))
        except Exception as e:
            print(f"Ошибка сортировки: {e}")
        self.reload_trees()

    def on_current_select(self, event):
        selected = self.tree_current.selection()
        if selected:
            index = self.tree_current.index(selected[0])
            order = Order.from_dict(self.orders_current[index])
            self.sidebar_label_current.configure(text=f"Выбран заказ:\n{order.client}\n{order.model}")
            
            # Активируем кнопки в боковой панели
            for btn in self.sidebar_btn_frame_current.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="normal")
        else:
            self.sidebar_label_current.configure(text="Нет выбранных заказов")
            for btn in self.sidebar_btn_frame_current.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="disabled")

    def on_done_select(self, event):
        selected = self.tree_done.selection()
        if selected:
            index = self.tree_done.index(selected[0])
            order = Order.from_dict(self.orders_done[index])
            self.sidebar_label_done.configure(text=f"Выбран заказ:\n{order.client}\n{order.model}")
            
            for btn in self.sidebar_btn_frame_done.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="normal")
        else:
            self.sidebar_label_done.configure(text="Нет выбранных заказов")
            for btn in self.sidebar_btn_frame_done.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="disabled")

    def on_canceled_select(self, event):
        selected = self.tree_canceled.selection()
        if selected:
            index = self.tree_canceled.index(selected[0])
            order = Order.from_dict(self.orders_canceled[index])
            self.sidebar_label_canceled.configure(text=f"Выбран заказ:\n{order.client}\n{order.model}")
            
            for btn in self.sidebar_btn_frame_canceled.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="normal")
        else:
            self.sidebar_label_canceled.configure(text="Нет выбранных заказов")
            for btn in self.sidebar_btn_frame_canceled.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="disabled")

    def on_assigned_select(self, event):
        selected = self.tree_assigned.selection()
        if selected:
            index = self.tree_assigned.index(selected[0])
            order = Order.from_dict(self.orders_assigned[index])
            self.sidebar_label_assigned.configure(text=f"Выбран заказ:\n{order.client}\n{order.model}")
            for btn in self.sidebar_btn_frame_assigned.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="normal")
        else:
            self.sidebar_label_assigned.configure(text="Нет выбранных заказов")
            for btn in self.sidebar_btn_frame_assigned.winfo_children():
                if isinstance(btn, (tk.Button, ttk.Button)):
                    btn.configure(state="disabled")

    def reload_trees(self):
        # self.load_data()  # УБРАНО: теперь данные не перезагружаются при каждом обновлении таблицы
        self.tree_current.delete(*self.tree_current.get_children())
        for order in self.orders_current:
            try:
                order_obj = Order.from_dict(order)
                self.tree_current.insert('', 'end', values=(
                    order_obj.client,
                    order_obj.master,
                    order_obj.model,
                    order_obj.work_price,
                    order_obj.price,
                    order_obj.date,
                    "Ожидает выдачи" if order_obj.ready else "Не готов"
                ))
            except Exception as e:
                print(f"Ошибка при загрузке заказа: {e}")
        self.tree_done.delete(*self.tree_done.get_children())
        for order in self.orders_done:
            try:
                order_obj = Order.from_dict(order)
                self.tree_done.insert('', 'end', values=(
                    order_obj.client,
                    order_obj.master,
                    order_obj.model,
                    order_obj.work_price,
                    order_obj.price,
                    order_obj.date,
                    "Выдан" if order_obj.ready else "Не готов"
                ))
            except Exception as e:
                print(f"Ошибка при загрузке заказа: {e}")
        self.tree_canceled.delete(*self.tree_canceled.get_children())
        for order in self.orders_canceled:
            try:
                order_obj = Order.from_dict(order)
                self.tree_canceled.insert('', 'end', values=(
                    order_obj.client,
                    order_obj.master,
                    order_obj.model,
                    order_obj.work_price,
                    order_obj.price,
                    order_obj.date,
                    "Отменён" if order_obj.ready else "Отменён"
                ))
            except Exception as e:
                print(f"Ошибка при загрузке заказа: {e}")
        self.tree_assigned.delete(*self.tree_assigned.get_children())
        for order in self.orders_assigned:
            try:
                order_obj = Order.from_dict(order)
                self.tree_assigned.insert('', 'end', values=(
                    order_obj.client,
                    order_obj.master,
                    order_obj.model,
                    order_obj.work_price,
                    order_obj.price,
                    order_obj.date,
                    "Присвоен" if order_obj.ready else "Присвоен"
                ))
            except Exception as e:
                print(f"Ошибка при загрузке заказа: {e}")

    def manual_reload_trees(self):
        self.reload_trees()
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Информация", "Обновлено успешно")

    def show_context_menu_current(self, event):
        item = self.tree_current.identify_row(event.y)
        if item:
            self.tree_current.selection_set(item)
            self.context_menu_current.post(event.x_root, event.y_root)

    def show_context_menu_done(self, event):
        item = self.tree_done.identify_row(event.y)
        if item:
            self.tree_done.selection_set(item)
            self.context_menu_done.post(event.x_root, event.y_root)

    def show_context_menu_canceled(self, event):
        item = self.tree_canceled.identify_row(event.y)
        if item:
            self.tree_canceled.selection_set(item)
            self.context_menu_canceled.post(event.x_root, event.y_root)

    def show_context_menu_assigned(self, event):
        item = self.tree_assigned.identify_row(event.y)
        if item:
            self.tree_assigned.selection_set(item)
            self.context_menu_assigned.post(event.x_root, event.y_root)

    def add_order(self):
        data = self.get_order_data()
        if data:
            order = Order(
                client=data["client"],
                phone=data["phone"],
                email=data["email"],
                master=data["master"],
                model=data["model"],
                issue=data["issue"],
                work_price=data["work_price"],
                price=data["price"],
                parts=data["parts"],
                comment=data["comment"],
                warranty=data.get("warranty", "")
            )
            self.orders_current.append(order.to_dict())
            self.apply_sorting()
            self.save_data()

    def edit_order(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        index = self.tree_current.index(selected[0])
        old_data = self.orders_current[index]
        new_data = self.get_order_data(old_data)
        if new_data:
            self.orders_current[index] = Order.from_dict(new_data).to_dict()
            self.apply_sorting()
            self.save_data()

    def open_order(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        index = self.tree_current.index(selected[0])
        old_data = self.orders_current[index]
        self.get_order_data(old_data, read_only=True)

    def open_done_order(self):
        selected = self.tree_done.selection()
        if not selected:
            return
        index = self.tree_done.index(selected[0])
        old_data = self.orders_done[index]
        self.get_order_data(old_data, read_only=True)

    def open_canceled_order(self):
        selected = self.tree_canceled.selection()
        if not selected:
            return
        index = self.tree_canceled.index(selected[0])
        old_data = self.orders_canceled[index]
        self.get_order_data(old_data, read_only=True)

    def open_assigned_order(self):
        selected = self.tree_assigned.selection()
        if not selected:
            return
        index = self.tree_assigned.index(selected[0])
        old_data = self.orders_assigned[index]
        self.get_order_data(old_data, read_only=True)

    def delete_order(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот заказ?"):
            return
        index = self.tree_current.index(selected[0])
        del self.orders_current[index]
        self.apply_sorting()
        self.save_data()

    def mark_done(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        index = self.tree_current.index(selected[0])
        data = self.orders_current.pop(index)
        # Сохраняем исходный статус для восстановления при возврате
        data["prev_ready"] = data.get("ready", False)
        # Если был не готов, при переносе в выполненные ставим ready=True (Ожидает выдачи)
        if not data["prev_ready"]:
            data["ready"] = True
        self.orders_done.append(data)
        self.apply_sorting()
        self.save_data()

    def cancel_order(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        index = self.tree_current.index(selected[0])
        data = self.orders_current.pop(index)
        # Сохраняем исходный статус для восстановления при возврате
        data["prev_ready"] = data.get("ready", False)
        self.orders_canceled.append(data)
        self.apply_sorting()
        self.save_data()

    def return_order(self):
        selected = self.tree_done.selection()
        if not selected:
            return
        index = self.tree_done.index(selected[0])
        data = self.orders_done.pop(index)
        # Восстанавливаем исходный статус
        if "prev_ready" in data:
            data["ready"] = data["prev_ready"]
            del data["prev_ready"]
        self.orders_current.append(data)
        self.apply_sorting()
        self.save_data()

    def return_canceled_order(self):
        selected = self.tree_canceled.selection()
        if not selected:
            return
        index = self.tree_canceled.index(selected[0])
        data = self.orders_canceled.pop(index)
        # Восстанавливаем исходный статус
        if "prev_ready" in data:
            data["ready"] = data["prev_ready"]
            del data["prev_ready"]
        self.orders_current.append(data)
        self.apply_sorting()
        self.save_data()

    def return_assigned_order(self):
        selected = self.tree_assigned.selection()
        if not selected:
            return
        index = self.tree_assigned.index(selected[0])
        data = self.orders_assigned.pop(index)
        # Восстанавливаем исходный статус
        if "prev_ready" in data:
            data["ready"] = data["prev_ready"]
            del data["prev_ready"]
        self.orders_current.append(data)
        self.apply_sorting()
        self.save_data()

    def assign_order(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        index = self.tree_current.index(selected[0])
        data = self.orders_current.pop(index)
        # Сохраняем исходный статус для восстановления при возврате
        data["prev_ready"] = data.get("ready", False)
        self.orders_assigned.append(data)
        self.apply_sorting()
        self.save_data()

    def get_order_data(self, old_data=None, read_only=False):
        dialog = tk.Toplevel(self)
        dialog.title("Просмотр заказа" if read_only else "Добавить заказ")
        screen_width = self.winfo_screenwidth()
        window_width = 680
        content_width = 640
        # Удаляем скроллбар и canvas, используем обычный Frame
        content_width = 680
        content_pad = 32
        zapchast_block_height = 80  # Примерная высота одного блока (LabelFrame с полями)
        zapchast_count = 4
        content_height = zapchast_count * zapchast_block_height + 2 * content_pad
        dialog.geometry(f"{content_width}x{content_height}")
        dialog.minsize(content_width, content_height)
        # dialog.maxsize(content_width, content_height)  # Окно можно растягивать
        self.center_window(dialog)
        
        # Добавляем переменную для отслеживания полноэкранного режима
        self.parts_fullscreen_mode = False
        self.parts_entries = []  # Список для хранения всех полей ввода запчастей
        
        def on_resize(event):
            width = event.width
            new_fullscreen_mode = width > screen_width * 0.9
            if new_fullscreen_mode != self.parts_fullscreen_mode:
                self.parts_fullscreen_mode = new_fullscreen_mode
                # Переупаковываем все поля ввода
                for entry in self.parts_entries:
                    if hasattr(entry, 'pack_info'):
                        entry.pack_forget()
                        entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=self.parts_fullscreen_mode)
        dialog.bind('<Configure>', on_resize)
        
        # --- Новый скроллируемый контейнер ---
        canvas = tk.Canvas(dialog, highlightthickness=0, bd=0, relief='flat')
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Sidebar.TFrame")
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_frame_configure)
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Прокрутка колесиком мыши (оригинальный вариант)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        # --- ВОССТАНАВЛИВАЮ ОТСТУПЫ И ДИЗАЙН ---
        content_pad = 32
        content_frame = ttk.Frame(scrollable_frame, style="Sidebar.TFrame")
        content_frame.pack(fill="both", expand=True, padx=content_pad, pady=content_pad)
        # --- Готовность ---
        ready_var = tk.BooleanVar(value=(old_data.get("ready", False) if old_data else False))
        ready_frame = ttk.LabelFrame(content_frame, text="Готовность", padding=(10, 5, 10, 5))
        ready_frame.pack(fill='x', padx=0, pady=5)
        chk_ready = ttk.Checkbutton(ready_frame, text="Готов", variable=ready_var, state='disabled' if read_only else 'normal', style="TCheckbutton")
        chk_ready.pack(side='left', padx=10)
        chk_not_ready = ttk.Checkbutton(ready_frame, text="Не готов", variable=ready_var, onvalue=False, offvalue=True, state='disabled' if read_only else 'normal', style="TCheckbutton")
        # Реализуем поведение: если выбран "Готов", то "Не готов" снимается и наоборот
        def on_ready_change(*args):
            if ready_var.get():
                chk_not_ready.state(['!selected'])
            else:
                chk_ready.state(['!selected'])
            # Автообновление таблицы при изменении готовности
            if not read_only:
                self.apply_sorting()
        ready_var.trace_add('write', on_ready_change)
        chk_not_ready.pack(side='left', padx=10)

        fields = [
            ("Имя клиента", "client"),
            ("Номер телефона", "phone"),
            ("Email", "email"),
            ("Мастер", "master"),
            ("Модель устройства", "model"),
            ("Неисправность", "issue"),
            ("Срок гарантии", "warranty"),
            ("Комментарий", "comment"),
            ("Цена за работу", "work_price"),
            ("Стоимость заказа", "price")
        ]

        entries = {}
        for label, field in fields:
            block = ttk.LabelFrame(content_frame, text=label, padding=(10, 5, 10, 5))
            block.pack(fill='x', padx=0, pady=5)
            if field == "comment":
                entry = tk.Text(block, height=4, relief='flat', borderwidth=0, font=("Arial", 12))
                if old_data and field in old_data:
                    entry.insert("1.0", old_data[field])
                if read_only:
                    entry.config(state='disabled')
            else:
                entry = tk.Entry(block, relief='flat', borderwidth=0, font=("Arial", 12))
                if old_data and field in old_data:
                    entry.insert(0, old_data[field])
                if read_only:
                    entry.config(state='readonly')
            entry.pack(fill='x', padx=0, pady=0)
            entries[field] = entry

        parts_label = ttk.LabelFrame(content_frame, text="Запчасти, ссылки и цены", padding=(10, 5, 10, 5))
        parts_label.pack(fill='x', padx=0, pady=5)
        parts_frame = tk.Frame(parts_label, highlightthickness=0, bd=0, relief='flat')
        parts_frame.pack(fill='both', expand=True)
        parts_list = []

        # Сначала определяем add_part, чтобы она была доступна в add_part_field
        def add_part():
            add_part_field()
        def add_part_field(part_text='', link_text='', price_text=''):
            container = tk.Frame(parts_frame, bg='white')
            container.pack(fill='x', pady=3)
            border_color = '#cccccc'
            if read_only:
                part_entry = tk.Entry(container, relief='solid', borderwidth=1, font=("Arial", 12), bg="white", highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
                part_entry.insert(0, part_text)
                part_entry.config(state='readonly')
                part_entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=True)
                
                link_entry = tk.Entry(container, relief='solid', borderwidth=1, font=("Arial", 12), bg="white", highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
                link_entry.insert(0, link_text)
                link_entry.config(state='readonly')
                link_entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=True)
                
                price_entry = tk.Entry(container, relief='solid', borderwidth=1, font=("Arial", 12), bg="white", highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
                price_entry.insert(0, price_text)
                price_entry.config(state='readonly')
                price_entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=True)
            else:
                part_entry = tk.Entry(container, relief='solid', borderwidth=1, font=("Arial", 12), bg="white", highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
                part_entry.insert(0, part_text)
                part_entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=True)
                
                link_entry = tk.Entry(container, relief='solid', borderwidth=1, font=("Arial", 12), bg="white", highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
                link_entry.insert(0, link_text)
                link_entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=True)
                
                price_entry = tk.Entry(container, relief='solid', borderwidth=1, font=("Arial", 12), bg="white", highlightthickness=1, highlightbackground=border_color, highlightcolor=border_color)
                price_entry.insert(0, price_text)
                price_entry.pack(side='left', padx=(0, 6), pady=2, fill='x', expand=True)
                
                btn_frame = tk.Frame(container, bg='white')
                btn_frame.pack(side='left', padx=(6,0))
                parts_list.append((part_entry, link_entry, price_entry))

        # Заполнение полей запчастей
        if old_data and "parts" in old_data and old_data["parts"]:
            parts_raw = old_data["parts"].split(", ")
            for p in parts_raw:
                part_parts = p.split(" | ")
                if len(part_parts) == 3:
                    part_name, link, part_price = part_parts
                    add_part_field(part_name.strip(), link.strip(), part_price.strip())
                elif len(part_parts) == 2:
                    part_name, rest = part_parts
                    if "http" in rest:
                        add_part_field(part_name.strip(), rest.strip(), "")
                    else:
                        add_part_field(part_name.strip(), "", rest.strip())
                else:
                    add_part_field(p.strip(), "", "")
        else:
            add_part_field()

        if not read_only:
            def add_part():
                add_part_field()
            add_part_btn = ttk.Button(content_frame, text="+ Запчасть", style="My.TButton", command=add_part)
            add_part_btn.pack(pady=5)

        saved: dict[str, Any] = {'result': None}

        if not read_only:
            def save():
                if not entries['client'].get().strip() or not entries['model'].get().strip():
                    messagebox.showerror("Ошибка", "Имя клиента и модель обязательны")
                    return
                data = {
                    "client": entries['client'].get().strip(),
                    "phone": entries['phone'].get().strip(),
                    "email": entries['email'].get().strip(),
                    "master": entries['master'].get().strip(),
                    "model": entries['model'].get().strip(),
                    "issue": entries['issue'].get().strip(),
                    "warranty": entries['warranty'].get().strip() if 'warranty' in entries else '',
                    "comment": entries['comment'].get("1.0", "end-1c").strip(),
                    "work_price": entries['work_price'].get().strip(),
                    "price": entries['price'].get().strip(),
                    "parts": "",
                    "ready": bool(ready_var.get())
                }
                parts = []
                for p, l, pr in parts_list:
                    part = p.get().strip()
                    link = l.get().strip()
                    price = pr.get().strip()
                    if part:
                        part_str = part
                        if link:
                            part_str += f" | {link}"
                        if price:
                            part_str += f" | {price}"
                        parts.append(part_str)
                data["parts"] = ", ".join(parts)
                saved['result'] = data
                dialog.destroy()
            save_btn = ttk.Button(content_frame, text="Сохранить", style="My.TButton", command=save)
            save_btn.pack(pady=10)

        dialog.wait_window()
        # Удаляем бинды mousewheel только после закрытия окна
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        return saved['result']

    def export_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON файлы", "*.json")])
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump({
                        "current": self.orders_current, 
                        "done": self.orders_done,
                        "canceled": self.orders_canceled,
                        "assigned": self.orders_assigned
                    }, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Успех", f"Данные успешно экспортированы в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные:\n{e}")

    def import_data(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.orders_current = self.convert_old_format(data.get("current", []))
                self.orders_done = self.convert_old_format(data.get("done", []))
                self.orders_canceled = self.convert_old_format(data.get("canceled", []))
                self.orders_assigned = self.convert_old_format(data.get("assigned", [])) if "assigned" in data else []
                self.data_file = filename
                self.save_config()
                self.reload_trees()
                self.save_data()
                messagebox.showinfo("Успех", f"Данные успешно импортированы из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные:\n{e}")

    def choose_data_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if filename:
            self.data_file = filename
            self.save_config()
            self.load_data()
            self.reload_trees()
            messagebox.showinfo("Успех", f"Путь к файлу данных сохранён и данные загружены из {filename}")

    def choose_backup_bat(self):
        filename = filedialog.askopenfilename(filetypes=[("BAT файлы", "*.bat")])
        if filename:
            self.backup_bat_path = filename
            self.save_config()
            messagebox.showinfo("Успех", f"Путь к BAT файлу сохранён: {filename}")

    def save_data_path(self):
        path = self.data_file
        if not os.path.exists(path):
            messagebox.showerror("Ошибка", "Файл не найден")
            return
        self.data_file = path
        self.save_config()
        self.load_data()
        self.reload_trees()
        messagebox.showinfo("Успех", "Путь сохранён и данные загружены")

    def save_backup_bat_path(self):
        path = self.backup_bat_path
        if path and not os.path.exists(path):
            messagebox.showerror("Ошибка", "Файл не найден")
            return
        self.backup_bat_path = path
        self.save_config()
        messagebox.showinfo("Успех", "Путь к BAT файлу сохранён")

    def set_equal_column_widths(self, tree, cols):
        total_width = tree.winfo_width()
        col_count = len(cols)
        if col_count == 0:
            return
        col_width = max(50, total_width // col_count)
        for col in cols:
            tree.column(col, width=col_width)

    def show_check(self):
        selected = self.tree_current.selection()
        if not selected:
            return
        index = self.tree_current.index(selected[0])
        order_data = self.orders_current[index]
        self.create_check_window(order_data)

    def show_done_check(self):
        selected = self.tree_done.selection()
        if not selected:
            return
        index = self.tree_done.index(selected[0])
        order_data = self.orders_done[index]
        self.create_check_window(order_data)

    def show_canceled_check(self):
        selected = self.tree_canceled.selection()
        if not selected:
            return
        index = self.tree_canceled.index(selected[0])
        order_data = self.orders_canceled[index]
        self.create_check_window(order_data)

    def show_assigned_check(self):
        selected = self.tree_assigned.selection()
        if not selected:
            return
        index = self.tree_assigned.index(selected[0])
        order_data = self.orders_assigned[index]
        self.create_check_window(order_data)

    def create_check_window(self, order_data):
        check_window = tk.Toplevel(self)
        check_window.title("Чек заказа")
        check_window.geometry("500x600")
        check_window.resizable(False, False)
        self.center_window(check_window)
        
        # Создаем скроллируемый контейнер
        canvas = tk.Canvas(check_window, highlightthickness=0, bd=0, relief='flat')
        scrollbar = ttk.Scrollbar(check_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Прокрутка колесиком мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Создаем фрейм для чека
        check_frame = tk.Frame(scrollable_frame, bg="white", padx=30, pady=30)
        check_frame.pack(fill="both", expand=True)
        
        # Заголовок
        header_frame = tk.Frame(check_frame, bg="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # --- ДОБАВЛЯЕМ ЛОГОТИП В ВИЗУАЛЬНОЕ ОКНО ЧЕКА ---
        try:
            logo_img = tk.PhotoImage(file=resource_path("logo2.png"))
            logo_label = tk.Label(header_frame, image=logo_img, bg="white")
            logo_label.image = logo_img  # type: ignore[attr-defined]  # чтобы не удалялся сборщиком мусора
            logo_label.pack(pady=(0, 10))
        except Exception as e:
            print(f"Ошибка загрузки logo2.png (чек): {e}")
            pass  # если не найден логотип, просто пропускаем
        # --- КОНЕЦ ДОБАВЛЕНИЯ ЛОГОТИПА ---

        title_label = tk.Label(header_frame, text="ASBEST REPAIR TEAM", 
                              font=("Arial", 16, "bold"), bg="white")
        title_label.pack()
        
        order_label = tk.Label(header_frame, text=f"Заказ: {order_data.get('model', '')}", 
                              font=("Arial", 12), bg="white")
        order_label.pack()
        
        # Данные заказа (только важные)
        data_frame = tk.Frame(check_frame, bg="white")
        data_frame.pack(fill="both", expand=True)
        
        order_obj = Order.from_dict(order_data)
        
        # Создаем поля данных (уменьшенный список)
        fields_data = [
            ("Клиент:", order_obj.client),
            ("Модель:", order_obj.model),
            ("Неисправность:", order_obj.issue),
            ("Срок гарантии:", order_data.get('warranty', '')),
            ("Стоимость:", order_obj.price),
            ("Дата:", order_obj.date)
        ]
        
        for label, value in fields_data:
            if value:  # Показываем только заполненные поля
                field_frame = tk.Frame(data_frame, bg="white")
                field_frame.pack(fill="x", pady=3)
                
                label_widget = tk.Label(field_frame, text=label, font=("Arial", 11, "bold"), 
                                       bg="white", anchor="w")
                label_widget.pack(anchor="w")
                
                value_widget = tk.Label(field_frame, text=value, font=("Arial", 11), 
                                       bg="white", anchor="w", wraplength=400)
                value_widget.pack(anchor="w", pady=(1, 0))
        
        # Запчасти отдельно с разделением на строки
        if order_obj.parts:
            parts_frame = tk.Frame(data_frame, bg="white")
            parts_frame.pack(fill="x", pady=3)
            
            parts_label = tk.Label(parts_frame, text="Запчасти:", font=("Arial", 11, "bold"), 
                                  bg="white", anchor="w")
            parts_label.pack(anchor="w")
            
            parts_raw = order_obj.parts.split(", ")
            for part in parts_raw:
                if part.strip():
                    part_parts = part.split(" | ")
                    part_name = part_parts[0].strip() if len(part_parts) > 0 else ""
                    link = part_parts[1].strip() if len(part_parts) > 1 else ""
                    price = part_parts[2].strip() if len(part_parts) > 2 else ""
                    if part_name:
                        part_widget = tk.Label(parts_frame, text=part_name, font=("Arial", 11), bg="white", anchor="w", wraplength=400)
                        part_widget.pack(anchor="w", pady=(1, 0))
                    if link:
                        link_widget = tk.Label(parts_frame, text=link, font=("Arial", 10, "underline"), fg="blue", bg="white", anchor="w", wraplength=400, cursor="hand2")
                        link_widget.pack(anchor="w", pady=(0, 0))
                        link_widget.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
                    if price:
                        price_widget = tk.Label(parts_frame, text=price, font=("Arial", 10), bg="white", anchor="w", wraplength=400)
                        price_widget.pack(anchor="w", pady=(0, 0))
                    # Отступ между запчастями
                    if part_name or link or price:
                        tk.Label(parts_frame, text="", bg="white").pack(anchor="w", pady=(0, 2))
        
        # Подпись внизу
        footer_frame = tk.Frame(check_frame, bg="white")
        footer_frame.pack(fill="x", pady=(20, 0))
        
        footer_label = tk.Label(footer_frame, text="Сохраните этот чек на случай возврата по гарантии", 
                               font=("Arial", 11), bg="white")
        footer_label.pack()
        
        # Кнопка сохранения (теперь внизу, внутри скролла)
        save_frame = tk.Frame(check_frame, bg="white")
        save_frame.pack(fill="x", pady=10)
        
        def save_check():
            try:
                from PIL import Image as PILImage, ImageDraw, ImageFont
                import os
                # Функция для переноса текста по ширине
                def wrap_text(text, font, max_width):
                    img_tmp = PILImage.new('RGB', (10, 10), 'white')
                    draw_tmp = ImageDraw.Draw(img_tmp)
                    words = text.split()
                    lines = []
                    current_line = ''
                    for word in words:
                        test_line = current_line + (' ' if current_line else '') + word
                        if draw_tmp.textlength(test_line, font=font) <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    return lines
                # --- ДОБАВЛЯЕМ ЛОГОТИП В JPG ЧЕКА ---
                logo_path = resource_path("logo2.png")
                logo_img = None
                try:
                    logo_img = PILImage.open(logo_path).convert("RGBA")
                except Exception as e:
                    print(f"Ошибка загрузки logo2.png (JPG чек): {e}")
                    logo_img = None
                # --- КОНЕЦ ДОБАВЛЕНИЯ ЛОГОТИПА ---
                img_width = 500
                min_height = 700
                img_height = min_height
                while True:
                    img = PILImage.new('RGB', (img_width, img_height), 'white')
                    draw = ImageDraw.Draw(img)
                    # Используем стандартный шрифт (должно быть внутри цикла!)
                    try:
                        font_large = ImageFont.truetype("arialbd.ttf", 16)
                        font_medium = ImageFont.truetype("arialbd.ttf", 12)
                        font_small = ImageFont.truetype("arialbd.ttf", 10)
                        font_small_bold = font_small
                    except:
                        font_large = ImageFont.load_default()
                        font_medium = ImageFont.load_default()
                        font_small = ImageFont.load_default()
                        font_small_bold = font_small
                    y_position = 30
                    # Вставляем логотип, если удалось загрузить
                    if logo_img:
                        logo_w = 120
                        scale = logo_w / logo_img.width
                        logo_h = int(logo_img.height * scale)
                        logo_resized = logo_img.resize((logo_w, logo_h), PILImage.Resampling.LANCZOS)
                        img.paste(logo_resized, (int((img_width-logo_w)/2), y_position), logo_resized)
                        y_position += logo_h + 10
                    # --- СЛЕДОМ ЗАГОЛОВОК И ЗАКАЗ ---
                    text1 = "ASBEST REPAIR TEAM"
                    text2 = f"Заказ: {order_obj.model}"
                    text1_width = draw.textlength(text1, font=font_large)
                    text2_width = draw.textlength(text2, font=font_medium)
                    x1 = int((img_width - text1_width) / 2)
                    x2 = int((img_width - text2_width) / 2)
                    draw.text((x1, y_position), text1, fill="black", font=font_large)
                    y_position += 35
                    draw.text((x2, y_position), text2, fill="black", font=font_medium)
                    y_position += 50
                    # --- ДАННЫЕ ЗАКАЗА ---
                    for label, value in fields_data:
                        if value:
                            draw.text((30, y_position), label, fill="black", font=font_small_bold)
                            y_position += 18
                            words = value.split()
                            lines = []
                            current_line = ""
                            for word in words:
                                test_line = current_line + " " + word if current_line else word
                                if draw.textlength(test_line, font=font_small_bold) < 440:
                                    current_line = test_line
                                else:
                                    if current_line:
                                        lines.append(current_line)
                                    current_line = word
                            if current_line:
                                lines.append(current_line)
                            for line in lines:
                                draw.text((30, y_position), line, fill="black", font=font_small_bold)
                                y_position += 18
                            y_position += 6
                    # --- ЗАПЧАСТИ ---
                    if order_obj.parts:
                        draw.text((30, y_position), "Запчасти:", fill="black", font=font_small)
                        y_position += 20
                        parts_raw = order_obj.parts.split(", ")
                        for part in parts_raw:
                            if part.strip():
                                part_parts = part.split(" | ")
                                part_name = part_parts[0].strip() if len(part_parts) > 0 else ""
                                link = part_parts[1].strip() if len(part_parts) > 1 else ""
                                price = part_parts[2].strip() if len(part_parts) > 2 else ""
                                if len(parts_raw) > 1:
                                    box_x0 = 25
                                    box_y0 = y_position + 3
                                    box_x1 = img_width - 25
                                    block_lines = 1  # теперь одна строка
                                    box_y1 = y_position + 3 + block_lines*24 + 8
                                    draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline="#888", width=1)
                                    # Название
                                    name_x = box_x0 + 8
                                    name_y = y_position + 12
                                    draw.text((name_x, name_y), part_name, fill="black", font=font_small_bold)
                                    # Ссылка
                                    link_x = box_x0 + 150  # сдвигаем ближе к центру
                                    link_y = name_y
                                    max_link_width = 220
                                    link_text = link
                                    # Обрезаем ссылку, если она длинная
                                    while draw.textlength(link_text, font=font_small_bold) > max_link_width and len(link_text) > 3:
                                        link_text = link_text[:-1]
                                    if link_text != link:
                                        link_text = link_text[:-3] + '...'
                                    draw.text((link_x, link_y), link_text, fill="blue", font=font_small_bold)
                                    # Цена
                                    price_x = box_x1 - 110  # справа, с запасом
                                    price_y = name_y
                                    price_text = price
                                    # Гарантируем, что цена не обрежется (до 10 символов)
                                    if len(price_text) > 10:
                                        price_text = price_text[:10]
                                    draw.text((price_x, price_y), price_text, fill="black", font=font_small_bold)
                                    y_position = box_y1 + 6
                                else:
                                    if part_name:
                                        draw.text((30, y_position), part_name, fill="black", font=font_small_bold)
                                        y_position += 18
                                    if link:
                                        draw.text((30, y_position), link, fill="blue", font=font_small_bold)
                                        y_position += 18
                                    if price:
                                        draw.text((30, y_position), price, fill="black", font=font_small_bold)
                                        y_position += 18
                                    if part_name or link or price:
                                        y_position += 6
                    # --- ПОДПИСИ ВНИЗУ ---
                    y_position += 30
                    try:
                        font_footer = ImageFont.truetype("arialbd.ttf", 12)
                    except:
                        font_footer = font_medium
                    footer_text = "Сохраните этот чек на случай возврата по гарантии."
                    footer_text2 = "Если в чеке отсутствует строка с сроком гарантии - гарантия не распространяется на ваше устройство, запчасти и / или неисправность."
                    max_footer_width = img_width - 60
                    footer_lines = wrap_text(footer_text, font_footer, max_footer_width)
                    footer2_lines = wrap_text(footer_text2, font_footer, max_footer_width)
                    for line in footer_lines:
                        line_width = draw.textlength(line, font=font_footer)
                        x_line = int((img_width - line_width) / 2)
                        draw.text((x_line, y_position), line, fill="black", font=font_footer)
                        y_position += 22
                    for line in footer2_lines:
                        line_width = draw.textlength(line, font=font_footer)
                        x_line = int((img_width - line_width) / 2)
                        draw.text((x_line, y_position), line, fill="black", font=font_footer)
                        y_position += 22
                    # --- ПРОВЕРКА ВЫСОТЫ ---
                    if y_position > img_height - 40:
                        img_height += 200
                        continue
                    else:
                        break
                # Сохраняем в папку Downloads
                downloads_path = os.path.expanduser("~/Downloads")
                if not os.path.exists(downloads_path):
                    downloads_path = os.path.expanduser("~/Desktop")
                model_name = str(order_obj.model).replace(" ", "_").replace("/", "_")
                filename = f"{model_name}_asbestrepair.jpg"
                filepath = os.path.join(downloads_path, filename)
                img.save(filepath, "JPEG", quality=95)
                messagebox.showinfo("Успех", f"Чек сохранен в:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить чек:\n{e}")
        
        save_button = ttk.Button(save_frame, text="💾 Сохранить как JPG", command=save_check, style="My.TButton")
        save_button.pack()
        
        # Удаляем бинды mousewheel после закрытия окна
        def on_closing():
            try:
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            except Exception:
                pass
            check_window.destroy()
        
        check_window.protocol("WM_DELETE_WINDOW", on_closing)

    def clear_ui(self):
        # Удалить все дочерние виджеты главного окна
        for widget in self.winfo_children():
            widget.destroy()

# --- Восстанавливаю функцию для поиска ресурсов ---
def resource_path(filename):
    import sys, os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

if __name__ == "__main__":
    app = AsbestApp()
    app.mainloop()