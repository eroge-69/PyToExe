import os
import time
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    print("=== ALARM WARNET ===")
    print("1. 30 Menit")
    print("2. 1 Jam")
    print("3. 2 Jam")
    print("4. 3 Jam")
    print("5. 4 Jam")
    pilihan = input("Pilih waktu: ")
    return {
        '1': 30,
        '2': 60,
        '3': 120,
        '4': 180,
        '5': 240
    }.get(pilihan, None)

def countdown(minutes):
    total_seconds = minutes * 60
    warning_sent = False

    while total_seconds > 0:
        mins = total_seconds // 60
        secs = total_seconds % 60
        clear_screen()
        print(f"Sisa waktu: {mins:02d}:{secs:02d}")
        if total_seconds == 600 and not warning_sent:  # 10 menit sebelum habis
            print("\nPERINGATAN: 10 menit lagi waktu akan habis!")
            warning_sent = True
            time.sleep(3)
        time.sleep(1)
        total_seconds -= 1

    print("Waktu habis! Menjalankan ulang alarm...")
    time.sleep(2)
    subprocess.Popen(["python", os.path.realpath(__file__)])  # Restart file

if __name__ == "__main__":
    clear_screen()
    durasi = None
    while durasi is None:
        durasi = show_menu()
    countdown(durasi)
