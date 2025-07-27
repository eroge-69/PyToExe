import tkinter as tk
root = tk.Tk()
root.title("A")
root.attributes('-fullscreen', True)
def create_windows():
    for _ in range(10000):
        win = tk.Toplevel(root)
        win.title("A")
        win.attributes('-fullscreen', True)
create_windows()
root.mainloop() 