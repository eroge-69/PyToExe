import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os

# Create hidden main window for dialogs
root = tk.Tk()
root.withdraw()

try:
    # Select file
    file_path = filedialog.askopenfilename(
        title="Select your Ledger (.xls) file",
        filetypes=[("Excel files", "*.xls")]
    )
    if not file_path:
        raise Exception("No file selected.")

    # Enter GST rate
    gst_rate = simpledialog.askfloat(
        "GST Rate", "Enter GST rate (%)", minvalue=0, maxvalue=100
    )
    if gst_rate is None:
        raise Exception("No GST rate entered.")

    # Read Excel file
    df = pd.read_excel(file_path)

    if "Total Amount" not in df.columns:
        raise Exception("The file must have a column named 'Total Amount'.")

    # Calculate
    df["Commission (5%)"] = df["Total Amount"] * 0.05
    df["GST Amount"] = df["Commission (5%)"] * (gst_rate / 100)
    df["Total Earning"] = df["Commission (5%)"] + df["GST Amount"]

    # Add Grand Total row
    totals = pd.DataFrame({
        "Total Amount": [df["Total Amount"].sum()],
        "Commission (5%)": [df["Commission (5%)"].sum()],
        "GST Amount": [df["GST Amount"].sum()],
        "Total Earning": [df["Total Earning"].sum()]
    }, index=["Grand Total"])
    df = pd.concat([df, totals])

    # Save processed file
    output_path = os.path.join(os.path.dirname(file_path), "processed_ledger.xlsx")
    df.to_excel(output_path, index=True)

    messagebox.showinfo("Done", f"Processed file saved as:\n{output_path}")

except Exception as e:
    messagebox.showerror("Error", str(e))
