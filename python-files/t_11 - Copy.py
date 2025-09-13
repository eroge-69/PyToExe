import tkinter as tk
from tkinter import ttk
import os
import csv

# Max length for each field
MAX_LEN = {
    "barcode": 19,   # 19 digits
    "KLASA": 1,      # single digit/char
    "PALETA": 3
}

def validate_numeric(P):
    """Allow only numbers in the entry fields."""
    return P.isdigit() or P == ""

def format_barcode(code: str) -> str:
    """Format the 19-digit code into groups separated by tabs."""
    if len(code) != 19 or not code.isdigit():
        raise ValueError("Barcode must be exactly 19 digits")

    parts = [
        code[0:5],   # first 5
        code[5:10],  # next 5
        code[10:12], # 2
        code[12:14], # 2
        code[14:17], # 3
        code[17:19]  # 2
    ]
    return "\t".join(parts)

def on_barcode_change(*args):
    """Auto-jump to KLASA when barcode is full."""
    if len(fields["barcode"].get()) >= MAX_LEN["barcode"]:
        entries["KLASA"].focus_set()

def on_klasa_change(*args):
    """Auto-jump to PALETA when KLASA is full."""
    if len(fields["KLASA"].get()) >= MAX_LEN["KLASA"]:
        entries["PALETA"].focus_set()

def confirm(event=None):
    """Save values to a CSV (TSV) file depending on KLASA, then reset form."""
    barcode = fields["barcode"].get()
    klasa = fields["KLASA"].get()
    paleta = fields["PALETA"].get()

    if barcode and klasa and paleta:
        try:
            formatted_barcode = format_barcode(barcode)
        except ValueError:
            print("Invalid barcode:", barcode)
            return

        # Decide output file based on KLASA
        if klasa == "1":
            filename = "KLASA1.csv"
        elif klasa == "2":
            filename = "KLASA2.csv"
        elif klasa == "3":
            filename = "KLASA3.csv"
        else:
            filename = "temp.csv"

        # Write as CSV (TSV)
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([formatted_barcode, klasa, paleta])

        print(f"Saved to {filename}:", formatted_barcode, klasa, paleta)

    # Clear all fields
    for field in fields:
        fields[field].set("")

    # Reset focus to barcode
    entries["barcode"].focus()

    # Update last 3 entries display (from temp.csv only)
    update_last_entries()

def update_last_entries():
    """Read last 3 entries from temp.csv and display them."""
    if os.path.exists("temp.csv"):
        with open("temp.csv", "r") as f:
            lines = f.readlines()
        last_three = lines[-3:]
    else:
        last_three = []

    last_entries_text.config(state="normal")
    last_entries_text.delete(1.0, tk.END)
    last_entries_text.insert(tk.END, "".join(last_three))
    last_entries_text.config(state="disabled")

root = tk.Tk()
root.title("Input Form")

# Validation: only numbers
vcmd = (root.register(validate_numeric), "%P")

fields = {}
entries = {}

# Create labels + entries
for i, field in enumerate(["barcode", "KLASA", "PALETA"]):
    ttk.Label(root, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="w")
    var = tk.StringVar()
    entry = ttk.Entry(root, textvariable=var, validate="key", validatecommand=vcmd)
    entry.grid(row=i, column=1, padx=5, pady=5)
    fields[field] = var
    entries[field] = entry

# barcode auto-jump
fields["barcode"].trace_add("write", on_barcode_change)

# KLASA auto-jump
fields["KLASA"].trace_add("write", on_klasa_change)

# PALETA Enter → confirm
entries["PALETA"].bind("<Return>", confirm)

# Exit button
exit_button = ttk.Button(root, text="Exit", command=root.destroy)
exit_button.grid(row=3, column=0, columnspan=2, pady=10)

# Last 3 entries display (from temp.csv only)
ttk.Label(root, text="Last 3 entries (temp.csv):").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
last_entries_text = tk.Text(root, height=3, width=60, state="disabled", wrap="none")
last_entries_text.grid(row=4, column=1, padx=5, pady=5)

# Start at barcode
entries["barcode"].focus()

# Load last entries on startup
update_last_entries()

root.mainloop()
