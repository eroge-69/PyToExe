import tkinter as tk
import random
import time
import threading
import os
import ctypes
import sys
from PIL import Image, ImageTk
import winsound

# ===================== 1. Фейковый античит =====================
def fake_scan():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("NIKKE ANTI-CHEAT")
    root.configure(bg="black")

    # Логотип Nikke (можно добавить картинку)
    logo = tk.Label(
        root,
        text="NIKKE: GODDESS OF VICTORY",
        font=("Arial", 30, "bold"),
        fg="#FF00FF",
        bg="black"
    )
    logo.pack(pady=20)

    # Сообщение о блокировке
    alert = tk.Label(
        root,
        text="⛔ ВАШ АККАУНТ ЗАБЛОКИРОВАН!\nОбнаружены читы!",
        font=("Arial", 25),
        fg="red",
        bg="black"
    )
    alert.pack(pady=10)

    # Фейковый прогресс-бар сканирования
    scan_frame = tk.Frame(root, bg="black")
    scan_frame.pack(pady=20)

    tk.Label(
        scan_frame,
        text="Сканирование системы...",
        font=("Arial", 14),
        fg="white",
        bg="black"
    ).pack()

    progress = tk.Canvas(scan_frame, width=500, height=20, bg="gray")
    progress.pack(pady=10)

    # Лог "найденных" файлов
    log = tk.Text(
        root,
        width=70,
        height=12,
        bg="black",
        fg="#00FF00",
        font=("Consolas", 10)
    )
    log.pack(pady=10)

    # Симулируем сканирование
    def scan_system():
        files = [
            "Nikke.exe (HACK: SPEEDHACK)",
            "d3d11.dll (CHEAT ENGINE)",
            "config.ini (MODIFIED)",
            "save.dat (CORRUPTED)"
        ]

        for i in range(101):
            progress.delete("all")
            progress.create_rectangle(0, 0, 5 * i, 20, fill="#FF0000")
            root.update()
            time.sleep(0.05)

        for file in files:
            log.insert(tk.END, f"[!] Найден вредоносный файл: {file}\n")
            time.sleep(0.7)
            root.update()

        log.insert(tk.END, "\n[CRITICAL] Игра будет удалена через 10 секунд!\n")
        time.sleep(3)
        root.destroy()

    threading.Thread(target=scan_system).start()
    root.mainloop()

# ===================== 2. Фейковое удаление игры =====================
def fake_deletion():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("NIKKE UNINSTALL")
    root.configure(bg="black")

    # Стиль командной строки
    log = tk.Text(
        root,
        width=90,
        height=25,
        bg="black",
        fg="#00FF00",
        font=("Consolas", 12),
        insertbackground="green"
    )
    log.pack(pady=10)

    # Эффект печатающегося текста
    def type_effect(text, delay=0.05):
        for char in text:
            log.insert(tk.END, char)
            log.see(tk.END)
            root.update()
            time.sleep(delay)

    # Симулируем удаление
    def delete_files():
        type_effect("C:\\Nikke> UNINSTALL /FORCE\n\n")
        time.sleep(1)

        files = [
            "Удаление Nikke.exe...",
            "Удаление игровых данных...",
            "Очистка кэша...",
            "Удаление сохранений...",
            "Стирание следов взлома..."
        ]

        for file in files:
            type_effect(f"> {file}\n")
            time.sleep(random.uniform(0.5, 1.5))
            type_effect("[УСПЕШНО]\n\n")

        type_effect("\n> Игра полностью удалена!\n")
        type_effect("> Ваш аккаунт заблокирован на 30 дней.\n")
        time.sleep(3)
        root.destroy()

    threading.Thread(target=delete_files).start()
    root.mainloop()

# ===================== 3. Глюки системы =====================
def system_glitches():
    # 1. Случайные звуки ошибок
    def play_sounds():
        for _ in range(5):
            time.sleep(random.randint(10, 30))
            winsound.Beep(1000, 500)

    # 2. Дёргание курсора
    def mouse_jitter():
        while True:
            x, y = ctypes.windll.user32.GetCursorPos()
            ctypes.windll.user32.SetCursorPos(
                x + random.randint(-50, 50),
                y + random.randint(-50, 50)
            )
            time.sleep(0.1)

    # 3. Мерцание экрана
    def screen_flicker():
        for _ in range(10):
            root = tk.Tk()
            root.attributes("-fullscreen", True)
            root.configure(bg="red")
            root.after(100, root.destroy)
            root.mainloop()
            time.sleep(0.5)

    threading.Thread(target=play_sounds, daemon=True).start()
    threading.Thread(target=mouse_jitter, daemon=True).start()
    threading.Thread(target=screen_flicker, daemon=True).start()

# ===================== 4. Синий экран смерти =====================
def fake_bsod():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="#0078D7")

    error_msg = """
    :( Ваш компьютер был заблокирован
    из-за нарушения лицензии NIKKE.

    Код ошибки: 0xNIKKE_BAN
    Свяжитесь с поддержкой: support@nikke.com
    """

    tk.Label(
        root,
        text=error_msg,
        font=("Arial", 24),
        fg="white",
        bg="#0078D7",
        justify="left"
    ).pack(pady=100)

    root.after(5000, root.destroy)
    root.mainloop()

# ===================== 5. Запуск всего сценария =====================
if __name__ == "__main__":
    fake_scan()          # 1. Сканирование
    fake_deletion()      # 2. Удаление
    system_glitches()    # 3. Глюки
    fake_bsod()          # 4. Синий экран

    # Разоблачение через 5 минут
    time.sleep(300)
    ctypes.windll.user32.MessageBoxW(0, "ЭТО БЫЛ РОЗЫГРЫШ, ЛОЛ 😝", "NIKKE PRANK", 0x40)