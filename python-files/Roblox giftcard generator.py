import random
import time
import sys
from colorama import init, Fore, Style

# Initialize colorama
init()

def generate_code():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return '-'.join(''.join(random.choices(chars, k=4)) for _ in range(3))

def print_ascii_banner():
    ascii_art = Fore.GREEN + Style.BRIGHT + r"""
 _______             __        __                                      __   ______    __                                          __                                           
/       \           /  |      /  |                                    /  | /      \  /  |                                        /  |                                          
$$$$$$$  |  ______  $$ |____  $$ |  ______   __    __         ______  $$/ /$$$$$$  |_$$ |_     _______   ______    ______    ____$$ |        ______    ______   _______        
$$ |__$$ | /      \ $$      \ $$ | /      \ /  \  /  |       /      \ /  |$$ |_ $$// $$   |   /       | /      \  /      \  /    $$ |       /      \  /      \ /       \       
$$    $$< /$$$$$$  |$$$$$$$  |$$ |/$$$$$$  |$$  \/$$/       /$$$$$$  |$$ |$$   |   $$$$$$/   /$$$$$$$/  $$$$$$  |/$$$$$$  |/$$$$$$$ |      /$$$$$$  |/$$$$$$  |$$$$$$$  |      
$$$$$$$  |$$ |  $$ |$$ |  $$ |$$ |$$ |  $$ | $$  $$<        $$ |  $$ |$$ |$$$$/      $$ | __ $$ |       /    $$ |$$ |  $$/ $$ |  $$ |      $$ |  $$ |$$    $$ |$$ |  $$ |      
$$ |  $$ |$$ \__$$ |$$ |__$$ |$$ |$$ \__$$ | /$$$$  \       $$ \__$$ |$$ |$$ |       $$ |/  |$$ \_____ /$$$$$$$ |$$ |      $$ \__$$ |      $$ \__$$ |$$$$$$$$/ $$ |  $$ |      
$$ |  $$ |$$    $$/ $$    $$/ $$ |$$    $$/ /$$/ $$  |      $$    $$ |$$ |$$ |       $$  $$/ $$       |$$    $$ |$$ |      $$    $$ |      $$    $$ |$$       |$$ |  $$ |      
$$/   $$/  $$$$$$/  $$$$$$$/  $$/  $$$$$$/  $$/   $$/        $$$$$$$ |$$/ $$/         $$$$/   $$$$$$$/  $$$$$$$/ $$/        $$$$$$$/        $$$$$$$ | $$$$$$$/ $$/   $$/       
                                                            /  \__$$ |                                                                     /  \__$$ |                          
                                                            $$    $$/                                                                      $$    $$/                           
                                                             $$$$$$/                                                                        $$$$$$/         
       By - chain
    """ + Style.RESET_ALL
    print(ascii_art)

def ask_to_run():
    print_ascii_banner()
    print(Fore.WHITE + "Welcome to the Robux Gift Card Scanner (Definitely Real)")
    choice = input(Fore.WHITE + "Do you want to start scanning? (Y/N): ").strip().upper()
    print(Style.RESET_ALL)
    if choice != 'Y':
        print(Fore.MAGENTA + "Operation cancelled. No Robux today. Maybe tomorrow 💤" + Style.RESET_ALL)
        sys.exit()

def print_fake_scan():
    print(Fore.YELLOW + "Scanning for working Robux gift card codes...\n" + Style.RESET_ALL)
    time.sleep(1)

    attempts = random.randint(200, 500)
    for _ in range(attempts):
        code = generate_code()
        print(Fore.RED + f"[X] Invalid code: {code}" + Style.RESET_ALL)
        time.sleep(0.03)

    valid_code = generate_code()
    print(Fore.GREEN + f"\n[✔] VALID CODE FOUND: {valid_code}")
    time.sleep(1.5)
    print(Fore.CYAN + "Redeeming 1,000,000 Robux... 💸")
    time.sleep(2)
    print(Fore.MAGENTA + "\nJust kidding. You really thought? 😂" + Style.RESET_ALL)

if __name__ == "__main__":
    ask_to_run()
    print_fake_scan()


