import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime

def simpan_data():
    data = {
        "no_surat": entry_no_surat.get(),
        "tanggal": entry_tanggal.get(),
        "customer": entry_customer.get(),
        "alamat": entry_alamat.get(),
        "barang": entry_barang.get(),
        "jumlah": entry_jumlah.get(),
        "keterangan": entry_keterangan.get()
    }

    if not all(data.values()):
        messagebox.showwarning("Peringatan", "Semua field harus diisi.")
        return

    with open("surat_jalan.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data.values())
        messagebox.showinfo("Sukses", "Data berhasil disimpan.")

    for entry in entries:
        entry.delete(0, tk.END)

# Setup window
root = tk.Tk()
root.title("Aplikasi Surat Jalan")
root.geometry("400x450")

# Form input
fields = [
    ("No Surat Jalan", "SJ-" + datetime.now().strftime("%Y%m%d%H%M")),
    ("Tanggal", datetime.now().strftime("%Y-%m-%d")),
    ("Nama Customer", ""),
    ("Alamat", ""),
    ("Nama Barang", ""),
    ("Jumlah", ""),
    ("Keterangan", "")
]

entries = []

for label_text, default in fields:
    label = tk.Label(root, text=label_text)
    label.pack()
    entry = tk.Entry(root)
    entry.insert(0, default)
    entry.pack()
    entries.append(entry)

entry_no_surat, entry_tanggal, entry_customer, entry_alamat, entry_barang, entry_jumlah, entry_keterangan = entries

# Tombol Simpan
btn_simpan = tk.Button(root, text="Simpan Data", command=simpan_data, bg="green", fg="white")
btn_simpan.pack(pady=10)

root.mainloop()
