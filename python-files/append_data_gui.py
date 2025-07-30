import csv
import os
import tkinter as tk
from tkinter import messagebox

FILENAME = "ael_30072025.csv"
NEW_ROWS = [
    ["NIFTY", "OTH", "2.1", "0", "2.1"],
    ["NIFTY", "OTM", "3.1", "0", "3.1"],
    ["BANKNIFTY", "OTH", "2.1", "0", "2.1"],
    ["BANKNIFTY", "OTM", "3.1", "0", "3.1"],
    ["FINNIFTY", "OTH", "2.1", "0", "2.1"],
    ["FINNIFTY", "OTM", "3.1", "0", "3.1"],
    ["MIDCPNIFTY", "OTH", "2.1", "0", "2.1"],
    ["MIDCPNIFTY", "OTM", "3.1", "0", "3.1"],
    ["NIFTYNXT50", "OTH", "2.1", "0", "2.1"],
    ["NIFTYNXT50", "OTM", "3.1", "0", "3.1"],
]

def get_last_serial(filename):
    last_serial = 0
    if not os.path.exists(filename):
        return last_serial
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].isdigit():
                last_serial = max(last_serial, int(row[0]))
    return last_serial

def append_records():
    try:
        start_serial = get_last_serial(FILENAME) + 1
        with open(FILENAME, "a", newline="") as f:
            writer = csv.writer(f)
            for i, row in enumerate(NEW_ROWS):
                writer.writerow([start_serial + i] + row)
        messagebox.showinfo("Success", "✅ 10 records successfully appended!")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# GUI Setup
window = tk.Tk()
window.title("CSV Record Appender")
window.geometry("300x150")
window.resizable(False, False)

label = tk.Label(window, text="Click below to append records to the CSV file.")
label.pack(pady=20)

run_button = tk.Button(window, text="Run", command=append_records, height=2, width=10, bg="#28a745", fg="white")
run_button.pack()

window.mainloop()
