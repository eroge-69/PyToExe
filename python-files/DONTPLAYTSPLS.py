import tkinter as tk
import random

suits = ['♠', '♥', '♦', '♣']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

def draw_card():
    value = random.choice(list(values.keys()))
    suit = random.choice(suits)
    return f"{value}{suit}", values[value]

def calculate_hand(hand):
    total = sum(card[1] for card in hand)
    aces = sum(1 for card in hand if card[0].startswith('A'))
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def deal():
    global player_hand, dealer_hand
    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card()]
    result_label.config(text="")
    update_display()

def hit():
    player_hand.append(draw_card())
    if calculate_hand(player_hand) > 21:
        result_label.config(text="You Busted! Dealer Wins.")
    update_display()

def stand():
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(draw_card())
    player_total = calculate_hand(player_hand)
    dealer_total = calculate_hand(dealer_hand)
    if dealer_total > 21:
        result_label.config(text="The Dealer Busted. You Win!")
    elif player_total > dealer_total:
        result_label.config(text="You Win!")
    elif player_total < dealer_total:
        result_label.config(text="Dealer Wins.")
    else:
        result_label.config(text="It's a Tie!")
    update_display()

def update_display():
    player_cards = " ".join(card[0] for card in player_hand)
    dealer_cards = " ".join(card[0] for card in dealer_hand)
    player_label.config(text=f"Player: {player_cards} ({calculate_hand(player_hand)})")
    dealer_label.config(text=f"Dealer: {dealer_cards} ({calculate_hand(dealer_hand)})")

root = tk.Tk()
root.title("Blackjack")
root.geometry("400x200")

player_hand = []
dealer_hand = []

player_label = tk.Label(root, text="Player: ", font=("Arial", 14))
player_label.pack()

dealer_label = tk.Label(root, text="Dealer: ", font=("Arial", 14))
dealer_label.pack()

result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack()

deal_button = tk.Button(root, text="Deal💰", command=deal, font=("Arial", 12))
deal_button.pack()

hit_button = tk.Button(root, text="Hit🃏", command=hit, font=("Arial", 12))
hit_button.pack()

stand_button = tk.Button(root, text="Pass❎", command=stand, font=("Arial", 12))
stand_button.pack()

root.mainloop()
