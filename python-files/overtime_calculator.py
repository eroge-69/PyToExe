
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def main():
    # Set up GUI
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("Overtime Calculator", "Please select the Excel file with the sheet 'Arbeitszeiten pro Tag'")
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])

    if not file_path:
        messagebox.showwarning("No File", "No file was selected. Exiting.")
        return

    try:
        df = pd.read_excel(file_path, sheet_name="Arbeitszeiten pro Tag")
    except Exception as e:
        messagebox.showerror("Error", f"Could not read the sheet 'Arbeitszeiten pro Tag'.\n\n{e}")
        return

    # Check required columns
    if df.columns[0] != 'Unnamed: 0':
        df.columns.values[0] = "Employee"  # Rename column A
    if df.columns[12] != 'Unnamed: 12':
        df.columns.values[12] = "Overtime"  # Rename column M

    try:
        df['Employee'] = df['Employee'].astype(str)
        df['Overtime'] = pd.to_numeric(df['Overtime'], errors='coerce').fillna(0.0)
    except Exception as e:
        messagebox.showerror("Error", f"Error processing columns.\n\n{e}")
        return

    # Group and summarize
    summary = df.groupby('Employee', as_index=False)['Overtime'].sum()
    summary['Paid Hours'] = summary['Overtime'].apply(lambda x: round(x - 10, 2) if x > 10 else 0.0)
    summary = summary.sort_values('Employee').reset_index(drop=True)

    # Save output
    output_dir = os.path.dirname(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"Overtime_Report_{timestamp}.xlsx")

    try:
        summary.to_excel(output_file, index=False)
        messagebox.showinfo("Success", f"Overtime report saved as:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save the output file.\n\n{e}")

if __name__ == "__main__":
    main()
