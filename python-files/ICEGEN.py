import random
import sys
import os
import time
import string

# Set terminal to fullscreen (Windows only)
os.system('mode con: cols=120 lines=40')

# Settings
TERM_WIDTH = 120
enable_colors = True

# Define code generators for each card type
def apple_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def steam_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def amazon_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def google_play_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def xbox_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def psn_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def roblox_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def netflix_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def spotify_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def ebay_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def walmart_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def bestbuy_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def visa_prepaid_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def mastercard_prepaid_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def doordash_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def uber_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def starbucks_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def nintendo_eshop_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def riot_games_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def hulu_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def disney_plus_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

# Gift card dictionary with code generator mappings
gift_cards = {
    1: ("Apple", apple_code),
    2: ("Steam", steam_code),
    3: ("Amazon", amazon_code),
    4: ("Google Play", google_play_code),
    5: ("Xbox", xbox_code),
    6: ("PlayStation (PSN)", psn_code),
    7: ("Roblox", roblox_code),
    8: ("Netflix", netflix_code),
    9: ("Spotify", spotify_code),
    10: ("eBay", ebay_code),
    11: ("Walmart", walmart_code),
    12: ("Best Buy", bestbuy_code),
    13: ("Visa Prepaid", visa_prepaid_code),
    14: ("MasterCard Prepaid", mastercard_prepaid_code),
    15: ("DoorDash", doordash_code),
    16: ("Uber", uber_code),
    17: ("Starbucks", starbucks_code),
    18: ("Nintendo eShop", nintendo_eshop_code),
    19: ("Riot Games", riot_games_code),
    20: ("Hulu", hulu_code),
    21: ("Disney+", disney_plus_code),
}

# Color handling
def print_color(text, color='ice'):
    colors = {
        'ice': '\033[96m',     # Light cyan (ice blue)
        'green': '\033[92m',   # Green
        'red': '\033[91m',     # Red
        'reset': '\033[0m'
    }
    if enable_colors:
        print(colors.get(color, colors['reset']) + text + colors['reset'])
    else:
        print(text)

def center_text(text):
    return text.center(TERM_WIDTH)

def clear_screen():
    print("\033c", end="")

# Corrected Banner for "ICEGEN"
def print_big_icegen():
    print_color("=" * TERM_WIDTH, 'ice')
    print()
    print_color(center_text(" ██▓ ▄████▄  ▓█████      ▄████ ▓█████  ███▄    █ "), 'ice')
    print_color(center_text("▓██▒▒██▀ ▀█  ▓█   ▀     ██▒ ▀█▒▓█   ▀  ██ ▀█   █ "), 'ice')
    print_color(center_text("▒██▒▒▓█    ▄ ▒███      ▒██░▄▄▄░▒███   ▓██  ▀█ ██▒"), 'ice')
    print_color(center_text("░██░▒▓▓▄ ▄██▒▒▓█  ▄    ░▓█  ██▓▒▓█  ▄ ▓██▒  ▐▌██▒"), 'ice')
    print_color(center_text("░██░▒ ▓███▀ ░░▒████▒   ░▒▓███▀▒░▒████▒▒██░   ▓██░"), 'ice')
    print_color(center_text("░▓  ░ ░▒ ▒  ░░░ ▒░ ░    ░▒   ▒ ░░ ▒░ ░░ ▒░   ▒ ▒ "), 'ice')
    print_color(center_text(" ▒ ░  ░  ▒    ░ ░  ░     ░   ░  ░ ░  ░░ ░░   ░ ▒░"), 'ice')
    print_color(center_text(" ▒ ░░           ░      ░ ░   ░    ░      ░   ░ ░ "), 'ice')
    print_color(center_text(" ░  ░ ░         ░  ░         ░    ░  ░         ░ "), 'ice')
    print_color(center_text("    ░                                             "), 'ice')
    print()
    print_color(center_text("❄  ICEGEN - BEST GIFT CARD GENERATOR  ❄"), 'ice')  # Updated text
    print()
    print_color("=" * TERM_WIDTH, 'ice')
    print()

# Menu
def show_menu():
    print_color(center_text("🎁 Select a Gift Card:"), 'ice')
    print()

    # Print gift cards as two columns
    for i in range(1, 12):  # Loop for left column (1 to 10)
        left_item = f"[{i}] {gift_cards[i][0]}"
        print_color(f"{left_item.ljust(TERM_WIDTH // 2)}", 'ice')

    for i in range(11, 22):  # Loop for right column (11 to 21)
        right_item = f"[{i}] {gift_cards[i][0]}"
        print_color(f"{right_item.rjust(TERM_WIDTH)}", 'ice')

    print_color(center_text("[0] Exit"), 'red')
    print()

# Login
def login():
    correct_username = "ICEGEN"
    correct_password = "ISTHEBEST"

    print_color(center_text("🔐 Login to continue"), 'ice')
    username = input("Username: ")
    password = input("Password: ")

    if username == correct_username and password == correct_password:
        print_color(center_text("✅ Login successful! 😊"), 'green')
        return True
    else:
        print_color(center_text("❌ Incorrect username or password!"), 'red')
        return False

# Function to generate a random money value between $15.00 and $150.00
def generate_random_money():
    return round(random.uniform(15.00, 150.00), 2)

# Code generation with delay and money amount
def generate_codes(card_choice, quantity):
    card_name, code_generator = gift_cards.get(card_choice, (None, None))

    if card_name:
        print(f"Generating {quantity} codes for {card_name}:")
        
        start_time = time.time()
        for i in range(quantity):
            # Simulate delay of 5 seconds for each code
            time.sleep(5)  # 5 seconds delay
            generated_code = code_generator()

            # Every 1 minute, choose 1 random code and give it money
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1500:
                random_money = generate_random_money()
                print_color(f" → {generated_code} ${random_money:.2f}", 'green')  # Green for money code
                start_time = time.time()  # Reset the timer
            else:
                print_color(f" → {generated_code} $0.00", 'red')  # Red for $0.00 codes
    else:
        print("Invalid selection.")
    print()

# Main program
def run():
    clear_screen()
    print_big_icegen()

    if not login():
        sys.exit()

    # Adding the "Loading, Please Wait" message with a few seconds delay
    print_color(center_text("🔄 Loading, please wait..."), 'ice')
    time.sleep(3)  # 3 seconds delay for loading message

    while True:
        clear_screen()
        show_menu()

        try:
            choice = int(input("Your choice (0–21): ").strip())
        except ValueError:
            print_color(center_text("⚠ Invalid selection. Please pick 0–21."), 'red')
            continue
        
        print()

        if choice == 0:
            print_color(center_text("👋 Exiting ICEGEN. Stay cool!"), 'ice')
            break

        elif choice in range(1, 22):
            quantity = int(input("How many codes? "))
            generate_codes(choice, quantity)
            input(center_text("Press Enter to return to the menu..."))

        else:
            print_color(center_text("⚠ Invalid selection. Please pick 0–21."), 'red')

if __name__ == "__main__":
    run()
