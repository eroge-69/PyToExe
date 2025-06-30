import random
import numpy as np
import matplotlib.pyplot as plt


class Card:
    """ a single
     card in the game."""

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        # display the card as text
        return f"{self.rank}{self.suit}"


class Deck:
    # represents a deck of cards

    def __init__(self, seed):
        self.cards = []
        self.seed = seed
    
        suits = ["♠", "♥", "♦", "♣"]
        ranks = [ "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

        for suit in suits: # create the deck 
            for rank in ranks:
                self.cards.append(Card(suit, rank))

        self.shuffle()
        

    def shuffle(self):
        random.seed(self.seed)
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop(0)


class Hand:
    """ represents a player's
    hand in Blackjack – that is, the list
    of cards currently in the player's
    hand during the game round."""

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def reset(self):
        self.cards.clear()

    def get_value(self): # calc the hand's value

        total = 0
        aces = 0

        for card in self.cards:
            if card.rank in ['J', 'Q', 'K']:
                total = total + 10
            elif card.rank == 'A':
                total = total + 11
                aces = aces + 1
            else:
                total = total + int(card.rank)
        # if we passed 21,  subtract 10 for each ace
        while total > 21 and aces > 0:
            total = total - 10
            aces = aces - 1

        return total


class Player:

    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = Hand()
        self.bet = 0

    def place_bet(self, amount):
        if amount <= 0 or amount > self.chips:
            raise ValueError(f"Please enter a number between 0 and {self.chips}.")
        self.bet = amount
        self.chips -= amount

    def add_card(self, card):
        self.hand.add_card(card)
        

    def has_bust(self):
        return self.hand.get_value() > 21

    def reset_hand(self):
        self.hand.reset()
        self.bet = 0


class BotPlayer(Player):


    def __init__(self, name, chips, seed):
        super().__init__(name, chips)
        self.seed = seed
        self.rng = random.Random(seed)

    def decide_move(self):
        if self.hand.get_value() < 17:
            return "hit"
        return "stand"

    """while bot.decide_move() == "hit":
        bot.add_card(deck.deal_card())"""

    def place_random_bet(self):
        amount = self.rng.randint(1, self.chips)
        self.place_bet(amount)


class Dealer(Player):
    # represent dealer in the game

    def __init__(self):
        super().__init__("Dealer", 0)
        self.hidden_card = None

    def set_hidden_card(self, card):
        # stores the hidden card
        self.hidden_card = card

    def reveal_hidden_card(self):
        # reveals the hidden card and adds it to the dealer's hand.
        if self.hidden_card: 
            self.hand.add_card(self.hidden_card)
            print(f"\nDealer reveals hidden card: {self.hidden_card}")
            self.hidden_card = None

    def should_draw(self):
        # determines whether the dealer should draw another card.
        return self.hand.get_value() < 17


class GameManager:
    # manage the entire blackjack game

    def __init__(self):
        
        self.name = self.get_player_name()
        self.chips = self.get_player_chips()
        self.player_sit = self.get_player_seat()
        self.seat_map = {}  # dict for seat number (1-3) -> player object 
        self.seed = None
        # load bots
        self.bots = self.load_players_from_file("BotPlayers.txt")
        for bot in self.bots:
            print(f"{bot.name} now has {bot.chips} chips.")
        bot_seats = [s for s in [1, 2, 3] if s != self.player_sit] # make sure the bot is not in the same seat as the player
        for i, bot in enumerate(self.bots):
            self.seat_map[bot_seats[i]] = bot
        self.player = Player(self.name, self.chips)
        self.seat_map[self.player_sit] = self.player
        self.dealer = Dealer()

    
        self.deck = None

        # For rebuy logic, track original chips for each bot
        for bot in self.bots:
            bot.original_chips = bot.chips
            bot.total_bought = bot.chips
        self.player.original_chips = self.player.chips
        self.player.total_bought = self.player.chips


    def get_player_name(self):
        while True:# get player name
            name = input("Enter your name: ").strip()
            if name:
                return name
            print("Name cannot be empty.")

    def get_player_chips(self):
        # get chips (100-1000)
        while True: 
            chips_input = input("Enter the amount of chips: ").strip()
            if chips_input.lstrip('-').isdigit():
                chips = int(chips_input)
                if 100 <= chips <= 1000:
                    return chips #
                else:
                    print("Please enter a number between 100 and 1000.") 
            else:
                print("Invalid input. Please enter a valid integer.")


    def get_player_seat(self):
        #   input for seat  (1-3)
        while True:
            seat_input = input("Where would you like to sit? (Choose a seat number from 1 to 3): ").strip()
            if seat_input.lstrip('-').isdigit():
                player_sit = int(seat_input) 
                if 1 <= player_sit <= 3:
                    return player_sit
                else:
                    print("Please enter a number between 1 and 3. ")
            else:
                print("Invalid input. Please enter a valid integer.")
    def get_seed(self):
        # get the seed from the user !
        print("Nothing is left to chance when you are an engineer.")
        while True:   
            input_seed = input("Enter a seed value for the game: ").strip()
            if input_seed.lstrip('-').isdigit():
                seed = int(input_seed)
                return seed 
            else:
                print("Invalid input. Please enter a valid integer.")

    def load_players_from_file(self, path):                                                   
        # lod bot players from a file
        bot_players = []
        try:
            with open(path, "r") as file:
                for line in file:
                    name, chips, bot_seed = line.strip().split(",")
                    bot_players.append(BotPlayer(name, int(chips), int(bot_seed)))
        except FileNotFoundError:
            print("Bot players file not found. Proceeding without bots.")
        return bot_players

    def start_game(self):
        print("Welcome to Blackjack!")
        self.seed = self.get_seed()
        self.deck = Deck(self.seed)
        while True:
            print(f"\n{self.name}, you have {self.player.chips} chips.")
            play_input = input("Do you want to play a round? (yes/no): ").strip().lower()
            if play_input == "yes":
                self.play_round()
                self.resolve_results()
                # self.show_summary()
                if self.player.chips == 0:
                    rebuy_input = input("You have no chips left. Do you want to rebuy? (yes/no): ").strip().lower()
                    if rebuy_input == "yes":
                        while True:
                            rebuy_amount = input("Enter rebuy amount (100-1000): ").strip()
                            if rebuy_amount.isdigit() and 100 <= int(rebuy_amount) <= 1000:
                                self.player.chips += int(rebuy_amount)
                                self.player.total_bought += int(rebuy_amount)
                                print(f"You rebought {rebuy_amount} chips. Now have {self.player.chips} chips.")
                                break
                            else:
                                print("Invalid input. Please enter a number between 100 and 1000.")
                    else:
                        print("You chose to leave the table.")
                        self.show_final_statistics()
                        self.draw_table_summary()
                        break
            elif play_input == "no":
                print("You chose to leave the table.")
                self.show_final_statistics()
                self.draw_table_summary()
                break
            else:
                print("Please enter one of the following: yes, no")

    def handle_bets(self):
        # Player bet
        while True:
            bet_input = input(f"{self.name}, enter your bet (1 - {self.player.chips}): ").strip()
            if bet_input.lstrip('-').isdigit():
                bet = int(bet_input)
                if 1 <= bet <= self.player.chips:
                    self.player.place_bet(bet)
                    print(f"{self.name} now has {self.player.chips} chips.")
                    break
                else:
                    print(f"Please enter a number between 1 and {self.player.chips}.")
            else:
                print("Invalid input. Please enter a valid integer.")
        # Bots bet
        for bot in self.bots:
            if bot.chips == 0:
                # Rebuy logic: double total bought so far
                rebuy_amount = bot.total_bought
                bot.chips += rebuy_amount
                
                bot.total_bought += rebuy_amount
                print(f"{bot.name} was out of chips and added {rebuy_amount} more chips.")
            bot.place_random_bet()
            print(f"{bot.name} bets {bot.bet} chips and now has {bot.chips} chips.")
        print("")

    def deal_initial_cards(self):
        # Deal one card per round to each seat in order, then dealer, for two rounds
        seats = [1, 2, 3]
        for round_num in range(2):
            for seat in seats:
                player = self.seat_map.get(seat)
                if player:
                    player.add_card(self.deck.deal_card())
            if round_num == 0:
                self.dealer.add_card(self.deck.deal_card())
            else:
                self.dealer.set_hidden_card(self.deck.deal_card())

    def show_hands(self, reveal_dealer=False):
        # show all hands in seat order, dealer last
        for seat in [1, 2, 3]:
            player = self.seat_map.get(seat)
            if player:
                cards_str = [str(card) for card in player.hand.cards]
                if player is self.player:
                    print(f"You got: {cards_str} (value: {player.hand.get_value()})")
                else:
                    print(f"{player.name} hand: {cards_str} (value: {player.hand.get_value()})")
        # Dealer
        if reveal_dealer:
            dealer_cards = ' '.join(str(card) for card in self.dealer.hand.cards)
            if self.dealer.hidden_card:
                dealer_cards += ' ??'
            print(f"\nDealer shows: {dealer_cards}")
        else:
            if self.dealer.hand.cards:
                print(f"\nDealer shows: {self.dealer.hand.cards[0]}")

    def play_round(self):
        # Card shortage check
        if len(self.deck.cards) < 20:
            print("Less than 20 cards left. Creating new deck.")
            self.deck = Deck(self.seed)
        # Reset hands
        self.player.reset_hand()
        self.dealer.reset_hand()
        for bot in self.bots:
            bot.reset_hand()
        # Handle bets
        self.handle_bets()
        # Deal cards
        self.deal_initial_cards()
        # Show hands (dealer's second card hidden)
        self.show_hands(reveal_dealer=False)
        # Player and bots turn in seat order
        for seat in [1, 2, 3]:
            player = self.seat_map.get(seat)
            if not player:
                continue
            # Human player
            if player is self.player:
                while player.hand.get_value() <= 21:
                    action = input("\nDo you want to 'hit' or 'stand'? ").strip().lower()
                    if action == "hit":
                        player.add_card(self.deck.deal_card())
                        print(f"You drew: {player.hand.cards[-1]}")
                        print(f"New hand: { [str(card) for card in player.hand.cards] } (value: {player.hand.get_value()})")
                    elif action == "stand":
                        break
                    else:
                        print("Please enter one of the following: hit, stand")
            # Bot player
            elif isinstance(player, BotPlayer):
                print(f"\n{player.name}'s trun:")
                move = player.decide_move()
                while move == "hit":
                    player.add_card(self.deck.deal_card())
                    print(f"{player.name} draws: {player.hand.cards[-1]}")
                    move = player.decide_move()
                if move == "stand":
                    cards_str = [str(card) for card in player.hand.cards]
                    print(f"{player.name} stands. Hand: {cards_str} (value: {player.hand.get_value()})")
                else:
                    print(f"{player.name} busted!")
                
        # Dealer turn
        self.dealer.reveal_hidden_card()
        cards_str = [str(card) for card in self.dealer.hand.cards]
        print(f"Dealer's hand: {cards_str} (value: {self.dealer.hand.get_value()})")
        while self.dealer.should_draw():
            self.dealer.add_card(self.deck.deal_card())
            print(f"Dealer draws a: {self.dealer.hand.cards[-1]}")
            cards_str = [str(card) for card in self.dealer.hand.cards]
            print(f"Dealer now has: {cards_str} (value: {self.dealer.hand.get_value()})")
        # Show all hands (dealer revealed)
        # self.show_hands(reveal_dealer=True)

    def resolve_results(self):
        # determine the game results and distributes winnings
        print(f"\nYour final hand value: {self.player.hand.get_value()}")
        player_value = self.player.hand.get_value()
        dealer_value = self.dealer.hand.get_value()
        if self.player.has_bust():
            print("You busted and lost your bet.")
        elif self.dealer.has_bust():
            winnings = self.player.bet * 2
            self.player.chips += winnings
            print(f"You win! You now have {self.player.chips} chips.")
        elif player_value > dealer_value:
            winnings = self.player.bet * 2
            self.player.chips += winnings
            print(f"You win! You now have {self.player.chips} chips.")
        elif player_value == dealer_value:
            self.player.chips += self.player.bet
            print("Player ties with dealer. Bet returned.")
        else:
            print("You lost this round.")

        # bots results
        for bot in self.bots:
            bot_value = bot.hand.get_value()
            if bot.has_bust():
                print(f"{bot.name} had {bot.hand.get_value()} → busted and lost.")
            elif self.dealer.has_bust():
                winnings = bot.bet * 2
                bot.chips += winnings
                print(f"{bot.name} had {bot.hand.get_value()} → won and now has {bot.chips} chips.")
            elif bot_value > dealer_value:
                winnings = bot.bet * 2
                bot.chips += winnings
                print(f"{bot.name} had {bot.hand.get_value()} → won and now has {bot.chips} chips.")
                # print(f"{bot.name} won {winnings} chips!")
            elif bot_value == dealer_value:
                bot.chips += bot.bet
                # print(f"{bot.name} ties with dealer. Bet returned.")
            else:
                print(f"{bot.name} had {bot.hand.get_value()} → lost this round.")
        print('')
        print(f"{self.name}, you have {self.player.chips} chips.")

    def show_summary(self):
        # display a summary of chips remaining for each player
        print(f"Player: {self.player.chips} chips remaining.")
        for bot in self.bots:
            print(f"{bot.name}: {bot.chips} chips remaining.")

    def show_final_statistics(self):
        # Gather all players (player + bots)
        all_players = [self.player] + self.bots
        names = [p.name for p in all_players]
        chips = np.array([p.chips for p in all_players])
        total_bought = np.array([p.total_bought for p in all_players])
        ratios = chips / total_bought
        # ranking (descending by ratio)
        ranking_indices = np.argsort(-ratios)
        print("\n--- Game Summary ---")
        # Print players in seat order
        for seat in [1, 2, 3]:
            player = self.seat_map.get(seat)
            if player:
                print(f"{player.name}: {player.chips} chips")
        print(f"\nAverage chips: {np.mean(chips):.2f}")
        print(f"Highest chip count: {np.max(chips)}")
        print("\nPlayer ranking (highest to lowest):")
        for i, idx in enumerate(ranking_indices):
            print(f"{i+1}. {names[idx]} - Chips: {chips[idx]}, Invested: {total_bought[idx]}, Return Rate: {ratios[idx]:.2f}")
            
        # store for image
        self.final_ranking = ranking_indices
        self.final_ratios = ratios

    def draw_table_summary(self):
        #player seat mapping: 1=right, 2=bottom, 3=left
        seat_positions = {
            1: (0.8, 0.5),  # right
            2: (0.5, 0.15), # bottom
            3: (0.2, 0.5),  # left
        }
        fig, ax = plt.subplots(figsize=(8, 6))
        # dark green background
        fig.patch.set_facecolor('#014421')
        ax.set_facecolor('#014421')
        # draw round table
        table_circle = plt.Circle((0.5, 0.5), 0.3, color='#228B22', ec='black', lw=3)
        ax.add_patch(table_circle)
        # draw players
        all_players = [self.player] + self.bots
        seat_map = {v: k for k, v in self.seat_map.items()}
        ranking = self.final_ranking
        for i, player in enumerate(all_players):
            # find seat
            seat = None
            for s, p in self.seat_map.items():
                if p is player:
                    seat = s
                    break
            if seat is None:
                continue
            x, y = seat_positions[seat]
            # bBox color
            if player is self.player:
                box_color = '#FFD700'  # gold
                text_color = 'black'
                label = f"{player.name} (you)"
            else:
                box_color = '#B22222'  # red
                text_color = 'white'
                label = player.name
            # ranking
            rank = np.where(ranking == i)[0][0] + 1
            # draw tthe box
            ax.add_patch(plt.Rectangle((x-0.09, y-0.05), 0.18, 0.1, color=box_color, ec='black', lw=2, zorder=2))
            # player informaton
            ax.text(x, y+0.025, label, ha='center', va='bottom', fontsize=12, color=text_color, weight='bold', zorder=3)
            ax.text(x, y-0.01, f"Chips: {player.chips}", ha='center', va='center', fontsize=10, color=text_color, zorder=3)
            ax.text(x, y-0.035, f"Rank: {rank}", ha='center', va='center', fontsize=10, color=text_color, zorder=3)
        # Hide axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        plt.tight_layout()
        plt.savefig('table_summary.png', dpi=150)
        plt.close()
        print("Table image with seating and ranking saved as 'table_summary.png'.")

def main():
    with open("BotPlayers.txt", "w") as file:
        file.write("Bot_A,120,11\n")
        file.write("Bot_B,1,22\n")

    # print("BotPlayers.txt created!")
# 
    # init and start game
    game = GameManager() # all prints untill the welcome 
    game.start_game()


if __name__ == '__main__':
    main()  