import os
import sys

user_input = input("Enter command: ").strip().lower()

if user_input == "32bit":
    os.startfile("setupfor16and32bit.exe")
elif user_input == "setup":
    os.startfile("setup.exe")
else:
    print("Unknown command")