
import subprocess
import time
import pyautogui

# Paleidžia programą
subprocess.Popen(r'C:\RIV_GAMA\RIV_GAMA.EXE')

# Palaukiame, kol programa pasileis
time.sleep(5)

# Simuliuojame teksto ir klavišų įvedimą
pyautogui.write('ZILVINAS')
pyautogui.press('tab')
pyautogui.write('240170')
pyautogui.press('enter')
