import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
import os
import pandas as pd
import tempfile
import win32print
import win32api

# Basic setup
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("800x600")
app.title("Ice Cream Billing System")

# Global variables
invoice_number = 1
order_data = []

flavors = {
    "Vanilla": 100,
    "Chocolate": 120,
    "Strawberry": 110,
    "Mango": 130
}

# Header
header = ctk.CTkLabel(app, text="Ice Cream Billing", font=("Arial", 24, "bold"))
header.pack(pady=10)

# Frame for flavor selection
selection_frame = ctk.CTkFrame(app)
selection_frame.pack(pady=10)

selected_items = {}

def update_bill():
    global selected_items
    bill_textbox.delete("1.0", "end")
    total = 0
    bill_textbox.insert("end", f"Invoice #: {invoice_number}\n")
    bill_textbox.insert("end", f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    bill_textbox.insert("end", "\nItem\tQty\tPrice\n")
    bill_textbox.insert("end", "----------------------------\n")
    for item, qty in selected_items.items():
        if qty > 0:
            price = flavors[item] * qty
            total += price
            bill_textbox.insert("end", f"{item}\t{qty}\t{price}\n")
    bill_textbox.insert("end", f"\nTotal: {total} PKR")

    return total

def add_item(flavor):
    selected_items[flavor] = selected_items.get(flavor, 0) + 1
    update_bill()

def remove_item(flavor):
    if selected_items.get(flavor, 0) > 0:
        selected_items[flavor] -= 1
    update_bill()

for i, (flavor, price) in enumerate(flavors.items()):
    frame = ctk.CTkFrame(selection_frame)
    frame.grid(row=i, column=0, pady=5, padx=5, sticky="w")
    label = ctk.CTkLabel(frame, text=f"{flavor} ({price} PKR)")
    label.pack(side="left", padx=5)
    add_btn = ctk.CTkButton(frame, text="+", width=30, command=lambda f=flavor: add_item(f))
    add_btn.pack(side="left")
    remove_btn = ctk.CTkButton(frame, text="-", width=30, command=lambda f=flavor: remove_item(f))
    remove_btn.pack(side="left")

# Textbox for bill
bill_textbox = ctk.CTkTextbox(app, width=600, height=200)
bill_textbox.pack(pady=10)

# Save and Print

def save_and_print():
    global invoice_number, selected_items
    if not selected_items:
        messagebox.showwarning("Warning", "No items selected.")
        return

    total = update_bill()
    data = []
    for item, qty in selected_items.items():
        if qty > 0:
            data.append({
                "Invoice": invoice_number,
                "Item": item,
                "Quantity": qty,
                "Price": flavors[item] * qty,
                "Total": total,
                "Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    df = pd.DataFrame(data)
    file_exists = os.path.isfile("sales.xlsx")
    if file_exists:
        existing_df = pd.read_excel("sales.xlsx")
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel("sales.xlsx", index=False)

    # Print
    receipt_text = bill_textbox.get("1.0", "end")
    filename = tempfile.mktemp(".txt")
    with open(filename, "w") as f:
        f.write(receipt_text)

    try:
        printer_name = win32print.GetDefaultPrinter()
        win32api.ShellExecute(0, "print", filename, None, ".", 0)
    except:
        messagebox.showerror("Printer Error", "No printer connected.")

    invoice_number += 1
    selected_items = {}
    update_bill()

save_btn = ctk.CTkButton(app, text="Paid & Print", command=save_and_print)
save_btn.pack(pady=10)

app.mainloop()
