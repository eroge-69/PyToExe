
import time
import sys

def type_slow(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    type_slow("[*] Sistem erişimi başlatılıyor...", 0.04)
    time.sleep(1)
    type_slow("[+] Yüksek izinler alındı.", 0.04)
    time.sleep(1)
    type_slow("[!] Kapatma başlatılıyor...", 0.04)
    time.sleep(1)

    for i in range(10, 0, -1):
        print(f"Kapanmaya {i} saniye kaldı...")
        time.sleep(1)

    print("💥 Şaka! Bilgisayar kapanmadı :)")
    input("Kapatmak için Enter’a bas...")

if __name__ == "__main__":
    main()
