import pandas as pd
import xlsxwriter

# Sample dummy dataframes (replace these with your actual data)
df = pd.DataFrame({
    'Load ID': [101, 102, 103],
    'Origin': ['Toronto', 'Ottawa', 'London'],
    'Destination': ['Montreal', 'Kingston', 'Windsor'],
    'Status': ['Dispatched', 'In Transit', 'Delivered']
})

df_driver_updates = pd.DataFrame({
    'Driver': ['John Doe', 'Jane Smith'],
    'Check-in Time': ['2025-03-01 09:00', '2025-03-01 10:30'],
    'Location': ['Toronto', 'Ottawa'],
    'Update': ['On route', 'Delayed']
})

df_rate_confirmation = pd.DataFrame({
    'Load ID': [101, 103],
    'Rate Confirmed': [2500, 3200],
    'Carrier': ['Carrier A', 'Carrier B']
})

def autofit_columns(worksheet, df):
    for i, col in enumerate(df.columns):
        max_len = max(
            df[col].astype(str).map(len).max(),
            len(str(col))
        )
        worksheet.set_column(i, i, max_len + 2)

output_file = "/mnt/data/Dispatch_Portfolio_Complete_With_Cover.xlsx"

with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    # Write dataframes to sheets
    df.to_excel(writer, sheet_name="Load Board", index=False)
    autofit_columns(writer.sheets["Load Board"], df)

    df_driver_updates.to_excel(writer, sheet_name="Driver Check-ins", index=False)
    autofit_columns(writer.sheets["Driver Check-ins"], df_driver_updates)

    df_rate_confirmation.to_excel(writer, sheet_name="Rate Confirmation", index=False)
    autofit_columns(writer.sheets["Rate Confirmation"], df_rate_confirmation)

    # Add Cover Page
    workbook = writer.book
    worksheet = workbook.add_worksheet("Cover Page")
    writer.sheets["Cover Page"] = worksheet

    # Formats
    bold_center = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 14
    })
    normal_center = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 12
    })

    # Optionally adjust column widths and row heights on cover page
    worksheet.set_column('B:J', 30)  # set wide enough columns
    for row in range(3, 9):
        worksheet.set_row(row, 25)  # set row height

    # Merge cells and add text
    worksheet.merge_range('B3:J3', 'DISPATCH TRAINING PORTFOLIO', bold_center)
    worksheet.merge_range('B5:J5', 'Prepared by: Vijaykumar Ramlalit Yadav', normal_center)
    worksheet.merge_range('B6:J6', 'Role: Freelance Dispatcher (Unpaid Learning Project)', normal_center)
    worksheet.merge_range('B7:J7', 'Period: March – May 2025', normal_center)
    worksheet.merge_range('B8:J8', 'Location: Ontario, Canada (Remote)', normal_center)

print(f"Excel file saved to {output_file}")
