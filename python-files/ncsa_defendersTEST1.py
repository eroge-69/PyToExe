import tkinter as tk
from tkinter import filedialog, messagebox
import os
import hashlib
import shutil

# Define known malicious file hashes (simulated)
MALWARE_SIGNATURES = {
    "44d88612fea8a8f36de82e1278abb02f",  # Example MD5 (EICAR test string)
}

QUARANTINE_DIR = "quarantine"

def calculate_md5(file_path):
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(4096):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except:
        return None

def scan_file(file_path):
    file_hash = calculate_md5(file_path)
    if file_hash in MALWARE_SIGNATURES:
        return True
    return False

def scan_directory(directory):
    infected_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if scan_file(full_path):
                infected_files.append(full_path)
    return infected_files

def quarantine_files(files):
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)
    for file in files:
        try:
            shutil.move(file, os.path.join(QUARANTINE_DIR, os.path.basename(file)))
        except Exception as e:
            print(f"Failed to quarantine {file}: {e}")

# GUI Setup
def start_scan():
    folder = filedialog.askdirectory()
    if not folder:
        return
    results = scan_directory(folder)
    if results:
        quarantine_files(results)
        messagebox.showwarning("Threats Found", f"{len(results)} infected file(s) detected and quarantined.")
    else:
        messagebox.showinfo("Scan Complete", "No threats detected.")

app = tk.Tk()
app.title("NCSA DEFENDERS Antivirus")
app.geometry("400x200")

title_label = tk.Label(app, text="NCSA DEFENDERS", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

scan_button = tk.Button(app, text="Scan Folder", command=start_scan, font=("Arial", 14))
scan_button.pack(pady=20)

footer = tk.Label(app, text="Basic Antivirus Prototype", font=("Arial", 10), fg="gray")
footer.pack(side="bottom")

app.mainloop()
