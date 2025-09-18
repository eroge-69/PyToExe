Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import ttk, messagebox

# konsumsi BBM (km/liter)
konsumsi_bbm = {
    "Bis (Lama)": 3,
    "Bis (Baru)": 4,
    "New Avanza": 9,
    "Toyota Rush": 9,
    "Hiace Baru": 9,
    "Hiace Lama": 7
}

def hitung_bbm():
    try:
        jenis = combo_mobil.get()
        jarak = float(entry_jarak.get())
        harga_bbm = float(entry_harga.get())

        if jenis not in konsumsi_bbm:
            messagebox.showwarning("Peringatan", "Pilih jenis mobil terlebih dahulu!")
...             return
... 
...         konsumsi = konsumsi_bbm[jenis]
...         liter = jarak / konsumsi
...         total_biaya = liter * harga_bbm
... 
...         hasil.set(f"Uang BBM = Rp {total_biaya:,.0f}")
... 
...     except ValueError:
...         messagebox.showerror("Error", "Masukkan angka yang valid!")
... 
... # GUI
... root = tk.Tk()
... root.title("Perhitungan BBM Kendaraan Dinas")
... root.geometry("400x300")
... 
... tk.Label(root, text="Jenis Mobil:").pack(anchor="w", padx=10, pady=5)
... combo_mobil = ttk.Combobox(root, values=list(konsumsi_bbm.keys()), state="readonly")
... combo_mobil.pack(fill="x", padx=10)
... 
... tk.Label(root, text="Jarak (km):").pack(anchor="w", padx=10, pady=5)
... entry_jarak = tk.Entry(root)
... entry_jarak.pack(fill="x", padx=10)
... 
... tk.Label(root, text="Harga BBM (Rp/liter):").pack(anchor="w", padx=10, pady=5)
... entry_harga = tk.Entry(root)
... entry_harga.pack(fill="x", padx=10)
... 
... btn = tk.Button(root, text="Hitung Uang BBM", command=hitung_bbm, bg="green", fg="white")
... btn.pack(pady=15)
... 
... hasil = tk.StringVar()
... tk.Label(root, textvariable=hasil, font=("Arial", 12, "bold"), fg="blue").pack(pady=10)
... 
... root.mainloop()
