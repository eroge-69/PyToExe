import tkinter as tk
from tkinter import messagebox, filedialog
import os

# === Global Variable ===
total = 0

# === Functions ===
def add_item():
    try:
        item = entry_product.get()
        qty = int(entry_qty.get())
        price = float(entry_price.get())
        amount = qty * price
        invoice_listbox.insert(tk.END, f"{item:<30} {amount}")
        global total
        total += amount
        total_label.config(text=f"Total: {total}")
        entry_product.delete(0, tk.END)
        entry_qty.delete(0, tk.END)
        entry_price.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Please enter valid values")

def save_invoice():
    file = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file:
        for i in range(invoice_listbox.size()):
            file.write(invoice_listbox.get(i) + "\n")
        file.write(f"\nTotal: {total}")
        file.close()
        messagebox.showinfo("Saved", "Invoice saved successfully!")

def delete_item():
    try:
        selected_index = invoice_listbox.curselection()
        if selected_index:
            item_text = invoice_listbox.get(selected_index)
            amount = int(item_text.split()[-1])
            global total
            total -= amount
            total_label.config(text=f"Total: {total}")
            invoice_listbox.delete(selected_index)
        else:
            messagebox.showwarning("Warning", "Please select an item to delete.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def print_invoice():
    try:
        file = open("invoice_temp.txt", "w", encoding="utf-8")
        for i in range(invoice_listbox.size()):
            file.write(invoice_listbox.get(i) + "\n")
        file.write(f"\nTotal: {total}")
        file.close()
        # os.startfile("invoice_temp.txt", "print")  ← تم التعليق عليه مؤقتاً لتفادي الخطأ أثناء التحويل لـ EXE
    except Exception as e:
        messagebox.showerror("Error", f"Printing failed: {e}")

# === UI Setup ===
window = tk.Tk()
window.title("Invoice Generator")
window.geometry("500x600")
window.config(bg="white")

# Title
title_label = tk.Label(window, text="Invoice Generator", font=("Arial", 16, "bold"), bg="white")
title_label.pack(pady=10)

# Customer Name
tk.Label(window, text="Customer Name:", bg="white").pack()
entry_customer = tk.Entry(window)
entry_customer.pack()

# Product
tk.Label(window, text="Product/Service:", bg="white").pack()
entry_product = tk.Entry(window)
entry_product.pack()

# Quantity
tk.Label(window, text="Quantity:", bg="white").pack()
entry_qty = tk.Entry(window)
entry_qty.pack()

# Price
tk.Label(window, text="Price per Unit:", bg="white").pack()
entry_price = tk.Entry(window)
entry_price.pack()

# Add Item Button
btn_add = tk.Button(window, text="Add Item", command=add_item, bg="#c3f2b5")
btn_add.pack(pady=5)

# Listbox
invoice_listbox = tk.Listbox(window, width=50)
invoice_listbox.pack(pady=10)

# Total Label
total_label = tk.Label(window, text="Total: 0", bg="white", font=("Arial", 12, "bold"))
total_label.pack()

# Save Button
btn_save = tk.Button(window, text="Save as PDF", command=save_invoice, bg="#d0e0ff")
btn_save.pack(pady=5)

# Delete Button
btn_delete = tk.Button(window, text="Delete Selected Item", command=delete_item, bg="#ff9999")
btn_delete.pack(pady=5)

# Print Button
btn_print = tk.Button(window, text="Print Invoice", command=print_invoice, bg="#ccffcc")
btn_print.pack(pady=5)

# Signature
signature_label = tk.Label(window, text="Designed by Eng. Ruaa Aziz Al-Mousawi @Ruaa0aziz", fg="gray", bg="white", font=("Arial", 8))
signature_label.pack(side="left", padx=10, pady=10)

window.mainloop()