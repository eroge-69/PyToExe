import win32gui
import win32con
import pyautogui
import time

# Fungsi bantu: cek apakah warna pixel sesuai (dengan toleransi)
def warna_sama(w1, w2, toleransi=10):
    return all(abs(a - b) <= toleransi for a, b in zip(w1, w2))

# Konfigurasi akun
accounts = [
    {
        "title": "Perfect World 2",        # Judul window akun
        "hp_pixel": (98, 47),
        "hp_color": (180, 47, 47),
        "mp_pixel": (98, 63),
        "mp_color": (0, 92, 148),
        "hp_key": win32con.VK_F1,          # F1 untuk pot HP
        "mp_key": 0x33                     # Tombol '3' untuk pot MP
    },
    # Tambah akun lain di sini jika window title berbeda
]

def kirim_tombol(hwnd, key_code):
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)

print("Bot auto-potion MULTI AKUN berjalan... Tekan CTRL+C untuk keluar.")

try:
    while True:
        for acc in accounts:
            hwnd = win32gui.FindWindow(None, acc["title"])
            if not hwnd:
                print(f"[!] Window '{acc['title']}' tidak ditemukan.")
                continue

            # Ambil warna pixel saat ini
            warna_hp = pyautogui.pixel(*acc["hp_pixel"])
            warna_mp = pyautogui.pixel(*acc["mp_pixel"])

            # Cek HP
            if warna_sama(warna_hp, acc["hp_color"]):
                kirim_tombol(hwnd, acc["hp_key"])
                print(f"[{acc['title']}] → Pot HP!")

            # Cek MP
            if warna_sama(warna_mp, acc["mp_color"]):
                kirim_tombol(hwnd, acc["mp_key"])
                print(f"[{acc['title']}] → Pot MP!")

        time.sleep(0.2)  # Delay 200ms antar cek

except KeyboardInterrupt:
    print("\nBot dihentikan.")