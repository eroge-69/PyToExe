import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import fitz  # PyMuPDF
import re
import os

def extract_final_layouts(part_summary_pdf):
    final_layouts = {}
    with pdfplumber.open(part_summary_pdf) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().splitlines()
            part = None
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                match_part = re.match(r'^Name:\s*([\dA-Za-z\-]+)\s*Sortcode1:', line)
                if match_part:
                    part = match_part.group(1)
                match_layouts = re.match(r'^Layouts On:\s*([\d, ]*)', line)
                if part and match_layouts:
                    layouts_full = match_layouts.group(1)
                    j = i + 1
                    while j < len(lines):
                        nextline = lines[j].strip()
                        if re.match(r'^[\d, ]+$', nextline):
                            layouts_full += ' ' + nextline
                            j += 1
                        else:
                            break
                    layouts = [int(x) for x in re.findall(r'\d+', layouts_full)]
                    if layouts:
                        max_layout = max(layouts)
                        if part not in final_layouts or max_layout > final_layouts[part]:
                            final_layouts[part] = max_layout
                    part = None
                    i = j
                else:
                    i += 1
    return final_layouts

def annotate_layout_report(layout_report_pdf, final_layouts, output_folder, total_sheets):
    doc = fitz.open(layout_report_pdf)
    for page_num in range(doc.page_count):
        page = doc[page_num]
        layout_num = page_num + 1
        text = page.get_text("text")
        part_numbers = set(re.findall(r'\d{5,8}(?:-\d{2})?', text))
        for part in part_numbers:
            if part in final_layouts and final_layouts[part] == layout_num:
                part_instances = page.search_for(part)
                for rect in part_instances:
                    box_width = 8
                    box_height = 8
                    gap = 6
                    box_x0 = rect.x1 + gap
                    box_y0 = rect.y0
                    box_x1 = box_x0 + box_width
                    box_y1 = box_y0 + box_height
                    page.draw_rect([box_x0, box_y0, box_x1, box_y1], color=(0, 0, 0), width=1)
                    page.draw_line((box_x0 + 1.5, box_y0 + box_height // 2), (box_x0 + box_width // 2, box_y1 - 1.5), color=(0, 0, 0), width=1)
                    page.draw_line((box_x0 + box_width // 2, box_y1 - 1.5), (box_x1 - 1.5, box_y0 + 1.5), color=(0, 0, 0), width=1)
        # Add sheet count text to the top of the first page
        if page_num == 0 and total_sheets:
            page.insert_text((72, 36), f"Total Sheet Count: {total_sheets}", fontsize=16, color=(0, 0, 0))
    base = os.path.basename(layout_report_pdf)
    outpath = os.path.join(output_folder, f"annotated_{base}")
    doc.save(outpath)
    return outpath

def select_part_summary():
    filename = filedialog.askopenfilename(title="Select Part Summary PDF", filetypes=[("PDF files", "*.pdf")])
    part_summary_var.set(filename)

def select_layout_report():
    filename = filedialog.askopenfilename(title="Select Layout Report PDF", filetypes=[("PDF files", "*.pdf")])
    layout_report_var.set(filename)

def select_output_folder():
    foldername = filedialog.askdirectory(title="Select Output Folder")
    output_folder_var.set(foldername)

def run_annotation():
    part_summary = part_summary_var.get()
    layout_report = layout_report_var.get()
    output_folder = output_folder_var.get()
    total_sheets = total_sheets_var.get().strip()
    if not (part_summary and layout_report and output_folder):
        messagebox.showerror("Missing Input", "Please select all files and output folder before running.")
        return
    if not total_sheets.isdigit():
        messagebox.showerror("Invalid Input", "Please enter a valid sheet count (whole number).")
        return
    try:
        final_layouts = extract_final_layouts(part_summary)
        if not final_layouts:
            messagebox.showerror("Error", "No parts found in Part Summary PDF.")
            return
        outpath = annotate_layout_report(layout_report, final_layouts, output_folder, int(total_sheets))
        messagebox.showinfo("Success", f"Annotated PDF saved to:\n{outpath}")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

root = tk.Tk()
root.title("Layout Report Checkbox Annotator")
root.geometry("540x380")

tk.Label(root, text="Part Summary PDF:").pack(anchor='w', padx=16, pady=(14,2))
part_summary_var = tk.StringVar()
tk.Entry(root, textvariable=part_summary_var, width=64).pack(anchor='w', padx=16)
tk.Button(root, text="Browse", command=select_part_summary).pack(anchor='w', padx=16, pady=(0,8))

tk.Label(root, text="Layout Report PDF:").pack(anchor='w', padx=16, pady=(0,2))
layout_report_var = tk.StringVar()
tk.Entry(root, textvariable=layout_report_var, width=64).pack(anchor='w', padx=16)
tk.Button(root, text="Browse", command=select_layout_report).pack(anchor='w', padx=16, pady=(0,8))

tk.Label(root, text="Output Folder:").pack(anchor='w', padx=16, pady=(0,2))
output_folder_var = tk.StringVar()
tk.Entry(root, textvariable=output_folder_var, width=64).pack(anchor='w', padx=16)
tk.Button(root, text="Browse", command=select_output_folder).pack(anchor='w', padx=16, pady=(0,8))

tk.Label(root, text="Total Sheet Count:").pack(anchor='w', padx=16, pady=(0,2))
total_sheets_var = tk.StringVar()
tk.Entry(root, textvariable=total_sheets_var, width=16).pack(anchor='w', padx=16)

tk.Button(root, text="Annotate Layout Report", command=run_annotation, height=2, width=35).pack(pady=12)

root.mainloop()

