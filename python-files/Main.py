import random

print("=== Permainan Tebak Angka ===")
print("Saya sudah memilih angka antara 1 sampai 20.")
print("Coba tebak angkanya! Ketik '0' untuk menyerah.\n")

angka_rahasia = random.randint(1, 20)
tebakan = -1
percobaan = 0

while tebakan != angka_rahasia:
    try:
        tebakan = int(input("Masukkan tebakan Anda: "))
        percobaan += 1

        if tebakan == 0:
            print(f"Kamu menyerah. Angka yang benar adalah {angka_rahasia}.")
            break

        if tebakan < angka_rahasia:
            print("Terlalu rendah!\n")
        elif tebakan > angka_rahasia:
            print("Terlalu tinggi!\n")
        else:
            print(f"Selamat! Kamu berhasil menebak dalam {percobaan} percobaan.")
    except ValueError:
        print("Masukkan angka yang valid!\n")
