# Modul Kalkulator Sederhana
print("Selamat datang di Kalkulator Sederhana!")
print("Pilih operasi:")
print("1. Tambah (+)")
print("2. Kurang (-)")
print("3. Kali (*)")
print("4. Bagi (/)")

# Ambil input dari user
pilihan = input("Masukkan pilihan (1/2/3/4): ")

# Cek kalau input bukan angka 1-4
if pilihan not in ['1', '2', '3', '4']:
    print("Pilihan salah, bro! Harus 1, 2, 3, atau 4.")
else:
    # Ambil dua angka dari user
    angka1 = float(input("Masukkan angka pertama: "))
    angka2 = float(input("Masukkan angka kedua: "))

    # Logika operasi
    if pilihan == '1':
hasil = angka1 + angka2
        print(f"Hasil: {angka1} + {angka2} = {hasil}")
    elif pilihan == '2':
        hasil = angka1 - angka2
        print(f"Hasil: {angka1} - {angka2} = {hasil}")
    elif pilihan == '3':
        hasil = angka1 * angka2
        print(f"Hasil: {angka1} * {angka2} = {hasil}")
    elif pilihan == '4':
        # Cek pembagian dengan nol
        if angka2 == 0:
            print("Error: Gak bisa bagi dengan nol!")
        else:
            hasil = angka1 / angka2
            print(f"Hasil: {angka1} / {angka2} = {hasil}")
        