
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
from tkinter import filedialog, Tk
import os

# Απόκρυψη κύριου παραθύρου tkinter
root = Tk()
root.withdraw()

# Επιλογή των 3 αρχείων excel
files = filedialog.askopenfilenames(title="Επίλεξε τα 3 αρχεία EXCEL", filetypes=[("Excel files", "*.xlsx")])
if len(files) != 3:
    print("Πρέπει να επιλέξεις ακριβώς 3 αρχεία.")
    exit()

# Φόρτωση των τριών αρχείων
dfs = [pd.read_excel(file) for file in files]

# Συνένωση όλων των εγγραφών
df = pd.concat(dfs, ignore_index=True)

# Διατηρούμε μόνο τις απαραίτητες στήλες
keep_cols = ["ΟΝΟΜΑΤΕΠΩΝΥΜΟ", "ΩΡΑ ΠΡΟΣΕΛΕΥΣΗΣ", "ΩΡΑ ΑΠΟΧΩΡΗΣΗΣ"]
df = df[keep_cols]

# Αφαίρεση διπλοεγγραφών αν υπάρχουν
df = df.drop_duplicates()

# Προσθήκη στήλης ΚΑΤΑΣΤΑΣΗ
df["ΚΑΤΑΣΤΑΣΗ"] = df.apply(
    lambda row: "ΠΑΡΩΝ" if pd.notna(row["ΩΡΑ ΠΡΟΣΕΛΕΥΣΗΣ"]) and pd.notna(row["ΩΡΑ ΑΠΟΧΩΡΗΣΗΣ"]) else "", axis=1
)

# Αποθήκευση προσωρινά σε Excel
temp_file = "ΠΑΡΟΥΣΙΟΛΟΓΙΟ_ΜΕ_DROPDOWN.xlsx"
df.to_excel(temp_file, index=False)

# Φόρτωση για προσθήκη drop-down
wb = load_workbook(temp_file)
ws = wb.active

# Δημιουργία drop-down
options = ["Κ/Α", "ΑΙΜΟΔ.", "ΓΟΝΙΚ", "ΑΝΑΡΩΤ", "ΕΙΔ", "ΡΕΠΟ", "Η/ΑΝ"]
formula = '"' + ",".join(options) + '"'
dv = DataValidation(type="list", formula1=formula, allow_blank=True)
col_katastasi = df.columns.get_loc("ΚΑΤΑΣΤΑΣΗ") + 1
max_row = ws.max_row
dv.add(f"{ws.cell(row=1, column=col_katastasi).column_letter}2:{ws.cell(row=1, column=col_katastasi).column_letter}{max_row}")
ws.add_data_validation(dv)

# Αποθήκευση τελικού αρχείου
wb.save(temp_file)

# Άνοιγμα του αρχείου για προβολή / εκτύπωση
os.startfile(temp_file)
