import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
import os
from datetime import datetime, timedelta

def scan_csv_files():
    """Scan current directory for CSV files."""
    return [f for f in os.listdir('.') if f.endswith('.csv')]

def generate_output():
    selected_file = file_var.get()
    if not selected_file:
        messagebox.showerror("Error", "Please select a CSV file.")
        return

    # Get dates from calendars
    start_date = start_cal.get_date()
    end_date = end_cal.get_date()

    # Add fixed times
    start_dt = datetime.combine(start_date, datetime.strptime("18:00", "%H:%M").time())
    end_dt = datetime.combine(end_date, datetime.strptime("16:00", "%H:%M").time())

    # If end time is "earlier" than start, assume it's the next day
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    # Load CSV
    try:
        df = pd.read_csv(selected_file, parse_dates=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV: {e}")
        return

    # Detect datetime column
    datetime_col = None
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            datetime_col = col
            break
        except Exception:
            continue

    if not datetime_col:
        messagebox.showerror("Error", "No datetime column found in CSV.")
        return

    # Convert to datetime
    df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")
    df = df.dropna(subset=[datetime_col])

    # Filter between start and end datetime
    mask = (df[datetime_col] >= start_dt) & (df[datetime_col] <= end_dt)
    filtered = df.loc[mask]

    # Save output
    out_file = f"filtered_{selected_file}"
    filtered.to_csv(out_file, index=False)

    messagebox.showinfo("Success", f"Filtered CSV saved as {out_file}")

# GUI setup
root = tk.Tk()
root.title("CSV Date Filter")

# Start date
tk.Label(root, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
start_cal = DateEntry(root, width=12, background='darkblue',
                      foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
start_cal.grid(row=0, column=1, padx=5, pady=5)

# End date
tk.Label(root, text="End Date:").grid(row=1, column=0, padx=5, pady=5)
end_cal = DateEntry(root, width=12, background='darkblue',
                    foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
end_cal.grid(row=1, column=1, padx=5, pady=5)

# File dropdown
tk.Label(root, text="Select CSV File:").grid(row=2, column=0, padx=5, pady=5)
file_var = tk.StringVar()
csv_files = scan_csv_files()
file_menu = ttk.Combobox(root, textvariable=file_var, values=csv_files, state="readonly")
file_menu.grid(row=2, column=1, padx=5, pady=5)

# Generate button
generate_btn = tk.Button(root, text="Generate", command=generate_output)
generate_btn.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
