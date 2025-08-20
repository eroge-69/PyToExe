import csv
from datetime import datetime

# Daftar kelas dan siswa
data_siswa = {
    "10": ["Ali", "Budi", "Citra", "Dewi"],
    "11": ["Eka", "Fajar", "Gina", "Hadi"],
    "12": ["Intan", "Joko", "Kiki", "Lina"]
}

# Fungsi absensi
def absensi_jam_ke_nol():
    print("Absensi Jam ke Nol SMA Islam Al Ghozali")
    kelas = input("Pilih kelas (10/11/12): ")
    if kelas not in data_siswa:
        print("Kelas tidak ditemukan.")
        return
    today = datetime.today().strftime('%Y-%m-%d')
    hasil_absen = []
    for nama in data_siswa[kelas]:
        print(f"Nama: {nama}")
        status = input("Status (Hadir/Sakit/Izin/Alpa): ")
        hasil_absen.append([today, kelas, nama, status])
    # Simpan data absen ke file
    with open(f"absensi_jamke0_{kelas}_{today}.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Tanggal", "Kelas", "Nama", "Status"])
        writer.writerows(hasil_absen)
    print("Absensi selesai dan tersimpan.")

absensi_jam_ke_nol()
