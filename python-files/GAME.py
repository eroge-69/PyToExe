import pygame
import time

pygame.init()
pygame.mixer.init()



w = 800
h = 600
px, py = 55, 392

T = []

frames = [
    pygame.image.load("E1.png"),
    pygame.image.load("E2.png"),
    pygame.image.load("E3.png"),
    pygame.image.load("E4.png"),
    pygame.image.load("E5.png"),
    pygame.image.load("E6.png"),
    pygame.image.load("E7.png"),
    pygame.image.load("E8.png"),
    pygame.image.load("E9.png"),
    pygame.image.load("E10.png")
]



frames = [pygame.transform.scale(f, (45, 45)) for f in frames] 



screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Geometry Bat")

Player = pygame.image.load("Player.png")
World = pygame.image.load("BackGround.png")
Thistle = pygame.image.load("Thistle.png")

World = pygame.transform.scale(World, (w,h))
Player = pygame.transform.scale(Player, (45, 45))
Thistle = pygame.transform.scale(Thistle, (42, 42))

Pr = Player.get_rect()
Tr = Thistle.get_rect()


jump_speed = 7
frame_index = 0
frame_delay = 10
frame_count = 0
active = True
done = False
stop = False
vel_y = 0
live = True
spawn_timer = 0
spawn_delay = 90
back = pygame.mixer.music.load("music.mp3")
death = pygame.mixer.Sound("Death.mp3")
pygame.mixer.music.play(-1)


def reset():
    global px, py, vel_y, T, active, done, stop, live

    px, py = 55, 395
    vel_y = 0
    T = []

    active = True
    done = False
    stop = False
    live = True
    pygame.mixer.music.play(-1)
    


run = True
clock = pygame.time.Clock()
while run:
    clock.tick(60)
    gravity = 1
    jump_speed = -18

    ground_y = 395
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if live:
            if event.type == pygame.MOUSEBUTTONDOWN and py >=  ground_y:
                vel_y = jump_speed
            vel_y += gravity
            py += vel_y

            if py >= ground_y:
                py = ground_y
                vel_y = 0
        
            
            

    Pr.x, Pr.y = px, py
    
    
    screen.blit(World, (0,0))

    
    

    
    

    if live:
        key = pygame.key.get_pressed()
        if (key[pygame.K_SPACE] and py >=  ground_y):
            vel_y = jump_speed 
    
        vel_y += gravity
        py += vel_y

        if py >= ground_y:
            py = ground_y
            vel_y = 0
    
    collision = False
    for obs in T:
        Tr.x, Tr.y = obs["x"], obs["y"]
        if Pr.colliderect(Tr) and active:
            collision = True
    
    if collision:
        active = False
        stop = True
        frame_index = 0
        frame_count = 0
            
        

    
        

    if not active and not done:
        death.play()
        pygame.mixer.music.pause()
        
        frame_count += 2
        if frame_count >= frame_delay:
            frame_count = 0
            frame_index += 1
        
        if frame_index >= len(frames):
            frame_index = len(frames) - 1
            done = True
        screen.blit(frames[frame_index], (px, py))
        live = False
    
    else:
        screen.blit(Player, (px, py))
    
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        spawn_timer = 0
        T.append({"x": 550, "y": 400})
        

    
    
    for obs in T:
        if not stop:
            obs["x"] -= 5
        screen.blit(Thistle, (obs["x"], obs["y"]))
    
    
        

    
    if done:
        reset()


    pygame.display.update()

pygame.quit()