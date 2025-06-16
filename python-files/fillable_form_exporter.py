
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Fields and their types
date_fields = ["Date of Hire:", "EE DOB:", "EE EFF:", "DP DOB:", "DP EFF:"]
special_options = {
    "COB:": ["", "N/A", "?", "NOI", "Medicare"],
    "LASERED:": ["", "N/A", "?", "NONE"],
    "GAPLESS:": ["", "N/A", "?", "NONE"],
    "DOMESTIC:": ["", "N/A", "?", "NONE"],
    "CLAIMS PAID PRIOR YEAR:": ["", "N/A", "?", "NONE"],
    "CHECK FOR DUPLICATES FROM PRIOR YEAR:": ["", "N/A", "?", "NONE"],
    "HOSPITAL AUDIT:": ["", "N/A", "?", "NONE"],
    "ADDITIONAL INFO NEEDED:": ["", "N/A", "?", "NONE"]
}
text_fields = [
    "DISCLOSED:", "WORK STATUS:", "SUMMARY:", "Service Types:"
]

# Combine all fields
all_fields = ["Coverage Analysis Conducted"] + date_fields + list(special_options.keys()) + text_fields

# Create the main application window
root = tk.Tk()
root.title("Fillable Form Exporter")

entries = {}

def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%m/%d/%Y")
        return True
    except ValueError:
        return False

def export_to_txt():
    output_lines = ["Coverage Analysis Conducted\n"]
    for label, widget in entries.items():
        value = widget.get()
        if value == "N/A" or value.strip() == "":
            continue
        if label in date_fields and not validate_date(value):
            messagebox.showerror("Invalid Date", f"Please enter a valid date in mm/dd/yyyy format for '{label}'")
            return
        output_lines.append(f"{label} {value}")
    with open("form_output.txt", "w") as f:
        f.write("\n".join(output_lines))
    messagebox.showinfo("Success", "Form exported to form_output.txt")

# Create form fields
for field in all_fields:
    frame = tk.Frame(root)
    frame.pack(fill="x", padx=10, pady=2)
    label = tk.Label(frame, text=field, width=35, anchor="w")
    label.pack(side="left")
    if field in special_options:
        var = ttk.Combobox(frame, values=special_options[field])
        var.pack(side="left", fill="x", expand=True)
        entries[field] = var
    elif field in date_fields:
        var = tk.Entry(frame)
        var.insert(0, "mm/dd/yyyy")
        var.pack(side="left", fill="x", expand=True)
        entries[field] = var
    elif field in text_fields or field == "Coverage Analysis Conducted":
        var = tk.Entry(frame)
        var.pack(side="left", fill="x", expand=True)
        entries[field] = var

# Export button
export_btn = tk.Button(root, text="Export to TXT", command=export_to_txt)
export_btn.pack(pady=10)

# Run the application
root.mainloop()
