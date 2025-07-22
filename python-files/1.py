import os
import re
import openpyxl
from openpyxl.styles import Font
from datetime import datetime

# ✅ Rates for printing (you can edit these if needed)
print_rates = {
    '4R': 6,
    '4X6': 6,
    '5X7': 10,
    '6X8': 12,
    '6X9': 14,
    '8X10': 18,
    '8X12': 20,
    '10X12': 24,
    '10X15': 28,
    '12X15': 32,
    '12X18': 40
}

# ✅ Extract size and quantity per photo from folder name
def get_quantity_from_folder(folder_name):
    folder_name = folder_name.replace(" ", "")
    match = re.match(r'([0-9]+(?:[Rr]|[xX×=][0-9]+))=([0-9]+)$', folder_name)
    if match:
        raw_size = match.group(1)
        quantity = int(match.group(2))
        size = raw_size.replace("=", "X").replace("×", "X").upper()
        return size, quantity
    return None, 0

# ✅ Base folders
base_path = r"D:\02Ganesh Lab"
shops = ["Ganesh Art", "Lalit Art"]
all_sizes = ['4R', '4X6', '5X7', '6X8', '6X9', '8X10', '8X12', '10X12', '10X15', '12X15', '12X18']
output_excel = "Ganesh_Lab_Report_With_Totals.xlsx"

# ✅ Initialize workbook
wb = openpyxl.Workbook()
wb.remove(wb.active)

sheets = {}
monthly_totals = {}

# 🔁 Process folders
for date_folder in sorted(os.listdir(base_path)):
    try:
        date_obj = datetime.strptime(date_folder, "%d.%m.%Y")
        month_number = date_obj.strftime("%m")
        formatted_date = date_obj.strftime("%d-%m-%Y")
    except:
        continue

    for shop in shops:
        shop_path = os.path.join(base_path, date_folder, shop)
        if not os.path.isdir(shop_path):
            continue

        sheet_name = f"{shop} {month_number}"
        if sheet_name not in sheets:
            ws = wb.create_sheet(title=sheet_name)
            header = ["Date"] + all_sizes
            ws.append(header)
            for col in range(1, len(header) + 1):
                ws.cell(row=1, column=col).font = Font(bold=True)
            sheets[sheet_name] = ws
            monthly_totals[sheet_name] = {size: 0 for size in all_sizes}

        ws = sheets[sheet_name]
        size_count = {size: 0 for size in all_sizes}

        for folder in os.listdir(shop_path):
            folder_path = os.path.join(shop_path, folder)
            if not os.path.isdir(folder_path):
                continue

            size, per_photo_qty = get_quantity_from_folder(folder)
            if not size or size not in size_count:
                continue

            photo_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
            total = photo_count * per_photo_qty
            size_count[size] += total
            monthly_totals[sheet_name][size] += total

        row = [formatted_date] + [size_count[size] for size in all_sizes]
        ws.append(row)

# ✅ Add monthly total row at end of each sheet
for sheet_name, ws in sheets.items():
    last_row = ws.max_row + 1
    ws.cell(row=last_row, column=1).value = "TOTAL"
    ws.cell(row=last_row, column=1).font = Font(bold=True)

    total_amount = 0
    for col, size in enumerate(all_sizes, start=2):
        qty = monthly_totals[sheet_name][size]
        ws.cell(row=last_row, column=col).value = qty
        ws.cell(row=last_row, column=col).font = Font(bold=True)
        rate = print_rates.get(size, 0)
        total_amount += qty * rate

    # ✅ Add grand total amount
    ws.cell(row=last_row + 1, column=1).value = "Total Amount ₹"
    ws.cell(row=last_row + 1, column=2).value = total_amount
    ws.cell(row=last_row + 1, column=1).font = Font(bold=True)
    ws.cell(row=last_row + 1, column=2).font = Font(bold=True)

# 💾 Save workbook
wb.save(output_excel)
print(f"✅ Report with monthly totals and amounts saved as: {output_excel}")
