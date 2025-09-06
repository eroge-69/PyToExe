
import pygame
import math
import random
from pygame import mixer

# initialize the game
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# background
background = pygame.image.load('backround (1).png')

# background sound
mixer.music.load('spring-forest-nature-332842.mp3')
mixer.music.play(-1)

# Caption and icon
pygame.display.set_caption("Haunt the bird")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

# player
playerImg = pygame.image.load('player-removebg-preview.png')
playerX = 330
playerY = 335
playerX_change = 0

# enemy
birdImg = pygame.image.load('bird.png')
doveImg = pygame.image.load('dove.png')

enemyImg = []
enemyX = []
enemyY = []
enemyStartX = []
enemyStartY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = random.randint(2, 10)

for i in range(num_of_enemies):
    if random.random() < 0.5:  # random choice between bird and dove
        enemyImg.append(birdImg)
        startX = random.randint(0, 200)
        startY = random.randint(50, 150)
        enemyX.append(startX)
        enemyY.append(startY)
        enemyStartX.append(startX)
        enemyStartY.append(startY)
        enemyX_change.append(0.3)   # bird moves right
        enemyY_change.append(40)
    else:
        enemyImg.append(doveImg)
        startX = random.randint(600, 736)
        startY = random.randint(50, 150)
        enemyX.append(startX)
        enemyY.append(startY)
        enemyStartX.append(startX)
        enemyStartY.append(startY)
        enemyX_change.append(-0.3)  # dove moves left
        enemyY_change.append(40)

# bullet
bulletImg = pygame.image.load('shell__1_-removebg-preview.png')
bulletX = 0
bulletY = 390
bulletX_change = 0
bulletY_change = 5
bullet_state = "ready"  # "ready" = cannot see bullet, "fire" = bullet is moving

# score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
textY = 10

# missed
missed_value = 0

# game over text
over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (0, 255, 0))
    screen.blit(score, (x, y))

def show_missed(x, y):
    missed_text = font.render("Missed : " + str(missed_value), True, (255, 0, 0))
    screen.blit(missed_text, (x, y + 40))

def game_over_text():
    over = over_font.render("Game Over", True, (255, 0, 0))
    screen.blit(over, (200, 250))
    gameover_Sound = mixer.Sound('080205_life-lost-game-over-89697.mp3')
    gameover_Sound.play()

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    return distance < 27

# Game loop
running = True
while running:

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -2
            if event.key == pygame.K_RIGHT:
                playerX_change = 2
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if bullet_state == "ready":
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
                    bullet_Sound = mixer.Sound('doom-shotgun-2017-80549.mp3')
                    bullet_Sound.play()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Player movement
    playerX += playerX_change
    playerX = max(0, min(playerX, 672))  # keep inside screen

    # Enemy movement
    for i in range(num_of_enemies):

        # Game over
        if missed_value >= 49:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            mixer.music.stop()
            game_over_text()
            running = False
            break

        enemyX[i] += enemyX_change[i]

        # Transformation logic: reset enemies when they go out of bounds
        if enemyImg[i] == birdImg and enemyX[i] > 750:
            enemyX[i] = enemyStartX[i]
            enemyY[i] = enemyStartY[i]
            missed_value += 1

        elif enemyImg[i] == doveImg and enemyX[i] <= 50:
            enemyX[i] = enemyStartX[i]
            enemyY[i] = enemyStartY[i]
            missed_value += 1

        # Collision
        if isCollision(enemyX[i], enemyY[i], bulletX, bulletY):
            bulletY = playerY
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = enemyStartX[i]
            enemyY[i] = enemyStartY[i]
            explosion_Sound = mixer.Sound('mixkit-arcade-retro-game-over-213.wav')
            explosion_Sound.play()

        enemy(enemyX[i], enemyY[i], i)

    # Bullet movement
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change
        if bulletY <= 0:
            bulletY = playerY
            bullet_state = "ready"

    player(playerX, playerY)
    show_score(textX, textY)
    show_missed(textX, textY)

    pygame.display.update()
