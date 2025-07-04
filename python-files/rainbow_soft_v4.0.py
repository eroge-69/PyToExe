import tkinter as tk
from tkinter import messagebox, ttk
from collections import Counter
from datetime import datetime, timedelta, timezone

default_colors = {
    "00": "#0000ff",  # Blue
    "01": "#008000",  # Green
    "10": "#FFFF00",  # Yellow
    "11": "#FFA500",  # Orange
}

# Threshold color
red_color = "#F44336"  # Red

# Store last cleared entry
last_cleared_entry = ""

# Helpers to insert and refocus
def insert_bit(bit):
    entry.insert(tk.END, bit)
    entry.focus_set()

def insert_preset(value):
    entry.insert(tk.END, value)
    entry.focus_set()

def analyze_sequence():
    binary_seq = entry.get().strip()

    if not all(bit in "01" for bit in binary_seq) or len(binary_seq) < 2:
        messagebox.showerror("Invalid Input", "Please enter a binary sequence with at least 2 digits.")
        return

    for widget in result_frame.winfo_children():
        widget.destroy()

    two_bit_combos = [binary_seq[i:i+2] for i in range(len(binary_seq) - 1)]
    combo_counts = Counter(two_bit_combos)
    colors = default_colors.copy()

    # Color rules
    compare_pairs = [("00", "01"), ("10", "11")]
    for a, b in compare_pairs:
        if abs(combo_counts.get(a, 0) - combo_counts.get(b, 0)) >= 3:
            colors[a] = red_color
            colors[b] = red_color

    for combo in combo_counts:
        if combo_counts[combo] >= 10:
            colors[combo] = red_color

    # Mark logic
    last_bit = binary_seq[-1]
    group_a = last_bit + "0"
    group_b = last_bit + "1"
    count_a = combo_counts.get(group_a, 0)
    count_b = combo_counts.get(group_b, 0)

    marks = {group_a: "", group_b: ""}
    if count_a > 0 and count_b > 0:
        if count_a > count_b:
            marks[group_a] = "🏐"
        elif count_b > count_a:
            marks[group_b] = "🏐"
    elif count_a > 0:
        marks[group_a] = "🏐"
    elif count_b > 0:
        marks[group_b] = "🏐"

    # Text Output with emoji in white
    tk.Label(result_frame, text="Terminal", font=("Segoe UI", 12, "bold"), bg="#000000", fg="white").pack(anchor="w", pady=(0, 5))

    for combo in ["00", "01", "10", "11"]:
        count = combo_counts.get(combo, 0)
        mark = marks.get(combo, "")
        color = colors.get(combo, "white")

        line_frame = tk.Frame(result_frame, bg="#000000")
        line_frame.pack(anchor="w", pady=1)

        if mark:
            tk.Label(line_frame, text=mark, fg="white", font=("Consolas", 12, "bold"), bg="#263238").pack(side="left")
        else:
            tk.Label(line_frame, text="   ", bg="#000000").pack(side="left")  # Adjusted spacing

        combo_label = tk.Label(line_frame, text=f"{combo}: {count}", fg=color, font=("Consolas", 12), bg="#000000")
        combo_label.pack(side="left")

def clear_all():
    global last_cleared_entry
    last_cleared_entry = entry.get()
    entry.delete(0, tk.END)
    for widget in result_frame.winfo_children():
        widget.destroy()

def restore_entry():
    if last_cleared_entry:
        entry.delete(0, tk.END)
        entry.insert(0, last_cleared_entry)

# GUI setup
root = tk.Tk()
root.title("Rainbow_soft")
root.geometry("400x450")
root.resizable(True, True)

root.configure(bg="#ECEFF1")  # Light grey background

# Apply a modern theme
style = ttk.Style()
style.theme_use('clam')  # 'clam' or 'alt' often look more modern than 'default' or 'classic'

# Configure general styles for ttk.Button and ttk.Entry
style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6, relief="flat",
                background="#607D8B", foreground="white")  # Default background/foreground
style.map('TButton', background=[('active', '#78909C')])  # Default hover effect

# *** Entry field style: Font size dramatically increased to 36, and vertical padding adjusted ***
style.configure('Input.TEntry',
                font=('Segoe UI', 36, 'bold'),  # Font size changed from 24 to 36
                foreground="#FFC107",
                fieldbackground="#000000",
                borderwidth=1,
                relief="solid",
                insertcolor="#FFC107",
                padding=[10, 20]  # Increased vertical padding to 20
                )
# *********************************************************************************************

style.configure('TLabel', background="#ECEFF1", font=("Segoe UI", 11))  # Default label style

# Input Frame
input_frame = tk.Frame(root, bg="#ECEFF1", pady=15)
input_frame.pack(fill="x", padx=2, pady=(5, 2))

tk.Label(input_frame, text="Entry:", font=("Segoe UI", 11, "bold"), bg="#ECEFF1", fg="#37474F").pack(anchor="w", padx=5)
entry = ttk.Entry(input_frame, width=30, style='Input.TEntry')
entry.configure(font=('Segoe UI', 18, 'bold'))
entry.pack(pady=(1, 3))  # Removed fill='x' and padx to minimize width visually

# Key Bindings
entry.bind("<Return>", lambda event: analyze_sequence())
entry.bind("<Control-Return>", lambda event: analyze_sequence())
entry.bind("<Control-BackSpace>", lambda event: clear_all())

# Buttons Frame
button_frame = tk.Frame(input_frame, bg="#ECEFF1")
button_frame.pack(pady=5)

btn_1 = ttk.Button(button_frame, text="1", command=lambda: insert_bit("1"))
btn_1.pack(side="left", padx=(0, 10))

sync_btn = ttk.Button(button_frame, text="Sync", command=analyze_sequence, style='Sync.TButton')
style.configure('Sync.TButton', background="#4CAF50", foreground="white")
style.map('Sync.TButton', background=[('active', '#66BB6A')])
sync_btn.pack(side="left")

btn_0 = ttk.Button(button_frame, text="0", command=lambda: insert_bit("0"))
btn_0.pack(side="left", padx=(10, 0))

# Result Frame
result_frame = tk.LabelFrame(root, text="Data", font=("Segoe UI", 10, "bold"),
                              bg="#263238", fg="white", padx=15, pady=15, bd=0, relief="flat")  # Dark background for terminal look
result_frame.pack(fill="both", padx=20, pady=10, expand=True)

# Clear and Restore Buttons
clear_frame = tk.Frame(root, bg="#ECEFF1")
clear_frame.pack(pady=(0, 15))

clear_btn = ttk.Button(clear_frame, text="Clear", command=clear_all, style='Clear.TButton')
style.configure('Clear.TButton', background="#F44336", foreground="white")
style.map('Clear.TButton', background=[('active', '#EF5350')])
clear_btn.pack(side="left", padx=(0, 10))

backspace_btn = ttk.Button(clear_frame, text="⌫", command=lambda: entry.delete(len(entry.get()) - 1) if entry.get() else None,
                           style='Backspace.TButton')
style.configure('Backspace.TButton', background="#FF9800", foreground="white")
style.map('Backspace.TButton', background=[('active', '#FFB74D')])
backspace_btn.pack(side="left")

restore_btn = ttk.Button(clear_frame, text="🔁", command=restore_entry,
                         style='Restore.TButton')
style.configure('Restore.TButton', background="#03A9F4", foreground="white")
style.map('Restore.TButton', background=[('active', '#29B6F6')])
restore_btn.pack(side="left", padx=(10, 0))

# Clock
def update_clock():
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime.now(ist).strftime('%H:%M:%S')
    clock_label.config(text=current_time)
    root.after(1000, update_clock)

clock_label = tk.Label(root, font=("Consolas", 32, "bold"), fg="#37474F", bg="#ECEFF1")  # Darker clock color
clock_label.pack(pady=(5, 15))

update_clock()

# Preset Buttons
preset_frame = tk.Frame(root, bg="#ECEFF1")
preset_frame.pack(pady=(0, 10))

preset_1 = ttk.Button(preset_frame, text="11001", command=lambda: insert_preset("11001"))
preset_1.pack(side="left", padx=5)

preset_2 = ttk.Button(preset_frame, text="00110", command=lambda: insert_preset("00110"))
preset_2.pack(side="left", padx=5)

# Set focus to entry box at startup
entry.focus_set()

# Start GUI loop
root.mainloop()
