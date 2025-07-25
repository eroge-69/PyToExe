#!/usr/bin/env python
# coding: utf-8

# In[4]:


import tkinter as tk
from tkinter import ttk

def calculate_all():
    try:
        entry = float(entry_var.get())
    except:
        entry = None
    try:
        risk = float(risk_var.get())
    except:
        risk = None
    try:
        target = float(target_var.get())
    except:
        target = None
    try:
        sl = float(sl_var.get())
    except:
        sl = None
    try:
        exit_price = float(exit_var.get())
    except:
        exit_price = None

    # Recalculate StopLoss if Entry and Risk % are provided
    if entry is not None and risk is not None:
        sl = entry - (entry * risk / 100)
        sl_var.set(f"{sl:.2f}")

    # Recalculate Risk % if Entry and SL are provided
    if entry is not None and sl is not None:
        risk = ((entry - sl) / entry) * 100
        risk_var.set(f"{risk:.2f}")

    # Recalculate Exit if Entry and Target % are provided
    if entry is not None and target is not None:
        exit_price = entry + (entry * target / 100)
        exit_var.set(f"{exit_price:.2f}")

    # Recalculate Target % if Entry and Exit are provided
    if entry is not None and exit_price is not None:
        target = ((exit_price - entry) / entry) * 100
        target_var.set(f"{target:.2f}")

def clear_all():
    entry_var.set("")
    risk_var.set("")
    target_var.set("")
    sl_var.set("")
    exit_var.set("")

# Create GUI
root = tk.Tk()
root.title("Trading Calculator")
root.geometry("380x380")
root.configure(bg="#e0eafc")

frame = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

# Title
title = tk.Label(frame, text="Trading Calculator", font=("Segoe UI", 16, "bold"), fg="#247ba0", bg="white")
title.pack(pady=10)

# Input section
fields = [("Entry Price:", "entry_var"),
          ("Risk %:", "risk_var"),
          ("Target %:", "target_var"),
          ("StopLoss:", "sl_var"),
          ("Exit Price:", "exit_var")]

vars_dict = {}
for label_text, var_name in fields:
    var = tk.StringVar()
    vars_dict[var_name] = var
    row = tk.Frame(frame, bg="white")
    row.pack(pady=6, padx=10, fill="x")
    label = tk.Label(row, text=label_text, width=14, anchor="w", bg="white", fg="#333a4d", font=("Segoe UI", 10))
    label.pack(side=tk.LEFT)
    entry = tk.Entry(row, textvariable=var, width=18, font=("Segoe UI", 10), relief=tk.SOLID, bd=1)
    entry.pack(side=tk.RIGHT, fill="x", expand=True)

entry_var = vars_dict["entry_var"]
risk_var = vars_dict["risk_var"]
target_var = vars_dict["target_var"]
sl_var = vars_dict["sl_var"]
exit_var = vars_dict["exit_var"]

# Buttons
button_frame = tk.Frame(frame, bg="white")
button_frame.pack(pady=15)

calc_btn = tk.Button(button_frame, text="Calculate", bg="#37c6ff", fg="white", font=("Segoe UI", 10, "bold"),
                     padx=10, pady=5, relief=tk.FLAT, command=calculate_all)
calc_btn.grid(row=0, column=0, padx=10)

clear_btn = tk.Button(button_frame, text="Clear", bg="#6f85ee", fg="white", font=("Segoe UI", 10, "bold"),
                      padx=10, pady=5, relief=tk.FLAT, command=clear_all)
clear_btn.grid(row=0, column=1, padx=10)

root.mainloop()


# In[ ]:




