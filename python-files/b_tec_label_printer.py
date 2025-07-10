import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

customers = {}

# Load saved customers
try:
    with open("customers.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                customers[row[0]] = row[1]
except FileNotFoundError:
    pass

def save_customer(name, address):
    customers[name] = address
    with open("customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name, address in customers.items():
            writer.writerow([name, address])

def print_label():
    name = customer_name.get()
    address = customer_address.get("1.0", tk.END).strip()
    qty = ink_qty.get()
    price = ink_price.get()

    if not name or not address or not qty or not price:
        messagebox.showwarning("Missing Info", "Fill all fields.")
        return

    try:
        total = float(qty) * float(price)
    except ValueError:
        messagebox.showerror("Invalid Input", "Qty and Price must be numbers.")
        return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    label_data = f"""
From:
B Tech Digital
Thushara
Kithulawa, Kalutara South
0766689175
Date: {date_str}

To:
{name}
{address}

Ink Qty: {qty}
Price: Rs. {price}
Total: Rs. {total:.2f}
"""

    # Show preview
    preview_window = tk.Toplevel(root)
    preview_window.title("Label Preview")
    tk.Label(preview_window, text=label_data, justify="left", font=("Courier New", 10)).pack(padx=10, pady=10)
    tk.Button(preview_window, text="Print", command=preview_window.destroy).pack(pady=5)

    # Save record
    with open("label_records.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date_str, name, address, qty, price, f"{total:.2f}"])

    save_customer(name, address)

def autofill_address(event):
    name = customer_name.get()
    if name in customers:
        customer_address.delete("1.0", tk.END)
        customer_address.insert(tk.END, customers[name])

def export_report():
    total_sale = 0
    total_qty = 0
    try:
        with open("label_records.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
    except FileNotFoundError:
        messagebox.showinfo("No Data", "No label records found.")
        return

    month = datetime.now().strftime("%Y-%m")
    report_data = [["Date", "Name", "Address", "Qty", "Price", "Total"]]
    for row in data:
        if row[0].startswith(month):
            report_data.append(row)
            try:
                total_sale += float(row[5])
                total_qty += float(row[3])
            except:
                pass

    report_data.append([])
    report_data.append(["", "", "", f"Total Qty: {total_qty}", "", f"Total Sales: Rs. {total_sale:.2f}"])

    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(report_data)
        messagebox.showinfo("Exported", f"Report saved as:\n{file}")

# GUI Setup
root = tk.Tk()
root.title("B Tec Customer Label")
root.geometry("500x450")

tk.Label(root, text="Customer Name").pack()
customer_name = ttk.Combobox(root, values=list(customers.keys()))
customer_name.pack()
customer_name.bind("<<ComboboxSelected>>", autofill_address)

tk.Label(root, text="Customer Address").pack()
customer_address = tk.Text(root, height=3)
customer_address.pack()

tk.Label(root, text="Ink Quantity").pack()
ink_qty = tk.Entry(root)
ink_qty.pack()

tk.Label(root, text="Price (Rs.)").pack()
ink_price = tk.Entry(root)
ink_price.pack()

tk.Button(root, text="Print Label", command=print_label).pack(pady=10)
tk.Button(root, text="Monthly Report", command=export_report).pack(pady=5)

root.mainloop()
