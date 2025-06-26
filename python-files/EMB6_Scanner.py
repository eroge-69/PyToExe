import tkinter as tk
from tkinter import ttk

def process_scan(*args):
    raw_input = scan_var.get()
    if "MAC:" in raw_input:
        processed = raw_input.split("MAC:")[0].strip()
    else:
        processed = raw_input.strip()
    result_var.set(processed)

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(result_var.get())
    root.update()

# Create main window
root = tk.Tk()
root.title("S/N Scanner")
root.geometry("500x220")

# Main frame
frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

# Title label at the top
title_label = ttk.Label(frame, text="EMB6-BRD-SOM S/N Scanner", font=("Arial", 16, "bold"))
title_label.pack(pady=(0, 10))

# Entry field with tracking
scan_var = tk.StringVar()
scan_var.trace_add("write", process_scan)

scan_entry = ttk.Entry(frame, textvariable=scan_var, width=50, font=("Arial", 14))
scan_entry.pack(pady=10)

# Result display and copy button
result_var = tk.StringVar()
result_frame = ttk.Frame(frame)
result_frame.pack()

result_label = ttk.Label(result_frame, textvariable=result_var, font=("Arial", 12))
result_label.pack(side="left", padx=(0, 10))

copy_button = ttk.Button(result_frame, text="Copy", command=copy_to_clipboard)
copy_button.pack(side="left")

# Autofocus on scan input
scan_entry.focus()

root.mainloop()
