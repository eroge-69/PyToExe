import pyautogui
import keyboard
import time
import math
import os
import sys

# Texto arcoíris en consola
def print_rainbow(text):
    colors = [
        '\033[91m',  # Rojo
        '\033[93m',  # Amarillo
        '\033[92m',  # Verde
        '\033[96m',  # Cyan
        '\033[94m',  # Azul
        '\033[95m',  # Magenta
    ]
    reset = '\033[0m'
    rainbow_text = ''
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        rainbow_text += f"{color}{char}"
    print(rainbow_text + reset)

# Limpieza de consola
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Menú principal
def mostrar_menu():
    clear_console()
    pico_logo = r"""
       /\
      /  \      __
     /----\    |==|
    /      \   |  |
   /  /\    \  |  |
  /__/  \____\_|__|
    """

    titulo = r"""
 __  __ _       _             
|  \/  (_)_ __ (_)_ __   __ _ 
| |\/| | | '_ \| | '_ \ / _` |
| |  | | | | | | | | | | (_| |
|_|  |_|_|_| |_|_|_| |_|\__, |
                        |___/ 
    """

    print(pico_logo)
    print_rainbow(titulo)
    print_rainbow("1. Iniciar el modo MINERO")
    print_rainbow("2. Salir")
    opcion = input("\nSelecciona una opción (1/2): ")
    return opcion.strip()

# Presionar tecla E
def presionar_e():
    pyautogui.press('e')

# Movimiento circular simulando WASD
def moverse_circular(tiempo_movimiento=5):
    start_time = time.time()
    interval = 0.1
    try:
        while time.time() - start_time < tiempo_movimiento:
            elapsed = time.time() - start_time
            angle = (elapsed * 2 * math.pi) / tiempo_movimiento
            x = math.cos(angle)
            y = math.sin(angle)

            if y > 0:
                keyboard.press('w')
            else:
                keyboard.press('s')

            if x > 0:
                keyboard.press('d')
            else:
                keyboard.press('a')

            presionar_e()
            time.sleep(interval)

            keyboard.release('w')
            keyboard.release('s')
            keyboard.release('a')
            keyboard.release('d')
    finally:
        for key in ['w', 'a', 's', 'd']:
            keyboard.release(key)

# Loop del modo minero
def modo_minero():
    print_rainbow("\n[*] Modo MINERO iniciado. Presiona 'q' para detener.")
    time.sleep(2)
    try:
        while not keyboard.is_pressed('q'):
            presionar_e()
            print("[*] Presionando E...")
            time.sleep(10)

            print("[*] Moviéndose en círculo y presionando E...")
            moverse_circular(5)
    except KeyboardInterrupt:
        print("\n[*] Modo minero detenido.")
    finally:
        for key in ['w', 'a', 's', 'd']:
            keyboard.release(key)
        print_rainbow("[*] Modo MINERO finalizado.")

# Programa principal
def main():
    while True:
        opcion = mostrar_menu()
        if opcion == "1":
            modo_minero()
        elif opcion == "2":
            print_rainbow("Saliendo del programa...")
            break
        else:
            print_rainbow("Opción inválida. Intenta de nuevo.")
            time.sleep(2)

if __name__ == "__main__":
    main()