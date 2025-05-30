import time
import threading
import keyboard  # pip install keyboard
import winsound

running = True
lupa_abierta = False

def abrir_lupa():
    global lupa_abierta
    if not lupa_abierta:
        print("Abriendo la lupa...")
        keyboard.press_and_release('windows + plus')
        time.sleep(1)
        lupa_abierta = True

def toggle_invert():
    keyboard.press_and_release('ctrl+alt+i')

def loop_toggle_and_beep():
    abrir_lupa()
    while running:
        toggle_invert()
        winsound.Beep(800, 300)  # beep 800Hz, 300ms
        time.sleep(0.5)

try:
    print("Iniciando inversión de colores + beep + sonido en loop. Ctrl+C para salir.")

    # Reproducir sonido wave.wav en loop (archivo debe estar en la misma carpeta)
    winsound.PlaySound("wave.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)

    thread = threading.Thread(target=loop_toggle_and_beep)
    thread.start()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nDeteniendo programa...")
    running = False
    thread.join()
    # Parar sonido
    winsound.PlaySound(None, winsound.SND_PURGE)
    # Restaurar colores normales
    toggle_invert()
    print("Colores restaurados y sonido detenido.")
