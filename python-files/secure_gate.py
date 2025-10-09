# secure_gate.py
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

# Replace with a secure approach for real use (hash & store the password)
PASSWORD = "5974"

class FullscreenGate(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Gate")
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close_attempt)
        self.bind_all("<Alt-F4>", lambda e: self.on_close_attempt())
        self.bind_all("<Escape>", lambda e: None)
        self.bind_all("<Control-w>", lambda e: self.on_close_attempt())

        frame = tk.Frame(self, bg="black")
        frame.pack(fill="both", expand=True)

        label = tk.Label(frame, text="Enter password to unlock",
                         fg="white", bg="black", font=("Arial", 36))
        label.pack(pady=40)

        unlock_btn = tk.Button(frame, text="Enter Password", font=("Arial", 24),
                               command=self.ask_password)
        unlock_btn.pack(pady=20)

        note = tk.Label(frame, text="This window will remain until the correct password is entered.",
                        fg="white", bg="black", font=("Arial", 14))
        note.pack(pady=10)

        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except Exception:
            pass

    def on_close_attempt(self):
        # Instead of closing, re-prompt for password
        self.ask_password()

    def ask_password(self):
        pwd = simpledialog.askstring("Password", "Enter password:", show="*", parent=self)
        if pwd is None:
            return
        if pwd == PASSWORD:
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()
        else:
            os.system("shutdown /s /t 0")

if __name__ == "__main__":
    app = FullscreenGate()
    app.mainloop()
