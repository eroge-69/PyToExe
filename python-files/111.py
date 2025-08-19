import tkinter as tk
from threading import Thread, Event
from pynput.keyboard import Controller, Key, Listener
import time

keyboard = Controller()
stop_event = Event()
pause_event = Event()

# начальные значения интервалов
intervals = {
    "wait_after_alt": 10,
    "hold_space": 1,
    "wait_after_enter": 6
}

def press_keys():
    while not stop_event.is_set():
        if pause_event.is_set():
            time.sleep(0.1)
            continue

        # ALT
        keyboard.press(Key.alt)
        keyboard.release(Key.alt)
        time.sleep(intervals["wait_after_alt"])

        # SPACE (зажатие)
        keyboard.press(Key.space)
        time.sleep(intervals["hold_space"])
        keyboard.release(Key.space)

        # ENTER
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

        time.sleep(intervals["wait_after_enter"])

def on_press(key):
    try:
        # проверка по vk-коду (Ё)
        if hasattr(key, "vk") and key.vk in (192, 223):
            if pause_event.is_set():
                pause_event.clear()
                print("▶ Продолжение")
            else:
                pause_event.set()
                print("⏸ Пауза")
    except Exception as e:
        print("Ошибка:", e)

def start_listener():
    with Listener(on_press=on_press) as listener:
        listener.join()

def update_intervals():
    try:
        intervals["wait_after_alt"] = float(entry_alt.get())
        intervals["hold_space"] = float(entry_space.get())
        intervals["wait_after_enter"] = float(entry_enter.get())
    except ValueError:
        pass

# --- GUI ---
root = tk.Tk()
root.title("Автокликер клавиш")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Пауза после ALT (сек)").grid(row=0, column=0, sticky="w")
entry_alt = tk.Entry(frame)
entry_alt.insert(0, str(intervals["wait_after_alt"]))
entry_alt.grid(row=0, column=1)

tk.Label(frame, text="Зажатие SPACE (сек)").grid(row=1, column=0, sticky="w")
entry_space = tk.Entry(frame)
entry_space.insert(0, str(intervals["hold_space"]))
entry_space.grid(row=1, column=1)

tk.Label(frame, text="Пауза после ENTER (сек)").grid(row=2, column=0, sticky="w")
entry_enter = tk.Entry(frame)
entry_enter.insert(0, str(intervals["wait_after_enter"]))
entry_enter.grid(row=2, column=1)

update_btn = tk.Button(frame, text="Обновить интервалы", command=update_intervals)
update_btn.grid(row=3, column=0, columnspan=2, pady=5)

# запуск фоновых потоков
thread = Thread(target=press_keys, daemon=True)
thread.start()
listener_thread = Thread(target=start_listener, daemon=True)
listener_thread.start()

root.protocol("WM_DELETE_WINDOW", lambda: (stop_event.set(), root.destroy()))
root.mainloop()