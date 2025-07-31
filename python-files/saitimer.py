import tkinter as tk
import time
import threading
import win32gui
import win32process
import psutil

class SAI2Timer:
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.root = tk.Tk()
        self.root.title("SAI Timer")
        self.root.geometry("200x60")
        self.root.configure(bg="white")
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)

        self.label = tk.Label(self.root, text="00:00:00", font=("Segoe UI", 18), bg="white", fg="black")
        self.label.pack(expand=True)

        self.check_thread = threading.Thread(target=self.window_check_loop, daemon=True)
        self.check_thread.start()

        self.update_timer()
        self.root.mainloop()

    def get_foreground_exe(self):
        hwnd = win32gui.GetForegroundWindow()
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except Exception:
            return None

    def window_check_loop(self):
        while True:
            current_window = self.get_foreground_exe()
            if current_window and 'sai' in current_window.lower():
                if not self.running:
                    self.running = True
                    self.start_time = time.time() - self.elapsed_time
            else:
                if self.running:
                    self.running = False
                    self.elapsed_time = time.time() - self.start_time
            time.sleep(0.5)

    def update_timer(self):
        if self.running:
            current_time = time.time() - self.start_time
        else:
            current_time = self.elapsed_time

        hours = int(current_time // 3600)
        minutes = int((current_time % 3600) // 60)
        seconds = int(current_time % 60)
        self.label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
        self.root.after(500, self.update_timer)

if __name__ == "__main__":
    SAI2Timer()
