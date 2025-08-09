#!/usr/bin/env python3
"""
Pope's Ara - Terminal Edition (Python 3)
A lightweight, dependency-free CLI game inspired by the rules snapshot.

Goal: Avoid collecting 4 Kings on your table. If you do, you lose the round.

Cards in deck: 4..10, J, Q, K, A (four suits). 2s and 3s are excluded.

Card Effects (from the fetched page):
- K: Automatically placed on your table. Collect all 4 and you lose!
- Q: Lets you get a King either from the deck or from your opponent's table (hurts you).
- J: Draw an additional card immediately.
- A: If you have a King, return one to the deck (reshuffled). Otherwise, opponent draws 2.
- 10: Your opponent takes a card of their choice from your hand.
- 9: Skip your next turn.
- 8: Make your opponent get a King from the deck.
- 7: Draw a card higher than 7 from the deck.
- 6: Switch hands with your opponent.
- 5: Discard a card from your hand or remove one of your Kings from the table.
- 4: Draw 3 additional cards.

This is a simple 1v1 (You vs AI) implementation with straightforward AI heuristics.
"""

import random
import sys
from typing import List, Optional

RANKS: List[str] = ["4","5","6","7","8","9","10","J","Q","K","A"]
SUITS: List[str] = ["♠","♥","♦","♣"]
RANK_VALUE = {**{str(n): n for n in range(4, 11)}, "J": 11, "Q": 12, "K": 13, "A": 14}

class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards: List[Card] = [Card(r, s) for r in RANKS for s in SUITS]
        random.shuffle(self.cards)
    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None
    def put_back_and_shuffle(self, card: Card):
        self.cards.append(card)
        random.shuffle(self.cards)
    def take_king_from_deck(self) -> Optional[Card]:
        # Find and remove a King from the deck if available
        for i, c in enumerate(self.cards):
            if c.rank == "K":
                return self.cards.pop(i)
        return None
    def __len__(self):
        return len(self.cards)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.kings_on_table: int = 0
        self.skip_next: bool = False
    def hand_as_str(self) -> str:
        return " ".join(f"[{i}:{c}]" for i, c in enumerate(self.hand)) or "(empty)"

class Game:
    def __init__(self):
        self.deck = Deck()
        self.discard: List[Card] = []
        self.players = [Player("You"), Player("AI")]
        self.current = 0  # index of current player
        self.starting_hand_size = 3
        self.deal_starting_hands()

    def opponent_index(self, idx: int) -> int:
        return 1 - idx

    def deal_starting_hands(self):
        for _ in range(self.starting_hand_size):
            for i in range(2):
                self.draw_card(i)

    def draw_card(self, idx: int, silent: bool = False):
        card = self.deck.draw()
        if not card:
            if not silent:
                self.info(f"Deck is empty.")
            return
        if card.rank == "K":
            self.players[idx].kings_on_table += 1
            if not silent:
                self.info(f"{self.players[idx].name} drew a King! It goes to their table.")
        else:
            self.players[idx].hand.append(card)
            if not silent:
                self.info(f"{self.players[idx].name} drew {card}.")

    def auto_place_kings_in_hand(self, idx: int):
        # In case a King ever ends up in hand for any reason, auto-place it
        player = self.players[idx]
        kings = [c for c in player.hand if c.rank == "K"]
        if kings:
            for k in kings:
                player.hand.remove(k)
                player.kings_on_table += 1
            self.info(f"{player.name} auto-placed {len(kings)} King(s) from hand to table.")

    def check_lose(self) -> Optional[int]:
        # Returns index of loser if someone has 4 kings
        for i, p in enumerate(self.players):
            if p.kings_on_table >= 4:
                return i
        return None

    def info(self, msg: str):
        print(f"\n>>> {msg}")

    def status(self):
        you, ai = self.players
        print("\n====== Game Status ======")
        print(f"Deck: {len(self.deck)} cards | Discard: {len(self.discard)}")
        print(f"Your Kings: {you.kings_on_table} | AI Kings: {ai.kings_on_table}")
        print(f"Your hand: {you.hand_as_str()}")
        print("========================\n")

    # --- Card effects ---
    def effect_Q(self, idx: int):
        player = self.players[idx]
        opp = self.players[self.opponent_index(idx)]
        if player.name == "You":
            choice = ""
            while choice not in {"deck", "opponent", "d", "o"}:
                choice = input("Q: Get a King from (deck/opponent)? ").strip().lower()
            from_deck = choice in {"deck", "d"}
        else:
            # AI: prefers deck if opponent (you) has 0 Kings; otherwise picks opponent (still bad for itself)
            from_deck = (opp.kings_on_table == 0)
        if from_deck:
            k = self.deck.take_king_from_deck()
            if k:
                player.kings_on_table += 1
                self.info(f"{player.name} used Q and took a King from the deck (onto their table).")
            else:
                self.info("No Kings left in deck.")
        else:
            if opp.kings_on_table > 0:
                opp.kings_on_table -= 1
                player.kings_on_table += 1
                self.info(f"{player.name} used Q and took a King from opponent's table (onto their table).")
            else:
                self.info("Opponent has no Kings to take.")

    def effect_J(self, idx: int):
        self.draw_card(idx, silent=False)

    def effect_A(self, idx: int):
        player = self.players[idx]
        opp = self.players[self.opponent_index(idx)]
        if player.kings_on_table > 0:
            player.kings_on_table -= 1
            self.deck.put_back_and_shuffle(Card("K", random.choice(SUITS)))
            self.info(f"{player.name} returned a King to the deck.")
        else:
            self.info(f"{player.name} has no Kings; {opp.name} draws 2.")
            self.draw_card(self.opponent_index(idx), silent=False)
            self.draw_card(self.opponent_index(idx), silent=False)

    def effect_10(self, idx: int):
        player = self.players[idx]
        opp = self.players[self.opponent_index(idx)]
        if not player.hand:
            self.info("No cards in hand for opponent to take.")
            return
        if opp.name == "You":
            # Human chooses which to take
            take_idx = None
            while take_idx is None:
                try:
                    take_idx = int(input(f"10: Choose a card index to take from AI: {player.hand_as_str()} -> index: "))
                    if take_idx < 0 or take_idx >= len(player.hand):
                        take_idx = None
                except ValueError:
                    take_idx = None
        else:
            # AI chooses: prefer to take an Ace, else highest value
            best_i = 0
            best_score = -1
            for i, c in enumerate(player.hand):
                score = 100 if c.rank == "A" else RANK_VALUE.get(c.rank, 0)
                if score > best_score:
                    best_i = i
                    best_score = score
            take_idx = best_i
        stolen = player.hand.pop(take_idx)
        opp.hand.append(stolen)
        self.info(f"{opp.name} took {stolen} from {player.name} using 10.")

    def effect_9(self, idx: int):
        player = self.players[idx]
        player.skip_next = True
        self.info(f"{player.name} will skip their next turn.")

    def effect_8(self, idx: int):
        opp = self.players[self.opponent_index(idx)]
        k = self.deck.take_king_from_deck()
        if k:
            opp.kings_on_table += 1
            self.info(f"{self.players[idx].name} forced {opp.name} to get a King from the deck.")
        else:
            self.info("No Kings left in deck.")

    def effect_7(self, idx: int):
        # Draw until > 7 is drawn (i.e., 8 or higher). Kings still auto-place.
        while True:
            card = self.deck.draw()
            if not card:
                self.info("Deck empty while resolving 7.")
                return
            if card.rank == "K":
                self.players[idx].kings_on_table += 1
                self.info(f"{self.players[idx].name} drew a King (via 7) -> table.")
                return
            if RANK_VALUE[card.rank] > 7:
                self.players[idx].hand.append(card)
                self.info(f"{self.players[idx].name} drew {card} (via 7).")
                return
            else:
                # Put back lower card at bottom and continue (or discard).
                # We'll discard to keep it simple.
                self.discard.append(card)

    def effect_6(self, idx: int):
        p = self.players[idx]
        o = self.players[self.opponent_index(idx)]
        p.hand, o.hand = o.hand, p.hand
        self.info(f"{p.name} switched hands with {o.name}.")
        # Ensure kings aren't in hand (safety)
        self.auto_place_kings_in_hand(idx)
        self.auto_place_kings_in_hand(self.opponent_index(idx))

    def effect_5(self, idx: int):
        player = self.players[idx]
        if player.name == "You":
            where = ""
            while where not in {"hand", "table", "h", "t"}:
                where = input("5: Discard from (hand/table)? ").strip().lower()
            if where in {"table", "t"}:
                if player.kings_on_table > 0:
                    player.kings_on_table -= 1
                    self.info("You discarded a King from your table.")
                else:
                    self.info("You have no Kings on table to discard.")
            else:
                if not player.hand:
                    self.info("Your hand is empty.")
                    return
                try:
                    idx_to_discard = int(input(f"Choose card index to discard: {player.hand_as_str()} -> index: "))
                except ValueError:
                    self.info("Invalid input; discarding the last card by default.")
                    idx_to_discard = len(player.hand) - 1
                idx_to_discard = max(0, min(idx_to_discard, len(player.hand) - 1))
                disc = player.hand.pop(idx_to_discard)
                self.discard.append(disc)
                self.info(f"You discarded {disc} from your hand.")
        else:
            # AI: Prefer discarding a King from table if any, else random from hand
            if player.kings_on_table > 0:
                player.kings_on_table -= 1
                self.info("AI discarded a King from its table.")
            elif player.hand:
                # Avoid discarding 'A' if possible
                non_aces = [i for i, c in enumerate(player.hand) if c.rank != "A"]
                idx_to_discard = random.choice(non_aces) if non_aces else random.randrange(len(player.hand))
                disc = player.hand.pop(idx_to_discard)
                self.discard.append(disc)
                self.info(f"AI discarded {disc} from hand.")
            else:
                self.info("AI had nothing to discard.")

    def effect_4(self, idx: int):
        for _ in range(3):
            self.draw_card(idx, silent=False)

    def play_card(self, idx: int, hand_index: int):
        player = self.players[idx]
        if hand_index < 0 or hand_index >= len(player.hand):
            self.info("Invalid card index.")
            return False
        card = player.hand.pop(hand_index)
        self.discard.append(card)
        self.info(f"{player.name} played {card}.")
        r = card.rank
        if r == "Q":
            self.effect_Q(idx)
        elif r == "J":
            self.effect_J(idx)
        elif r == "A":
            self.effect_A(idx)
        elif r == "10":
            self.effect_10(idx)
        elif r == "9":
            self.effect_9(idx)
        elif r == "8":
            self.effect_8(idx)
        elif r == "7":
            self.effect_7(idx)
        elif r == "6":
            self.effect_6(idx)
        elif r == "5":
            self.effect_5(idx)
        elif r == "4":
            self.effect_4(idx)
        elif r == "K":
            # Safety: auto-place
            self.players[idx].kings_on_table += 1
        return True

    def human_turn(self):
        p = self.players[0]
        if p.skip_next:
            p.skip_next = False
            self.info("You skip this turn.")
            return
        self.status()
        while True:
            cmd = input("Your move: (d=draw, p <index>=play) ").strip().lower()
            if cmd == "d" or cmd == "draw":
                self.draw_card(0, silent=False)
                self.auto_place_kings_in_hand(0)
                break
            if cmd.startswith("p ") or cmd.startswith("play "):
                parts = cmd.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    idx = int(parts[1])
                    if self.play_card(0, idx):
                        self.auto_place_kings_in_hand(0)
                        break
            print("Invalid command. Examples: 'd' or 'p 0'")

    def ai_choose_card_index(self) -> Optional[int]:
        ai = self.players[1]
        # Heuristic priority: A (if has kings) > 8 > 6 > 5 (if has kings) > 7 > J > 4 > 10 > 9 > Q
        # Avoid Q and 9 if possible.
        priorities = [
            lambda c: (c.rank == "A" and self.players[1].kings_on_table > 0),
            lambda c: (c.rank == "8"),
            lambda c: (c.rank == "6"),
            lambda c: (c.rank == "5" and self.players[1].kings_on_table > 0),
            lambda c: (c.rank == "7"),
            lambda c: (c.rank == "J"),
            lambda c: (c.rank == "4"),
            lambda c: (c.rank == "10"),
            lambda c: (c.rank == "9"),
            lambda c: (c.rank == "Q"),
        ]
        for prio in priorities:
            for i, c in enumerate(ai.hand):
                if prio(c):
                    return i
        return None

    def ai_turn(self):
        ai = self.players[1]
        if ai.skip_next:
            ai.skip_next = False
            self.info("AI skips this turn.")
            return
        # Decide whether to play or draw
        idx = self.ai_choose_card_index()
        if idx is None:
            self.draw_card(1, silent=False)
            self.auto_place_kings_in_hand(1)
        else:
            self.play_card(1, idx)
            self.auto_place_kings_in_hand(1)

    def run(self):
        self.info("Welcome to Pope's Ara (CLI). Avoid collecting 4 Kings!")
        while True:
            loser = self.check_lose()
            if loser is not None:
                winner = self.opponent_index(loser)
                self.info(f"{self.players[loser].name} has 4 Kings. {self.players[winner].name} wins!")
                print("Game over.")
                return
            if len(self.deck) == 0:
                self.info("Deck exhausted. It's a draw!")
                return
            # Human turn then AI turn
            self.human_turn()
            loser = self.check_lose()
            if loser is not None or len(self.deck) == 0:
                continue
            self.ai_turn()


def main():
    random.seed()
    g = Game()
    g.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
