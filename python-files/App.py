import tkinter as tk
from collections import deque

active_windows = deque()


def open_new_window(parent_window=None):
    window = tk.Toplevel(parent_window) if parent_window else tk.Tk()
    window.title("pwnd by the crucifix")

    label = tk.Label(window, text="discord.gg/crucifixion", padx=20, pady=20)
    label.pack()

    active_windows.append(window)

    window.protocol("WM_DELETE_WINDOW", lambda: on_window_close(window))

    return window

def on_window_close(window_to_close):
    window_to_close.destroy()

    for i, win in enumerate(active_windows):
        if win == window_to_close:
            del active_windows[i]
            break

    open_new_window()


def main():
    initial_window = open_new_window()
    initial_window.title("pwnd noob")

    initial_window.mainloop()

if __name__ == "__main__":
    main()