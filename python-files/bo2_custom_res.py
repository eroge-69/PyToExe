
import tkinter as tk
import win32gui
import win32con

def resize_window(window_title, width, height):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.MoveWindow(hwnd, 100, 100, width, height, True)
        return True
    return False

def apply_resolution():
    title = title_entry.get()
    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
        if resize_window(title, width, height):
            result_label.config(text="✅ Resolution applied!", fg="green")
        else:
            result_label.config(text="❌ Game window not found.", fg="red")
    except ValueError:
        result_label.config(text="❌ Invalid input.", fg="red")

# GUI Setup
app = tk.Tk()
app.title("BO2 Custom Res")
app.geometry("300x180")

tk.Label(app, text="BO2 Window Title:").pack()
title_entry = tk.Entry(app)
title_entry.insert(0, "Call of Duty®: Black Ops II")
title_entry.pack()

tk.Label(app, text="Width:").pack()
width_entry = tk.Entry(app)
width_entry.insert(0, "1920")
width_entry.pack()

tk.Label(app, text="Height:").pack()
height_entry = tk.Entry(app)
height_entry.insert(0, "1080")
height_entry.pack()

tk.Button(app, text="Apply Resolution", command=apply_resolution).pack(pady=5)
result_label = tk.Label(app, text="")
result_label.pack()

app.mainloop()
