import random
plys = 0
cpus = 0
def menu():
    mode = input('\033[0m'+"choose mode(easy/standard/hard)/else to quit: ")
    if mode == "easy":
        easy()
    elif mode == "standard":
        standard()
    elif mode == "hard":
        hard()
def easy():
    print('\033[92m' + "easy mode")
    global plys, cpus
    while True:
        Popt = ["rock","paper","scissors","menu"]
        opt = ["rock","paper","scissors"]
        cpu = ""
        ply = None
        print("-"*25)
        ply = input("choose your option: ").strip().lower()
        while ply not in Popt:
            ply = input("choose your option: ").strip().lower()
        if ply == "rock":
            cpu = random.choices(opt,weights=[5,5,90])[0]
        elif ply == "paper":
            cpu = random.choices(opt,weights=[90,5,5])[0]
        elif ply == "scissors":
           cpu = random.choices(opt,weights=[5,90,5])[0]
        elif ply == "menu":
            plys = 0
            cpus = 0
            return menu()
        print(f"you: {ply}\ncpu:{cpu}")
        if ply == cpu:
            print ("tie")
        elif (ply == "rock" and cpu == "scissors") or \
               (ply == "paper" and cpu == "rock") or \
               (ply == "scissors" and cpu == "paper"):
                   print("you win")
                   plys += 1
        else:
             print("you lose")
             cpus += 1
        print(f"your score: {plys}\ncpu score:{cpus}")
        print("-"*25)
        
sdps = 0
sdcps = 0
        
def standard():
    print('\033[93m' + "standard mode")
    global sdps, sdcps
    while True:
        Popt = ["rock","paper","scissors","menu"]
        opt = ["rock","paper","scissors"]
        cpu = ""
        ply = None
        print("-"*25)
        ply = input("choose your option: ").strip().lower()
        while ply not in Popt:
            ply = input("choose your option: ").strip().lower()
        if ply == "rock":
            cpu = random.choices(opt)[0]
        elif ply == "paper":
            cpu = random.choices(opt)[0]
        elif ply == "scissors":
           cpu = random.choices(opt)[0]
        elif ply == "menu":
            sdps = 0
            sdcps = 0
            return menu()
        print(f"you: {ply}\ncpu:{cpu}")
        if ply == cpu:
            print ("tie")
        elif (ply == "rock" and cpu == "scissors") or \
               (ply == "paper" and cpu == "rock") or \
               (ply == "scissors" and cpu == "paper"):
                   print("you win")
                   sdps += 1
        else:
             print("you lose")
             sdcps += 1
        print(f"your score: {sdps}\ncpu score:{sdcps}")
        print("-"*25)


hdps = 0
hdcps = 0


def hard():
    print('\033[91m' + "hard mode")
    global hdps, hdcps
    while True:
        Popt = ["rock","paper","scissors","menu"]
        opt = ["rock","paper","scissors"]
        cpu = ""
        ply = None
        print("-"*25)
        ply = input("choose your option: ").strip().lower()
        while ply not in Popt:
            ply = input("choose your option: ").strip().lower()
        if ply == "rock":
            cpu = random.choices(opt,weights=[10,80,10])[0]
        elif ply == "paper":
            cpu = random.choices(opt,weights=[10,10,80])[0]
        elif ply == "scissors":
           cpu = random.choices(opt,weights=[80,10,10])[0]
        elif ply == "menu":
            hdps = 0
            hdcps = 0
            return menu()
        print(f"you: {ply}\ncpu:{cpu}")
        if ply == cpu:
            print ("tie")
        elif (ply == "rock" and cpu == "scissors") or \
               (ply == "paper" and cpu == "rock") or \
               (ply == "scissors" and cpu == "paper"):
                   print("you win")
                   hdps += 1
        else:
             print("you lose")
             hdcps += 1
        print(f"your score: {hdps}\ncpu score:{hdcps}")
        print("-"*25)
menu()