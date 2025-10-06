import tkinter as tk
from tkinter import ttk

def toggle_checkbox():
    status_label.config(text="Status: ON" if aimboost_var.get() else "Status: OFF")

# Create the main window
root = tk.Tk()
root.title("Devil Shop")
root.geometry("300x200")  # Set window size

# Add a label for the title "Devil Shop" at the top
title_label = ttk.Label(root, text="Devil Shop", font=("Arial", 16, "bold"))
title_label.pack(pady=20)

# Create a BooleanVar to track checkbox state
aimboost_var = tk.BooleanVar()

# Create the Aimboost checkbox
aimboost_checkbox = ttk.Checkbutton(root, text="Aimboost", variable=aimboost_var, command=toggle_checkbox)
aimboost_checkbox.pack(pady=10)

# Create a label to display ON/OFF status
status_label = ttk.Label(root, text="Status: OFF", font=("Arial", 12))
status_label.pack(pady=10)

# Start the main event loop
root.mainloop()