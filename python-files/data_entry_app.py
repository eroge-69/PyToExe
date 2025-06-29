
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

FILE_PATH = "1234.xlsx"

# Load or create DataFrame
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=[
        "Customer No", "Cost Per One", "listing Per One", "Quantity",
        "Cost", "Sell Price", "Profit for Item", "Delivery Cost", "Status"
    ])

def calculate_values(cost_per_one, listing_per_one, quantity, delivery_cost):
    try:
        cost = float(cost_per_one) * float(quantity)
        sell_price = float(listing_per_one) * float(quantity)
        delivery_cost = float(delivery_cost) if delivery_cost else 0
        profit = sell_price - cost - delivery_cost
        return cost, sell_price, profit
    except:
        return None, None, None

def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)

def save_data():
    global df
    try:
        cust_no = entries["Customer No"].get()
        if not cust_no:
            messagebox.showwarning("Validation", "Customer No is required.")
            return

        cost_per_one = entries["Cost Per One"].get()
        listing_per_one = entries["listing Per One"].get()
        quantity = entries["Quantity"].get()
        delivery_cost = entries["Delivery Cost"].get()
        status = entries["Status"].get()

        cost, sell_price, profit = calculate_values(cost_per_one, listing_per_one, quantity, delivery_cost)
        if cost is None:
            messagebox.showerror("Error", "Invalid input in numeric fields.")
            return

        # Remove existing record if exists
        df = df[df["Customer No"] != float(cust_no)]

        # Append new record
        df = pd.concat([df, pd.DataFrame([{
            "Customer No": float(cust_no),
            "Cost Per One": float(cost_per_one),
            "listing Per One": float(listing_per_one),
            "Quantity": float(quantity),
            "Cost": cost,
            "Sell Price": sell_price,
            "Profit for Item": profit,
            "Delivery Cost": float(delivery_cost) if delivery_cost else 0,
            "Status": status
        }])], ignore_index=True)

        df.to_excel(FILE_PATH, index=False)
        messagebox.showinfo("Success", "Record saved successfully.")
        clear_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def search_data():
    try:
        cust_no = entries["Customer No"].get()
        if not cust_no:
            messagebox.showwarning("Validation", "Enter Customer No to search.")
            return

        record = df[df["Customer No"] == float(cust_no)]
        if record.empty:
            messagebox.showinfo("Not Found", "No record found.")
            return

        record = record.iloc[0]
        for col in entries:
            val = record[col]
            entries[col].delete(0, tk.END)
            entries[col].insert(0, str(val))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_data():
    global df
    try:
        cust_no = entries["Customer No"].get()
        if not cust_no:
            messagebox.showwarning("Validation", "Enter Customer No to delete.")
            return

        df = df[df["Customer No"] != float(cust_no)]
        df.to_excel(FILE_PATH, index=False)
        messagebox.showinfo("Deleted", "Record deleted.")
        clear_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Layout
root = tk.Tk()
root.title("Customer Data Entry")
entries = {}

fields = [
    "Customer No", "Cost Per One", "listing Per One", "Quantity",
    "Delivery Cost", "Status"
]

for i, field in enumerate(fields):
    tk.Label(root, text=field).grid(row=i, column=0, sticky=tk.W, pady=2)
    entry = tk.Entry(root)
    entry.grid(row=i, column=1, pady=2)
    entries[field] = entry

tk.Button(root, text="Save / Update", command=save_data).grid(row=len(fields), column=0, pady=5)
tk.Button(root, text="Search", command=search_data).grid(row=len(fields), column=1, pady=5)
tk.Button(root, text="Delete", command=delete_data).grid(row=len(fields)+1, column=0, pady=5)
tk.Button(root, text="Clear", command=clear_fields).grid(row=len(fields)+1, column=1, pady=5)

root.mainloop()
