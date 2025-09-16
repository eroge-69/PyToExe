import tkinter as tk
from tkinter import messagebox
import random
import threading
import time
import keyboard
import sys
import os

# --- Проверка зависимостей ---
try:
    from PIL import ImageGrab, ImageTk, Image
    import pyautogui
except ImportError:
    root_err = tk.Tk()
    root_err.withdraw()
    messagebox.showerror("❌ Ошибка", "Не установлены зависимости!\n\nЗапусти в терминале:\npip install pyautogui pillow keyboard")
    sys.exit(1)

# --- GUI Предупреждения ---
def show_warning(title, message):
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    result = messagebox.askyesno(title, message)
    root.destroy()
    return result

# Первое предупреждение
if not show_warning(
    "⚠️ ПРЕДУПРЕЖДЕНИЕ 1/2",
    "Этот скрипт создаст экстремальную нагрузку на систему:\n"
    "- 50 окон\n- 150 движений курсора\n- Инверсия экрана\n- Смена обоев\n\n"
    "РАЗРЕШИТЬ ЗАПУСК?\n(Рекомендуется только в ВМ!)"
):
    sys.exit(0)

# Второе предупреждение — разрешение на системные изменения
allow_real_changes = show_warning(
    "🚨 ПРЕДУПРЕЖДЕНИЕ 2/2 — ВАЖНО!",
    "РАЗРЕШИТЬ РЕАЛЬНЫЕ СИСТЕМНЫЕ ИЗМЕНЕНИЯ?\n"
    "• Управление курсором\n• Инверсия экрана\n• Установка обоев\n\n"
    "❗ Работает ТОЛЬКО в Виртуальной Машине с откатом (snapshot) ❗\n\n"
    "Если откажешь — будет только визуальный эффект внутри окон."
)

# Флаг для остановки
running = True

# Обработчик F10
def stop_on_f10():
    global running
    while running:
        if keyboard.is_pressed('F10'):
            print("\n🛑 F10 нажат — остановка...")
            running = False
            break
        time.sleep(0.1)

threading.Thread(target=stop_on_f10, daemon=True).start()

# Главное окно управления
main_root = tk.Tk()
main_root.title("🧪 VM STRESS TEST — НЕ ЗАКРЫВАТЬ")
main_root.geometry("350x180+50+50")
main_root.configure(bg="#111")
tk.Label(
    main_root,
    text="ТЕСТ ЗАПУЩЕН\nНажмите F10 для остановки",
    font=("Consolas", 14),
    fg="#0f0",
    bg="#111"
).pack(expand=True, pady=20)

# Создание 50 окон
windows = []
for i in range(50):
    win = tk.Toplevel() if i > 0 else main_root
    win.title(f"Окно {i+1}")
    win.geometry(f"150x80+{random.randint(0, 800)}+{random.randint(0, 600)}")
    label = tk.Label(win, text="⚠️ VM TEST", font=("Arial", 8), bg="#222", fg="white")
    label.pack(expand=True)
    windows.append(win)
    if i == 0:
        main_root = win

# Движение курсоров (и системного, если разрешено)
def move_all_cursors():
    screen_width, screen_height = pyautogui.size() if allow_real_changes else (1920, 1080)
    while running:
        for _ in range(150):  # 150 "движений"
            x = random.randint(0, screen_width - 1)
            y = random.randint(0, screen_height - 1)
            if allow_real_changes:
                try:
                    pyautogui.moveTo(x, y, duration=0.005)
                except:
                    pass
            time.sleep(0.001)
        time.sleep(0.1)

# Инверсия экрана каждые 0.05с (если разрешено)
def invert_screen():
    if not allow_real_changes:
        return
    while running:
        try:
            # Windows: включить сочетание в "Специальных возможностях" → Ctrl+Alt+I
            pyautogui.hotkey('ctrl', 'alt', 'i')
        except:
            pass
        time.sleep(0.05)

# Установка обоев каждые 0.5с (если разрешено)
def set_wallpaper_loop():
    if not allow_real_changes:
        return

    temp_dir = os.path.join(os.getcwd(), "temp_wallpapers")
    os.makedirs(temp_dir, exist_ok=True)

    i = 0
    while running:
        try:
            screenshot = pyautogui.screenshot()
            path = os.path.join(temp_dir, f"wall_{i % 5}.png")
            screenshot.save(path)

            # Только Windows
            if os.name == 'nt':
                import ctypes
                ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        except Exception as e:
            print(f"[Обои] Ошибка: {e}")
        time.sleep(0.5)

# Фейковая инверсия (если системная не разрешена)
def fake_invert():
    colors = ["#000", "#fff", "#f00", "#0f0", "#00f", "#ff0", "#0ff", "#f0f", "#888", "#222"]
    while running:
        color = random.choice(colors)
        for win in windows:
            try:
                win.config(bg=color)
                for child in win.winfo_children():
                    child.config(bg=color)
            except:
                pass
        time.sleep(0.05)

# Запуск потоков
if allow_real_changes:
    threading.Thread(target=move_all_cursors, daemon=True).start()
    threading.Thread(target=invert_screen, daemon=True).start()
    threading.Thread(target=set_wallpaper_loop, daemon=True).start()

threading.Thread(target=fake_invert, daemon=True).start()

# Закрытие по F10
def check_stop():
    if not running:
        for win in windows:
            try:
                win.destroy()
            except:
                pass
        sys.exit(0)
    main_root.after(100, check_stop)

main_root.after(100, check_stop)

# Сообщение в консоль (если кто-то смотрит)
print("✅ Тест запущен! Для остановки нажмите F10.")

# Запуск GUI
try:
    main_root.mainloop()
except KeyboardInterrupt:
    pass