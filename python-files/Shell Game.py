#Shell Gameu
import random


def shellgame(c,count=0):
    shellgamen = random.randint(1, 3)

    if c ==shellgamen and shellgamen ==1:
        print(f'wow!\n'
              f'[0],[],[]')
        count += 1
        q = input("do you want to play again?: ")
        if q == "Y" or q == "y":
            c = int(input("please enter number between 1 -3: "))
            shellgame(c, count)
    elif c == shellgamen and shellgamen == 2:
        print(f'wow2!\n'
              f'[],[O],[]')
        count += 1
        q = input("do you want to play again?: ")
        if q == "Y" or q == "y":
            c = int(input("please enter number between 1 -3: "))
            shellgame(c,count)
    elif c == shellgamen and shellgamen == 3:
        print(f'wow3!\n'
              f'[],[],[O]')
        count +=1
        print(count)
        q=input("do you want to play again?: ")
        if q =="Y" or q == "y":
            c = int(input("please enter number between 1 -3: "))
            shellgame(c,count)

    elif c >= 4:
        print(f'the number is not good! you won {count} times ')
        a = input("you lose! you want to try again?: ")
        if a == "y" or a == "Y":
            c = int(input("please enter number between 1 -3: "))
            shellgame(c,count)
    else:
        a=input("you lose! you want to try again?: ")
        if a=="y" or a=="Y":
            c = int(input("please enter number between 1 -3: "))
            shellgame(c,count)
        else:
            print(f'bye bye ! you won {count} times!')

c = int(input("please enter number between 1 -3: "))
shellgame(c,0)
