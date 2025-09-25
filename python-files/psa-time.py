import time
import pyautogui

# délai avant envoi pour te permettre de placer le focus
time.sleep(0.8)

sequence = [
    "N", "tab","O","tab","O","tab","O","tab","O","tab","O","tab",
    "N","tab","N","tab","O","tab","O","tab","O","tab","O","tab",
    "O","tab","N","tab","N","tab","O","tab","O","tab","O","tab",
    "O","tab","O","tab","N","tab","tab",
    "1","tab","1","tab","1","tab","1","tab","1","tab","tab","tab",
    "R","tab","S","tab","S","tab","S","tab","R","tab","tab","tab",
    "R","tab","S","tab","S","tab","S","tab","R","enter"
]

# map simple pour pyautogui (pyautogui uses 'tab' and 'enter' as keywords)
def send(token):
    if token.lower() == "tab":
        pyautogui.press('tab')
    elif token.lower() == "enter":
        pyautogui.press('enter')
    else:
        # send single character (handles letters/numbers)
        pyautogui.typewrite(token)
    # petit délai pour fiabilité
    time.sleep(0.04)

for t in sequence:
    send(t)
