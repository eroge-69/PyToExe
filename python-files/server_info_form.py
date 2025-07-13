
import tkinter as tk
from tkinter import ttk, messagebox
from openpyxl import load_workbook
import os

EXCEL_FILE = "server_info.xlsx"

def submit_form():
    data = [entry.get() for entry in entries]
    hardware_type = hardware_type_var.get()
    data.append(hardware_type)

    if not all(data):
        messagebox.showwarning("Incomplete", "Please fill in all fields.")
        return

    if not os.path.exists(EXCEL_FILE):
        messagebox.showerror("Missing File", f"{EXCEL_FILE} not found.")
        return

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active
    ws.append(data)
    wb.save(EXCEL_FILE)
    messagebox.showinfo("Success", "Data saved successfully!")
    for e in entries:
        e.delete(0, tk.END)

root = tk.Tk()
root.title("Server Info Entry Form")

fields = ["Host Name", "Serial No.", "IP Address", "CPU", "RAM", "HDD/SSD", "Server Name / Host #"]
entries = []

for i, field in enumerate(fields):
    tk.Label(root, text=field).grid(row=i, column=0, sticky="e", padx=5, pady=2)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

tk.Label(root, text="Hardware Type").grid(row=len(fields), column=0, sticky="e", padx=5, pady=2)
hardware_type_var = tk.StringVar(value="Physical Server")
ttk.Combobox(root, textvariable=hardware_type_var, values=["Physical Server", "VM"]).grid(row=len(fields), column=1, padx=5, pady=2)

tk.Button(root, text="Submit", command=submit_form).grid(row=len(fields)+1, columnspan=2, pady=10)

root.mainloop()
