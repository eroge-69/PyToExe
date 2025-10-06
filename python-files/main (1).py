import pygame, random, sys

pygame.init()
WIDTH, HEIGHT = 480, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter 🚀")
clock = pygame.time.Clock()

# Ranglar
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)

font = pygame.font.SysFont(None, 36)

# O'yinchi (raketa)
player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 80, 50, 50)
player_speed = 6

# O‘qlar
bullets = []
bullet_speed = -8

# Dushmanlar (asteroidlar)
enemies = []
enemy_speed = 4
spawn_timer = 0

score = 0
game_over = False

# Ovoz qo‘shish (agar xohlasang)
# pygame.mixer.init()
# shoot_sound = pygame.mixer.Sound("laser.wav")

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if game_over and e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            # Restart
            enemies.clear()
            bullets.clear()
            score = 0
            game_over = False
            enemy_speed = 4
            player.x, player.y = WIDTH//2 - 25, HEIGHT - 80

    keys = pygame.key.get_pressed()

    if not game_over:
        # Harakat
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed

        # Otish (SPACE)
        if keys[pygame.K_SPACE]:
            if len(bullets) < 6:  # cheklangan o‘qlar
                bullets.append(pygame.Rect(player.centerx - 3, player.top - 10, 6, 10))
                # shoot_sound.play()  # agar ovoz bo‘lsa

        # O‘qlarni harakatlantirish
        for b in bullets[:]:
            b.y += bullet_speed
            if b.y < 0:
                bullets.remove(b)

        # Dushman yaratish
        spawn_timer += 1
        if spawn_timer > 30:
            spawn_timer = 0
            enemy_x = random.randint(20, WIDTH - 40)
            enemies.append(pygame.Rect(enemy_x, -40, 40, 40))

        # Dushmanlar harakati
        for enemy in enemies[:]:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:
                enemies.remove(enemy)

            # To‘qnashuv (raketa bilan)
            if enemy.colliderect(player):
                game_over = True

        # O‘q va dushman to‘qnashuvi
        for b in bullets[:]:
            for enemy in enemies[:]:
                if b.colliderect(enemy):
                    bullets.remove(b)
                    enemies.remove(enemy)
                    score += 1
                    # Har 10 ochkoda tezlik oshadi
                    if score % 10 == 0:
                        enemy_speed += 1
                    break

    # Chizish
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, player)

    for b in bullets:
        pygame.draw.rect(screen, YELLOW, b)

    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    if game_over:
        over_text = font.render("GAME OVER! Press R to Restart", True, RED)
        screen.blit(over_text, (40, HEIGHT//2 - 20))

    pygame.display.flip()
    clock.tick(60)