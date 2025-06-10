import pygame
import random
import time
import os

from pygame.examples.video import clock

pygame.init()

# Параметры окна
WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический Боевик")

# Загрузка изображений
player_image = pygame.image.load('player.png')
enemy_image = pygame.image.load('enemy.png')
background_image = pygame.image.load('phon.jpg')


# Спрайты пуль
bullet_image = pygame.Surface((10, 4))
bullet_image.fill((255, 0, 0))
player_bullet_image = pygame.Surface((10, 4))
player_bullet_image.fill((0, 255, 0))

class Player:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.lives = 3
        self.bullets = []
        self.bullet_timer = 0
        self.bullet_interval = 15
        self.score = 0

    def move(self, up, down):
        if up and self.y > 0:
            self.y -= self.speed
        if down and self.y < HEIGHT - player_image.get_height():
            self.y += self.speed

    def shoot(self):
        if self.bullet_timer >= self.bullet_interval:
            bullet_x = self.x + player_image.get_width()
            bullet_y = self.y + player_image.get_height() // 2
            self.bullets.append([bullet_x, bullet_y])
            self.bullet_timer = 0

    def update(self):
        self.bullet_timer += 1

    def check_collisions(self, enemies):
        for enemy in enemies:
            if self.collides_with(enemy):
                self.lives -= 1
                if self.lives <= 0:
                    return True  # Game over
        return False

    def collides_with(self, enemy):
        return (self.x + player_image.get_width() >= enemy.x and
                self.x <= enemy.x + enemy_image.get_width() and
                self.y + player_image.get_height() >= enemy.y and
                self.y <= enemy.y + enemy_image.get_height())

class Enemy:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.bullets = []
        self.bullet_timer = 0
        self.bullet_interval = 60

    def move(self):
        self.y += self.direction * random.randint(1, 3)
        if self.y <= 0 or self.y >= HEIGHT - enemy_image.get_height():
            self.direction *= -1

    def shoot(self):
        if self.bullet_timer >= self.bullet_interval:
            bullet_x = self.x - 10
            bullet_y = self.y + enemy_image.get_height() // 2
            self.bullets.append([bullet_x, bullet_y])
            self.bullet_timer = 0

    def update(self):
        self.bullet_timer += 1

class Score:
    def __init__(self):
        self.start_time = 0
        self.survival_time = 0
        self.high_score = self.load_high_score()
        self.score_file = "highscore.txt"

    def start_game(self):
        self.start_time = time.time()

    def update_survival_time(self):
        self.survival_time = time.time() - self.start_time

    def save_high_score(self):
        with open(self.score_file, "w") as file:
            file.write(str(self.high_score))

    def load_high_score(self):
        if os.path.exists(self.score_file):
            with open(self.score_file, "r") as file:
                return int(file.read())
        return 0

# Отображение текста
def draw_text(surface, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

# Отображение интерфейса меню
def show_menu():
    screen.fill((0, 0, 0))
    draw_text(screen, "Космический Боевик", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Нажмите любую клавишу для начала", 36, WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()
    wait_for_key()

# Ожидание пока нажмут кнопку
def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                waiting = False

# Интерфейс рестарта игры
def restart_game():
    global player, enemies, survival_time
    player = Player(50, HEIGHT // 2, 5)
    enemies = []
    survival_time = 0

# Основной цикл игры
def main():
    global player, enemies, survival_time
    clock = pygame.time.Clock()
    running = True
    in_game = False
    spawn_timer = 0
    spawn_interval = 100  # Интервал появления врагов

    show_menu()
    restart_game()

    while running:
        clock.tick(FPS)
        player.update()

        if in_game:
            player.move(pygame.key.get_pressed()[pygame.K_UP], pygame.key.get_pressed()[pygame.K_DOWN])
            player.shoot()

            # Проверка коллизий
            if player.check_collisions(enemies):
                in_game = False

            # Обновление врагов и пуль
            for enemy in enemies:
                enemy.move()
                enemy.shoot()
                enemy.update()

            # Обновление пуль игрока
            player.bullets = [[x - 10, y] for x, y in player.bullets if x > 0]

            # Обновление пуль врагов
            for enemy in enemies:
                enemy.bullets = [[x + 10, y] for x, y in enemy.bullets if x < WIDTH]

            # Удаление врагов и подсчет очков
            enemies = [enemy for enemy in enemies if enemy.x > -enemy_image.get_width()]
            player.score += len(enemies)  # Увеличиваем счет за каждого врага

            # Появление новых врагов
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                enemy_y = random.randint(0, HEIGHT - enemy_image.get_height())
                enemies.append(Enemy(WIDTH, enemy_y, random.choice([-1, 1])))
                spawn_timer = 0

            # Отрисовка
            screen.blit(background_image, (0, 0))
            screen.blit(player_image, (player.x, player.y))
            for enemy in enemies:
                screen.blit(enemy_image, (enemy.x, enemy.y))
            for bullet in player.bullets:
                screen.blit(player_bullet_image, bullet)
            for enemy in enemies:
                for bullet in enemy.bullets:
                    screen.blit(bullet_image, bullet)

            draw_text(screen, f"Lives: {player.lives}", 36, 70, 10)
            draw_text(screen, f"Score: {player.score}", 36, WIDTH - 100, 10)
            pygame.display.flip()

        # Проверка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Условие окончания игры
        if not in_game:
            show_game_over()

    pygame.quit()
def show_game_over():
    screen.fill((0, 0, 0))
    draw_text(screen, "Игра окончена", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, f"Счет: {player.score}", 36, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Нажмите любую клавишу для перезапуска", 36, WIDTH // 2, HEIGHT // 2 + 40)
    pygame.display.flip()
    wait_for_key()
    restart_game()


#Ожидание пока нажмут кнопку
def wait_for_key():
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                waiting = False

#Интерфейс рестарта игры
def restart_game():
    global player_x, player_y, lives, enemies, vrag_puli, player_puli, survival_time, start_time, in_game
    player_x = 50
    player_y = HEIGHT // 2
    lives = 3
    enemies = []
    vrag_puli = []
    player_puli = []
    survival_time = 0
    start_time = time.time()
    in_game = True

#Сохранение лучшего результата
#def save_high_score(score):
#    with open(score_file, 'w') as f:
#        f.write(str(score))

#Загрузка лучшего результата
#def load_high_score():
#    if os.path.exists(score_file):
#        with open(score_file, 'r') as f:
#            return float(f.read())
#    return 0

#high_score = load_high_score() #Лучший результат

#show_menu() #Показать меню
#restart_game() #Перезапуск игры

##Основной цикл игры
while running:
    clock.tick(FPS)

    if in_game:
        survival_time = time.time() - start_time #Определение времени выживания

        #Проверка взаимодействия с игрой
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #Часть управления модлькой игрока
#        keys = pygame.key.get_pressed()
#        if keys[pygame.K_UP] and player_y > 0:
#            player_y -= player_speed
#        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_image.get_height():
#            player_y += player_speed


#        player_puli_timer += 1 #Увеличивает счетчик таймера на +1
#        #Проверка нажатия кнопки SPACE
#        if keys[pygame.K_SPACE] and player_puli_timer >= player_puli_interval:
#            bullet_x = player_x + player_image.get_width()
#            bullet_y = player_y + player_image.get_height() // 2
#            player_puli.append([bullet_x, bullet_y])
#            player_puli_timer = 0

#        vrag_time += 1 #Увеличивает время врага на +1
#        #Услвоие создание новых врагов
#        if vrag_time >= vrag_int:
#            vrag_time = 0
#            enemy_y = random.randint(0, HEIGHT - enemy_image.get_height())
#            enemy_x = WIDTH - 100
#            enemies.append([enemy_x, enemy_y, random.choice([-1, 1])])

        #Обеспечение случайного движение врагов
        for enemy in enemies:
            enemy[1] += enemy[2] * random.randint(1, 3)
            if enemy[1] <= 0 or enemy[1] >= HEIGHT - enemy_image.get_height():
                enemy[2] *= -1

        #Создание списка пуль и добавляет их к позиции каждого врага
#        vrag_puli_time += 1
#        if vrag_puli_time >= vrag_puli_interval:
#            vrag_puli_time = 0
#            for enemy in enemies:
#                bullet_x = enemy[0] - 10
#                bullet_y = enemy[1] + enemy_image.get_height() // 2
#                vrag_puli.append([bullet_x, bullet_y])

        # Изменение координаты вражеской пули
        for bullet in vrag_puli:
            bullet[0] -= 10
        # Изменение координаты пули игрока
        for bullet in player_puli:
            bullet[0] += 10
        #Удаление лишних пуль
        vrag_puli = [bullet for bullet in vrag_puli if bullet[0] > 0]
        player_puli = [bullet for bullet in player_puli if bullet[0] < WIDTH]

        #Gроверка коснулась ли пуля игрока
        player_rect = pygame.Rect(player_x, player_y, player_image.get_width(), player_image.get_height())
        for bullet in vrag_puli:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_image.get_width(), bullet_image.get_height())
            if player_rect.colliderect(bullet_rect):
                lives -= 1
                vrag_puli.remove(bullet)
                if lives <= 0:
                    in_game = False
                    game_over = True
        #Gроверка коснулась ли пуля врага
        for bullet in player_puli:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], player_bullet_image.get_width(), player_bullet_image.get_height())
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_image.get_width(), enemy_image.get_height())
                if bullet_rect.colliderect(enemy_rect):
                    enemies.remove(enemy)
        #Создаёт окно с игрой, где игрок управляет персонажем и стреляет пулями
        screen.blit(phon.jpg, (0, 0))
        screen.blit(player_image, (player_x, player_y))
        for enemy in enemies:
            screen.blit(enemy_image, (enemy[0], enemy[1]))
        for bullet in vrag_puli:
            screen.blit(bullet_image, (bullet[0], bullet[1]))
        for bullet in player_puli:
            screen.blit(player_bullet_image, (bullet[0], bullet[1]))
        draw_text(screen, f"Lives: {lives}", 36, 70, 10)
        draw_text(screen, f"Время: {survival_time:.2f} сек", 36, WIDTH - 150, 10)
        pygame.display.flip()
    #Условие окончания игры
    elif game_over:
        show_game_over()
        restart_game()

pygame.quit()