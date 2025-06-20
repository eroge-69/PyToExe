
import rarfile
import itertools
import string
import time
import os

# === KONFIGURASI ===
RAR_PATH = r"C:\Users\NamaKamu\Desktop\fileku.rar"  # Ganti path ini ke lokasi file RAR kamu
MAX_LENGTH = 4  # Panjang maksimal password
CHARSET = string.ascii_lowercase + string.digits  # Kombinasi karakter yang ingin dicoba
# Untuk huruf besar, tambah: + string.ascii_uppercase
# Untuk simbol: + "!@#$%^&*()"

# Pastikan unrar.exe terdeteksi
rarfile.UNRAR_TOOL = "UnRAR.exe"

# Cek apakah file RAR tersedia
if not os.path.isfile(RAR_PATH):
    print(f"[!] File tidak ditemukan: {RAR_PATH}")
    exit()

# Buka file RAR
try:
    rf = rarfile.RarFile(RAR_PATH)
except Exception as e:
    print(f"[!] Gagal membuka file RAR: {e}")
    exit()

print("[~] Mulai brute-force password...")
print(f"[~] Charset     : {CHARSET}")
print(f"[~] Max Length  : {MAX_LENGTH}")
print(f"[~] File Target : {RAR_PATH}\n")

start_time = time.time()
found = False
attempt_count = 0

# Loop panjang password dari 1 hingga MAX_LENGTH
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
            # Beberapa error (misal CRC) diabaikan
            pass

    if found:
        break

if not found:
    print(f"\n[!] Password tidak ditemukan sampai panjang {MAX_LENGTH}")
