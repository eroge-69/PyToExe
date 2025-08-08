



import os
import time
from colorama import init, Fore
import pyperclip

# Initialize colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def center_text(text, width=80):
    return text.center(width)

def text_to_hex(text):
    return text.encode('utf-8').hex()

def hex_to_text(hex_string):
    try:
        return bytes.fromhex(hex_string).decode('utf-8')
    except ValueError:
        return "Invalid hexadecimal input."

def text_to_decimal(text):
    return ' '.join(str(ord(char)) for char in text)

def decimal_to_text(decimal_string):
    try:
        numbers = decimal_string.strip().split()
        return ''.join(chr(int(num)) for num in numbers)
    except ValueError:
        return "Invalid decimal input."

def show_menu():
    clear_screen()
    print("=" * 80)
    print(center_text("🔢 TEXT ENCODER/DECODER MENU 🔢"))
    print("=" * 80)
    print(center_text("1. Encode to Hexadecimal"))
    print(center_text("2. Decode from Hexadecimal"))
    print(center_text("3. Encode to Decimal (ASCII)"))
    print(center_text("4. Decode from Decimal"))
    print(center_text("5. Exit"))
    print("=" * 80)

def copy_prompt(result):
    choice = input(center_text("Copy result to clipboard? (y/n): ")).strip().lower()
    if choice == 'y':
        pyperclip.copy(result)
        print(center_text(Fore.YELLOW + "✅ Copied to clipboard!"))

def main():
    while True:
        show_menu()
        choice = input(center_text("Choose an option (1-5): ")).strip()

        if choice == '1':
            text = input(center_text("Enter text to encode to hex: "))
            hex_result = text_to_hex(text)
            print(center_text(Fore.GREEN + f"Hex: {hex_result}"))
            copy_prompt(hex_result)

        elif choice == '2':
            hex_input = input(center_text("Enter hex to decode: "))
            decoded = hex_to_text(hex_input)
            print(center_text(f"Text: {decoded}"))
            copy_prompt(decoded)

        elif choice == '3':
            text = input(center_text("Enter text to encode to decimal: "))
            decimal_result = text_to_decimal(text)
            print(center_text(Fore.BLUE + f"Decimal: {decimal_result}"))
            copy_prompt(decimal_result)

        elif choice == '4':
            decimal_input = input(center_text("Enter decimal (space-separated): "))
            decoded = decimal_to_text(decimal_input)
            print(center_text(f"Text: {decoded}"))
            copy_prompt(decoded)

        elif choice == '5':
            print(center_text("Goodbye! 👋"))
            time.sleep(1)
            break
        else:
            print(center_text("Invalid choice. Try again."))

        input(center_text("Press Enter to return to menu..."))

if __name__ == "__main__":
    main()

