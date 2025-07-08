import xlwings as xw
from tkinter import Tk, filedialog, messagebox
from collections import defaultdict

def condense_excel():
    # GUI file picker
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select an Excel File",
        filetypes=[("Excel Files", "*.xlsm *.xlsx")]
    )
    if not file_path:
        return

    # Open workbook
    app = xw.App(visible=False)
    wb = app.books.open(file_path)
    ws = wb.sheets[0]

    data = ws.range("A1").expand().value
    headers = data[0]
    rows = data[1:]

    group_totals = defaultdict(lambda: [0] * 12)  # C to N = 12 columns

    for row in rows:
        title = str(row[0]).strip()
        if not title:
            continue
        for i in range(12):  # Columns C to N
            val = row[i + 2]
            if isinstance(val, (int, float)):
                group_totals[title][i] += val

    # Write output to new sheet
    try:
        wb.sheets["Condensed"].delete()
    except:
        pass
    ws_out = wb.sheets.add("Condensed")
    ws_out.range("A1").value = headers

    row_index = 2
    for title, totals in group_totals.items():
        ws_out.range(f"A{row_index}").value = title
        ws_out.range(f"C{row_index}:N{row_index}").value = [totals]
        row_index += 1

    # Format currency columns
    ws_out.range(f"C2:N{row_index - 1}").number_format = "$#,##0.00"
    ws_out.range("A:N").column_width = 20

    # Save and close
    wb.save()
    wb.close()
    app.quit()

    # Show your ASCII dog message
    messagebox.showinfo("there ya go ya", """
  ^_^
 (o o)
  \\_/
""")

if __name__ == "__main__":
    condense_excel()