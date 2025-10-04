import tkinter as tk
from tkinter import messagebox
import win32print

def print_label():
    color = color_entry.get().strip()
    weight = weight_entry.get().strip()
    karat = karat_entry.get().strip()
    tdw = tdw_entry.get().strip()
    price = price_entry.get().strip()

    if not (color and weight and karat and tdw and price):
        messagebox.showwarning("Missing Data", "Please fill out all fields before printing.")
        return

    # EPL label 2.5×2.5 cm, slightly right (~0.3cm), original Y, smaller font
    epl = f"""
N
q400
Q200,24
D20
S2
A18,10,0,1,1,1,N,"Colour:"
A88,10,0,1,1,1,N,"{color}"
A18,50,0,1,1,1,N,"Weight:"
A88,50,0,1,1,1,N,"{weight}"
A18,90,0,1,1,1,N,"Karat:"
A88,90,0,1,1,1,N,"{karat}"
A18,130,0,1,1,1,N,"TDW:"
A88,130,0,1,1,1,N,"{tdw}"
A18,170,0,1,1,1,N,"Price:"
A88,170,0,1,1,1,N,"${price}"
P1
"""

    printer_name = "ZDesigner TLP 2824"

    try:
        hprinter = win32print.OpenPrinter(printer_name)
        win32print.StartDocPrinter(hprinter, 1, ("EPL Label", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, epl.encode("utf-8"))
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)
        messagebox.showinfo("Success", "Label sent to printer successfully!")
    except Exception as e:
        messagebox.showerror("Printing Error", f"Could not print label:\n{e}")

# ---------------- GUI ----------------
root = tk.Tk()
root.title("ZDesigner TLP 2824 Label Printer")
root.geometry("300x260")
root.resizable(False, False)

tk.Label(root, text="Colour:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
color_entry = tk.Entry(root, width=25)
color_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Weight:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
weight_entry = tk.Entry(root, width=25)
weight_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Karat:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
karat_entry = tk.Entry(root, width=25)
karat_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="TDW:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
tdw_entry = tk.Entry(root, width=25)
tdw_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(root, text="Price:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
price_entry = tk.Entry(root, width=25)
price_entry.grid(row=4, column=1, padx=5, pady=5)

print_button = tk.Button(
    root, text="Print Label", command=print_label,
    bg="#4CAF50", fg="white", width=20
)
print_button.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
