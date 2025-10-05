import tkinter as tk
from tkinter import messagebox, ttk
import csv

# ============================================================
# Aplikasi: Kalkulator Kebutuhan & Biaya Pupuk (GUI Version)
# ============================================================

# Data kebutuhan pupuk per m² dan harga per kg
kebutuhan_per_m2 = {"cabai": 0.05, "tomat": 0.04, "jagung": 0.03}
harga_pupuk = {"cabai": 12000, "tomat": 10000, "jagung": 8000}

# Fungsi untuk menghitung pupuk dan biaya
def hitung():
    tanaman = combo_tanaman.get().lower()
    luas_input = entry_luas.get()
    
    if not tanaman or not luas_input:
        messagebox.showwarning("Peringatan", "Harap isi semua data!")
        return
    
    try:
        luas = float(luas_input)
    except ValueError:
        messagebox.showerror("Error", "Luas lahan harus berupa angka!")
        return
    
    if tanaman not in kebutuhan_per_m2:
        messagebox.showerror("Error", "Jenis tanaman tidak tersedia!")
        return
    
    total_pupuk = luas * kebutuhan_per_m2[tanaman]
    total_biaya = total_pupuk * harga_pupuk[tanaman]
    
    hasil = (
        f"Tanaman: {tanaman.capitalize()}\n"
        f"Luas lahan: {luas} m²\n"
        f"Kebutuhan pupuk: {total_pupuk:.2f} kg\n"
        f"Harga per kg: Rp{harga_pupuk[tanaman]:,}\n"
        f"Total biaya: Rp{total_biaya:,.2f}"
    )
    
    text_hasil.config(state="normal")
    text_hasil.delete(1.0, tk.END)
    text_hasil.insert(tk.END, hasil)
    text_hasil.config(state="disabled")

# Fungsi untuk menyimpan hasil ke file
def simpan():
    pilihan = combo_simpan.get()
    hasil = text_hasil.get(1.0, tk.END).strip()
    
    if not hasil:
        messagebox.showwarning("Peringatan", "Belum ada hasil yang dihitung!")
        return
    
    if pilihan == "File .txt":
        with open("hasil_kalkulator_pupuk.txt", "a") as file:
            file.write(hasil + "\n" + "-"*40 + "\n")
        messagebox.showinfo("Berhasil", "Hasil disimpan di 'hasil_kalkulator_pupuk.txt'")
    
    elif pilihan == "File .csv":
        lines = hasil.split("\n")
        data = [line.split(": ")[1] for line in lines if ": " in line]
        with open("hasil_kalkulator_pupuk.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        messagebox.showinfo("Berhasil", "Hasil disimpan di 'hasil_kalkulator_pupuk.csv'")
    
    else:
        messagebox.showwarning("Peringatan", "Pilih format penyimpanan terlebih dahulu!")

# ============================================================
# Desain Tampilan Aplikasi
# ============================================================

root = tk.Tk()
root.title("Aplikasi Kalkulator Pupuk Sederhana")
root.geometry("420x450")
root.resizable(False, False)

# Judul
judul = tk.Label(root, text="🌿 Kalkulator Kebutuhan & Biaya Pupuk 🌿",
                 font=("Arial", 12, "bold"), pady=10)
judul.pack()

# Frame input
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Jenis Tanaman:").grid(row=0, column=0, sticky="w")
combo_tanaman = ttk.Combobox(frame_input, values=["Cabai", "Tomat", "Jagung"], state="readonly", width=20)
combo_tanaman.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_input, text="Luas Lahan (m²):").grid(row=1, column=0, sticky="w")
entry_luas = tk.Entry(frame_input, width=23)
entry_luas.grid(row=1, column=1, padx=10, pady=5)

# Tombol Hitung
btn_hitung = tk.Button(root, text="Hitung Kebutuhan Pupuk", command=hitung,
                       bg="#4CAF50", fg="white", width=30)
btn_hitung.pack(pady=10)

# Kotak hasil
text_hasil = tk.Text(root, height=8, width=45, state="disabled", wrap="word", bg="#f9f9f9")
text_hasil.pack(pady=5)

# Pilihan penyimpanan
frame_simpan = tk.Frame(root)
frame_simpan.pack(pady=5)

tk.Label(frame_simpan, text="Simpan hasil sebagai:").grid(row=0, column=0, padx=5)
combo_simpan = ttk.Combobox(frame_simpan, values=["File .txt", "File .csv"], state="readonly", width=15)
combo_simpan.grid(row=0, column=1, padx=5)
btn_simpan = tk.Button(frame_simpan, text="Simpan", command=simpan, bg="#2196F3", fg="white", width=10)
btn_simpan.grid(row=0, column=2, padx=5)

# Footer
footer = tk.Label(root, text="© 2025 - Proyek Pembelajaran ATPH x Python", font=("Arial", 8), fg="gray")
footer.pack(pady=10)

root.mainloop()
