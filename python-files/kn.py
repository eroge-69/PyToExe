import random
import os

print("Welcome to KODINERDS - The Classic Text Adventure!")
print("You are a KODINERD trying to collect data and avoid bugs in the digital world.")
print("Navigate through levels by choosing your actions wisely.")
print("Type 'help' to see commands.")

player_data = 0
player_lives = 3
level = 1
clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    print("Commands:")
    print("  run - move forward")
    print("  jump - jump over a bug")
    print("  status - show your current data and lives")
    print("  help - show this help message")
    print("  quit - exit the game")

def encounter(level):
    bug_chance = min(30 + level * 5, 80)
    data_chance = 50
    event = random.randint(1, 100)
    if event <= bug_chance:
        return 'bug'
    elif event <= bug_chance + data_chance:
        return 'data'
    else:
        return 'nothing'

while player_lives > 0:
    print(f"\nLevel {level} - What do you want to do? (run/jump/status/help/quit)")
    action = input("> ").strip().lower()

    if action == 'help':
        show_help()
    elif action == 'status':
        print(f"Data collected: {player_data}")
        print(f"Lives remaining: {player_lives}")
    elif action == 'quit':
        print("Thanks for playing KODINERDS!")
        break
    elif action == 'run':
        event = encounter(level)
        if event == 'bug':
            print("Oh no! You ran into a bug and lost a life!")
            player_lives -= 1
        elif event == 'data':
            print("Great! You found some data points!")
            player_data += 10
        else:
            print("You moved forward safely.")
    elif action == 'jump':
        event = encounter(level)
        if event == 'bug':
            print("You jumped over a bug safely!")
        elif event == 'data':
            print("You jumped and collected some data points!")
            player_data += 10
        else:
            print("You jumped but found nothing.")
    else:
        print("Invalid command. Type 'help' for a list of commands.")

    if player_data >= level * 50:
        level += 1
        print(f"\nCongratulations! You advanced to level {level}!")

if player_lives == 0:
    print("Game Over! You ran out of lives.")
    print(f"You collected a total of {player_data} data points.")
