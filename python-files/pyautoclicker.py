import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Controller, Key, Listener
import threading
import time
import string

keyboard = Controller()
running = False
pressed_keys = set()

# Все поддерживаемые клавиши
available_keys = {}

# Добавим буквы a-z
for char in string.ascii_lowercase:
    available_keys[char.upper()] = char

# Добавим цифры 0–9
for i in range(10):
    available_keys[str(i)] = str(i)

# F1–F12
for i in range(1, 13):
    available_keys[f"F{i}"] = getattr(Key, f"f{i}")

# Специальные клавиши
special_keys = {
    "Space": Key.space,
    "Enter": Key.enter,
    "Esc": Key.esc,
    "Tab": Key.tab,
    "Backspace": Key.backspace,
    "Shift": Key.shift,
    "Ctrl": Key.ctrl,
    "Alt": Key.alt,
    "CapsLock": Key.caps_lock,
    "Insert": Key.insert,
    "Delete": Key.delete,
    "Home": Key.home,
    "End": Key.end,
    "PageUp": Key.page_up,
    "PageDown": Key.page_down,
    "Left": Key.left,
    "Right": Key.right,
    "Up": Key.up,
    "Down": Key.down,
    "NumLock": Key.num_lock,
    "PrintScreen": Key.print_screen,
    "ScrollLock": Key.scroll_lock,
    "Pause": Key.pause,
    "`": '`',
    "-": '-',
    "=": '=',
    "[": '[',
    "]": ']',
    "\\": '\\',
    ";": ';',
    "'": "'",
    ",": ',',
    ".": '.',
    "/": '/',
}

available_keys.update(special_keys)

# GUI
root = tk.Tk()
root.title("Нажиматель кнопок")
root.geometry("300x250")

key_var = tk.StringVar(value="F")
delay_var = tk.StringVar(value="1.0")

def press_key_loop(key, delay):
    global running
    while running:
        keyboard.press(key)
        keyboard.release(key)
        time.sleep(delay)

def start_pressing():
    global running
    if running:
        return
    running = True
    selected = key_var.get()
    delay = float(delay_var.get())
    key = available_keys.get(selected)
    if key:
        threading.Thread(target=press_key_loop, args=(key, delay), daemon=True).start()

def stop_pressing():
    global running
    running = False

def toggle_running():
    if running:
        stop_pressing()
        print("[Ctrl+F8] ⛔ Остановлено")
    else:
        start_pressing()
        print("[Ctrl+F8] ✅ Запущено")

# Глобальное сочетание Ctrl + F8
def on_press(key):
    try:
        if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            pressed_keys.add('ctrl')
        elif key == Key.f8:
            pressed_keys.add('f8')

        if 'ctrl' in pressed_keys and 'f8' in pressed_keys:
            toggle_running()
            pressed_keys.clear()
    except:
        pass

def on_release(key):
    try:
        if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            pressed_keys.discard('ctrl')
        elif key == Key.f8:
            pressed_keys.discard('f8')
    except:
        pass

listener = Listener(on_press=on_press, on_release=on_release)
listener.daemon = True
listener.start()

# GUI элементы
ttk.Label(root, text="Выбери кнопку:").pack(pady=5)
ttk.Combobox(root, textvariable=key_var, values=list(available_keys.keys())).pack()

ttk.Label(root, text="Кулдаун (сек):").pack(pady=5)
ttk.Entry(root, textvariable=delay_var).pack()

ttk.Button(root, text="Старт", command=start_pressing).pack(pady=10)
ttk.Button(root, text="Стоп", command=stop_pressing).pack()

ttk.Label(root, text="▶ Горячая клавиша: Ctrl + F8").pack(pady=5)

root.mainloop()
