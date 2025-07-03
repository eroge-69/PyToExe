
import keyboard
import tkinter as tk
from threading import Thread

running = False
window = None

def toggle_fullscreen():
    global running, window

    if not running:
        running = True
        window = tk.Tk()
        window.attributes('-fullscreen', True)
        window.configure(bg='black')
        window.bind('<KeyPress-q>', lambda e: close_window())
        window.mainloop()
    else:
        close_window()

def close_window():
    global running, window
    if window:
        window.destroy()
    running = False

def listen_for_q():
    while True:
        keyboard.wait('q')
        toggle_fullscreen()

if __name__ == "__main__":
    listener = Thread(target=listen_for_q)
    listener.start()
