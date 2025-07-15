import pyautogui
import time

# Espera un momento para que todo esté listo
time.sleep(2)

# Presiona Windows + R para abrir el cuadro de ejecución
pyautogui.hotkey('win', 'r')

# Espera un segundo para asegurarse de que el cuadro de ejecución se abrió
time.sleep(1)

# Escribe 'cmd' en el cuadro de ejecución
pyautogui.write('cmd')

# Presiona Enter para abrir CMD
pyautogui.press('enter')

# Espera unos segundos para que se abra el CMD
time.sleep(2)

# Escribe 'ping google.com' en CMD
pyautogui.write('ping google.com')

# Presiona Enter para ejecutar el ping
pyautogui.press('enter')
