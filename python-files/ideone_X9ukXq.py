import csv

# Daftar nama siswa dan mata pelajaran, bisa disesuaikan
daftar_siswa = ["Ali", "Budi", "Citra", "Dewi"]
daftar_mapel = ["Matematika", "Fisika", "Biologi", "Kimia"]

# Fungsi input nilai
def input_nilai():
    print("Input Nilai Siswa SMA Islam Al Ghozali\n")
    kelas = input("Masukkan kelas (misal: 10 IPA 1): ")
    hasil_nilai = []
    for nama in daftar_siswa:
        print(f"\nNama siswa: {nama}")
        for mapel in daftar_mapel:
            while True:
                try:
                    nilai = float(input(f"  Nilai {mapel}: "))
                    break
                except ValueError:
                    print("Masukkan angka!")
            hasil_nilai.append([kelas, nama, mapel, nilai])
    # Simpan ke CSV
    with open(f"nilai_{kelas.replace(' ','_')}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Kelas", "Nama", "Mata Pelajaran", "Nilai"])
        writer.writerows(hasil_nilai)
    print("\nInput nilai selesai dan disimpan.")

input_nilai()
