import openpyxl
from pathlib import Path
import xlwings as xw
import os
import re
import sys

def run_update():
    #wb = xw.Book.caller()
    workbook_path = sys.argv[1]
    wb = xw.Book(workbook_path)
    attributes = get_attributes(wb.fullname)
    data = parse_accounts(wb.fullname, attributes["month"])
    month = month_translate(attributes["month"])
    print("Looking for monthtxt:", attributes["month"])
    wbx = openpyxl.load_workbook(wb.fullname, data_only=True)
    sheetx = wbx['Plan kont']

    account_rows = {}

    for row in sheetx.iter_rows(min_row=2, max_col=3):
        for cell in row:
            val = str(cell.value).strip() if cell.value else ""
            if val in data[0]:
                account_rows[val] = cell.row
                
    sheet = wb.sheets['Plan kont']

    for acct, row_num in account_rows.items():
        sheet.range(f"{month}{row_num}").value = data[0][acct]

    attributes_workbook = wb.sheets['Automatic Update']
    files_updated = data[1]
    attributes_workbook.range("C14").value = "Files updated: " + ", ".join(Path(file).name for file in files_updated)
    print("DONE!")
    
def get_attributes(workbook):
    attributes = {}
    wb = openpyxl.load_workbook(workbook)
    attributes_workbook = wb['Automatic Update']
    attributes["directory"] = attributes_workbook["C2"].value
    attributes["client"] = attributes_workbook["C3"].value
    attributes["monthtxt"] = attributes_workbook["T16"].value.upper()
    attributes["month"] = attributes_workbook["C7"].value.upper()
    attributes["year"] = str(attributes_workbook["C8"].value)
    return attributes

def month_translate(month):
    mapping = {
        "STYCZEŃ": "T",
        "LUTY": "U",
        "MARZEC": "V",
        "KWIECIEŃ": "W",
        "MAJ": "X",
        "CZERWIEC": "Y",
        "LIPIEC": "Z",
        "SIERPIEŃ": "AA",
        "WRZESIEŃ": "AB",
        "PAŹDZIERNIK": "AC",
        "LISTOPAD": "AD",
        "GRUDZIEŃ": "AE"
    }
    return mapping.get(month, None)

def parse_accounts(workbook, month):
    acct_re = re.compile(r'^[^|]*\|\s*(\d+(?:-\d+)*)')
    if (month == "STYCZEŃ"):
        num_re = re.compile(r'^(?:[^|]*\|){4,5}\s*(\d+(?:\s\d{3})*,\d{2})')
    else:
        num_re = re.compile(r'^(?:[^|]*\|){3,4}\s*(\d+(?:\s\d{3})*,\d{2})')

    
    attributes = get_attributes(workbook)
    print(attributes)
    files = []

    result = {}
    for filename in os.listdir(attributes["directory"]):
        if filename.endswith('.txt') or filename.endswith('.TXT'):
            file_path = os.path.join(attributes["directory"], filename)
            if os.path.isfile(file_path):
                with open(file_path, encoding="mac_roman", errors='replace') as f:
                    for lineno, line in enumerate(f, 1):
                        if (lineno == 2):
                            if attributes["client"] in line:
                                print("YIPPIE")
                            else:
                                break
                        if (lineno == 5):
                            if attributes["monthtxt"] in line:
                                print("YIPPIE2")
                            else:
                                break
                            if attributes["year"] in line:
                                print("YIPPIE3")
                                files.append(file_path)
                            else:
                                break
                        m = acct_re.search(line)
                        if not m:
                            continue

                        acct = m.group(1)
                        nums = num_re.findall(line)

                        # default to zero if no money found
                        if nums:
                            raw = nums[0]
                            # remove spaces, convert comma to dot
                            norm = raw.replace(' ', '').replace(',', '.')
                            try:
                                val = float(norm)
                            except ValueError:
                                val = 0.0
                            print(f"Line {lineno}: → {acct} = {val}")
                        else:
                            val = 0.0
                            print(f"Line {lineno}: → {acct} found, no amount → defaulting to 0.0")

                        result[acct] = val

    return result, files
    
if __name__ == "__main__":
    run_update()