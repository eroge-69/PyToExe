import pyautogui as automation
from time import sleep

print("Welcome to Automation!")
print("How many loops do you want?")
loop = int(input("insert here: "))

print("Starting automation")
for number in range(0, loop):
    print(f"Loop number:  {number}")
    automation.moveTo(965, 100, duration=5)
    sleep(30)
    automation.moveTo(400, 150, duration=5)
    sleep(30)


print("Finished!")
