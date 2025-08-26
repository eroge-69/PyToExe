import subprocess
import time
import pyautogui
import tkinter as tk
from tkinter import filedialog
import os
import xlwings as xw
import sys    
import win32com.client
from tkinter import filedialog, ttk, messagebox
import xlwings as xw
from pathlib import Path


# Paths
wincross_path = r"C:\TAG\WinCross\wincross.exe"

root = tk.Tk()
root.withdraw()  # Hide main window

# Kill any running WinCross
subprocess.run(["taskkill", "/f", "/im", "wincross.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Select Job File
job_file = filedialog.askopenfilename(title="Select Job File", filetypes=[("Job Files", "*.job")])
if not job_file:   # user pressed cancel
    print("No Job File selected. Exiting...")
    sys.exit()

# Select Data File
data_file = filedialog.askopenfilename(title="Select Data File", filetypes=[("SPSS Data", "*.sav")])
if not data_file:   # user pressed cancel
    print("No Data File selected. Exiting...")
    sys.exit()
f1 = os.path.dirname(data_file)
f0 = os.path.splitext(os.path.basename(data_file))
data_file2 =  os.path.join(f1, os.path.splitext(os.path.basename(data_file))[0] + ".sav")

# # Paths
folder = os.path.dirname(job_file)
file_stem = os.path.splitext(os.path.basename(job_file))[0]    
os.system("taskkill /f /im excel.exe")
# Join with .xlsx
new_path = os.path.join(folder, "OutputFile" + ".xlsx")
if os.path.exists(new_path):
    os.remove(new_path)
    print(f"Deleted existing file: {new_path}")

# Open WinCross
subprocess.Popen([wincross_path, job_file, data_file2])
# Wait for Wincross to fully open
time.sleep(25)  # adjust depending on speed

# Automate WinCross with PyAutoGUI
pyautogui.hotkey("alt", "r")
time.sleep(2)
pyautogui.press("t")
time.sleep(2)
pyautogui.press("a")
time.sleep(1)

pyautogui.hotkey("alt", "x")
time.sleep(5)
pyautogui.press("tab")
time.sleep(5)
pyautogui.press("enter")
time.sleep(5)
pyautogui.press("tab", presses=11, interval=0.2)
time.sleep(5)
pyautogui.press("right")
time.sleep(2)
pyautogui.press("tab", presses=6, interval=0.2)
time.sleep(1)
pyautogui.press("down")
time.sleep(1)
pyautogui.press("tab", presses=24, interval=0.2)
time.sleep(5)
pyautogui.press("right")
time.sleep(1)
pyautogui.press("tab")
time.sleep(1)
pyautogui.press("up")
time.sleep(1)
pyautogui.press("up")
time.sleep(1)
pyautogui.press("up")
time.sleep(1)
pyautogui.press("tab", presses=17, interval=0.2)
time.sleep(1)
pyautogui.press("right")
time.sleep(1)
pyautogui.press("tab")
time.sleep(1)
pyautogui.press("up")
time.sleep(1)
pyautogui.press("tab")
time.sleep(1)
pyautogui.press("enter")
time.sleep(1)
pyautogui.press("space")
time.sleep(1)
pyautogui.press("enter")
time.sleep(1)
pyautogui.press("tab")
time.sleep(1)
pyautogui.press("enter")
time.sleep(2)
pyautogui.hotkey("alt", "r")
time.sleep(60)
pyautogui.hotkey("alt", "y")
time.sleep(30)

    # Connect to running Excel
try:
    # Get active Excel instance
    app = xw.apps.active
    wb2 = app.books.active
except:
    time.sleep(2)  # wait & retry

if not wb2:
    print("No Excel workbook opened by WinCross.")
    sys.exit()
new_path = os.path.join(folder, "OutputFile.xlsx")
wb2.save(new_path)
time.sleep(2) 

os.system("taskkill /f /im excel.exe")
# Kill any running WinCross
subprocess.run(["taskkill", "/f", "/im", "wincross.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# ---------- GLOBALS ----------
Store_TOC = {}
Dict, TC, TBS, TTL, TCIDX = {}, {}, {}, {}, {}
Job_Name = ""
All_In_One = False
Store_TOC = {}
Dict, TC, TBS, TTL, TCIDX = {}, {}, {}, {}, {}
Job_Name = ""
All_In_One = False


# ---------- UTILITY ----------
def open_excel_folder(path):
    """Open all .xlsx files from folder"""
    folder = Path(path)
    return list(folder.glob("*.xlsx"))


def find_in_range(ws, text):
    """Find first occurrence of text in sheet"""
    for row in ws.used_range.rows:
        for cell in row:
            if str(cell.value).strip() == text:
                return cell
    return None


# ---------- TOC DATA ----------
def wincross_toc_get_data(ws):
    """Build Store_TOC dictionary from sheet"""
    if ws.range("A1").value == "Apply Filter":
        ws.range("A:A").delete()  # Deletes first column
    ws.range("2:2").delete()  # Deletes Row 2
    ws.range("2:2").delete()  # Deletes Row 2 again (was Row 3 before shift)
    global Store_TOC, Job_Name
    Store_TOC = {}
    rng_values = ws.used_range.value

    for i in range(4, len(rng_values), 3):  # VBA starts at row 5
        ky = rng_values[i][1]   # col 2
        val = rng_values[i + 1][1]
        if ky:
            Store_TOC[str(ky)] = val

    Job_Name = ws.book.sheets[1].range("A3").value


# ---------- FORMATTING CLASS ----------
class FormattingClass:
    def __init__(self, r, g, b):
        self.R = r
        self.G = g
        self.B = b

    def stat_letter(self, rng):
        for cell in rng:
            val = cell.value
            if val not in (None, "-") and not isinstance(val, (int, float)):
                cell.color = (self.R, self.G, self.B)
                cell.font.color = (255, 255, 255)
                cell.font.bold = True


    def column_border_bps(self,rng):
        """Apply border formatting like VBA colunm_border_BPS"""
        # Borders in xlwings: index follows Excel's borders enumeration
        # 7=xlEdgeLeft, 10=xlEdgeRight, 9=xlEdgeBottom, 8=xlEdgeTop
        xlEdgeLeft, xlEdgeRight, xlEdgeBottom, xlEdgeTop = 7, 10, 9, 8
        color = (216, 224, 229)

        for border_id in [xlEdgeLeft, xlEdgeRight, xlEdgeBottom, xlEdgeTop]:
            b = rng.api.Borders(border_id)
            b.LineStyle = 1  # xlContinuous
            b.Color = color[0] + 256 * color[1] + 65536 * color[2]  # RGB to BGR

    def below_header_color(self, rng):
        rng.color = (216, 224, 229)
        rng.font.bold = True
        rng.api.HorizontalAlignment = -4108  # xlCenter

    def top_header_color(self, rng):
        rng.color = (self.R, self.G, self.B)
        rng.font.color = (255, 255, 255)
        rng.font.bold = True
        rng.api.HorizontalAlignment = -4108

    def remove_hyphen(self, rng):
        for cell in rng:
            if cell.value:
                txt = str(cell.value).strip()
                while "--" in txt:
                    txt = txt.replace("--", "-")
                    txt = txt.replace("-", "")
                txt = txt.replace("\n", " \n")
                cell.value = txt
                cell.api.HorizontalAlignment = -4108
                cell.api.VerticalAlignment = -4107

    def insert_outside_border_thick(self, rng):
        for i in [7, 8, 9, 10]:  # edges: left, right, top, bottom
            border = rng.api.Borders(i)
            border.LineStyle = 1
            border.Weight = 3  # xlMedium
            border.Color = 0

    def base_border(self, rng):
        border = rng.api.Borders(9)  # bottom edge
        border.LineStyle = 1
        border.ColorIndex = 0
        border.Weight = 2  # xlThin


# ---------- TAB FORMATTING ----------
def WINCROSS_TAB_FORMATTING(ws, tab_no, tab_ttl, fm: FormattingClass, tcidx, tc, tbs, ttl, dict_ranges):
    ws.api.Hyperlinks.Delete()
    ws.name = tab_no.replace(" ", "_")

    if ws.range("A1").value in ["Table Name", "Apply Filter"]:
        ws.range("A:A").delete()

    used = ws.used_range
    values = used.value

    # find "Comparison Groups:"
    isStat, isError = False, False
    tab_end = len(values)
    for i, row in enumerate(values, start=1):
        if not row or all(cell in (None, "") for cell in row):
            continue
        if isinstance(row[0], str) and "Comparison Groups:" in row[0]:
            isStat = True
            break

    # find "Base -"
    tab_begin = None
    for i, row in enumerate(values, start=1):
        if row and str(row[0]).startswith("Base -"):
            tab_begin = i + 2
            base_line = ws.range(tab_begin - 2, 1).value
            ws.range(f"A{i-1}:A{i}").value = ""
            ws.range(f"A{i-1}:A{i}").api.HorizontalAlignment = -4131  # xlLeft
            break
    else:
        isError = True
    if isError or not tab_begin:
        return

    ws.cells.api.Interior.Color = 16777215  # white
    ws.cells.api.Font.Name = "Verdana"
    ws.cells.api.Font.Size = 8

    # Banner formatting: look for line breaks
    ban_st = None
    for i, row in enumerate(values, start=1):
        if row and "\n" in str(row[0]):
            ban_st = i
            break

    temp = []
    if ban_st:
        for i in range(tab_begin - 2, ban_st - 1, -1):
            val = ws.range(i, 1).value
            if val and "\n" in str(val):
                temp.append(i)

    if len(temp) == 1:
        rng = ws.range((temp[0], 2), (temp[0], used.columns.count))
        fm.remove_hyphen(rng)
        fm.top_header_color(rng)
    elif len(temp) > 1:
        rng = ws.range((temp[0], 2), (temp[0], used.columns.count))
        fm.remove_hyphen(rng)
        fm.below_header_color(rng)
        for idx in temp[1:]:
            rng = ws.range((idx, 2), (idx, used.columns.count))
            fm.remove_hyphen(rng)
            fm.top_header_color(rng)

    # Stat letter color
    if isStat:
        rng = ws.range((tab_begin, 2), (tab_end, used.columns.count))
        fm.stat_letter(rng)

    # Unwrap stub text
    ws.range((tab_begin, 1), (tab_end, 1)).api.WrapText = False
    ws.range(f"{tab_begin-4}:{tab_end}").row_height = 15

    ban_begin = temp[-1] if temp else tab_begin

    # Borders
    rng = ws.range((ban_begin, 2), (tab_end-4, used.columns.count))
    fm.insert_outside_border_thick(rng)

    for i in range(2, used.columns.count + 1):
        rng = ws.range((ban_begin, i), (tab_end-4, i))

        # handle merged cells → select entire merge area
        if ws.cells(ban_begin, i).merge_cells:
            merge_area = ws.cells(ban_begin, i).merge_area
            merge_cols = merge_area.columns.count
            # extend range across merged columns
            b_rng = ws.range((ban_begin, i), (tab_end-4, i + merge_cols - 1))
            fm.column_border_bps(b_rng)
            i += merge_cols  # skip to next unprocessed col
        else:
            fm.column_border_bps(rng)
            i += 1

    # Column formatting
    ws.range((1, 2), (1, used.columns.count)).column_width = 12
    ws.range((1, 2), (1, used.columns.count)).api.HorizontalAlignment = -4108

    # Bold base row
    ws.range((tab_begin - 3, 1), (tab_begin - 2, used.columns.count)).font.bold = True
    rng = ws.range((tab_begin - 2, 1), (tab_begin - 2, used.columns.count))
    fm.base_border(rng)

    # Add total row
    base_val = ws.range(tab_begin - 2, 2).value
    base_count = round(base_val) if isinstance(base_val, (int, float)) else 0
    ws.range(tab_begin - 2, 1).value = "Total"

    # Clean up rows
    ws.range(f"{ban_begin-1}:4").delete()
    for _ in range(4):
        ws.range("4:4").insert(shift="down")

    ws.range("A4").value = tab_no
    ws.range("A5").value = tab_ttl
    ws.range("A6").value = base_line
        # Read values from cells
    tbl = ws.range((4, 1)).value  # Cell A4
    toc = f"{ws.name}!A4"
    tbase = ws.range((6, 1)).value  # Cell A6
    titl = ws.range((5, 1)).value  # Cell A5

    # Equivalent of scripting.dictionary
    bbs = {}
    bbs[1] = tbase
    bbs[2] = base_count

    # Store into Python dictionaries
    tcidx[tbl] = 4
    tc[tbl] = toc
    tbs[tbl] = bbs
    ttl[tbl] = titl

        # Get UsedRange
    used_rng = ws.api.UsedRange
    dict_ranges[tab_no] = used_rng
    xlCenter = -4108  # Excel constant for center alignment

    last_col = ws.api.UsedRange.Columns.Count  # last used column
    ws.range(
        (1, 2),
        (ws.api.UsedRange.Rows.Count, last_col)
    ).api.HorizontalAlignment = xlCenter



# ---------- MAIN WINCROSS ----------
def wincross_main(r, g, b, all_in_one, logo, folder_path):
    tcidx = {}
    tc = {}
    tbs = {}
    ttl = {}
    dict_ranges={}
    if folder_path:
            app = xw.App() #visible=False
            wb = app.books.open(folder_path)

            ws2 = wb.sheets[1]
            ws2.activate()

            # UsedRange
            used_rng = ws2.api.UsedRange

            # Find "Comparison Groups:"
            xfind = used_rng.Find(
                What="Comparison Groups:",
                LookIn=-4163  # xlValues = -4163
            )


            # Return to sheet(1)
            wb.sheets[0].activate()

            wincross_toc_get_data(wb.sheets[0])
            fm = FormattingClass(r, g, b)
            for i, (tb, tt) in enumerate(Store_TOC.items()):
                ws = wb.sheets[i + 1]
                WINCROSS_TAB_FORMATTING(ws, tb, tt, fm, tcidx, tc, tbs, ttl, dict_ranges)
            if all_in_one:
                    all_sheet_in_one_tab (dict_ranges, tcidx, tc)
            toc_hyperlink(wb,all_in_one,wb.sheets[1].range("a3").value, True, logo,tc,ttl, tbs, tcidx )
            delete_sheets1(wb, all_in_one)
            wb.save()
            wb.close()

            messagebox.showinfo("Python", "Done")
    else:
        messagebox.showwarning("Python", "No folder selected")




# ---------- TKINTER UI ----------


def all_sheet_in_one_tab(dict_ranges, tcidx, tc):
    wb = xw.books.active  # ActiveWorkbook
    ws_banner = wb.sheets.add(after=wb.sheets[-1])
    ws_banner.name = "Banner"
    ws_banner.cells.api.Interior.Color = 16777215  # white
    ws_banner.cells.api.Font.Name = "Verdana"
    ws_banner.cells.api.Font.Size = 8

    cur = 1  # row tracker

    # Loop over dictionary items (each item is a range)
    for tb1 in dict_ranges.keys():
        # Copy data from source range to Banner
        # values = xrng.values
        rows = dict_ranges[tb1].Rows.Count
        cols = dict_ranges[tb1].Columns.Count
        # cols = len(values[0]) if isinstance(values, list) and isinstance(values[0], list) else 1

        dict_ranges[tb1].Copy(ws_banner.range((cur, 1)).api)

        # Extract table name (cell cur+3, col 1)
        tbl = ws_banner.range((cur+3, 1)).value
        toc = f"{ws_banner.name}!A{cur+3}"
        last_row = ws_banner.range("A" + str(ws_banner.cells.last_cell.row)).end("up").row
        xlWhole = 1  # exact match
        xlValues = -4163  # search values
        xlByRows = 1
        xlPrevious = 2

        found = ws_banner.range("A:A").api.Find(
            What="Total",
            LookIn=xlValues,
            LookAt=xlWhole,
            SearchOrder=xlByRows,
            SearchDirection=xlPrevious  # search upwards → last match
        )
        if found:
            ws_banner.range(f"{found.Row}:{last_row}").row_height = 15

        # Update dictionary mappings
        tcidx[tbl] = cur + 3
        tc[tbl] = toc
        # If needed, add back TTL / TBS mappings

        # Move down by copied rows + 1
        cur = cur + rows + 1

    # Adjust formatting
    used_rng = ws_banner.used_range
    cur = used_rng.rows.count

    ws_banner.range("A:A").column_width = 40
    ws_banner.range(ws_banner.range("B1"), ws_banner.range((1, used_rng.columns.count))).column_width = 12

    # Adjust row heights if bold
    for i in range(1, cur+1):
        if ws_banner.range((i, 1)).font.bold:
            ws_banner.range((i, 1)).row_height = 15

    # Hide gridlines & select A1
    ws_banner.range("A1").select()


def toc_hyperlink(wb, all_in_one, job, is_wincross, logo, tc, ttl, tbs, tcidx):

    # Add TOC sheet
    ws_toc = wb.sheets.add(after=wb.sheets[-1])
    ws_toc.name = "TOC"
    ws_toc.cells.api.Interior.Color = 16777215  # white
    ws_toc.cells.api.Font.Name = "Verdana"
    ws_toc.cells.api.Font.Size = 8

    for i, (tbl, toc) in enumerate(tc.items()):
        row = 10 + i

        # Write values
        ws_toc.range((row, 2)).value = tbl  # Table number
        ws_toc.range((row, 3)).value = ttl[tbl]  # Question title

        dic = tbs[tbl]  # bbs dictionary
        ws_toc.range((row, 4)).value = dic[1]  # Base
        ws_toc.range((row, 5)).value = dic[2]  # Base count
        ws_toc.range((row, 5)).api.HorizontalAlignment = -4108  # xlCenter

        str_address = toc  # "Sheet!A4"
        str2 = f"TOC!B{row}"

        # Hyperlink TOC → Table
        ws_toc.api.Hyperlinks.Add(Anchor=ws_toc.range((row, 3)).api,
                                  Address="", SubAddress=str_address)
        ws_toc.api.Hyperlinks.Add(Anchor=ws_toc.range((row, 2)).api,
                                  Address="", SubAddress=str_address)

        # Get table start row from TCIDX
        ss = tcidx[tbl]

        if all_in_one:
            ws_banner = wb.sheets["Banner"]
            cell = ws_banner.range((ss, 1))
            cell.font.color = (0, 0, 255)  # RGB(0,0,255)
            cell.font.underline = True
            ws_toc.api.Hyperlinks.Add(Anchor=cell.api,
                                      Address="", SubAddress=str2)
        else:
            ws_target = wb.sheets[i + 1]  # VBA Sheets(i+2) → Python index (i+1)
            cell = ws_target.range((ss, 1))
            ws_toc.api.Hyperlinks.Add(Anchor=cell.api,
                                      Address="", SubAddress=str2)

    # Headers
    ws_toc.range((8, 3)).value = job
    ws_toc.range((9, 2)).value = "Table No."
    ws_toc.range((9, 3)).value = "Question Title"
    ws_toc.range((9, 4)).value = "Base"


    if is_wincross:
        ws_toc.range((9, 5)).value = "Counts"
    toc_final(wb,is_wincross, logo)


def toc_final(wb, is_wincross, logo):
    ws = wb.sheets["TOC"]  # assumes TOC already exists
    # Set global font
    ws.cells.font.name = "Verdana"
    ws.cells.font.size = 8

    # Get used range row count
    used_rng = ws.api.UsedRange
    xrow = used_rng.Rows.Count

    # Bold + center rows 8–9
    ws.range("8:9").font.bold = True
    ws.range("8:9").api.HorizontalAlignment = -4108  # xlCenter = -4108

    # Number of columns depends on isWincross
    tot = 5 if is_wincross else 4

    # Color font blue in data region
    rng = ws.range((10, 1), (7 + xrow, tot))
    rng.font.color = (0, 0, 255)

    # Apply thick borders column by column (simulating Formatting_Class)
    for i in range(2, tot + 1):
        rng = ws.range((10, i), (7 + xrow, i))
        insert_outside_border_thick(rng)

        rng = ws.range((9, i), (9, i))
        insert_outside_border_thick(rng)

    # Column widths
    ws.range("B:B").column_width = 10
    ws.range("C:C").column_width = 130
    ws.range("D:D").column_width = 30
    ws.range("E:E").column_width = 10

    # Copy logo shape from first sheet of this workbook
    # wbk_name = wb.name
    # src_ws = wb.sheets[0]
    # src_shape = src_ws.api.Shapes(logo)
    # src_shape.Copy()

    # Paste into TOC
    # ws.activate()
    # ws.range("B1").select()
    # ws.api.Paste()

    # Position pasted shape ("Picture 1" is default name for pasted picture)
    # shp = ws.api.Shapes("Picture 1")
    # shp.Top = 10
    # shp.Width = 60
    # shp.Height = 60

    # Hide gridlines + select A1
    ws.range("A1").select()

def delete_sheets1(wb, flag):
    ws_count = len(wb.sheets)

    # Disable alerts (Excel asks confirmation for delete)
    xw.apps.active.api.DisplayAlerts = False

    if flag:  # True → delete all except last 2 sheets
        for i in range(ws_count - 2, 0, -1):   # VBA For i = ws-2 To 1 Step -1
            wb.sheets[i-1].delete()            # Python index = i-1
    else:  # False → delete first sheet
        wb.sheets[0].delete()

    # Move TOC sheet to the front
    wb.sheets["TOC"].api.Move(Before=wb.sheets[0].api)

    # Select each sheet and go to A1
    ws_count = len(wb.sheets)
    for i in range(ws_count, 0, -1):           # VBA For i = ws To 1 Step -1
        ws = wb.sheets[i-1]
        ws.activate()
        ws.range("A1").select()

def insert_outside_border_thick(rng):
    """Apply thick outside border like VBA Insert_Outside_Border_Thick"""
    for idx in [7, 8, 9, 10]:  # xlEdgeLeft=7, Top=8, Bottom=9, Right=10
        border = rng.api.Borders(idx)
        border.LineStyle = 1    # xlContinuous
        border.Weight = 4       # xlThick
# GUI

R, G, B = 16, 58, 93
logo = "Picture 4"
all_in_one = True
wincross_main(R, G, B, all_in_one, logo, new_path)
os.system("taskkill /f /im excel.exe")

