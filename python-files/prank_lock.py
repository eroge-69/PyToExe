# prank_lock.py
# Реалистичный безопасный пранк "винлокер" — имитация экрана блокировки.
# Пароль для разблокировки: 1234567890
# Запуск: python prank_lock.py
# Внимание: используйте только на своих машинах или с разрешения владельца.

import tkinter as tk
from tkinter import font, messagebox
import time
import getpass
import threading

PASSWORD = "1234567890"   # пароль для разблокировки

def update_time():
    while True:
        try:
            now = time.strftime("%H:%M")
            date = time.strftime("%A, %d %B %Y")
            time_label.config(text=now)
            date_label.config(text=date)
            time.sleep(1)
        except tk.TclError:
            break  # окно закрыто

def try_unlock(event=None):
    entered = entry.get()
    if entered == PASSWORD:
        # мягкое разблокирование
        root.destroy()
    else:
        # "shake" эффект и сообщение
        shake_window()
        entry.delete(0, tk.END)
        # краткое уведомление
        error_label.config(text="Неверный пароль", fg="#ff6b6b")
        root.after(1500, lambda: error_label.config(text=""))

def shake_window():
    # небольшой эффект дрожания окна
    x = root.winfo_x()
    y = root.winfo_y()
    for dx in (-20, 20, -12, 12, -6, 6, 0):
        root.geometry(f"+{x+dx}+{y}")
        root.update()
        time.sleep(0.02)

def on_close():
    # блокируем закрытие через крестик (Alt+F4 будет тоже вызывать это)
    pass

def allow_quit_backdoor(event=None):
    # Секретная комбинация для автора: Ctrl+Shift+Q — аварийно закрыть.
    # Оставь или удали по желанию. Я рекомендую оставить, если будешь демонстрировать пранк.
    root.destroy()

# Создаём окно
root = tk.Tk()
root.title("Windows")
root.attributes("-fullscreen", True)   # полноэкранный режим
root.attributes("-topmost", True)      # поверх всех окон
root.configure(background="#0b0b0b")
root.protocol("WM_DELETE_WINDOW", on_close)

# Получаем имя пользователя для реалистичности
username = getpass.getuser()

# Центрированный фрейм с контентом
frame = tk.Frame(root, bg="#0b0b0b")
frame.pack(expand=True)

# Шрифты
time_font = font.Font(family="Segoe UI", size=96, weight="bold")
date_font = font.Font(family="Segoe UI", size=20)
user_font = font.Font(family="Segoe UI", size=24)
entry_font = font.Font(family="Segoe UI", size=16)

# Метки времени и даты
time_label = tk.Label(frame, text="", fg="white", bg="#0b0b0b", font=time_font)
time_label.pack(pady=(50, 0))

date_label = tk.Label(frame, text="", fg="#cfcfcf", bg="#0b0b0b", font=date_font)
date_label.pack(pady=(5, 40))

# Инфо о пользователе
user_label = tk.Label(frame, text=username, fg="white", bg="#0b0b0b", font=user_font)
user_label.pack(pady=(0,20))

# Поле ввода пароля (без видимого кнопочного интерфейса)
entry = tk.Entry(frame, show="*", font=entry_font, justify="center", width=30)
entry.pack(pady=(0,10))
entry.focus_set()

# Подсказка
hint = tk.Label(frame, text="Введите пароль для разблокировки", fg="#bfbfbf", bg="#0b0b0b")
hint.pack()

error_label = tk.Label(frame, text="", fg="#ff6b6b", bg="#0b0b0b", font=date_font)
error_label.pack(pady=(10,0))

# Привязка Enter для проверки пароля
root.bind("<Return>", try_unlock)

# Скрытие курсора внутри окна для реалистичности (можно закомментировать)
root.config(cursor="none")

# Секретная аварийная комбинация: Ctrl+Shift+Q (комментарий: можно убрать или заменить)
root.bind("<Control-Shift-KeyPress-Q>", allow_quit_backdoor)

# Запускаем поток обновления времени чтобы интерфейс не блокировался
t = threading.Thread(target=update_time, daemon=True)
t.start()

# Инструктивный текст внизу (маленький) — для предотвращения реального вреда
small = tk.Label(root, text="Это безопасная имитация — для выхода введите пароль или завершите процесс через Диспетчер задач.",
                 fg="#6f6f6f", bg="#0b0b0b", font=("Segoe UI", 9))
small.pack(side="bottom", pady=10)

root.mainloop()
