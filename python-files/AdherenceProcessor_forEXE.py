
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import timedelta
import os

# GUI for file selection
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select Raw Patient Adherence Excel File", filetypes=[("Excel files", "*.xlsx *.xls")])

if not file_path:
    raise Exception("No file selected.")

# Load raw data
raw_df = pd.read_excel(file_path)

# Standardize column names
raw_df.columns = raw_df.columns.str.strip().str.lower()
required_columns = ['patient id', 'delivery date', 'days supplied']

# Check required columns
if not all(col in raw_df.columns for col in required_columns):
    raise ValueError(f"Missing one or more required columns: {required_columns}")

# Drop rows with missing required fields
clean_df = raw_df.dropna(subset=['patient id', 'delivery date', 'days supplied']).copy()

# Normalize types
clean_df['delivery date'] = pd.to_datetime(clean_df['delivery date'])
clean_df['days supplied'] = clean_df['days supplied'].astype(int)

# Sort by patient and date
clean_df.sort_values(by=['patient id', 'delivery date'], inplace=True)

# Processed DataFrame
processed_rows = []
for patient_id, group in clean_df.groupby('patient id'):
    group = group.sort_values('delivery date').reset_index(drop=True)
    for i in range(len(group)):
        row = group.loc[i].to_dict()
        row['days between'] = (group.loc[i, 'delivery date'] - group.loc[i - 1, 'delivery date']).days if i > 0 else ""
        row['expected delivery'] = (group.loc[i - 1, 'delivery date'] + timedelta(days=group.loc[i - 1, 'days supplied'])) if i > 0 else ""
        row['days late'] = (group.loc[i, 'delivery date'] - row['expected delivery']).days if i > 0 else ""
        row['is late'] = 1 if i > 0 and row['days late'] > 5 else 0
        processed_rows.append(row)

processed_df = pd.DataFrame(processed_rows)

# Adherence Summary
summary = processed_df.groupby('patient id').agg(
    total_refills=('delivery date', 'count'),
    late_refills=('is late', 'sum'),
    first_delivery=('delivery date', 'min'),
    last_delivery=('delivery date', 'max'),
    total_supplied=('days supplied', 'sum')
).reset_index()

summary['total_days'] = (summary['last_delivery'] - summary['first_delivery']).dt.days
summary['avg_days_between'] = summary['total_days'] / (summary['total_refills'] - 1)
summary['mpr (%)'] = (summary['total_supplied'] / summary['total_days'] * 100).round(1)
summary['% late refills'] = (summary['late_refills'] / summary['total_refills'] * 100).round(1)

# Output path
output_path = os.path.splitext(file_path)[0] + "_Adherence_Output.xlsx"

# Write to Excel with formatting
with pd.ExcelWriter(output_path, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
    raw_df.to_excel(writer, sheet_name='Raw Data', index=False)
    processed_df.to_excel(writer, sheet_name='Processed Data', index=False)
    summary.to_excel(writer, sheet_name='Adherence Summary', index=False)

    # Apply conditional formatting to MPR column
    workbook = writer.book
    worksheet = writer.sheets['Adherence Summary']
    red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    yellow = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})

    mpr_col = summary.columns.get_loc('mpr (%)')  # zero-based index
    start_row = 1
    end_row = len(summary)
    col_letter = chr(65 + mpr_col)

    worksheet.conditional_format(f'{col_letter}{start_row+1}:{col_letter}{end_row+1}', {
        'type': 'cell',
        'criteria': '<',
        'value': 90,
        'format': red
    })
    worksheet.conditional_format(f'{col_letter}{start_row+1}:{col_letter}{end_row+1}', {
        'type': 'cell',
        'criteria': '<',
        'value': 100,
        'format': yellow
    })

print(f"✅ Done! Output saved to: {output_path}")
