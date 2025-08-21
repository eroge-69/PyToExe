import os
import sys
from time import sleep
import requests  # pastikan requests sudah diinstall: pip install requests

LICENSE_FILE = "license.key"
API_URL = "https://apikey.my/digital-license-system/activate_license.php"

def warna(text, color, attrs=None):
    try:
        from termcolor import colored
        return colored(text, color, attrs=attrs if attrs else [])
    except:
        return text

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def wait(msg="\nTekan Enter untuk keluar..."):
    input(warna(msg, "green"))

def check_license():
    clear()
    print(warna("="*50, "cyan"))
    print(warna("TG-BULK-PRO LICENSE ACCESS", "white", ["bold"]))
    print(warna("="*50, "cyan"))
    print()
    print(warna("Sila masukkan license key yang sah untuk mengakses sistem.", "yellow"))
    print(warna("License key akan disimpan dan tidak diminta lagi selepas ini.", "yellow"))
    print()

    # Cuba baca dari file dulu
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            saved_key = f.read().strip()
            # Semak dengan API
            if verify_license_online(saved_key):
                print(warna("✅ License key sah! Akses dibenarkan.", "green", ["bold"]))
                sleep(1)
                return True

    # Jika tiada atau tidak sah, minta user masukkan
    key = input(warna("→ Masukkan License Key : ", "cyan", ["bold"])).strip()
    if verify_license_online(key):
        with open(LICENSE_FILE, "w") as f:
            f.write(key)
        print(warna("\n✅ License key diterima. Anda boleh teruskan.", "green", ["bold"]))
        sleep(1)
        return True
    else:
        print(warna("\n❌ License key salah! Sila cuba lagi.", "red", ["bold"]))
        wait()
        return False

def verify_license_online(key):
    try:
        payload = {
            "license_key": key,
            "user_info": os.getenv("USERNAME") or os.getenv("USER") or "python-client"
        }
        response = requests.post(API_URL, data=payload, timeout=10)
        # API expected to return JSON with status "success" if valid
        resp = response.json()
        return resp.get("status") == "success"
    except Exception as e:
        print(warna(f"Ralat sambungan ke pelayan lesen: {e}", "red"))
        wait("Sambungan gagal. Sila semak internet atau hubungi admin.")
        return False

def main():
    while True:
        if check_license():
            # Bila berjaya, terus panggil menu.py
            os.system("python menu.py")
            break
        else:
            clear()

if __name__ == "__main__":
    main()