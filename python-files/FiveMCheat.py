import ctypes
import keyboard
import time
import threading
import os
from colorama import init, Fore, Style

# Inicjalizacja kolorów w konsoli
init()

# Ładowanie DLL
try:
    dll = ctypes.WinDLL("./FiveMCheatDLL.dll")
    print(Fore.GREEN + "[DLL] Załadowano bibliotekę FiveMCheatDLL.dll" + Style.RESET_ALL)
except Exception as e:
    print(Fore.RED + f"[DLL] Błąd ładowania DLL: {e}" + Style.RESET_ALL)
    exit(1)

# Status cheatów
cheats = {
    "1": {"name": "God Mode", "status": False, "func": dll.EnableGodMode},
    "2": {"name": "Unlimited Ammo", "status": False, "func": dll.EnableUnlimitedAmmo},
    "3": {"name": "Speed Hack", "status": False, "func": dll.EnableSpeedHack}
}

class CheatMenu:
    def __init__(self):
        self.menu_visible = False

    def toggle_menu(self):
        self.menu_visible = not self.menu_visible
        if self.menu_visible:
            self.display_menu()

    def display_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.RED + "===== CHEAT MENU FOR FIVEM =====\n" + Style.RESET_ALL)
        for key, cheat in cheats.items():
            status = "ON" if cheat["status"] else "OFF"
            print(f"{key}. {cheat['name']} [{status}]")
        print("\nNaciśnij odpowiedni numer, aby przełączyć cheat.")
        print("Naciśnij F5, aby zamknąć menu.")

    def handle_input(self):
        while True:
            if self.menu_visible:
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN:
                    key = event.name
                    if key in cheats:
                        cheat = cheats[key]
                        cheat["status"] = not cheat["status"]
                        result = cheat["func"](1 if cheat["status"] else 0)
                        print(Fore.CYAN + f"[Cheat] {cheat['name']}: {'WŁĄCZONY' if cheat['status'] else 'WYŁĄCZONY'} {'(Sukces)' if result else '(Błąd)'}" + Style.RESET_ALL)
                        self.display_menu()
            time.sleep(0.1)

def main():
    print(Fore.BLUE + "Witaj w programie Cheat dla FiveM!" + Style.RESET_ALL)
    print("Naciśnij F5, aby otworzyć menu.")

    menu = CheatMenu()

    # Uruchom obsługę inputu w osobnym wątku
    input_thread = threading.Thread(target=menu.handle_input)
    input_thread.daemon = True
    input_thread.start()

    # Rejestracja klawisza F5 do togglowania menu
    keyboard.add_hotkey('f5', menu.toggle_menu)

    # Główna pętla programu
    while True:
        time.sleep(1)

if _name_ == "_main_":
    main()