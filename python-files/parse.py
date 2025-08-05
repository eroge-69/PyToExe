import os
import sys
import csv
from datetime import datetime
from PyPDF2 import PdfReader
import pyodbc

# --- PATH HELPERS ---
def exe_dir():
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

base_dir = exe_dir()

# ✅ Updated path to Forms inside Access Inputs
pdf_folder = os.path.join(base_dir, "Access Inputs", "Forms")
csv_export_folder = os.path.join(base_dir, "Access Inputs", "CSVs")
os.makedirs(csv_export_folder, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_csv = os.path.join(csv_export_folder, f"output_{timestamp}.csv")

access_db = os.path.join(base_dir, "ASUBudgetDB.accdb")
access_table = "Budget Requests"
print(f"🔍 Access DB path: {access_db}")
# ----------------------

def clean_value(col_name, value):
    if value is None or value == "":
        return None  # Convert empty strings to NULL for Access

    numeric_fields = {
        "Supplies (4521) Request",
        "Printing (4531) Request",
        "Food (4581) Request",
        "Contracts (5621) Request",
        "Rentals (5635) Request",
        "Travel (5681) Request",
        "Other (5890) Request",
        "Equipment (6401) Request",
        "Total Requested",
    }

    try:
        if col_name in numeric_fields:
            return float(value.replace(',', ''))
    except Exception:
        return None

    return value

# --- Extract data from all PDFs ---
data_rows = []
fieldnames = set()

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        reader = PdfReader(pdf_path)
        fields = reader.get_form_text_fields()

        if not fields:
            print(f"⚠️ No form fields found in: {filename}")
            continue

        description_lines = []

        # Merge Item Description fields into main description
        for key in sorted(fields.keys()):
            if key.startswith("Item Description"):
                raw_value = fields.get(key)
                value = raw_value.strip() if isinstance(raw_value, str) else ""
                if value:
                    label = key.replace("Item Description", "").strip()
                    description_lines.append(f"{label}: {value}\n")

        main_desc_key = "Description of Event/Activity"
        original_desc = fields.get(main_desc_key)
        original_desc = original_desc.strip() if isinstance(original_desc, str) else ""

        if original_desc:
            description_lines.append("")  # blank line before main description
            description_lines.append(original_desc)

        if description_lines:
            fields[main_desc_key] = "\n".join(description_lines)

        # Remove all Item Description fields
        for key in list(fields.keys()):
            if key.startswith("Item Description"):
                fields.pop(key)

        # Remove SourceFile field if present
        fields.pop("SourceFile", None)

        # Rename date field
        for key in list(fields.keys()):
            if key.strip() == "Event/Activity Date_af_date":
                fields["Event/Activity Date"] = fields.pop(key)
                break

        # Rename amount total requested field
        for key in list(fields.keys()):
            if key.strip() == "Amount Total Requested":
                fields["Total Requested"] = fields.pop(key)
                break

        # Add prefix "25REQ" to REQID if it exists
        reqid_key = "REQID"
        if reqid_key in fields:
            original_reqid = fields[reqid_key]
            if original_reqid and not str(original_reqid).startswith("25REQ"):
                fields[reqid_key] = "25REQ" + str(original_reqid)

        fieldnames.update(fields.keys())
        data_rows.append(fields)

if not data_rows:
    print("❌ No data extracted. Exiting.")
    exit()

fieldnames = sorted(list(fieldnames))

# Write CSV
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in data_rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})

print(f"✅ Extracted data written to: {output_csv}\n")

# Upload to Access with cleaned data
try:
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={access_db};'
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    with open(output_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            columns = [col.strip() for col in row.keys()]
            columns_sql = ', '.join(f"[{col}]" for col in columns)
            placeholders = ', '.join(['?'] * len(columns))
            values = [clean_value(col, row[col]) for col in columns]

            sql = f"INSERT INTO [{access_table}] ({columns_sql}) VALUES ({placeholders})"
            cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data uploaded to Access successfully.")
except Exception as e:
    print(f"❌ Access upload failed: {e}")
