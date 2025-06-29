import pygame
from sys import exit
import random
import time

# Цвета
green = [0, 255, 0]
red = [255, 0, 0]
blue = [0, 0, 255]
yellow = [255, 255, 0]  # Исправлено: желтый цвет должен быть [255,255,0], а не [0,255,255]

pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 36)

# Экран
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.image = pygame.Surface((rect.width, rect.height))
        self.image.fill(yellow)
        self.rect = self.image.get_rect(topleft=rect.topleft)

# Персонаж
body_size = pygame.Rect(450, 900, 135, 135)
player_sprite = Player(body_size)

# Группа спрайтов для падающих объектов
all_sprites = pygame.sprite.Group()

# Таймер для появления новых объектов
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 300)

# Очки
score = 0
last_score_time = pygame.time.get_ticks()

class Falling_Scebob(pygame.sprite.Sprite):
    def __init__(self, screen_width, speed):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(yellow)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

speed_1 = 10
max_speed = 35
speed_increase_rate=0.85

start_time=time.time()

running=True
game_over=False   # Флаг окончания игры

while running:
    current_time_ms=pygame.time.get_ticks()
    current_time=time.time()
    elapsed_time=current_time-start_time
    current_speed=min(speed_1+speed_increase_rate*elapsed_time,max_speed)

    if not game_over:
        # Обновление очков каждую секунду
        if current_time_ms - last_score_time >=1000:
            score+=1
            last_score_time=current_time_ms

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False

            elif event.type==SPAWN_EVENT:
                shape= Falling_Scebob(1000,int(current_speed))
                all_sprites.add(shape)

        # Обработка клавиш для перемещения персонажа
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            body_size.move_ip(-15,0)
        if keys[pygame.K_RIGHT]:
            body_size.move_ip(15,0)

        # Ограничение по границам экрана для персонажа            
        if body_size.x<0:
            body_size.x=0
        elif body_size.x+body_size.width>1000:
            body_size.x=1000-body_size.width

        # Обновление rect у игрока (чтобы отрисовать его на экране)
        player_sprite.rect.topleft = body_size.topleft

        # Удаление вышедших за границы объектов (снизу)
        for sprite in all_sprites:
            if sprite.rect.top > 1000:
                sprite.kill()

        # Обновление спрайтов (падающих объектов)
        all_sprites.update()

        # Обработка столкновений с падающими объектами (с игроком)
        collided_sprites=pygame.sprite.spritecollide(player_sprite, all_sprites, True)

        # Проверка условий окончания игры: либо по очкам либо по столкновению
        if score>=40:
            print("Достигнут лимит очков")   # Для отладки
            game_over=True

        if collided_sprites:
            print("Столкновение обнаружено")   # Для отладки
            game_over=True

    # Если игра окончена — показываем финальный экран и ждем перед выходом
    if game_over:
        screen.fill((0,0,0))
        thank_text=font.render("GOOD GAME BRO!", True,(255 ,255 ,255))
        text_rect=thank_text.get_rect(center=(500,500))
        screen.blit(thank_text,text_rect)
        pygame.display.flip()
        
        # Ждем 3 секунды и выходим из цикла (игры)
        pygame.time.wait(3000)
        running=False

    else:
        # Рисуем сцену и персонажа только если игра не окончена
        
        screen.fill((0 ,0 ,0))
        
        # Рисуем персонажа и его лицо/глаза/рот 
        body=pygame.draw.rect(screen,green,body_size)   # Используем цвет yellow вместо green для тела
        
        eye_center_1=(body.x+body.width//4,
                     body.y+body.height//4)
        
        eye_1=pygame.draw.circle(screen,redundant_color:=red ,center=eye_center_1,radius=16)
        
        eye_center_2=(body.x+3*body.width//4,
                     body.y+body.height//4)
        
        eye_2=pygame.draw.circle(screen,redundant_color:=red ,center=eye_center_2,radius=16)

        
        mouth_size=pygame.Rect(
            body.x+body.width//4,
            body.y+int(1.2*body.height//2),
            body.width//2,
            body.height//6)
        
        mouth=pygame.draw.rect(screen,(blue),mouth_size)   # Не нужно указывать 'width' чтобы заполнить
        
        # Рисуем падающие объекты поверх сцены с персонажем (если нужно)
        
       # Перед рисованием всех спрайтов — убедимся что они в правильном порядке (обычно так и есть)
       
        all_sprites.draw(screen)

       # Отрисовка очков в левом верхнем углу
        score_text=font.render(f"Очки: {score}", True,(255 ,255 ,255))
        screen.blit(score_text,(10 ,10))

    # Обновляем дисплей и ограничиваем FPS в любом случае (после рисования или финального экрана)
    pygame.display.flip()
    clock.tick(60)

# После выхода из цикла — ничего не рисуем. Всё уже сделано.
pygame.quit()
exit()