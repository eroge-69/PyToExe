import tkinter as tk
from tkinter import simpledialog

class ZikrCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("Zikr Counter")
        self.root.geometry("300x200")
        self.root.attributes("-topmost", True)  # Always on top

        self.count = 0
        self.key_binding = "space"  # default key

        # Label for counter
        self.label = tk.Label(root, text=str(self.count), font=("Arial", 48, "bold"))
        self.label.pack(pady=20)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        self.inc_btn = tk.Button(btn_frame, text="+1", command=self.increment, width=6, height=2)
        self.inc_btn.grid(row=0, column=0, padx=5)

        self.dec_btn = tk.Button(btn_frame, text="-1", command=self.decrement, width=6, height=2)
        self.dec_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset, width=6, height=2)
        self.reset_btn.grid(row=0, column=2, padx=5)

        # Change key binding button
        self.key_btn = tk.Button(root, text="Set Key", command=self.set_key)
        self.key_btn.pack(pady=10)

        # Default binding
        self.root.bind(f"<{self.key_binding}>", lambda event: self.increment())

    def increment(self):
        self.count += 1
        self.label.config(text=str(self.count))

    def decrement(self):
        if self.count > 0:
            self.count -= 1
        self.label.config(text=str(self.count))

    def reset(self):
        self.count = 0
        self.label.config(text=str(self.count))

    def set_key(self):
        new_key = simpledialog.askstring("Set Key", "Enter key name (e.g. space, a, F1):")
        if new_key:
            # remove old binding
            self.root.unbind(f"<{self.key_binding}>")
            self.key_binding = new_key
            self.root.bind(f"<{self.key_binding}>", lambda event: self.increment())

if __name__ == "__main__":
    root = tk.Tk()
    app = ZikrCounter(root)
    root.mainloop()