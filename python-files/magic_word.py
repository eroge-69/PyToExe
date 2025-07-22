import time
import sys

# Fungsi loading palsu
def loading(teks, durasi=0.3, titik=3):
    print(teks, end="", flush=True)
    for _ in range(titik):
        time.sleep(durasi)
        print(".", end="", flush=True)
    print("\n")

# Program utama
def magic_program():
    print("== PROGRAM RAHASIA 😎 ==")
    print("Akses hanya untuk yang tahu password.\n")

    # Step 1: Password
    password = input("🔑 Masukkan password: ")
    if password != "jawa":
        print("❌ Password salah. Akses ditolak.")
        return

    print("\n✅ Password diterima.")
    loading("Mengakses sistem rahasia")

    # Step 2: Magic 3x
    print("\n💡 Sekarang ketik 'magic' 3 kali untuk membuka pesan rahasia.\n")
    counter = 0
    while counter < 3:
        kata = input(f"Ketik kata ajaib ke-{counter + 1}: ")
        if kata.lower() == "magic":
            counter += 1
        else:
            print("❌ Salah. Ulang dari awal.\n")
            counter = 0

    # Step 3: Loading efek dramatis
    loading("\n🧠 Memproses pesan rahasia", 0.5, 5)

    # Step 4: Munculkan pesan
    print("✨ Rahasia telah terbuka...")
    time.sleep(1)
    print("👉 riji kontol\n")

# Jalankan program
if __name__ == "__main__":
    magic_program()

input("Tekan Enter untuk keluar...")
