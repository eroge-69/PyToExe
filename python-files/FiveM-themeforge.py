import os
import time
import random
import threading
import winsound
import ctypes
from colorama import init, Fore, Back, Style

init(autoreset=True)

# ===== SCARY EFFECTS =====
def play_scary_sound():
    for freq in [440, 330, 260, 800, 200]:
        winsound.Beep(freq, 200)

def fake_blue_screen():
    ctypes.windll.user32.MessageBoxW(0, "CRITICAL ERROR: MEMORY CORRUPTION", "BLUE SCREEN", 0x10)
    os.system("color 1F")  # Blauer Hintergrund (Fake-BSOD)
    time.sleep(2)
    os.system("color 0A")

def fake_mouse_movement():
    for _ in range(20):
        ctypes.windll.user32.SetCursorPos(
            random.randint(0, 1920),
            random.randint(0, 1080)
        )
        time.sleep(0.1)

def fake_disk_wipe():
    print(Fore.RED + "\n[!!!] DELETING SYSTEM32...")
    for i in range(1, 101):
        print(Fore.RED + f"[{i}%] C:\\Windows\\System32\\*.* ERASED")
        time.sleep(0.05)

def fake_ransom_note():
    note = f"""
    {Fore.RED}
    ╔════════════════════════════════════════════╗
    ║ !!! ALL YOUR FILES HAVE BEEN ENCRYPTED !!! ║
    ║                                            ║
    ║ PAY 0.5 BITCOIN TO:                        ║
    ║ bc1qthemeforgefakewalletxxxxxxxxxxxxxx     ║
    ║                                            ║
    ║ OR YOUR DATA WILL BE LEAKED TO THE DARK WEB ║
    ╚════════════════════════════════════════════╝
    """
    print(note)

# ===== MAIN HACK SIMULATION =====
def print_scary_intro():
    print(Fore.RED + r"""
     _____ _    _ _____ _____ _  ________ _____  
    / ____| |  | |_   _|  __ \ |/ /  ____|  __ \ 
   | (___ | |__| | | | | |__) | ' /| |__  | |__) |
    \___ \|  __  | | | |  ___/|  < |  __| |  _  / 
    ____) | |  | |_| |_| |    | . \| |____| | \ \ 
   |_____/|_|  |_|_____|_|    |_|\_\______|_|  \_\
    """)
    print(Fore.RED + ">> YOUR PC IS NOW REMOTELY CONTROLLED BY THEMEFORGE <<\n")

def simulate_hack():
    print(Fore.YELLOW + "[+] Exploiting Zero-Day Vulnerability...")
    time.sleep(1)
    print(Fore.RED + "[+] Bypassing Windows Defender...")
    time.sleep(0.7)
    print(Fore.RED + "[+] Injecting Rootkit Payload...")
    time.sleep(1)
    print(Fore.RED + "[+] ACCESS GRANTED: ADMIN PRIVILEGES OBTAINED\n")

def steal_all_data():
    print(Fore.RED + "[!] STEALING YOUR DATA:")
    stolen_data = [
        "Browser Cookies", "Saved Passwords", "Credit Card Info",
        "IP: 192.168.1." + str(random.randint(1, 255)),
        "Minecraft Account", "Discord Token", "WiFi Passwords"
    ]
    for data in stolen_data:
        print(Fore.RED + f"    - {data} → SENT TO THEMEFORGE SERVERS")
        time.sleep(0.3)

def open_doomsday_terminals():
    for _ in range(100):  # 100 Fenster!
        os.system("start cmd /k echo !!! GOT HACKED BY THEMEFORGE !!! && color 0C")
        time.sleep(0.02)

def endless_terror_loop():
    while True:
        ctypes.windll.user32.BlockInput(True)  # Maus/Tastatur kurz blockieren
        time.sleep(0.5)
        ctypes.windll.user32.BlockInput(False)
        print(Fore.RED + "!!! YOUR FILES ARE NOW ENCRYPTED !!! PAY BITCOIN TO UNLOCK !!!")
        time.sleep(0.1)

# ===== START THE HORROR =====
if __name__ == "__main__":
    # 1. Starte gruselige Effekte
    threading.Thread(target=play_scary_sound).start()
    threading.Thread(target=fake_mouse_movement).start()
    
    # 2. Fake-Hacking-Animation
    print_scary_intro()
    simulate_hack()
    steal_all_data()
    fake_blue_screen()
    
    # 3. Öffne 100 CMD-Fenster + Fake-Datenlöschung
    threading.Thread(target=open_doomsday_terminals).start()
    threading.Thread(target=fake_disk_wipe).start()
    
    # 4. Fake-Ransomware-Note
    fake_ransom_note()
    
    # 5. Endlos-Terror-Loop (bis man es killt)
    endless_terror_loop()