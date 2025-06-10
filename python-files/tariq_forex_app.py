# Tariq Forex App with Main Menu, Calculator, and Journal
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import csv
from docx import Document
from PIL import ImageTk, Image

# Constants
PAIR_PIP_VALUES = {
    'NQ': 20,
    'SP': 50,
    'EURUSD': 10,
    'GBPUSD': 10,
    'XAUUSD': 100,
    'US30': 10
}

# Main App
class TariqApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tariq Forex App")
        self.root.geometry("400x300")
        self.root.configure(bg="#f2f2f2")
        self.file_path = os.getcwd()  # Default file path

        ttk.Button(root, text="Tariq Forex Calculator", command=self.open_calculator, width=30).pack(pady=20)
        ttk.Button(root, text="Daily Journal", command=self.open_journal, width=30).pack(pady=20)

    def open_calculator(self):
        self.new_window(TariqForexCalculator)

    def open_journal(self):
        self.new_window(DailyJournal)

    def new_window(self, app_class):
        new_root = tk.Toplevel(self.root)
        app_class(new_root, self)

# Calculator Window
class TariqForexCalculator:
    def __init__(self, root, parent):
        self.root = root
        self.root.title("Tariq Forex Calculator")
        self.root.geometry("500x550")
        self.root.configure(bg="#f2f2f2")
        self.parent = parent

        self.create_label_entry("💲 Account Size", "account_size")
        self.create_label_dropdown("📉 Risk %", "risk_percent", ["0.50", "1", "2"])
        self.create_label_value("💥 Risk $", "risk_dollars", readonly=True)
        self.create_label_dropdown("🔁 Pair", "pair", list(PAIR_PIP_VALUES.keys()))
        self.create_label_entry("🎯 Target ($)", "target")
        self.create_label_entry("🛑 Stop Size (pips)", "stop_size")
        self.create_label_value("📦 Lot Size", "lot_size", readonly=True)
        self.create_label_value("🎯 Pips Needed to Win", "pips_needed", readonly=True)

        tk.Button(root, text="🧮 Calculate", command=self.calculate, bg="#4CAF50", fg="white", width=20).pack(pady=8)
        tk.Button(root, text="🧹 Clear", command=self.clear_all, bg="#2196F3", fg="white", width=20).pack(pady=4)
        tk.Button(root, text="🧽 Clear Stop Size", command=self.clear_stop_size, bg="#FFC107", fg="black", width=20).pack(pady=4)
        tk.Button(root, text="🔙 Back", command=self.root.destroy, bg="#e91e63", fg="white", width=20).pack(pady=4)

    def create_label_entry(self, text, var_name):
        label = tk.Label(self.root, text=text, bg="#f2f2f2", anchor="w", font=("Arial", 10, "bold"))
        label.pack(fill="x", padx=20)
        entry = tk.Entry(self.root)
        entry.pack(fill="x", padx=20, pady=3)
        setattr(self, var_name, entry)

    def create_label_dropdown(self, text, var_name, options):
        label = tk.Label(self.root, text=text, bg="#f2f2f2", anchor="w", font=("Arial", 10, "bold"))
        label.pack(fill="x", padx=20)
        combo = ttk.Combobox(self.root, values=options)
        combo.pack(fill="x", padx=20, pady=3)
        setattr(self, f"{var_name}_combo", combo)
        setattr(self, var_name, combo)

    def create_label_value(self, text, var_name, readonly=False):
        label = tk.Label(self.root, text=text, bg="#f2f2f2", anchor="w", font=("Arial", 10, "bold"))
        label.pack(fill="x", padx=20)
        entry = tk.Entry(self.root, state="readonly" if readonly else "normal")
        entry.pack(fill="x", padx=20, pady=3)
        setattr(self, var_name, entry)

    def calculate(self):
        try:
            account_size = float(self.account_size.get())
            stop_size = float(self.stop_size.get())
            pair = self.pair.get()
            pip_value = PAIR_PIP_VALUES.get(pair, 10)
            risk_percent = float(self.risk_percent.get())
            risk_dollars = (risk_percent / 100) * account_size

            self.risk_dollars.config(state="normal")
            self.risk_dollars.delete(0, tk.END)
            self.risk_dollars.insert(0, f"{risk_dollars:.2f}")
            self.risk_dollars.config(state="readonly")

            lot_size = risk_dollars / (pip_value * stop_size)
            self.lot_size.config(state="normal")
            self.lot_size.delete(0, tk.END)
            self.lot_size.insert(0, f"{lot_size:.2f}")
            self.lot_size.config(state="readonly")

            target = float(self.target.get())
            pips_needed = target / (lot_size * pip_value)
            self.pips_needed.config(state="normal")
            self.pips_needed.delete(0, tk.END)
            self.pips_needed.insert(0, f"{pips_needed:.2f}")
            self.pips_needed.config(state="readonly")

        except Exception as e:
            print("Error:", e)

    def clear_all(self):
        for var in ["account_size", "risk_percent", "risk_dollars", "target", "stop_size", "lot_size", "pips_needed"]:
            entry = getattr(self, var)
            entry.config(state="normal")
            entry.delete(0, tk.END)
            if "readonly" in entry.cget("state"):
                entry.config(state="readonly")

    def clear_stop_size(self):
        self.stop_size.delete(0, tk.END)

# DailyJournal class will be completed in the next file
class DailyJournal:
    def __init__(self, root, parent):
        pass
