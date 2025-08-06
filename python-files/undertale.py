# undertale_battle_graphic.py
import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Undertale Battle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load the sprite (ensure frisk_sprite.png is in the same folder)
try:
    sprite = pygame.image.load("frisk_sprite.png").convert_alpha()
    sprite = pygame.transform.scale(sprite, (100, 100))  # Resize if needed
except FileNotFoundError:
    print("Error: frisk_sprite.png not found!")
    sys.exit()

# Game variables
player_hp = 20
monster_hp = 10
monster_name = "Flowey"
font = pygame.font.Font(None, 36)

def draw_text(text, x, y):
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x, y))

def battle():
    clock = pygame.time.Clock()
    running = True

    while running and player_hp > 0 and monster_hp > 0:
        screen.fill(BLACK)
        screen.blit(sprite, (50, 400))  # Display sprite
        draw_text(f"Your HP: {player_hp}", 50, 50)
        draw_text(f"{monster_name}'s HP: {monster_hp}", 50, 100)
        draw_text("* Choose: [F]ight [S]pare", 50, 150)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:  # Fight
                    damage = random.randint(1, 5)
                    monster_hp -= damage
                    draw_text(f"* You dealt {damage} damage!", 50, 200)
                    pygame.display.flip()
                    time.sleep(1)
                elif event.key == pygame.K_s:  # Spare
                    if random.random() < 0.5:
                        draw_text(f"* {monster_name} was spared!", 50, 200)
                        running = False
                    else:
                        draw_text(f"* {monster_name} refuses!", 50, 200)
                        pygame.display.flip()
                        time.sleep(1)

        # Monster attack
        if monster_hp > 0:
            damage = random.randint(1, 3)
            player_hp -= damage
            draw_text(f"* {monster_name} dealt {damage} damage!", 50, 250)
            pygame.display.flip()
            time.sleep(1)

        pygame.display.flip()
        clock.tick(30)

    if player_hp <= 0:
        draw_text("* You lost... GAME OVER.", 50, 300)
    elif monster_hp <= 0:
        draw_text("* You won!", 50, 300)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import random
    print("Loading Undertale-inspired battle...")
    battle()