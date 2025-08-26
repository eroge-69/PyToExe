import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os

# ⚠️ Update these paths
FILE_PATH = r"\\cpmasisi01\common\GSC_FEDEX_ASHLAND_DC\128_Canada\records.csv"       # CSV to save records
COUNTRIES_FILE = r"\\cpmasisi01\common\GSC_FEDEX_ASHLAND_DC\128_Canada\countries.txt"  # TXT with country list


def load_countries():
    """Load country list from TXT file on network drive."""
    if not os.path.isfile(COUNTRIES_FILE):
        messagebox.showerror("Error", f"Countries file not found:\n{COUNTRIES_FILE}")
        return []
    with open(COUNTRIES_FILE, "r", encoding="utf-8") as f:
        countries = [line.strip() for line in f if line.strip()]
    return countries


def save_record(hu, country):
    """Append record to CSV on network drive."""
    folder = os.path.dirname(FILE_PATH)
    if not os.path.exists(folder):
        messagebox.showerror("Error", f"Network folder not found:\n{folder}")
        return False

    file_exists = os.path.isfile(FILE_PATH)

    try:
        with open(FILE_PATH, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["HU", "Country of Origin"])
            writer.writerow([hu, country])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not save record:\n{e}")
        return False


def submit():
    hu = entry_hu.get().strip()
    country = combo_country.get().strip()

    if not hu or not country:
        messagebox.showwarning("Missing Data", "Please enter both HU and select a Country of Origin.")
        return

    if save_record(hu, country):
        messagebox.showinfo("Success", "Record saved successfully!")
        entry_hu.delete(0, tk.END)
        combo_country.set("")


# ---------------- GUI ----------------
root = tk.Tk()
root.title("Record Entry - HU & Country of Origin")
root.geometry("400x240")

# HU
label_hu = tk.Label(root, text="HU:")
label_hu.pack(pady=5)
entry_hu = tk.Entry(root, width=40)
entry_hu.pack()

# Country of Origin (Combo Box)
label_country = tk.Label(root, text="Country of Origin:")
label_country.pack(pady=5)

countries_list = load_countries()
combo_country = ttk.Combobox(root, values=countries_list, width=37, state="readonly")
combo_country.pack()

# Buttons Frame
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

# Save Button
submit_btn = tk.Button(btn_frame, text="Save Record", command=submit, bg="green", fg="white", width=15)
submit_btn.grid(row=0, column=0, padx=10)

# Exit Button
exit_btn = tk.Button(btn_frame, text="Exit", command=root.destroy, bg="red", fg="white", width=15)
exit_btn.grid(row=0, column=1, padx=10)

root.mainloop()
