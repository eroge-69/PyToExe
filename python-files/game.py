
import os
import random

logo = (r"""
        
 /$$$$$$$$ /$$                   /$$                               /$$$$$$   /$$                         /$$      
| $$_____/| $$                  | $$                              /$$__  $$ | $$                        | $$      
| $$      | $$   /$$  /$$$$$$$ /$$$$$$    /$$$$$$  /$$$$$$       | $$  \__//$$$$$$    /$$$$$$   /$$$$$$ | $$   /$$
| $$$$$   | $$  /$$/ /$$_____/|_  $$_/   /$$__  $$|____  $$      |  $$$$$$|_  $$_/   |____  $$ /$$__  $$| $$  /$$/
| $$__/   | $$$$$$/ |  $$$$$$   | $$    | $$  \__/ /$$$$$$$       \____  $$ | $$      /$$$$$$$| $$  \__/| $$$$$$/ 
| $$      | $$_  $$  \____  $$  | $$ /$$| $$      /$$__  $$       /$$  \ $$ | $$ /$$ /$$__  $$| $$      | $$_  $$ 
| $$$$$$$$| $$ \  $$ /$$$$$$$/  |  $$$$/| $$     |  $$$$$$$      |  $$$$$$/ |  $$$$/|  $$$$$$$| $$      | $$ \  $$
|________/|__/  \__/|_______/    \___/  |__/      \_______/       \______/   \___/   \_______/|__/      |__/  \__/
    """)


bosslogo = (r"""

                                               
  /     \             \            /    \       
 |       |             \          |      |      
 |       `.             |         |       :     
 `        |             |        \|       |     
  \       | /       /  \\\   --__ \\       :    
   \      \/   _--~~          ~--__| \     |    
    \      \_-~                    ~-_\    |    
     \_     \        _.--------.______\|   |    
       \     \______// _ ___ _ (_(__>  \   |    
        \   .  C ___)  ______ (_(____>  |  /    
        /\ |   C ____)/      \ (_____>  |_/     
       / /\|   C_____)       |  (___>   /  \    
      |   (   _C_____)\______/  // _/ /     \   
      |    \  |__   \\_________// (__/       |  
     | \    \____)   `----   --'             |  
     |  \_          ___\       /_          _/ | 
    |              /    |     |  \            | 
    |             |    /       \  \           | 
    |          / /    |         |  \           |
    |         / /      \__/\___/    |          |
   |           /        |    |       |         |
   |          |         |    |       |         |

     

 """)   

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw():
    print ("****************")

def save():
    list = [
        name,
        str(HP),
        str(FullHP),
        str(Power),
        str(Defence),
        str(Gold),
        str(Overdose),
        str(Assholeloosness)
    ]

    f = open("load.txt", "w")

    for item in list:
        f.write(item + "\n")
    f.close()

run = True
menu = True
rules = False
play = False
actone = False
actthree = False
actfor = False
actfive = False
battle = False

HP = 50
FullHP = HP
Power = 3
Defence = 3
Gold = 0
Overdose = 0
Assholeloosness = 0


enemies_list = ["Gipsy", "Crackhead", "Tesco security"]

mobs = {
        "Gipsy": {
        "HP": 15,
        "Power": 5,
        "Defence": 4,
        "Gold": 8
    },
        "Crackhead": {
        "HP": 12,
        "Power": 3,
        "Defence": 2,
        "Gold": 12
    },
        "Tesco security": {
        "HP": 20,
        "Power": 7,
        "Defence": 5,
        "Gold": 20
    }

}

boss_list = ["Big Bob"]

boss = {
    "Big Bob": {
        "HP": 50,
        "Power": 4,
        "Defence": 1,
        "Gold": 100
    }
}

def battle():
    global fight, play, run, HP, FullHP, Gold, Assholeloosness

    enemy = random.choice(enemies_list)
    eHP = mobs[enemy]["HP"]
    eFullHP = eHP
    ePower = mobs[enemy]["Power"]
    eDefence = mobs[enemy]["Defence"]
    eGold = mobs[enemy]["Gold"]

    while fight:
        clear()
        draw()
        print("Dont let" + " " + enemy + " " + "broke your nose!")
        draw()
        print(enemy + " " + "HP:" + str(eHP) + "/" + str(eFullHP))
        print(name + " " + "HP:" + str(HP) + "/" + str(FullHP))
        draw()
        print("1 -Attack")
        print("2 -Turn your ass up")

        choise = input("* ")

        if choise == "1":
            eHP -= Power
            print(name + " " + "dealt" + " " + str(Power) + " " + "damage" + " " + enemy + " " + "!")
            if eHP > 0:
                HP -= ePower
                print(enemy + " " + "delt" + " " +str(ePower) + " " +"damage" + " " + name + " " + "!")
            input("* ")
        elif choise == "2":
            clear()
            print("Noo its so losse! I can't feel anything!")
            Assholeloosness = Assholeloosness+ 1
            input("* ")
            clear()
            print("You are gaped + 1")
            eHP = eHP - 1
            input("* ")
            clear()
            print(enemy + " " + "HP - 1")
            input("* ")

        if HP <= 0:
            clear()
            print(enemy + " " + "Knock out" + " " + name + "...")
            draw()
            fight = False
            play = False
            run = False
            print("You are dead.")
            input("* ")
            quit()

        if eHP <=0:
            clear()
            print(name + " " + "Knock out" + " " + enemy + "...")
            draw()
            fight = False
            print("Somehow you win a fight!")
            input("* ")
            Gold = Gold + eGold


def ofiss():
    global  bossfight, HP, FullHP, Gold, Overdose, Assholeloosness

    enemy = random.choice(boss_list)
    bHP = boss[enemy]["HP"]
    bFullHP= bHP
    bpower = boss[enemy]["Power"]
    bdefence = boss[enemy]["Defence"]
    bgold = boss[enemy]["Gold"]

    while bossfight:
        clear()
        draw()
        print("Dont let" + " " + enemy + " " + "dominate you!")
        draw()
        print(enemy + " " + "HP:" + str(bHP) + "/" + str(bFullHP))
        print(name + " " + "HP:" + str(HP) + "/" + str(FullHP))
        draw()
        print("1 -Attack")
        print("2 -Turn your ass")

        choise = input("* ")

        if choise == "1":
            bHP -= Power
            print(name + " " + "delt" + " " + str(Power) + " " + "damage" + " " + enemy + " " + "!")
            if bHP > 0:
                HP -= bpower
                print(enemy + " " + "delt" + " " +str(bpower) + " " +"damage" + " " + name + " " + "!")
            input("* ")
        elif choise == "2":
            clear()
            print("Grrr auch bastard")
            Assholeloosness = Assholeloosness + 1
            input("* ")
            clear()
            print("You got streched + 1")
            bHP = bHP - 1
            input("* ")
            clear()
            print(enemy + " " + "HP - 1")
            input("* ")

        if HP <= 0:
            print(enemy + " " + "Your legs got pushed behind your head" + " " + name + " " + "and banged in asshole")
            draw()
            clear()
            print("You are gaped")
            Assholeloosness = Assholeloosness + 50
            print(bosslogo)
            bossfight = False
            input("* ")


        if bHP <=0:
            print(name + " " + "Knocked out" + " " + enemy + "...")
            draw()
            bossfight = False
            print("Luck was with you and you saved your virginity.")
            Gold = Gold + bgold
            input("* ")

while run:
    while menu:
        clear()
        print(logo)
        draw()
        print("1. Start new game")
        print("2. Load game")
        print("3. Rules")
        print("4. Exit")
        draw()
        if rules:
            print("You mast help Viking to get a job in German hardcore porn industry Ekstra Stark. Dont let him overdose")
            print("If his overdose level reach 100 he dies.")
            draw()
            rules = False
            menu = True

        choise = input("* ")

        if choise == "1":
            clear()
            name = ("Vikings")
            menu = False
            play = True

        elif choise == "2":
            try:
                f = open("load.txt", "r")
                load_list = f.readlines()
                if len(load_list) == 8:
                    name = load_list[0][:-1]
                    HP = load_list[1][:-1]
                    FullHP = load_list[2][:-1]
                    Power = load_list[3][:-1]
                    Defence = load_list[4][:-1]
                    Gold = load_list[5][:-1]
                    Overdose = load_list[6][:-1]
                    Assholeloosness = load_list[7][:-1]
                    clear()
                    draw()
                    print("Welcome back cunt!" +" " + name + " "+ "Bastard!")
                    draw()
                    input("* ")
                    menu = False
                    play = True
                else:
                    print("Your save file is corrupted")
                    input("* ")
            except OSError:
                print("You dont have a saved game")
                input("* ")
        elif choise == "3":
            rules = True
            
        elif choise == "4":
            quit()

    while play:
        save()
        draw()
        print("Viking dont forget you have job interview today! Your grandma is shouting from room. What you will gonna do?")
        draw()
        input("* ")
        actone = True

        while actone:
            clear()
            print("Name: " + name)
            print("HP: " + str(HP) + "/" + str(FullHP))
            print("Power: " + str(Power))
            print("Defence: " + str(Defence))
            print("Gold: " + str(Gold))
            print("Overdose: " + str(Overdose))
            print("Asshole loosnes: " + str(Assholeloosness))
            draw()
            print("1. Get a grip and call to Ekstra Stark!")
            print("2. Drink a beer!")
            draw()
            

            choise = input("* ")

            if choise == "1":
                clear()
                print("Rrrrrr phone ring in Ekstra Stark offise")
                input("* ")
                clear()
                print("Mmm its me SinkHoleG calling. I would love to get a casting in porn movie")
                input("* ")
                clear()
                print("I have extreamly small penis like micro and massive balls.")
                input("* ")
                clear()
                print("Well done! Your interview is set.")
                input("* ")
                actone = False
                acttwo = True

            elif choise == "2":
                clear()
                print("Start smashing beer")
                input("* ")
                Overdose = Overdose +1
                if Overdose >= 100:
                    clear()
                    print(" You was sleeping on back and puking on your face and die.")
                    input("* ")
                    quit()
                if Overdose < 100:
                    clear()
                    print(" Mmmmm two liter beer from plastic bottle went in like a butter.")
                    input()
                    clear()
                    print("Overdose + 1")
                    input("* ")

        while acttwo:
            clear()
            print("Name: " + name)
            print("HP: " + str(HP) + "/" + str(FullHP))
            print("Power: " + str(Power))
            print("Defence: " + str(Defence))
            print("Gold: " + str(Gold))
            print("Overdose: " + str(Overdose))
            print("Asshole loosnes: " + str(Assholeloosness))
            draw()
            print("1. Take your brand new Homo 2000 bag and go.")
            print("2. Little bit strech your asshole with fingers.")
            print("3. Smoka some crack!")
            draw()

            choise = input("* ")

            if choise == "1":
                    clear()
                    draw()
                    print("You are outside and your alco sense give you a warning.")
                    print("1. Run away like a small girl.")
                    print("2. Tell them you dont have a money and be ready to fight!")
                    draw()
                    

            elif choise == "2":
                    clear()
                    print("Smash your fingers in ass!")
                    Assholeloosness = Assholeloosness + 1
                    input("* ")
                    clear()
                    print("Asshole loosness +1")
                    input("* ")
                    clear()
                    print("WTF? TV remote control!")
                    Assholeloosness = Assholeloosness + 1
                    input("* ")
                    clear()
                    print("Asshole loosness +1")

            elif choise == "3":
                    clear()
                    print("You feel high and shit yourself!")
                    input("* ")
                    Overdose = Overdose + 1
                    clear()
                    print("Overdose + 1")
                    input("* ")
                    if Overdose >= 100:
                        clear()
                        print("You pass out with ass up and die!")
                        input("* ")
                        quit()
                    if Overdose < 100:
                        clear()
                        print("This was sooo good! fuck yeah!")

            choise = input("* ")

            if choise == "1":
                    clear()
                    print("Your escape was succsessful")
                    input("* ")
                    acttwo = False
                    actthree = True

            elif choise == "2":
                    clear()
                    print("Gggg asshole i dont have money! Fuck off!")
                    input("* ")
                    clear()
                    fight = True
                    battle()

        while actthree:
            clear()
            print("Name: " + name)
            print("HP: " + str(HP) + "/" + str(FullHP))
            print("Power: " + str(Power))
            print("Defence: " + str(Defence))
            print("Gold: " + str(Gold))
            print("Overdose: " + str(Overdose))
            print("Asshole loosnes: " + str(Assholeloosness))
            draw()
            print("1. Catch a bus to city center.")
            print("2. Pick up cigarete end from street.")
            draw()

            choise = input("* ")

            if choise == "1":
                clear()
                print("And here you are, front of Extra Stark office! You are so proud of yourself.")
                input("* ")
                if Assholeloosness >=10:
                    print("Ooo Mr SinkHoleG! We was waiting for you.")
                    input("* ")
                    cactfor = True

                if Assholeloosness < 10:
                    clear()
                    print("You can't be Mr SinkHoleG. Your asshole is to tight!!!")
                    input("* ")
                    clear()
                    print("You pathetic homeless!")
                    input("* ")
                    actthree = False
                    actfor = True

            elif choise == "2":
                clear()
                print("Mmm so lovely cigarette bud ....!")
                input("* ")
                clear()
                Overdose = Overdose + 2
                print("Taste like shit. Eactly how i like it.")
                input("* ")
                clear()
                print("Overdose + 2")
                input("* ")

        while actfor:
            clear()
            print("Suprise suprise there is some filipino homo front of you!")
            input("* ")
            clear()
            print("Name: " + name)
            print("HP: " + str(HP) + "/" + str(FullHP))
            print("Power: " + str(Power))
            print("Defence: " + str(Defence))
            print("Gold: " + str(Gold))
            print("Overdose: " + str(Overdose))
            print("Asshole loosnes: " + str(Assholeloosness))
            draw()
            print("1. Fight with big Bob to get last girl.")
            print("2. Accept your fate and film a hardcore german gay sex scene.")
            draw()

            choise = input("* ")

            if choise == "1":
                clear()
                print("Thats it Viking i will gonna strech you!!!")
                input("* ")
                clear()
                print("I gonna use lemon on you!!!")
                input("* ")
                clear()
                print("Ha ha ha")
                input("* ")
                bossfight = True
                ofiss()
                actfor = False
                actfive = True

            elif choise == "2":
                clear()
                print("Im relly sorry Mr SinkHoleG your asshole is not gaped enough....!")
                input("* ")
                print("We recomend you to talk with Big Bob.")
                input("* ")

        while actfive:
            clear
            draw()
            print("Ekstra Startk team saw your destroyed asshole and you got a job instantly.")
            input("* ")
            print("In the following years, Vikings lived happily ever after and appeared in over 300 episodes.")
            input("* ")
            quit()