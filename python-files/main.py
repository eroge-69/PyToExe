# durak_game.py

import random
from colorama import init, Fore, Style

init(autoreset=True)

# Константи
RANKS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
SUIT_COLORS = {'♠': Fore.WHITE, '♣': Fore.GREEN, '♥': Fore.RED, '♦': Fore.MAGENTA}

# Допоміжні функції
def format_card(card):
    rank, suit = card
    return SUIT_COLORS[suit] + rank + suit + Style.RESET_ALL

def card_value(card):
    return RANKS.index(card[0])

def beats(def_card, att_card, trump_suit):
    if def_card[1] == att_card[1]:
        return card_value(def_card) > card_value(att_card)
    elif def_card[1] == trump_suit and att_card[1] != trump_suit:
        return True
    return False

def print_hand(hand, label="Ваші карти"):
    print(f"\n{Style.BRIGHT}{label}:{Style.RESET_ALL}")
    for i, card in enumerate(hand):
        print(f"  {i+1}: {format_card(card)}")
    print()

def find_lowest_trump(hand, trump_suit):
    trumps = [card for card in hand if card[1] == trump_suit]
    return min(trumps, key=card_value) if trumps else None

def draw_cards(hand, count, deck):
    while len(hand) < count and deck:
        hand.append(deck.pop())

def initialize_game():
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    trump_card = deck[-1]
    trump_suit = trump_card[1]
    player_hand = []
    computer_hand = []
    draw_cards(player_hand, 6, deck)
    draw_cards(computer_hand, 6, deck)

    player_trump = find_lowest_trump(player_hand, trump_suit)
    computer_trump = find_lowest_trump(computer_hand, trump_suit)
    player_turn = True if player_trump and (not computer_trump or card_value(player_trump) < card_value(computer_trump)) else False

    return deck, trump_suit, player_hand, computer_hand, player_turn

# Основна гра
def play():
    deck, trump_suit, player_hand, computer_hand, player_turn = initialize_game()
    print(f"\nКозир: {SUIT_COLORS[trump_suit]}{trump_suit}{Style.RESET_ALL}")

    while True:
        if not player_hand and not deck:
            print(Fore.GREEN + "\n🎉 Ви перемогли!")
            break
        if not computer_hand and not deck:
            print(Fore.RED + "\n🤖 Комп’ютер переміг!")
            break

        print_hand(player_hand)

        if player_turn:
            # Гравець атакує
            while True:
                try:
                    move = int(input(Fore.CYAN + "Оберіть карту для атаки (номер): ")) - 1
                    if 0 <= move < len(player_hand):
                        attack_card = player_hand.pop(move)
                        print(f"🗡️ Ви атакуєте: {format_card(attack_card)}")
                        break
                except ValueError:
                    continue

            # Комп’ютер захищається
            defend_card = None
            for card in computer_hand:
                if beats(card, attack_card, trump_suit):
                    defend_card = card
                    break

            if defend_card:
                computer_hand.remove(defend_card)
                print(f"🛡️ Комп’ютер відбився: {format_card(defend_card)}")
                player_turn = False
            else:
                print(Fore.YELLOW + "📥 Комп’ютер не відбився й бере карту.")
                computer_hand.append(attack_card)
                player_turn = True

        else:
            # Комп’ютер атакує
            attack_card = min(computer_hand, key=lambda c: (c[1] != trump_suit, card_value(c)))
            computer_hand.remove(attack_card)
            print(f"🤖 Комп’ютер атакує: {format_card(attack_card)}")

            # Гравець захищається
            defend_options = [card for card in player_hand if beats(card, attack_card, trump_suit)]
            if defend_options:
                print_hand(player_hand)
                while True:
                    try:
                        move = int(input(Fore.CYAN + "Чим будете захищатись (номер): ")) - 1
                        if 0 <= move < len(player_hand):
                            defend_card = player_hand[move]
                            if beats(defend_card, attack_card, trump_suit):
                                player_hand.pop(move)
                                print(f"🛡️ Ви відбились: {format_card(defend_card)}")
                                break
                            else:
                                print(Fore.RED + "⛔ Ця карта не може бити!")
                    except:
                        continue
                player_turn = True
            else:
                print(Fore.RED + "📥 Ви не можете відбитись. Берете карту.")
                player_hand.append(attack_card)
                player_turn = False

        # Добір карт
        draw_cards(player_hand, 6, deck)
        draw_cards(computer_hand, 6, deck)
        print(Fore.LIGHTBLACK_EX + f"[У колоді залишилось {len(deck)} карт]")

if __name__ == "__main__":
    print(Fore.YELLOW + Style.BRIGHT + "\n🃏 Ласкаво просимо в гру 'Дурак'!\n")
    play()

