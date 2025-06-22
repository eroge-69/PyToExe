
import re

def extract_player_cards(entry):
    match = re.search(r"\d+\(([^)]+)\)", entry)
    if match:
        return match.group(1).split(" ")
    return []

def suit_count(cards):
    suits = {"♠️": 0, "♥️": 0, "♦️": 0, "♣️": 0}
    for card in cards:
        for suit in suits:
            if suit in card:
                suits[suit] += 1
    return suits

def predict_next_suit(suits):
    rules = {
        "♦️": ("♥️", 40),
        "♠️": ("♣️", 35),
        "♥️": ("♦️", 33),
        "♣️": ("♠️", 38),
    }
    predictions = []
    for suit, count in suits.items():
        if count == 2 and suit in rules:
            next_suit, base_prob = rules[suit]
            confidence = base_prob
            predictions.append((next_suit, confidence))
    return predictions

def main():
    print("=== Baccarat Suit Predictor ===")
    print("Enter a Player hand like this format: 6(10♦️5♦️A♠️)")
    entry = input("Player Hand Entry: ").strip()
    cards = extract_player_cards(entry)
    if not cards:
        print("Invalid input format. Please use the format: 6(10♦️5♦️A♠️)")
        return
    suits = suit_count(cards)
    predictions = predict_next_suit(suits)
    if not predictions:
        print("No 2-suit pattern detected. No prediction made.")
    else:
        for suit, conf in predictions:
            print(f"Predicted next likely suit: {suit} with confidence {conf}%")

if __name__ == "__main__":
    main()
