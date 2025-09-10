#clear console
import os
def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')
#clear console, nemazat
#autopytoexe , pro linux
#pyinstaller --onefile --console --target-architecture=win64 test.py , pro windows

import sys
import pyautogui   # pyright: ignore[reportMissingModuleSource]
import time
import keyboard # pyright: ignore[reportMissingModuleSource]

#funkce
def userExit():
    sys.exit()

def menu():
    print("   aping's spammer menu:   ")
    print("---------------------------")
    print("1. infinite spammer")
    print("2. word spammer")
    print("(for exiting the program use: ctrl + b)")
    option = input("enter your option: ")

    if option == "1":
        print("---------------------------")
        userInput = input("enter your sentence to spam: ")
        print("---------------------------")
        print("move cursor to the input field and press 'enter' to create coordinations for script")
        print("(dont move with windows after getting coordinations!!)")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        print(f"coordinations: x={x}, y={y}")
        time.sleep(1)
        while True:
            pyautogui.write(userInput, 0.1)
            pyautogui.press("enter")
            
            if keyboard.is_pressed("ctrl+b"):
                userExit()

    elif option == "2":
        print("---------------------------")
        userInput = input("enter your sentence to spam: ")
        print("---------------------------")
        userCount = input("enter how many times you want to spam the sentence(number): ")
        
        if userCount == "":
            print("not an option")
            time.sleep(2)
            clearConsole()
            menu() 

        print("---------------------------")
        print("move cursor to the input field and press 'enter' to create coordinations for script")
        print("(dont move with windows after getting coordinations!!)")
        keyboard.wait("enter")
        x, y = pyautogui.position()
        print(f"coordinations: x={x}, y={y}")
        time.sleep(1)

        i = 1
        while i <= int(userCount):
            pyautogui.write(userInput, 0.1)
            pyautogui.press("enter")
            i = i+1
            
            if keyboard.is_pressed("ctrl+b"):
                userExit()

    else:
        print("not an option")
        time.sleep(2)
        clearConsole()
        menu()
    
#script
clearConsole()
menu()