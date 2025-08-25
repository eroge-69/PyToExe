import pygame
import random
import sys
import os

# -------------------- Initialize Pygame --------------------
pygame.init()

# -------------------- Screen dimensions and title --------------------
# Get the current display resolution for full-screen mode
display_info = pygame.display.Info()
screen_width = display_info.current_w
screen_height = display_info.current_h
game_window = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Snake Game")

# -------------------- Colors --------------------
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)
blue = (0, 0, 255)
orange = (255, 165, 0)

# -------------------- Game Properties --------------------
game_clock = pygame.time.Clock()
block_size = 10
difficulty_levels = {
    "Easy": 10,
    "Medium": 15,
    "Hard": 25
}

# Font for score and messages
font_style = pygame.font.SysFont("Helvetica", 20)
large_font = pygame.font.SysFont("Helvetica", 50)
menu_font = pygame.font.SysFont("Helvetica", 30)

# -------------------- High Score Functions --------------------
high_score_file = "high_score.txt"

def load_high_score():
    """Loads the high score from a file."""
    try:
        with open(high_score_file, "r") as file:
            score = int(file.read())
            return score
    except (IOError, ValueError):
        # File doesn't exist or is empty/invalid
        return 0

def save_high_score(score):
    """Saves the high score to a file."""
    with open(high_score_file, "w") as file:
        file.write(str(score))

# -------------------- Game Functions --------------------

def display_score(score, high_score):
    """Displays the current score and high score on the screen."""
    score_text = font_style.render("Score: " + str(score), True, white)
    high_score_text = font_style.render("High Score: " + str(high_score), True, white)
    game_window.blit(score_text, [0, 0])
    game_window.blit(high_score_text, [0, 25])

def message(msg, color, y_offset=0):
    """Displays a message on the screen with an optional vertical offset."""
    game_msg = large_font.render(msg, True, color)
    text_rect = game_msg.get_rect(center=(screen_width / 2, screen_height / 3 + y_offset))
    game_window.blit(game_msg, text_rect)

def draw_snake(block_size, snake_list):
    """Draws the snake on the screen."""
    for block in snake_list:
        pygame.draw.rect(game_window, green, [block[0], block[1], block_size, block_size])

def generate_food_position():
    """Generates a random position for the food."""
    food_x = round(random.randrange(0, screen_width - block_size) / 10.0) * 10.0
    food_y = round(random.randrange(0, screen_height - block_size) / 10.0) * 10.0
    return food_x, food_y

def start_menu():
    """Displays the main menu and handles difficulty selection."""
    menu = True
    difficulty = "Medium"
    
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    menu = False
                elif event.key == pygame.K_UP:
                    levels = list(difficulty_levels.keys())
                    current_index = levels.index(difficulty)
                    if current_index > 0:
                        difficulty = levels[current_index - 1]
                elif event.key == pygame.K_DOWN:
                    levels = list(difficulty_levels.keys())
                    current_index = levels.index(difficulty)
                    if current_index < len(levels) - 1:
                        difficulty = levels[current_index + 1]
        
        game_window.fill(black)
        message("Snake Game", orange, -100)
        message("Press ENTER to Start", white, 100)

        # Draw difficulty buttons
        y_pos = screen_height / 2
        for level, speed in difficulty_levels.items():
            color = green if level == difficulty else white
            text = menu_font.render(f"Difficulty: {level}", True, color)
            text_rect = text.get_rect(center=(screen_width / 2, y_pos))
            game_window.blit(text, text_rect)
            y_pos += 40

        pygame.display.update()
        game_clock.tick(15)

    return difficulty_levels[difficulty]

def game_loop(initial_speed):
    """The main game loop."""
    game_state = "playing"
    high_score = load_high_score()
    
    # Game variables
    lead_x = screen_width / 2
    lead_y = screen_height / 2
    change_x = 0
    change_y = 0
    snake_list = []
    snake_length = 1
    food_x, food_y = generate_food_position()
    current_speed = initial_speed
    
    is_fullscreen = True

    while game_state != "quit":
        if game_state == "playing":
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and change_x != block_size:
                        change_x = -block_size
                        change_y = 0
                    elif event.key == pygame.K_RIGHT and change_x != -block_size:
                        change_x = block_size
                        change_y = 0
                    elif event.key == pygame.K_UP and change_y != block_size:
                        change_y = -block_size
                        change_x = 0
                    elif event.key == pygame.K_DOWN and change_y != -block_size:
                        change_y = block_size
                        change_x = 0
                    elif event.key == pygame.K_F11:
                        # Toggle full-screen mode
                        is_fullscreen = not is_fullscreen
                        if is_fullscreen:
                            pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                        else:
                            pygame.display.set_mode((720, 480))

            # --- Game Logic ---
            if lead_x >= screen_width or lead_x < 0 or lead_y >= screen_height or lead_y < 0:
                game_state = "game_over"

            lead_x += change_x
            lead_y += change_y

            snake_head = [lead_x, lead_y]
            snake_list.append(snake_head)
            if len(snake_list) > snake_length:
                del snake_list[0]

            for block in snake_list[:-1]:
                if block == snake_head:
                    game_state = "game_over"

            if lead_x == food_x and lead_y == food_y:
                food_x, food_y = generate_food_position()
                snake_length += 1
                current_speed += 0.5

            # --- Drawing ---
            game_window.fill(black)
            pygame.draw.rect(game_window, red, [food_x, food_y, block_size, block_size])
            draw_snake(block_size, snake_list)
            display_score(snake_length - 1, high_score)
            pygame.display.update()
            
            game_clock.tick(current_speed)

        elif game_state == "game_over":
            score = snake_length - 1
            if score > high_score:
                high_score = score
                save_high_score(high_score)

            game_window.fill(black)
            message("Game Over!", red, -50)
            message("Press C to Play Again or Q to Quit", white, 50)
            display_score(score, high_score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_state = "quit"
                    elif event.key == pygame.K_c:
                        main() # Restart the main loop

    pygame.quit()
    sys.exit()

def main():
    initial_speed = start_menu()
    game_loop(initial_speed)

# -------------------- Start the game --------------------
if __name__ == "__main__":
    main()
