import pygame
import sys
from enemies import Enemy
pygame.init()
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
fps = 24
clock.tick(fps)
playercolor = (255,255,0)
bg_color = (0,162,255)
text_color = (0,0,0)
game_font = pygame.font.SysFont("", 30)
coin_image = pygame.image.load("images/Coin.png")
#Player
player_image = pygame.image.load("images/player.png")
playerx = 10
playery = 40
playerwidth = 64
playerheight = 64
playerspeed = 15
score = 0
enemy_image = pygame.image.load("images/enemy.png")
image = pygame.font.SysFont("", 30)
def draw_enemies():
    screen.blit(enemy_image,enemy)
    if player.colliderect(enemy):
        sys.exit()






enemy = pygame.Rect(300,100,64,64)
coin_width = coin_image.get_width()
coin_height = coin_image.get_height()
coins = [pygame.Rect(300, 100, coin_width, coin_height),pygame.Rect(250, 170, coin_width, coin_height),
         pygame.Rect(200, 120, coin_width, coin_height)]
def draw_coins():
    global score
    for coin in coins:
        screen.blit(coin_image, (coin[0], coin[1]))
    for coin in coins:
        if coin.colliderect(player):
            coins.remove(coin)
            score += 1
            print(score)
enemy_x = 300
enemy_y = 100





player = pygame.Rect(playerx, playery, playerwidth, playerheight)
def draw_text(text, font, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))

def draw_sprites():
    screen.blit(player_image, player)
    draw_enemies()
    draw_coins()
    draw_text(("Score: " + str(score)), game_font, (255,0,0), 10, 10)








#!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!MAIN LOOP!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        key = pygame.key.get_pressed()

        if key[pygame.K_d]:
            player.x = player.x + playerspeed
        elif key[pygame.K_a]:
            player.x = player.x - playerspeed
        elif key[pygame.K_w]:
            player.y = player.y - playerspeed
        elif key[pygame.K_s]:
            player.y = player.y + playerspeed



    screen.fill(bg_color)

    #pygame.draw.rect(screen, playercolor, (playerx, playery, playerwidth, playerheight))
    draw_sprites()
    pygame.display.flip()

