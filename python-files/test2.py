import tkinter as tk
from tkinter import messagebox
import sys
import os
import ctypes
import threading
import time
import json
import base64

class CodeVerificationApp:
    def __init__(self):
        # Админ код
        self.admin_code = "3225"
        
        # Загружаем сохраненные настройки
        self.load_settings()
        
        # Переменные для экстренной комбинации
        self.emergency_combo = "noyas"
        self.emergency_buffer = ""
        
        self.setup_ui()
        self.block_keyboard()
        
    def load_settings(self):
        """Загружает настройки из скрытого файла"""
        self.config_file = "system_lock.dat"
        self.make_file_hidden()
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.correct_code = config.get('correct_code', '0000')
                    self.bg_color = config.get('bg_color', '#1a1a1a')
            else:
                # Значения по умолчанию
                self.correct_code = "0000"
                self.bg_color = "#1a1a1a"
                self.save_settings()
                
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.correct_code = "0000"
            self.bg_color = "#1a1a1a"
    
    def save_settings(self):
        """Сохраняет настройки в скрытый файл"""
        try:
            config = {
                'correct_code': self.correct_code,
                'bg_color': self.bg_color
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.make_file_hidden()
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def make_file_hidden(self):
        """Делает файл скрытым используя Windows API"""
        try:
            if os.path.exists(self.config_file):
                # Устанавливаем скрытый атрибут через ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                FILE_ATTRIBUTE_SYSTEM = 0x04
                ctypes.windll.kernel32.SetFileAttributesW(self.config_file, 
                                                         FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
        except:
            pass
        
    def setup_ui(self):
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("System Lock")
        
        # Полноэкранный режим
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.geometry("{0}x{1}+0+0".format(
            self.root.winfo_screenwidth(), 
            self.root.winfo_screenheight()
        ))
        
        self.root.configure(bg=self.bg_color)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Переменные для виртуальной клавиатуры
        self.show_password = False
        
        # Создаем элементы интерфейса
        self.create_widgets()
        self.create_virtual_keyboard()
        
        # Запускаем мониторинг блокировки клавиш
        self.start_keyboard_monitor()
        self.start_emergency_combo_monitor()
        
    def create_widgets(self):
        # Основной контейнер
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.place(relx=0.5, rely=0.4, anchor='center')
        
        # Заголовок
        self.title_label = tk.Label(
            self.main_frame,
            text="СИСТЕМА ЗАБЛОКИРОВАНА", 
            font=("Arial", 24, "bold"),
            fg='#ff4444',
            bg=self.bg_color
        )
        self.title_label.pack(pady=(0, 30))
        
        # Метка с инструкцией
        self.instruction = tk.Label(
            self.main_frame, 
            text="Введите код безопасности для разблокировки системы:", 
            font=("Arial", 16),
            fg='white' if self.bg_color == '#1a1a1a' else 'black',
            bg=self.bg_color
        )
        self.instruction.pack(pady=10)
        
        # Поле для ввода кода
        self.code_entry = tk.Entry(
            self.main_frame, 
            font=("Arial", 20),
            show="●" if not self.show_password else "",
            justify='center',
            width=15,
            bg='#2b2b2b' if self.bg_color == '#1a1a1a' else '#f0f0f0',
            fg='white' if self.bg_color == '#1a1a1a' else 'black',
            borderwidth=2,
            relief='solid'
        )
        self.code_entry.pack(pady=20)
        
        # Привязываем Enter к проверке кода
        self.root.bind('<Return>', lambda event: self.verify_code())
        
    def create_virtual_keyboard(self):
        """Создает виртуальную клавиатуру"""
        keyboard_frame = tk.Frame(self.root, bg=self.bg_color)
        keyboard_frame.place(relx=0.5, rely=0.75, anchor='center')
        
        # Кнопки клавиатуры
        buttons = [
            '1', '2', '3',
            '4', '5', '6', 
            '7', '8', '9',
            'Show', '0', 'Del'
        ]
        
        row, col = 0, 0
        for i, button in enumerate(buttons):
            if i % 3 == 0 and i != 0:
                row += 1
                col = 0
            
            if button == 'Del':
                btn = tk.Button(
                    keyboard_frame,
                    text="DELETE",
                    font=("Arial", 12, "bold"),
                    command=self.delete_char,
                    bg='#f44336',
                    fg='white',
                    width=8,
                    height=2
                )
            elif button == 'Show':
                btn = tk.Button(
                    keyboard_frame,
                    text="SHOW",
                    font=("Arial", 12, "bold"),
                    command=self.toggle_password_visibility,
                    bg='#2196F3',
                    fg='white',
                    width=8,
                    height=2
                )
            else:
                btn = tk.Button(
                    keyboard_frame,
                    text=button,
                    font=("Arial", 14, "bold"),
                    command=lambda b=button: self.add_char(b),
                    bg='#555555',
                    fg='white',
                    width=8,
                    height=2
                )
            
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
    
    def add_char(self, char):
        """Добавляет символ в поле ввода"""
        self.code_entry.insert(tk.END, char)
    
    def delete_char(self):
        """Удаляет последний символ из поля ввода"""
        current_text = self.code_entry.get()
        if current_text:
            self.code_entry.delete(len(current_text)-1, tk.END)
    
    def toggle_password_visibility(self):
        """Переключает видимость пароля"""
        self.show_password = not self.show_password
        self.code_entry.config(show="" if self.show_password else "●")
        
    def block_keyboard(self):
        """Блокирует системные комбинации клавиш"""
        for key in ['<Alt-Key>', '<Win-Key>', '<Control-Escape>', '<Alt-F4>', 
                   '<Control-Alt-Delete>', '<Alt-Tab>', '<Control-Shift-Escape>', 
                   '<F11>', '<Escape>']:
            self.root.bind(key, lambda e: 'break')
        
    def start_keyboard_monitor(self):
        """Запускает поток для постоянной блокировки клавиш"""
        def monitor():
            while True:
                try:
                    user32 = ctypes.windll.user32
                    if user32.GetAsyncKeyState(0x12):  # VK_MENU (Alt)
                        user32.keybd_event(0x12, 0, 0x0002, 0)
                    if user32.GetAsyncKeyState(0x5B):  # VK_LWIN
                        user32.keybd_event(0x5B, 0, 0x0002, 0)
                    time.sleep(0.01)
                except:
                    pass
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def start_emergency_combo_monitor(self):
        """Запускает мониторинг экстренной комбинации клавиш"""
        def monitor_combo():
            while True:
                try:
                    user32 = ctypes.windll.user32
                    
                    # Проверяем каждую клавишу из комбинации
                    for key_char in "noyas":
                        key_code = ord(key_char.upper())
                        if user32.GetAsyncKeyState(key_code):
                            self.emergency_buffer += key_char
                            time.sleep(0.1)  # Небольшая задержка между нажатиями
                            
                            # Проверяем совпадение с комбинацией
                            if self.emergency_combo in self.emergency_buffer:
                                self.emergency_shutdown()
                                self.emergency_buffer = ""
                                break
                    
                    # Ограничиваем размер буфера
                    if len(self.emergency_buffer) > 10:
                        self.emergency_buffer = self.emergency_buffer[-10:]
                    
                    time.sleep(0.05)
                except:
                    pass
        
        combo_thread = threading.Thread(target=monitor_combo, daemon=True)
        combo_thread.start()
    
    def emergency_shutdown(self):
        """Экстренное отключение программы"""
        try:
            messagebox.showinfo("Экстренное отключение", 
                              "Программа будет экстренно отключена!\nКомбинация: noyas")
            self.root.destroy()
            sys.exit()
        except:
            os._exit(0)
        
    def verify_code(self):
        entered_code = self.code_entry.get().strip()
        
        if not entered_code:
            messagebox.showerror("Ошибка", "Поле ввода пустое! Введите код.")
            return
        
        if entered_code == self.correct_code:
            self.unlock_system()
        elif entered_code == self.admin_code:
            self.open_admin_panel()
        else:
            messagebox.showerror("Ошибка", "Неверный код! Система останется заблокированной.")
            self.code_entry.delete(0, tk.END)
    
    def unlock_system(self):
        """Разблокирует систему"""
        messagebox.showinfo("Успех", "Код верный! Система разблокирована.")
        self.root.destroy()
        sys.exit()
    
    def open_admin_panel(self):
        """Открывает админ-панель"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_admin_interface()
    
    def create_admin_interface(self):
        """Создает интерфейс админ-панели"""
        # Заголовок
        title_label = tk.Label(
            self.main_frame,
            text="АДМИН-ПАНЕЛЬ", 
            font=("Arial", 24, "bold"),
            fg='#4CAF50',
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # Текущий код
        current_code_label = tk.Label(
            self.main_frame,
            text=f"Текущий основной код: {self.correct_code}", 
            font=("Arial", 14),
            fg='white' if self.bg_color == '#1a1a1a' else 'black',
            bg=self.bg_color
        )
        current_code_label.pack(pady=10)
        
        # Поле для нового кода
        new_code_label = tk.Label(
            self.main_frame,
            text="Новый основной код:", 
            font=("Arial", 12),
            fg='white' if self.bg_color == '#1a1a1a' else 'black',
            bg=self.bg_color
        )
        new_code_label.pack(pady=10)
        
        self.new_code_entry = tk.Entry(
            self.main_frame, 
            font=("Arial", 16),
            justify='center',
            width=15,
            bg='#3b3b3b' if self.bg_color == '#1a1a1a' else '#ffffff',
            fg='white' if self.bg_color == '#1a1a1a' else 'black',
            borderwidth=2,
            relief='solid'
        )
        self.new_code_entry.pack(pady=10)
        self.new_code_entry.focus()
        
        # Выбор цвета фона
        color_label = tk.Label(
            self.main_frame,
            text="Цвет фона:", 
            font=("Arial", 12),
            fg='white' if self.bg_color == '#1a1a1a' else 'black',
            bg=self.bg_color
        )
        color_label.pack(pady=10)
        
        color_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        color_frame.pack(pady=5)
        
        colors = [
            ("Чёрный", "#1a1a1a"),
            ("Белый", "#ffffff"), 
            ("Синий", "#1a237e"),
            ("Красный", "#b71c1c")
        ]
        
        for color_name, color_code in colors:
            btn = tk.Button(
                color_frame,
                text=color_name,
                font=("Arial", 10),
                command=lambda c=color_code: self.change_bg_color(c),
                bg=color_code,
                fg='white' if color_code != '#ffffff' else 'black',
                width=8,
                padx=5
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для кнопок
        buttons_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        # Кнопка сохранения кода
        def save_new_code():
            new_code = self.new_code_entry.get().strip()
            if not new_code:
                messagebox.showerror("Ошибка", "Введите новый код!")
                return
            if len(new_code) < 4:
                messagebox.showerror("Ошибка", "Код должен содержать минимум 4 символа!")
                return
            
            self.correct_code = new_code
            self.save_settings()
            messagebox.showinfo("Успех", f"Основной код изменен на: {new_code}")
            self.return_to_main()
        
        save_button = tk.Button(
            buttons_frame,
            text="СОХРАНИТЬ КОД",
            font=("Arial", 10, "bold"),
            command=save_new_code,
            bg='#2196F3',
            fg='white',
            padx=15,
            pady=8
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сброса настроек
        def reset_to_default():
            if messagebox.askyesno("Подтверждение", "Сбросить все настройки по умолчанию?\nОсновной код будет: 0000\nЦвет фона: Чёрный"):
                self.correct_code = "0000"
                self.bg_color = "#1a1a1a"
                self.save_settings()
                messagebox.showinfo("Успех", "Настройки сброшены по умолчанию!")
                self.restart_interface()
        
        default_button = tk.Button(
            buttons_frame,
            text="ПО УМОЛЧАНИЮ", 
            font=("Arial", 10),
            command=reset_to_default,
            bg='#FF9800',
            fg='white',
            padx=15,
            pady=8
        )
        default_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка возврата
        return_button = tk.Button(
            buttons_frame,
            text="НАЗАД",
            font=("Arial", 10),
            command=self.return_to_main,
            bg='#757575',
            fg='white',
            padx=15,
            pady=8
        )
        return_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка закрытия программы
        close_button = tk.Button(
            buttons_frame,
            text="ЗАКРЫТЬ",
            font=("Arial", 10),
            command=self.close_program,
            bg='#f44336',
            fg='white',
            padx=15,
            pady=8
        )
        close_button.pack(side=tk.LEFT, padx=5)
        
        self.root.bind('<Return>', lambda event: save_new_code())
    
    def change_bg_color(self, color):
        """Изменяет цвет фона"""
        self.bg_color = color
        self.save_settings()
        self.restart_interface()
    
    def restart_interface(self):
        """Перезапускает интерфейс с новыми настройками"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
        self.create_virtual_keyboard()
    
    def close_program(self):
        """Закрывает программу"""
        if messagebox.askyesno("Подтверждение", "Закрыть программу?\nСистема будет разблокирована."):
            self.root.destroy()
            sys.exit()
    
    def return_to_main(self):
        """Возвращает основной интерфейс"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_widgets()
        self.root.bind('<Return>', lambda event: self.verify_code())
    
    def on_closing(self):
        pass
    
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def add_to_startup():
    """Добавляет программу в автозагрузку"""
    try:
        import winreg
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
            python_exe = sys.executable
            exe_path = f'"{python_exe}" "{exe_path}"'
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "SystemLock", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print("Программа добавлена в автозагрузку!")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    # add_to_startup()  # Раскомментировать для автозагрузки
    app = CodeVerificationApp()
    app.run()
