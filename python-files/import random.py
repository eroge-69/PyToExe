import random

def guess_the_number():
    number = random.randint(1, 100)
    attempts = 0

    while True:
        guess = int(input("Take a guess: "))
        attempts += 1

        if guess < number:
            print("Мало!")
        elif guess > number:
            print("чел ты куда много!")
        else:
            print("Congratulations! You guessed the number in", attempts, "attempts.")
            break

guess_the_number()