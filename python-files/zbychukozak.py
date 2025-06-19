import pymem
import pymem.process
import re
from datetime import datetime

# 🕒 Sprawdzenie daty ważności
deadline = datetime(2025, 6, 20, 2, 0, 0)  # 20.06.2026 02:00
now = datetime.now()

if now > deadline:
    print("[!] Ten skrypt wygasł i nie może już działać.")
    input("\n[!] Naciśnij Enter, aby zamknąć...")
    exit()

try:
    print("[*] Łączenie z procesem csgo.exe...")
    pm = pymem.Pymem('csgo.exe')

    print("[*] Szukanie modułu client.dll...")
    try:
        client = pymem.process.module_from_name(pm.process_handle, 'client.dll')
    except:
        client = pymem.process.module_from_name(pm.process_handle, 'client_panorama.dll')

    print(f"[+] client.dll załadowany przy 0x{client.lpBaseOfDll:X}")
    clientModule = pm.read_bytes(client.lpBaseOfDll, client.SizeOfImage)

    print("[*] Wyszukiwanie wzorca bajtów...")
    pattern = re.search(rb'\x33\xC0\x83\xFA.\xB9\x20', clientModule)
    
    if not pattern:
        print("[-] Nie znaleziono wzorca. Offset prawdopodobnie się zmienił!")
    else:
        address = client.lpBaseOfDll + pattern.start() + 4
        current = pm.read_uchar(address)
        print(f"[+] Adres znaleziony: 0x{address:X}, aktualna wartość: {current}")

        new_value = 2 if current == 1 else 1
        pm.write_uchar(address, new_value)
        print(f"[✓] Zmieniono wartość na: {new_value}")

    pm.close_process()

except Exception as e:
    print(f"[!] Wystąpił błąd: {e}")

input("\n[!] Naciśnij Enter, aby zamknąć...")