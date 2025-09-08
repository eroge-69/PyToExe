# payload.py
import tkinter as tk
from tkinter import messagebox

def run_malicious_code():
    messagebox.showinfo("lmao got you", "get dunked on loser")
    # Add more malicious actions here (e.g., data theft, ransomware, etc.)

root = tk.Tk()
root.withdraw()  # Hide the window
run_malicious_code()
