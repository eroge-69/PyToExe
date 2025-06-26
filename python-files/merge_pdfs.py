# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
# Get started with interactive Python!
# Supports Python Modules: builtins, math,pandas, scipy 
# matplotlib.pyplot, numpy, operator, processing, pygal, random, 
# re, string, time, turtle, urllib.request
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp
import os
import sys
from pypdf import PdfMerger

def merge_all_pdfs_in_current_folder():
    folder = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else file)
    output_path = os.path.join(folder, "объединенный.pdf")

    merger = PdfMerger()
    pdf_files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf") and f != "объединенный.pdf")

    if not pdf_files:
        print("❌ Нет PDF-файлов для объединения.")
        return

    for pdf in pdf_files:
        full_path = os.path.join(folder, pdf)
        merger.append(full_path)
        print(f"✅ Добавлен: {pdf}")

    merger.write(output_path)
    merger.close()
    print(f"\n📄 Объединённый файл сохранён как: объединенный.pdf")

if name == "main":
    merge_all_pdfs_in_current_folder()