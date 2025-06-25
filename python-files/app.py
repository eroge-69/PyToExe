# app.py
import tkinter as tk
from tkinter import ttk, messagebox

def on_submit():
    # Do whatever processing you need here…
    # …

    # Show confirmation pop-up
    messagebox.showinfo("Done", "Successful")

root = tk.Tk()
root.title("Two-Text Demo")
root.geometry("400x220")        # width x height
root.resizable(False, False)    # disable window resize

# --- Widgets ---
ttk.Label(root, text="First text:").pack(anchor="w", padx=15, pady=(15, 0))
entry1 = ttk.Entry(root, width=40)
entry1.pack(padx=15)

ttk.Label(root, text="Second text:").pack(anchor="w", padx=15, pady=(15, 0))
entry2 = ttk.Entry(root, width=40)
entry2.pack(padx=15)

ttk.Button(root, text="Submit", command=on_submit).pack(pady=20)

root.mainloop()
