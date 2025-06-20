import os
import subprocess
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import winreg

# Registry constants
REG_PATH = r"Software\SolidWorksPDFOpener"
DEFAULT_PDF_FOLDER = r"G:\Shared drives\Dept - Engineering\2. PDF Drawings"
MAX_HISTORY = 10

SW_EXTENSIONS = (".sldprt", ".sldasm")
PDF_EXTENSION = ".pdf"

def open_file(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file:\n{path}\n\n{e}")

def find_and_open_files(sw_folder, pdf_folder, base_name):
    found_any = False

    for ext in SW_EXTENSIONS:
        sw_file = os.path.join(sw_folder, base_name + ext)
        if os.path.isfile(sw_file):
            open_file(sw_file)
            found_any = True
            break

    pdf_file = os.path.join(pdf_folder, base_name + PDF_EXTENSION)
    if os.path.isfile(pdf_file):
        open_file(pdf_file)
        found_any = True

    if not found_any:
        messagebox.showwarning("Not Found", f"No matching files found for: {base_name}")

def select_folder(entry_widget):
    path = filedialog.askdirectory()
    if path:
        entry_widget.set(path) if isinstance(entry_widget, ttk.Combobox) else entry_widget.delete(0, tk.END) or entry_widget.insert(0, path)

def run_search():
    sw_folder = sw_entry.get()
    pdf_folder = pdf_entry.get()
    base_name = name_entry.get().strip()

    if not os.path.isdir(sw_folder) or not os.path.isdir(pdf_folder):
        messagebox.showerror("Invalid Folders", "Please select valid folders for both SolidWorks and PDF files.")
        return
    if not base_name:
        messagebox.showerror("Missing Name", "Please enter a base file name.")
        return

    save_registry_config(sw_folder, pdf_folder)
    update_sw_history(sw_folder)
    find_and_open_files(sw_folder, pdf_folder, base_name)

# ---- Registry Helpers ----

def save_registry_config(sw_folder, pdf_folder):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, "LastSWFolder", 0, winreg.REG_SZ, sw_folder)
        winreg.SetValueEx(key, "LastPDFFolder", 0, winreg.REG_SZ, pdf_folder)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error saving registry: {e}")

def load_registry_config():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        sw_folder = winreg.QueryValueEx(key, "LastSWFolder")[0]
        pdf_folder = winreg.QueryValueEx(key, "LastPDFFolder")[0]
        winreg.CloseKey(key)
        return sw_folder, pdf_folder
    except:
        return "", DEFAULT_PDF_FOLDER

def load_sw_history():
    history = []
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        i = 0
        while True:
            val = winreg.EnumValue(key, i)
            if val[0].startswith("History"):
                history.append(val[1])
            i += 1
    except OSError:
        pass
    return history

def update_sw_history(new_path):
    history = load_sw_history()
    if new_path in history:
        history.remove(new_path)
    history.insert(0, new_path)
    history = history[:MAX_HISTORY]
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        # Clear old values
        i = 0
        while True:
            val = winreg.EnumValue(key, i)
            if val[0].startswith("History"):
                winreg.DeleteValue(key, val[0])
            else:
                i += 1
    except OSError:
        pass
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        for idx, path in enumerate(history):
            winreg.SetValueEx(key, f"History{idx}", 0, winreg.REG_SZ, path)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error updating history in registry: {e}")

# ---- GUI Setup ----

root = tk.Tk()
root.title("Open SolidWorks and PDF Files")

# Load previous state from registry
saved_sw, saved_pdf = load_registry_config()
sw_history = load_sw_history()
if saved_sw and saved_sw not in sw_history:
    sw_history.insert(0, saved_sw)

# SolidWorks folder with dropdown history
tk.Label(root, text="SolidWorks Folder:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
sw_entry = ttk.Combobox(root, values=sw_history, width=47)
sw_entry.set(saved_sw)
sw_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=lambda: select_folder(sw_entry)).grid(row=0, column=2, padx=5, pady=5)

# PDF folder
tk.Label(root, text="PDF Folder:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
pdf_entry = tk.Entry(root, width=50)
pdf_entry.insert(0, saved_pdf)
pdf_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=lambda: select_folder(pdf_entry)).grid(row=1, column=2, padx=5, pady=5)

# Filename
tk.Label(root, text="Base Filename (no extension):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
name_entry = tk.Entry(root, width=50)
name_entry.grid(row=2, column=1, padx=5, pady=5)

# Go button
tk.Button(root, text="Find and Open Files", command=run_search, bg="blue", fg="white").grid(row=3, column=1, pady=15)

root.mainloop()
