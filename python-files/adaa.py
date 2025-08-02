import tkinter as tk
import ctypes

# Make window always on top
def make_always_on_top(window):
    window.attributes("-topmost", True)
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    styles |= 0x00000080  # WS_EX_TOOLWINDOW
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles)

# Total Sale Injector
def create_injector_window():
    injector = tk.Tk()
    injector.title("Overlay Injector")
    injector.geometry("220x60+100+100")
    injector.configure(bg='blue')
    injector.overrideredirect(False)
    make_always_on_top(injector)

    tk.Label(injector, text="Total Sale:", bg="blue", fg="white", font=("Arial", 12)).place(x=10, y=10)
    sale_var = tk.StringVar()
    sale_var.set("000000.00")
    tk.Entry(injector, textvariable=sale_var, font=("Arial", 12), bg="white").place(x=100, y=10, width=100)
    return injector

# Blue Box for Minus Hiding
def create_blue_box():
    blue_box = tk.Tk()
    blue_box.title("Minus Hider")
    blue_box.geometry("20x20+400+100")
    blue_box.configure(bg='#000080')  # FINAL COLOR: Navy (#000080)
    blue_box.overrideredirect(True)
    make_always_on_top(blue_box)

    def start_move(event):
        blue_box.x = event.x
        blue_box.y = event.y

    def do_move(event):
        x = blue_box.winfo_pointerx() - blue_box.x
        y = blue_box.winfo_pointery() - blue_box.y
        blue_box.geometry(f"+{x}+{y}")

    blue_box.bind("<ButtonPress-1>", start_move)
    blue_box.bind("<B1-Motion>", do_move)

    return blue_box

# Launch both windows
injector_window = create_injector_window()
blue_box_window = create_blue_box()

injector_window.mainloop()