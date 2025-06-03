import pygame
import random

pygame.init()

a = 900
b = 700
White = (255,255,255)
Black = (0,0,0)
red = (255,0,0)

screen = pygame.display.set_mode((a,b))
pygame.display.set_caption('Troll Puzzle')
run = True
show_inst1 = True
sys_font = pygame.font.SysFont('arial',30)
inst1 = sys_font.render('Nothing here you can exit click the button',True,Black) 
inst1_rect = inst1.get_rect()
inst1_rect.center = (a/2 , b/2)

inst2 = sys_font.render('lol this is a fake button,find a real button to exit!',True,Black) 
inst2_rect = inst2.get_rect()
inst2_rect.center = (a/2 , b/2)

button_real = None
button = pygame.Rect(a-500,b-300,100,50)
clock = pygame.time.Clock()

while run:
    screen.fill(White)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button.collidepoint(event.pos):
                show_inst1 = False
                button.x = random.randint(0,a-32)
                button.y = random.randint(0,b-32)

                if button_real == None:
                    button_real = pygame.Rect(random.randint(0,a-40),random.randint(0,b-40),100,100)

            if not show_inst1 and button and button_real.collidepoint(event.pos):
                print('You found it')
                run = False
            
    if show_inst1:
        screen.blit(inst1,inst1_rect)
    else:
        screen.blit(inst2,inst2_rect)
        if button_real:
            pygame.draw.rect(screen,White,button_real)
        
    
    pygame.draw.rect(screen,red,button)
    clock.tick(60)
    pygame.display.update()
pygame.quit()