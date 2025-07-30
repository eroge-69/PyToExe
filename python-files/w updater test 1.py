import tkinter as tk
import threading
import time
import keyboard  # Install with: pip install keyboard
import sys

class FakeWindowsUpdate:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#0078D7")  # Windows update blue
        self.root.attributes('-fullscreen', True)

        self.percent = 0
        self.running = True
        self.spinner_states = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0

        # Spinner
        self.label_spinner = tk.Label(root, text="", font=("Segoe UI", 50), fg="white", bg="#0078D7")
        self.label_spinner.pack(pady=(100, 10))

        # Update text
        self.label_status = tk.Label(root, text="Working on updates", font=("Segoe UI", 28), fg="white", bg="#0078D7")
        self.label_status.pack(pady=10)

        # Percent
        self.label_percent = tk.Label(root, text="0% complete", font=("Segoe UI", 22), fg="white", bg="#0078D7")
        self.label_percent.pack(pady=10)

        # Message
        self.label_message = tk.Label(root, text="Don't turn off your computer", font=("Segoe UI", 22), fg="white", bg="#0078D7")
        self.label_message.pack(pady=10)

        threading.Thread(target=self.update_loop, daemon=True).start()
        threading.Thread(target=self.check_exit_combo, daemon=True).start()

    def update_loop(self):
        while self.running:
            if self.percent < 999:
                self.percent += 1
            self.label_percent.config(text=f"{self.percent}% complete")
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_states)
            self.label_spinner.config(text=self.spinner_states[self.spinner_index])
            time.sleep(0.3)  # Slow update: ~1% every 0.3 seconds (~5 minutes to 999%)

    def check_exit_combo(self):
        while self.running:
            if keyboard.is_pressed("ctrl+shift+e"):
                self.running = False
                self.root.destroy()
                sys.exit()
            time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = FakeWindowsUpdate(root)
    root.mainloop()
