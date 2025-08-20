import random
import time
import pygame
import os


def load_highscore():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))


pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
pygame.display.set_caption("Skyscrapped")
running = True
px = 375
py = 200
yvelocity = 0
speed = 6
ex = 100
extwo = 100
hurt_timer = 60
ph = 10
level = 1
next_level = False
enemy_here = False
enemytwo_here = False
Highscore = load_highscore()


def collision():
    global py, yvelocity, px, hurt_timer, ph, running
    if py >= 400:
        py = 400
        yvelocity = 0
    if px >= 610:
        px = 610
    if px <= 20:
        px = 20

    # Enemy collision detection
    if (px < ex + 50 and px + 50 > ex and py + 100 > 400
            and py < 500):  # Check if player is at ground level with enemy
        if hurt_timer <= 0:
            if enemy_here:
                hurt_timer = 60
                ph -= 1
                if ph <= 0:
                    running = False
    if (px < extwo + 50 and px + 50 > extwo and py + 100 > 400
            and py < 500):  # Check if player is at ground level with enemy
        if hurt_timer <= 0:
            if enemytwo_here:
                hurt_timer = 60
                ph -= 1
                if ph <= 0:
                    running = False


height = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if py == 400:
                    yvelocity = 20

    # Check for held keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        speed = 12
        height = 25
    else:
        speed = 6
        height = 0
    if keys[pygame.K_a]:
        px -= speed
    if keys[pygame.K_d]:
        px += speed

    if ex > px:
        ex -= 2
    if ex < px:
        ex += 2

    if extwo > px:
        extwo -= 2
    if extwo < px:
        extwo += 2

    if next_level:
        level += 1
        next_level = False
        if random.randint(1, 3) == 1:
            enemy_here = False
            if random.randint(1, 3) == 1:
                enemytwo_here = False
            else:
                enemytwo_here = True
        else:
            enemy_here = True
        ex = random.randint(250, 550)
        extwo = random.randint(250, 550)
        yvelocity = 0
        py = 400
        px = 100

    if level > Highscore:
        Highscore = level
        save_highscore(Highscore)

    screen.fill((255, 255, 255))
    pygame.draw.polygon(screen, (145, 145, 145), [(0, 490), (800, 490),
                                                  (800, 600), (0, 600)])
    pygame.draw.polygon(screen, (200, 200, 200), [(650, 500), (650, 0),
                                                  (800, 0), (800, 500)])
    pygame.draw.polygon(screen, (200, 200, 200), [(0, 500), (0, 0), (30, 0),
                                                  (30, 500)])

    pygame.draw.polygon(screen, (200, 200, 200), [(0, 500), (800, 500),
                                                  (800, 600), (0, 600)])
    pygame.draw.polygon(screen, (255, 255, 255), [(0, 500), (0, 0), (20, 0),
                                                  (20, 500)])
    pygame.draw.polygon(screen, (255, 255, 255), [(660, 500), (660, 0),
                                                  (800, 0), (800, 500)])

    pygame.draw.polygon(screen, (50, 205, 205), [(90, 410), (310, 410),
                                                 (310, 290), (90, 290)])

    pygame.draw.polygon(screen, (100, 255, 255), [(100, 400), (300, 400),
                                                  (300, 300), (100, 300)])

    pygame.draw.polygon(screen, (200, 255, 255), [(160, 320), (280, 390),
                                                  (290, 380), (170, 310)])
    yvelocity -= 1
    py -= yvelocity
    collision()
    if enemy_here:
        pygame.draw.polygon(screen, (150, 50, 50), [(ex, 500), (50 + ex, 500),
                                                    (50 + ex, 0 + 400),
                                                    (ex, 0 + 400)])
        pygame.draw.polygon(screen, (200, 100, 100), [(ex + 10, 490),
                                                      (40 + ex, 490),
                                                      (40 + ex, 410),
                                                      (ex + 10, 410)])
    if enemytwo_here:
        pygame.draw.polygon(screen, (150, 50, 50), [(extwo, 500),
                                                    (50 + extwo, 500),
                                                    (50 + extwo, 0 + 400),
                                                    (extwo, 0 + 400)])
        pygame.draw.polygon(screen, (200, 100, 100), [(extwo + 10, 490),
                                                      (40 + extwo, 490),
                                                      (40 + extwo, 410),
                                                      (extwo + 10, 410)])
    if px == 610:
        if py > 350 - height:
            next_level = True

    pygame.draw.polygon(screen, (50, 50, 50), [(px, 100 + py),
                                               (50 + px, 100 + py),
                                               (50 + px, height + py),
                                               (px, height + py)])
    pygame.draw.polygon(screen, (100, 100, 100), [(px + 10, 90 + py),
                                                  (40 + px, 90 + py),
                                                  (40 + px, height + py + 10),
                                                  (px + 10, height + py + 10)])

    pygame.draw.polygon(screen, (0, 0, 0), [(710, 350), (660, 350), (660, 500),
                                            (710, 500)])

    pygame.draw.rect(screen, (100, 0, 0), (0, 0, 120, 40))
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, ph * 10, 20))

    # Display level text
    level_text = small_font.render(f"Level {level}", True, (0, 0, 0))
    screen.blit(level_text, (10, 50))

    level_text = small_font.render(f"Highscore {Highscore}", True, (0, 0, 0))
    screen.blit(level_text, (10, 70))

    # Display game title and instructions
    lines = ["Skyscrapped", "SHIFT: sprint", "A/D: move", "SPACE: jump"]
    y_offset = 510
    if level == 1:
        for i, line in enumerate(lines):
            if i == 0:  # Title
                text = font.render(line, True, (0, 0, 0))
            else:  # Instructions
                text = small_font.render(line, True, (0, 0, 0))
            screen.blit(text, (10, y_offset + i * 20))
            if i == 0:
                y_offset += 10  # Extra space after title

    pygame.display.flip()
    pygame.time.Clock().tick(60)
    if hurt_timer > 0:
        hurt_timer -= 1
f = 255
for i in range(10):
    screen.fill((int(0 + f), int(0 + f), int(0 + f)))
    pygame.display.flip()
    time.sleep(0.05)
    f -= 255 / 10

pygame.quit()
