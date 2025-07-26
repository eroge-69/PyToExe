import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import sys

# Load data from CSV (same folder)
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_path, "morajieen_data.csv")
df = pd.read_csv(data_path)

def search():
    query = entry.get().strip()
    filter_type = filter_var.get()
    results_list.delete(0, tk.END)

    if query == "":
        return

    if filter_type == "يحتوي على":
        results = df[df["NAME"].str.contains(query, case=False, na=False)]
    elif filter_type == "يبدأ بـ":
        results = df[df["NAME"].str.startswith(query, na=False)]
    elif filter_type == "ينتهي بـ":
        results = df[df["NAME"].str.endswith(query, na=False)]
    elif filter_type == "يطابق تمامًا":
        results = df[df["NAME"].str.lower() == query.lower()]
    else:
        results = pd.DataFrame()

    if results.empty:
        results_list.insert(tk.END, "لا توجد نتائج مطابقة")
    else:
        for _, row in results.iterrows():
            results_list.insert(tk.END, f"{row['NAME']} - رقم الملف: {row['MRN']}")

root = tk.Tk()
root.title("المراجعين القدامى")
root.geometry("600x400")
root.configure(bg="white")

entry = tk.Entry(root, font=("Arial", 14), justify="right")
entry.pack(pady=10)

filter_var = tk.StringVar(value="يحتوي على")
filter_menu = ttk.Combobox(root, textvariable=filter_var, font=("Arial", 12), justify="right")
filter_menu["values"] = ["يحتوي على", "يبدأ بـ", "ينتهي بـ", "يطابق تمامًا"]
filter_menu.pack(pady=5)

search_btn = tk.Button(root, text="بحث", command=search, font=("Arial", 14), bg="#0078D7", fg="white")
search_btn.pack(pady=10)

results_list = tk.Listbox(root, font=("Arial", 12), width=80, height=10, justify="right")
results_list.pack(pady=10)

root.mainloop()
