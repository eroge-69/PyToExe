import ctypes
import time
import subprocess

# Windows-Struktur für LastInputInfo
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]

def get_idle_time():
    """Gibt die Leerlaufzeit in Sekunden zurück."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis / 1000.0
    else:
        return 0

def main():
    IDLE_LIMIT = 60  # Sekunden
    while True:
        idle_time = get_idle_time()
        if idle_time >= IDLE_LIMIT:
            print(f"Inaktivität erkannt ({int(idle_time)} Sekunden). Screensaver wird gestartet.")
            subprocess.call('rundll32.exe user32.dll,SendMessageA 0xFFFF 0x112 0xF140 0', shell=True)
            time.sleep(60)  # Warte, bevor du wieder prüfst
        time.sleep(5)  # Regelmäßige Abfrage

if __name__ == "__main__":
    main()