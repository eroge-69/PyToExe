import pyautogui
import tkinter as tk
from tkinter import messagebox
import time
import threading
import sys
import os

pyautogui.PAUSE = 0.1

class AutoScrollApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Scroll App")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        self.scrolling = False
        self.scroll_thread = None
        
        self.label = tk.Label(root, text="Scroll Speed (pixels):")
        self.label.pack(pady=10)
        
        self.speed_entry = tk.Entry(root, width=10)
        self.speed_entry.insert(0, "100")
        self.speed_entry.pack()
        
        self.start_button = tk.Button(root, text="Start Scrolling", command=self.start_scroll)
        self.start_button.pack(pady=10)
        
        self.stop_button = tk.Button(root, text="Stop Scrolling", command=self.stop_scroll, state="disabled")
        self.stop_button.pack(pady=10)
        
        self.status_label = tk.Label(root, text="Status: Stopped")
        self.status_label.pack(pady=10)
        
    def start_scroll(self):
        try:
            scroll_amount = int(self.speed_entry.get())
            if scroll_amount <= 0:
                messagebox.showerror("Error", "Scroll speed must be a positive number!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for scroll speed!")
            return
            
        self.scrolling = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Status: Scrolling")
        
        self.scroll_thread = threading.Thread(target=self.scroll_loop, args=(scroll_amount,))
        self.scroll_thread.daemon = True
        self.scroll_thread.start()
        
    def stop_scroll(self):
        self.scrolling = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Status: Stopped")
        
    def scroll_loop(self, scroll_amount):
        try:
            while self.scrolling:
                pyautogui.scroll(-scroll_amount)
                time.sleep(0.5)
        except Exception as e:
            self.scrolling = False
            self.root.after(0, lambda: self.status_label.config(text="Status: Error"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scrolling error: {str(e)}"))
            self.root.after(0, lambda: self.start_button.config(state="normal"))
            self.root.after(0, lambda: self.stop_button.config(state="disabled"))

if __name__ == "__main__":
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    root = tk.Tk()
    app = AutoScrollApp(root)
    root.mainloop()