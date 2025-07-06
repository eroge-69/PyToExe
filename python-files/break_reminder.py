
from tkinter import Tk, Label
import time
import threading
import ctypes
import sys

def block_input():
    ctypes.windll.user32.BlockInput(True)

def unblock_input():
    ctypes.windll.user32.BlockInput(False)

def show_break_screen(duration=120):
    root = Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    root.attributes('-topmost', True)
    root.overrideredirect(True)

    label = Label(root, text="BREAK\nDrink Water 💧", fg="white", bg="black", font=("Helvetica", 50), justify='center')
    label.pack(expand=True)

    countdown_label = Label(root, text="", fg="white", bg="black", font=("Helvetica", 40))
    countdown_label.pack()

    def update_countdown():
        for i in range(duration, 0, -1):
            countdown_label.config(text=f"Remaining: {i//60}:{i%60:02d}")
            root.update()
            time.sleep(1)
        root.destroy()

    block_input()
    threading.Thread(target=update_countdown).start()
    root.mainloop()
    unblock_input()

def start_cycle(work_duration=1800, break_duration=120):
    while True:
        time.sleep(work_duration)
        show_break_screen(break_duration)

if __name__ == "__main__":
    try:
        threading.Thread(target=start_cycle, daemon=True).start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        unblock_input()
        sys.exit(0)
