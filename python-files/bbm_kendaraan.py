
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
        jarak_awal = float(entry_awal.get())
        jarak_akhir = float(entry_akhir.get())
        harga_bbm = float(entry_harga.get())

        if jenis not in konsumsi_bbm:
            messagebox.showwarning("Peringatan", "Pilih jenis mobil terlebih dahulu!")
            return

        jarak = jarak_akhir - jarak_awal
        konsumsi = konsumsi_bbm[jenis]
        liter = jarak / konsumsi
        total_biaya = liter * harga_bbm

        hasil.set(f"Uang BBM = Rp {total_biaya:,.0f}")

    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid!")

root = tk.Tk()
root.title("Perhitungan BBM Kendaraan Dinas")
root.geometry("400x350")

tk.Label(root, text="Jenis Mobil:").pack(anchor="w", padx=10, pady=5)
combo_mobil = ttk.Combobox(root, values=list(konsumsi_bbm.keys()), state="readonly")
combo_mobil.pack(fill="x", padx=10)

tk.Label(root, text="Jarak Awal (km):").pack(anchor="w", padx=10, pady=5)
entry_awal = tk.Entry(root)
entry_awal.pack(fill="x", padx=10)

tk.Label(root, text="Jarak Akhir (km):").pack(anchor="w", padx=10, pady=5)
entry_akhir = tk.Entry(root)
entry_akhir.pack(fill="x", padx=10)

tk.Label(root, text="Harga BBM (Rp/liter):").pack(anchor="w", padx=10, pady=5)
entry_harga = tk.Entry(root)
entry_harga.pack(fill="x", padx=10)

btn = tk.Button(root, text="Hitung Uang BBM", command=hitung_bbm, bg="green", fg="white")
btn.pack(pady=15)

hasil = tk.StringVar()
tk.Label(root, textvariable=hasil, font=("Arial", 12, "bold"), fg="blue").pack(pady=10)

root.mainloop()
