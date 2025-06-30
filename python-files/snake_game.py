import pygame, random, os, time

pygame.init()
#crunch_sound = pygame.mixer.Sound('Sounds/crunch.wav')
#hit_sound = pygame.mixer.Sound('Sounds/hit.wav')
#point_sound = pygame.mixer.Sound('Sounds/point.wav')
#swoosh_sound = pygame.mixer.Sound('Sounds/swoosh.wav')

# Colors
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
black = (0, 0, 0)
blue1 = (93,216,228)
blue2 = (84,194,205)

# Creating game window
screen_width = 640
screen_height = 640
grid_size = 20
grid_width = screen_width/grid_size
grid_height = screen_height/grid_size

def drawGrid(surface, color):
    for y in range(1, int(grid_height)-1):
        for x in range(1, int(grid_width)-1):
            if (x+y)%2 == 0:
                r = pygame.Rect((x*grid_size, y*grid_size), (grid_size,grid_size))          # pygame.Rect((left, top), (width, height))
                pygame.draw.rect(surface, color, r)
            else:
                rr = pygame.Rect((x*grid_size, y*grid_size), (grid_size,grid_size))
                pygame.draw.rect(surface, color, rr)

gameWindow = pygame.display.set_mode((screen_width,screen_height))

# Game Title
pygame.display.set_caption("SnakeWithSnake")
pygame.display.update()
fps = 60
clock = pygame.time.Clock()

# Defining font and text over screen
def text_screen(text, color, x, y, size):
    myfont = pygame.font.SysFont(None, size)
    screen_text = myfont.render(text, True, color)
    gameWindow.blit(screen_text, [x,y])

# def text_screen(text , color, x, y, size):
#     font = pygame.font.SysFont(None, size)
#     screen_text = font.render(text, True, color)
#     gameWindow.blit(screen_text, screen_text.get_rect(center = gameWindow.get_rect().center))
#     print(screen_text.get_rect(center = gameWindow.get_rect().center))


# Ploting snake 
def plot_snake(suface, color, snake_list, size):
    for x,y in snake_list:
        pygame.draw.rect(suface, color, [x, y, size, size], 0, 5,5,5,5,5)

def drawMain(surface):
    surface.fill(blue1)
    drawGrid(surface, (102, 255, 51))
    pygame.draw.rect(surface, black, [20,20,600,600], 1)
        
# Welcome Screen
def welcome():
    exit_game = False
    # Check if hiscore file exists
    if os.path.exists("Hiscore.txt"):
        with open("Hiscore.txt","r+") as f:
            if f.read() == "":
                f.write("0")
    else:
        with open("Hiscore.txt", "w") as f:
            f.write("0")
    with open("Hiscore.txt", "r") as f:
        hiscore = f.read()
    while not exit_game:
        # gameWindow.fill((0, 204, 153))
        drawMain(gameWindow)

        text_screen("Welcome", black, 245, 217, 50)
        text_screen("Press Space Bar To Play", black, 119, 300, 50)
        text_screen(f"Hi-Score : {hiscore}", black, 235, 500, 40)
        pygame.display.update()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    #swoosh_sound.play()
                    gameloop()



# Game Loop
def gameloop():

    # Game specific variables
    exit_game = False
    game_over = False
    pause = False
    
    # Properties of snake
    snake_x = screen_width/2
    snake_y = screen_height/2
    velocity_x = 0
    velocity_y = 0
    init_velocity = 3
    snake_list  = []
    snake_length = 1

    food_x = random.randint(grid_size+1, screen_width - (grid_size*2) - 1)
    food_y = random.randint(grid_size+1, screen_height - (grid_size*2) - 1)


    # Individual score
    score = 0

    with open("Hiscore.txt", "r") as f:
        hiscore = f.read()

    while not exit_game:

        # Pause condition
        if pause:
            text_screen("Pause", yellow, 225, 266, 100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        #point_sound.play()
                        pause = False
                        
        # Game over condition
        elif game_over:
            with open("Hiscore.txt", "w") as f:
                f.write(str(hiscore))

            drawMain(gameWindow)

            text_screen("Game Over", black, 187, 220, 70)
            text_screen("Press Enter To Continue", black, 35, 300, 70)
            text_screen(f"Score : {score}", black, 262, 450, 40)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        #swoosh_sound.play()
                        time.sleep(1)
                        gameloop()
                        
        # Game logic
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        velocity_x = 0
                        velocity_y = -init_velocity
                    elif event.key == pygame.K_DOWN:
                        velocity_x = 0
                        velocity_y = init_velocity
                    elif event.key == pygame.K_LEFT:
                        velocity_x = -init_velocity
                        velocity_y = 0
                    elif event.key == pygame.K_RIGHT:
                        velocity_x = init_velocity
                        velocity_y = 0
                    elif event.key == pygame.K_p:
                        #point_sound.play()
                        pause = True
                    elif event.key == pygame.K_w:
                        welcome()
                    elif event.key == pygame.K_q:
                        drawMain(gameWindow)
                        text_screen("Thanks for playing SnakeWithSnake", black, 70, 300, 40)
                        pygame.display.update()
                        clock.tick(fps)
                        time.sleep(2)
                        exit_game = True

                        
            snake_x = snake_x + velocity_x
            snake_y = snake_y + velocity_y

            if abs(snake_x - food_x) < 8 and abs(snake_y - food_y) < 8:
                score += 10
                #crunch_sound.play()
                food_x = random.randint(grid_size+1, screen_width - (grid_size*2) - 1)
                food_y = random.randint(grid_size+1, screen_height - (grid_size*2) - 1)
                snake_length += 5    
                if int(hiscore) < score:
                    hiscore = score
                    
            # gameWindow.fill((0, 0, 0))
            gameWindow.fill(blue1)

            text_screen(f"Score : {score}", black, 5, 3, 25)
            text_screen("Press Q to quit      Press W for Welcome Screen", black, 110, 3, 25)
            text_screen(f"Hi-Score : {hiscore}", black, 515, 3, 25)


            drawGrid(gameWindow, (102, 255, 51))
            pygame.draw.rect(gameWindow, black, [20,20,600,600], 1)
            
            # Ploting food
            pygame.draw.rect(gameWindow, red, [food_x, food_y, grid_size, grid_size], 0, 5,5,5,5,5)
            pygame.draw.rect(gameWindow, black, [food_x, food_y, grid_size, grid_size], 1, 5,5,5,5,5)            

            plot_snake(gameWindow, (102, 0, 102), snake_list, grid_size)
            
            head = [snake_x, snake_y]
            snake_list.append(head)

            if len(snake_list) > snake_length:
                del snake_list[0]

            if (snake_x < 22) or (snake_x > screen_width-(grid_size*2)+2) or (snake_y < 22) or (snake_y > screen_height-(grid_size*2)+2):
                #hit_sound.play()
                time.sleep(1)
                game_over = True

            if head in snake_list[:-1]:
                #hit_sound.play()
                time.sleep(1)
                game_over = True

            
        pygame.display.update()
        clock.tick(fps)
    pygame.quit()
    quit()

welcome()