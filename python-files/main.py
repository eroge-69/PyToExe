import random
from itertools import zip_longest
import time
from datetime import datetime
import os
import json
import ast

def clear_console():
    """Clears the console screen."""
    # Check the operating system
    if os.name == 'nt':  # For Windows
        _ = os.system('cls')
    else:  # For macOS and Linux
        _ = os.system('clear')


# Deck of cards with their values set for blackjack, Aces will be changed to ones if necessary later when user is playing
cards = {
    "Ace of Spades": 11,
    "Two of Spades": 2,
    "Three of Spades": 3,
    "Four of Spades": 4,
    "Five of Spades": 5,
    "Six of Spades": 6,
    "Seven of Spades": 7,
    "Eight of Spades": 8,
    "Nine of Spades": 9,
    "Ten of Spades": 10,
    "Jack of Spades": 10,
    "Queen of Spades": 10,
    "King of Spades":10,

    "Ace of Clubs": 11,
    "Two of Clubs": 2,
    "Three of Clubs": 3,
    "Four of Clubs": 4,
    "Five of Clubs": 5,
    "Six of Clubs": 6,
    "Seven of Clubs": 7,
    "Eight of Clubs": 8,
    "Nine of Clubs": 9,
    "Ten of Clubs": 10,
    "Jack of Clubs": 10,
    "Queen of Clubs": 10,
    "King of Clubs":10,

    "Ace of Diamonds": 11,
    "Two of Diamonds": 2,
    "Three of Diamonds": 3,
    "Four of Diamonds": 4,
    "Five of Diamonds": 5,
    "Six of Diamonds": 6,
    "Seven of Diamonds": 7,
    "Eight of Diamonds": 8,
    "Nine of Diamonds": 9,
    "Ten of Diamonds": 10,
    "Jack of Diamonds": 10,
    "Queen of Diamonds": 10,
    "King of Diamonds":10,

    "Ace of Hearts": 11,
    "Two of Hearts": 2,
    "Three of Hearts": 3,
    "Four of Hearts": 4,
    "Five of Hearts": 5,
    "Six of Hearts": 6,
    "Seven of Hearts": 7,
    "Eight of Hearts": 8,
    "Nine of Hearts": 9,
    "Ten of Hearts": 10,
    "Jack of Hearts": 10,
    "Queen of Hearts": 10,
    "King of Hearts":10,
}
loaded = False
Betting = True

# The Player object which will store values like how much money the player has and which cards they have
class Player:
    def __init__(self):
        self.hand = {}
        self.key_names = []
        self.money = 1000
        self.bet = 0
        self.name = ""

# The Dealer object with will store which cards the dealer has
class Dealer:
    def __init__(self):
        self.hand = {}
        self.key_names = []
        
# The Dealer will give snarky comments while the player is playing and this function stores and returns those comments 
def dealer_comment(player, dealer, total, dtotal):
    return "Hi :3"

# Returns the name of a card both to use in print commands and to assign a card as a key for the cards dictionary
def dealCard(cards_dict, n=0):
    if n < 0:
        n += len(cards_dict)
    for i, key in enumerate(cards_dict.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")

# Runs before each round, deals two cards both to the dealer and the player
# and makes the player place their bet and shows how much money they have left after the bet
def dealHand(player, dealer):
    player.hand = {}

    # deal card to player
    player.hand[dealCard(available_cards,random.randint(0, len(available_cards) - 1))] = 0
    #TODO remove when done testing
    #player.hand[dealCard(available_cards, 0)] = 0


    # assign value to player's card and remove card from available cards
    player.key_names = []
    for key in player.hand:
        player.key_names.append(key)
    player.hand[player.key_names[0]] = cards[player.key_names[0]]
    del available_cards[player.key_names[0]]

    # deal card to player
    player.hand[dealCard(available_cards, random.randint(0, len(available_cards) - 1))] = 0

    # assign value to player's card and remove card from available cards
    player.key_names = []
    for key in player.hand:
        player.key_names.append(key)
    player.hand[player.key_names[1]] = cards[player.key_names[1]]
    del available_cards[player.key_names[1]]

    dealer.hand = {}

    # deal card to the dealer
    dealer.hand[dealCard(available_cards, random.randint(0, len(available_cards) - 1))] = 0

    # assign value to dealer's card and remove card from available cards
    dealer.key_names = []
    for key in dealer.hand:
        dealer.key_names.append(key)
    dealer.hand[dealer.key_names[0]] = cards[dealer.key_names[0]]
    del available_cards[dealer.key_names[0]]

    #deal card to the dealer
    dealer.hand[dealCard(available_cards, random.randint(0, len(available_cards) - 1))] = 0

    # assign values to the dealer's card and remove card from available cards
    dealer.key_names = []
    for key in dealer.hand:
        dealer.key_names.append(key)
    dealer.hand[dealer.key_names[1]] = cards[dealer.key_names[1]]
    del available_cards[dealer.key_names[1]]

# The Round of play, handles everything from getting blackjack to busting to the dealer getting either
def playRound(player, dealer, round):
    round_over = False
    player_stayed = False

    if player.bet == 0:
        clear_console()
        print(f"########## Round {round} ##########\n"
              "Your cards are:               Dealer's cards are:")
        pcards_list = []
        dcards_list = []
        for card in dealer.hand:
            dcards_list.append("The " + card)
        for card in player.hand:
            pcards_list.append("The " + card)
        if not player_stayed:
            dcards_list[0] = "The ???"
        cards_list = []
        for pcards, dcards in zip_longest(pcards_list, dcards_list, fillvalue=""):
            cards_list.append(f"{pcards:<29} {dcards}")
        for line in cards_list:
            print(line)

    # have player place a bet, min bet has to be at least 1/5 of the player's balance
    betting = True
    while betting:
        # finds the total value of the player's cards
        #TODO Needs Better Placement
        total = 0
        for card in player.hand:
            total += player.hand[card]
        if total == 21:
            player.bet = player.money/5
            betting = False
        else:
            if player.bet == 0:
                try:

                    print(f"You have ${player.money}, how much would you like to bet? You have to bet at least ${player.money/5}:")
                    bchoice = input()
                    bchoice = bchoice.replace(",", "")

                    if bchoice.upper().split(" ")[0] == "SAVE":
                        data = {
                            "save": f"{player.name} {datetime.now()}",
                            "phand": player.key_names,
                            "money": player.money,
                            "bet": player.bet,
                            "name": player.name,
                            "dhand": dealer.key_names,
                            "round": round
                        }
                        with open("data/saves.json", "r") as f:
                            jdata = json.load(f)
                        jdata.append(data)
                        with open("data/saves.json", "w") as f:
                            json.dump(jdata, f ,indent=4)
                        continue
                    elif int(bchoice) > player.money:
                        print("### You Don't Have That Much Money.. Nice Try Tho ###")
                        continue
                    elif int(bchoice) < player.money/5:
                        print("### You Have To Bet More Than That.. Can't You Read? ###")
                        continue
                    else:
                        player.bet = int(bchoice)
                        betting = False
                except ValueError:
                    print(f"### You Typed '{bchoice}'... We Bet With Money Here.. ###")
            else:
                betting = False

    if not loaded:
        player.money -= player.bet

    while not round_over:


        clear_console()
        print(f"########## Round {round} ##########\n"
              "Your cards are:               Dealer's cards are:")
        pcards_list = []
        dcards_list = []
        for card in dealer.hand:
            dcards_list.append("The " + card)
        for card in player.hand:
            pcards_list.append("The " + card)
        if not player_stayed:
            dcards_list[0] = "The ???"
        cards_list = []
        for pcards, dcards in zip_longest(pcards_list, dcards_list, fillvalue=""):
            cards_list.append(f"{pcards:<29} {dcards}")
        for line in cards_list:
            print(line)

        print(f"\nYour bet is ${player.bet} After the bet you have ${player.money} left")

        # finds the total value of the player's cards
        total = 0
        for card in player.hand:
            total += player.hand[card]

        # If the player's cards go over 21
        if total > 21:
            i = 0
            while True:
                # convert aces from 11 to 1 until either the total is < 21 or there are no more aces
                while total > 21:

                    if i > len(player.key_names) - 1:
                        break
                    elif player.hand[player.key_names[i]] == 11:
                        player.hand[player.key_names[i]] = 1
                        i += 1
                    else:
                        i += 1

                    total = 0
                    for card in player.hand:
                        total += player.hand[card]

                # if there are no aces to convert to 1 and the total is still over 21 the player loses the round
                if total > 21:
                    round_over = True
                    print("#### You Bust! ####")
                    time.sleep(3)
                    break
                else:
                    break

        # if player has a blackjack they win the round
        if total == 21:
            if len(player.key_names) > 2:
                player.money += player.bet * 2
                print("#### Blackjack! ####")
                time.sleep(3)
                break
            else:
                player.money += player.bet * 2.5
                print("#### Natural Blackjack! ####")
                time.sleep(3)
                break

        # if the value of the player's cards is less than 21,
        # the player can either hit or stay
        elif total < 21:

            print(f"You're at {total} would you like to hit or stay: ")
            choice = input()

            # if player chooses to hit, deal a card and find the new total value of the player's cards
            if choice.upper() == "HIT":
                # deal card to player
                player.hand[dealCard(available_cards, random.randint(0, len(available_cards) - 1))] = 0

                # assign value to player's card and remove card from available cards
                player.key_names = []
                for key in player.hand:
                    player.key_names.append(key)
                player.hand[player.key_names[len(player.key_names) - 1]] = cards[player.key_names[len(player.key_names) - 1]]
                del available_cards[player.key_names[len(player.key_names) - 1]]

                for card in player.hand:
                    total += player.hand[card]
                continue

            # Dealers rounds of play
            elif choice.upper() == "STAY":
                dealer_wait = 2

                while not round_over:
                    dealer_total = 0
                    for card in dealer.hand:
                        dealer_total += dealer.hand[card]
                    clear_console()
                    print(f"########## Round {round} ##########\n"
                          "Your cards are:               Dealer's cards are:")
                    pcards_list = []
                    dcards_list = []
                    for card in dealer.hand:
                        dcards_list.append("The " + card)
                    for card in player.hand:
                        pcards_list.append("The " + card)
                    cards_list = []
                    for pcards, dcards in zip_longest(pcards_list, dcards_list, fillvalue=""):
                        cards_list.append(f"{pcards:<29} {dcards}")
                    for line in cards_list:
                        print(line)
                    print(f"Your total: {total}                Dealer Total: {dealer_total}")
                    time.sleep(dealer_wait)
                    dealer_wait = 2

                    if dealer_total > 21:
                        dealer_wait = 0
                        i = 0
                        while not round_over:
                            # converts aces from 11 to 1 until daler total < 21 or there are no more aces
                            while dealer_total > 21:

                                if i > len(dealer.key_names) - 1:
                                    break
                                elif dealer.hand[dealer.key_names[i]] == 11:
                                    dealer.hand[dealer.key_names[i]] = 1
                                    i += 1
                                    dealer_total = 0
                                    for card in dealer.hand:
                                        dealer_total += dealer.hand[card]
                                    continue
                                else:
                                    i += 1
                                    continue


                            # if dealer busts
                            if dealer_total > 21:
                                player.money += player.bet * 2
                                print("#### Dealer Bust! ####")
                                time.sleep(3)
                                round_over = True
                                break
                            else:
                                break

                    # if dealer gets blackjack
                    elif dealer_total == 21:
                        print("#### Dealer Blackjack! ####")
                        time.sleep(3)
                        round_over = True
                        break
                    # if dealer has higher score than player without going over 21
                    elif dealer_total > total:
                        print("#### Dealer Won! ####")
                        time.sleep(3)
                        round_over = True
                        break
                    # if dealer total equals player total
                    elif dealer_total == total:
                        player.money += player.bet
                        print("#### Push! ####")
                        time.sleep(3)
                        round_over = True
                        break
                    # if dealer needs to draw an extra card
                    elif dealer_total < total:
                        # deal card to the dealer
                        dealer.hand[dealCard(available_cards, random.randint(0, len(available_cards) - 1))] = 0

                        # assign value to dealer's card and remove card from available cards
                        dealer.key_names = []
                        for key in dealer.hand:
                            dealer.key_names.append(key)
                        dealer.hand[dealer.key_names[len(dealer.key_names) - 1]] = cards[dealer.key_names[len(dealer.key_names) - 1]]
                        del available_cards[dealer.key_names[len(dealer.key_names) - 1]]

                        dealer_total = 0
                        for card in dealer.hand:
                            dealer_total += dealer.hand[card]

                        clear_console()
                        print(f"########## Round {round} ##########\n"
                              "Your cards are:               Dealer's cards are:")
                        pcards_list = []
                        dcards_list = []
                        for card in dealer.hand:
                            dcards_list.append("The " + card)
                        for card in player.hand:
                            pcards_list.append("The " + card)
                        cards_list = []
                        for pcards, dcards in zip_longest(pcards_list, dcards_list, fillvalue=""):
                            cards_list.append(f"{pcards:<29} {dcards}")
                        for line in cards_list:
                            print(line)
                        print(f"Your total: {total}                Dealer Total: {dealer_total}")
                        time.sleep(2)
            elif choice.upper().split(" ")[0] == "SAVE":
                data = {
                    "save": f"{player.name} {datetime.now()}",
                    "bet": player.bet,
                    "phand": player.key_names,
                    "money": player.money,
                    "name": player.name,
                    "dhand": dealer.key_names,
                    "round": round
                }
                with open("data/saves.json", "r") as f:
                    jdata = json.load(f)
                jdata.append(data)
                with open("data/saves.json", "w") as f:
                    json.dump(jdata, f, indent=4)
            else:
                print("### Choose 'Hit' or 'Stay' Please ###")
                time.sleep(2)

if __name__ == "__main__":
    player = Player()
    dealer = Dealer()
    available_cards = cards.copy()
    highscore = 0
    round = 1

    print("You walk into a dimly-lit side room in the casino. The room is mostly empty except for a filing cabinet, a "
          "Blackjack table, and a well dressed but somehow still disheveled dealer snuffing out a cigarette.\n"
          "### Ah I see they've sent me another sucker ###\n"
          "The dealer looks you over with judgemental eyes.\n"
          "### Or maybe you've been here before.. I honestly never can remember ###\n"
          "(Type your name to start a new game or type 'load' to open a previous saved game):")
    player.name = input()
    if player.name.upper() == "LOAD":
        print("The dealer digs through the filing cabinet and pulls out some files\n"
              "### Ah here we go... which one of these is you? ###")
        with open('data/saves.json', 'r') as f:
            jdata = json.load(f)
        i = 1
        for list in jdata:
            print(f"{i}. {list['save']}")
            i += 1
        print("(Choose a save file by typing its number)")
        while True:
            try:
                load_choice = input()
                if int(load_choice) < 1:
                    print("### I'm afraid that file doesn't exist here in the real world ###")
                    continue
                load_choice = int(load_choice) - 1
                jdict = jdata[load_choice]
                player.key_names = jdict["phand"]
                player.money = jdict["money"]
                player.bet = jdict["bet"]
                player.name = jdict["name"]
                dealer.key_names = jdict["dhand"]
                round = jdict["round"]
                loaded = True
                break
            except (TypeError, ValueError):
                print("### Please just tell me which file is yours by saying its number.. ###")
            except IndexError:
                print("### I'm afraid that file doesn't exist here in the real world ###")

        i = 0
        while i < len(player.key_names):
            player.hand[player.key_names[i]] = cards[player.key_names[i]]
            del available_cards[player.key_names[i]]
            i += 1
        i = 0
        while i < len(dealer.key_names):
            dealer.hand[dealer.key_names[i]] = cards[dealer.key_names[i]]
            del available_cards[dealer.key_names[i]]
            i += 1


    while True:
        if player.money > highscore:
            highscore = player.money
        if player.money <= 0:
            print("###### GAME OVER ######")
            print(f"###### High Score: ${highscore}! ######")
            print(f"###### Survived For {round - 1} Rounds! ######")
            break

        if len(available_cards) < 16:
            print("#### Shuffling Cards! ####")
            time.sleep(3)
            available_cards = cards.copy()

        if not loaded:
            dealHand(player, dealer)
        playRound(player, dealer, round)
        round += 1
        loaded = False
        player.bet = 0