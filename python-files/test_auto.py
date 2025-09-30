# test_fill_form_clipboard.py
import pyautogui
import pyperclip
import time
import sys

# Seguridad: mueve el ratón a la esquina superior izquierda para abortar rápido
pyautogui.FAILSAFE = True

def wait_countdown(seconds):
    print(f"Tienes {seconds} segundos para poner la ventana del formulario en primer plano...")
    for i in range(seconds, 0, -1):
        print(i, end=" ", flush=True)
        time.sleep(1)
    print()

def click_and_write(x, y, text=None, use_clipboard=False, click_duration=0.1, write_interval=0):
    """Hace clic en (x, y) y escribe texto si se da."""
    print(f"Clic en ({x}, {y})")
    pyautogui.moveTo(x, y, duration=0)
    pyautogui.click(duration=click_duration) 
    if text is not None:
        if use_clipboard:
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
        else:
            pyautogui.write(text, interval=write_interval)
        print(f"Escribiendo: {text}")

def main():
    # Cuenta regresiva para preparar la ventana
    wait_countdown(2)

    try:
        # 1) Click (839, 421) — sin texto asociado
        click_and_write(839, 421, None)

        # 2) Click (246, 588) -> NOMBRE
        click_and_write(246, 588, "Paul")

        # 3) Click (652, 594) -> APELLIDO
        click_and_write(652, 594, "Atreides")

        # 4) Click (359, 705) -> FECHA
        click_and_write(359, 705, "01/01/1963")

        # 5) Click (685, 718) -> MAIL (usa portapapeles para @)
        click_and_write(685, 718, "paul@muadib.com", use_clipboard=True)

        # 6) Scroll (bajar)
        print("Haciendo scroll hacia abajo (-500)")
        pyautogui.scroll(-500)
        time.sleep(0.1)

        # 7) Click (333, 434) -> TELEFONO
        click_and_write(333, 360, "6123456789")

        # 8) Click (825, 536) -> último clic (por ejemplo, enviar)
        click_and_write(825, 536, None)

        print("Script finalizado.")
    except pyautogui.FailSafeException:
        print("\nAbortado por mover el ratón a la esquina (FailSafe).")
        sys.exit(1)
    except Exception as e:
        print(f"\nHa ocurrido un error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
