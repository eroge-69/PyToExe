import pygame, random, os

pygame.init()

# Screen
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("War of Heat")
icon = pygame.image.load("war.png")
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load("flag.png")
playerX = 370
playerY = 480
playerSpeed = 1.2
playerBullets = []
playerBulletImg = pygame.image.load("bullet.png")
lastPlayerShot = 0
playerFireDelay = 300  # milliseconds
playerHealth = 3  # 3 lives

# Enemy
enemyImg = pygame.image.load("enemy.png")
enemies = []
numEnemies = 3
enemyBullets = []
enemyBulletImg = pygame.image.load("enemybullet.png")

for i in range(numEnemies):
    enemies.append({
        "x": random.randint(50, 700),
        "y": random.randint(50, 150),
        "speed": 0.8,
        "dir": 1,
        "last_shot": 0,
        "health": 2  # each enemy takes 2 hits
    })

enemyFireDelay = 1500  # enemies shoot every 1.5 sec
playerBulletSpeed = 6  # faster player bullet
enemyBulletSpeed = 3   # slower enemy bullet

# Score
score = 0
highscore = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt","r") as f:
        try: highscore = int(f.read())
        except: highscore = 0

font = pygame.font.Font(None, 36)

# Game states
game_over = False
victory = False

def reset_game():
    global playerX, playerY, playerBullets, enemyBullets, enemies, score, game_over, victory, playerHealth
    playerX = 370
    playerY = 480
    playerBullets = []
    enemyBullets = []
    enemies.clear()
    for i in range(numEnemies):
        enemies.append({
            "x": random.randint(50, 700),
            "y": random.randint(50, 150),
            "speed": 0.8,
            "dir": 1,
            "last_shot": 0,
            "health": 2
        })
    score = 0
    game_over = False
    victory = False
    playerHealth = 3

# Draw health bar
def draw_health(x, y, health):
    for i in range(health):
        pygame.draw.rect(screen, (255,0,0), (x + i*35, y, 30, 20))  # red hearts

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((255,213,154))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over and not victory:
        # Movement
        if keys[pygame.K_w] and playerY > 0:
            playerY -= playerSpeed
        if keys[pygame.K_s] and playerY < 536:
            playerY += playerSpeed
        if keys[pygame.K_a] and playerX > 0:
            playerX -= playerSpeed
        if keys[pygame.K_d] and playerX < 736:
            playerX += playerSpeed

        # Shooting (Player)
        if keys[pygame.K_j]:
            now = pygame.time.get_ticks()
            if now - lastPlayerShot > playerFireDelay:
                playerBullets.append([playerX+16, playerY])
                lastPlayerShot = now

        # Update player bullets
        for b in playerBullets[:]:
            b[1] -= playerBulletSpeed
            if b[1] < 0:
                playerBullets.remove(b)

        # Update enemies
        for e in enemies:
            e["x"] += e["speed"] * e["dir"]
            if e["x"] <= 0 or e["x"] >= 736:
                e["dir"] *= -1

            # Enemy shooting
            now = pygame.time.get_ticks()
            if now - e["last_shot"] > enemyFireDelay:
                enemyBullets.append([e["x"]+16, e["y"]+32])
                e["last_shot"] = now

        # Update enemy bullets
        for b in enemyBullets[:]:
            b[1] += enemyBulletSpeed
            if b[1] > 600:
                enemyBullets.remove(b)

        # Collision check (player bullets -> enemies)
        for b in playerBullets[:]:
            for e in enemies[:]:
                if e["x"] < b[0] < e["x"]+64 and e["y"] < b[1] < e["y"]+64:
                    playerBullets.remove(b)
                    e["health"] -= 1
                    if e["health"] <= 0:
                        enemies.remove(e)
                        score += 10
                    break

        # Collision check (enemy bullets -> player)
        for b in enemyBullets[:]:
            if playerX < b[0] < playerX+64 and playerY < b[1] < playerY+64:
                enemyBullets.remove(b)
                playerHealth -= 1
                if playerHealth <= 0:
                    game_over = True
                    if score > highscore:
                        highscore = score
                        with open("highscore.txt","w") as f:
                            f.write(str(highscore))

        # Victory check
        if len(enemies) == 0:
            victory = True
            if score > highscore:
                highscore = score
                with open("highscore.txt","w") as f:
                    f.write(str(highscore))

        # Draw player
        screen.blit(playerImg, (playerX, playerY))

        # Draw bullets
        for b in playerBullets:
            screen.blit(playerBulletImg, (b[0], b[1]))
        for b in enemyBullets:
            screen.blit(enemyBulletImg, (b[0], b[1]))

        # Draw enemies
        for e in enemies:
            screen.blit(enemyImg, (e["x"], e["y"]))

        # Draw score
        text = font.render(f"Score: {score}  Highscore: {highscore}", True, (0,0,0))
        screen.blit(text, (10,10))

        # Draw health bar
        draw_health(650, 10, playerHealth)

    else:
        # Game Over / Victory screen
        if game_over:
            msg = font.render("GAME OVER - Press R to Restart", True, (255,0,0))
        else:
            msg = font.render("VICTORY! - Press R to Restart", True, (0,200,0))
        screen.blit(msg, (200,300))
        hs = font.render(f"Highscore: {highscore}", True, (0,0,0))
        screen.blit(hs, (300,350))

        if keys[pygame.K_r]:
            reset_game()

    pygame.display.update()
    clock.tick(60)
