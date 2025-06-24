import pyodbc
import re
import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import datetime
import pandas as pd
from openpyxl import Workbook

def normalize_number(number):
    try:
        return str(float(str(number).replace(",", "").replace("(", "-").replace(")", "")))
    except ValueError:
        return number

def highlight_numbers_in_pdf(pdf_path, numbers_with_labels, key_instn):
    try:
        doc = fitz.open(pdf_path)
        found_numbers = set()
        not_found_numbers = set(numbers_with_labels.keys())
        normalized_to_original = {}

        for num in numbers_with_labels:
            normalized_num = normalize_number(num)
            if normalized_num not in normalized_to_original:
                normalized_to_original[normalized_num] = []
            normalized_to_original[normalized_num].append(num)

        for page in doc:
            words = page.get_text("words")
            lines = {}
            for w in words:
                y0 = round(w[1], 1)
                lines.setdefault(y0, []).append(w)

            line_keys = sorted(lines.keys())
            for i, y0 in enumerate(line_keys):
                combined_words_set = set(" ".join(w[4] for w in lines[y0]).lower().split())
                if i > 0:
                    combined_words_set.update(set(" ".join(w[4] for w in lines[line_keys[i-1]]).lower().split()))
                if i < len(line_keys) - 1:
                    combined_words_set.update(set(" ".join(w[4] for w in lines[line_keys[i+1]]).lower().split()))

                for w in lines[y0]:
                    word_text = w[4]
                    normalized_word = normalize_number(word_text.rstrip("%"))
                    if normalized_word in normalized_to_original:
                        for original_num in normalized_to_original[normalized_word]:
                            entries = numbers_with_labels[original_num]
                            match_ratio = 0
                            for entry in entries:
                                label_words = set(str(entry['label']).lower().split())
                                common_words = label_words.intersection(combined_words_set)
                                ratio = len(common_words) / len(label_words) if label_words else 0
                                if ratio > match_ratio:
                                    match_ratio = ratio
                            rect = fitz.Rect(w[:4])
                            color = (0, 1, 0) if match_ratio >= 0.50 else (1, 1, 0)
                            highlight = page.add_highlight_annot(rect)
                            highlight.set_colors(stroke=color)
                            highlight.update()
                            found_numbers.add(normalized_word)
                            not_found_numbers.discard(original_num)


        original_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"highlighted_{original_name}.pdf"
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", output_filename)
        doc.save(output_path)
        doc.close()
        return output_path, found_numbers, not_found_numbers
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process PDF: {e}")
        return None, set(), set()

def run_query(key_instn, fiscal_entries):
    server = '10.128.193.165'
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'Trusted_Connection=yes;'
    )
    conditions = []
    for year_entry, quarter_entry in fiscal_entries:
        year = year_entry.get().strip()
        quarter = quarter_entry.get().strip()
        if year and quarter:
            conditions.append(f"(eo1.FiscalYear = {year} AND eo1.FiscalQuarter = '{quarter}')")
    fiscal_condition = f" AND ({' OR '.join(conditions)})" if conditions else ""

    query_template = f"""
    SELECT DISTINCT edv.ExtractionDocumentValue,
    edv.ExtractionDocumentLabelShort,
    eo1.FiscalYear,
    eo1.FiscalQuarter
    FROM SNLEdit..SourceTaggingDataItem stdi
    LEFT JOIN SNLEdit..SourceTagDissection std ON std.KeySourceTaggingDataItem = stdi.KeySourceTaggingDataItem AND std.UpdOperation <> 2 
    LEFT JOIN SNLEdit..SourceTagging st ON stdi.KeySourceTaggingDataItem = st.KeySourceTaggingDataItem AND st.UpdOperation < 2 AND stdi.appstatus = 2 AND std.keysourcetagging = st.keysourcetagging
    LEFT JOIN snledit..ExtractionDocumentValue edv ON edv.KeyExtractionDocumentValue = st.KeyExtractionDocumentValue
    JOIN snledit..finleop eo ON stdi.keytable = 560 AND eo.keyfinleop = CAST(stdi.OID AS FLOAT)
    JOIN snledit..finl eo1 ON eo.keyfinleop = eo1.keyfinleop AND eo1.FiscalYear IS NOT NULL
    WHERE eo.KeyInstn = '{key_instn}'
    AND stdi.appstatus = 2
    AND stdi.UpdOperation <> 2
    AND std.appstatus = 2
    AND std.UpdOperation <> 2
    {fiscal_condition}
    UNION
    SELECT DISTINCT edv.ExtractionDocumentValue,
                    edv.ExtractionDocumentLabelShort,
                    eo1.FiscalYear,
                    eo1.FiscalQuarter
    FROM SNLEdit..SourceTaggingDataItem stdi
    LEFT JOIN SNLEdit..SourceTagDissection std ON std.KeySourceTaggingDataItem = stdi.KeySourceTaggingDataItem AND std.UpdOperation <> 2 
    LEFT JOIN SNLEdit..SourceTagging st ON stdi.KeySourceTaggingDataItem = st.KeySourceTaggingDataItem AND st.UpdOperation < 2 AND stdi.appstatus = 2 AND std.keysourcetagging = st.keysourcetagging
    LEFT JOIN snledit..ExtractionDocumentValue edv ON edv.KeyExtractionDocumentValue = st.KeyExtractionDocumentValue
    LEFT JOIN snledit..finl eo1 ON stdi.keytable = 107 AND eo1.keyfinl = CAST(stdi.OID AS FLOAT)
    LEFT JOIN snledit..finleop eo ON eo1.keyfinleop = eo.keyfinleop
    WHERE eo.KeyInstn = '{key_instn}'
    AND stdi.appstatus = 2
    AND stdi.UpdOperation <> 2
    AND std.appstatus = 2
    AND std.UpdOperation <> 2
    {fiscal_condition}
    """

    try:
        result_text.insert(tk.END, "Connecting to SQL Server...\n")
        root.update()
        conn = pyodbc.connect(conn_str)
        result_text.insert(tk.END, "Connection successful!\n")
        root.update()
        cursor = conn.cursor()
        result_text.insert(tk.END, "Executing query...\n")
        root.update()
        cursor.execute(query_template)
        rows = cursor.fetchall()
        result_text.insert(tk.END, "Query executed. Processing results...\n")
        root.update()
        numbers_with_labels = {}
        for value, label, year, quarter in rows:
            if value is not None and label:
                matches = re.findall(r'-?\d+\.?\d*', str(value).replace(',', ''))
                for match in matches:
                    numbers_with_labels.setdefault(match, []).append({
                        'label': label,
                        'year': year,
                        'quarter': quarter
                    })
        return numbers_with_labels
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return {}

def export_to_excel(not_found_numbers, numbers_with_labels, output_path):
    try:
        excel_path = os.path.splitext(output_path)[0] + ".xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append(["Number", "Label", "Year", "Quarter"])
        for number in not_found_numbers:
            for entry in numbers_with_labels[number]:
                ws.append([number, entry['label'], entry['year'], entry['quarter']])
        wb.save(excel_path)
        return excel_path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export to Excel: {e}")
        return None

def compare_excel_files(excel_path1, excel_path2, fiscal_entries):
    try:
        df1 = pd.read_excel(excel_path1)
        df2 = pd.read_excel(excel_path2)
        result_text.insert(tk.END, "\n--- Line items to look for ---\n")

        # Create a new Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Differences"
        ws.append(["Number", "Label", "Year", "Quarter"])

        for idx, (year_entry, quarter_entry) in enumerate(fiscal_entries):
            year = year_entry.get().strip()
            quarter = quarter_entry.get().strip()
            if not year or not quarter:
                continue

            filtered_df1 = df1[(df1['Year'] == int(year)) & (df1['Quarter'].astype(str) == quarter)]
            filtered_df2 = df2[(df2['Year'] == int(year)) & (df2['Quarter'].astype(str) == quarter)]

            common_rows = pd.merge(filtered_df1[['Label', 'Number']], filtered_df2[['Label', 'Number']], on=['Label', 'Number'], how='inner')

            if idx == 0:
                different_rows = filtered_df2[~filtered_df2.set_index(['Label', 'Number']).index.isin(common_rows.set_index(['Label', 'Number']).index)]
            else:
                different_rows = filtered_df1[~filtered_df1.set_index(['Label', 'Number']).index.isin(common_rows.set_index(['Label', 'Number']).index)]

            result_text.insert(tk.END, f"\nYear: {year}, Quarter: {quarter}\n")
            if not different_rows.empty:
                result_text.insert(tk.END, "Different Rows:\n" + different_rows.to_string(index=False) + "\n")
                for _, row in different_rows.iterrows():
                    ws.append([row['Number'], row['Label'], year, quarter])
            else:
                result_text.insert(tk.END, "No different rows found.\n")

        # Save the Excel file
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", "comparison_results.xlsx")
        wb.save(output_path)
        result_text.insert(tk.END, f"\nComparison results saved to: {output_path}\n")

    except Exception as e:
        messagebox.showerror("Error", f"Comparison failed: {e}")


def browse_pdf_file(entry_widget):
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if pdf_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, pdf_path)

def process_numbers():
    key_instn = entry_key_instn.get().strip()
    pdf_paths = [entry_pdf_path.get().strip(), entry_pdf_path2.get().strip()]
    if not key_instn or not all(pdf_paths):
        messagebox.showerror("Error", "Please enter KeyInstn and select two PDF files.")
        return
    result_text.insert(tk.END, "Starting process...\n")
    root.update()
    numbers_with_labels = run_query(key_instn, fiscal_entries)
    if not numbers_with_labels:
        messagebox.showerror("Error", "No numeric values found.")
        return

    excel_paths = []
    for i, pdf_path in enumerate(pdf_paths, start=1):
        result_text.insert(tk.END, f"Processing PDF {i}...\n")
        root.update()
        output_path, found_numbers, not_found_numbers = highlight_numbers_in_pdf(pdf_path, numbers_with_labels, key_instn)
        if output_path:
            result_text.insert(tk.END, f"Highlighted PDF {i} saved to: {output_path}\n")
            if not_found_numbers:
                result_text.insert(tk.END, f"Numbers not found in PDF {i}: ({len(not_found_numbers)})\n")
                excel_path = export_to_excel(not_found_numbers, numbers_with_labels, output_path)
                if excel_path:
                    result_text.insert(tk.END, f"Excel file {i} saved to: {excel_path}\n")
                    excel_paths.append(excel_path)
            else:
                result_text.insert(tk.END, f"All numbers were found and highlighted in PDF {i}!\n")

    if len(excel_paths) == 2:
        compare_excel_files(excel_paths[0], excel_paths[1], fiscal_entries)

# GUI setup
root = tk.Tk()
root.title("Comparer")
root.geometry("600x800")

label_key_instn = tk.Label(root, text="KeyInstn")
label_key_instn.pack(pady=5)
entry_key_instn = tk.Entry(root, width=50)
entry_key_instn.pack(pady=5)

label_pdf_path = tk.Label(root, text="PDF File 1")
label_pdf_path.pack(pady=5)
entry_pdf_path = tk.Entry(root, width=50)
entry_pdf_path.pack(pady=5)
button_browse_pdf1 = tk.Button(root, text="Browse PDF 1", command=lambda: browse_pdf_file(entry_pdf_path))
button_browse_pdf1.pack(pady=5)

label_pdf_path2 = tk.Label(root, text="PDF File 2")
label_pdf_path2.pack(pady=5)
entry_pdf_path2 = tk.Entry(root, width=50)
entry_pdf_path2.pack(pady=5)
button_browse_pdf2 = tk.Button(root, text="Browse PDF 2", command=lambda: browse_pdf_file(entry_pdf_path2))
button_browse_pdf2.pack(pady=5)

label_fiscal_info = tk.Label(root, text="Enter up to 5 Fiscal Year and Quarter pairs")
label_fiscal_info.pack(pady=5)

current_year = datetime.datetime.now().year
years = [str(current_year - i) for i in range(30)]
quarters = ["1", "2", "3", "4", "6", "9", "Y"]

fiscal_entries = []
for i in range(5):
    frame = tk.Frame(root)
    frame.pack(pady=2)
    year_combobox = ttk.Combobox(frame, values=years, width=10)
    year_combobox.pack(side=tk.LEFT, padx=5)
    quarter_combobox = ttk.Combobox(frame, values=quarters, width=10)
    quarter_combobox.pack(side=tk.LEFT, padx=5)
    fiscal_entries.append((year_combobox, quarter_combobox))

button_process = tk.Button(root, text="Compare!", command=process_numbers)
button_process.pack(pady=10)

result_text = tk.Text(root, height=20, width=80)
result_text.pack(pady=10)

root.mainloop()
