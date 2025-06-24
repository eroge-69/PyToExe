import tkinter as tk
from tkinter import messagebox

def format_mac(mac_raw: str) -> str:
    mac_clean = ''.join(filter(str.isalnum, mac_raw)).upper()
    if len(mac_clean) != 12:
        return "Error: MAC address must have 12 hexadecimal characters."
    return ':'.join(mac_clean[i:i+2] for i in range(0, 12, 2))

def on_format():
    raw = entry.get()
    result = format_mac(raw)
    output_var.set(result)
    if result.startswith("Error"):
        messagebox.showerror("Invalid Input", result)

def copy_to_clipboard():
    formatted_mac = output_var.get()
    if not formatted_mac or formatted_mac.startswith("Error"):
        messagebox.showwarning("Nothing to Copy", "Please format a valid MAC address first.")
        return
    root.clipboard_clear()
    root.clipboard_append(formatted_mac)
    messagebox.showinfo("Copied", "Formatted MAC address copied to clipboard.")

# GUI setup
root = tk.Tk()
root.title("MAC Address Formatter")
root.geometry("400x180")

tk.Label(root, text="Enter MAC address (e.g., AABBCCDDEEFF):").pack(pady=5)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Format", command=on_format).pack(pady=5)

output_var = tk.StringVar()
output_label = tk.Label(root, textvariable=output_var, font=("Courier", 12), fg="blue")
output_label.pack(pady=5)

tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=5)

root.mainloop()
