import tkinter as tk
from tkinter import ttk, font, messagebox
import pyautogui
import time
import threading

class LegionAutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Legion AutoClicker")
        self.root.geometry("400x300")
        self.root.configure(bg='black')
        
        # Legion-style terminal font
        self.custom_font = font.Font(family="Courier", size=10, weight="bold")
        
        # Variables
        self.running = False
        self.click_count = 0
        self.interval = tk.StringVar(value="0.5")  # Now a StringVar for direct input
        self.click_type = tk.StringVar(value="Left Click")
        
        # UI Setup
        self.setup_ui()
    
    def setup_ui(self):
        # Main Frame (Terminal-like background)
        main_frame = tk.Frame(self.root, bg='black', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title (Legion-style header)
        title = tk.Label(
            main_frame,
            text="LEGION AUTOCLICKER v1.0",
            bg='black',
            fg='#00ff00',
            font=self.custom_font
        )
        title.pack(pady=(0, 10))
        
        # Interval Input (Manual Entry)
        interval_frame = tk.Frame(main_frame, bg='black')
        interval_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            interval_frame,
            text="INTERVAL (sec):",
            bg='black',
            fg='#00ff00',
            font=self.custom_font
        ).pack(side=tk.LEFT)
        
        self.interval_entry = ttk.Entry(
            interval_frame,
            textvariable=self.interval,
            width=10,
            style='Terminal.TEntry'
        )
        self.interval_entry.pack(side=tk.LEFT, padx=5)
        
        # Dropdown for Click Type
        click_frame = tk.Frame(main_frame, bg='black')
        click_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            click_frame,
            text="CLICK TYPE:",
            bg='black',
            fg='#00ff00',
            font=self.custom_font
        ).pack(side=tk.LEFT)
        
        self.click_dropdown = ttk.Combobox(
            click_frame,
            textvariable=self.click_type,
            values=["Left Click", "Right Click", "Middle Click"],
            state="readonly",
            width=12,
            style='Terminal.TCombobox'
        )
        self.click_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Click Counter
        self.counter_label = tk.Label(
            main_frame,
            text="CLICKS: 0",
            bg='black',
            fg='#00ff00',
            font=self.custom_font
        )
        self.counter_label.pack(pady=5)
        
        # Start/Stop Button
        self.toggle_button = tk.Button(
            main_frame,
            text="START",
            command=self.toggle_clicking,
            bg='#003300',
            fg='#00ff00',
            activebackground='#002200',
            activeforeground='#00ff00',
            font=self.custom_font,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.toggle_button.pack(pady=10, fill=tk.X)
        
        # Status Bar
        self.status_bar = tk.Label(
            main_frame,
            text="STATUS: READY",
            bg='black',
            fg='#00ff00',
            font=self.custom_font
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.configure('Terminal.TEntry', background='black', foreground='#00ff00')
        self.style.configure('Terminal.TCombobox', background='black', foreground='#00ff00')
    
    def toggle_clicking(self):
        if not self.running:
            try:
                interval = float(self.interval.get())
                if interval <= 0:
                    raise ValueError("Interval must be positive")
                
                self.running = True
                self.toggle_button.config(text="STOP", bg='#330000')
                self.status_bar.config(text="STATUS: RUNNING")
                self.click_thread = threading.Thread(target=self.auto_click)
                self.click_thread.daemon = True
                self.click_thread.start()
            except ValueError:
                messagebox.showerror("Error", "Invalid interval! Enter a positive number.")
        else:
            self.running = False
            self.toggle_button.config(text="START", bg='#003300')
            self.status_bar.config(text="STATUS: STOPPED")
    
    def auto_click(self):
        while self.running:
            click_type = self.click_type.get()
            
            if click_type == "Left Click":
                pyautogui.leftClick()
            elif click_type == "Right Click":
                pyautogui.rightClick()
            else:
                pyautogui.middleClick()
            
            self.click_count += 1
            self.counter_label.config(text=f"CLICKS: {self.click_count}")
            time.sleep(float(self.interval.get()))

if __name__ == "__main__":
    root = tk.Tk()
    app = LegionAutoClicker(root)
    root.mainloop()