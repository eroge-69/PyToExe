# ============================================================
# Program: Kalkulator Kebutuhan Pupuk
# Integrasi Ilmu ATPH dan Koding Dasar
# ============================================================

print("=== Kalkulator Kebutuhan Pupuk ===")
print("Jenis tanaman yang tersedia: cabai, tomat, jagung")
print("-----------------------------------")

# Input dari pengguna
tanaman = input("Masukkan jenis tanaman: ").lower()
luas = float(input("Masukkan luas lahan (m²): "))

# Data kebutuhan pupuk per meter persegi (contoh data)
# (Nilai ini bisa disesuaikan dengan data pertanian sebenarnya)
kebutuhan_per_m2 = {
    "cabai": 0.05,   # kg pupuk per m²
    "tomat": 0.04,
    "jagung": 0.03
}

# Proses perhitungan
if tanaman in kebutuhan_per_m2:
    total_pupuk = luas * kebutuhan_per_m2[tanaman]
    print("-----------------------------------")
    print(f"Tanaman: {tanaman.capitalize()}")
    print(f"Luas lahan: {luas} m²")
    print(f"Kebutuhan pupuk: {total_pupuk:.2f} kg")
else:
    print("Maaf, jenis tanaman tidak tersedia dalam data.")

print("-----------------------------------")
print("Terima kasih telah menggunakan Kalkulator Pupuk!")