# -*- coding: utf-8 -*-
"""
Nokia SAA Test Name → OID Index Converter (English Version)
------------------------------------------------------------
Interactive GUI tool: enter your SAA Test name, and get the
corresponding Nokia SNMP OID index (ASCII formatted).
"""

import tkinter as tk
from tkinter import messagebox

def to_oid_index(test_name, owner="TiMOS CLI"):
    """Convert SAA test name + owner to Nokia OID index format"""
    owner_bytes = [str(ord(c)) for c in owner]
    test_bytes = [str(ord(c)) for c in test_name]
    owner_index = f"{len(owner)}." + ".".join(owner_bytes)
    test_index = f"{len(test_name)}." + ".".join(test_bytes)
    full_index = f"{owner_index}.{test_index}"
    return owner_index, test_index, full_index

def generate_oid():
    test_name = entry.get().strip()
    if not test_name:
        messagebox.showwarning("Input Error", "Please enter the SAA Test name first.")
        return
    owner_index, test_index, full_index = to_oid_index(test_name)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"=== Nokia SAA OID Encoder ===\n")
    result_text.insert(tk.END, f"Test name : {test_name}\n")
    result_text.insert(tk.END, f"Owner     : TiMOS CLI\n\n")
    result_text.insert(tk.END, f"Owner part : {owner_index}\n")
    result_text.insert(tk.END, f"Test part  : {test_index}\n\n")
    result_text.insert(tk.END, f"➡️ Full OID index:\n{full_index}\n\n")
    result_text.insert(tk.END, f"Example usage:\n")
    result_text.insert(tk.END, f"  1.3.6.1.4.1.6527.3.1.2.11.1.4.1.6.{full_index}.<RunID>\n")

# Create GUI window
window = tk.Tk()
window.title("Nokia SAA → OID Converter")
window.geometry("700x500")
window.resizable(False, False)
window.configure(bg="#1e1e1e")

label = tk.Label(window, text="Enter SAA Test name:", fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
label.pack(pady=10)

entry = tk.Entry(window, width=40, font=("Consolas", 12))
entry.pack(pady=5)

btn = tk.Button(window, text="Convert to OID", command=generate_oid, bg="#0078d7", fg="white", font=("Segoe UI", 11), relief="ridge", width=20)
btn.pack(pady=10)

result_text = tk.Text(window, wrap="word", height=18, width=80, font=("Consolas", 11), bg="#2d2d2d", fg="#dcdcdc")
result_text.pack(padx=10, pady=10)

window.mainloop()
