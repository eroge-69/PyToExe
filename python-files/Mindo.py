import random
import time
from colorama import Fore, Style, init
import sys
import itertools
import shutil
import string
import os
import json

init(autoreset=True)

RAINBOW_COLORS = [
    Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA
]

rainbow_cycle = itertools.cycle(RAINBOW_COLORS)

KEY_FILE = "admin_keys.json"
ADMIN_PANEL_PASSWORD = "adminpass123"

# Load keys from file
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r") as f:
        admin_keys = set(json.load(f))
else:
    admin_keys = set()

def save_keys():
    with open(KEY_FILE, "w") as f:
        json.dump(list(admin_keys), f)

def generate_admin_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_terminal_width():
    return shutil.get_terminal_size((80, 20)).columns

def rainbow_print(text):
    width = get_terminal_width()
    for line in text.split("\n"):
        centered_line = line.center(width)
        for char in centered_line:
            color = next(rainbow_cycle)
            sys.stdout.write(color + char)
        print(Style.RESET_ALL)

def admin_panel():
    password = input("Enter admin panel password: ")
    if password != ADMIN_PANEL_PASSWORD:
        rainbow_print("Incorrect password. Access denied.")
        return
    while True:
        rainbow_print("\nADMIN PANEL")
        rainbow_print("[1] Generate New Admin Key")
        rainbow_print("[2] View Existing Keys")
        rainbow_print("[3] Exit Admin Panel")
        choice = input("→ ")
        if choice == "1":
            new_key = generate_admin_key()
            admin_keys.add(new_key)
            save_keys()
            rainbow_print(f"New Admin Key Generated: {new_key}")
        elif choice == "2":
            if not admin_keys:
                rainbow_print("No admin keys generated yet.")
            else:
                for key in admin_keys:
                    rainbow_print(f"Key: {key}")
        elif choice == "3":
            break
        else:
            rainbow_print("Invalid choice. Try again.")

def admin_features():
    rainbow_print("Access granted to admin features.")
    admin_panel()

def generate_ms(ms_type, num_ms, click_range, cdc_range, extra=""):
    ms_list = []
    rainbow_print(f"\nGenerating {num_ms} entries for {ms_type}...\n")
    for i in range(num_ms):
        click_rate = round(random.uniform(*click_range), 2)
        duty_cycle = round(random.uniform(*cdc_range), 2)
        ms_entry = f"{ms_type} {i + 1}: Click Rate = {click_rate}, CDC = {duty_cycle} {extra}"
        rainbow_print(ms_entry)
        ms_list.append(ms_entry)
        time.sleep(0.001)
    return ms_list

def get_input(prompt):
    width = get_terminal_width()
    line = f"{'─' * (width - 2)}"
    print(f"\n╭{line}╮")
    centered_prompt = prompt.center(width)
    print(f"│{centered_prompt}│")
    print(f"╰{line}╯")
    return input("→ ")

def main():
    rainbow_print(r"""
  __  __ _           _       
 |  \/  (_)_ __   __| | ___  
 | |\/| | | '_ \ / _` |/ _ \ 
 | |  | | | | | | (_| | (_) |
 |_|  |_|_|_| |_|\__,_|\___/ 
                              
     W E L C O M E   T O   M I S C   G E N E R A T O R
    """)

    key_input = get_input("Enter Admin Key to unlock paid features or type 'adminpanel' to access Admin Panel")

    if key_input == "adminpanel":
        admin_features()
        return
    elif key_input in admin_keys:
        rainbow_print("Access granted. Welcome, paid user!")
    else:
        rainbow_print("Invalid key. Access denied.")
        sys.exit()

    while True:
        try:
            num_ms = int(get_input("Enter the number of MS entries to generate (max 50,000)"))
            if num_ms > 50000:
                rainbow_print("Maximum limit is 50,000.")
                continue

            rainbow_print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                          SELECT MS GENERATION TYPE                        ║
╠════════════════════════════════════════════════════════════════════════════╣
║ [01] ➤ THX 28 CPS      | 29.91–30.10 Click Rate  | CDC: 24.5–30           ║
║ [02] ➤ THX 20 CPS      | 20–22 Click Rate        | CDC: 5 (Fixed)         ║
║ [03] ➤ THX 14 CPS      | 14.39–14.55 Click Rate  | CDC: 5–100             ║
║ [04] ➤ Breakaway 28    | 28.98–29.10 Click Rate  | CDC: 49–52 (⚠️ Not Rec)║
║ [05] ➤ Breakaway 20    | 21.31–21.45 Click Rate  | CDC: 5–50              ║
║ [06] ➤ Breakaway 14    | 14.39–14.55 Click Rate  | CDC: 5–100             ║
║ [07] ➤ VAC 28 CPS      | 30–31 Click Rate        | CDC: 22–24             ║
║ [08] ➤ VAC 20 CPS      | 21–22 Click Rate        | CDC: 23–24             ║
║ [09] ➤ VAC 14 CPS      | 0–5 Click Rate          | CDC: 90–100            ║
║ [10] ➤ CUSTOM          | You choose your ranges!                          ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

            ms_choice = get_input("Enter choice (1–10)")
            if ms_choice == "1":
                generate_ms("THX 28 CPS", num_ms, (29.91, 30.10), (24.5, 30))
            elif ms_choice == "2":
                generate_ms("THX 20 CPS", num_ms, (20, 22), (5, 5))
            elif ms_choice == "3":
                generate_ms("THX 14 CPS", num_ms, (14.39, 14.55), (5, 100))
            elif ms_choice == "4":
                generate_ms("Breakaway 28 CPS", num_ms, (28.98, 29.10), (49, 52), "(Not Recommended)")
            elif ms_choice == "5":
                generate_ms("Breakaway 20 CPS", num_ms, (21.31, 21.45), (5, 50))
            elif ms_choice == "6":
                generate_ms("Breakaway 14 CPS", num_ms, (14.39, 14.55), (5, 100))
            elif ms_choice == "7":
                generate_ms("VAC 28 CPS", num_ms, (30, 31), (22, 24))
            elif ms_choice == "8":
                generate_ms("VAC 20 CPS", num_ms, (21, 22), (23, 24))
            elif ms_choice == "9":
                generate_ms("VAC 14 CPS", num_ms, (0, 5), (90, 100))
            elif ms_choice == "10":
                click_rate_min = float(get_input("Enter minimum Click Rate"))
                click_rate_max = float(get_input("Enter maximum Click Rate"))
                cdc_min = float(get_input("Enter minimum CDC"))
                cdc_max = float(get_input("Enter maximum CDC"))
                generate_ms("Custom MS", num_ms, (click_rate_min, click_rate_max), (cdc_min, cdc_max))
            else:
                rainbow_print("Invalid choice. Please choose 1–10.")
                continue

        except ValueError:
            rainbow_print("Invalid input. Please enter numbers only.")

if __name__ == "__main__":
    main()
