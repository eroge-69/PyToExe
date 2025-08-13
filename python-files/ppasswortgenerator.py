import random 
import string

print("Your Password is> ")

letters = string.printable
password=""
for x in range(10):
    password+=random.choice(letters)
print(password)