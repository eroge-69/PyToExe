import tkinter as tk
from tkinter import ttk, simpledialog
import json
import os

DATA_FILE = "poker_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class PokerActionTracker:
    def __init__(self, root):
        self.root = root
        self.nickname = self.choose_nickname()
        if not self.nickname:
            root.destroy()
            return
        self.root.title(f"Poker Tracker - {self.nickname}")
        self.data = load_data()
        if self.nickname in self.data:
            self.actions = self.data[self.nickname]["actions"]
            self.total_actions = self.data[self.nickname]["total"]
        else:
            self.actions = {
                "Raise": 0,
                "Call": 0,
                "Fold": 0,
                "3-Bet": 0,
                "Fold to 3-Bet": 0
            }
            self.total_actions = 0
        self.labels = {}
        row = 0
        for action in self.actions:
            button = ttk.Button(root, text=action, command=lambda a=action: self.action_click(a))
            button.grid(row=row, column=0, padx=5, pady=5, sticky="w")
            label = ttk.Label(root, text=f"{action}: 0.00%")
            label.grid(row=row, column=1, padx=5, pady=5, sticky="w")
            self.labels[action] = label
            row += 1
        self.total_label = ttk.Label(root, text=f"Total Actions: {self.total_actions}")
        self.total_label.grid(row=row, column=0, columnspan=2, pady=10)
        self.update_percentages()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def choose_nickname(self):
        data = load_data()
        existing_nicks = list(data.keys())
        prompt = "Enter a new nickname or choose an existing one:\nExisting: " + ", ".join(existing_nicks) if existing_nicks else "Enter a new nickname:"
        return simpledialog.askstring("Nickname", prompt)
    
    def action_click(self, action):
        self.actions[action] += 1
        self.total_actions += 1
        self.update_percentages()
        self.total_label.config(text=f"Total Actions: {self.total_actions}")
    
    def update_percentages(self):
        for action in self.actions:
            percentage = 0.0 if self.total_actions == 0 else (self.actions[action] / self.total_actions) * 100
            self.labels[action].config(text=f"{action}: {percentage:.2f}%")
    
    def on_closing(self):
        self.data[self.nickname] = {
            "actions": self.actions,
            "total": self.total_actions
        }
        save_data(self.data)
        self.root.destroy()

if name == "__main__":
    root = tk.Tk()
    app = PokerActionTracker(root)
    root.mainloop()