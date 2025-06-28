import tkinter as tk

# Настройки приложения
APP_TITLE = 'Windows Lock'
APP_ICON_PATH = None # Укажите путь к иконке, если хотите добавить её
CORRECT_PASSWORD = '5455'  # Пароль для разблокировки

class WinLocker(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(APP_TITLE)
        if APP_ICON_PATH is not None:
            self.iconbitmap(default=APP_ICON_PATH)
            
        self.geometry('300x150')
        self.resizable(False, False)
        
        # Полное закрытие окон Windows (без возможности закрыть крестиком или Alt+F4)
        self.overrideredirect(True)
        self.wm_attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.bind('<Alt-F4>', lambda e: None)
    
        # Основной интерфейс
        label = tk.Label(self, text="Введите пароль:", font=("Arial", 12))
        label.pack(pady=(20, 10))
        
        self.entry_password = tk.Entry(self, show='*', width=20)
        self.entry_password.pack()
        
        button_unlock = tk.Button(self, text="Разблокировать", command=self.unlock_screen)
        button_unlock.pack(pady=10)
        
        self.lock_screen()
    
    def lock_screen(self):
        """ Блокирует рабочий стол """
        self.focus_force()  # Заставляет окно получать фокус
        self.lift()  # Поднимает окно поверх всех остальных окон
        self.attributes("-fullscreen", True)  # Развернуть на весь экран
    
    def unlock_screen(self):
        """ Проверяет пароль и закрывает приложение, если правильный введен """
        password = self.entry_password.get().strip()
        if password == CORRECT_PASSWORD:
            self.destroy()
        else:
            self.bell()  # Звук предупреждения
            self.entry_password.delete(0, tk.END)

if __name__ == "__main__":
    app = WinLocker()
    app.mainloop()