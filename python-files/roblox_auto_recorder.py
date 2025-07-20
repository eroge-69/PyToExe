
import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import pyautogui
from pynput import mouse, keyboard

events = []
recording = False
playing = False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Auto Recorder for Roblox")
        self.root.geometry("360x300")
        self.root.resizable(False, False)

        self.create_widgets()
        self.listener_thread = threading.Thread(target=self.global_hotkeys)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def create_widgets(self):
        tk.Label(self.root, text="Горячие клавиши:", font=("Segoe UI", 10, "bold")).pack(pady=5)
        tk.Label(self.root, text="▶ Воспроизведение: F9
🎥 Запись: F8
⛔ Остановка: ESC", fg="#444").pack()

        tk.Label(self.root, text="Циклы воспроизведения:", font=("Segoe UI", 10, "bold")).pack(pady=(15, 0))
        self.cycles_entry = tk.Entry(self.root, width=10, justify='center')
        self.cycles_entry.insert(0, "1")
        self.cycles_entry.pack()

        self.status_label = tk.Label(self.root, text="Ожидание действия...", fg="blue")
        self.status_label.pack(pady=10)

        self.start_btn = tk.Button(self.root, text="▶ Воспроизвести", command=self.start_playback)
        self.start_btn.pack(pady=5)

        self.record_btn = tk.Button(self.root, text="🎥 Начать запись", command=self.start_recording)
        self.record_btn.pack(pady=5)

    def start_recording(self):
        threading.Thread(target=self.record).start()

    def start_playback(self):
        try:
            loops = self.cycles_entry.get()
            if loops.strip() == "":
                loops = 1
            elif loops.strip().lower() == "inf":
                loops = float('inf')
            else:
                loops = int(loops)
            threading.Thread(target=self.play, args=(loops,)).start()
        except:
            messagebox.showerror("Ошибка", "Введите корректное число циклов (например, 1, 5, или inf)")

    def record(self):
        global recording, events
        events = []
        recording = True
        start_time = time.time()
        self.status_label.config(text="🔴 Запись... Нажми ESC для остановки", fg="red")

        def on_click(x, y, button, pressed):
            if not recording:
                return False
            if button == mouse.Button.right:
                events.append({'type': 'rclick', 'pressed': pressed, 'time': time.time() - start_time})
            events.append({'type': 'click', 'x': x, 'y': y, 'button': str(button), 'pressed': pressed, 'time': time.time() - start_time})

        def on_move(x, y):
            if recording:
                events.append({'type': 'move', 'x': x, 'y': y, 'time': time.time() - start_time})

        def on_press(key):
            nonlocal recording
            if key == keyboard.Key.esc:
                recording = False
                return False
            if recording:
                events.append({'type': 'key', 'key': str(key), 'time': time.time() - start_time})

        with mouse.Listener(on_click=on_click, on_move=on_move) as ml,              keyboard.Listener(on_press=on_press) as kl:
            kl.join()

        with open('recording.json', 'w') as f:
            json.dump(events, f, indent=2)
        self.status_label.config(text="✅ Запись завершена", fg="green")

    def play(self, loops):
        global playing
        try:
            with open('recording.json', 'r') as f:
                actions = json.load(f)
        except FileNotFoundError:
            self.status_label.config(text="❌ Нет записанных действий", fg="red")
            return

        self.status_label.config(text="▶ Воспроизведение...", fg="blue")
        playing = True

        try:
            while playing and loops > 0:
                start_time = time.time()
                for event in actions:
                    if not playing:
                        break
                    wait_time = event['time'] - (time.time() - start_time)
                    if wait_time > 0:
                        time.sleep(wait_time)
                    if event['type'] == 'click' and event['pressed']:
                        pyautogui.click(x=event['x'], y=event['y'])
                    elif event['type'] == 'move':
                        pyautogui.moveTo(event['x'], event['y'], duration=0.01)
                    elif event['type'] == 'key':
                        key = event['key'].replace("'", "").replace("Key.", "")
                        pyautogui.press(key)
                    elif event['type'] == 'rclick' and event['pressed']:
                        pyautogui.mouseDown(button='right')
                    elif event['type'] == 'rclick' and not event['pressed']:
                        pyautogui.mouseUp(button='right')
                if isinstance(loops, int):
                    loops -= 1
        finally:
            self.status_label.config(text="✅ Воспроизведение завершено", fg="green")

    def global_hotkeys(self):
        def on_press(key):
            if key == keyboard.Key.f8:
                self.start_recording()
            elif key == keyboard.Key.f9:
                self.start_playback()
            elif key == keyboard.Key.esc:
                global recording, playing
                recording = False
                playing = False
                self.status_label.config(text="⛔ Остановлено", fg="orange")

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
