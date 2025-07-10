# Re-run the Excel creation since the tool is now available again.

# Create workbook and worksheet
wb_corrected = Workbook()
ws_corrected = wb_corrected.active
ws_corrected.title = "Contacts 4x16"

# Fill the worksheet to match 4-column and 16-row structure
for row_idx, row in enumerate(structured_data_4x16, start=1):
    for col_idx, (name, phone) in enumerate(row, start=1):
        ws_corrected.cell(row=row_idx, column=col_idx, value=f"{name}\n{phone}")

# Adjust column widths
for col in range(1, 5):
    ws_corrected.column_dimensions[get_column_letter(col)].width = 30

# Save the updated file
final_excel_path = "/mnt/data/contacts_exact_layout_4x16.xlsx"
wb_corrected.save(final_excel_path)

final_excel_path
