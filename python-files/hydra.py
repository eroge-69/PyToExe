import tkinter as tk

root = tk.Tk()
root.title("Main Window")
root.attributes('-fullscreen', True)

def create_windows():
    for _ in range(5):
        win = tk.Toplevel(root)
        win.title("BAHAHA BITCH")
        win.attributes('-fullscreen', True)

create_windows()
root.mainloop()