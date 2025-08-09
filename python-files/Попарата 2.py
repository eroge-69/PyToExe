import pygame
import sys
import random
import math

pygame.init()

# Window setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pope's Ara")

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
pygame.font.init()
FONT_SPECIAL = pygame.font.SysFont("Special Elite", 24)
FONT_SPECIAL_SMALL = pygame.font.SysFont("Special Elite", 18)
FONT_SPECIAL_BIG = pygame.font.SysFont("Special Elite", 28)

# Colors
COLOR_BG = (10, 50, 0)
COLOR_TEXT = (245, 222, 179)
COLOR_GOLD = (255, 215, 0)
COLOR_BORDER = (139, 69, 19)

# Game state container
gameState = {
    "discardSource": None,
    "deck": [],
    "playerHand": [],
    "playerTable": [],
    "aiHand": [],
    "aiTable": [],
    "currentTurn": "player",
    "selectedCardIndex": -1,
    "coins": 100,
    "inventory": [],
    "message": "",
    "showMessage": False,
    "messageTimeout": 0,
    "gamePhase": "normal",
    "specialAction": None,
    "skipNextTurn": False,
    "aiSkill": 0.5,
    "cardHover": 0,
    "cardHoverDirection": 1,
    "tutorialShown": False
}

# Card images cache
cardImages = {}

# Button class for UI
class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hover = False

    def draw(self, surface):
        bg_color = (160, 92, 44) if not self.hover else (180, 110, 60)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT, self.rect, 2, border_radius=8)
        text_surf = FONT_SPECIAL.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

# --- Card rendering functions ---

CARD_WIDTH, CARD_HEIGHT = 140, 200

def draw_card_surface(value, suit):
    """Draws a card surface similar to the HTML canvas version."""
    surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    ctx = surf
    # Background
    ctx.fill((245, 222, 179))
    pygame.draw.rect(ctx, COLOR_BORDER, ctx.get_rect(), 4)

    # Card corners text
    color = (196, 30, 58) if suit in ['♥', '♦'] else (0, 0, 0)
    font_corner = pygame.font.SysFont("Special Elite", 24, bold=True)
    # Top-left
    ctx.blit(font_corner.render(value, True, color), (10, 5))
    ctx.blit(font_corner.render(suit, True, color), (10, 30))
    # Bottom-right
    text_v = font_corner.render(value, True, color)
    text_s = font_corner.render(suit, True, color)
    ctx.blit(text_v, (CARD_WIDTH - text_v.get_width() - 10, CARD_HEIGHT - 35))
    ctx.blit(text_s, (CARD_WIDTH - text_s.get_width() - 10, CARD_HEIGHT - 60))

    # Placeholder for unique artwork
    # In HTML version, each face card has unique pirate art; here we simulate with colored shapes
    if value == "K":
        pygame.draw.rect(ctx, color, (40, 90, 60, 70))  # Robe
        pygame.draw.circle(ctx, (232, 194, 152), (70, 70), 20)  # Head
    elif value == "Q":
        pygame.draw.polygon(ctx, color, [(40, 160), (100, 160), (70, 90)])  # Dress
        pygame.draw.circle(ctx, (232, 194, 152), (70, 70), 20)  # Head
    elif value == "J":
        pygame.draw.rect(ctx, color, (50, 100, 40, 50))  # Vest
        pygame.draw.circle(ctx, (232, 194, 152), (70, 70), 20)  # Head
    elif value == "A" and suit == "♠":
        pygame.draw.polygon(ctx, (0, 0, 0), [(70, 80), (50, 120), (90, 120)])  # Spade

    return surf


def get_card_image(card):
    """Get or create card surface."""
    if card not in cardImages:
        value = card[:-1]
        suit = card[-1]
        cardImages[card] = draw_card_surface(value, suit)
    return cardImages[card]


# --- Deck creation & shuffle ---
def initialize_deck():
    suits = ['♠', '♣', '♥', '♦']
    values = ['A', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q']
    deck = [v + s for s in suits for v in values]
    # Add Kings explicitly
    deck += ['K♠', 'K♣', 'K♥', 'K♦']
    return shuffle_deck(deck)

def shuffle_deck(deck):
    shuffled = deck[:]
    random.shuffle(shuffled)
    return shuffled


# --- Initial deal ---
def deal_initial_cards():
    gameState["playerHand"].clear()
    gameState["aiHand"].clear()
    gameState["playerTable"].clear()
    gameState["aiTable"].clear()

    for _ in range(4):
        p_card = gameState["deck"].pop()
        if p_card.startswith("K"):
            gameState["playerTable"].append(p_card)
        else:
            gameState["playerHand"].append(p_card)

        a_card = gameState["deck"].pop()
        if a_card.startswith("K"):
            gameState["aiTable"].append(a_card)
        else:
            gameState["aiHand"].append(a_card)

    gameState["currentTurn"] = "ai"  # AI goes first in HTML version

# --- Core game actions ---

def draw_card(player):
    """Draws a card from the deck for either player."""
    if not gameState["deck"]:
        return None

    card = gameState["deck"].pop()
    if player == "player":
        if card.startswith("K"):
            gameState["playerTable"].append(card)
            display_message(f"You drew a King - placed on your table!")
        else:
            gameState["playerHand"].append(card)
            display_message(f"You drew {card}")
        handle_special_card_effects(card, "player")
    else:
        if card.startswith("K"):
            gameState["aiTable"].append(card)
            display_message("Opponent drew a King - placed on their table!")
        else:
            gameState["aiHand"].append(card)
            display_message("Opponent drew a card")
        handle_special_card_effects(card, "ai")
    return card


def play_card(player, card_index):
    """Play a card from a player's hand."""
    if player == "player":
        if 0 <= card_index < len(gameState["playerHand"]):
            card = gameState["playerHand"][card_index]
            if card.startswith("K"):
                display_message("Kings are automatically shown on the table")
                return
            gameState["playerHand"].pop(card_index)
            gameState["playerTable"].append(card)
            display_message(f"You played {card}")
            handle_special_card_effects(card, "player")
            if gameState["gamePhase"] == "normal":
                end_turn()
    else:
        if 0 <= card_index < len(gameState["aiHand"]):
            card = gameState["aiHand"][card_index]
            if card.startswith("K"):
                display_message("Kings are automatically shown on the table")
                return
            gameState["aiHand"].pop(card_index)
            gameState["aiTable"].append(card)
            display_message("Opponent played a card")
            handle_special_card_effects(card, "ai")
            if gameState["gamePhase"] == "normal":
                end_turn()


def handle_special_card_effects(card, player):
    """Replicates HTML special card effects for player or AI."""
    value = card[:-1]  # everything except last char (suit)

    if player == "player":
        if value == "Q":
            display_message("Queen lets you choose where to get a King from!")
            # For now, simulate taking from deck if possible
            take_king_from_deck("player")
        elif value == "J":
            display_message("Jack lets you draw a different card!")
            if gameState["deck"]:
                new_card = gameState["deck"].pop()
                gameState["playerHand"].append(new_card)
                display_message(f"You drew {new_card} from Jack's effect")
        elif value == "4":
            display_message("4 makes you draw 3 additional cards!")
            for _ in range(3):
                if gameState["deck"]:
                    gameState["playerHand"].append(gameState["deck"].pop())
        elif value == "9":
            display_message("9 makes you skip your next turn!")
            gameState["skipNextTurn"] = True
        elif value == "5":
            display_message("5 lets you discard a card from your hand or table!")
            discard_from_hand("player")
        elif value == "6":
            display_message("6 lets you switch hands with opponent!")
            gameState["playerHand"], gameState["aiHand"] = gameState["aiHand"], gameState["playerHand"]
        elif value == "7":
            display_message("7 makes you draw a higher card!")
            draw_higher_than_7("player")
        elif value == "8":
            display_message("8 makes your opponent get a king!")
            take_king_from_deck("ai")
        elif value == "10":
            if gameState["playerHand"]:
                taken = gameState["playerHand"].pop(0)
                gameState["aiHand"].append(taken)
                display_message("Opponent took a card from your hand.")
        elif value == "A":
            if any(c.startswith("K") for c in gameState["playerTable"]):
                king_to_return = next(c for c in gameState["playerTable"] if c.startswith("K"))
                gameState["playerTable"].remove(king_to_return)
                gameState["deck"].append(king_to_return)
                random.shuffle(gameState["deck"])
                display_message("Returned a King to the deck!")
            else:
                draw_two_cards("ai")

    else:  # AI's turn
        if value == "Q":
            if gameState["playerTable"]:
                king_to_take = next((c for c in gameState["playerTable"] if c.startswith("K")), None)
                if king_to_take:
                    gameState["playerTable"].remove(king_to_take)
                    gameState["aiTable"].append(king_to_take)
                    display_message("Opponent took a King from your table!")
            else:
                take_king_from_deck("ai")
        elif value == "J":
            if gameState["deck"]:
                gameState["aiHand"].append(gameState["deck"].pop())
        elif value == "4":
            for _ in range(3):
                if gameState["deck"]:
                    gameState["aiHand"].append(gameState["deck"].pop())
        elif value == "9":
            gameState["skipNextTurn"] = True
        elif value == "5":
            discard_from_hand("ai")
        elif value == "6":
            gameState["playerHand"], gameState["aiHand"] = gameState["aiHand"], gameState["playerHand"]
        elif value == "7":
            draw_higher_than_7("ai")
        elif value == "8":
            take_king_from_deck("player")
        elif value == "10":
            if gameState["aiHand"]:
                gameState["playerHand"].append(gameState["aiHand"].pop(0))
        elif value == "A":
            if any(c.startswith("K") for c in gameState["aiTable"]):
                king_to_return = next(c for c in gameState["aiTable"] if c.startswith("K"))
                gameState["aiTable"].remove(king_to_return)
                gameState["deck"].append(king_to_return)
                random.shuffle(gameState["deck"])
            else:
                draw_two_cards("player")

    check_game_state()


# --- Helper functions for special effects ---
def take_king_from_deck(player):
    kings_in_deck = [c for c in gameState["deck"] if c.startswith("K")]
    if kings_in_deck:
        king = kings_in_deck.pop()
        gameState["deck"].remove(king)
        if player == "player":
            gameState["playerTable"].append(king)
        else:
            gameState["aiTable"].append(king)

def draw_two_cards(player):
    for _ in range(2):
        if gameState["deck"]:
            card = gameState["deck"].pop()
            if player == "player":
                if card.startswith("K"):
                    gameState["playerTable"].append(card)
                else:
                    gameState["playerHand"].append(card)
            else:
                if card.startswith("K"):
                    gameState["aiTable"].append(card)
                else:
                    gameState["aiHand"].append(card)

def discard_from_hand(player):
    if player == "player" and gameState["playerHand"]:
        gameState["playerHand"].pop(0)
    elif player == "ai" and gameState["aiHand"]:
        gameState["aiHand"].pop(0)

def draw_higher_than_7(player):
    high_cards = [c for c in gameState["deck"] if c[:-1] in ["8", "9", "10", "J", "Q", "K"]]
    if high_cards:
        chosen = high_cards.pop()
        gameState["deck"].remove(chosen)
        if player == "player":
            gameState["playerHand"].append(chosen)
        else:
            gameState["aiHand"].append(chosen)


def end_turn():
    gameState["selectedCardIndex"] = -1
    sync_kings()

    if not check_game_state():
        gameState["currentTurn"] = "ai" if gameState["currentTurn"] == "player" else "player"
        if gameState["skipNextTurn"]:
            gameState["skipNextTurn"] = False
            gameState["currentTurn"] = "ai" if gameState["currentTurn"] == "player" else "player"
        if gameState["currentTurn"] == "ai":
            ai_turn()


def ai_turn():
    if gameState["currentTurn"] != "ai":
        return
    if random.random() < gameState["aiSkill"]:
        specials = [c for c in gameState["aiHand"] if c[:-1] in ["A", "Q", "J", "5", "6", "8", "10"]]
        if specials:
            play_card("ai", gameState["aiHand"].index(specials[0]))
        else:
            draw_card("ai")
            end_turn()
    else:
        if gameState["aiHand"] and random.random() > 0.5:
            non_kings = [c for c in gameState["aiHand"] if not c.startswith("K")]
            if non_kings:
                play_card("ai", gameState["aiHand"].index(random.choice(non_kings)))
            else:
                draw_card("ai")
                end_turn()
        else:
            draw_card("ai")
            end_turn()

# --- Utility functions ---

def sync_kings():
    """Moves Kings from hand to table automatically."""
    # Player
    for card in gameState["playerHand"][:]:
        if card.startswith("K"):
            gameState["playerHand"].remove(card)
            if card not in gameState["playerTable"]:
                gameState["playerTable"].append(card)
    # AI
    for card in gameState["aiHand"][:]:
        if card.startswith("K"):
            gameState["aiHand"].remove(card)
            if card not in gameState["aiTable"]:
                gameState["aiTable"].append(card)


def check_game_state():
    """Checks if one player has all 4 Kings."""
    player_kings = [c for c in gameState["playerTable"] if c.startswith("K")]
    ai_kings = [c for c in gameState["aiTable"] if c.startswith("K")]

    if len(player_kings) == 4 or len(ai_kings) == 4:
        if len(player_kings) == 4:
            display_message("You have all Kings! You lose this round!")
            gameState["coins"] -= 10
        else:
            display_message("Opponent has all Kings! You win this round!")
            gameState["coins"] += 20
            gameState["aiSkill"] = min(0.9, gameState["aiSkill"] + 0.05)
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # restart game after 3s
        return True
    return False


def display_message(msg):
    """Show a temporary overlay message."""
    gameState["message"] = msg
    gameState["showMessage"] = True
    gameState["messageTimeout"] = pygame.time.get_ticks()


# --- Rendering ---

def draw_game():
    screen.fill(COLOR_BG)

    # Coins display
    coins_text = FONT_SPECIAL.render(f"Coins: {gameState['coins']}", True, COLOR_GOLD)
    screen.blit(coins_text, (WIDTH - coins_text.get_width() - 20, 15))

    # Player table cards
    draw_card_row(gameState["playerTable"], HEIGHT - CARD_HEIGHT - 150)
    # Player hand cards
    draw_card_row(gameState["playerHand"], HEIGHT - CARD_HEIGHT - 50)

    # AI table cards
    draw_card_row(gameState["aiTable"], 150)
    # AI hand cards (face down)
    draw_card_row(["??"] * len(gameState["aiHand"]), 50, facedown=True)

    # Buttons
    for b in ui_buttons:
        b.draw(screen)

    # Message overlay
    if gameState["showMessage"]:
        msg_surf = FONT_SPECIAL_BIG.render(gameState["message"], True, COLOR_TEXT)
        msg_bg = pygame.Surface((msg_surf.get_width() + 40, msg_surf.get_height() + 20))
        msg_bg.fill((0, 0, 0))
        msg_bg.set_alpha(200)
        rect = msg_bg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(msg_bg, rect)
        screen.blit(msg_surf, (rect.x + 20, rect.y + 10))


def draw_card_row(cards, y, facedown=False):
    if not cards:
        return
    spacing = CARD_WIDTH + 10
    total_width = spacing * len(cards) - 10
    start_x = WIDTH // 2 - total_width // 2
    for i, card in enumerate(cards):
        x = start_x + i * spacing
        if facedown:
            pygame.draw.rect(screen, (80, 0, 0), (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(screen, COLOR_BORDER, (x, y, CARD_WIDTH, CARD_HEIGHT), 4)
        elif card == "??":
            pygame.draw.rect(screen, (80, 0, 0), (x, y, CARD_WIDTH, CARD_HEIGHT))
        else:
            screen.blit(get_card_image(card), (x, y))

# --- Game start & UI setup ---

def start_new_game():
    gameState["deck"] = initialize_deck()
    deal_initial_cards()
    gameState["selectedCardIndex"] = -1
    gameState["gamePhase"] = "normal"
    gameState["specialAction"] = None
    gameState["skipNextTurn"] = False
    if gameState["currentTurn"] == "ai":
        pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # AI moves after 1s


# UI Buttons
ui_buttons = [
    Button((50, HEIGHT - 40, 120, 30), "Draw Card", lambda: draw_card("player")),
    Button((200, HEIGHT - 40, 120, 30), "Play Card", lambda: play_card("player", 0)),
    Button((350, HEIGHT - 40, 120, 30), "Shop", lambda: display_message("Shop not implemented yet")),
]

# Start the game
start_new_game()

# --- Main loop ---
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # UI button events
        for b in ui_buttons:
            b.handle_event(event)

        # Timers
        if event.type == pygame.USEREVENT + 1:
            start_new_game()
        elif event.type == pygame.USEREVENT + 2:
            ai_turn()
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # clear timer

    # Hide message after 3 seconds
    if gameState["showMessage"] and pygame.time.get_ticks() - gameState["messageTimeout"] > 3000:
        gameState["showMessage"] = False

    draw_game()
    pygame.display.flip()

pygame.quit()
sys.exit()

