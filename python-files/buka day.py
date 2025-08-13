import time
import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_bar():
    for i in range(101):
        time.sleep(0.03)
        print(f"\r🔄 Menghapus sistem... {i}%", end="")
    print("\n❌ Gagal menghapus sistem. Sistem rusak total!")

def fake_hack():
    clear_screen()
    print("🚨 PERINGATAN: Sistem telah diretas!")
    time.sleep(2)
    print("🔓 Akses administrator berhasil diperoleh.")
    time.sleep(2)
    print("💾 Mengambil data pribadi...")
    for i in range(1, 6):
        print(f"📂 File_{i}.jpg berhasil diambil.")
        time.sleep(1)
    print("⚠️ Sistem akan dimatikan dalam 5 detik!")
    for i in range(5, 0, -1):
        print(f"⏳ {i}...")
        time.sleep(1)
    clear_screen()
    print("💥 Sistem gagal dimatikan.")
    time.sleep(1)
    print("😱 Semua data telah dienkripsi.")
    time.sleep(2)
    print("\n😜 panik panik.")
    print("prankkk")

fake_hack()