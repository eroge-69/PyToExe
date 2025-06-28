import tkinter as tk
from threading import Thread, Event
from pynput.keyboard import Key, Controller
import time

class ShiftPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shift Key Presser")

        self.start_button = tk.Button(root, text="Start", command=self.start_pressing)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_pressing, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.running = Event()
        self.keyboard = Controller()

    def press_shift(self):
        while self.running.is_set():
            self.keyboard.press(Key.shift)
            self.keyboard.release(Key.shift)
            time.sleep(0.25)

    def start_pressing(self):
        self.running.set()
        self.thread = Thread(target=self.press_shift)
        self.thread.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_pressing(self):
        self.running.clear()
        self.thread.join()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShiftPresserApp(root)
    root.mainloop()