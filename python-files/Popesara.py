import pygame
import random
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
CARD_WIDTH, CARD_HEIGHT = 80, 120
FPS = 60

# Colors
GREEN = (10, 50, 0)      # Table felt
GOLD = (218, 165, 32)    # Accents
WHITE = (245, 222, 179)  # Card background
BROWN = (139, 69, 19)    # Card borders

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pope's Ara")
clock = pygame.time.Clock()

class Card:
    def __init__(self, value, suit):
        self.value = value  # 'K', 'Q', 'J', 'A', '2'-'10'
        self.suit = suit    # '♠', '♣', '♥', '♦'
        self.face_up = False
        self.image = self._render_card()
    
    def _render_card(self):
        """Generate card visuals dynamically"""
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        surf.fill(WHITE)
        pygame.draw.rect(surf, BROWN, (0, 0, CARD_WIDTH, CARD_HEIGHT), 3)
        
        if self.face_up:
            # Dynamic card drawing
            color = (200, 0, 0) if self.suit in ('♥', '♦') else (0, 0, 0)
            small_font = pygame.font.Font(None, 24)
            large_font = pygame.font.Font(None, 48)
            
            # Render card value/suit
            value_text = small_font.render(self.value, True, color)
            suit_text = large_font.render(self.suit, True, color)
            
            surf.blit(value_text, (5, 5))
            surf.blit(suit_text, (CARD_WIDTH//2 - 10, CARD_HEIGHT//2 - 10))
        else:
            # Card back design
            pygame.draw.rect(surf, BROWN, (5, 5, CARD_WIDTH-10, CARD_HEIGHT-10))
            title_font = pygame.font.Font(None, 20)
            title = title_font.render("Pope's Ara", True, GOLD)
            surf.blit(title, (CARD_WIDTH//2 - 40, CARD_HEIGHT//2 - 10))
        
        return surf

class Game:
    def __init__(self):
        self.deck = []
        self.player_hand = []
        self.ai_hand = []
        self.player_table = []
        self.ai_table = []
        self.current_turn = 'player'  # or 'ai'
        self.coins = 100
        self._initialize_deck()
    
    def _initialize_deck(self):
        """Create a shuffled deck with 4 Kings"""
        suits = ['♠', '♣', '♥', '♦']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q']
        
        # Add standard cards
        for suit in suits:
            for value in values:
                self.deck.append(Card(value, suit))
        
        # Add Kings (4 total)
        for suit in suits:
            self.deck.append(Card('K', suit))
        
        random.shuffle(self.deck)
    
    def deal_initial_cards(self):
        """Deal 4 cards to each player"""
        for _ in range(4):
            self.player_hand.append(self.deck.pop())
            self.ai_hand.append(self.deck.pop())
    
    def draw_card(self, player):
        """Draw a card from deck to player's hand"""
        if self.deck:
            card = self.deck.pop()
            if player == 'player':
                self.player_hand.append(card)
            else:
                self.ai_hand.append(card)
            return card
        return None

def main():
    game = Game()
    game.deal_initial_cards()
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                handle_click(event.pos, game)
        
        # Update game state
        if game.current_turn == 'ai':
            ai_turn(game)
        
        # Render
        screen.fill(GREEN)
        render_game(screen, game)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

def handle_click(pos, game):
    """Process player clicks"""
    if game.current_turn != 'player':
        return
    
    # Check deck click
    deck_rect = pygame.Rect(SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2 - 60, 80, 120)
    if deck_rect.collidepoint(pos):
        game.draw_card('player')
        game.current_turn = 'ai'
    
    # Check hand cards
    for i, card in enumerate(game.player_hand):
        card_rect = pygame.Rect(50 + i*90, SCREEN_HEIGHT - 150, CARD_WIDTH, CARD_HEIGHT)
        if card_rect.collidepoint(pos):
            play_card(game, i)