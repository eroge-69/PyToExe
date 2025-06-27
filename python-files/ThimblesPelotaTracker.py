
import cv2
import numpy as np
import pyautogui
import time

# ===================== CONFIGURACIÓN =====================
SCREEN_REGION = (0, 0, 1920, 1080)  # Ajusta si usas otra resolución
AUTO_CLICK = True  # Cambia a False si no quieres clic automático

print("Presiona 's' cuando la pelota esté visible para marcarla...")

# Esperar tecla 's' para seleccionar región con la pelota
while True:
    screenshot = pyautogui.screenshot(region=SCREEN_REGION)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    cv2.imshow("Selecciona la pelota con el mouse y presiona ENTER", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        from_center = False
        r = cv2.selectROI("Selecciona la pelota", frame, from_center)
        tracker = cv2.TrackerCSRT_create()
        ok = tracker.init(frame, r)
        break

print("Pelota marcada. Siguiendo...")

while True:
    screenshot = pyautogui.screenshot(region=SCREEN_REGION)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    ok, bbox = tracker.update(frame)
    if ok:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
    else:
        cv2.putText(frame, "Tracking perdido", (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    cv2.imshow("Seguimiento de la pelota", frame)
    key = cv2.waitKey(30) & 0xFF

    if key == 27:  # ESC para salir
        break

    # Si los vasos se han detenido, puedes forzar clic (ej: tecla c)
    if key == ord('c') and ok and AUTO_CLICK:
        center_x = int(bbox[0] + bbox[2] / 2)
        center_y = int(bbox[1] + bbox[3] / 2)
        pyautogui.click(x=center_x, y=center_y)
        print(f"Clic en coordenadas: ({center_x}, {center_y})")

cv2.destroyAllWindows()
