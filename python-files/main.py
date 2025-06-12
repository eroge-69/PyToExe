import pyautogui
import time
import keyboard
import win32api
import win32con

def keypress(key):
    win32api.keybd_event(key,0 , 0 , 0)
    win32api.keybd_event(key,0,win32con.KEYEVENTF_KEYUP,0)
def count():
    pyautogui.FAILSAFE = True
    print("STARTING . . ." , sep='')

    for i in range (1 ,10):
        time.sleep(1)
        print(i)
    print("GO")
    


count()

pyautogui.press('l')
def main():
    orginallcolor = pyautogui.pixel(1894 , 1061)
    while True:
        color = pyautogui.pixel(1894 , 1061)
        time.sleep(0.001)
        if color != orginallcolor:

            keypress(74)
            keypress(72)
            keypress(80)
            keypress(75)
                     
            time.sleep(10)
            pyautogui.press('l') 
            for i in range (1 ,10):
                time.sleep(1)
                print(i)
                if i == 5:
                    pyautogui.press('l')
            print('GO')
            main()

            
main()
print('done')
