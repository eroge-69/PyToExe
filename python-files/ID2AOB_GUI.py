# ID2AOB_GUI.py
import tkinter as tk
from tkinter import messagebox

def to_aob(n: int, bytes_len: int = 4) -> str:
    return n.to_bytes(bytes_len, byteorder="little", signed=False).hex(" ").upper()

def convert():
    s = entry.get().strip()
    try:
        if s.lower().startswith("0x"):
            dec = int(s, 16)
        else:
            dec = int(s)
        hx = hex(dec).upper()
        aob4 = to_aob(dec, 4)
        aob8 = to_aob(dec, 8)

        result.set(f"Decimal: {dec}\nHex: {hx}\nAOB 4B: {aob4}\nAOB 8B: {aob8}")
    except:
        messagebox.showerror("Error", "Invalid input! Enter Decimal or 0xHex.")

def copy_result():
    root.clipboard_clear()
    root.clipboard_append(result.get())
    root.update()
    messagebox.showinfo("Copied", "Result copied to clipboard!")

# GUI setup
root = tk.Tk()
root.title("ID2AOB Converter")
root.geometry("400x300")

tk.Label(root, text="Enter ID (Decimal or 0xHex):").pack(pady=5)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Convert", command=convert).pack(pady=5)
tk.Button(root, text="Copy", command=copy_result).pack(pady=5)

result = tk.StringVar()
tk.Label(root, textvariable=result, justify="left").pack(pady=10)

root.mainloop()
