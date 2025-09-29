#!/usr/bin/env python3

import os
import subprocess
import plistlib
import io
import getpass
import sys
from typing import Optional
import platform

def clear_terminal():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux, macOS, etc.
        os.system('clear')

#     print(TERMINAL_GRUEN("VERSION: 0x4E4554535445524D494E454C2D56322E30"))

# farben _______________________________________________________________
RESET = "\x1b[0m"

def hintergrund_grau(stufe=235):
    # stufe: 232 (dunkel) bis 255 (hell)
    print(f"\x1b[48;5;{stufe}m\x1b[2J\x1b[H", end="")

# Vordergrundfarben
def SCHWARZ(text):      return f"\x1b[30m{text}{RESET}"
def ROT(text):          return f"\x1b[31m{text}{RESET}"
def GRUEN(text):        return f"\x1b[32m{text}{RESET}"
def GELB(text):         return f"\x1b[33m{text}{RESET}"
def BLAU(text):         return f"\x1b[34m{text}{RESET}"
def MAGENTA(text):      return f"\x1b[35m{text}{RESET}"
def CYAN(text):         return f"\x1b[36m{text}{RESET}"
def WEISS(text):        return f"\x1b[37m{text}{RESET}"
def ORANGE(text):       return f"\x1b[38;5;208m{text}{RESET}"

# Terminal-Grün (klassisches Terminalgrün, ANSI 256-Farbe 46)
def TERMINAL_GRUEN(text): return f"\x1b[38;5;46m{text}{RESET}"

# Helle Vordergrundfarben
def HELL_SCHWARZ(text): return f"\x1b[90m{text}{RESET}"
def HELL_ROT(text):     return f"\x1b[91m{text}{RESET}"
def HELL_GRUEN(text):   return f"\x1b[92m{text}{RESET}"
def HELL_GELB(text):    return f"\x1b[93m{text}{RESET}"
def HELL_BLAU(text):    return f"\x1b[94m{text}{RESET}"
def HELL_MAGENTA(text): return f"\x1b[95m{text}{RESET}"
def HELL_CYAN(text):    return f"\x1b[96m{text}{RESET}"
def HELL_WEISS(text):   return f"\x1b[97m{text}{RESET}"
def ORANGE_BG(text):    return f"\x1b[48;5;208m{text}{RESET}"

# Hintergrundfarben
def SCHWARZ_BG(text):   return f"\x1b[40m{text}{RESET}"
def ROT_BG(text):       return f"\x1b[41m{text}{RESET}"
def GRUEN_BG(text):     return f"\x1b[42m{text}{RESET}"
def GELB_BG(text):      return f"\x1b[43m{text}{RESET}"
def BLAU_BG(text):      return f"\x1b[44m{text}{RESET}"
def MAGENTA_BG(text):   return f"\x1b[45m{text}{RESET}"
def CYAN_BG(text):      return f"\x1b[46m{text}{RESET}"
def WEISS_BG(text):     return f"\x1b[47m{text}{RESET}"
#______________________________________________________________________

#serien nummer


def _run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()

def _run_bytes(cmd: list[str]) -> bytes:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)

def _clean(s: str) -> str:
    # Entfernt typische Header/Leerzeilen
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())

def get_serial_number() -> Optional[str]:
    system = platform.system()

    if system == "Darwin":  # macOS
        # 1) Bevorzugt: system_profiler als XML und mit plistlib parsen
        try:
            raw = _run_bytes(["system_profiler", "-xml", "SPHardwareDataType"])
            plist = plistlib.load(io.BytesIO(raw))
            info = plist[0]["_items"][0]
            serial = info.get("serial_number") or info.get("serial_number_system")
            if serial:
                return serial.strip()
        except Exception:
            pass

        # 2) Fallback: ioreg als Plist und IOPlatformSerialNumber auslesen
        try:
            raw = _run_bytes(["ioreg", "-a", "-d2", "-c", "IOPlatformExpertDevice"])
            arr = plistlib.load(io.BytesIO(raw))
            if isinstance(arr, list) and arr:
                props = arr[0].get("IORegistryEntryChildren", [{}])[0].get("IOPlatformSerialNumber")
                if props:
                    return str(props).strip()
        except Exception:
            pass

        return None

    elif system == "Windows":
        # 1) PowerShell (modern, WMIC ist teils veraltet)
        try:
            ps_cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance -ClassName Win32_BIOS).SerialNumber"
            ]
            out = _clean(_run(ps_cmd))
            if out:
                return out
        except Exception:
            pass

        # 2) Fallback: WMIC (auf manchen Systemen noch vorhanden)
        try:
            out = _clean(_run(["wmic", "bios", "get", "serialnumber"]))
            lines = [l for l in out.splitlines() if l.lower() != "serialnumber"]
            if lines:
                return lines[-1].strip()
        except Exception:
            pass

        return None

    else:
        # Optionaler Linux-Pfad (falls du’s doch mal brauchst)
        try:
            path = "/sys/class/dmi/id/product_serial"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    s = f.read().strip()
                    return s or None
        except Exception:
            pass
        return None

#-----
def titel_1(titel):
    sys.stdout.write(f"\33]0;{titel}\a")
    sys.stdout.flush()

def eingabe_(input):
    klein = input.lower()
    print
    if "cls" in klein or "clear" in klein:
        titel_1("NETSPECTRE PRO TERMINEL: CLEAR")
        if " -L" in input:
            start()
        else:
            clear_terminal()
            netspro()
    elif klein == "exit":
        clear_terminal()
        sys.exit(0)
    elif  "--version" in klein:
        titel_1("NETSPECTRE PRO TERMINEL: VERSION")
        if " -a" in klein:
            print("Version Name: Net Spectre Pro Terminel (MacOs and Win) V2.1.0")
            print(TERMINAL_GRUEN("VERSION: 0x4E4554535445524D494E454C2D56322E312E30"))
            netspro()
        else:
            print(TERMINAL_GRUEN("VERSION: 0x4E4554535445524D494E454C2D56322E312E30"))
            netspro()
    else:
        titel_1("NETSPECTRE PRO TERMINEL: ERROR")
        print(ROT_BG("We diddent find that command                                 "))
        print(ROT_BG("                                                             "))
        print(ROT_BG("you've found an error or found a coomand that we shold add?  "))
        print(ROT_BG("Please feel free to email me: Hendrik.Hanking@icloud.com     "))
        netspro()

def logo_netspro():
    return(ORANGE(r""" 
   _  __    __    ____             __            ___  ___  ____ 
  / |/ /__ / /_  / __/__  ___ ____/ /________   / _ \/ _ \/ __ \
 /    / -_) __/ _\ \/ _ \/ -_) __/ __/ __/ -_) / ___/ , _/ /_/ /
/_/|_/\__/\__/ /___/ .__/\__/\__/\__/_/  \__/ /_/  /_/|_|\____/ 
                  /_/                                           """))


def netspro():
    user = getpass.getuser()
    print("")
    eingabe = input(TERMINAL_GRUEN(f"{user}@{get_serial_number()}-0x4E455453 ~/ "))
    print(eingabe_(eingabe))

def start():
    clear_terminal()
    titel_1("NETSPECTRE PRO TERMINEL")
    print("NICHT WEITERGEBEN")
    print("Copyright Hendrik Hanking 2025")
    print("")
    print(ROT_BG("FOR EDUCATIONAL PERPUSUS ONLY"))
    print(TERMINAL_GRUEN(logo_netspro()))
    print("")
    netspro()
start()