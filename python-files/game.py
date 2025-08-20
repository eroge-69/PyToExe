import random
import os
import platform
import time

def clear_screen():
    # Clear console screen for Windows, Mac, Linux
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def get_feedback(guess, secret):
    diff = abs(guess - secret)
    if diff == 0:
        return "🎯 Correct!"
    elif diff <= 3:
        return "🔥 Very close!"
    elif diff <= 10:
        return "😊 Close."
    else:
        return "❄️ Far off."

def number_guessing_game(high_score=None):
    clear_screen()
    print("\n🎮 Number Guessing Game")
    print("👨‍💻 Created by Khubaib Ahmad (11th-PCM)")
    print("I'm thinking of a number between 1 and 100.")
    print("Try to guess it in as few attempts as possible!\n")

    secret_number = random.randint(1, 100)
    max_attempts = 10
    attempts = 0
    previous_guesses = []

    while attempts < max_attempts:
        guess_input = input(f"[Attempt {attempts + 1}/{max_attempts}] Enter your guess (or type 'give up' to reveal): ").strip().lower()

        if guess_input == 'give up':
            print(f"😔 The number was: {secret_number}")
            break

        if not guess_input.isdigit():
            print("🚫 Please enter a valid number between 1 and 100.\n")
            continue

        guess = int(guess_input)

        if guess < 1 or guess > 100:
            print("📏 Your guess must be between 1 and 100.\n")
            continue

        attempts += 1
        previous_guesses.append(guess)

        feedback = get_feedback(guess, secret_number)
        print(f"{feedback}\n")

        if guess == secret_number:
            print(f"🎉 Well done! You guessed it in {attempts} attempts.")
            if high_score is None or attempts < high_score:
                high_score = attempts
                print("🏆 New high score!")
            break
    else:
        print(f"💀 You've used all attempts. The number was {secret_number}.")

    print(f"\n📜 Your guesses: {previous_guesses}")
    print(f"🥇 Best score this session: {high_score if high_score else 'N/A'}")
    print("👨‍💻 Game developed by Khubaib Ahmad (11th-PCM)")

    play_again = input("\n🔁 Play again? (y/n): ").lower()
    if play_again == 'y':
        number_guessing_game(high_score)
    else:
        print("\n👋 Thanks for playing!")
        print("Exiting in 5 seconds...")
        time.sleep(5)  # Give user time to read final message

if __name__ == "__main__":
    number_guessing_game()
