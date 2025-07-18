import pygame
import random

# Initialize PyGame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crazy Eights")
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

# Card setup
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [{'suit': s, 'rank': r} for s in suits for r in ranks]

def deal_cards(deck):
    random.shuffle(deck)
    return deck[:8], deck[8:16], deck[16], deck[17:]

def is_playable(card, top_card, current_suit):
    return (card['rank'] == '8' or 
            card['rank'] == top_card['rank'] or 
            card['suit'] == current_suit)

def draw_card(draw_pile):
    return draw_pile.pop(0) if draw_pile else None

def draw_hand(hand, y):
    for i, card in enumerate(hand):
        card_text = f"{card['rank']} of {card['suit']}"
        txt = font.render(card_text, True, (255, 255, 255))
        screen.blit(txt, (20 + i * 100, y))

def get_card_index(mouse_pos, y, hand):
    for i in range(len(hand)):
        card_x = 20 + i * 100
        if card_x < mouse_pos[0] < card_x + 80 and y < mouse_pos[1] < y + 30:
            return i
    return None

def computer_play(hand, top_card, current_suit):
    for i, card in enumerate(hand):
        if is_playable(card, top_card, current_suit):
            chosen = hand.pop(i)
            return chosen, chosen['suit'] if chosen['rank'] != '8' else random.choice(suits)
    return None, current_suit

def show_text(text, y):
    txt = font.render(text, True, (255, 255, 0))
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))

def game_loop():
    deck = create_deck()
    player_hand, computer_hand, top_card, draw_pile = deal_cards(deck)
    current_suit = top_card['suit']
    player_turn = True
    game_over = False
    message = ""

    while not game_over:
        screen.fill((0, 128, 0))
        draw_hand(player_hand, HEIGHT - 40)
        draw_hand(['Hidden'] * len(computer_hand), 40)

        show_text(f"Top Card: {top_card['rank']} of {top_card['suit']} | Suit in play: {current_suit}", HEIGHT // 2)
        show_text(message, HEIGHT // 2 + 40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
                index = get_card_index(event.pos, HEIGHT - 40, player_hand)
                if index is not None:
                    selected = player_hand[index]
                    if is_playable(selected, top_card, current_suit):
                        top_card = selected
                        current_suit = selected['suit']
                        player_hand.pop(index)
                        message = f"You played {selected['rank']} of {selected['suit']}"
                        if selected['rank'] == '8':
                            current_suit = random.choice(suits)
                            message += f" and changed suit to {current_suit}"
                        if not player_hand:
                            game_over = True
                            message = "🎉 You win!"
                        player_turn = False
                    else:
                        message = "Invalid play!"
                else:
                    # Clicked outside: draw card
                    card = draw_card(draw_pile)
                    if card:
                        player_hand.append(card)
                        message = "You drew a card"

        if not player_turn and not game_over:
            pygame.time.wait(800)  # Pause for effect
            card, suit = computer_play(computer_hand, top_card, current_suit)
            if card:
                top_card = card
                current_suit = suit
                message = f"Computer played {card['rank']} of {card['suit']}"
                if card['rank'] == '8':
                    message += f" and changed suit to {current_suit}"
                if not computer_hand:
                    game_over = True
                    message = "😢 Computer wins!"
            else:
                card = draw_card(draw_pile)
                if card:
                    computer_hand.append(card)
                    message = "Computer drew a card"
                else:
                    message = "Draw pile empty"
            player_turn = True

        clock.tick(30)

game_loop()
