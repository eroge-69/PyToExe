#!/usr/bin/env python3
import ctypes
import sys
import os

# ANSI escape codes for a retro feel
GREEN = '\033[92m'
CYAN = '\033[96m'
RESET = '\033[0m'

def is_admin() -> bool:
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()  # type: ignore
    except:
        return False

def run_as_admin():
    """Relaunch the script with admin rights."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1
    )
    sys.exit()

def main():
    # Header
    print(GREEN + "#" * 40 + RESET)
    print(GREEN + "#  Hola usuario, bienvenido al   #" + RESET)
    print(GREEN + "#  asistente de reparación de    #" + RESET)
    print(GREEN + "#      PandaSystems              #" + RESET)
    print(GREEN + "#" * 40 + "\n" + RESET)

    # Message
    print(CYAN + "El comando que estás a punto de ejecutar [SFC /scannow]")
    print("sirve para revisar y reparar archivos del sistema de Windows")
    print("que estén dañados o faltantes.\n" + RESET)

    # User prompt
    choice = input("¿Deseas continuar? Presiona \"S\" para aceptar o \"N\" para cerrar: ")
    choice = choice.strip().upper()

    if choice == "S":
        print("\nEjecutando SFC /scannow...\n")
        os.system("SFC /scannow")
    else:
        print("\n¡Gracias por ocupar los servicios de PandaSystems, vuelve pronto!")

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
    main()
