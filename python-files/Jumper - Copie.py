import pgzrun
HEIGHT = 500
WIDTH = 500
TITLE = "Jumper"
platform = Rect(0, 450, 500, 100)
player = Rect(0, 400, 50, 50)
obstacle = Rect(450, 425, 25, 25)
sun = Rect(0, 0, 100, 100)
score = 1
def draw():
    screen.fill((127.5, 127.5, 255))
    screen.draw.filled_rect(platform, ((0, 127.5, 0)))
    screen.draw.filled_rect(player, "pink")
    screen.draw.filled_rect(obstacle, "white")
    screen.draw.filled_rect(sun, "yellow")
    screen.draw.text(str(score), (250, 250), fontsize = 50, color = "black")
def update():
    global score
    global speed
    playerx = player.x
    playery = player.y
    obstaclex = obstacle.x
    player.y += 2.5
    obstacle.x -= 7.5
    if obstaclex < 12.5:
        obstacle.x = 450
        score += 1
    if player.colliderect(platform):
        player.x = playerx
        player.y = playery
    if obstacle.colliderect(player):
        obstacle.x = 450
        score -= 1
def on_mouse_down():
    player.y = 350
pgzrun.go()
