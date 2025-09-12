import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Snake Game Deluxe")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREY = (150, 150, 150)
LIGHT_GREY = (200, 200, 200)

# Game variables
BLOCK_SIZE = 20
FPS = 10  # Snake speed
FONT_SMALL = pygame.font.Font(None, 35)
FONT_MEDIUM = pygame.font.Font(None, 50)
FONT_LARGE = pygame.font.Font(None, 70)

# Global game state and customization options
game_state = 'MENU'
snake_color = GREEN # Default snake color

# --- Helper Functions ---

def draw_text(text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    SCREEN.blit(text_surface, text_rect)
    return text_rect

def create_button(text, font, x, y, width, height, active_color, inactive_color, event):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)

    current_color = active_color if button_rect.collidepoint(mouse_pos) else inactive_color
    pygame.draw.rect(SCREEN, current_color, button_rect)
    draw_text(text, font, BLACK, x, y)

    # Check for click only if the mouse button was pressed down within the button
    if event is not None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if button_rect.collidepoint(mouse_pos):
            return True
    return False

# --- Game Functions ---

def reset_game():
    global snake, snake_direction, food_pos, score
    snake = [{'x': 100, 'y': 100}, {'x': 80, 'y': 100}, {'x': 60, 'y': 100}] # Start within typical play area
    snake_direction = 'RIGHT'
    score = 0
    place_food()

def place_food():
    global food_pos
    # Ensure food spawns within the visible play area (not overlapping score or menu elements if they existed)
    # For a full-screen game, this is essentially the whole screen minus padding.
    max_x = (SCREEN_WIDTH // BLOCK_SIZE) - 1
    max_y = (SCREEN_HEIGHT // BLOCK_SIZE) - 1

    food_x = random.randrange(max_x) * BLOCK_SIZE
    food_y = random.randrange(max_y) * BLOCK_SIZE
    
    # Regenerate if food spawns on the snake
    while any(segment['x'] == food_x and segment['y'] == food_y for segment in snake):
        food_x = random.randrange(max_x) * BLOCK_SIZE
        food_y = random.randrange(max_y) * BLOCK_SIZE
        
    food_pos = [food_x, food_y]

def draw_snake_body(snake_list, color):
    for segment in snake_list:
        pygame.draw.rect(SCREEN, color, (segment['x'], segment['y'], BLOCK_SIZE, BLOCK_SIZE))

def draw_food_item(food_position):
    pygame.draw.rect(SCREEN, RED, (food_position[0], food_position[1], BLOCK_SIZE, BLOCK_SIZE))

def display_score_ingame(score_val):
    draw_text(f"Score: {score_val}", FONT_SMALL, WHITE, SCREEN_WIDTH - 80, 20, center=False) # Top right corner

# --- Menu Screens ---

def main_menu(event):
    global game_state
    SCREEN.fill(BLACK)
    draw_text("Snake Game Deluxe", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

    if create_button("Play", FONT_MEDIUM, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 200, 70, GREEN, LIGHT_GREY, event):
        reset_game()
        game_state = 'PLAYING'
    if create_button("Customize", FONT_MEDIUM, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90, 200, 70, BLUE, LIGHT_GREY, event):
        game_state = 'CUSTOMIZE'
    if create_button("Quit", FONT_MEDIUM, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180, 200, 70, RED, LIGHT_GREY, event):
        pygame.quit()
        sys.exit()

def customize_menu(event):
    global game_state, snake_color
    SCREEN.fill(BLACK)
    draw_text("Customize Snake Skin", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

    color_options = [
        (GREEN, "Lime"), (BLUE, "Blue"), (YELLOW, "Yellow"), (ORANGE, "Orange"), (WHITE, "White")
    ]
    
    y_offset = SCREEN_HEIGHT // 2 - 50
    for i, (color, name) in enumerate(color_options):
        button_x = SCREEN_WIDTH // 2
        button_y = y_offset + i * 60
        if create_button(name, FONT_SMALL, button_x, button_y, 150, 40, color, LIGHT_GREY, event):
            snake_color = color

    if create_button("Back to Menu", FONT_MEDIUM, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 250, 70, GREY, LIGHT_GREY, event):
        game_state = 'MENU'

def game_over_menu(event):
    global game_state, score
    SCREEN.fill(BLACK)
    draw_text("GAME OVER!", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(f"Final Score: {score}", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    if create_button("Play Again", FONT_MEDIUM, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 250, 70, GREEN, LIGHT_GREY, event):
        reset_game()
        game_state = 'PLAYING'
    if create_button("Main Menu", FONT_MEDIUM, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 190, 250, 70, BLUE, LIGHT_GREY, event):
        game_state = 'MENU'

# --- Main Game Loop ---
def run_game_loop():
    global snake_direction, food_pos, score, game_state, snake

    clock = pygame.time.Clock()

    while True: # Main application loop, keeps window open
        current_event = None # Reset event for button handling per frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_state == 'PLAYING':
                    if event.key == pygame.K_UP and snake_direction != 'DOWN':
                        snake_direction = 'UP'
                    elif event.key == pygame.K_DOWN and snake_direction != 'UP':
                        snake_direction = 'DOWN'
                    elif event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                        snake_direction = 'LEFT'
                    elif event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                        snake_direction = 'RIGHT'
            # Pass mouse click events to button handler only if it's a MOUSEBUTTONDOWN event
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current_event = event

        if game_state == 'MENU':
            main_menu(current_event)
        elif game_state == 'CUSTOMIZE':
            customize_menu(current_event)
        elif game_state == 'GAME_OVER':
            game_over_menu(current_event)
        elif game_state == 'PLAYING':
            # Game Logic
            head_x, head_y = snake[0]['x'], snake[0]['y'] # Get head from first segment
            if snake_direction == 'UP':
                head_y -= BLOCK_SIZE
            elif snake_direction == 'DOWN':
                head_y += BLOCK_SIZE
...             elif snake_direction == 'LEFT':
...                 head_x -= BLOCK_SIZE
...             elif snake_direction == 'RIGHT':
...                 head_x += BLOCK_SIZE
... 
...             new_head = {'x': head_x, 'y': head_y}
... 
...             # Check for collisions
...             collided_with_wall = (new_head['x'] < 0 or new_head['x'] >= SCREEN_WIDTH or
...                                   new_head['y'] < 0 or new_head['y'] >= SCREEN_HEIGHT)
...             collided_with_self = new_head in snake[1:] # Check against body, not head itself
... 
...             if collided_with_wall or collided_with_self:
...                 game_state = 'GAME_OVER'
...             else:
...                 snake.insert(0, new_head) # Add new head
... 
...                 # Food collision
...                 if new_head['x'] == food_pos[0] and new_head['y'] == food_pos[1]:
...                     score += 10
...                     place_food()
...                 else:
...                     snake.pop() # Remove tail if no food eaten
... 
...                 # Drawing
...                 SCREEN.fill(BLACK)
...                 draw_snake_body(snake, snake_color)
...                 draw_food_item(food_pos)
...                 display_score_ingame(score)
... 
...         pygame.display.flip()
...         clock.tick(FPS) # Control game speed, only relevant during PLAYING state
... 
... if __name__ == '__main__':
...     run_game_loop()
