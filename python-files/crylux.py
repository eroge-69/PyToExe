import os
import sys
import time
from pystyle import Colors, Colorate, Center

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner = r"""
 ▄████████    ▄████████ ▄██   ▄    ▄█       ███    █▄  ▀████    ▐████▀ 
███    ███   ███    ███ ███   ██▄ ███       ███    ███   ███▌   ████▀  
███    █▀    ███    ███ ███▄▄▄███ ███       ███    ███    ███  ▐███    
███         ▄███▄▄▄▄██▀ ▀▀▀▀▀▀███ ███       ███    ███    ▀███▄███▀                 by vantixt
███        ▀▀███▀▀▀▀▀   ▄██   ███ ███       ███    ███    ████▀██▄     
███    █▄  ▀███████████ ███   ███ ███       ███    ███   ▐███  ▀███    
███    ███   ███    ███ ███   ███ ███▌    ▄ ███    ███  ▄███     ███▄  
████████▀    ███    ███  ▀█████▀  █████▄▄██ ████████▀  ████       ███▄ 
             ███    ███           ▀                                    
"""
    print(Colorate.Horizontal(Colors.purple_to_blue, Center.XCenter(banner)))
    title = Center.XCenter("╔═══════════════════════════════════════════════╗\n" +
                           "║                   ddos this nigga             ║\n" +
                           "╚═══════════════════════════════════════════════╝\n")
    print(Colorate.Horizontal(Colors.purple_to_blue, title))

def handle_selection(option):
    file_mapping = {
        "1": "ddos.py",
        "2": "port_scanner.py"
    }

    if option in file_mapping:
        script = file_mapping[option]
        if os.path.exists(script):
            print(Colorate.Horizontal(Colors.purple_to_blue, f"\n➤ Starting {script}...\n"))
            time.sleep(1)
            os.system(f'python {script}')
        else:
            print(Colorate.Horizontal(Colors.purple_to_blue, f"\n✖ Error: {script} not found in current directory!\n"))
    else:
        print(Colorate.Horizontal(Colors.purple_to_blue, "\n✖ Invalid option!\n"))

def main_menu():
    while True:
        clear_screen()
        display_banner()

        menu = """
        [1] ➤ DDoS Tool
        [2] ➤ Port Scanner
        [3] ➤ Exit
        """
        print(Colorate.Horizontal(Colors.purple_to_blue, Center.XCenter(menu)))

        choice = input(Colorate.Horizontal(Colors.purple_to_blue, Center.XCenter("Select an option ➤ ")))

        if choice == "3":
            print(Colorate.Horizontal(Colors.purple_to_blue, "\nExiting..."))
            time.sleep(1)
            sys.exit()
        else:
            handle_selection(choice)
            input(Colorate.Horizontal(Colors.purple_to_blue, "\nPress Enter to continue..."))

if __name__ == "__main__":
    main_menu()
