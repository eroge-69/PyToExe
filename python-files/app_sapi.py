import datetime

# Data disimpan dalam bentuk list of dictionaries
data_kambing = []
data_sapi = []

def tambah_data(hewan):
    nama = input("Nama hewan: ")
    jenis = input("Jenis (Kambing/Sapi): ")
    tanggal_lahir = input("Tanggal lahir (YYYY-MM-DD): ")
    kesehatan = input("Status kesehatan: ")
    pakan = input("Jenis pakan: ")

    record = {
        "nama": nama,
        "jenis": jenis,
        "tanggal_lahir": tanggal_lahir,
        "kesehatan": kesehatan,
        "pakan": pakan
    }

    if jenis.lower() == "kambing":
        data_kambing.append(record)
    elif jenis.lower() == "sapi":
        data_sapi.append(record)
    else:
        print("Jenis tidak dikenali.")

def edit_data(hewan):
    nama = input("Masukkan nama hewan yang ingin diedit: ")
    target = None
    if hewan == "kambing":
        for d in data_kambing:
            if d["nama"] == nama:
                target = d
                break
    else:
        for d in data_sapi:
            if d["nama"] == nama:
                target = d
                break

    if target:
        print("Data ditemukan. Silakan edit.")
        target["tanggal_lahir"] = input("Tanggal lahir baru: ")
        target["kesehatan"] = input("Status kesehatan baru: ")
        target["pakan"] = input("Jenis pakan baru: ")
    else:
        print("Data tidak ditemukan.")

def hapus_data(hewan):
    nama = input("Masukkan nama hewan yang ingin dihapus: ")
    if hewan == "kambing":
        data_kambing[:] = [d for d in data_kambing if d["nama"] != nama]
    else:
        data_sapi[:] = [d for d in data_sapi if d["nama"] != nama]
    print("Data dihapus jika ditemukan.")

def simpan_ke_file():
    with open("database_peternakan.txt", "w") as f:
        f.write("=== Data Kambing ===\n")
        for d in data_kambing:
            f.write(str(d) + "\n")
        f.write("\n=== Data Sapi ===\n")
        for d in data_sapi:
            f.write(str(d) + "\n")
    print("Data berhasil disimpan ke database_peternakan.txt")

def cetak_data():
    print("\n=== Data Kambing ===")
    for d in data_kambing:
        print(d)
    print("\n=== Data Sapi ===")
    for d in data_sapi:
        print(d)

def menu():
    while True:
        print("\n--- MENU DATABASE PETERNAKAN ---")
        print("1. Tambah Data")
        print("2. Edit Data")
        print("3. Hapus Data")
        print("4. Simpan ke File")
        print("5. Cetak Data")
        print("6. Keluar")

        pilihan = input("Pilih menu (1-6): ")

        if pilihan == "1":
            tambah_data("hewan")
        elif pilihan == "2":
            jenis = input("Edit data kambing atau sapi? ")
            edit_data(jenis.lower())
        elif pilihan == "3":
            jenis = input("Hapus data kambing atau sapi? ")
            hapus_data(jenis.lower())
        elif pilihan == "4":
            simpan_ke_file()
        elif pilihan == "5":
            cetak_data()
        elif pilihan == "6":
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid.")

# Jalankan program
menu()
