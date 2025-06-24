
import rarfile
import itertools
import string
import time
import os

# === KONFIGURASI DASAR ===
MAX_LENGTH = 4  # Panjang maksimal password
CHARSET = string.ascii_lowercase + string.digits  # Kombinasi karakter yang dicoba
rarfile.UNRAR_TOOL = "UnRAR.exe"  # Pastikan UnRAR.exe ada di folder ini atau di PATH

# === INPUT MANUAL ===
print("=== Brute Force RAR Password Cracker ===")
input_path = input("Masukkan path lengkap file RAR (contoh: C:\\Users\\Nama\\file.rar): ").strip('"')

if not os.path.isfile(input_path):
    print(f"[!] File tidak ditemukan: {input_path}")
    input("Tekan Enter untuk keluar...")
    exit()

# Buka file RAR
try:
    rf = rarfile.RarFile(input_path)
except Exception as e:
    print(f"[!] Gagal membuka file RAR: {e}")
    input("Tekan Enter untuk keluar...")
    exit()

print("\n[~] Mulai brute-force password...")
print(f"[~] Charset     : {CHARSET}")
print(f"[~] Max Length  : {MAX_LENGTH}")
print(f"[~] File Target : {input_path}\n")

start_time = time.time()
found = False
attempt_count = 0

for length in range(1, MAX_LENGTH + 1):
    for chars in itertools.product(CHARSET, repeat=length):
        password = ''.join(chars)
        attempt_count += 1
        print(f"[{attempt_count}] Mencoba: {password}", end='\r')

        try:
            rf.extractall(pwd=password.encode('utf-8'))
            elapsed = time.time() - start_time
            print(f"\n\n[✔] PASSWORD DITEMUKAN: {password}")
            print(f"[⏱️] Total waktu: {elapsed:.2f} detik")
            print(f"[🔁] Total percobaan: {attempt_count}")
            found = True
            break
        except rarfile.BadRarFile:
            pass
        except Exception:
            pass

    if found:
        break

if not found:
    print(f"\n[!] Password tidak ditemukan sampai panjang {MAX_LENGTH}")

input("\nTekan Enter untuk keluar...")
