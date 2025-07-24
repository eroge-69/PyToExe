import pgzrun
from pgzero.builtins import Actor, keys
import random

HEIGHT = 550
WIDTH = 1000

player = Actor('raumschiff207711')
player.x = 250
player.y = 300

richtung = None

# Hintergrund
hg_x = 0
speed = 4

obstacles = []

counter = 0
game_over = False

def increase_counter():
    global counter, game_over
    if not game_over:
        counter += 1
        clock.schedule_unique(increase_counter, 1.0)

increase_counter()

def draw():
    screen.clear()
    screen.blit('ah', (hg_x, 0))

    if game_over:
        screen.draw.text(f"Game Over! Zeit: {counter} Sekunden", center=(WIDTH//2, HEIGHT//2 - 40), fontsize=60, color="red")
        screen.draw.text("Drücke 'R' zum Neustarten", center=(WIDTH//2, HEIGHT//2 + 40), fontsize=40, color="white")
    else:
        player.draw()
        for obs in obstacles:
            obs.draw()
        screen.draw.text(f"Zeit: {counter}", topleft=(10, 10), fontsize=40, color="white")


def update():
    global richtung, hg_x, speed, game_over

    if game_over:
        return

    if hg_x < -7422:
        hg_x = 0
    else:
        hg_x -= speed

    speed += 0.01

    if richtung == 'up' and player.y > 0:
        player.y -= 11
    elif richtung == 'down' and player.y < HEIGHT - player.height:
        player.y += 11

    for obs in obstacles:
        obs.x -= speed

    obstacles[:] = [o for o in obstacles if o.right > 0]

    for obs in obstacles:
        if player.colliderect(obs):
            game_over = True

    
    if len(obstacles) < 6 and random.randint(1, 100) < 3:
        new_obs = Actor('asteroid211') 
        new_obs.x = WIDTH + 100
        new_obs.y = random.randint(0, HEIGHT - new_obs.height)
        obstacles.append(new_obs)

    if len(obstacles) < 3:
        new_obs = Actor('asteroid211') 
        new_obs.x = WIDTH + 100
        new_obs.y = random.randint(0, HEIGHT - new_obs.height)
        obstacles.append(new_obs)

def on_key_down(key):
    global richtung, game_over, counter, speed, obstacles, player, hg_x

    if game_over and key == keys.R:
        game_over = False
        counter = 0
        speed = 4
        obstacles.clear()
        player.x = 250
        player.y = 300
        hg_x = 0
        increase_counter() 

    if key == keys.UP:
        richtung = 'up'
    elif key == keys.DOWN:
        richtung = 'down'

def on_key_up(key):
    global richtung
    if key == keys.UP or key == keys.DOWN:
        richtung = None

pgzrun.go()
