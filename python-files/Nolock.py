import ctypes
import time

# Movimiento relativo del mouse
def mover_mouse():
    x = 1  # Puedes ajustar este valor si quieres
    ctypes.windll.user32.mouse_event(0x0001, x, 1, 0, 0)
    ctypes.windll.user32.mouse_event(0x0001, -x, 1, 0, 0)

def mantener_activo():
    print("aMoGos")
    try:
        while True:
            mover_mouse()
            time.sleep(30)  # Cada 60 segundos
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")

mantener_activo()
