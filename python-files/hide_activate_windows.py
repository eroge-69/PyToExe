
import tkinter as tk
import ctypes

def get_wallpaper_color():
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         "Control Panel\\Colors")
    try:
        color_str, _ = winreg.QueryValueEx(key, "Background")
        r, g, b = [int(float(c)) for c in color_str.split()]
        return '#%02x%02x%02x' % (r, g, b)
    finally:
        winreg.CloseKey(key)

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "white")

root.geometry("400x60+0+2080")

bg_color = get_wallpaper_color()
frame = tk.Frame(root, bg=bg_color)
frame.pack(fill="both", expand=True)

label = tk.Label(frame, text="", bg=bg_color)
label.pack()

root.mainloop()
