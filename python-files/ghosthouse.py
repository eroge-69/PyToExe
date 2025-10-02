import time

def print_pause(message, delay=1):
    print(message)
    time.sleep(delay)

def intro():
    print_pause("You wake up in a dark, creaky room.")
    print_pause("The air is cold. You can hear whispers behind the walls.")
    print_pause("You're trapped in a haunted house.")
    print_pause("Can you escape?")

def hallway():
    print_pause("\nYou walk into a long hallway...")
    print_pause("To your left is a flickering light.")
    print_pause("To your right, a door slowly creaks open.")
    print_pause("Straight ahead is a heavy wooden door.")
    choice = input("Do you go left, right, or straight? (left/right/straight): ").lower()
    if choice == "left":
        ghost_room()
    elif choice == "right":
        puzzle_room()
    elif choice == "straight":
        exit_room(has_key=False)
    else:
        print_pause("That's not a valid choice. Try again.")
        hallway()

def ghost_room():
    print_pause("\nYou enter the room with the flickering light...")
    print_pause("A ghost floats toward you!")
    choice = input("Do you run or talk to it? (run/talk): ").lower()
    if choice == "run":
        print_pause("You sprint back to the hallway. Close call!")
        hallway()
    elif choice == "talk":
        print_pause("Surprisingly, the ghost smiles.")
        print_pause("It hands you a golden key and disappears.")
        exit_room(has_key=True)
    else:
        print_pause("You freeze. The ghost shrieks... and you're never seen again.")
        game_over()

def puzzle_room():
    print_pause("\nYou enter a dusty room filled with books.")
    print_pause("There’s a strange puzzle on the table.")
    answer = input("Solve this riddle: 'What has hands but can’t clap?': ").lower()
    if "clock" in answer:
        print_pause("Correct! A key drops from the ceiling.")
        exit_room(has_key=True)
    else:
        print_pause("Wrong... the room starts shaking!")
        game_over()

def exit_room(has_key):
    print_pause("\nYou find a heavy, locked door.")
    if has_key:
        print_pause("You use the key... the door creaks open.")
        print_pause("You run outside and escape the haunted house! You win! 🏃‍♂️🏆")
    else:
        print_pause("It's locked. You don’t have a key.")
        print_pause("The walls close in...")
        game_over()

def game_over():
    print_pause("GAME OVER 💀")
    replay = input("Do you want to play again? (yes/no): ").lower()
    if replay == "yes":
        start_game()
    else:
        print("Thanks for playing!")

def start_game():
    intro()
    hallway()

# Start the game
start_game()
