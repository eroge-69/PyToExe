import win32api
import time
import pyautogui
while 1:
    time.sleep(15)
    win32api.mouse_event(0x0001, 0, 200)  # MOVEMENT: dx=0, dy=500
    pyautogui.write('t')
    pyautogui.write('/rtp')  # Type with quarter-second pause in between each key.
    pyautogui.press('enter')
    try:
        pyautogui.press(['fn', 'f2'])
    except:
        pyautogui.press('f2')
