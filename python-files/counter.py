import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import pyperclip
import json
import os

class CounterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Counter Pro")
        self.root.geometry("400x500")
        self.root.resizable(True, True)
        
        # Always on top
        self.root.attributes('-topmost', True)
        
        # Variables
        self.counter = tk.IntVar(value=1)
        self.prefix = tk.StringVar(value="AL")
        
        # Load saved data
        self.load_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Update display
        self.update_display()
        
        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Counter Pro", 
                               font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Prefix input
        ttk.Label(main_frame, text="Präfix:").grid(row=1, column=0, sticky=tk.W, pady=5)
        prefix_entry = ttk.Entry(main_frame, textvariable=self.prefix, width=10)
        prefix_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        prefix_entry.bind('<KeyRelease>', lambda e: self.update_display())
        
        # Counter display
        self.display_var = tk.StringVar()
        display_label = ttk.Label(main_frame, textvariable=self.display_var, 
                                 font=("Courier", 18, "bold"),
                                 background="lightgray", 
                                 relief="sunken", 
                                 padding=10)
        display_label.grid(row=2, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="➕ Erhöhen", 
                  command=self.increment).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="📋 Kopieren", 
                  command=self.copy_to_clipboard).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🔄 Reset", 
                  command=self.reset).grid(row=0, column=2, padx=5)
        
        # Always on top toggle
        self.topmost_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Always on Top", 
                       variable=self.topmost_var, 
                       command=self.toggle_topmost).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Info
        info_text = """Format: DDMMYY + Präfix + Zähler
Datum wird automatisch aktualisiert
Einstellungen werden gespeichert"""
        
        ttk.Label(main_frame, text=info_text, 
                 font=("Arial", 9), 
                 foreground="gray").grid(row=5, column=0, columnspan=2, pady=20)
        
        # Configure column weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def get_today_date(self):
        today = datetime.date.today()
        return today.strftime("%d%m%y")
    
    def update_display(self):
        date_str = self.get_today_date()
        prefix = self.prefix.get().upper()
        counter_str = f"{self.counter.get():02d}"
        result = f"{date_str}{prefix}{counter_str}"
        self.display_var.set(result)
    
    def increment(self):
        self.counter.set(self.counter.get() + 1)
        self.update_display()
        self.save_data()
    
    def copy_to_clipboard(self):
        try:
            pyperclip.copy(self.display_var.get())
            messagebox.showinfo("Erfolg", "In Zwischenablage kopiert!")
        except:
            # Fallback ohne pyperclip
            self.root.clipboard_clear()
            self.root.clipboard_append(self.display_var.get())
            messagebox.showinfo("Erfolg", "In Zwischenablage kopiert!")
    
    def reset(self):
        self.counter.set(1)
        self.update_display()
        self.save_data()
    
    def toggle_topmost(self):
        self.root.attributes('-topmost', self.topmost_var.get())
    
    def save_data(self):
        data = {
            'counter': self.counter.get(),
            'prefix': self.prefix.get(),
            'topmost': self.topmost_var.get()
        }
        try:
            with open('counter_data.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def load_data(self):
        try:
            if os.path.exists('counter_data.json'):
                with open('counter_data.json', 'r') as f:
                    data = json.load(f)
                    self.counter.set(data.get('counter', 1))
                    self.prefix.set(data.get('prefix', 'AL'))
        except:
            pass
    
    def on_closing(self):
        self.save_data()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CounterApp()
    app.run()