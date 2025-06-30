run = True
import time
import random
import csv
import os
import webbrowser
import math

print("Starting Ag@m")
time.sleep(1)
logo = [
        '~~~      @@@@@@@      ~~~',
        '~~~     @@     @@     ~~~',
        '~~~    @@       @@    ~~~',
        '~~~   @@   @@@@@@@@   ~~~',
        '~~~   @@  @@    @@@   ~~~',
        '~~~   @@  @@    @@@   ~~~',
        '~~~   @@  @@    @@@   ~~~',
        '~~~   @@   @@@@@@@@   ~~~',
        '~~~    @@             ~~~',
        '~~~     @@       @@   ~~~',
        '~~~      @@@@@@@@@    ~~~'
        ]
for i in range(len(logo)):
    print(logo[i])
    time.sleep(0.5)

#Dungeon Masters
import random
import time

def dngnmstrz():
    crdts = 0
    name=input("What is your name?")
    if name == 'Starshot':
        print("win_codes: a.b.a.a.a.b..")
        name=input("What is your name?")
    time.sleep(0.2)
    print(f"Hello, {name}.")
    time.sleep(0.1)
    print("DISCLAMER: You will most likly die...")
    time.sleep(0.1)
    print("you are running down a dark stone hallway, unsure of how you got here, you  make a decision:")
    time.sleep(0.1)
    c1=input("you can, a : continue running, or, b : stop and rest. What do you do, " + name + "?")
    time.sleep(0.1)
    print()
    if c1 == 'a':
        print("You keep running and hit a  wall.")
        time.sleep(0.1)
        print("The wall appears to have three doors.")
        time.sleep(0.1)
        print("Your options are:")
        time.sleep(0.1)
        c2=input("a : a door with fire behind it, b : a door with poison apples behind it, or c : a door with certian death behind it. So, your call, " + name + ".")
        time.sleep(0.1)
        print()
        if c2 == 'b':
            print("You walk around the apples and come across a large hole!")
            time.sleep(0.1)
            print("You see a small ledge. Do you wish to attempt walking the ledge, or search for a sefer route?")
            time.sleep(0.1)
            c3=input("a : search an alternitave, or b : attemt the walk. It's up to you, " + name + ".")
            time.sleep(0.1)
            print()
            if c3 == 'a':
                print("You feel a button and press it.")
                time.sleep(0.1)
                print("A worrior appears.")
                time.sleep(0.1)
                c4=input("You can, a : talk to him, or b : stand there")
                time.sleep(0.1)
                print()
                if c4 == 'a':
                    print("You ask him his name. He claims to be Fredric, the neverdieing knight. He also agrees to help you cross the hole.")
                    time.sleep(0.1)
                    print("Fred pulls out two pairs of flying shoes.")
                    time.sleep(0.1)
                    print("Fred asks if you want to put them on.")
                    time.sleep(0.1)
                    c5=input("a : put on the shoes, or b : try to jump the hole")
                    time.sleep(0.1)
                    print()
                    if c5 == 'a':
                        print(f"You put on the shoes. {name}! Those shoes suit you. Fred says. The flying shoes take you to the other side of the hole.")
                        time.sleep(0.1)
                        print("You wait for Fred, but as you wach him fly, the shoes fail and he plumits.")
                        time.sleep(0.1)
                        print("You keep running with Freds sword that he threw after he fell.")
                        time.sleep(0.1)
                        print("You are getting tired and have the option to rest.")
                        time.sleep(0.1)
                        c6=input("a : keep going, or b : stop and rest")
                        time.sleep(0.1)
                        print()
                        if c6 == 'b':
                            print("You stop and rest, a screeching echos throughout the tunnel.")
                            print("You draw your sword and perpare to put up a fight!")
                            print(f"Fred comes out of nowhere and kills the hairy beast. {name}! Fred shouts.")
                            print("Notification!")
                            print("Fred is back!")
                            print("The cave splits into two caves")
                            c7=input("a : first cave, or b : second cave")
                            print()
                            if c7 == 'a': #this "if" statment changes everything!
                                print("You choose the first path.")
                                print("Your walk turns into a crawl and the passage grows smaller.")
                                print(f"{name}! You look back and Fred is stuck!")
                                print("Fred asks for help but as you struggle the top of the passage crushes Fred and your hand.")
                                print("Notification!")
                                print(f"Fred died. {name}'s hand is gone!")
                                print("You search your bag for medical gauze to cover up your hand.")
                                print("You find some and wrap your hand.")
                                print("Should you keep going, or rest?")
                                ac1=input(f"a : rest, or b : keep going")
                                print()
                                if ac1 == 'a':
                                    print("You rest.")
                                    print("When you wake up you feel recharged. Your hand is still in pain.")
                                    print("You walk on and there are three doors. You are confused and dissorented.")
                                    print("For some reason you turn around and walk to where you last saw Fred, only he wasn't there. You are lost.")
                                    print("You hear a weird noise.")
                                    ac2=input("You have a decision; a : draw Fred's sword, or b : stay put")
                                    print()
                                    if ac2 == 'a':
                                        print("As you draw the sword the noise repeats and echos.")
                                        print("You blacked out!")
                                        print("You wake up in a lit room.")
                                        print("The corners of the room are lined in a metalic yellow metal while the walls a red velvet.")
                                        print("You try to stand up but find you are tied to a chair with a peice of paper on your lap. It reads: Don't panic, somebody will come.")
                                        print("You have a choice to struggle or wait")
                                        ac3=input("a : wait, or b : struggle")
                                        print()
                                        if ac3 == 'a':
                                            print("You wait.")
                                            print(f"Well, well, if it isn't {name}. And the greatsword of Fredric Galahad.")
                                            print("You ask them who they are.")
                                            print("They claim to be the great wizard Alchimedian Ssair.")
                                            print("Alchimedian uses the sword to cut your rope. He points it at you.")
                                            ac4=input("You can, a : try to take the sword with your remaining hand, or b : sit and see what happens")
                                            print()
                                            if ac4 == 'a':
                                                print("You reach your hand forward and grab the blade.")
                                                print("You cut your hand but it dosent bleed.")
                                                print("Your hand is in pain, but you mannage to get the sword from Alchimedian.")
                                                print("DIE ALCHIMEDIAN! You stab Alchimedian")
                                                print("Alchemedian died.")
                                                print("You have a choice to make.")
                                                ac5=input("a : leave through the door, or b : search an alternitave")
                                                print()
                                                if ac5 == 'a':
                                                    print("You get up and walk out the door.")
                                                    print("")
                                                    print("You won!")
                                                    print("Status: one hand, slightly depresed,")
                                                    crdts=input("Would you like credits? (y/n)")
                                                    if crdts == 'y':
                                                        print("")
                                                        print("A concept by Starshot studios")
                                                        print("Programed by:")
                                                        print("Sailas de Kok")
                                                        print("Scratch name:")
                                                        print("a_Pet_Turtle and de-Kok_stuff")
                                                        print("Thanks for playing!")
                                                    win=input("")
                                                if ac5 == 'b':
                                                    print("You search an alternitave.")
                                                    print("You press a button and hear strings pulling behind you.")
                                                    print("You turn around and see-")
                                                    print("You died! Cause: shot with arrow")
                                                else:
                                                    print("You sit as and a chandelier falls on you.")
                                                    print("You are in a blank void alone with your thoughts.")
                                                    print()
                                                    print("Yay?")
                                                    win=input("")
                                            else:
                                                print("You died! Cause: stabbed with greatsword")
                                                win=input("")
                                        else:
                                            print("You struggle to leave the chair.")
                                            print("The chair moves and pulls a rope.")
                                            print("You look up.")
                                            print("You died! Cause: crushed by falling chandelier")
                                            win=input("")
                                    else:
                                        print("You died! Cause: unknown")
                                        win=input("")
                                else:
                                    print("You keep going.")
                                    print("You collapse due to a lack of energy.")
                                    print("You died! Cause: unknown")
                                    win=input("")
                            else:
                                if c7 == 'b':
                                    print("You choose the second path.")
                                    print("It is a very open path.")
                                    print("You come across a dead end.")
                                    print("There are two ropes.")
                                    print("Fred wants to make a decision this time.")
                                    bc1=input("a : let Fred choose, or b : you choose")
                                    print()
                                    if c1 == 'a':
                                        print("you let Fred choose")
                                        frdchrz=random.randint(1,2)
                                        frdchrz = int(frdchrz)
                                        if frdchrz == 1:
                                            print("Fred pulls the first rope and the path fills with water.")
                                            print("You died! Cause: drowned")
                                            win=input("")
                                        else:
                                            print("Fred pulls the second lever and a path appears.")
                                            print("The path grows darker as you go deeper.")
                                            print("You hear a strange noise echo through your eardrum.")
                                            print(f"You have a choice, {name}")
                                            bc2=input("a : investigate or, b : prepare for battle")
                                            print()
                                            if bc2 == 'a':
                                                print("A red light blinds you.")
                                                print("When you regain vision, (and consensousness,) you are in a golf course.")
                                                print("A hairry beast greats you and invites you to play golf.")
                                                print("Like always, you have a choice. a : you stay and play golf with a suspicious beast and Fred, b : run away; you dont trust this guy")
                                                bc3=input("a : stay, b : run")
                                                print()
                                                if bc3 == 'a':
                                                    print("")
                                                    print("You won!")
                                                    print("status: Happy")
                                                    print("  🔳  🔳  ")
                                                    print("          ")
                                                    print("🔳      🔳")
                                                    print("  🔳🔳🔳  ")
                                                    crdts=input("Would you like credits? (y/n)")
                                                    if crdts == 'y':
                                                            print("")
                                                            print("A concept by Starshot studios")
                                                            print("Programed by:")
                                                            print("Sailas de Kok")
                                                            print("Scratch name:")
                                                            print("a_Pet_Turtle and de-Kok_stuff")
                                                            print("Thanks for playing!")
                                                    win=input("")
                                                else:
                                                    if bc3 == 'b':
                                                        print("You run away")
                                                        print("Wait for the next update!")
                                                        win=input("")
                                                    else:
                                                        crdts=input("Would you like credits? (y/n)")
                                                        if crdts == 'y':
                                                            print("")
                                                            print("A concept by Starshot studios")
                                                            print("Programed by:")
                                                            print("Sailas de Kok")
                                                            print("Scratch name:")
                                                            print("a_Pet_Turtle and de-Kok_stuff")
                                                            print("Thanks for playing!")
                                                    win=input("")
                                                        
                                            else:
                                                print("You died! Cause: unknown")
                                                win=input("")
                                else:
                                    print("You died! Cause: sudden hart attack")
                                    win=input("")
                        else:
                            print("You keep running.")
                            print("You see a light! It's the exit! Your free!")
                            print("You died! Cause: disentegrated")
                            win=input("")
                    else: 
                        print("You take a majestic leap.")
                        print("You died! Cause: hit the bottom of the hole too hard")
                        win=input("")
                else:
                    print("You died! Cause: impaled with knights sword")
                    win=input("")
            else:
                if c3 == 'b':
                    print("You attempt the walk")
                    print("You get to the other side.")
                    c3c=input("There are two caves. a : unknown, b : unknown.")
                    print("It is too late! You fall and try to scramble your body up, but when you look up you see the dungeon is collapsing! You turn left and right trying to get out. You look up. Hey, whats th-")
                    print("You died! Cause: dungeon collapse")
                    win=input("")
                else:
                    print("You died! Cause: fell in hole")
                    win=input("")
        else:
            if c2 == 'a':
                print("You died! Cause: wraped in flames")
                win=input("")
            else:
                print("You died! Cause: unknown")
                win=input("")
    else:
        print("You died! Cause: unknown")
        win=input("")

#Number Guesser
def numbergussr():
    sml="1"
    big="10"
    num=random.randint(1,10)
    watitis=f"{sml} through {big}"
    guess=int(input(f"Guess a number, {watitis}."))
    if guess == num:
        print("You got lucky.")
        exit()
    else:
        if guess > num:
              print("Guess lower")
              big=guess
        else:
            if guess < num:
                print("Guess higher")
                sml=guess
    watitis=f"{sml} through {big}"
    guess=input(f"Guess a number, {watitis}.")
    guess = int(guess)
    if guess == num:
        print("Second try! Nice!")
        exit()
    else:
        if guess > num:
            print("Guess lower")
            big=guess
        else:
            if guess < num:
                print("Guess higher")
                sml=guess
    watitis=f"{sml} through {big}"
    guess=input(f"Guess a number, {watitis}.")
    guess = int(guess)
    if guess == num:
        print("You win!")
        print(f"The number was {num}!")
        exit()
    else:
        print("You lose.")
        print(f"The number was {num}.")

#python in python
def pyinpy():
    print("python... in python...")
    print("Type run to run your code. When the code is done running, you will return to home.")
    commandslist = []
    response = ''
    
    def addtolist(response):
        commandslist.append(response)

    def run():
        runcodestring = "\n".join(commandslist)
        print()
        print("# Running code:\n", runcodestring)
        print()
        try:
            exec(runcodestring)
        except Exception as e:
            print(f"An error occurred: {e}")
    
    while response != 'run':
        response = input(">>> ")
        if response != 'run':
            addtolist(response)
    run()

#Blackjack
class Blackjack:
    def __init__(self):
        double_down=False
        self.player_chips = {'green': 10, 'red': 5, 'white': 1}
        self.card_list = {
            '2 of Spades': 2, '2 of Hearts': 2, '2 of Clubs': 2, '2 of Diamonds': 2,
            '3 of Spades': 3, '3 of Hearts': 3, '3 of Clubs': 3, '3 of Diamonds': 3,
            '4 of Spades': 4, '4 of Hearts': 4, '4 of Clubs': 4, '4 of Diamonds': 4,
            '5 of Spades': 5, '5 of Hearts': 5, '5 of Clubs': 5, '5 of Diamonds': 5,
            '6 of Spades': 6, '6 of Hearts': 6, '6 of Clubs': 6, '6 of Diamonds': 6,
            '7 of Spades': 7, '7 of Hearts': 7, '7 of Clubs': 7, '7 of Diamonds': 7,
            '8 of Spades': 8, '8 of Hearts': 8, '8 of Clubs': 8, '8 of Diamonds': 8,
            '9 of Spades': 9, '9 of Hearts': 9, '9 of Clubs': 9, '9 of Diamonds': 9,
            '10 of Spades': 10, '10 of Hearts': 10, '10 of Clubs': 10, '10 of Diamonds': 10,
            'Jack of Spades': 10, 'Jack of Hearts': 10, 'Jack of Clubs': 10, 'Jack of Diamonds': 10,
            'Queen of Spades': 10, 'Queen of Hearts': 10, 'Queen of Clubs': 10, 'Queen of Diamonds': 10,
            'King of Spades': 10, 'King of Hearts': 10, 'King of Clubs': 10, 'King of Diamonds': 10,
            'Ace of Spades': 11, 'Ace of Hearts': 11, 'Ace of Clubs': 11, 'Ace of Diamonds': 11
        }
        self.dealt_cards = []

    def cash_out(self):
        total_value = sum(self.player_chips.values())
        print(f"\nYou are cashing out. You have a total of ${total_value}.")
        exit()

    def draw_cards(self):
        self.dealt_cards = random.sample(list(self.card_list.keys()), 4)

    def calculate_hand_value(self, cards):
        value = 0
        aces = 0
        for card in cards:
            card_value = self.card_list[card]
            if card_value == 11:
                aces += 1
            value += card_value
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_soft_17(self, cards):
        value = self.calculate_hand_value(cards)
        if value == 17:
            for card in cards:
                if self.card_list[card] == 11:
                    return True
        return False

    def play_game(self):
        self.draw_cards()
        print("Welcome to the solo-blackjack casino.py. You will start with $45 dollars in chips.")
        print("Red chips are worth $5, White chips $1, and green chips $10")
        print(f"You have {self.player_chips['green']} green chips, {self.player_chips['red']} red chips, and {self.player_chips['white']} white chips.")

        while True:
            bet_green, bet_red, bet_white = map(int, input("Type how many chips you would like to put in in the format of green, red, white. Example: 1, 2, 4 would be 1 green, 2 red, and 4 white: ").split(", "))
            total_bet = bet_green * 10 + bet_red * 5 + bet_white * 1
            if total_bet == 0:
                print("You need to bet at least one chip.")
                continue
            if bet_green > self.player_chips['green'] or bet_red > self.player_chips['red'] or bet_white > self.player_chips['white']:
                print("You don't have enough chips to make that bet.")
                continue
            break

        self.player_chips['green'] -= bet_green
        self.player_chips['red'] -= bet_red
        self.player_chips['white'] -= bet_white

        player_cards = self.dealt_cards[:2]
        dealer_cards = self.dealt_cards[2:]

        print(f"You have been dealt the cards {player_cards[0]} and {player_cards[1]}. The dealer has been dealt {dealer_cards[0]} and an unknown card.")

        while True:
            hit_or_stand = input("Would you like to 'hit', 'stand' or 'double down'?").lower()
            if hit_or_stand == 'hit':
                dealt_card = random.choice(list(self.card_list.keys()))
                player_cards.append(dealt_card)
                print(f"You have been dealt the {dealt_card}")
                player_value = self.calculate_hand_value(player_cards)
                print(f"Your current hand value is {player_value}.")
                if player_value > 21:
                    print("Bust! You exceeded 21.")
                    break
            elif hit_or_stand == 'stand':
                print("You chose to stand.")
                break
            elif hit_or_stand == 'double down':
                self.double_down(player_cards, bet_green, bet_red, bet_white)
                break
            else:
                print("Invalid input. Please type 'hit' or 'stand'.")

        player_value = self.calculate_hand_value(player_cards)
        dealer_value = self.calculate_hand_value(dealer_cards)

        while dealer_value < 17 or (dealer_value == 17 and self.is_soft_17(dealer_cards)):
            dealt_card = random.choice(list(self.card_list.keys()))
            dealer_cards.append(dealt_card)
            dealer_value = self.calculate_hand_value(dealer_cards)
            print(f"The dealer currently has the cards: {dealer_cards[:-1]} and an unknown card.")
            time.sleep(2.5)
            print("The dealer has either hit a soft 17 or has a card value under 17. They must draw another card.")
            time.sleep(2.5)
            print(f"The dealer has drawn '{dealt_card}'. Current dealer value: {dealer_value}")

        print("The dealer's final hand is: ")
        for q in range(len(dealer_cards)):
            print(dealer_cards[q])
        time.sleep(1.5)

        if player_value > 21:
            print("You busted. You lose your bet.")
        elif dealer_value > 21:
            print("The dealer busted. You win!")
            self.player_chips['green'] += bet_green * 2
            self.player_chips['red'] += bet_red * 2
            self.player_chips['white'] += bet_white * 2
        elif player_value > dealer_value:
            print("You won! You get double the chips you put in.")
            self.player_chips['green'] += bet_green * 2
            self.player_chips['red'] += bet_red * 2
            self.player_chips['white'] += bet_white * 2
        elif player_value < dealer_value:
            print("You lost. You lose the chips you put in.")
        else:
            print("It's a tie. Dealer wins, you lose the chips you put in.")

        print(f"Your current chip count is: {self.player_chips['green']} green chips, {self.player_chips['red']} red chips, and {self.player_chips['white']} white chips.")

    def run(self):
        while True:
            self.play_game()
            run_another = input("Do you want to 'play again', or 'cash out'? ").lower()
            if run_another == 'cash out':
                self.cash_out()
            elif run_another == 'play again':
                continue
            else:
                print("Invalid response. Exiting...")
    def double_down(self, player_cards, bet_green, bet_red, bet_white):
        dealt_card = random.choice(list(self.card_list.keys()))
        player_cards.append(dealt_card)
        self.player_chips['green'] -= bet_green
        self.player_chips['red'] -= bet_red
        self.player_chips['white'] -= bet_white
        print(f"You doubled down, doubling your bet. You have drawn a {dealt_card}.")

#Date picker
def datepc():
    year = random.randint(0, 2024)
    m = random.randint(1, 12)
    ampm = ["am", "pm"]
    ap = random.choice(ampm)
    if year % 4 == 0:
        leapyr = ""
    else:
        leapyr = " not"
    if m == 1 or m == 3 or m == 5 or m == 7 or m == 9 or m == 11:
        d = random.randint(1, 31)
    elif m == 2:
        if year % 4 == 0:
            d = random.randint(1, 29)
            leap = ""
        else:
            d = random.randint(1, 28)
            leap = "not"
    else:
        d = random.randint(1, 30)
    hr = random.randint(1, 12)
    minu = random.randint(0, 59)
    if minu <= 9:
        minu = '0' + str(minu)
    else:
        minu = str(minu)
    if m == 1:
        m = 'Jan.'
    elif m == 2:
        m = 'Feb.'
    elif m == 3:
        m = 'Mar.'
    elif m == 4:
        m = 'Apr.'
    elif m == 5:
        m = 'May'
    elif m == 6:
        m = 'June'
    elif m == 7:
        m = 'July'
    elif m == 8:
        m = 'Aug.'
    elif m == 9:
        m = 'Sep.'
    elif m == 10:
        m = 'Oct.'
    elif m == 11:
        m = 'Nov.'
    elif m == 12:
        m = 'Dec.'
    print(f"The date is {m} {d}, {year}. It is {leapyr} a leap year. Time: {hr}:{minu} {ap}.")
#Coin flip    
def coin():
    print("Heads, or tails? (h/t)")
    bet = input()
    if bet != 'h' or 't':
        print("invalid input. Try again.")
        coin()
    flippick = random.randint(1, 2)
    if flippick == 1:
        flip = 'heads'
    else:
        flip = 'tails'
    print(f"You flipped {flip}!")
    if bet == 'h' and flip == 'heads' or bet == 't' and flip == 'tails':
        print("You win!")
    else:
        print("You loose")
#Rock paper scissors
def rps():
    time.sleep(1)
    print("""
        choose from these three:
        r --- rock
        p --- paper
        s --- scissors""")
    choice = input()
    aichoice = random.randint(1, 3)
    if aichoice == 1:
        aichoice = 'r'
    elif aichoice == 2:
        aichoice = 'p'
    elif aichoice == 3:
        aichoice = 's'
    else:
        print("there was an error")
    time.sleep(0.05)
    print("Rock!")
    time.sleep(0.1)
    print("Paper!")
    time.sleep(0.1)
    print("Scissors!")
    time.sleep(0.1)
    print("Shoot!")
    if choice == aichoice:
        print("Tie")
    elif choice == 'r' and aichoice == 'p':
        print("You loose. Paper covers rock.")
    elif choice == 'r' and aichoice == 's':
        if random.randint(1, 100) == 1:
            print("You won. The rock turns out to be a substance that disentagrates scissors and only scissors. The scissors disentigrate.")
        else:
            print("You win. Rock crushes scissors")
    elif choice == 'p' and aichoice == 'r':
        print("You win.")
    elif choice == 'p' and aichoice == 's':
        print("You loose.")
    elif choice == 's' and aichoice == 'p':
        print("You win.")
    elif choice == 's' and aichoice == 'r':
        print("You loose.")
#dice
def dice():
    print('''
        Type '1' for a 4-sided die.
        Type '2' for a 6-sided die.
        Type '3' for a 8-sided die.
        Type '4' for a 10-sided die.
        Type '5' for a 12-sided die.
        Type '6' for a 20-sided die.
        Type '7' for a hundred-sided die.''')
    die = input()
    if die == '1':
        print("You rolled " + str(random.randint(1, 4)))
    elif die == '2':
        print("You rolled " + str(random.randint(1, 6)))
    elif die == '3':
        print("You rolled " + str(random.randint(1, 8)))
    elif die == '4':
        print("You rolled " + str(random.randint(1, 10)))
    elif die == '5':
        print("You rolled " + str(random.randint(1, 12)))
    elif die == '6':
        print("You rolled " + str(random.randint(1, 20)))
    elif die == '7':
        print("You rolled " + str(random.randint(1, 100)))
    else:
        print("Invalid input. Returning to home.")
    print("Roll again? (y/n)")
    ans = input()
    if ans == 'y':
        dice()
    elif ans == "n":
        print("Returning to home.")
    else:
        print("Invalid input. Returning to home.")
        
#Merge sorter
def merge_sort():
    def mergesort(arr):
        if len(arr) <= 1:
            return arr
    
        mid = len(arr) // 2
        lefthalf = arr[:mid]
        righthalf = arr[mid:]
        left_sorted = mergesort(lefthalf)
        right_sorted = mergesort(righthalf)
        return merge(left_sorted, right_sorted)

    def merge(left, right):
        sorted_array = []
        leftindex, rightindex = 0, 0
        while leftindex < len(left) and rightindex < len(right):
            if left[leftindex] <= right[rightindex]:
                sorted_array.append(left[leftindex])
                leftindex += 1
            else: 
                sorted_array.append(right[rightindex])
                rightindex += 1
        sorted_array.extend(right[rightindex:])
        sorted_array.extend(left[leftindex:])
        return sorted_array
    print("Enter the numbers separated by space: ")
    arr = list(map(int, input().split()))
    sorted_arr = mergesort(arr)
    print("Sorted array:", sorted_arr)

#Magic 8 ball
def magic8():
    answers = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes – definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    print("What is your question? (Press enter to submit answer)")
    question = input()
    answer = random.choice(answers)
    print(f"{answer} You asked {question}")
    print("Shake again? y/n")
    shkagn = input()
    if shkagn == 'y':
        magic8()
    else:
        print("Invalid input. Returning to home.")


#calculator
def calc():
    def add(x, y):
        return x + y

    def subtract(x, y):
        return x - y

    def multiply(x, y):
        return x * y

    def divide(x, y):
        if y == 0:
            return "Error! Division by zero!"
        return x / y

    def square_root(x):
        if x < 0:
            return "Error! Cannot find square root of a negative number!"
        return math.sqrt(x)

    print("Select operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Square Root")
    print("6. Area of a paralellogram")
    print("7. Area of a triangle")
    while True:
        print("Enter choice 1, 2, 3, 4, 5, 6, 7")
        choice = input()
        if choice in ('1', '2', '3', '4'):
            print("Enter first number: ")
            num1 = float(input())
            print("Enter second number: ")
            num2 = float(input())
            if choice == '1':
                print("Result:", add(num1, num2))
            elif choice == '2':
                print("Result:", subtract(num1, num2))
            elif choice == '3':
                print("Result:", multiply(num1, num2))
            elif choice == '4':
                print("Result:", divide(num1, num2))
        elif choice == '5':
            print("Enter a number: ")
            num = float(input())
            print("Result:", square_root(num))
        elif choice in ('6', '7'):
            print("Enter the base")
            base = float(input())
            print("Enter the height")
            height = float(input())
            if choice == '6':
                print("Result:", base * height)
            elif choice == '7':
                print("Result:", (base * height) / 2)
        else:
            print("Invalid Input")
        print("Do you want to perform another calculation? (y/n): ")
        another_calculation = input()
        if another_calculation.lower() != 'y':
            print("Returning to home")
            break

#expenses tracker        
def expenses():
    class ExpenseTracker:
        def __init__(self):
            self.expenses = []

        def add_expense(self, category, amount):
            self.expenses.append({"Category": category, "Amount": amount})
            print("Expense added successfully!")

        def view_expenses(self):
            if self.expenses:
                print("Expense Summary:")
                print("{:<15} {:<10}".format("Category", "Amount"))
                for expense in self.expenses:
                    print("{:<15} ${:<10.2f}".format(expense["Category"], expense["Amount"]))
            else:
                print("No expenses recorded.")

        def export_to_csv(self, filename):
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Category', 'Amount']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for expense in self.expenses:
                    writer.writerow(expense)
            print("Data exported to CSV successfully!")

    def main():
        print("Welcome to the Expense Tracker App!")
        expense_tracker = ExpenseTracker()
        while True:
            print("\nOptions:")
            print("1. Add Expense")
            print("2. View Expenses")
            print("4. Exit")
            print("3. Export Expenses to CSV")
            choice = input("Enter your choice: ")
            if choice == '1':
                category = input("Enter the expense category: ")
                amount = float(input("Enter the expense amount: "))
                expense_tracker.add_expense(category, amount)
            elif choice == '2':
                expense_tracker.view_expenses()
            elif choice == '3':
                filename = input("Enter the filename to export to (e.g., expenses.csv): ")
                expense_tracker.export_to_csv(filename)
            elif choice == '4':
                print("Exiting the Expense Tracker App. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    if __name__ == "__main__":
        main()

#War card game
def war():
    pscore = 0
    aiscore = 0
    cardlist = {
        '2 of Spades': 2,
        '2 of Hearts': 2,
        '2 of Clubs': 2,
        '2 of Diamonds': 2,
        '3 of Spades': 3,
        '3 of Hearts': 3,
        '3 of Clubs': 3,
        '3 of Diamonds': 3,
        '4 of Spades': 4,
        '4 of Hearts': 4,
        '4 of Clubs': 4,
        '4 of Diamonds': 4,
        '5 of Spades': 5,
        '5 of Hearts': 5,
        '5 of Clubs': 5,
        '5 of Diamonds': 5,
        '6 of Spades': 6,
        '6 of Hearts': 6,
        '6 of Clubs': 6,
        '6 of Diamonds': 6,
        '7 of Spades': 7,
        '7 of Hearts': 7,
        '7 of Clubs': 7,
        '7 of Diamonds': 7,
        '8 of Spades': 8,
        '8 of Hearts': 8,
        '8 of Clubs': 8,
        '8 of Diamonds': 8,
        '9 of Spades': 9,
        '9 of Hearts': 9,
        '9 of Clubs': 9,
        '9 of Diamonds': 9,
        '10 of Spades': 10,
        '10 of Hearts': 10,
        '10 of Clubs': 10,
        '10 of Diamonds': 10,
        'Jack of Spades': 11,
        'Jack of Hearts': 11,
        'Jack of Clubs': 11,
        'Jack of Diamonds': 11,
        'Queen of Spades': 12,
        'Queen of Hearts': 12,
        'Queen of Clubs': 12,
        'Queen of Diamonds': 12,
        'King of Spades': 13,
        'King of Hearts': 13,
        'King of Clubs': 13,
        'King of Diamonds': 13,
        'Ace of Spades': 1,
        'Ace of Hearts': 1,
        'Ace of Clubs': 1,
        'Ace of Diamonds': 1
    }

    def pdraw():
        time.sleep(0.2)
        pcard = random.choice(list(cardlist.keys()))
        pvalue = cardlist[pcard]
        print(f"You drew a {pcard}")
        del cardlist[pcard]
        return pvalue

    def aidraw():
        time.sleep(0.2)
        aicard = random.choice(list(cardlist.keys()))
        aivalue = cardlist[aicard]
        print(f"The opponent drew a {aicard}")
        del cardlist[aicard]
        return aivalue

    def play():
        nonlocal pscore, aiscore
        pvalue = pdraw()
        aivalue = aidraw()
        time.sleep(2.5)
        if pvalue < aivalue:
            aiscore += 1
            print("Opponent wins this round!")
        elif pvalue > aivalue:
            pscore += 1
            print("You win this round!")
        else:
            print("Tied round.")

    while len(cardlist) != 0:
        play()
    if pscore < aiscore:
        print("You lose!")
    elif pscore > aiscore:
        print("You win!")
    else:
        print("It's a tie.")
#notes
notes = []
def addnote():
    addnotes = input("Add your note: ")
    notes.append(addnotes)
    print("Note added successfully.")

def viewnote():
    if not notes:
        print("No notes")
        return
    clear_screen()
    for i, note in enumerate(notes, 1):
        print(f"{i}. {note}")

def deletenote():
    if not notes:
        print("No notes")
        return
    viewnote()
    delete = int(input("Enter the number of which note you want to delete: "))
    if 1 <= delete <= len(notes):
        del notes[delete - 1]
        print("Note deleted successfully.")
    else:
        print("Invalid note number. Returning to home.")

def clear_screen():
    print("")

def note():
    action = input("Add note, view note, delete note: ").lower()
    if action not in ["add note", "view note", "delete note"]:
        print("Invalid input. Returning to home.")
    else:
        if action == "add note":
            addnote()
        elif action == "view note":
            viewnote()
        elif action == "delete note":
            deletenote()
        else:
            print("Invalid input. Returning to home.")

#clock
def clock():
    print(time.ctime())

#info
def info():
    print("""
    Type ‘calculator’ for the calculator function
    Type ‘war’ for the war game
    Type 'expenses' for the expenses Tracker
    Type 'note' for the notepad
    Type 'magic8' for a magic 8 ball simulation
    Type 'dice' for the dice simulation
    Type 'merge sorter' for the merge sorter function
    Type 'roshambo' for the rock paper scisors function
    Type 'coin' for the coin flip simulation
    Type 'date pick' for the date picker
    Type 'blackjack' for the solo-blackjack simulation
    Type 'pyinpy' for python in python (pyin.py)
    Type 'time' for the time
    Type 'nmgsr' for the Number Guesser game
    Type 'www' for the web browser function
    Type 'dungeon' to play Dungeon Masters!!!""")

def www():
    webbrowser.open("https://" + input("""
    ⬇ Type or copy paste url here ⬇
    """))

#version
def version():
    print("""
Version v2.6 (version.update)
Produced by StarShot Studios with help from openai's chatGPT software and NAC.
    Programmers include:
    Sailas de Kok AWC (primary programmer)
    Luke Guererro RFP (secondary programmer)
    Aiden Kelly RFP (secondary programmer)
    Anay Verma? N/A (secondary programmer)
    
    AWC = Active With Coding
    RFP = Retired from Coding
    N/A = Status Not Avalable

Ag@m is a text-based operating system programmed in Python and designed for ease of use and the ability to preform use in an online interpiter.
Would you like to view the changelog? (y/n)""")
    view_chnglg = input()
    if view_chnglg == 'y':
        print("""
1.1 alpha: info and version added.
1.2 alpha: expenses Tracker, war game, and calculator added.
1.3 alpha: magic 8 ball added.
1.4 alpha: dice and merge sorter added.
1.5 alpha: rock, paper, scissors/roshambo added.
2.1 beta: logo and intro added.
2.2 beta: bug fixes.
2.3 beta: added coinflip and random date picker.
2.4 beta: updated date picker and bug fixes.
2.5 beta: date picker fixed.
2.6 beta: pyin.py and blackjack added.
2.7 beta: clock added and bugfixes.
2.8 beta: www added and bug fixes.
2.9 beta: number gusser added and WWW bugfixes
2.10 beta: more credits (yay), number gusser bugfixes, and calculator upgrade and rename
2.11 beta: wildly experimental Dungeon Masters added""")
    elif view_chnglg != 'n' or 'y':
        print("Invalid input. Returning to home.")

#main
def main_loop():
    while run:
        agam(input(""))

print("""
Welcome to Ag@m!
type 'info' for how to use Ag@m
type 'version' for info on Ag@m
or, start typing if you already know what to do!""")

def agam(inpt):
    if inpt == "info":
        info()
    elif inpt == "version":
        version()
    elif inpt == "war":
        war()
    elif inpt == "expenses":
        expenses()
    elif inpt == "calculator":
        calc()
    elif inpt == "magic8":
        magic8()
    elif inpt == "dice":
        dice()
    elif inpt == "merge sorter":
        merge_sort()
    elif inpt == "roshambo":
        rps()
    elif inpt == "coin":
        coin()
    elif inpt == "date pick":
        datepc()
    elif inpt == "blackjack":
        if __name__ == "__main__":
            blackjack = Blackjack()
            blackjack.run()
        else:
            print("Simulation failed. Returning to home.")
    elif inpt == "pyinpy":
        pyinpy()
    elif inpt == "time":
        clock()
    elif inpt == "www":
        www()
    elif inpt == "nmgsr":
        numbergussr()
    elif inpt == "dungeon":
        dngnmstrz()
    else:
        print("invalid input")

main_loop()
