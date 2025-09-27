# импортируем все это дело
import pygame
from pygame import K_LEFT, K_RIGHT, K_SPACE
import random



# время для медленных тиков и медленной смены фото перонажа
time1 = pygame.time.Clock()

# запускаем библиотеку
pygame.init()

# обозначаем границы экрана
screencast = pygame.display.set_mode((620, 259))
screen_width, screen_height = screencast.get_size()  # Получаем размеры экрана

# название (исправлена опечатка)
pygame.display.set_caption("игра гегама")

# добавляем иконку
icon = pygame.image.load( "img/для игры.png")
pygame.display.set_icon(icon)

# добавляем оружие
shuriken = pygame.image.load("img/shuriken.png").convert_alpha()
shuriken = pygame.transform.scale(shuriken, (20, 20))
shurikens = []
shuriken_left = 5

# противники
ghost = pygame.image.load("img/5366379616094258132.png")
ghost = pygame.transform.scale(ghost, (60, 64))

# Первый злодей
first_villain = pygame.image.load("img/Снимок экрана 2025-09-25 215448-Photoroom.png").convert_alpha()
first_villain = pygame.transform.scale(first_villain, (60, 64))

# Босс
boss = pygame.image.load("img/Снимок экрана 2024-05-03 172110.png").convert_alpha()
boss = pygame.transform.scale(boss, (128, 128))

# Сердечки для босса
heart = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.rect(heart, (255, 0, 0), (0, 0, 20, 20))


# Класс для врагов с фиксированной высотой
class Enemy:
    def __init__(self, x, y, enemy_type, height):
        self.rect = pygame.Rect(x, y, 60, 64)
        self.enemy_type = enemy_type  # 'ghost' или 'villain'
        self.height = height  # Фиксированная высота
        self.rect.y = y  # Устанавливаем высоту один раз

    def move(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        if self.enemy_type == 'villain':
            screen.blit(first_villain, self.rect)
        else:
            screen.blit(ghost, self.rect)


class Boss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 128, 128)
        self.health = 7
        self.speed = 4
        self.direction = 1  # 1 - вправо, -1 - влево
        self.min_x = 100  # Левая граница движения
        self.max_x = 500  # Правая граница движения
        self.attack_timer = 0
        self.attack_interval = 2000  # Атака каждые 2 секунды
        self.is_attacking = False
        self.attack_speed = 7

    def move(self):
        # Периодическая атака
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_timer > self.attack_interval:
            self.is_attacking = True
            self.attack_timer = current_time
            # При атаке двигаемся быстрее
            speed = self.attack_speed
        else:
            self.is_attacking = False
            speed = self.speed

        # Двигаем босса
        self.rect.x += self.direction * speed

        # Меняем направление при достижении границ
        if self.rect.x <= self.min_x:
            self.rect.x = self.min_x
            self.direction = 1  # Двигаемся вправо
        elif self.rect.x >= self.max_x:
            self.rect.x = self.max_x
            self.direction = -1  # Двигаемся влево

    def draw(self, screen):
        screen.blit(boss, self.rect)
        # Отображение здоровья
        for i in range(self.health):
            screen.blit(heart, (self.rect.x + i * 25, self.rect.y - 30))


enemies = []  # Обычные враги
boss_instance = None  # Босс
boss_active = False
boss_spawned = False
warning_displayed = False
warning_timer = 0
boss_spawn_score = 250  # Первое появление босса
next_boss_spawn = 250  # Следующее появление босса

# Сюрикены на карте
shuriken_pickups = []
shuriken_spawn_points = [100, 300, 500, 700, 900]

# фон проигрыша
game_over_bg = pygame.image.load( "img/png-klev-club-dpmo-p-game-over-png-19.png").convert_alpha()
game_over_bg = pygame.transform.scale(game_over_bg, (620, 259))

# фон
background_image = pygame.image.load( "img/game-background-2d-application-illustration-260nw-501375310.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
bg_width = background_image.get_width()

# для анимации хождения и бега лист с фото
walk_left = [
    pygame.image.load(  "img/лево/лево1.png").convert_alpha(),
    pygame.image.load( "img/лево/лево2.png").convert_alpha(),
    pygame.image.load( "img/лево/лево3.png").convert_alpha(),
    pygame.image.load("img/лево/лево4.png").convert_alpha()
]

walk_right = [
    pygame.image.load( "img/право/право1.png").convert_alpha(),
    pygame.image.load( "img/право/право2.png").convert_alpha(),
    pygame.image.load( "img/право/право3.png").convert_alpha(),
    pygame.image.load( "img/право/право4.png").convert_alpha()
]

# песни тоже лист для смены
bg_songs = [
    pygame.mixer.Sound( 'songs/8597bb02c2b2555.mp3'),
]

current_song_index = 0
current_song = bg_songs[current_song_index]
current_song.play(-1)

ghost_timer = pygame.USEREVENT + 1
pygame.time.set_timer(ghost_timer, 2000)

# для бесконечного фона при беге
bg_x = 0
bg_y = 155
player_speed_x = 5
player_speed_y = 0
player_x = 200
player_y = bg_y
is_jump = False
normal_jump_count = -13  # Обычная высота прыжка
boss_jump_count = -18  # Высота прыжка для перепрыгивания босса
jump_count = normal_jump_count
player_move = 0
gameplay = True

# Переменная для ограничения частоты выстрелов
last_shot_time = 0
shot_delay = 300

# Система очков и сложности
score = 0
high_score = 0
ghost_speed = 10
score_increase_timer = 0
score_increase_interval = 1000

# Шрифты
text_font = pygame.font.Font('fonts/Asimovian-Regular.ttf', 50)
small_font = pygame.font.Font( 'fonts/Asimovian-Regular.ttf', 24)
score_font = pygame.font.Font( 'fonts/Asimovian-Regular.ttf', 36)
warning_font = pygame.font.Font( 'fonts/Asimovian-Regular.ttf', 60)

restart_text = text_font.render("RESTART GAME", False, (240, 248, 255))
restart_text_rect = restart_text.get_rect(topleft=(135, 170))

run = True


def spawn_shuriken_pickups():
    for point in shuriken_spawn_points:
        if score >= point and not any(p['point'] == point for p in shuriken_pickups):
            shuriken_pickups.append({
                'rect': pygame.Rect(screen_width + 100, bg_y + 20, 20, 20),
                'point': point,
                'collected': False
            })


# начало добавления деталей в игру
while run:
    current_time = pygame.time.get_ticks()

    # Отрисовка фона
    screencast.blit(background_image, (bg_x, 0))
    screencast.blit(background_image, (bg_x + bg_width, 0))

    if gameplay:
        # Спавн сюрикенов на карте
        spawn_shuriken_pickups()

        # Увеличение очков со временем
        if current_time - score_increase_timer > score_increase_interval:
            score += 10
            score_increase_timer = current_time

            if score % 100 == 0:
                ghost_speed += 1

            # Активация босса при достижении нужного количества очков
            if score >= next_boss_spawn and not boss_active:
                boss_active = True
                boss_spawned = True
                warning_displayed = True
                warning_timer = current_time
                enemies.clear()  # Очищаем обычных врагов
                # Увеличиваем сложность для следующего босса
                next_boss_spawn += 500  # Следующий босс через 500 очков
                # Устанавливаем высоту прыжка для босса
                jump_count = boss_jump_count

        # Отображение предупреждения о боссе
        if warning_displayed:
            if current_time - warning_timer < 3000:
                warning_text = warning_font.render("ЗЛОЙ АГАААС!!!", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
                screencast.blit(warning_text, warning_rect)
            else:
                warning_displayed = False
                # Создаем босса после предупреждения
                boss_instance = Boss(300, bg_y - 50)  # Появляется в центре
                # Увеличиваем здоровье босса в зависимости от количества появлений
                boss_instance.health = 7 + (score // 500)  # +1 здоровье за каждые 500 очков

        # Отображение очков и сюрикенов
        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        shuriken_text = small_font.render(f"Shurikens: {shuriken_left}", True, (255, 255, 255))
        speed_text = small_font.render(f"Speed: {ghost_speed}", True, (255, 255, 255))
        boss_text = small_font.render(f"Next Boss: {next_boss_spawn}", True, (255, 100, 100))

        screencast.blit(score_text, (10, 10))
        screencast.blit(shuriken_text, (10, 50))
        screencast.blit(speed_text, (10, 80))
        screencast.blit(boss_text, (10, 110))

        player_rect = walk_left[0].get_rect(topleft=(player_x, player_y))

        # Отрисовка и движение сюрикенов на карте
        for pickup in shuriken_pickups[:]:
            if not pickup['collected']:
                screencast.blit(shuriken, pickup['rect'])
                pickup['rect'].x -= ghost_speed

                if player_rect.colliderect(pickup['rect']):
                    shuriken_left += 3
                    pickup['collected'] = True
                    shuriken_pickups.remove(pickup)
                elif pickup['rect'].x < -50:
                    shuriken_pickups.remove(pickup)

        # Отрисовка и движение босса
        if boss_active and boss_instance:
            boss_instance.move()  # Босс двигается туда-сюда
            boss_instance.draw(screencast)

            # Отображение статуса атаки босса
            if boss_instance.is_attacking:
                attack_text = small_font.render("BOSS ATTACK!", True, (255, 0, 0))
                screencast.blit(attack_text, (boss_instance.rect.x, boss_instance.rect.y - 60))

            # Отображение направления движения
            direction_text = small_font.render(f"Moving: {'RIGHT' if boss_instance.direction == 1 else 'LEFT'}", True,
                                               (200, 200, 0))
            screencast.blit(direction_text, (boss_instance.rect.x, boss_instance.rect.y - 80))

            # Столкновение с боссом
            if player_rect.colliderect(boss_instance.rect):
                # Прыжок на голову босса
                if player_rect.bottom < boss_instance.rect.y + 30:
                    boss_instance.health -= 1
                    player_speed_y = -12  # Сильный отскок
                    if boss_instance.health <= 0:
                        score += 200  # Больше очков за босса
                        boss_active = False
                        boss_instance = None
                        # Возвращаем обычную высоту прыжка
                        jump_count = normal_jump_count
                else:
                    gameplay = False
                    if score > high_score:
                        high_score = score

        # Отрисовка и движение обычных врагов (только когда нет босса)
        if not boss_active:
            for enemy in enemies[:]:
                enemy.move(ghost_speed)
                enemy.draw(screencast)

                # Столкновение с врагом
                if player_rect.colliderect(enemy.rect):
                    gameplay = False
                    if score > high_score:
                        high_score = score

                # Удаляем врагов за экраном
                if enemy.rect.x < -100:
                    enemies.remove(enemy)

        # Управление персонажем
        keys_for_move = pygame.key.get_pressed()
        if keys_for_move[K_LEFT]:
            screencast.blit(walk_left[player_move], (player_x, player_y))
        else:
            screencast.blit(walk_right[player_move], (player_x, player_y))

        # Движение фона (останавливается при боссе)
        if not boss_active:
            bg_x -= 1
            if bg_x <= -bg_width:
                bg_x = 0

        # Анимация ходьбы
        if keys_for_move[K_LEFT] or keys_for_move[K_RIGHT]:
            if player_move == 3:
                player_move = 0
            else:
                player_move += 1

        # Движение влево/вправо
        if keys_for_move[K_LEFT] and player_x > 30:
            player_x -= player_speed_x
        elif keys_for_move[K_RIGHT] and player_x < 500:
            player_x += player_speed_x

        # Прыжок
        if not is_jump:
            if keys_for_move[K_SPACE]:
                is_jump = True
                player_speed_y = jump_count
        else:
            player_speed_y += 1
            player_y += player_speed_y

            if player_y >= bg_y:
                player_y = bg_y
                player_speed_y = 0
                is_jump = False

        # Движение и столкновения сюрикенов игрока
        if shurikens:
            for el in shurikens[:]:
                screencast.blit(shuriken, (el.x, el.y))
                el.x += 4

                if el.x > 660:
                    shurikens.remove(el)
                    continue

                # Столкновения с боссом
                if boss_active and boss_instance and el.colliderect(boss_instance.rect):
                    boss_instance.health -= 1
                    if boss_instance.health <= 0:
                        score += 200
                        boss_active = False
                        boss_instance = None
                        jump_count = normal_jump_count
                    if el in shurikens:
                        shurikens.remove(el)
                    continue

                # Столкновения с обычными врагами (только когда нет босса)
                if not boss_active:
                    for enemy in enemies[:]:
                        if el.colliderect(enemy.rect):
                            enemies.remove(enemy)
                            score += 25
                            if el in shurikens:
                                shurikens.remove(el)
                            break

    else:
        # Экран проигрыша
        screencast.fill((0, 0, 0))
        screencast.blit(restart_text, restart_text_rect)

        final_score_text = text_font.render(f"Score: {score}", True, (255, 255, 255))
        high_score_text = text_font.render(f"High Score: {high_score}", True, (255, 215, 0))

        screencast.blit(final_score_text, (200, 100))
        screencast.blit(high_score_text, (180, 40))

    # Проверка клика по кнопке restart
    mouse = pygame.mouse.get_pos()
    if restart_text_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
        gameplay = True
        player_x = 200
        player_y = bg_y
        enemies.clear()
        shurikens.clear()
        shuriken_pickups.clear()
        shuriken_left = 5
        bg_x = 0
        player_move = 0
        is_jump = False
        player_speed_y = 0
        score = 0
        ghost_speed = 10
        score_increase_timer = current_time
        boss_active = False
        boss_spawned = False
        warning_displayed = False
        boss_instance = None
        boss_spawn_score = 250
        next_boss_spawn = 250
        jump_count = normal_jump_count

    # Обновление экрана
    pygame.display.update()

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == ghost_timer and gameplay and not boss_active:  # Враги появляются только когда нет босса
            # Меньше врагов сверху (20% случаев)
            if random.random() < 0.8:
                enemy_y = bg_y
            else:
                enemy_y = bg_y - 100

            # Чередуем типы врагов
            if score % 200 < 100:
                enemy_type = 'villain'
            else:
                enemy_type = 'ghost'

            enemies.append(Enemy(screen_width, enemy_y, enemy_type, enemy_y))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_b and gameplay and shuriken_left > 0:
            if current_time - last_shot_time > shot_delay:
                shurikens.append(shuriken.get_rect(topleft=(player_x + 30, player_y + 10)))
                last_shot_time = current_time
                shuriken_left -= 1

    time1.tick(60)

# выход из игры
pygame.quit()