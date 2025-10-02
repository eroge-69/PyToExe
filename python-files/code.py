import random
import time
import os

def clear():
    # Check the operating system
    if os.name == 'nt':  # For Windows
        _ = os.system('cls')
    else:  # For macOS and Linux
        _ = os.system('clear')
clear()
letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", " ", "!", "@", "#", "$", "%", "^", "&", "*", "?", "/"]
output = ""
while output != "Hello World!":
    temp = ""
    temp = random.choice(letters)
    tempo = output + temp
    print(tempo + "\n")
    if tempo == "H" or tempo == "He" or tempo == "Hel" or tempo == "Hell" or tempo == "Hello" or tempo == "Hello " or tempo == "Hello W" or tempo == "Hello Wo" or tempo == "Hello Wor" or tempo == "Hello Worl" or tempo == "Hello World" or tempo == "Hello World!":
        output += temp
    if output == "HH":
        output = "H"
    clear()
    time.sleep(0.01)
time.sleep(5)
ip = input("Enter a number:")
for i in range(4):
    print("Loading dependencies." + i * ".")
    time.sleep(0.5)
    clear()
# print("Loading dependencies..")
# time.sleep(0.5)
# print("Loading dependencies...")
# time.sleep(0.5)
# print("Loading dependencies....")
# time.sleep(0.5)
# print("Loading dependencies.....")
# time.sleep(0.5)
# print("Calculating Possibilities.")
# time.sleep(0.5)
# print("Calculating Possibilities..")
# time.sleep(0.5)
# print("Calculating Possibilities...")
# time.sleep(0.5)
# print("Calculating Possibilities....")
# time.sleep(0.5)
# print("Calculating Possibilities.....")
for j in range(4):
    print("Analysing." + i * ".")
    time.sleep(0.5)
    clear()
# print("Analysing..")
# time.sleep(0.5)
# print("Analysing...")
# time.sleep(0.5)
# print("Analysing....")
# time.sleep(0.5)
# print("Analysing.....")
# time.sleep(0.5)
for x in range(4):
    print("Calculating Possibilities." + i * ".")
    time.sleep(0.5)
    clear()
print("You are thinking:", ip)