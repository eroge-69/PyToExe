import os
import json
import time
import ctypes
from random import shuffle, choice, randint

# ------------------ VISUAL ENHANCEMENTS ------------------ #
def maximize_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 3)

def press_f11():
    time.sleep(1)
    VK_F11 = 0x7A
    ctypes.windll.user32.keybd_event(VK_F11, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_F11, 0, 2, 0)

VK_CONTROL = 0x11
VK_ADD = 0x6B

def press_ctrl_plus():
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
    for _ in range(9):
        ctypes.windll.user32.keybd_event(VK_ADD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_ADD, 0, 2, 0)
        time.sleep(0.1)
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0)

# ------------------ FILES & DATA ------------------ #
USERS_FILE = "users.json"
POT_FILE = "pot.json"
SCOREBOARD_FILE = "scoreboard.json"

def initialize_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(POT_FILE):
        with open(POT_FILE, 'w') as f:
            json.dump({"pot": 0}, f)
    if not os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, 'w') as f:
            json.dump([], f)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_pot():
    with open(POT_FILE, 'r') as f:
        return json.load(f)

def save_pot(pot):
    with open(POT_FILE, 'w') as f:
        json.dump(pot, f, indent=4)

def load_scoreboard():
    if os.path.exists(SCOREBOARD_FILE):
        with open(SCOREBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_scoreboard(scoreboard):
    with open(SCOREBOARD_FILE, 'w') as f:
        json.dump(scoreboard, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------ AUTH ------------------ #
def login():
    clear_screen()
    users = load_users()
    print("==============================")
    print("        LOGIN SYSTEM")
    print("==============================\n")

    input_username = input("Enter your username: ").strip()
    username_key = input_username.lower()

    matching_user = None
    for stored_user in users:
        if stored_user.lower() == username_key:
            matching_user = stored_user
            break

    if matching_user:
        password = input("Enter your password: ")
        if users[matching_user]['password'] == password:
            print(f"\nWelcome back, {matching_user}!")
            time.sleep(1.5)
            return matching_user
        else:
            print("\nIncorrect password.")
            time.sleep(2)
            return None
    else:
        print(f"\nUsername '{input_username}' not found. Creating new account...")
        password = input("Set your password: ")
        users[input_username] = {"password": password, "balance": 1000, "stats": {"wins": 0, "losses": 0, "games_played": 0}}
        save_users(users)
        print(f"\nAccount created! Starting balance: $1000")
        time.sleep(2)
        return input_username

# ------------------ ADVANCED FEATURES ------------------ #
def update_user_stats(username, won):
    """
    This helper is still available for other parts of the program.
    It loads users itself and saves. Do not call this inside blackjack
    where blackjack also uses its own local `users` object — that caused
    the overwrite bug previously.
    """
    users = load_users()
    stats = users[username].get("stats", {"wins": 0, "losses": 0, "games_played": 0})
    stats["games_played"] += 1
    if won:
        stats["wins"] += 1
    else:
        stats["losses"] += 1
    users[username]["stats"] = stats
    save_users(users)

def display_stats(username):
    users = load_users()
    stats = users[username].get("stats", {})
    print("\nYour Statistics:")
    print(f"Games Played: {stats.get('games_played', 0)}")
    print(f"Wins: {stats.get('wins', 0)}")
    print(f"Losses: {stats.get('losses', 0)}")

def ensure_balance(username):
    users = load_users()
    if users[username]['balance'] <= 0:
        print("\nYou've run out of money! Here's a bonus to keep playing.")
        users[username]['balance'] = 500
        save_users(users)
        print("$500 has been added to your balance. Good luck!")
        time.sleep(2)

# ------------------ MAIN ------------------ #
def main():
    press_f11()
    maximize_console()
    press_ctrl_plus()
    initialize_files()

    print("==============================")
    print(" WELCOME TO PYTHON CASINO 🎰")
    print("==============================\n")
    time.sleep(1.5)

    user = None
    while not user:
        user = login()

    while True:
        clear_screen()
        users = load_users()
        ensure_balance(user)
        print("==============================")
        print(f"    Welcome, {user}!")
        print("==============================")
        print(f"Balance: ${users[user]['balance']}\n")
        display_stats(user)
        print("\nMain Menu:")
        print("1. Play Blackjack 🃏")
        print("2. Play Roulette 🎡")
        print("3. View Leaderboard 📊")
        print("4. Logout")
        print("5. Quit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            blackjack(user)
        elif choice == "2":
            try:
                from roulette import roulette
                roulette(user)
            except ImportError:
                print("Roulette module not found.")
                time.sleep(2)
        elif choice == "3":
            scoreboard = load_scoreboard()
            print("\n==============================")
            print("       TOP 3 SCOREBOARD")
            print("==============================")
            for idx, entry in enumerate(scoreboard[:3]):
                print(f"{idx+1}. {entry['username']} - ${entry['balance']}")
            input("\nPress Enter to continue...")
        elif choice == "4":
            user = None
            while not user:
                user = login()
        elif choice == "5":
            print("\nThanks for playing! Goodbye!\n")
            break
        else:
            print("\nInvalid option. Try again.")
            time.sleep(2)

# ========================================================= #
# =================== BLACKJACK MODULE ==================== #
# ========================================================= #
def deal_card():
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    return choice(cards)

def calculate_score(hand):
    score = sum(hand)
    # convert Aces from 11 to 1 as needed
    while score > 21 and 11 in hand:
        hand[hand.index(11)] = 1
        score = sum(hand)
    return score

def update_scoreboard(username, balance):
    scoreboard = load_scoreboard()
    found = False
    for entry in scoreboard:
        if entry["username"] == username:
            entry["balance"] = balance
            found = True
            break
    if not found:
        scoreboard.append({"username": username, "balance": balance})
    scoreboard.sort(key=lambda x: x["balance"], reverse=True)
    save_scoreboard(scoreboard[:10])

def blackjack(username):
    # Load state once and operate on this local users dict.
    users = load_users()
    pot = load_pot()

    # Defensive check - ensure username exists (should, but just in case)
    if username not in users:
        print("Error: user not found.")
        time.sleep(2)
        return

    balance = users[username]["balance"]
    if balance <= 0:
        print("\nYou don't have enough balance to play.")
        time.sleep(2)
        return

    # ------------------ BET ------------------ #
    while True:
        try:
            bet = int(input(f"\nPlace your bet (Balance: ${balance}): "))
            if bet > 0 and bet <= balance:
                break
            else:
                print("Invalid bet amount.")
        except ValueError:
            print("Enter a valid number.")

    # Deduct bet into pot (modify local users and pot)
    users[username]["balance"] -= bet
    pot["pot"] += bet

    # Save immediately the deducted bet so if program exits we don't lose money
    save_users(users)
    save_pot(pot)

    # ------------------ INITIAL DEAL ------------------ #
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
    game_over = False

    while not game_over:
        player_score = calculate_score(player_hand)
        dealer_score = calculate_score(dealer_hand)

        print(f"\nYour hand: {player_hand}, current score: {player_score}")
        print(f"Dealer's first card: {dealer_hand[0]}")

        # Player blackjack (natural)
        if player_score == 21:
            print("Blackjack! You win 🎉")
            winnings = int(bet * 2.5)
            users[username]["balance"] += winnings
            pot["pot"] -= winnings

            # update stats in the local users object
            stats = users[username].get("stats", {"wins": 0, "losses": 0, "games_played": 0})
            stats["games_played"] = stats.get("games_played", 0) + 1
            stats["wins"] = stats.get("wins", 0) + 1
            users[username]["stats"] = stats

            # persist and update scoreboard
            save_users(users)
            save_pot(pot)
            update_scoreboard(username, users[username]["balance"])
            return

        # Player bust
        if player_score > 21:
            print("You went over 21. You lose ❌")

            # update stats in local users object
            stats = users[username].get("stats", {"wins": 0, "losses": 0, "games_played": 0})
            stats["games_played"] = stats.get("games_played", 0) + 1
            stats["losses"] = stats.get("losses", 0) + 1
            users[username]["stats"] = stats

            # persist
            save_users(users)
            save_pot(pot)
            update_scoreboard(username, users[username]["balance"])
            return

        choice_in = input("Type 'hit' to draw another card, 'stand' to pass: ").lower()
        if choice_in == "hit":
            player_hand.append(deal_card())
        else:
            game_over = True

    # ------------------ DEALER'S TURN ------------------ #
    while calculate_score(dealer_hand) < 17:
        dealer_hand.append(deal_card())

    player_score = calculate_score(player_hand)
    dealer_score = calculate_score(dealer_hand)

    print(f"\nYour final hand: {player_hand}, final score: {player_score}")
    print(f"Dealer's final hand: {dealer_hand}, final score: {dealer_score}")

    # Resolve outcome
    if dealer_score > 21 or player_score > dealer_score:
        print("You win 🎉")
        winnings = bet * 2
        users[username]["balance"] += winnings
        pot["pot"] -= winnings

        stats = users[username].get("stats", {"wins": 0, "losses": 0, "games_played": 0})
        stats["games_played"] = stats.get("games_played", 0) + 1
        stats["wins"] = stats.get("wins", 0) + 1
        users[username]["stats"] = stats

    elif player_score == dealer_score:
        print("It's a draw 🤝")
        users[username]["balance"] += bet
        # draw -> games_played increments, but not win/loss
        stats = users[username].get("stats", {"wins": 0, "losses": 0, "games_played": 0})
        stats["games_played"] = stats.get("games_played", 0) + 1
        users[username]["stats"] = stats

    else:
        print("Dealer wins ❌")
        stats = users[username].get("stats", {"wins": 0, "losses": 0, "games_played": 0})
        stats["games_played"] = stats.get("games_played", 0) + 1
        stats["losses"] = stats.get("losses", 0) + 1
        users[username]["stats"] = stats

    # persist everything once at the end
    save_users(users)
    save_pot(pot)
    update_scoreboard(username, users[username]["balance"])


# ------------------ MAIN ENTRY ------------------ #
if __name__ == "__main__":
    main()
