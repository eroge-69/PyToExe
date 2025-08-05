import pygame
import random
pygame.init()
pygame.mixer.init()



white = (255,255,255)
red = (255,0,0)
black = (0,0,0)
r = (0,0,55)

screen_width = 800
screen_height = 600
game_window = pygame.display.set_mode((screen_width,screen_height))

sound = pygame.mixer.Sound('eat.mp3')
bgimg = pygame.image.load('img.jpg')
bgimg = pygame.transform.scale(bgimg,(screen_width,screen_height)).convert_alpha()

pygame.display.set_caption("Snakes like AS")
pygame.display.update()
#Game Control variablee

font = pygame.font.SysFont("jokerman",52)
clock = pygame.time.Clock()
fps = 30

def plot_snake(game_window,color,snake_list,snake_size):
    for x,y in snake_list:
        pygame.draw.rect(game_window,color,[x,y,snake_size,snake_size])
    

def text_s(text,color,x,y):
    s_text = font.render(text,True,color)
    game_window.blit(s_text,[x,y])
def welcome():
    exit_game = False
    while not exit_game:
        game_window.fill(white)
        game_window.blit(bgimg,(0,0))
        text_s("Welcome to the World of Nags",red,2,240)
        text_s("       Press Space",red,2,300)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game == True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer.music.load('back.mp3')
                    pygame.mixer.music.play()
                    gameloop()

        pygame.display.update()
        clock.tick(30)        
def gameloop():
    game_over = False
    exit_game = False
    snake_x = 69
    snake_y = 76
    snake_size = 16
    food_size = 16
    clock = pygame.time.Clock()
    fps = 30
    velocity_x = 0
    velocity_y = 0
    e_velo = 5
    food_x = random.randint(20,screen_width/2)
    food_y = random.randint(20,screen_height/2)
    score = 0
    font = pygame.font.SysFont("jokerman",55)
    snake_list = []
    snake_lenght = 1
        
    while not exit_game:
        if game_over:
            game_window.fill(white)
            game_window.blit(bgimg,(0,0))
            text_s("Game Over , Press Enter",red,100,200)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        welcome()
        else:   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        velocity_x = e_velo
                        velocity_y = 0
                    if event.key == pygame.K_LEFT:
                        velocity_x = -e_velo
                        velocity_y = 0
                    if event.key == pygame.K_UP:
                        velocity_y = -e_velo
                        velocity_x = 0
                    if event.key == pygame.K_DOWN:
                        velocity_y = e_velo
                        velocity_x = 0

            
        
            snake_x += velocity_x
            snake_y += velocity_y

            if abs(snake_x - food_x)<9 and abs(snake_y - food_y)<9:
                score += 1
                food_x = random.randint(60,screen_width/2)
                food_y = random.randint(60,screen_height/2)
                snake_lenght += 5
                '''
                f =  open('hiscore.txt','w')
                h = f.write(str(score))
                a = open('hiscore.txt','r')
                b = a.read()
                
                print(b)
                '''
                sound.play()
                
            if snake_x < 0 or snake_x > screen_width or snake_y > screen_height or snake_y < 0:
                game_over = True
                pygame.mixer.music.load('game over.mp3')
                pygame.mixer.music.play()
            
                
                    
            game_window.fill(white)
            game_window.blit(bgimg,(0,0))
            text_s("Score:- "+ str(score),red,30,5)
            pygame.draw.rect(game_window,red,[food_x,food_y,snake_size,snake_size])   
            pygame.draw.rect(game_window,black,[snake_x,snake_y,snake_size,snake_size])
            plot_snake(game_window,black,snake_list,snake_size)

            head = []
            head.append(snake_x)
            head.append(snake_y)
            snake_list.append(head)
            
                
            if len(snake_list) > snake_lenght:
                del snake_list[0]
                
            if head in snake_list[:-1]:
                game_over = True
                pygame.mixer.music.load('game over.mp3')
                pygame.mixer.music.play()
                
        pygame.display.update()
        clock.tick(fps)#Frames per second

        
     
    
    pygame.quit()
    quit()
welcome()    

            
