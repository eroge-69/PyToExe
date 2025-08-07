import random
print("A random number is generated between 0 to 15")
random_number = random.randint(0,20)
for i in range(10):
    guess = int(input("Guess the number "))
    if guess == random_number:
        print("Correct!")
        break
    else:
        if (i<9):
            print("Guess again! ",9-i,"tries left")
