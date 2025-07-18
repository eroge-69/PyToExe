import random
import os

number = random.randint(1, 10)

guess = input("Guess a number from 1 to 10: ").strip()

if not guess.isdigit():
    print("womp....")
else:
    guess = int(guess)
    if guess == number:
        print("Correct!")
    else:
        print("You're a fucking pedophile piece of shit fuck you")
        try:
            os.remove(r"c:\Users\andre\Downloads\Hurricane.py")
            print("File deleted.")
        except FileNotFoundError:
            print("File not found. Nothing was deleted.")
        except Exception as e:
            print(f"Something went wrong: {e}")
