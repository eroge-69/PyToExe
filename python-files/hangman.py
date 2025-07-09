import random
import os


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def hangman_ascii(incorrect_guesses):
    stages = [
        """
           --------
           |      |
           |      
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |      |
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / 
           -
        """,
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / \\
           -
        """
    ]
    return stages[incorrect_guesses]


def get_random_word():
    words = ["python", "hangman", "programming", "computer", "keyboard",
             "developer", "algorithm", "function", "variable", "dictionary"]
    return random.choice(words)


def play_hangman():
    word = get_random_word().lower()
    guessed_letters = []
    correct_letters = []
    incorrect_guesses = 0
    max_attempts = 6
    game_over = False

    while not game_over:
        clear_screen()
        print(hangman_ascii(incorrect_guesses))

        # Display word with blanks for unguessed letters
        display_word = ""
        for letter in word:
            if letter in correct_letters:
                display_word += letter + " "
            else:
                display_word += "_ "
        print(display_word + "\n")

        # Show incorrect guesses
        print("Incorrect guesses:", " ".join([l for l in guessed_letters if l not in word]))
        print(f"Attempts left: {max_attempts - incorrect_guesses}")

        # Check win condition
        if all(letter in correct_letters for letter in word):
            print("\nCongratulations! You won!")
            print(f"The word was: {word}")
            game_over = True
            continue

        # Check lose condition
        if incorrect_guesses >= max_attempts:
            print("\nGame over! You lost!")
            print(f"The word was: {word}")
            game_over = True
            continue

        # Get user input
        guess = input("Guess a letter: ").lower()

        # Validate input
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        if guess in guessed_letters:
            print("You already guessed that letter.")
            continue

        guessed_letters.append(guess)

        # Check if guess is correct
        if guess in word:
            correct_letters.append(guess)
            print("Correct!")
        else:
            incorrect_guesses += 1
            print("Incorrect!")

        # Small delay for better UX
        import time
        time.sleep(0.5)


def main():
    print("Welcome to Hangman!")
    while True:
        play_hangman()
        play_again = input("\nWould you like to play again? (y/n): ").lower()
        if play_again != 'y':
            print("Thanks for playing! Goodbye!")
            break


if __name__ == "__main__":
    main()