
import tkinter as tk
import csv
import os
from datetime import datetime

APP_NAME = "Business Calculator"

def records_dir():
    # Prefer Documents\BusinessCalculator on Windows; fallback to home
    home = os.path.expanduser("~")
    documents = os.path.join(home, "Documents")
    target_dir = os.path.join(documents if os.path.isdir(documents) else home, "BusinessCalculator")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def records_path():
    return os.path.join(records_dir(), "business_records.csv")

def fmt(n):
    try:
        return f"{n:,.2f}"
    except Exception:
        return str(n)

def get_float(entry):
    txt = entry.get().strip()
    if txt == "":
        return 0.0
    return float(txt)

def calculate():
    try:
        sales = get_float(sales_entry)
        rent = get_float(rent_entry)
        salaries = get_float(salaries_entry)
        internet = get_float(internet_entry)
        other = get_float(other_entry)
        reinvest = get_float(reinvest_entry)
        month = month_entry.get().strip() or datetime.now().strftime("%B %Y")

        total_expenses = rent + salaries + internet + other + reinvest
        profit = sales - total_expenses
        half = profit / 2

        result = (
            f"Month: {month}\n"
            f"Total Sales: {fmt(sales)}\n"
            f"Total Expenses: {fmt(total_expenses)}\n"
            f"Net Profit: {fmt(profit)}\n"
            f"Half 1: {fmt(half)}\n"
            f"Half 2: {fmt(half)}"
        )
        result_label.config(text=result)

        # Save to CSV (record keeping)
        save_record(month, sales, total_expenses, profit, half)

    except ValueError:
        result_label.config(text="Please enter valid numbers only.")

def save_record(month, sales, expenses, profit, half):
    path = records_path()
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Month", "Sales", "Expenses", "Profit", "Half1", "Half2"])
        writer.writerow([month, f"{sales:.2f}", f"{expenses:.2f}", f"{profit:.2f}", f"{half:.2f}", f"{half:.2f}"])

def view_records():
    path = records_path()
    if not os.path.isfile(path):
        result_label.config(text="No records found yet. Click 'Calculate & Save' to add your first month.")
        return

    top = tk.Toplevel(root)
    top.title("Monthly Records")
    top.geometry("760x420")

    # Container with canvas + scrollbar (for many rows)
    container = tk.Frame(top)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    with open(path, "r", encoding="utf-8") as file:
        reader = list(csv.reader(file))

        totals = [0.0, 0.0, 0.0, 0.0, 0.0]  # Sales, Expenses, Profit, Half1, Half2

        for i, row in enumerate(reader):
            for j, value in enumerate(row):
                lbl = tk.Label(scroll_frame, text=value, borderwidth=1, relief="solid", width=18, anchor="w", padx=6, pady=3)
                lbl.grid(row=i, column=j, sticky="nsew")

            if i > 0:  # Skip header
                try:
                    totals[0] += float(row[1])  # Sales
                    totals[1] += float(row[2])  # Expenses
                    totals[2] += float(row[3])  # Profit
                    totals[3] += float(row[4])  # Half1
                    totals[4] += float(row[5])  # Half2
                except Exception:
                    pass

        # Add summary row
        summary_labels = ["TOTAL", fmt(totals[0]), fmt(totals[1]), fmt(totals[2]), fmt(totals[3]), fmt(totals[4])]
        for j, value in enumerate(summary_labels):
            lbl = tk.Label(scroll_frame, text=value, borderwidth=2, relief="ridge", width=18, padx=6, pady=5)
            lbl.grid(row=len(reader), column=j, sticky="nsew")

# Create main window
root = tk.Tk()
root.title(APP_NAME)
root.geometry("430x650")
root.resizable(False, False)

header = tk.Label(root, text="Monthly Business Calculator", font=("Segoe UI", 14, "bold"), pady=8)
header.pack()

# Input fields
def add_field(label_text):
    frame = tk.Frame(root)
    frame.pack(fill="x", padx=12, pady=4)
    tk.Label(frame, text=label_text, width=20, anchor="w").pack(side="left")
    entry = tk.Entry(frame, width=20)
    entry.pack(side="right")
    return entry

month_entry = add_field("Month (e.g., August 2025):")
month_entry.insert(0, datetime.now().strftime("%B %Y"))

sales_entry = add_field("Monthly Sales:")
rent_entry = add_field("Rent:")
salaries_entry = add_field("Salaries:")
internet_entry = add_field("Internet:")
other_entry = add_field("Other Expenses:")
reinvest_entry = add_field("Reinvestment:")

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Calculate & Save", width=18, command=calculate).grid(row=0, column=0, padx=6)
tk.Button(btn_frame, text="View Records", width=18, command=view_records).grid(row=0, column=1, padx=6)

# Result display
result_label = tk.Label(root, text="", justify="left", font=("Segoe UI", 10), padx=12, pady=8, anchor="w")
result_label.pack(fill="both", expand=False)

# Path info
path_info = tk.Label(root, text=f"Records file: {records_path()}", fg="gray")
path_info.pack(pady=6)

root.mainloop()
