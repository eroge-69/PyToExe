import random

def play_game():
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 50...")
    print("Can you guess what it is?")
    print("-" * 40)
    
    # Generate random number
    secret_number = random.randint(1, 50)
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        try:
            # Get player's guess
            guess = int(input(f"\nAttempt {attempts + 1}/{max_attempts}: Enter your guess: "))
            attempts += 1
            
            # Check the guess
            if guess == secret_number:
                print(f"Congratulations! You guessed it in {attempts} attempts!")
                print(f"The number was {secret_number}")
                break
            elif guess < secret_number:
                print("Too low! Try a higher number.")
            else:
                print("Too high! Try a lower number.")
                
            # Give hints based on how close they are
            difference = abs(guess - secret_number)
            if difference <= 5:
                print("You're very close!")
            elif difference <= 15:
                print("You're getting warmer!")
            else:
                print("You're quite far off!")
                
        except ValueError:
            print("Please enter a valid number!")
            attempts -= 1  # Don't count invalid inputs as attempts
            
        # Check if out of attempts
        if attempts == max_attempts and guess != secret_number:
            print(f"\nGame Over! You've used all {max_attempts} attempts.")
            print(f"The number was {secret_number}")
            break

def main():
    while True:
        play_game()
        
        # Ask if player wants to play again
        play_again = input("\nWould you like to play again? (y/n): ").lower()
        if play_again != 'y' and play_again != 'yes':
            print("Thanks for playing!")
            break
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()