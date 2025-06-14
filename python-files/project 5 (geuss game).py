import random

print("WELCOME TO GUESS GAME")

secret_word = random_integer = random.randint(1, 10)

guess = ""
guess_count = 0
guess_limit = 3
out_of_guess = False

while guess != secret_word and not out_of_guess:
    if guess_count < guess_limit:
       guess = int(input("ENTER GUESS FROM 1 TO 10 : "))
       guess_count += 1
    else:
        out_of_guess = True

if out_of_guess:
    print("YOU LOSE ")
else:
    print("YOU WIN")

print("the secret number was " ,random_integer)


print(" THANKS FOR USING MY APP PLEASE RATE MY APP FROM 10 ")

input("       rating : ")

print("*******THANKS*******    ")
