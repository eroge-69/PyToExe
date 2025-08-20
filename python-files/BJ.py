import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import winsound  # Only works on Windows; for other OS, this will need to be replaced or removed.

# --- Constants ---
DECK_COUNT = 6
RESHUFFLE_PENETRATION = 0.75  # Reshuffle when 75% of the deck is used
SUITS = {'♠': 'black', '♥': 'red', '♦': 'red', '♣': 'black'}
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_VALUES = {r: 10 if r in ['10', 'J', 'Q', 'K'] else (11 if r == 'A' else int(r)) for r in RANKS}
HI_LO_VALUES = {'2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
                '7': 0, '8': 0, '9': 0,
                '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1}

class Card:

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = CARD_VALUES[rank]
        self.color = SUITS[suit]

    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:

    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        self.cards = [Card(rank, suit) for _ in range(DECK_COUNT) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop() if self.cards else None


class BlackjackGame:

    def __init__(self, master):
        self.master = master
        self.deck = Deck()
        self.running_count = 0
        self.true_count = 0.0
        self.bet = 0
        
        self.token_amount = simpledialog.askinteger("Starting Tokens",
                                                    "Enter your starting token amount:",
                                                    minvalue=1,
                                                    initialvalue=100) or 100

        self.player_hands = []
        self.current_hand_index = 0
        self.dealer_hand = []
        self.dealer_hole_card = None

        self.view = GameView(master, self)
        self.view.update_tokens(self.token_amount)
        self.view.update_counts(self.running_count, self.true_count)
        self.in_round = False

    def play_sound(self, sound_type):
        try:
            frequency = 750
            duration = 100
            if sound_type == 'deal':
                winsound.Beep(frequency, duration)
            elif sound_type == 'win':
                winsound.Beep(1000, 300)
            elif sound_type == 'loss':
                winsound.Beep(400, 300)
            elif sound_type == 'blackjack':
                winsound.Beep(1200, 400)
            elif sound_type == 'bust':
                winsound.Beep(300, 400)
        except ImportError:
            pass

    def start_round(self):
        if self.in_round:
            self.view.update_message("Finish the current round first.")
            return

        try:
            bet = int(self.view.bet_entry.get())
        except ValueError:
            self.view.update_message("Invalid bet. Please use numbers only.")
            return

        if not (0 < bet <= self.token_amount):
            self.view.update_message("Invalid bet amount.")
            return

        if len(self.deck.cards) < (52 * DECK_COUNT * (1 - RESHUFFLE_PENETRATION)):
            self.deck.build()
            self.running_count = 0
            self.view.update_message("Reshuffling the shoe...")
            self.view.update_counts(self.running_count, 0)
            self.master.after(1500, self.start_round)
            return
        
        self.in_round = True
        self.bet = bet
        self.token_amount -= bet
        self.view.update_tokens(self.token_amount)
        self.view.set_game_state(in_progress=True)

        self.player_hands = [[]]
        self.dealer_hand = []
        self.current_hand_index = 0

        self.deal_card_to_player(self.player_hands[0])
        self.dealer_hole_card = self.deck.deal()
        self.deal_card_to_player(self.player_hands[0])
        self.deal_card_to_dealer(is_visible=True)

        self.view.display_all_hands(self.player_hands, self.current_hand_index, self.dealer_hand, self.dealer_hole_card)
        self.view.update_message("Your move. Good luck!")

        player_score = self.calculate_score(self.player_hands[0])
        if player_score == 21:
            self.reveal_dealer_hole_card()
            dealer_score = self.calculate_score(self.dealer_hand)
            if dealer_score == 21:
                self.end_round("push", "Push: Both have Blackjack!")
            else:
                payout = self.bet * 1.5
                self.end_round("blackjack", f"Blackjack! You win {int(payout)} tokens.", payout)
            self.play_sound('blackjack')
        else:
            self.update_buttons()

    def update_buttons(self):
        can_split_flag = self.can_split(self.player_hands[self.current_hand_index]) and \
                         len(self.player_hands) < 4 and \
                         self.token_amount >= self.bet
        self.view.enable_buttons(hit=True, stand=True, split=can_split_flag)

    def deal_card_to_player(self, hand):
        card = self.deck.deal()
        if card:
            hand.append(card)
            self.update_counts(card)
            self.play_sound('deal')

    def deal_card_to_dealer(self, is_visible=True):
        card = self.deck.deal()
        if card:
            self.dealer_hand.append(card)
            if is_visible:
                self.update_counts(card)
            self.play_sound('deal')

    def reveal_dealer_hole_card(self):
        if self.dealer_hole_card:
            self.dealer_hand.append(self.dealer_hole_card)
            self.update_counts(self.dealer_hole_card)
            self.dealer_hole_card = None
            self.view.display_all_hands(self.player_hands, self.current_hand_index, self.dealer_hand, None)


    def update_counts(self, card):
        self.running_count += HI_LO_VALUES[card.rank]
        decks_remaining = len(self.deck.cards) / 52
        self.true_count = self.running_count / decks_remaining if decks_remaining > 0 else 0
        self.view.update_counts(self.running_count, self.true_count)

    @staticmethod
    def calculate_score(hand):
        total = sum(card.value for card in hand)
        aces = sum(1 for card in hand if card.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def hit(self):
        current_hand = self.player_hands[self.current_hand_index]
        self.deal_card_to_player(current_hand)
        score = self.calculate_score(current_hand)
        
        self.view.display_all_hands(self.player_hands, self.current_hand_index, self.dealer_hand, self.dealer_hole_card)
        
        if score > 21:
            self.play_sound('bust')
            self.view.update_message(f"Hand {self.current_hand_index + 1} busts!")
            self.next_hand_or_dealer()
        elif score == 21:
             self.stand()
        else:
            self.update_buttons()

    def stand(self):
        self.view.update_message(f"You stand on hand {self.current_hand_index + 1}.")
        self.next_hand_or_dealer()

    def can_split(self, hand):
        return len(hand) == 2 and hand[0].rank == hand[1].rank

    def split(self):
        current_hand = self.player_hands[self.current_hand_index]
        if not self.can_split(current_hand):
            self.view.update_message("Cannot split this hand.")
            return
        if self.token_amount < self.bet:
            self.view.update_message("Insufficient tokens to split.")
            return

        self.token_amount -= self.bet
        self.view.update_tokens(self.token_amount)

        card_to_move = current_hand.pop()
        new_hand = [card_to_move]
        self.player_hands.insert(self.current_hand_index + 1, new_hand)

        self.deal_card_to_player(current_hand)
        self.deal_card_to_player(new_hand)

        self.view.update_message(f"Hand split. Now playing hand {self.current_hand_index + 1}.")
        self.view.display_all_hands(self.player_hands, self.current_hand_index, self.dealer_hand, self.dealer_hole_card)
        self.update_buttons()

    def next_hand_or_dealer(self):
        self.current_hand_index += 1
        if self.current_hand_index < len(self.player_hands):
            self.view.update_message(f"Playing hand {self.current_hand_index + 1}")
            self.view.display_all_hands(self.player_hands, self.current_hand_index, self.dealer_hand, self.dealer_hole_card)
            self.update_buttons()
        else:
            self.dealer_play()

    def dealer_play(self):
        self.view.enable_buttons(hit=False, stand=False, split=False)
        self.reveal_dealer_hole_card()

        while self.calculate_score(self.dealer_hand) < 17:
            self.master.after(500)
            self.deal_card_to_dealer(is_visible=True)
            self.view.display_all_hands(self.player_hands, -1, self.dealer_hand, None)
            self.master.update()

        self.determine_winner()

    def determine_winner(self):
        dealer_score = self.calculate_score(self.dealer_hand)
        results = []
        total_payout = 0
        
        for idx, hand in enumerate(self.player_hands):
            player_score = self.calculate_score(hand)
            if player_score > 21:
                results.append(f"Hand {idx+1} busts. You lose.")
                self.play_sound('loss')
            elif dealer_score > 21:
                results.append(f"Dealer busts. Hand {idx+1} wins!")
                total_payout += self.bet * 2
                self.play_sound('win')
            elif player_score > dealer_score:
                results.append(f"Hand {idx+1} wins!")
                total_payout += self.bet * 2
                self.play_sound('win')
            elif player_score == dealer_score:
                results.append(f"Hand {idx+1} is a push.")
                total_payout += self.bet
            else:
                results.append(f"Dealer wins against hand {idx+1}.")
                self.play_sound('loss')
        
        final_message = "\n".join(results)
        self.end_round("multi", final_message, total_payout)

    def end_round(self, result, message, payout_amount=0):
        if result == "blackjack":
            self.token_amount += self.bet + payout_amount
        elif result == "multi":
             self.token_amount += payout_amount
        elif result == "push":
            self.token_amount += self.bet

        self.view.update_tokens(self.token_amount)
        self.view.update_message(message)
        self.view.set_game_state(in_progress=False)
        self.in_round = False

        if self.token_amount <= 0:
            messagebox.showinfo("Game Over", "You've run out of tokens! Better luck next time.")
            # Automatically retry by resetting tokens and starting a new game
            self.token_amount = simpledialog.askinteger("Retry", "Enter your new starting token amount:", minvalue=1, initialvalue=100) or 100
            self.view.update_tokens(self.token_amount)
            self.deck.build()
            self.running_count = 0
            self.true_count = 0.0
            self.view.update_counts(self.running_count, self.true_count)
            self.in_round = False
            self.view.set_game_state(in_progress=False)
            self.view.update_message("Place your bet and press 'Deal' to play again.")


class GameView:

    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.master.title("Blackjack")
        
        self.bg_color = "#004d00"
        self.frame_bg_color = "#003300"
        self.button_green = "#43A047"
        self.font_main = ("Helvetica", 14, "bold")
        self.font_small = ("Helvetica", 12)
        self.card_bg = "#FFFFFF"
        self.red_color = "#D32F2F"
        self.black_color = "#212121"

        self.master.configure(bg=self.bg_color)

        info_frame = tk.Frame(master, bg=self.bg_color)
        info_frame.pack(pady=10, padx=10, fill='x')

        self.dealer_frame = tk.LabelFrame(master, text="DEALER", fg="white", bg=self.frame_bg_color, font=self.font_main, labelanchor='n', relief=tk.RIDGE, borderwidth=2)
        self.dealer_frame.pack(padx=20, pady=(5, 15), fill='x')

        self.player_frame = tk.LabelFrame(master, text="PLAYER", fg="white", bg=self.frame_bg_color, font=self.font_main, labelanchor='n', relief=tk.RIDGE, borderwidth=2)
        self.player_frame.pack(padx=20, pady=(5, 15), fill='x', expand=True, anchor='n')

        controls_frame = tk.Frame(master, bg=self.frame_bg_color, pady=10)
        controls_frame.pack(pady=10, padx=10, fill='x', side='bottom')

        self.token_label = tk.Label(info_frame, font=self.font_main, bg=self.bg_color, fg="white")
        self.token_label.pack(side='left', padx=10)
        self.count_label = tk.Label(info_frame, font=self.font_main, bg=self.bg_color, fg="white")
        self.count_label.pack(side='right', padx=10)

        self.dealer_score_label = tk.Label(self.dealer_frame, font=self.font_small, bg=self.frame_bg_color, fg="white", anchor='w')
        self.dealer_score_label.pack(anchor='w', padx=10)
        self.dealer_cards_frame = tk.Frame(self.dealer_frame, bg=self.frame_bg_color)
        self.dealer_cards_frame.pack(pady=5)

        self.player_hand_containers = []
        for i in range(4):
            container = {}
            container['main_frame'] = tk.Frame(self.player_frame, bg=self.frame_bg_color, pady=5)
            container['score_label'] = tk.Label(container['main_frame'], font=self.font_small, bg=self.frame_bg_color, fg="white")
            container['score_label'].pack(anchor='w')
            container['cards_frame'] = tk.Frame(container['main_frame'], bg=self.frame_bg_color)
            container['cards_frame'].pack(anchor='w')
            self.player_hand_containers.append(container)

        bet_frame = tk.Frame(controls_frame, bg=self.frame_bg_color)
        bet_frame.pack(side='left', padx=10)
        action_frame = tk.Frame(controls_frame, bg=self.frame_bg_color)
        action_frame.pack(side='right', padx=10)

        bet_label = tk.Label(bet_frame, text="Bet:", font=self.font_main, bg=self.frame_bg_color, fg="white")
        bet_label.pack(side='left', padx=(10, 5))

        self.bet_entry = tk.Entry(bet_frame, width=8, justify='center', font=self.font_main)
        self.bet_entry.insert(0, "10")
        self.bet_entry.pack(side='left')

        self.deal_button = tk.Button(bet_frame, text="Deal", command=self.controller.start_round, bg=self.button_green, fg="white",
                                     font=self.font_main, activebackground="#66BB6A")
        self.deal_button.pack(side='left', padx=15)

        self.hit_button = tk.Button(action_frame, text="Hit", command=self.controller.hit, state=tk.DISABLED,
                                    bg="#1E88E5", fg="white", font=self.font_main, activebackground="#42A5F5")
        self.hit_button.pack(side='left', padx=5)

        self.stand_button = tk.Button(action_frame, text="Stand", command=self.controller.stand, state=tk.DISABLED,
                                      bg="#E53935", fg="white", font=self.font_main, activebackground="#EF5350")
        self.stand_button.pack(side='left', padx=5)

        self.split_button = tk.Button(action_frame, text="Split", command=self.controller.split, state=tk.DISABLED,
                                      bg="#FBC02D", fg="black", font=self.font_main, activebackground="#FFEB3B")
        self.split_button.pack(side='left', padx=5)

        self.message_label = tk.Label(master, text="Place your bet and press 'Deal'", font=("Helvetica", 12, "italic"),
                                      bg=self.bg_color, fg="#FFC107")
        self.message_label.pack(pady=10, side='bottom')

    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def display_all_hands(self, player_hands, current_index, dealer_hand, dealer_hole_card):
        self._clear_frame(self.dealer_cards_frame)
        for card in dealer_hand:
            self.create_card_widget(self.dealer_cards_frame, card).pack(side='left', padx=5)
        if dealer_hole_card:
            self.create_card_back(self.dealer_cards_frame).pack(side='left', padx=5)
            self.dealer_score_label.config(text=f"Dealer Score: {self.controller.calculate_score(dealer_hand)}")
        else:
            self.dealer_score_label.config(text=f"Dealer Score: {self.controller.calculate_score(dealer_hand)}")

        for i in range(4):
            container = self.player_hand_containers[i]
            if i < len(player_hands):
                container['main_frame'].pack(anchor='w', padx=10, pady=3, fill='x')
                hand = player_hands[i]
                score = self.controller.calculate_score(hand)
                is_current = (i == current_index)
                
                self._clear_frame(container['cards_frame'])
                for card in hand:
                    self.create_card_widget(container['cards_frame'], card).pack(side='left', padx=5)
                
                score_text = f"Hand {i+1} Score: {score}"
                if is_current and self.controller.in_round:
                    container['score_label'].config(text=score_text + "  <--", fg="#FFEB3B")
                else:
                    container['score_label'].config(text=score_text, fg="white")
            else:
                container['main_frame'].pack_forget()

    def create_card_widget(self, parent_frame, card):
        card_frame = tk.Frame(parent_frame, relief="raised", borderwidth=2, bg=self.card_bg, width=60, height=90)
        card_frame.pack_propagate(False)
        fg_color = self.red_color if card.color == 'red' else self.black_color

        tk.Label(card_frame, text=card.rank, font=("Helvetica", 16, "bold"), fg=fg_color, bg=self.card_bg).place(x=4, y=2)
        tk.Label(card_frame, text=card.suit, font=("Helvetica", 18), fg=fg_color, bg=self.card_bg).place(relx=0.5, rely=0.5, anchor="center")
        
        return card_frame

    def create_card_back(self, parent_frame):
        card_frame = tk.Frame(parent_frame, relief="raised", borderwidth=2, bg="#1565C0", width=60, height=90)
        card_frame.pack_propagate(False)
        tk.Label(card_frame, text="?", font=("Helvetica", 36, "bold"), fg="yellow", bg="#1565C0").place(relx=0.5, rely=0.5, anchor="center")
        return card_frame

    def update_tokens(self, amount):
        self.token_label.config(text=f"Tokens: {amount}")

    def update_counts(self, running, true):
        self.count_label.config(text=f"Count: {running} | True: {true:.2f}")

    def update_message(self, text):
        self.message_label.config(text=text)

    def set_game_state(self, in_progress):
        deal_state = tk.DISABLED if in_progress else tk.NORMAL
        action_state = tk.NORMAL if in_progress else tk.DISABLED
        bet_state = "disabled" if in_progress else "normal"

        self.hit_button.config(state=action_state)
        self.stand_button.config(state=action_state)
        self.split_button.config(state=action_state)
        self.deal_button.config(state=deal_state)
        self.bet_entry.config(state=bet_state)

    def enable_buttons(self, hit=True, stand=True, split=False):
        self.hit_button.config(state=tk.NORMAL if hit else tk.DISABLED)
        self.stand_button.config(state=tk.NORMAL if stand else tk.DISABLED)
        self.split_button.config(state=tk.NORMAL if split else tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    game = BlackjackGame(root)
    root.mainloop()
