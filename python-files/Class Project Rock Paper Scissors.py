#Class Project
import random
print("We gonna play  -   O ,  [] ,  8<   - Rock , Paper , Scissors  :) ")
compchoice = ["Paper","Rock","Scissors"]
count =0
countl =0
countt =0
name = input("Plese enter your name: ")
name =name.capitalize()
def playgame():
    global count
    global countl
    global countt
    comp = random.choice(compchoice)
    #print(comp)
    user =input(f'Hello {name} This is the options: \n'
          "1.Paper []\n" 
          "2.Rock O\n"
          "3.Scissors 8<\n"
          "4.Watch score: \n")
    if user == "1" and comp == "Rock":
        print(f'The computer choose:{comp}')
        print("Wow you Won! Go Paper []")
        count+=1
        playagain()
    elif user == "1" and comp == "Paper":
        print(f'The computer choose: {comp}')
        print("This is Tie")
        countt+=1
        playagain()
    elif user == "1" and comp == "Scissors":
        print(f'The computer choose: {comp}')
        print("You lose!")
        countl +=1
        playagain()
    if user == "2" and comp == "Rock":
        print(f'The computer choose: {comp}')
        print("This is Tie")
        countt+=1
        playagain()
    elif user == "2" and comp == "Paper":
        print(f'The computer choose: {comp}')
        print("You lose!")
        countl += 1
        playagain()
    elif user == "2" and comp == "Scissors":
        print(f'The computer choose: {comp}')
        print("Wow you Won! You Rock O ! ")
        count += 1
        playagain()
    if user == "3" and comp == "Rock":
        print(f'The computer choose: {comp}')
        print("You lose!")
        countl += 1
        playagain()
    elif user == "3" and comp == "Paper":
        print(f'The computer choose: {comp}')
        print("Wow you Won! You Awsome 8< ! ")
        count += 1
        playagain()
    elif user == "3" and comp == "Scissors":
        print(f'The computer choose: {comp}')
        print("This is Tie")
        countt += 1
        playagain()
    if user == "4":
        print(f'{name} This is your Score Table: Wins: {count} , Tie: {countt} , Loses: {countl} ')
        reset =input("Play Y\\N To reset table score:")
        if reset == "y" or reset == "Y":
            countt,count,countl = 0,0,0
            playagain()
        else:
            playagain()
    elif not user == "1" or user == "2" or user == "3" or user == "4":
        print(f'Wrong choice! you press {user}')
        playagain()

def playagain():
    a=input("Would you like to play again? Y\\N: ")
    if a== "y" or a == "Y":
        playgame()
    elif a =="n" or a =="N":
        exit("Bye Bye")
    else:
        print("wrong choice")
        playagain()
playgame()
