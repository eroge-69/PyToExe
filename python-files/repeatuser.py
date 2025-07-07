import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def process_file():
    try:
        # Open file dialog
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        # Read the Excel file
        xls = pd.ExcelFile(file_path)
        df = xls.parse('Table1')

        # Rename relevant columns
        df = df.rename(columns={
            'Machine Name': 'Location',
            'Settlement Value (Vend Price)': 'Transaction Value',
            'Card Number': 'Card Number'
        })

        # Group by Location and Card Number
        grouped = df.groupby(['Location', 'Card Number']).size().reset_index(name='Transaction Count')

        # Split into repeat and single-use cards
        repeat_cards = grouped[grouped['Transaction Count'] > 1]
        single_use_cards = grouped[grouped['Transaction Count'] == 1]

        # Summaries
        repeat_counts = repeat_cards.groupby('Location')['Card Number'].nunique().reset_index(name='Repeat Card Count')
        repeat_card_values = df[df['Card Number'].isin(repeat_cards['Card Number'])]
        avg_transaction_repeat = repeat_card_values.groupby('Location')['Transaction Value'].mean().reset_index(name='Avg Transaction (Repeat Cards)')
        single_use_counts = single_use_cards.groupby('Location')['Card Number'].nunique().reset_index(name='Single-use Card Count')

        # Merge summaries
        report = repeat_counts.merge(avg_transaction_repeat, on='Location', how='outer')
        report = report.merge(single_use_counts, on='Location', how='outer')
        report = report.fillna({
            'Repeat Card Count': 0,
            'Avg Transaction (Repeat Cards)': 0,
            'Single-use Card Count': 0
        })

        # Save report to Desktop
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = os.path.join(desktop_path, "transaction_card_usage_report.xlsx")
        report.to_excel(output_path, index=False)

        messagebox.showinfo("Success", f"Report saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Build GUI
root = tk.Tk()
root.title("Card Usage Report Generator")
root.geometry("400x200")

label = tk.Label(root, text="Generate card usage report by location", font=("Arial", 12))
label.pack(pady=20)

btn = tk.Button(root, text="Select Excel File", command=process_file, font=("Arial", 10))
btn.pack(pady=10)

root.mainloop()
