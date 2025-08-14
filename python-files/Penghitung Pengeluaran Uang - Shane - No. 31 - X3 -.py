# Variabel
saldo = 0
riwayat = ""

# Menu
while True:
    print("=== Penghitung Pengeluaran Uang ===")
    print(f"Saldo Anda = Rp.{saldo:,}")
    print("1. Tambah Saldo")
    print("2. Tambah Pengeluaran")
    print("3. Lihat Riwayat")
    print("4. Keluar")

# Input
    pilihan = input("Masukan pilihan anda [1/2/3/4] = ")

    if pilihan == '1':
        jumlah = input("Masukan jumlah saldo = ")
        if jumlah.isdigit():
            jumlah = int(jumlah)
            saldo += jumlah
            riwayat = riwayat + f"Ditambah saldo = +Rp.{jumlah:,}\n"
            print(f"Saldo Sekarang = Rp.{saldo:,}")
        else:
            print("Masukan angka yang valid")

    elif pilihan == '2':
        jumlah = input("Masukan jumlah pengeluaran = ")
        if jumlah.isdigit():
            jumlah = int(jumlah)
            if saldo >= jumlah:
                    saldo -= jumlah
                    riwayat = riwayat + f"Pengeluara = -Rp.{jumlah:,}\n"
                    print(f"Pengeluaran = Rp.{jumlah:,}")
            else:
                    print("Saldo tidak cukup")
        else:
            print("Masukan angka yang valid")

    elif pilihan == '3':
        if riwayat != "":
            print("======== Riwayat Transaksi ========")
            print(riwayat, end="")
            print("===================================")
        else:
            print("Belum ada transaksi")

    elif pilihan == '4':
        continue

    else:
        print("Pilihan tidak ada")
