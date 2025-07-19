import pygame
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Clash - Naruto Edition")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Load and scale images
menu_bg = pygame.transform.scale(pygame.image.load("menu_bg.png").convert(), (WIDTH, HEIGHT))
background = pygame.transform.scale(pygame.image.load("background.png").convert(), (WIDTH, HEIGHT))
cloud = pygame.transform.scale(pygame.image.load("cloud.png").convert_alpha(), (200, 100))
naruto_skin = pygame.transform.scale(pygame.image.load("naruto.png").convert_alpha(), (50, 80))
sasuke_skin = pygame.transform.scale(pygame.image.load("sasuke.png").convert_alpha(), (50, 80))
kunai_img = pygame.transform.scale(pygame.image.load("kunai.png").convert_alpha(), (30, 30))
shuriken_img = pygame.transform.scale(pygame.image.load("shuriken.png").convert_alpha(), (30, 30))
sword_img = pygame.transform.scale(pygame.image.load("sword.png").convert_alpha(), (30, 30))
axe_img = pygame.transform.scale(pygame.image.load("axe.png").convert_alpha(), (30, 30))
wand_img = pygame.transform.scale(pygame.image.load("wand.png").convert_alpha(), (30, 30))

# Cloud position
cloud_x = 0

# Weapon switching
weapon_options = [kunai_img, shuriken_img, sword_img, axe_img, wand_img]
weapon_names = ["Kunai", "Shuriken", "Sword", "Axe", "Wand"]
player1_weapon_index = 0
player2_weapon_index = 1

# Draw animated background
def draw_background():
    screen.blit(background, (0, 0))
    screen.blit(cloud, (cloud_x, 50))

# Health bars only (no chakra)
def draw_health_bar(health, x_offset):
    pygame.draw.rect(screen, BLACK, (x_offset, 20, 200, 10))
    pygame.draw.rect(screen, RED, (x_offset, 20, health * 2, 10))

# Menu screen
def show_menu():
    global player1_weapon_index, player2_weapon_index
    screen.blit(menu_bg, (0, 0))
    title = font.render("Stickman Clash - Naruto Edition", True, WHITE)
    play = font.render("Press ENTER to Play", True, WHITE)
    quit_game = font.render("Press Q to Quit", True, WHITE)
    switch1 = font.render("Press W to Switch Player 1 Weapon", True, WHITE)
    switch2 = font.render("Press E to Switch Player 2 Weapon", True, WHITE)
    p1_weapon = font.render(f"Player 1 Weapon: {weapon_names[player1_weapon_index]}", True, WHITE)
    p2_weapon = font.render(f"Player 2 Weapon: {weapon_names[player2_weapon_index]}", True, WHITE)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    screen.blit(play, (WIDTH//2 - play.get_width()//2, 120))
    screen.blit(quit_game, (WIDTH//2 - quit_game.get_width()//2, 160))
    screen.blit(switch1, (WIDTH//2 - switch1.get_width()//2, 210))
    screen.blit(switch2, (WIDTH//2 - switch2.get_width()//2, 250))
    screen.blit(p1_weapon, (WIDTH//2 - p1_weapon.get_width()//2, 300))
    screen.blit(p2_weapon, (WIDTH//2 - p2_weapon.get_width()//2, 340))

    pygame.display.update()

# Show winner screen
def show_winner(winner_text):
    while True:
        screen.fill(BLACK)
        message = font.render(winner_text, True, WHITE)
        instruction = font.render("Press ENTER to go to Menu or Q to Quit", True, WHITE)
        screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # go back to menu
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Game loop
def game_loop():
    global cloud_x, player1_weapon_index, player2_weapon_index
    player1_x, player1_y = 100, 300
    player2_x, player2_y = 600, 300
    player1_vel_y = 0
    player2_vel_y = 0
    gravity = 1
    jump_strength = -15
    on_ground_y = 300
    player1_health = 100
    player2_health = 100
    attack_cooldown_p1 = 0
    attack_cooldown_p2 = 0
    running = True

    while running:
        screen.fill(WHITE)
        draw_background()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_a]: player1_x -= 5
        if keys[pygame.K_d]: player1_x += 5
        if keys[pygame.K_w] and player1_y >= on_ground_y: player1_vel_y = jump_strength
        if keys[pygame.K_LEFT]: player2_x -= 5
        if keys[pygame.K_RIGHT]: player2_x += 5
        if keys[pygame.K_UP] and player2_y >= on_ground_y: player2_vel_y = jump_strength

        # Gravity
        player1_vel_y += gravity
        player2_vel_y += gravity
        player1_y += player1_vel_y
        player2_y += player2_vel_y

        # Floor collision
        if player1_y > on_ground_y:
            player1_y = on_ground_y
            player1_vel_y = 0
        if player2_y > on_ground_y:
            player2_y = on_ground_y
            player2_vel_y = 0

        # Attack
        if attack_cooldown_p1 > 0: attack_cooldown_p1 -= 1
        if attack_cooldown_p2 > 0: attack_cooldown_p2 -= 1

        if keys[pygame.K_SPACE] and attack_cooldown_p1 == 0:
            if abs(player1_x - player2_x) < 60 and abs(player1_y - player2_y) < 60:
                player2_health -= 10
            attack_cooldown_p1 = 20

        if keys[pygame.K_RETURN] and attack_cooldown_p2 == 0:
            if abs(player2_x - player1_x) < 60 and abs(player2_y - player1_y) < 60:
                player1_health -= 10
            attack_cooldown_p2 = 20

        # Draw players and weapons
        screen.blit(naruto_skin, (player1_x - 25, player1_y - 80))
        screen.blit(weapon_options[player1_weapon_index], (player1_x + 20, player1_y - 20))
        screen.blit(sasuke_skin, (player2_x - 25, player2_y - 80))
        screen.blit(weapon_options[player2_weapon_index], (player2_x + 20, player2_y - 20))

        draw_health_bar(player1_health, 50)
        draw_health_bar(player2_health, 550)

        cloud_x -= 1
        if cloud_x < -200:
            cloud_x = WIDTH

        pygame.display.update()
        clock.tick(60)

        # Check for win condition
        if player1_health <= 0:
            show_winner("Player 2 Wins!")
            return
        if player2_health <= 0:
            show_winner("Player 1 Wins!")
            return

# Main menu loop
running = True
while running:
    show_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game_loop()
            elif event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_w:
                player1_weapon_index = (player1_weapon_index + 1) % len(weapon_options)
            elif event.key == pygame.K_e:
                player2_weapon_index = (player2_weapon_index + 1) % len(weapon_options)

pygame.quit()
sys.exit()
