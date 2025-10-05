
import tkinter as tk
from tkinter import messagebox
import math

def analyze_data():
    try:
        raw = text_box.get("1.0", tk.END).strip()
        lines = [float(x) for x in raw.splitlines() if x.strip()]
        if len(lines) < 2:
            messagebox.showwarning("Error", "Please enter at least two numbers.")
            return

        n = len(lines)
        mean = sum(lines) / n
        variance = sum((x - mean) ** 2 for x in lines) / (n - 1)
        stdev = math.sqrt(variance)

        target = float(target_entry.get())
        expected_return = (target - 1) * mean

        result = (
            f"Rounds analyzed: {n}\n"
            f"Mean: {mean:.4f}\n"
            f"Standard Deviation: {stdev:.4f}\n"
            f"Example Target {target:.2f}x Expected Return: {expected_return:.4f}"
        )
        result_label.config(text=result)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers only.")

# --- GUI ---
root = tk.Tk()
root.title("Crash Statistics Analyzer")
root.geometry("500x500")

title_label = tk.Label(root, text="Crash Statistics Analyzer", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

tk.Label(root, text="Paste multipliers (one per line):").pack()
text_box = tk.Text(root, height=15, width=40)
text_box.pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Target Multiplier:").pack(side=tk.LEFT)
target_entry = tk.Entry(frame, width=10)
target_entry.insert(0, "2.0")
target_entry.pack(side=tk.LEFT, padx=5)

analyze_btn = tk.Button(root, text="Analyze Data", command=analyze_data, bg="#4CAF50", fg="white")
analyze_btn.pack(pady=10)

result_label = tk.Label(root, text="", justify=tk.LEFT, font=("Consolas", 10))
result_label.pack(pady=10)

root.mainloop()
