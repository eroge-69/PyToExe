import tkinter as tk
import webbrowser
import pythoncom
import pyHook
import threading
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer

# Скрываем окно
root = tk.Tk()
root.withdraw()  # Скрываем главное окно

# Переменные для отслеживания мыши
mouse_movement_count = 0
MOVEMENT_THRESHOLD = 1000  # Количество движений для активации
TARGET_URL = "https://example.com"  # Ваш URL

def on_mouse_move(event):
    global mouse_movement_count
    mouse_movement_count += 1
    
    if mouse_movement_count >= MOVEMENT_THRESHOLD:
        webbrowser.open(TARGET_URL)
        mouse_movement_count = 0  # Сброс счетчика
    
    return True

def start_hook():
    hm = pyHook.HookManager()
    hm.MouseAllButtonsDown = on_mouse_move
    hm.MouseAllButtonsUp = on_mouse_move
    hm.MouseAll = on_mouse_move
    hm.HookMouse()
    
    pythoncom.PumpMessages()

# Запуск в отдельном потоке
hook_thread = threading.Thread(target=start_hook)
hook_thread.daemon = True
hook_thread.start()

root.mainloop()