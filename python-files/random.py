import random
def guess_the_number():
    number = random.randint(1, 100)
    attempts = 0
    while True:
        guess = int(input("угадывай, 1 до 100"))
        attempts += 1
        if guess < number:
            print("как то мало")
        elif guess > number:
            print("многа слишком")
        else:
            print(f"крутой че, угадал за {attempts} попыток.")