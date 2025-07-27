import time
import sys
import json
import os
import random

# Game state management
class GameState:
    def __init__(self):
        self.current_chapter = "start"
        self.inventory = []
        self.stats = {
            "Courage": 5,
            "Wisdom": 5,
            "Power": 5
        }
        self.visited_chapters = set()
        self.decisions = []

    def save_game(self, filename="savegame.json"):
        data = {
            "current_chapter": self.current_chapter,
            "inventory": self.inventory,
            "stats": self.stats,
            "visited_chapters": list(self.visited_chapters),
            "decisions": self.decisions
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True

    def load_game(self, filename="savegame.json"):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.current_chapter = data["current_chapter"]
            self.inventory = data["inventory"]
            self.stats = data["stats"]
            self.visited_chapters = set(data["visited_chapters"])
            self.decisions = data["decisions"]
            return True
        except:
            return False

# Utility Functions
def typewriter(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def make_choice(options, state, simulated_input=None):
    typewriter("\nWhat will you do?")
    for i, option in enumerate(options, 1):
        typewriter(f"{i}. {option}")

    simulated_inputs = simulated_input or ["1"]
    index = 0

    while index < len(simulated_inputs):
        choice = simulated_inputs[index].strip().lower()
        index += 1
        if choice in [str(i) for i in range(1, len(options)+1)]:
            state.decisions.append((state.current_chapter, int(choice)))
            return int(choice)
        elif choice == 'save':
            if state.save_game():
                typewriter("Game saved successfully!")
            else:
                typewriter("Save failed!")
        elif choice == 'load':
            if state.load_game():
                typewriter("Game loaded successfully!")
                return "load"
            else:
                typewriter("Load failed!")
        elif choice == 'inv':
            show_inventory(state)
        elif choice == 'stats':
            show_stats(state)
        elif choice.startswith('inspect '):
            describe_item(choice[8:].strip(), state)
        else:
            typewriter("Invalid choice! Please enter a number or command (save, load, inv, stats, inspect <item>)")

    return 1

def show_inventory(state):
    if not state.inventory:
        typewriter("\nYour inventory is empty.")
    else:
        typewriter("\nINVENTORY:")
        for item in state.inventory:
            typewriter(f"- {item}")

def show_stats(state):
    typewriter("\nCHARACTER STATS:")
    for stat, value in state.stats.items():
        typewriter(f"{stat}: {value}/10")

def describe_item(item, state):
    descriptions = {
        "Runic Knowledge": "A fragment of ancient language that whispers secrets of the temple.",
        "Torch": "A simple torch, but essential for seeing in the dark.",
        "Tattoo Insight": "Your tattoos let you see magical auras and hidden forces.",
        "Cracked Orb": "A damaged orb filled with chaotic energy.",
        "Star Compass": "Always points toward the location of the Starforged Blade.",
        "Ghostly Ally": "The spirit of Alaric, a spectral knight who guides you.",
        "Star Map": "A magical map showing celestial alignments and artifact paths."
    }
    if item in state.inventory:
        typewriter(f"\n{item}: {descriptions.get(item, 'No further information available.')}")
    else:
        typewriter("\nYou don't have that item.")

def stat_check(stat, difficulty, state):
    value = state.stats[stat]
    roll = random.randint(1, 6)
    total = value + roll
    typewriter(f"\n{stat} check: {value} + {roll} = {total} (Need ≥ {difficulty})")
    if total >= difficulty:
        typewriter("Success!")
        return True
    else:
        typewriter("Failure! Try improving your stats through your choices.")
        return False

def modify_stat(stat, amount, state):
    state.stats[stat] = max(1, min(10, state.stats[stat] + amount))
    change = "increased" if amount > 0 else "decreased"
    typewriter(f"\n{stat} {change} to {state.stats[stat]}!")

# Basic menu system
def main_menu(simulated_input=None):
    typewriter("\n" + "="*50)
    typewriter("SHADOWS OF THE SHATTERED KING")
    typewriter("="*50)
    typewriter("1. New Game")
    typewriter("2. Load Game")
    typewriter("3. Quit")

    simulated_inputs = simulated_input or ["1"]
    index = 0

    while index < len(simulated_inputs):
        choice = simulated_inputs[index].strip()
        index += 1
        if choice == '1':
            return GameState()
        elif choice == '2':
            state = GameState()
            if state.load_game():
                typewriter("Game loaded successfully!")
                return state
            else:
                typewriter("Load failed. Starting new game.")
                return GameState()
        elif choice == '3':
            typewriter("\nThank you for playing!")
            sys.exit()
        else:
            typewriter("Invalid choice. Please enter 1, 2, or 3.")

    return GameState()

def chapter_1(state):
    typewriter("\nYou awaken in a ruined chamber beneath a shattered sky. The wind howls through the broken stones.")
    typewriter("The ground trembles slightly as if the world itself grieves.")

    choice = make_choice([
        "Pick up a nearby torch.",
        "Inspect the strange glowing symbols on the wall.",
        "Call out to see if anyone else is here."
    ], state)

    if choice == 1:
        typewriter("You now hold a torch, its flame flickering in the dim light.")
        state.inventory.append("Torch")
        modify_stat("Courage", 1, state)
    elif choice == 2:
        typewriter("The symbols glow brighter as you study them. A memory stirs in your mind — ancient knowledge.")
        state.inventory.append("Runic Knowledge")
        modify_stat("Wisdom", 1, state)
    elif choice == 3:
        typewriter("A faint whisper responds. A ghostly figure materializes — a knight with sorrow in his eyes.")
        state.inventory.append("Ghostly Ally")
        modify_stat("Power", 1, state)

    state.current_chapter = "chapter_2"
    typewriter("\n[End of Chapter 1]")

def start_game():
    simulated_menu = ["1"]  # Replace or expand for other scenarios
    state = main_menu(simulated_menu)
    chapter_1(state)

if __name__ == "__main__":
    start_game()
