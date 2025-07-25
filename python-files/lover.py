# Your Digital Lover
#Created by Say Gex & Co.

from random import randint
from time import sleep
foreverloop = 1

print("Welcome to Your Digital Lover! Come on in to your new partner and spend some quality time with them!")
sleep(1)
print("Loading...")
sleep(2.4)
print("Loading finished! Get ready to meet your new lover!!!")
print("-----------------------------------------------------------------------------------------------------------------------------------------")
print("Sup")
while foreverloop == 1:
    reply = input("Reply: ")
    if "sex" in reply:
        print("Sex is so awesome I wanna do it")
    elif "love you" in reply:
        msgchance = randint(1,2)
        if msgchance == 1:
            print("I love you too bae")
        else:
            print("Go fuck yourself 'cause I don't love you back")
    elif "grocer" in reply:
        print("Hell nah I ain't gettin' the groceries")
    elif "do you work" in reply:
        print("I work like a pigeon")
    elif "secret" in reply:
        print("My secret is that my eyeballs are missing")
    elif "fuck you" in reply:
        print("Fuck you too")
    else:
        msgchance = randint(1,6)
        if msgchance == 1:
            print("Yes")
        elif msgchance == 2:
            print("Yes")
        elif msgchance == 3:
            print("No")
        elif msgchance == 4:
            print("No")
        elif msgchance == 5:
            print("Huhhhh")
        elif msgchance == 6:
            print("Chicken")