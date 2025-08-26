import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import winreg
import os
import subprocess
import sys
from PIL import Image, ImageTk
import threading
import math

class ModernButton(tk.Canvas):
    def __init__(self, parent, text="Button", width=200, height=40, 
                 color="#3498db", hover_color="#2980b9", command=None, 
                 icon=None, font_size=11):
        super().__init__(parent, width=width, height=height, 
                         highlightthickness=0, bg=parent.cget("bg"))
        
        self.color = color
        self.hover_color = hover_color
        self.command = command
        self.width = width
        self.height = height
        
        # Create gradient background
        self.background = self.create_round_rect(2, 2, width-2, height-2, 15, fill=color)
        
        # Add text
        self.text_id = self.create_text(width//2, height//2, text=text, 
                                      fill="white", font=("Segoe UI", font_size, "bold"))
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def create_round_rect(self, x1, y1, x2, y2, radius=15, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def on_enter(self, event):
        self.itemconfig(self.background, fill=self.hover_color)
        
    def on_leave(self, event):
        self.itemconfig(self.background, fill=self.color)
        
    def on_click(self, event):
        # Ripple effect
        x, y = event.x, event.y
        ripple = self.create_oval(x-5, y-5, x+5, y+5, fill="white", outline="", alpha=0.8)
        
        def expand_ripple(radius=5):
            if radius < 100:
                self.coords(ripple, x-radius, y-radius, x+radius, y+radius)
                alpha = int(255 * (1 - radius/100))
                self.itemconfig(ripple, fill=f"#ffffff{alpha:02x}")
                self.after(10, lambda: expand_ripple(radius+5))
            else:
                self.delete(ripple)
                if self.command:
                    self.command()
        
        expand_ripple()

class SystemTweaker:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ System Tweaker Pro")
        self.root.geometry("800x700")
        self.root.configure(bg="#1e1e2e")
        self.root.minsize(750, 650)
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.center_window()
        self.setup_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Header with gradient
        header = tk.Canvas(self.root, bg="#2c2c3b", height=70, highlightthickness=0)
        header.pack(fill="x")
        
        # Create gradient effect
        for i in range(800):
            r = int(44 + (i/800) * 20)
            g = int(44 + (i/800) * 10)
            b = int(59 - (i/800) * 10)
            color = f"#{r:02x}{g:02x}{b:02x}"
            header.create_line(i, 0, i, 70, fill=color)
        
        header.create_text(400, 35, text="⚙️ System Tweaker Pro", 
                         fill="white", font=("Segoe UI", 20, "bold"))
        
        # Main container with notebook
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configure style
        style = ttk.Style()
        style.configure("Custom.TNotebook", background="#1e1e2e", borderwidth=0)
        style.configure("Custom.TNotebook.Tab", background="#2c2c3b", foreground="white",
                       font=("Segoe UI", 10, "bold"), padding=[15, 5])
        style.map("Custom.TNotebook.Tab", background=[("selected", "#3498db")])
        
        # Create tabs
        self.create_windows_tab()
        self.create_appearance_tab()
        self.create_system_tab()
        self.create_tools_tab()
        self.create_advanced_tab()
        
        # Status bar
        status_bar = tk.Frame(self.root, bg="#2c2c3b", height=25)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, text="🟢 Готов к работе", fg="white", bg="#2c2c3b", 
                font=("Segoe UI", 9)).pack(side="left", padx=10)
        
    def create_windows_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(tab, text="🪟 Windows")
        
        # Theme section
        frame1 = tk.LabelFrame(tab, text=" 🎨 Тема оформления", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame1.pack(fill="x", padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value="Светлая")
        tk.Radiobutton(frame1, text="☀️ Светлая тема", variable=self.theme_var, 
                      value="Светлая", font=("Segoe UI", 10), fg="white", 
                      bg="#1e1e2e", selectcolor="#3498db").pack(anchor="w", pady=5, padx=10)
        tk.Radiobutton(frame1, text="🌙 Тёмная тема", variable=self.theme_var, 
                      value="Тёмная", font=("Segoe UI", 10), fg="white", 
                      bg="#1e1e2e", selectcolor="#3498db").pack(anchor="w", pady=5, padx=10)
        
        ModernButton(frame1, text="Применить тему", color="#3498db", 
                    command=self.change_theme).pack(pady=10, padx=10)
        
        # Activation section
        frame2 = tk.LabelFrame(tab, text=" 🔐 Активация", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame2.pack(fill="x", padx=10, pady=10)
        
        ModernButton(frame2, text="Убрать водяной знак", color="#e74c3c",
                    command=self.remove_watermark).pack(pady=10, padx=10)
        
    def create_appearance_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(tab, text="🎨 Внешний вид")
        
        # Desktop icons
        frame1 = tk.LabelFrame(tab, text=" 🖥️ Рабочий стол", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame1.pack(fill="x", padx=10, pady=10)
        
        btn_frame = tk.Frame(frame1, bg="#1e1e2e")
        btn_frame.pack(pady=5)
        
        ModernButton(btn_frame, text="Скрыть значки", color="#9b59b6", width=150,
                    command=self.hide_desktop_icons).pack(side="left", padx=5)
        ModernButton(btn_frame, text="Показать значки", color="#9b59b6", width=150,
                    command=self.show_desktop_icons).pack(side="left", padx=5)
        
        # Taskbar
        frame2 = tk.LabelFrame(tab, text=" 📋 Панель задач", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame2.pack(fill="x", padx=10, pady=10)
        
        ModernButton(frame2, text="Выровнять по центру", color="#f39c12",
                    command=self.center_taskbar_icons).pack(pady=10, padx=10)
        
        # Visual effects
        frame3 = tk.LabelFrame(tab, text=" ✨ Визуальные эффекты", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame3.pack(fill="x", padx=10, pady=10)
        
        self.performance_var = tk.StringVar(value="По умолчанию")
        tk.Radiobutton(frame3, text="🎨 Наилучший вид", variable=self.performance_var, 
                      value="Наилучший вид", font=("Segoe UI", 10), fg="white", 
                      bg="#1e1e2e", selectcolor="#3498db").pack(anchor="w", pady=3, padx=10)
        tk.Radiobutton(frame3, text="⚡ Наилучшее быстродействие", variable=self.performance_var, 
                      value="Наилучшее быстродействие", font=("Segoe UI", 10), fg="white", 
                      bg="#1e1e2e", selectcolor="#3498db").pack(anchor="w", pady=3, padx=10)
        tk.Radiobutton(frame3, text="🔧 По умолчанию", variable=self.performance_var, 
                      value="По умолчанию", font=("Segoe UI", 10), fg="white", 
                      bg="#1e1e2e", selectcolor="#3498db").pack(anchor="w", pady=3, padx=10)
        
        ModernButton(frame3, text="Применить настройки", color="#2ecc71",
                    command=self.set_performance).pack(pady=10, padx=10)
        
    def create_system_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(tab, text="⚡ Система")
        
        # Shutdown timer
        frame1 = tk.LabelFrame(tab, text=" ⏰ Таймер выключения", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame1.pack(fill="x", padx=10, pady=10)
        
        self.shutdown_var = tk.StringVar(value="5")
        times = [("5 минут", "5"), ("10 минут", "10"), ("15 минут", "15"), 
                ("30 минут", "30"), ("Свое значение", "0")]
        
        for text, value in times:
            tk.Radiobutton(frame1, text=text, variable=self.shutdown_var, 
                          value=value, font=("Segoe UI", 10), fg="white", 
                          bg="#1e1e2e", selectcolor="#3498db").pack(anchor="w", pady=2, padx=10)
        
        btn_frame = tk.Frame(frame1, bg="#1e1e2e")
        btn_frame.pack(pady=10)
        
        ModernButton(btn_frame, text="Установить таймер", color="#f39c12", width=150,
                    command=self.set_shutdown_timer).pack(side="left", padx=5)
        ModernButton(btn_frame, text="Отменить выключение", color="#e74c3c", width=150,
                    command=self.cancel_shutdown).pack(side="left", padx=5)
        
        # Timezone
        frame2 = tk.LabelFrame(tab, text=" 🌍 Часовой пояс", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame2.pack(fill="x", padx=10, pady=10)
        
        self.load_timezones()
        
        search_frame = tk.Frame(frame2, bg="#1e1e2e")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 Поиск:", font=("Segoe UI", 9), 
                fg="white", bg="#1e1e2e").pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_timezones)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                              font=("Segoe UI", 9), bg="#2c2c3b", fg="white",
                              insertbackground="white", relief="flat")
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        list_frame = tk.Frame(frame2)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.timezone_listbox = tk.Listbox(list_frame, font=("Segoe UI", 9), height=6,
                                         bg="#2c2c3b", fg="white", selectbackground="#3498db",
                                         yscrollcommand=scrollbar.set, relief="flat")
        self.timezone_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.timezone_listbox.yview)
        
        for tz in self.russian_timezones:
            self.timezone_listbox.insert(tk.END, tz)
        
        ModernButton(frame2, text="Установить часовой пояс", color="#1abc9c",
                    command=self.set_timezone).pack(pady=10, padx=10)
        
    def create_tools_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(tab, text="🛠️ Инструменты")
        
        # System tools
        frame1 = tk.LabelFrame(tab, text=" ⚙️ Системные утилиты", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame1.pack(fill="x", padx=10, pady=10)
        
        tools = [
            ("🎛️ Панель управления", "control"),
            ("🔧 Диспетчер устройств", "devmgmt.msc"),
            ("💾 Управление дисками", "diskmgmt.msc"),
            ("🌐 Сетевые подключения", "ncpa.cpl"),
            ("🖥️ Параметры системы", "sysdm.cpl"),
            ("🔍 Службы", "services.msc"),
            ("📊 Монитор ресурсов", "perfmon"),
            ("🗑️ Очистка диска", "cleanmgr")
        ]
        
        for i in range(0, len(tools), 2):
            btn_frame = tk.Frame(frame1, bg="#1e1e2e")
            btn_frame.pack(fill="x", pady=3)
            
            for j in range(2):
                if i + j < len(tools):
                    text, command = tools[i + j]
                    ModernButton(btn_frame, text=text, color="#95a5a6", width=180,
                                command=lambda cmd=command: self.open_system_tool(cmd)).pack(side="left", padx=5, expand=True)
        
        # Quick actions
        frame2 = tk.LabelFrame(tab, text=" ⚡ Быстрые действия", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame2.pack(fill="x", padx=10, pady=10)
        
        actions = [
            ("🔄 Перезапустить проводник", self.restart_explorer),
            ("📋 Буфер обмена", "clipbrd"),
            ("🎮 Игровой режим", "gamebar"),
            ("📷 Снимок экрана", "snippingtool")
        ]
        
        for i in range(0, len(actions), 2):
            btn_frame = tk.Frame(frame2, bg="#1e1e2e")
            btn_frame.pack(fill="x", pady=3)
            
            for j in range(2):
                if i + j < len(actions):
                    text, command = actions[i + j]
                    if isinstance(command, str):
                        ModernButton(btn_frame, text=text, color="#9b59b6", width=180,
                                    command=lambda cmd=command: self.open_system_tool(cmd)).pack(side="left", padx=5, expand=True)
                    else:
                        ModernButton(btn_frame, text=text, color="#9b59b6", width=180,
                                    command=command).pack(side="left", padx=5, expand=True)
    
    def create_advanced_tab(self):
        tab = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(tab, text="🔧 Дополнительно")
        
        # System info
        frame1 = tk.LabelFrame(tab, text=" ℹ️ Информация о системе", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame1.pack(fill="x", padx=10, pady=10)
        
        info_btn_frame = tk.Frame(frame1, bg="#1e1e2e")
        info_btn_frame.pack(pady=5)
        
        ModernButton(info_btn_frame, text="Показать информацию", color="#3498db",
                    command=self.show_system_info).pack(pady=5)
        
        # Advanced tools
        frame2 = tk.LabelFrame(tab, text=" 🛠️ Расширенные инструменты", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame2.pack(fill="x", padx=10, pady=10)
        
        advanced_tools = [
            ("📝 Редактор реестра", "regedit"),
            ("🔐 Локальные политики", "secpol.msc"),
            ("🖥️ Конфигурация системы", "msconfig"),
            ("📡 Диагностика памяти", "mdsched")
        ]
        
        for tool in advanced_tools:
            ModernButton(frame2, text=tool[0], color="#e74c3c",
                        command=lambda cmd=tool[1]: self.open_system_tool(cmd)).pack(pady=3)
        
        # Quick commands
        frame3 = tk.LabelFrame(tab, text=" ⌨️ Быстрые команды", font=("Segoe UI", 12, "bold"),
                              fg="white", bg="#1e1e2e", relief="flat", bd=1)
        frame3.pack(fill="x", padx=10, pady=10)
        
        commands = [
            ("📊 Диспетчер задач", "taskmgr"),
            ("🎮 DirectX", "dxdiag"),
            ("🔧 Управление компьютером", "compmgmt.msc"),
            ("📋 Просмотр событий", "eventvwr")
        ]
        
        for i in range(0, len(commands), 2):
            btn_frame = tk.Frame(frame3, bg="#1e1e2e")
            btn_frame.pack(fill="x", pady=3)
            
            for j in range(2):
                if i + j < len(commands):
                    text, command = commands[i + j]
                    ModernButton(btn_frame, text=text, color="#f39c12", width=180,
                                command=lambda cmd=command: self.open_system_tool(cmd)).pack(side="left", padx=5, expand=True)
    
    def load_timezones(self):
        self.russian_timezones = [
            "Europe/Kaliningrad (Калининград, UTC+2)",
            "Europe/Moscow (Москва, Санкт-Петербург, UTC+3)",
            "Europe/Samara (Самара, UTC+4)",
            "Asia/Yekaterinburg (Екатеринбург, UTC+5)",
            "Asia/Omsk (Омск, UTC+6)",
            "Asia/Krasnoyarsk (Красноярск, UTC+7)",
            "Asia/Irkutsk (Иркутск, UTC+8)",
            "Asia/Chita (Чита, UTC+9)",
            "Asia/Vladivostok (Владивосток, UTC+10)",
            "Asia/Magadan (Магадан, UTC+11)",
            "Asia/Kamchatka (Петропавловск-Камчатский, UTC+12)"
        ]
    
    def filter_timezones(self, *args):
        search_term = self.search_var.get().lower()
        self.timezone_listbox.delete(0, tk.END)
        
        for tz in self.russian_timezones:
            if search_term in tz.lower():
                self.timezone_listbox.insert(tk.END, tz)
    
    def change_theme(self):
        theme = self.theme_var.get()
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 
                                0, winreg.KEY_WRITE)
            
            if theme == "Тёмная":
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
            else:
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 1)
                
            winreg.CloseKey(key)
            messagebox.showinfo("Успех", f"Тема изменена на {theme.lower()}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить тему: {str(e)}")
    
    def remove_watermark(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Control Panel\Desktop", 
                                0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "PaintDesktopVersion", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False)
            subprocess.run(["explorer.exe"], check=False)
            
            messagebox.showinfo("Успех", "Водяной знак должен быть удален. Перезапустите проводник.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить водяной знак: {str(e)}")
    
    def set_performance(self):
        setting = self.performance_var.get()
        try:
            if setting == "Наилучший вид":
                subprocess.run(['powershell', 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name VisualSetting -Value 2'], check=True)
            elif setting == "Наилучшее быстродействие":
                subprocess.run(['powershell', 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name VisualSetting -Value 1'], check=True)
            else:
                subprocess.run(['powershell', 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name VisualSetting -Value 0'], check=True)
            
            messagebox.showinfo("Успех", f"Настройки производительности изменены на: {setting}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить настройки: {str(e)}")
    
    def hide_desktop_icons(self):
        try:
            subprocess.run(['powershell', 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name HideIcons -Value 1'], check=True)
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False)
            subprocess.run(["explorer.exe"], check=False)
            messagebox.showinfo("Успех", "Значки на рабочем столе скрыты")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скрыть значки: {str(e)}")
    
    def show_desktop_icons(self):
        try:
            subprocess.run(['powershell', 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name HideIcons -Value 0'], check=True)
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False)
            subprocess.run(["explorer.exe"], check=False)
            messagebox.showinfo("Успех", "Значки на рабочем столе показаны")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось показать значки: {str(e)}")
    
    def center_taskbar_icons(self):
        try:
            subprocess.run(['powershell', 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name TaskbarAl -Value 1'], check=True)
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False)
            subprocess.run(["explorer.exe"], check=False)
            messagebox.showinfo("Успех", "Значки на панели задач выровнены по центру")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить выравнивание: {str(e)}")
    
    def set_shutdown_timer(self):
        time_val = self.shutdown_var.get()
        
        if time_val == "0":
            custom_time = simpledialog.askinteger("Свое значение", "Введите время в минутах:", minvalue=1, maxvalue=1440)
            if custom_time:
                time_val = custom_time
            else:
                return
        
        try:
            seconds = int(time_val) * 60
            subprocess.run(['shutdown', '/s', '/t', str(seconds)], check=True)
            messagebox.showinfo("Таймер установлен", f"Компьютер выключится через {time_val} минут")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить таймер: {str(e)}")
    
    def cancel_shutdown(self):
        try:
            subprocess.run(['shutdown', '/a'], check=True)
            messagebox.showinfo("Отменено", "Запланированное выключение отменено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отменить выключение: {str(e)}")
    
    def set_timezone(self):
        selection = self.timezone_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите часовой пояс из списка")
            return
        
        selected_tz = self.timezone_listbox.get(selection[0])
        tz_id = selected_tz.split(' ')[0]
        
        try:
            subprocess.run(['tzutil', '/s', tz_id], check=True, shell=True)
            messagebox.showinfo("Успех", f"Часовой пояс изменен на: {selected_tz}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить часовой пояс. Запустите программу от имени администратора. Ошибка: {str(e)}")
    
    def open_system_tool(self, tool_command):
        try:
            subprocess.Popen(tool_command, shell=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть {tool_command}: {str(e)}")
    
    def restart_explorer(self):
        try:
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False)
            subprocess.run(["explorer.exe"], check=False)
            messagebox.showinfo("Успех", "Проводник перезапущен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось перезапустить проводник: {str(e)}")
    
    def show_system_info(self):
        try:
            info = subprocess.check_output('systeminfo', shell=True, text=True, encoding='cp866')
            # Create info window
            info_window = tk.Toplevel(self.root)
            info_window.title("Информация о системе")
            info_window.geometry("800x600")
            info_window.configure(bg="#1e1e2e")
            
            text_widget = tk.Text(info_window, bg="#2c2c3b", fg="white", font=("Consolas", 9))
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            text_widget.insert("1.0", info)
            text_widget.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о системе: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemTweaker(root)
    root.mainloop()