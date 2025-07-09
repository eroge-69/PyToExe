
import os
import shutil
import zipfile
from tkinter import Tk, filedialog
import win32com.client
from pathlib import Path
import ctypes

root = Tk()
root.withdraw()
source_folder = filedialog.askdirectory(title="Wähle den Hauptordner mit den DOCX/XLSX-Dateien")

if not source_folder:
    ctypes.windll.user32.MessageBoxW(0, "Kein Ordner gewählt. Vorgang abgebrochen.", "Abbruch", 0)
    exit()

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
output_folder = os.path.join(desktop, "PDF_Export")
os.makedirs(output_folder, exist_ok=True)

word = win32com.client.Dispatch("Word.Application")
excel = win32com.client.Dispatch("Excel.Application")
word.Visible = False
excel.Visible = False

def convert_word_to_pdf(input_path, output_path):
    doc = word.Documents.Open(input_path)
    doc.ExportAsFixedFormat(output_path, 17)
    doc.Close()

def convert_excel_to_pdf(input_path, output_path):
    wb = excel.Workbooks.Open(input_path)
    wb.ExportAsFixedFormat(0, output_path)
    wb.Close()

def export_files():
    for dirpath, _, filenames in os.walk(source_folder):
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            rel_path = os.path.relpath(dirpath, source_folder)
            target_dir = os.path.join(output_folder, rel_path)
            os.makedirs(target_dir, exist_ok=True)

            filename_wo_ext = os.path.splitext(file)[0]
            target_file = os.path.join(target_dir, filename_wo_ext + ".pdf")

            try:
                if file.endswith(".docx") or file.endswith(".doc"):
                    convert_word_to_pdf(full_path, target_file)
                elif file.endswith(".xlsx") or file.endswith(".xls"):
                    convert_excel_to_pdf(full_path, target_file)
            except Exception as e:
                print(f"Fehler bei {full_path}: {e}")

def zip_output_folder():
    zip_path = os.path.join(desktop, "PDF_Export.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root_dir, _, files in os.walk(output_folder):
            for file in files:
                abs_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(abs_path, output_folder)
                zipf.write(abs_path, rel_path)

export_files()
word.Quit()
excel.Quit()
zip_output_folder()

# Abschlussmeldung
ctypes.windll.user32.MessageBoxW(0, "PDF-Export abgeschlossen! ZIP liegt auf dem Desktop.", "Fertig", 0)
