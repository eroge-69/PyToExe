import os
import time
import ctypes
import subprocess

# Estilo consola: color verde sobre negro
os.system("title [ P R O T O C O L   N A V I U S // NETWORK MONITOR ]")
os.system("color 0A")
os.system("mode con: cols=80 lines=25")

def get_net_bytes():
    try:
        output = subprocess.check_output("netstat -e", shell=True, text=True)
        for line in output.splitlines():
            if "Bytes" in line:
                parts = line.split()
                rx = int(parts[1])
                tx = int(parts[2])
                return rx, tx
    except:
        return 0, 0
    return 0, 0

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    print("="*62)
    print("     ██████╗ ██████╗  ██████╗ ████████╗ ██████╗  ██████╗      ")
    print("    ██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝      ")
    print("    ██║  ███╗██████╔╝██║   ██║   ██║   ██║   ██║██║  ███╗     ")
    print("    ██║   ██║██╔══██╗██║   ██║   ██║   ██║   ██║██║   ██║     ")
    print("    ╚██████╔╝██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╔╝     ")
    print("     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝      ")
    print("="*62)
    print("     P R O T O C O L  N A V I U S - Monitoreo de velocidad en tiempo real")
    print()
    print("     Presiona Ctrl+C para salir")
    print("="*62)

# Mensaje de bienvenida
clear()
show_header()
time.sleep(2)

# Bucle principal
try:
    while True:
        rx1, tx1 = get_net_bytes()
        time.sleep(1)
        rx2, tx2 = get_net_bytes()

        down_diff = rx2 - rx1
        up_diff = tx2 - tx1
        down_rate = down_diff // 128  # bytes a Kbps
        up_rate = up_diff // 128

        clear()
        print("="*62)
        print("        P R O T O C O L   N A V I U S // MONITOREO EN TIEMPO REAL")
        print("="*62)
        print()
        print(f"  ↓ VELOCIDAD DE DESCARGA:   {down_rate} Kbps")
        print(f"  ↑ VELOCIDAD DE SUBIDA:     {up_rate} Kbps")
        print()
        print("  [Presiona Ctrl+C para salir]")
        print()
except KeyboardInterrupt:
    clear()
    print("Saliendo...")

