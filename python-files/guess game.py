import random

def number_guessing_game():
    print("🎮 Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 50.")

    # Computer picks a random number
    secret_number = random.randint(1, 50)
    attempts = 0

    while True:
        guess = input("Enter your guess (or 'q' to quit): ")

        if guess.lower() == 'q':
            print("Thanks for playing! The number was", secret_number)
            break

        # Convert guess to integer
        try:
            guess = int(guess)
        except ValueError:
            print("Please enter a valid number.")
            continue

        attempts += 1

        if guess < secret_number:
            print("Too low! Try again ⬆️")
        elif guess > secret_number:
            print("Too high! Try again ⬇️")
        else:
            print(f"🎉 Correct! The number was {secret_number}. You guessed it in {attempts} tries.")
            break

# Run the game
number_guessing_game()

