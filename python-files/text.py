# Hangman Console Game in Python

import random
import os

class HangmanGame:
    """Manages the state and logic for the Hangman game."""
    def __init__(self):
        # Large word list
        self.words = [
            "SWIFT", "MOBILE", "PROGRAM", "CODING", "APPLE", "SCHOOL", "FRIEND", "BOOK", "PIZZA", 
            "OCEAN", "MUSIC", "GUITAR", "PIANO", "DREAM", "CLOUDS", "GARDEN", "LUNCH", "DINNER", 
            "TRAVEL", "ADVENTURE", "FISHING", "CAMPING", "SUNSET", "BICYCLE", "SKATE", "FOOTBALL", 
            "BASKET", "VOLLEY", "TENNIS", "COMPUTER", "LAPTOP", "HEADPHONE", "KEYBOARD", "MOUSE", 
            "WEBSITE", "INTERNET", "SCIENCE", "HISTORY", "ARTIST", "POETRY", "ACTOR", "STAGE", 
            "MOVIE", "THEATER", "BEACH", "FOREST", "MOUNTAIN", "RIVER", "LAKE", "ANIMAL", "TIGER", 
            "LION", "EAGLE", "DOLPHIN", "WHALE", "ZEBRA", "CHESS", "CHECKERS", "PUZZLE", "RIDDLE", 
            "SECRET", "SURPRISE", "CAREFUL", "FRIENDLY", "HAPPY", "GRATEFUL", "KINDNESS", "HONEST", 
            "FUTURE", "EXPLORE", "DISCOVER", "CREATE", "BUILDER", "ENGINEER", "DESIGN", "SPORTS", 
            "OLYMPICS", "MEDAL", "CHAMPION", "TRAINER", "HEALTH", "FITNESS", "EXERCISE", "WATER", 
            "JUICE", "MILK", "SNACK", "VEGGIE", "FRUIT", "TOMATO", "CARROT", "GRAPE", "BANANA", 
            "LIBRARY", "READER", "WRITER", "JOURNAL", "PENCIL", "ERASER", "BACKPACK", "CLASSROOM", 
            "STUDENT", "TEACHER", "PROJECT", "GOAL", "SUCCESS", "LEARN", "KNOWLEDGE", "SMART", 
            "UNIVERSE", "PLANET", "STARGAZE", "COMFORT", "VACATION", "SNOWFLAKE", "HARVEST"
        ]
        self.initial_lives = 7
        self.secret_word = ""
        self.guessed_letters = set()
        self.lives_left = self.initial_lives
        self.game_state = 'playing'  # 'playing', 'won', 'lost'
        self.score = 0

    def reset_game(self):
        """Selects a new word and resets game state variables."""
        # Use random.choice() to safely pick a word
        if self.words:
            self.secret_word = random.choice(self.words)
        else:
            self.secret_word = "PYTHON" # Fallback
            
        self.guessed_letters = set()
        self.lives_left = self.initial_lives
        self.game_state = 'playing'

    def display_word_progress(self):
        """Returns the word with unguessed letters replaced by underscores."""
        # This is a concise Python list comprehension
        display = [letter if letter in self.guessed_letters else '_' for letter in self.secret_word]
        return ' '.join(display)

    def process_guess(self, guess):
        """Processes a single letter guess."""
        if self.game_state != 'playing':
            return

        uppercase_guess = guess.upper()

        if not uppercase_guess.isalpha() or len(uppercase_guess) != 1:
            return "Invalid input. Please enter a single letter."

        if uppercase_guess in self.guessed_letters:
            return f"You already guessed '{uppercase_guess}'. Try again."
        
        self.guessed_letters.add(uppercase_guess)
        
        if uppercase_guess in self.secret_word:
            result = f"Correct! '{uppercase_guess}' is in the word."
        else:
            self.lives_left -= 1
            result = f"Wrong! '{uppercase_guess}' is NOT in the word."

        self.check_game_state()
        return result

    def process_word_guess(self, word):
        """Processes a whole word guess."""
        if self.game_state != 'playing':
            return

        uppercase_word = word.upper()

        if uppercase_word == self.secret_word:
            # Winning condition
            self.guessed_letters.update(set(self.secret_word))
            self.game_state = 'won'
            self.score += 1
            return "🎉 CORRECT! You guessed the whole word! 🎉"
        else:
            # Losing condition for the guess
            self.lives_left -= 1
            self.check_game_state()
            return f"❌ Wrong word! '{word}' is not the secret word. Lost a life."

    def check_game_state(self):
        """Checks if the win or lose condition has been met."""
        if self.lives_left <= 0:
            self.game_state = 'lost'
            return

        # Check for win condition: True if all letters in the word have been guessed
        if all(letter in self.guessed_letters for letter in self.secret_word):
            self.game_state = 'won'
            self.score += 1

# --- Console Interface ---

def clear_screen():
    """Clears the console for a clean display."""
    # Use 'cls' for Windows, 'clear' for Unix/Linux/Mac
    os.system('cls' if os.name == 'nt' else 'clear')

def display_game_status(game):
    """Prints the current game state to the console."""
    clear_screen()
    print("========================================")
    print("      🐍 Python Hangman Master 🐍      ")
    print("========================================")
    print(f"Current Score: {game.score}")
    print(f"Lives Remaining: {game.lives_left} / {game.initial_lives}")
    print("-" * 40)
    print(f"Word: {game.display_word_progress()}")
    print("-" * 40)
    print(f"Guessed Letters: {', '.join(sorted(game.guessed_letters)) if game.guessed_letters else 'None'}")
    print("========================================")

def run_hangman_game():
    """Main game loop for the console application."""
    game = HangmanGame()
    
    print("Welcome to Python Hangman!")
    input("Press Enter to start your first game...")
    
    while True:
        game.reset_game()
        last_message = ""

        while game.game_state == 'playing':
            display_game_status(game)
            if last_message:
                print(f"\n[INFO]: {last_message}\n")
            
            # --- Get User Input ---
            user_input = input("Enter a single letter OR the whole word (or 'QUIT'): ").strip()
            
            if not user_input:
                last_message = "Please enter a guess."
                continue

            if user_input.upper() == 'QUIT':
                game.game_state = 'quit'
                break

            if len(user_input) == 1:
                # Process single letter guess
                last_message = game.process_guess(user_input)
            elif len(user_input) > 1:
                # Process whole word guess
                last_message = game.process_word_guess(user_input)
            else:
                last_message = "Invalid input. Please try again."

        # --- End of Round ---
        
        # Display final state
        display_game_status(game)
        print("-" * 40)
        
        if game.game_state == 'won':
            print(f"🎉 CONGRATULATIONS! You guessed the word: {game.secret_word} 🎉")
        elif game.game_state == 'lost':
            print(f"❌ GAME OVER! The word was: {game.secret_word} ❌")
        elif game.game_state == 'quit':
            print("Thanks for playing!")
            break

        # Ask to play again
        print(f"\nYour final score was: {game.score}")
        play_again = input("Play another round? (y/n): ").strip().lower()
        if play_again != 'y':
            print("Goodbye! Come back soon.")
            break

if __name__ == "__main__":
    run_hangman_game()

