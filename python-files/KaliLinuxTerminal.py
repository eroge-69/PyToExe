import os
import time
import random

# Colores estilo terminal (verde sobre negro)
GREEN = '\033[92m'
RESET = '\033[0m'

# Banner al iniciar
banner = f"""
{GREEN}
  _  __     _ _ _     _     _            _     _ _ _       
 | |/ /__ _| | | |___| |__ (_)__ _ _ _  | |__ (_) | |_ ___ 
 | ' </ _` | | | / -_) '_ \| / _` | ' \ | '_ \| | |  _/ -_)
 |_|\_\__,_|_|_|_\___|_.__//_\__,_|_||_||_.__/_|_|\__\___|

         K A L I   -   H A C K   -   M A T I
{RESET}
"""

# Limpia pantalla
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Simula actividad de hackeo
def simulate_activity():
    actions = [
        "Scanning ports...",
        "Bypassing firewall...",
        "Injecting payload...",
        "Accessing mail server...",
        "Sending spoofed emails...",
        "Encrypting data...",
        "Downloading target files...",
        "Establishing backdoor...",
        "Extracting credentials...",
        "Launching exploit...",
    ]
    for _ in range(5):
        print(f"{GREEN}{random.choice(actions)}{RESET}")
        time.sleep(0.4)

# Terminal falsa estilo Kali
def kali_terminal():
    clear()
    print(banner)
    print(f"{GREEN}Welcome to Kali Fake Terminal. Type 'help' or 'exit'.{RESET}\n")
    
    while True:
        try:
            user_input = input(f"{GREEN}kali@root:~$ {RESET}")
            command = user_input.strip().lower()

            if command == "exit":
                print(f"{GREEN}Session terminated. Goodbye.{RESET}")
                break
            elif command == "help":
                print("Available commands: help, hack, clear, exit")
            elif command == "clear":
                clear()
                print(banner)
            elif command == "hack":
                print(f"{GREEN}Hacking and sending email selected x100...{RESET}")
                for _ in range(100):
                    print("Hacking and sending email selected")
                    time.sleep(0.01)
            elif command:
                simulate_activity()
                print(f"{GREEN}Command '{command}' executed successfully.{RESET}")
        except KeyboardInterrupt:
            print("\nUse 'exit' to leave the terminal.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    kali_terminal()
