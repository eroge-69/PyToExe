
import tkinter as tk
import threading
import time

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple AutoClicker")
        self.master.geometry("300x150")
        self.running = False

        self.interval_label = tk.Label(master, text="Click Interval (seconds):")
        self.interval_label.pack(pady=5)

        self.interval_entry = tk.Entry(master)
        self.interval_entry.insert(0, "1.0")
        self.interval_entry.pack(pady=5)

        self.start_button = tk.Button(master, text="Start Clicking", command=self.start_clicking)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Clicking", command=self.stop_clicking)
        self.stop_button.pack(pady=5)

    def click_loop(self):
        import pyautogui
        try:
            interval = float(self.interval_entry.get())
        except ValueError:
            interval = 1.0
        while self.running:
            pyautogui.click()
            time.sleep(interval)

    def start_clicking(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.click_loop, daemon=True).start()

    def stop_clicking(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
