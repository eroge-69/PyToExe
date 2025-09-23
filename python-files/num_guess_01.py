import random

num = random.randint(1, 100)
valid = False
bingo = False
max = 100
min = 1

guess = int(input("Enter your guess (1 - 100): "))
while not(valid):
    if (guess > 0) and (guess < 101):
        valid = True
    else:
        guess = int(input("Enter your guess again (1 - 100): "))


while not(bingo):
    if (guess == num):
        bingo = True
        print ("BOOM! G a m e   O v e r!")
    elif (guess > num):
        max = guess
        guess = int(input(f"Enter your guess again ({min} - {max}): "))
    else:
        min = guess
        guess = int(input(f"Enter your guess again ({min} - {max}): "))
        