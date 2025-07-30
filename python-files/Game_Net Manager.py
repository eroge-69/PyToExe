import tkinter as tk
from tkinter import messagebox, simpledialog
import time
from datetime import datetime, timedelta
import json
import os

class GameNetApp:
    def init(self, root):
        self.root = root
        self.root.title("Game Net Manager")
        self.systems = {}
        self.timers = {}
        self.start_times = {}
        self.running = {}
        self.json_file = "systems.json"
        
        # Load saved systems
        self.load_systems()
        
        # Frame for inputs
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)
        
        # System name input
        tk.Label(input_frame, text="System Name:").grid(row=0, column=0, padx=5)
        self.system_name = tk.Entry(input_frame)
        self.system_name.grid(row=0, column=1, padx=5)
        
        # Rate input (Toman per minute)
        tk.Label(input_frame, text="Rate (Toman/min):").grid(row=0, column=2, padx=5)
        self.rate = tk.Entry(input_frame)
        self.rate.grid(row=0, column=3, padx=5)
        
        # Button to add system
        tk.Button(input_frame, text="Add System", command=self.add_system).grid(row=0, column=4, padx=5)
        
        # Frame for displaying systems
        self.systems_frame = tk.Frame(root)
        self.systems_frame.pack(pady=10)
        
        # Display loaded systems
        self.display_systems()
    
    def load_systems(self):
        """Load systems from JSON file"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    self.systems = json.load(file)
            except json.JSONDecodeError:
                self.systems = {}
    
    def save_systems(self):
        """Save systems to JSON file"""
        with open(self.json_file, 'w', encoding='utf-8') as file:
            json.dump(self.systems, file, ensure_ascii=False, indent=4)
    
    def display_systems(self):
        """Display saved systems in the UI"""
        # Clear previous widgets
        for widget in self.systems_frame.winfo_children():
            widget.destroy()
        
        for name, rate in self.systems.items():
            self.running[name] = False
            self.timers[name] = tk.Label(self.systems_frame, text=f"{name}: 00:00:00 - 0 Toman")
            self.timers[name].pack(pady=5)
            
            # Frame for buttons
            btn_frame = tk.Frame(self.systems_frame)
            btn_frame.pack()
            tk.Button(btn_frame, text="Start", command=lambda n=name: self.start_timer(n)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Reset", command=lambda n=name: self.reset_timer(n)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Change Rate", command=lambda n=name: self.change_rate(n)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Delete", command=lambda n=name: self.delete_system(n)).pack(side=tk.LEFT, padx=5)
    
    def add_system(self):
        name = self.system_name.get().strip()
        try:
            rate = float(self.rate.get())
            if name and rate > 0:
                if name not in self.systems:
                    self.systems[name] = rate
                    self.running[name] = False
                    self.timers[name] = tk.Label(self.systems_frame, text=f"{name}: 00:00:00 - 0 Toman")
                    self.timers[name].pack(pady=5)
                    
                    # Buttons for start, reset, change rate, and delete
                    btn_frame = tk.Frame(self.systems_frame)
                    btn_frame.pack()
                    tk.Button(btn_frame, text="Start", command=lambda: self.start_timer(name)).pack(side=tk.LEFT, padx=5)
                    tk.Button(btn_frame, text="Reset", command=lambda: self.reset_timer(name)).pack(side=tk.LEFT, padx=5)