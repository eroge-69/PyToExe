import os
import subprocess
import getpass
import time
from colorama import init, Fore

# Initialize colorama
init()

# Program list (use full paths or ensure they're in PATH)
PROGRAMS = [
    r"C:\Users\lucae\AppData\Local\Programs\Opera GX\opera.exe",  # Opera GX
    r"C:\Users\lucae\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk",
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\JetBrains\IntelliJ IDEA Community Edition 2025.1.1.1.lnk"
]

def show_loading_screen():
    """Displays a loading animation"""
    print(Fore.CYAN + "Sentinel: System activation starting..." + Fore.RESET)
    for i in range(1, 11):
        progress = "[" + "="*i + " "*(10-i) + "]"
        print(f"\r{progress} {i*10}%", end="")
        time.sleep(0.2)
    print("\n" + Fore.GREEN + "Sentinel: Activation complete." + Fore.RESET)
    time.sleep(1)

def show_auth_screen():
    """Simple authentication prompt"""
    print(Fore.CYAN + "\n=== Sentinel Authentication Protocol ===" + Fore.RESET)
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    if not username or not password:
        print(Fore.RED + "Error: Username and password cannot be empty!" + Fore.RESET)
        exit(1)
        
    print(Fore.GREEN + f"Sentinel: Access granted for {username}." + Fore.RESET)
    time.sleep(1)

def start_programs():
    """Launches programs with welcome messages"""
    print(Fore.CYAN + "\n=== Sentinel: Initializing System Environment ===" + Fore.RESET)
    
    for program in PROGRAMS:
        try:
            program_name = os.path.splitext(os.path.basename(program))[0].title()
            print(Fore.GREEN + f"Sentinel: Starting {program_name}..." + Fore.RESET)
            
            # Launch program (handles both Windows and cross-platform)
            if os.name == 'nt':  # Windows
                os.startfile(program) if os.path.exists(program) else subprocess.Popen(program)
            else:  # Other OS
                subprocess.Popen(program.split())
                
            print(Fore.CYAN + f"Sentinel: Welcome to {program_name}." + Fore.RESET)
            time.sleep(1)
            
        except Exception as e:
            print(Fore.RED + f"Error launching {program}: {e}" + Fore.RESET)
            continue
    
    print(Fore.GREEN + "\nSentinel: System environment fully initialized." + Fore.RESET)

def welcome_terminal():
    """Displays ASCII art welcome screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + r"""
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
    """ + Fore.RESET)
    print(Fore.YELLOW + "=== Sentinel System v2.0 ===" + Fore.RESET)

def main():
    welcome_terminal()
    show_loading_screen()
    show_auth_screen()
    start_programs()
    
    # Wait for user to exit
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
