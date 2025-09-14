# importing
import pygame
from sys import exit
from random import randint, choice

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk1 = pygame.image.load('game/graphics/Player/player_walk_1.png').convert_alpha()
        player_walk2 = pygame.image.load('game/graphics/Player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk1, player_walk2]
        self.player_index = 0
        self.player_jump = pygame.image.load('game/graphics/Player/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (80,300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('game/audio/jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()
    
    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300 
    
    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
            
    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'fly':
            fly_1 = pygame.image.load('game/graphics/fly/fly1.png').convert_alpha()
            fly_2 = pygame.image.load('game/graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 210
        else:
            snail_1 = pygame.image.load('game/graphics/snail/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('game/graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0 
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

def  colliosion_spirte():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else: return True

def display_score():
    current_time = (pygame.time.get_ticks() - start_time) // 1000
    score_surf = score_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center = (400, 50))
    screen.blit(score_surf, score_rect)
    return current_time
    
def player_animation():
    global player_surf, player_index

    if player_rect.bottom < 300:
        player_surf = player_jump
    else:
       player_index += 0.1
       if player_index >= len(player_walk): player_index = 0
       player_surf = player_walk[int(player_index)]

# game window
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Jumpy!')
clock = pygame.time.Clock()
game_active = False
start_time = 0
score = 0
bg = pygame.mixer.Sound('game/audio/music.wav')
bg.set_volume(0.7)
bg.play()


# groups
player = pygame.sprite.GroupSingle()
player.add(Player()) 

obstacle_group = pygame.sprite.Group()

# fonts
score_font = pygame.font.Font('game/font/Pixeltype.ttf', 50)
title_font = pygame.font.Font('game/font/Pixeltype.ttf', 100)

# background
sky_surf = pygame.image.load('game/graphics/Sky.png').convert()
ground_surf = pygame.image.load('game/graphics/ground.png').convert()

# snail
snail_frame1 = pygame.image.load('game/graphics/snail/snail1.png').convert_alpha()
snail_frame2 = pygame.image.load('game/graphics/snail/snail2.png').convert_alpha()
snail_frame = [snail_frame1, snail_frame2]
snail_frame_idex = 0
snail_surf = snail_frame[snail_frame_idex]

# fly
fly_frame1 = pygame.image.load('game/graphics/fly/fly1.png').convert_alpha()
fly_frame2 = pygame.image.load('game/graphics/fly/fly2.png').convert_alpha()
fly_frame = [fly_frame1, fly_frame2]
fly_frame_idex = 1
fly_surf = fly_frame[fly_frame_idex]

obstacle_rect_list = []

# player setup
player_walk1 = pygame.image.load('game/graphics/Player/player_walk_1.png').convert_alpha()
player_walk2 = pygame.image.load('game/graphics/Player/player_walk_2.png').convert_alpha()
player_walk = [player_walk1, player_walk2]
player_index = 0
player_jump = pygame.image.load('game/graphics/Player/jump.png').convert_alpha()

player_surf = player_walk[player_index]
player_rect = player_surf.get_rect(midbottom =(80, 300))
player_gravity = 0

# intro sceen
player_stand = pygame.image.load('game/graphics/Player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center = (400, 200)) 

game_name = title_font.render('Jumpy!', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center = (400, 80))

game_message = score_font.render('Press space to run', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center = (400, 330))

# timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

snail_animation_timer = pygame.USEREVENT +2
pygame.time.set_timer(snail_animation_timer, 500)

fly_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_animation_timer, 200)

# game loop
while True:

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_rect.collidepoint(event.pos) and player_rect.bottom >= 300:
                      player_gravity = -20

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom >= 300:
                        player_gravity = -20
        
        else:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                game_active = True
                
                score = 0
                start_time = pygame.time.get_ticks()
            
            
        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))    
                    
            if event.type == snail_animation_timer:
                if snail_frame_idex == 0: snail_frame_idex = 1
                else: snail_frame_idex = 0
                snail_surf = snail_frame[snail_frame_idex]

            if event.type == fly_animation_timer:
                if fly_frame_idex == 0: fly_frame_idex = 1
                else: fly_frame_idex = 0
                fly_surf = fly_frame[fly_frame_idex]


    
    # game
    if game_active:

        # rendering background
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, 300))

        score = display_score()

        # rendering and moving player
        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        # collions
        game_active = colliosion_spirte()
        
    # intro / game over screen
    else: 
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)
        obstacle_rect_list.clear()
        player_rect.midbottom = (80, 300)
        player_gravity = 0

        score_message = score_font.render(f"Your score: {score}", False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center = (400, 330))  
        screen.blit(game_name, game_name_rect)
        
        
        if score == 0:
            screen.blit(game_message, game_message_rect)
        
        else:
            screen.blit(score_message, score_message_rect)

    # updating the display and setting the frame rate
    pygame.display.update()
    clock.tick(60)
