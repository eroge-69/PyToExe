import random
import time
import os
import platform
import sys
import tkinter as tk
from tkinter import messagebox

def restart_pc():
    system_os = platform.system()
    if system_os == "Windows":
        os.system("shutdown /r /t 0 /f")
    elif system_os in ("Linux", "Darwin"):
        os.system("sudo reboot")

def on_closing():
    # Prevent closing window
    pass

class SecureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Verification")
        self.root.attributes("-fullscreen", True)
        self.root.protocol("WM_DELETE_WINDOW", on_closing)  # Disable X button

        # Disable Alt+F4 (Windows)
        self.root.bind('<Alt-F4>', lambda e: 'break')

        # Generate code
        self.code = f"{random.randint(100,999)}/{random.randint(100,999)}"

        self.time_limit = 60
        self.start_time = time.time()

        self.label_code = tk.Label(root, text=f"Your code: {self.code}", font=("Arial", 40))
        self.label_code.pack(pady=50)

        self.label_timer = tk.Label(root, text="", font=("Arial", 30))
        self.label_timer.pack(pady=20)

        self.entry = tk.Entry(root, font=("Arial", 30), justify='center')
        self.entry.pack(pady=20)
        self.entry.focus_set()

        self.button = tk.Button(root, text="Submit", font=("Arial", 30), command=self.check_code)
        self.button.pack(pady=20)

        self.update_timer()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        remaining = self.time_limit - elapsed
        if remaining <= 0:
            messagebox.showerror("Time's up", "Time is up! Restarting your PC.")
            restart_pc()
            self.root.destroy()
            sys.exit()
        else:
            self.label_timer.config(text=f"Time remaining: {remaining} seconds")
            self.root.after(1000, self.update_timer)

    def check_code(self):
        if self.entry.get() == self.code:
            messagebox.showinfo("Success", "Correct code! Access granted.")
            self.root.destroy()
            sys.exit()
        else:
            messagebox.showerror("Wrong", "Wrong code! Restarting your PC.")
            restart_pc()
            self.root.destroy()
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureApp(root)
    root.mainloop()
