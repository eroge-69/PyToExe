import os
import sys
import time

# Try importing colorama, install if not found
try:
    from colorama import Fore, Style, init
except ImportError:
    print("Installing colorama...")
    os.system(f"{sys.executable} -m pip install colorama")
    print("Installation complete. Restarting...")
    time.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)  # Restarts script cleanly

# Initialize colorama
init(autoreset=True)

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(
        f"{Fore.RED}    ____           {Fore.YELLOW}______      {Fore.GREEN}__           {Fore.CYAN}__      {Fore.MAGENTA}__            {Style.RESET_ALL}"
        f"\n{Fore.RED}   / __ \\__  __   {Fore.YELLOW}/ ____/___ _{Fore.GREEN}/ /______  __{Fore.CYAN}/ /___ _{Fore.MAGENTA}/ /_____  _____"
        f"\n{Fore.RED}  / /_/ / / / /  {Fore.YELLOW}/ /   / __ `/{Fore.GREEN} / ___/ / / /{Fore.CYAN} / __ `/{Fore.MAGENTA} __/ __ \\/ ___/"
        f"\n{Fore.RED} / ____/ /_/ /  {Fore.YELLOW}/ /___/ /_/ /{Fore.GREEN} / /__/ /_/ /{Fore.CYAN} / /_/ /{Fore.MAGENTA} /_/ /_/ / /    "
        f"\n{Fore.RED}/_/    \\__, /   {Fore.YELLOW}\\____/\\__,_/{Fore.GREEN}_/\\___/\\__,_/{Fore.CYAN}_/\\__,_/{Fore.MAGENTA}\\__/\\____/_/     "
        f"\n{Fore.RED}      /____/                                                     {Style.RESET_ALL}\n"
    )

def add(x, y): return x + y
def subtract(x, y): return x - y
def multiply(x, y): return x * y
def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

def calculator():
    while True:
        print_banner()
        print(f"{Fore.GREEN}=== Python Terminal Calculator ===")
        print(f"{Fore.GREEN}1. Add")
        print(f"{Fore.GREEN}2. Subtract")
        print(f"{Fore.GREEN}3. Multiply")
        print(f"{Fore.GREEN}4. Divide")
        print(f"{Fore.GREEN}5. Exit")

        choice = input(f"{Fore.GREEN}Choose an option (1-5): ")

        if choice == '5':
            print(f"{Fore.GREEN}Goodbye!")
            time.sleep(1)
            break

        if choice not in ['1', '2', '3', '4']:
            print(f"{Fore.GREEN}Invalid choice. Try again.")
            time.sleep(1.5)
            continue

        try:
            num1 = float(input(f"{Fore.GREEN}Enter first number: "))
            num2 = float(input(f"{Fore.GREEN}Enter second number: "))
        except ValueError:
            print(f"{Fore.GREEN}Invalid input. Numbers only.")
            time.sleep(1.5)
            continue

        if choice == '1':
            result = add(num1, num2)
        elif choice == '2':
            result = subtract(num1, num2)
        elif choice == '3':
            result = multiply(num1, num2)
        elif choice == '4':
            result = divide(num1, num2)

        print(f"{Fore.GREEN}Result: {result}")

        again = input(f"{Fore.GREEN}\nDo you want to perform another calculation? (Y/N): ").strip().lower()
        if again != 'y':
            print(f"{Fore.GREEN}Goodbye!")
            time.sleep(1)
            break

if __name__ == "__main__":
    calculator()
    input(f"{Fore.GREEN}Press Enter to exit...")
