import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import re
import time

# ======== Helper Function ========

def format_number(number):
    number = number.strip().replace(" ", "").replace("-", "")
    if not number:
        return None

    # Tambah tanda +
    if not number.startswith("+"):
        if number.startswith("00"):
            number = "+" + number[2:]
        elif number.startswith("0"):
            number = "+62" + number[1:]
        else:
            number = "+" + number

    # Format spasi per negara
    patterns = {
        "+62": r"(\+62)(\d{3,4})(\d+)",
        "+852": r"(\+852)(\d{4})(\d{4})",
        "+60": r"(\+60)(\d{2,3})(\d+)",
        "+65": r"(\+65)(\d{4})(\d{4})",
        "+91": r"(\+91)(\d{5})(\d{5})",
        "+92": r"(\+92)(\d{3,4})(\d+)",
        "+880": r"(\+880)(\d{3,4})(\d+)",
        "+966": r"(\+966)(\d{3})(\d+)",
        "+971": r"(\+971)(\d{2,3})(\d+)",
        "+63": r"(\+63)(\d{3})(\d+)",
        "+234": r"(\+234)(\d{3})(\d+)",
        "+1": r"(\+1)(\d{3})(\d{3})(\d{4})"
    }

    for code, pattern in patterns.items():
        if number.startswith(code):
            m = re.match(pattern, number)
            if m:
                return " ".join(m.groups())
    return number

def remove_duplicates(numbers):
    seen = set()
    result = []
    for num in numbers:
        if num not in seen:
            seen.add(num)
            result.append(num)
    return result

def process_txt_to_vcf(txt_file, contact_name, file_name, per_file, output_dir, progress_bar, status_label):
    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            numbers = [format_number(line) for line in f if format_number(line)]

        numbers = remove_duplicates(numbers)
        total_contacts = len(numbers)
        total_files = (total_contacts + per_file - 1) // per_file

        progress_bar["maximum"] = total_contacts
        progress_bar["value"] = 0
        status_label.config(text="⏳ Memproses...")

        for idx in range(0, total_contacts, per_file):
            batch = numbers[idx:idx+per_file]
            file_index = (idx // per_file) + 1
            vcf_path = os.path.join(output_dir, f"{file_name} {file_index}.vcf")

            with open(vcf_path, "w", encoding="utf-8") as vcf:
                for i, num in enumerate(batch, start=1):
                    contact_fullname = f"{contact_name} {i + idx}"
                    vcf.write("BEGIN:VCARD\n")
                    vcf.write("VERSION:3.0\n")
                    vcf.write(f"FN:{contact_fullname}\n")
                    vcf.write(f"TEL;TYPE=CELL:{num}\n")
                    vcf.write("END:VCARD\n\n")
                    progress_bar["value"] += 1
                    root.update_idletasks()
                    time.sleep(0.001)  # biar progress smooth

        status_label.config(text=f"✅ Selesai! {total_contacts} kontak → {total_files} file")
        messagebox.showinfo("Selesai", f"Berhasil membuat {total_files} file VCF dengan total {total_contacts} kontak.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ======== GUI ========

def browse_txt():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        txt_entry.delete(0, tk.END)
        txt_entry.insert(0, file_path)

def browse_output():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)

def start_process():
    txt_file = txt_entry.get()
    contact_name = contact_entry.get()
    file_name = file_entry.get()
    per_file = perfile_entry.get()
    output_dir = output_entry.get()

    if not txt_file or not contact_name or not file_name or not per_file or not output_dir:
        messagebox.showwarning("Peringatan", "Lengkapi semua field!")
        return

    try:
        per_file = int(per_file)
    except ValueError:
        messagebox.showwarning("Peringatan", "Kontak per file harus angka!")
        return

    process_txt_to_vcf(txt_file, contact_name, file_name, per_file, output_dir, progress_bar, status_label)

# GUI Setup
root = tk.Tk()
root.title("TXT to VCF Converter")
root.geometry("420x450")
root.resizable(False, False)

tk.Label(root, text="Pilih File TXT:").pack(pady=5)
txt_entry = tk.Entry(root, width=45)
txt_entry.pack()
tk.Button(root, text="Browse", command=browse_txt).pack()

tk.Label(root, text="Nama Kontak Dasar:").pack(pady=5)
contact_entry = tk.Entry(root, width=45)
contact_entry.pack()

tk.Label(root, text="Nama File Dasar:").pack(pady=5)
file_entry = tk.Entry(root, width=45)
file_entry.pack()

tk.Label(root, text="Kontak per File:").pack(pady=5)
perfile_entry = tk.Entry(root, width=45)
perfile_entry.pack()

tk.Label(root, text="Folder Output:").pack(pady=5)
output_entry = tk.Entry(root, width=45)
output_entry.pack()
tk.Button(root, text="Browse", command=browse_output).pack()

progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=15)

status_label = tk.Label(root, text="", font=("Arial", 11))
status_label.pack()

tk.Button(root, text="Proses", bg="green", fg="white", width=20, command=start_process).pack(pady=10)

root.mainloop()
