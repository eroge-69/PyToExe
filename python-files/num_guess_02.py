import random

num = random.randint(1, 100)
valid = False
bingo = False
again = "Y"
max = 100
min = 1

guess = int(input("Enter your guess (1 - 100): "))

while ((again == "Y") or (again == "y")):
    while not(valid):
        if (guess > 0) and (guess < 101):
            valid = True
        else:
            guess = int(input("Enter your guess again (1 - 100): "))


    while not(bingo):
        if (guess == num):
            bingo = True
            print ("BOOM! G a m e   O v e r!")
            again = input ("Play again? (Y/N): ")
            if ((again == "Y") or (again == "y")):
                guess = int(input("Enter your guess (1 - 100): "))
                valid = False
                bingo = False
                max = 100
                min = 1

        elif (guess > num):
            if (guess < max):
                max = guess
            guess = int(input(f"Enter your guess again ({min} - {max}): "))
        else:
            if (guess > min):
                min = guess
            guess = int(input(f"Enter your guess again ({min} - {max}): "))
