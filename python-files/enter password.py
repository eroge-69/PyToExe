import os

passcode = int(input("Enter Your Password: "))
if passcode == 2010:
    print("Shutting down...")
    os.system("shutdown /s /t 5")  
else:
    print("Incorrect password.")
