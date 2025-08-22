import os
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import sys
import ctypes

if getattr(sys, 'frozen', False):
    os.environ['TKDND_LIBRARY'] = os.path.join(sys._MEIPASS, 'tkdnd')

# === CONFIGURATION ===
PROGRAM_TITLE = "Steam Crusher"  # Change program name here
PROGRAM_ICON = "icon.ico"  # Put your .ico file path here (optional)

LUA_DEST = r"C:\Program Files (x86)\Steam\config\stplug-in"
MANIFEST_DEST = r"C:\Program Files (x86)\Steam\depotcache"


# === File Handling ===
def handle_files(file_list):
    copied_files = []
    skipped_files = []

    for file_path in file_list:
        file_path = file_path.strip("{}")  # Remove {} that come with drag-n-drop
        if not os.path.isfile(file_path):
            continue

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".lua":
            dest = LUA_DEST
        elif ext == ".manifest":
            dest = MANIFEST_DEST
        else:
            skipped_files.append(file_path)
            continue

        try:
            shutil.copy(file_path, dest)
            copied_files.append(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy {file_path}: {str(e)}")

    summary = []
    if copied_files:
        summary.append(f"Copied {len(copied_files)} files.")
    if skipped_files:
        summary.append(f"Skipped {len(skipped_files)} unsupported files.")

    if summary:
        messagebox.showinfo("Transfer Complete", "\n".join(summary))


# === Setup root window ===
root = TkinterDnD.Tk()
root.title(PROGRAM_TITLE)

# Fix for showing in taskbar even with overrideredirect
root.overrideredirect(True)  # No borders
root.geometry("+200+200")
root.config(bg="black")

# Make background transparent (Windows only)
root.wm_attributes("-transparentcolor", "black")

# Force it to appear in taskbar
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x00080000)  # WS_EX_APPWINDOW


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# === Load PNG as GUI ===
png_path = resource_path("icon.png")   # Your PNG
img = Image.open(png_path).resize((200, 200), Image.LANCZOS)
photo = ImageTk.PhotoImage(img)

root.geometry(f"{img.width}x{img.height}+200+200")

canvas = tk.Canvas(root, width=img.width, height=img.height,
                   highlightthickness=0, bg="black", bd=0)
canvas.pack()
canvas.create_image(0, 0, image=photo, anchor="nw")

# Label text overlay
label = tk.Label(root, text="Drop files here",
                 bg="#0e1f4e", fg="white", font=("JetBrains Mono", 13))
label.place(relx=0.5, rely=0.5, anchor="center")


# === Make window movable ===
def start_move(event):
    root.x = event.x_root
    root.y = event.y_root


def do_move(event):
    dx = event.x_root - root.x
    dy = event.y_root - root.y
    x = root.winfo_x() + dx
    y = root.winfo_y() + dy
    root.geometry(f"+{x}+{y}")
    root.x = event.x_root
    root.y = event.y_root


canvas.bind("<Button-1>", start_move)
canvas.bind("<B1-Motion>", do_move)


# === Drag & Drop ===
def drop(event):
    files = event.data.split()
    handle_files(files)


# Register drop target for both canvas and label
canvas.drop_target_register(DND_FILES)
canvas.dnd_bind("<<Drop>>", drop)

label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", drop)


# === Run ===
root.mainloop()
