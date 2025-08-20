import random

def number_guessing_game():
    print("🎮 Number Guessing Game")
    print("👨‍💻 Created by Khubaib Ahmad (11th-PCM)\n")
    print("I'm thinking of a number between 1 and 100.")
    print("You have 10 attempts to guess it.\n")

    secret_number = random.randint(1, 100)
    max_attempts = 10
    attempts = 0
    previous_guesses = []

    while attempts < max_attempts:
        guess_input = input(f"Attempt {attempts + 1}/{max_attempts} - Enter your guess: ")

        if not guess_input.isdigit():
            print("🚫 Invalid input. Please enter a number between 1 and 100.\n")
            continue

        guess = int(guess_input)

        if guess < 1 or guess > 100:
            print("📏 Out of limit! Your guess must be between 1 and 100.\n")
            continue

        attempts += 1
        previous_guesses.append(guess)

        if guess < secret_number:
            print("📉 your guess is low!\n")
        elif guess > secret_number:
            print("📈 your guess is high!\n")
        else:
            print(f"🎉 Correct! You guessed it in {attempts} attempts.")
            break
    else:
        print(f"💀 You've used all your attempts. The correct number was {secret_number}.")

    print("\n📜 Your guesses:", previous_guesses)

    print("\n👨‍💻 Game developed by Khubaib Ahmad (11th-PCM)")

    play_again = input("\n🔁 Play again? (yes/no): ").lower()
    if play_again == 'yes':
        print("\n🔄 Restarting game...\n")
        number_guessing_game()
    else:
        print("👋 Thanks for playing!")

if __name__ == "__main__":
    number_guessing_game()
