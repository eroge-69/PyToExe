import keyboard
import pyautogui
import time

pyautogui.FAILSAFE = False  # Fare köşeye gidince durmasın

print("F6'ya bas: /claim + tıklamalar + sa, hızlı kaydırma modu.")

while True:
    if keyboard.is_pressed("F6"):
        while keyboard.is_pressed("F6"):
            time.sleep(0.01)  # Spam önleme

        # 1. /claim yaz ve Enter
        pyautogui.press("t")
        time.sleep(0.05)
        pyautogui.typewrite("/claim")
        time.sleep(0.05)
        pyautogui.press("enter")
        time.sleep(0.1)

        # 2. Fareyi 20px sola kaydır ve tıkla (hızlı)
        pyautogui.moveRel(-20, 0, duration=0.05)
        pyautogui.click()
        time.sleep(0.05)

        # 3. "sa" yaz
        pyautogui.typewrite("sa")
        time.sleep(0.05)

        # 4. Fareyi 20px sola ve 20px aşağı kaydır ve tıkla (hızlı)
        pyautogui.moveRel(-20, 20, duration=0.05)
        pyautogui.click()

        print("Hızlı kaydırma işlemi tamamlandı!")

input("Program bitti, çıkmak için Enter'a basın...")
