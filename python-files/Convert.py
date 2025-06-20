#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import os
import openpyxl
from opencc import OpenCC

def convert_traditional_to_simplified_excel(input_file, output_file):
    cc = OpenCC('t2s')  # Traditional to Simplified
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active

    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                cell.value = cc.convert(cell.value)

    wb.save(output_file)
    print(f"Converted '{input_file}' -> '{output_file}'")

def convert_all_xlsx_in_current_directory():
    excel_files = glob.glob("*.xlsx")
    for file in excel_files:
        base, ext = os.path.splitext(file)
        output_file = f"{base}_simplified{ext}"
        convert_traditional_to_simplified_excel(file, output_file)

if __name__ == "__main__":
    convert_all_xlsx_in_current_directory()


# In[ ]:


# pip install openpyxl opencc-python-reimplemented


# In[ ]:




