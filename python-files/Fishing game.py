#hello gays

import os
import time
import math

while True:
    playername = input("What will be your username?: ")
    if playername in ["", " ", "  ", "   ", "    ", "     "]:
        print("This name is empty.")
    else:
        break

FGCoins = 0
bootpts = 1
bootptsprice = 5
fishpts = 0
fishptsprice = 25
big_fishpts = 0
bigfishptsprice = 50
tunapts = 0
tunaptsprice = 100
salmonpts = 0
salmonptsprice = 250
caviar_fishpts = 0
caviarfishptsprice = 500
sharkpts = 0
sharkptsprice = 1000
fishtimes = 0
boat_points = bootpts + fishpts + big_fishpts + tunapts + salmonpts + caviar_fishpts + sharkpts
fishing_duration = 2
fishing_duration_price = 10
boots = 0
boots_sp = 1
fish = 0
fish_sp = 3
big_fish = 0
big_fish_sp = 7
tuna = 0
tuna_sp = 15
salmon = 0
salmon_sp = 30
caviar_fish = 0
caviar_fish_sp = 50
shark = 0
shark_sp = 100


def greet():
    os.system('cls')
    boat_points = bootpts + fishpts + big_fishpts + tunapts + salmonpts + caviar_fishpts + sharkpts
    print(f"Hello {playername}!")
    print(f"You have {FGCoins} FG¢ and boat points {boat_points}")
    print(f"You have fished {fishtimes} Times.")
    print("""What do you want to do?
1) Go fishing
2) View inventory
3) Sell & buy stuff
4) Exit""")
    while True:
        optionchoose1 = input("What option do you want to choose? (note: type 1, 2, 3, or 4): ")
        if optionchoose1 in ["1", "2", "3", "4"]:
            break
        else:
            print("This is not a valid option!")
    if optionchoose1 == "1":
        gofishing()
    elif optionchoose1 == "2":
        viewinventory()
    elif optionchoose1 == "3":
        sell()
    elif optionchoose1 == "4":
        quit()

def gofishing():
    print("Going fishing")
    for i in range(3):
        print(i + 1)
        time.sleep(0.5)
    os.system('cls')
    tempboots = 0
    tempfish = 0
    tempbigfish = 0
    temptuna = 0
    tempsalmon = 0
    tempcaviar = 0
    tempshark = 0
    for i in range(fishing_duration):
        global bootpts; global fishpts; global big_fishpts; global tunapts; global salmonpts; global caviar_fishpts; global sharkpts
        tempboots += bootpts
        tempfish += fishpts
        tempbigfish += big_fishpts
        temptuna += tunapts
        tempsalmon += caviar_fishpts
        tempcaviar += caviar_fishpts
        tempshark += sharkpts
        print(f"""You catched {tempboots} Boots
You catched {tempfish} fish
You catched {tempbigfish} big fish
You catched {temptuna} tuna
You catched {tempsalmon} salmon
You catched {tempcaviar} caviar fish
You catched {tempshark} sharks
""")
        time.sleep(0.1)
        os.system('cls')
    
    global boots
    global fish
    global big_fish
    global tuna
    global salmon
    global caviar_fish
    global shark
    boots += tempboots
    fish += tempfish
    big_fish += tempbigfish
    tuna += temptuna
    salmon += tempsalmon
    caviar_fish += tempcaviar
    shark += tempshark

    global fishtimes
    fishtimes += 1
    print(f"You now have fished {fishtimes} times.")
    print(f"You now have {boots} boots")
    print(f"You now have {fish} fish")
    print(f"You now have {big_fish} big fish.")
    print(f"You now have {tuna} tuna.")
    print(f"You now have {salmon} salmon.")
    print(f"You now have {caviar_fish} caviar fish.")
    print(f"You now have {shark} sharks.")
    print("Returning to main menu in 3 seconds")
    time.sleep(3)
    greet()

def viewinventory():
    os.system('cls')
    print(f"{boots} boots")
    print(f"{fish} fish")
    print(f"{big_fish} big fish.")
    print(f"{tuna} tuna.")
    print(f"{salmon} salmon.")
    print(f"{caviar_fish} caviar fish.")
    print(f"{shark} sharks.")
    while True:
        optionchoose2 = input("Return to main menu? (Y for yes)")
        if optionchoose2 == "Y" or optionchoose2 == "y":
            greet()
            break
        else:
            print("This is not a valid option! try again.")

def sell():
    os.system('cls')
    while True:
        optionchoose2 = input("""What do you want to do in the Sell & buy stuff section?
1) Upgrade boat points
2) Sell fish
3) Upgrade fishing duration
4) Go back
Note:(Type 1, 2, 3 or 4) : 
""")
        if optionchoose2 in ["1", "2", "3", "4"]:
            break
        else:
            print("This is not a valid option, try again!")

    if optionchoose2 == "1":
        B = True
        C = False
        os.system('cls')
        global boat_points
        global FGCoins
        global bootpts; global fishpts; global big_fishpts; global tunapts; global salmonpts; global caviar_fishpts; global sharkpts
        global bootptsprice; global fishptsprice; global bigfishptsprice; global tunaptsprice; global salmonptsprice; global caviarfishptsprice; global sharkptsprice
        print("Note: These points are the number of increase of fishes during fishing")
        print(f"""1) Buy 1 boot point for {bootptsprice}FG¢.(You have {bootpts})
2) Buy 1 fish point for {fishptsprice}FG¢.(You have {fishpts})
3) Buy 1 big fish point for {bigfishptsprice}FG¢.(You have {big_fishpts})
4) Buy 1 tuna point for {tunaptsprice}FG¢.(You have {tunapts})
5) Buy 1 salmon point for {salmonptsprice}FG¢.(You have {salmonpts})
6) Buy 1 caviar fish point for {caviarfishptsprice}FG¢.(You have {caviar_fishpts})
7) Buy 1 shark point for {sharkptsprice}FG¢.(You have {sharkpts})
8) Back
""")
        while B:
            while True:
                optionchoose5 = input("Type a number (1, 2, 3, 4, 5, 6, 7 or 8) :")
                if optionchoose5 in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    break
                else:
                    if C:
                        print("Not a valid option. Try again!")
                    elif not optionchoose5 in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                        print("Not enough FG¢!")
            if optionchoose5 == "1" and FGCoins >= bootptsprice:
                FGCoins -= bootptsprice
                bootptsprice += math.ceil(bootptsprice * 1.375)
                bootpts += 1
                B = False
                break
            elif optionchoose5 == "2" and FGCoins >= fishptsprice:
                FGCoins -= fishptsprice
                fishptsprice += math.ceil(fishptsprice * 1.375)
                fishpts += 1
                B = False
                break
            elif optionchoose5 == "3" and FGCoins >= bigfishptsprice:
                FGCoins -= bigfishptsprice
                bigfishptsprice += math.ceil(bigfishptsprice * 1.375)
                big_fishpts += 1
                B = False
                break
            elif optionchoose5 == "4" and FGCoins >= tunaptsprice:
                FGCoins -= tunaptsprice
                tunaptsprice += math.ceil(tunaptsprice * 1.375)
                tunapts += 1
                B = False
                break
            elif optionchoose5 == "5" and FGCoins >= salmonptsprice:
                FGCoins -= salmonptsprice
                salmonptsprice += math.ceil(salmonptsprice * 1.375)
                salmonpts += 1
                B = False
                break
            elif optionchoose5 == "6" and FGCoins >= caviarfishptsprice:
                FGCoins -= caviarfishptsprice
                caviarfishptsprice += math.ceil(caviarfishptsprice * 1.375)
                caviar_fishpts += 1
                B = False
                break
            elif optionchoose5 == "7" and FGCoins >= sharkptsprice:
                FGCoins -= sharkptsprice
                sharkptsprice += math.ceil(sharkptsprice * 1.375)
                sharkpts += 1
                B = False
                break
            elif optionchoose5 == "8":
                sell()
            else:
                C = True
        sell()
        
    elif optionchoose2 == "2":
        os.system('cls')
        global boots; global fish; global big_fish; global tuna; global salmon; global caviar_fish; global shark
        global boots_sp; global fish_sp; global big_fish_sp; global salmon_sp; global tuna_sp; global caviar_fish_sp; global shark_sp
        print("You have")
        print(f"{boots} boots (1) for {boots * boots_sp}FG¢")
        print(f"{fish} fish (2) for {fish * fish_sp}FG¢")
        print(f"{big_fish} big fish. (3) for {big_fish * big_fish_sp}FG¢")
        print(f"{tuna} tuna. (4) for {tuna * tuna_sp}FG¢")
        print(f"{salmon} salmon. (5) for {salmon * salmon_sp}FG¢")
        print(f"{caviar_fish} caviar fish. (6) for {caviar_fish * caviar_fish_sp}FG¢")
        print(f"{shark} sharks. (7) for {shark * shark_sp}FG¢")
        while True:
            optionchoose3 = input(f"Input a number (8 to sell all fish) for {boots * boots_sp + fish * fish_sp + big_fish * big_fish_sp + tuna * tuna_sp + salmon * salmon_sp + caviar_fish * caviar_fish_sp + shark * shark_sp}FG¢: ")
            if optionchoose3 in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                break
            else:
                print("This is not a valid option.")
        if optionchoose3 == "1":
            FGCoins += boots * boots_sp
            boots = 0
        elif optionchoose3 == "2":
            FGCoins += fish * fish_sp
            fish = 0
        elif optionchoose3 == "3":
            FGCoins += big_fish * big_fish_sp
            big_fish = 0
        elif optionchoose3 == "4":
            FGCoins += tuna * tuna_sp
            tuna = 0
        elif optionchoose3 == "5":
            FGCoins += salmon * salmon_sp
            salmon = 0
        elif optionchoose3 == "6":
            FGCoins += caviar_fish * caviar_fish_sp
            caviar_fish = 0
        elif optionchoose3 == "7":
            FGCoins += shark * shark_sp
            shark = 0
        elif optionchoose3 == "8":
            FGCoins += boots * boots_sp + fish * fish_sp + big_fish * big_fish_sp + tuna * tuna_sp + salmon * salmon_sp + caviar_fish * caviar_fish_sp + shark * shark_sp
            boots = 0
            fish = 0
            big_fish = 0
            tuna = 0
            salmon = 0
            caviar_fish = 0
            shark = 0
        sell()
    elif optionchoose2 == "3":
        os.system('cls')
        A = True
        while True:
            global fishing_duration; global fishing_duration_price
            print(f"""You have {FGCoins}FG¢
Fishing duration is {fishing_duration}.
Rate is {fishing_duration_price}FG¢
1) 1 Fishing duration for {fishing_duration_price}FG¢
2) 10 Fishing duration for {fishing_duration_price * 10}FG¢
3) 25 fishing duration for {fishing_duration_price * 25}FG¢
4) 50 fishing duraion for {fishing_duration_price * 50}FG¢
5) Back""")
            while A:
                while True:
                    optionchoose4 = input("Type a number (1, 2, 3, 4, or 5)")
                    if optionchoose4 in ["1", "2", "3", "4", "5"]:
                        break
                    else:
                        print("This is not a valid option, try again!")
                if optionchoose4 == "1" and FGCoins >= fishing_duration_price:
                    FGCoins -= fishing_duration_price
                    fishing_duration += 1
                    fishing_duration_price += 1
                    break
                elif optionchoose4 == "2" and FGCoins >= fishing_duration_price * 10:
                    FGCoins -= fishing_duration_price * 10
                    fishing_duration += 2
                    fishing_duration_price += 10
                    break
                elif optionchoose4 == "3" and FGCoins >= fishing_duration_price * 25:
                    FGCoins -= fishing_duration_price * 25
                    fishing_duration += 25
                    fishing_duration_price += 25
                    break
                elif optionchoose4 == "4" and FGCoins >= fishing_duration_price * 50:
                    FGCoins -= fishing_duration_price * 50
                    fishing_duration += 50
                    fishing_duration_price += 50
                    break
                elif optionchoose4 == "5":
                    A = False
                    break
                else:
                    print("You cant afford that!")
            sell()
    elif optionchoose2 == "4":
        greet()
        
#credits:
#coding: @m41m6a (hapy) (on discord)
#basically everything: @m41m6a (hapy) (on discord)
greet()