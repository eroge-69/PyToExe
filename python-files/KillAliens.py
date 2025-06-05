import pygame
import random

pygame.init()

ENRED = (160, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (25, 255, 255)
EnColours = (ENRED, GREEN, BLUE)

# Variables
ShootSound = pygame.mixer.Sound('Assets\8-bit-laser-151672.mp3')
KillSound = pygame.mixer.Sound('Assets\8-bit-explosion-3-340456.mp3')
HurtSound = pygame.mixer.Sound('Assets\gameboy-pluck-41265.mp3')


Running = True
sWidth = 400
sHeight = 600
rWidth = 75
rHeight = 25
rXPos = ((sWidth // 2) - (rWidth / 2))
rYPos = 570
r2Width = 10
r2Height = 25
r2XPos = (rXPos + (rWidth // 2) - (r2Width / 2))
r2YPos = (rYPos - rHeight)
rVel = 12
eYPos = 50
eWidth = 50
eHeight = 50
eColour = GREEN
enemy_spawn_timer = 0
enemy_spawn_interval = 60
font = pygame.font.SysFont(None, 48)
eVel = random.randint(1, 10)

enemies = []
bullets = []

score = 0
lives = 10

clock = pygame.time.Clock()

# Screen
Screen = pygame.display.set_mode((sWidth, sHeight))
pygame.display.set_caption("KillAliens")

pygame.mixer.music.load('Assets\Deltarune OST_ 30 - Chaos King.mp3')
pygame.mixer.music.play(-1)

# GameLoop
while Running:
    clock.tick(60)
    eXPos = random.randint(0, sWidth - eWidth)

    # KeyPresses d 
    Keys = pygame.key.get_pressed()
    if Keys[pygame.K_a]:
        rXPos -= rVel
        r2XPos -= rVel
    if Keys[pygame.K_d]:
        rXPos += rVel
        r2XPos += rVel

    if rXPos < 0:
        rXPos = 0
        r2XPos = (rXPos + (rWidth // 2) - (r2Width // 2))
    if rXPos + rWidth > sWidth:
        rXPos = sWidth - rWidth
        r2XPos = (rXPos + (rWidth // 2) - (r2Width // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.Sound.play(ShootSound)
                bullets.append({
                    "bXPos": r2XPos,
                    "bYPos": r2YPos,
                    "bWidth": 5,
                    "bHeight": 25
                })

    enemy_spawn_timer += 1
    if enemy_spawn_timer >= enemy_spawn_interval:
        enemies.append({
            "eXPos": random.randint(0, sWidth - eWidth),
            "eYPos": 50,
            "eWidth": eWidth,
            "eHeight": eHeight,
            "eColour": random.choice(EnColours),
            "eVel": random.randint(1, 10)
        })
        enemy_spawn_timer = 0

    Screen.fill(BLACK)
    # Body of Mode + Cannon
    pygame.draw.rect(Screen, RED, pygame.Rect(rXPos, rYPos, rWidth, rHeight))        
    pygame.draw.rect(Screen, RED, pygame.Rect(r2XPos, r2YPos, r2Width, r2Height))

    # Move all bullets upward
    for bullet in bullets:
        bullet["bYPos"] -= 10  # Adjust speed as desired

    for enemy in enemies:
        enemy["eYPos"] += enemy["eVel"]

    # --- Bullet-enemy collision detection and removal ---
    bullets_to_remove = []
    enemies_to_remove = []

    for bullet in bullets:
        bullet_rect = pygame.Rect(
            int(bullet["bXPos"]),
            int(bullet["bYPos"]),
            int(bullet["bWidth"]),
            int(bullet["bHeight"])
        )
        for enemy in enemies:
            enemy_rect = pygame.Rect(
                int(enemy["eXPos"]),
                int(enemy["eYPos"]),
                int(enemy["eWidth"]),
                int(enemy["eHeight"])
            )
            if bullet_rect.colliderect(enemy_rect):
                bullets_to_remove.append(bullet)
                enemies_to_remove.append(enemy)
                pygame.mixer.Sound.play(KillSound)
                score += 1

    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)
    # --- End collision detection ---

    # Optionally, remove bullets that go off the top of the screen
    bullets = [bullet for bullet in bullets if bullet["bYPos"] + bullet["bHeight"] > 0]

    # Draw all bullets
    for bullet in bullets:
        pygame.draw.rect(
            Screen,
            bullet.get("bColour", (255, 255, 255)),  # default to white if not set
            pygame.Rect(
                int(bullet["bXPos"]),
                int(bullet["bYPos"]),
                int(bullet["bWidth"]),
                int(bullet["bHeight"])
            )
        )

    for enemy in enemies:
        pygame.draw.rect(
            Screen,
            enemy.get("eColour", (0, 0, 255)),
            pygame.Rect(
                int(enemy["eXPos"]),
                int(enemy["eYPos"]),
                int(enemy["eWidth"]),
                int(enemy["eHeight"])
            )
        )


    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    Screen.blit(score_surface, (20, 20))
    lives_surface = font.render(f"Lives: {lives}", True, (255, 255, 255))
    Screen.blit(lives_surface, (20, 60))

    if lives == 0:
        pygame.quit()

    # Remove enemies that reach the bottom and decrease lives
    enemies_to_remove_bottom = []
    for enemy in enemies:
        if enemy["eYPos"] > sHeight:
            enemies_to_remove_bottom.append(enemy)
            lives -= 1
            pygame.mixer.Sound.play(HurtSound)

    for enemy in enemies_to_remove_bottom:
        if enemy in enemies:
            enemies.remove(enemy)

    pygame.display.update()

pygame.quit()

