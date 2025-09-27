mytitle = "Phantaso - OwO Level Kasmak"
from os import system
system("title "+mytitle)

import pyautogui
import time
import random

Turkish_Characters = {
    "ç": "c",
    "Ç": "C",
    "ğ": "g",
    "Ğ": "G",
    "ı": "i",
    "İ": "I",
    "ö": "o",
    "Ö": "O",
    "ş": "s",
    "Ş": "S",
    "ü": "u",
    "Ü": "U"
}

def main():
    pyautogui.PAUSE = 0.03
    pyautogui.FAILSAFE = True

    print("Çalıştırmak istediğiniz yerin boş bir metin alanı olduğundan emin olun")

    time.sleep(5)
    print("\n1. metini gönderdim")

    with open("file.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    message_count = 1

    for line in lines:
        line = line.rstrip("\n")
        for char in line:
            if char in Turkish_Characters:
                pyautogui.press(Turkish_Characters[char])
            else:
                pyautogui.press(char)

        pyautogui.press('enter')
        wait_time = 15 + 5 * random.random()
        time.sleep(wait_time)
        message_count += 1
        print(f"{message_count}. metini gönderdim")

if __name__ == "__main__":
    main()
