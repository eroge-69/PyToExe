import pygame
import random
import time

 
pygame.init()

 
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('لعبة الروبوت')

 
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

 
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 60)

 
robot_width = 100
robot_height = 150
robot_x = WIDTH // 2 - robot_width // 2
robot_y = HEIGHT - robot_height - 10
robot_speed = 5

 
monster_width = 60
monster_height = 60
monsters = []

 
giant_monster_width = 150
giant_monster_height = 200
giant_monster = None

 
game_over = False
fighting = False

 
pygame.mixer.music.load("background_music.mp3")  # ضع مسار الموسيقى هنا
pygame.mixer.music.play(-1)  # تكرار الموسيقى

 
def draw_robot(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, robot_width, robot_height))

 
def draw_monster(x, y):
    pygame.draw.rect(screen, RED, (x, y, monster_width, monster_height))

 
def draw_giant_monster(x, y):
    pygame.draw.rect(screen, GREEN, (x, y, giant_monster_width, giant_monster_height))

 
def draw_text(text, font, color, x, y):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

 
def fight_monsters():
    global fighting, monsters
    fighting = True
   
    for monster in monsters:
        monster[1] += 2  

 
def fight_giant_monster():
    global game_over, giant_monster
     
    if giant_monster[1] <= robot_y + robot_height:
        draw_text("جيت لي برجليك!", big_font, WHITE, WIDTH // 2 - 150, HEIGHT // 2)
        pygame.display.update()
        time.sleep(2)
        game_over = True

 
def game_loop():
    global robot_x, robot_y, game_over, fighting, monsters, giant_monster

    running = True
    clock = pygame.time.Clock()

 
    draw_text("يَلَّا للدفاع عن العالم!", big_font, WHITE, WIDTH // 4, HEIGHT // 4)
    pygame.display.update()
    time.sleep(2)

    while running:
        screen.fill((0, 0, 0))   

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    robot_x -= robot_speed
                if event.key == pygame.K_RIGHT:
                    robot_x += robot_speed
                if event.key == pygame.K_DOWN:
                    robot_y += robot_speed
                if event.key == pygame.K_UP:
                    robot_y -= robot_speed
                if event.key == pygame.K_RETURN:                           fight_monsters()
                if event.key == pygame.K_ESCAPE:   
                    running = False

        
        draw_robot(robot_x, robot_y)

        
        if fighting:
            
            if random.random() < 0.01:   
                monster_x = random.randint(0, WIDTH - monster_width)
                monster_y = 0
                monsters.append([monster_x, monster_y])

           
            for monster in monsters[:]:
                draw_monster(monster[0], monster[1])
                if monster[1] > HEIGHT:   
                    monsters.remove(monster)

             
            for monster in monsters:
                if monster[1] >= robot_y and monster[1] <= robot_y + robot_height:
                    draw_text("هجوم على الوحش!", font, WHITE, WIDTH // 2 - 100, HEIGHT // 2)
                    monsters.remove(monster)
                    break

         
        if not giant_monster:
            giant_monster = [WIDTH // 2 - giant_monster_width // 2, 100]

        if giant_monster:
            draw_giant_monster(giant_monster[0], giant_monster[1])
            fight_giant_monster()

        
        pygame.display.update()
        clock.tick(60)

 
game_loop()

# إنهاء اللعبة
pygame.quit()
