import pygame
from sys import exit 
from random import randint

def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = font.render(f'Score: {current_time}',False,(64,64,64))
    score_rect = score_surf.get_rect(center = (400,80))
    screen.blit(score_surf,score_rect)
    return current_time

def obstacle_movement(obstacle_list):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= 5
            
            
            screen.blit(snail_surf,obstacle_rect)

        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100 ]    

        return obstacle_list
    else: return []

#initiate pygame
pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption("Runner")
clock = pygame.time.Clock()
font = pygame.font.Font("Python/.venv/Main Scripts/font/Pixeltype.ttf", 50)
game_active = False
start_time = 0
score = 0

sky_surf = pygame.image.load("Python/.venv/Main Scripts/graphics/Sky.png").convert()
ground_surf = pygame.image.load("Python/.venv/Main Scripts/graphics/Ground.png").convert()

#score_surf = font.render("Runner", False, (64,64,64))
#score_rect = score_surf.get_rect(center = (400,50))

#Obstacles
snail_surf = pygame.image.load("Python/.venv/Main Scripts/graphics/snail/snail1.png").convert_alpha()
snail_rect = snail_surf.get_rect(bottomright = (600,300))

obstacle_rect_list = []

#Player in-game
player_surf = pygame.image.load("Python/.venv/Main Scripts/graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(midbottom = (80,300))
player_gravity = 0

#Intro Screen/ Restart
player_stand = pygame.image.load('Python/.venv/Main Scripts/graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand,0,2)
player_stand_rect = player_stand.get_rect(center = (400,200))

#tITLE text
Game_title = font.render("Pixel Runner", False, (111,196,169))
game_title_rect = Game_title.get_rect(center = (400,50))

game_message = font.render('Press Space to Run',False,(111,196,169))
game_message_rect = game_message.get_rect(center = (400,320))

#timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,1400)

#While loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit() 
#Game active loop
        if game_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_rect.collidepoint(event.pos):
                    player_gravity = -20

                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom == 300:
                    player_gravity = -20
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                snail_rect.left = 800
                start_time = int(pygame.time.get_ticks() / 1000)

        if event.type == obstacle_timer and game_active:
            obstacle_rect_list.append(snail_surf.get_rect(bottomright = (randint(900,1100), 300)))

    #drawing surfaces on-screen    
    if game_active:
        screen.blit(sky_surf,(0,0))
        screen.blit(ground_surf,(0,300))
        display_score()
        #pygame.draw.rect(screen, "#c0e8ec",score_rect)
        #pygame.draw.rect(screen, "#c0e8ec",score_rect,10)
        #screen.blit(score_surf,score_rect)
        score = display_score()

    #Speed of snail and setting it back 
        snail_rect.x -= 4
        if snail_rect.right <= 0: snail_rect.left = 800
        screen.blit(snail_surf,snail_rect)

        #Player
        player_gravity += 1
        player_rect.y += player_gravity
        if player_rect.bottom >= 300: player_rect.bottom = 300
        screen.blit(player_surf,player_rect)

        # Obstacle movement
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)

        #collision
        if snail_rect.colliderect(player_rect):
            game_active = False
    else:
        screen.fill((94,129,162))
        screen.blit(player_stand,player_stand_rect)

        score_message = font.render(f"Your score: {score}",False,(111,196,169))
        score_message_rect = score_message.get_rect(center = (400,330))
        screen.blit(Game_title,game_title_rect)

        if score == 0: screen.blit(game_message,game_message_rect)
        else: screen.blit(score_message,score_message_rect)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_active = True
    
    pygame.display.update()
    clock.tick(60)


