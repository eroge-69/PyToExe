import random
import string
from colorama import Fore, Style, init
import os

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print(Fore.RED + Style.BRIGHT + """
██╗     ██╗███████╗████████╗    ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗     ██╗   ██╗ ██╗
██║     ██║██╔════╝╚══██╔══╝    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗    ██║   ██║███║
██║     ██║███████╗   ██║       ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝    ██║   ██║╚██║
██║     ██║╚════██║   ██║       ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗    ╚██╗ ██╔╝ ██║
███████╗██║███████║   ██║       ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║     ╚████╔╝  ██║
╚══════╝╚═╝╚══════╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝      ╚═══╝   ╚═╝
""")
    print(Fore.RED + "        Username Generator | by Fq & MF2 | Need help? server:https://discord.gg/shAMcy3S")
    print(Fore.RED + "-" * 60)

def choose_format():
    print(Fore.RED + "Choose username format:")
    formats = [
        "1) 2 Letters + _",
        "2) 3 Letters + _",
        "3) 1 Letter + 1 Digit + _",
        "4) 4 Letters",
        "5) 2 Digits + 1 Letter + _",
        "6) 3 Digits + _",
        "7) 2 Letters + 2 Digits",
        "8) 1 Letter + 2 Digits + _",
        "9) 3 Letters",
        "10) 2 Digits + 2 Letters",
        "11) 1 Letter + 3 Digits",
        "12) 1 Digit + 1 Letter + 1 Digit + _",
        "13) 3 Letters + 1 Digit",
        "14) 2 Digits + _ + 1 Letter",
        "15) 4 Digits",
        "16) 2 Letters + 1 Digit + _",
        "17) 1 Letter + 2 Digits + 1 Letter",
        "18) 3 Digits + 2 Letters",
        "19) 1 Letter + _ + 2 Digits",
        "20) 2 Digits + 2 Digits + _"
    ]
    for fmt in formats:
        print(Fore.RED + fmt)
    choice = input(Fore.RED + "Enter option (1-20): ")
    return choice

def generate_username(choice):
    if choice == "1":
        return ''.join(random.choices(string.ascii_letters, k=2)) + '_'
    elif choice == "2":
        return ''.join(random.choices(string.ascii_letters, k=3)) + '_'
    elif choice == "3":
        return random.choice(string.ascii_letters) + random.choice(string.digits) + '_'
    elif choice == "4":
        return ''.join(random.choices(string.ascii_letters, k=4))
    elif choice == "5":
        return ''.join(random.choices(string.digits, k=2)) + random.choice(string.ascii_letters) + '_'
    elif choice == "6":
        return ''.join(random.choices(string.digits, k=3)) + '_'
    elif choice == "7":
        return ''.join(random.choices(string.ascii_letters, k=2)) + ''.join(random.choices(string.digits, k=2))
    elif choice == "8":
        return random.choice(string.ascii_letters) + ''.join(random.choices(string.digits, k=2)) + '_'
    elif choice == "9":
        return ''.join(random.choices(string.ascii_letters, k=3))
    elif choice == "10":
        return ''.join(random.choices(string.digits, k=2)) + ''.join(random.choices(string.ascii_letters, k=2))
    elif choice == "11":
        return random.choice(string.ascii_letters) + ''.join(random.choices(string.digits, k=3))
    elif choice == "12":
        return random.choice(string.digits) + random.choice(string.ascii_letters) + random.choice(string.digits) + '_'
    elif choice == "13":
        return ''.join(random.choices(string.ascii_letters, k=3)) + random.choice(string.digits)
    elif choice == "14":
        return ''.join(random.choices(string.digits, k=2)) + '_' + random.choice(string.ascii_letters)
    elif choice == "15":
        return ''.join(random.choices(string.digits, k=4))
    elif choice == "16":
        return ''.join(random.choices(string.ascii_letters, k=2)) + random.choice(string.digits) + '_'
    elif choice == "17":
        return random.choice(string.ascii_letters) + ''.join(random.choices(string.digits, k=2)) + random.choice(string.ascii_letters)
    elif choice == "18":
        return ''.join(random.choices(string.digits, k=3)) + ''.join(random.choices(string.ascii_letters, k=2))
    elif choice == "19":
        return random.choice(string.ascii_letters) + '_' + ''.join(random.choices(string.digits, k=2))
    elif choice == "20":
        return ''.join(random.choices(string.digits, k=2)) + ''.join(random.choices(string.digits, k=2)) + '_'
    else:
        return None

def main():
    clear()
    logo()

    format_choice = choose_format()
    if format_choice not in [str(i) for i in range(1, 21)]:
        print(Fore.RED + "Invalid choice.")
        return

    try:
        count = int(input(Fore.RED + "Enter number of usernames to generate: " + Fore.CYAN))
    except ValueError:
        print(Fore.RED + "Invalid number.")
        return

    print(Fore.RED + f"\nGenerating {count} usernames...\n")

    with open("username.txt", "w", encoding="utf-8") as f:
        for _ in range(count):
            username = generate_username(format_choice)
            if username:
                print(Fore.RED + "Generated: " + Fore.WHITE + username)
                f.write(username + "\n")
            else:
                print(Fore.RED + "Error in generation.")
                break

    print(Fore.GREEN + f"\nDone! Saved to {Fore.CYAN}username.txt\n")

if __name__ == "__main__":
    main()
