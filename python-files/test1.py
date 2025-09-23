import tkinter as tk
from tkinter import ttk, filedialog

# Buat jendela utama
root = tk.Tk()
root.title("Demo Tkinter")
root.geometry("600x400")

def pilih_folder():
    folder = filedialog.askdirectory()
    if folder:
        label_folder.config(text=f"Folder: {folder}")

btn_pilih = tk.Button(root, text="Pilih Folder", command=pilih_folder)
btn_pilih.pack(pady=10)

label_folder = tk.Label(root, text="Belum ada folder")
label_folder.pack()

# Buat tabel
kolom = ("Well Name", "GR", "RT", "DT", "Start", "End")
tabel = ttk.Treeview(root, columns=kolom, show="headings")

# Set judul kolom
for col in kolom:
    tabel.heading(col, text=col)
    tabel.column(col, width=80)

tabel.pack(expand=True, fill="both", pady=10)

# Contoh data dummy
data = [
    ("Well-01", "✔️", "✔️", "❌", 1500, 3200),
    ("Well-02", "✔️", "❌", "✔️", 1200, 2800),
]

for row in data:
    tabel.insert("", "end", values=row)


# Jalankan aplikasi
root.mainloop()