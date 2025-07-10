import pygame
import random

from pygame import mixer

# Initialize Pygame
pygame.init()

# Starting the mixer
mixer.init()

# Loading the song
mixer.music.load("My Best Friend is a.mp3")

# Setting the volume
mixer.music.set_volume(0.7)

# Start playing the song
mixer.music.play()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Run Mayita")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fox properties
fox_image = pygame.image.load("Mayita.png").convert_alpha() # Load your fox image
fox_rect = fox_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
fox_speed = 5

# Coin properties
coin_image = pygame.image.load("cheese.png").convert_alpha() # Load your coin image
coins = [] # List to store active coins
score = 0

running = True
clock = pygame.time.Clock()

start_time = pygame.time.get_ticks()
countdown_duration = 107000 # 107 seconds

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    elapsed_time = pygame.time.get_ticks() - start_time
    remaining_time = max(0, countdown_duration - elapsed_time)

    if remaining_time == 0:
        print("Countdown finished!")
        running = False # End the game or transition

    # Display remaining_time on screen

    # Fox Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and fox_rect.left > 0:
        fox_rect.x -= fox_speed
    if keys[pygame.K_RIGHT] and fox_rect.right < SCREEN_WIDTH:
        fox_rect.x += fox_speed

    # Coin Spawning (example: spawn a new coin every 45 frames)
    if random.randint(1, 60) == 1:
        new_coin_rect = coin_image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), 0))
        coins.append(new_coin_rect)

    # Coin Movement and Collision
    for coin_rect in coins[:]: # Iterate over a copy to allow removal
        coin_rect.y += 3 # Coin falling speed
        if coin_rect.colliderect(fox_rect):
            score += 1
            coins.remove(coin_rect)
        elif coin_rect.top > SCREEN_HEIGHT: # Remove if off-screen
            coins.remove(coin_rect)

    # Drawing
    screen.fill(BLACK) # Clear screen
    screen.blit(fox_image, fox_rect)
    for coin_rect in coins:
        screen.blit(coin_image, coin_rect)

    # Display score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip() # Update the displaypyinstaller myscript.py
    clock.tick(30) # Limit frame rate

# Done! Print the final score
print(f"Game over! Final score: {score}")

pyinstaller coin_game.py