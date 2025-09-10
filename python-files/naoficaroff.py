import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading

class AutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automation Tool")
        self.root.geometry("300x200")
        
        self.running = False
        
        # Calculate relative coordinates
        screen_width, screen_height = pyautogui.size()
        self.x = int(screen_width * 0.1)  # 10% of screen width
        self.y = int(screen_height * 0.3)  # 30% of screen height
        
        # GUI elements
        self.label = tk.Label(root, text="Automation Tool", font=("Arial", 14))
        self.label.pack(pady=10)
        
        self.status_label = tk.Label(root, text="Status: Stopped", fg="red")
        self.status_label.pack(pady=5)
        
        self.start_button = tk.Button(root, text="Start", command=self.start_automation)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_automation, state="disabled")
        self.stop_button.pack(pady=5)
        
        self.quit_button = tk.Button(root, text="Quit", command=self.quit_app)
        self.quit_button.pack(pady=5)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
    def automation_loop(self):
        while self.running:
            for _ in range(2):
                if not self.running:
                    break
                pyautogui.click(x=self.x, y=self.y)
            time.sleep(3)
            pyautogui.hotkey('f3')
            time.sleep(0.2)
    
    def start_automation(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Status: Running", fg="green")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.thread = threading.Thread(target=self.automation_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop_automation(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def quit_app(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    pyautogui.FAILSAFE = True  
    root = tk.Tk()
    app = AutomationApp(root)
    root.mainloop()