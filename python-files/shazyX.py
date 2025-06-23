import os
import shutil
import ctypes
from tkinter import *
from tkinter import messagebox

# ======== DARK THEME COLORS ========
BG_COLOR = "#1e1e1e"
BTN_COLOR = "#2d2d2d"
TEXT_COLOR = "#ffffff"
HIGHLIGHT = "#5e5eff"

# ======== FUNCTIONS ========

def clean_temp_env():
    temp_path = os.getenv('TEMP')
    try:
        for item in os.listdir(temp_path):
            item_path = os.path.join(temp_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except:
                pass
        messagebox.showinfo("ShazyX", "✅ %TEMP% cleaned.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def clean_temp_win():
    path = r"C:\Windows\Temp"
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except:
                pass
        messagebox.showinfo("ShazyX", "✅ Windows Temp cleaned.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def clean_prefetch():
    path = r"C:\Windows\Prefetch"
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                os.remove(item_path)
            except:
                pass
        messagebox.showinfo("ShazyX", "✅ Prefetch cleaned.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def free_ram():
    try:
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
        messagebox.showinfo("ShazyX", "✅ RAM cleared.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ======== GUI ========

app = Tk()
app.title("ShazyX Optimizer")
app.geometry("350x300")
app.configure(bg=BG_COLOR)

Label(app, text="ShazyX Optimizer", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=HIGHLIGHT).pack(pady=10)

Button(app, text="🧹 Clean %TEMP%", width=25, command=clean_temp_env, bg=BTN_COLOR, fg=TEXT_COLOR).pack(pady=10)
Button(app, text="🧹 Clean Windows Temp", width=25, command=clean_temp_win, bg=BTN_COLOR, fg=TEXT_COLOR).pack(pady=10)
Button(app, text="⚙️ Clean Prefetch", width=25, command=clean_prefetch, bg=BTN_COLOR, fg=TEXT_COLOR).pack(pady=10)
Button(app, text="🧠 Free RAM", width=25, command=free_ram, bg=BTN_COLOR, fg=TEXT_COLOR).pack(pady=10)

app.mainloop()
