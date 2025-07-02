import os
import time
import sys

def spoof():
    print("\nZamykam Steam...")
    os.system("taskkill /f /im steam.exe >nul 2>&1")  # Ukrycie błędów, jeśli Steam nie działa
    print("Odliczanie:")

    for i in range(1, 11):
        print(f"{i * 10}%")
        time.sleep(0.001)  # 1 milisekunda (realnie będzie prawie niezauważalne)
    
    print("Gotowe!\n")
    input("Naciśnij Enter, aby kontynuować...")

def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("----- Polaris Spoofer Beta -----\n")
        print("1. Spoof")
        print("2. Exit\n")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            spoof()
        elif choice == "2":
            print("Zamykanie programu...")
            time.sleep(1)
            sys.exit()
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")
            time.sleep(1)

if __name__ == "__main__":
    main()
