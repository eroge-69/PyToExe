import random
import pygame
import math

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы и настройки
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = WINDOW_WIDTH / 3
TICK = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Игровые переменные
ball_radius = WINDOW_HEIGHT / 20 + 20
ball_x = 300
ball_y = 200
ball_speed_y = 6

paddle1_y = WINDOW_HEIGHT / 2
paddle2_y = WINDOW_HEIGHT / 2
paddle_size = min(WINDOW_HEIGHT / 3, 250)
paddle_speed = WINDOW_WIDTH / 40
ball_speed_x = paddle_speed / 2

player1_score = 0
player2_score = 0
paddle_thickness = 10
paddle2_thickness = 10

# Переменные для событий и анимации
animation_step = 0
current_event = 0
current_events_list = [0, 0, 0]
events_name_list = [
    "Без эффекта",
    "Непредсказуемый мяч",
    "Малые платформы",
    "Гравитация платформ",
    "Гравитация",
    "Гравитация",
    "Обратное управление",
    "Тьма"
]
events_list_text = ""
font = pygame.font.SysFont('arial', 20, True)
text_surface = font.render('. . .', True, (255, 255, 255))


max_events = 7
event_timer = WINDOW_WIDTH
event_speed = (WINDOW_WIDTH / 100) / 5
ball_gravity = 0
delay_counter = 0

# Класс мяч отвечает за все и хар-ки
class Ball:
    BallsCount = 0
    def __init__(self, ID, Radius=ball_radius, Color=WHITE, PosX=0, PosY=0, SpeedX=0, SpeedY=0):
        self.ID = ID
        self.Radius = Radius
        self.Color = Color
        self.PosX = PosX
        self.PosY = PosY
        self.SpeedX = SpeedX
        self.SpeedY = SpeedY
        Ball.BallsCount += 1

    def SetPos(self, PosX, PosY):
        self.PosX = PosX
        self.PosY = PosY
# Список мячей в списке где 1 элемент это объект
Balls_list = []
# Функция добавления мяча
def AddBall():
    Balls_list.append(Ball(0, ball_radius, WHITE, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, ball_speed_x, ball_speed_y))

def DelBalls():
    for obj in Balls_list:
        if obj.ID >= 1:
            Balls_list[obj] = None
for i in range(0, 2):
    AddBall()

# Переменные визуальных эффектов
light_intensity = 255
light_intensity2 = 255
background_brightness = 100
pulse_effect = 0
middle_line_radius = 20
pause_state = -1

# Флаги состояния игры
game_running = True
main_loop_active = True

# Настройка экрана
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME, 213)
screen_buffer = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME, 32)

pygame.display.set_caption("Pin --- Pang")

# Загрузка звуков
ball_teleport_sound = pygame.mixer.Sound('BALL_TP_GLITCH.wav')
ball_teleport_sound.set_volume(0.1)
glitch_sound = pygame.mixer.Sound('glitch.wav')
glitch_sound.set_volume(0.1)
pong_sound = pygame.mixer.Sound('pong.mp3')
pong_sound.set_volume(0.1)

background_sound = pygame.mixer.Sound('BG2.mp3')
background_sound.set_volume(pong_sound.get_volume() + 0.3)
background_sound.play()

BACKGROUND_SOUND_EVENT = pygame.USEREVENT
pygame.time.set_timer(BACKGROUND_SOUND_EVENT, int(background_sound.get_length()) * 1000)

# Загрузка изображений
background_image = pygame.image.load("BG.png")
background_image.set_alpha(100)
pause_background = pygame.image.load("PAUSE_BG (2).png")
pause_background.set_alpha(100)

#all_image = pygame.image.load("Ball" + str(current_event) + ".png")

# Создание объектов управления
game_clock = pygame.time.Clock()

# Время зажатия кнопки Escape
ButtonHoldTime = 0



def handle_game_events():
    global game_running, main_loop_active, pause_state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
            main_loop_active = False

        if event.type == BACKGROUND_SOUND_EVENT:
            background_sound.stop()
            background_sound.play()


# Основной игровой цикл
while game_running:
    handle_game_events()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    # Обновление цветов для эффектов
    white_effect_color = (255, light_intensity, light_intensity)
    white_effect_color2 = (255, light_intensity2, light_intensity2)

    # Обработка клавиш управления
    if keys[pygame.K_BACKSPACE]:
        game_running = False
    # Пауза и выход из паузы
    if keys[pygame.K_ESCAPE] and ButtonHoldTime < 1:
        pause_state /= -1
        ButtonHoldTime += 1
        background_image.set_alpha(100)
        background_sound.set_volume(0.5)
        if pause_state == 1:
            glitch_sound.play()
            background_image.set_alpha(50)
            background_sound.set_volume(0.1)
            paused_bg = pygame.transform.scale(pause_background,
                                               (WINDOW_WIDTH * 2, WINDOW_HEIGHT * 2))
    elif not keys[pygame.K_ESCAPE] and ButtonHoldTime > 0:
        ButtonHoldTime = 0

    # Игровая логика (только если не на паузе)
    if pause_state != 1:
        # Изменения кадра анимации
        animation_step += 1
        # Движение мяча
        for obj in Balls_list:
            if math.fabs(obj.SpeedX) < WINDOW_WIDTH / 80:
                if obj.SpeedX < 0:
                    obj.SpeedX -= 0.1
                else:
                    obj.SpeedX += 0.1
            obj.PosX += obj.SpeedX
            obj.PosY += obj.SpeedY

        # Столкновение с правой ракеткой
        for obj in Balls_list:
            if obj.PosX > WINDOW_WIDTH - obj.Radius:
                if paddle1_y + paddle_size > obj.PosY > paddle1_y - paddle_size:
                    obj.SpeedX = -obj.SpeedX
                    obj.SpeedY = random.randint(-5, 5)
                    paddle_thickness = 50
                    pong_sound.play()
                    pulse_effect = 50
                else:
                    obj.SpeedX = 0
                    player1_score += 1
                    light_intensity2 = 0
                    obj.PosX, obj.PosY = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2
                    event_timer = 0
                    ball_teleport_sound.play()

        # Столкновение с левой ракеткой
        for obj in Balls_list:
            if obj.PosX < 0 + ball_radius:
                if paddle2_y + paddle_size > obj.PosY > paddle2_y - paddle_size:
                    obj.SpeedX = -obj.SpeedX
                    paddle2_thickness = 50
                    pong_sound.play()
                    pulse_effect = 50
                else:
                    obj.SpeedX = 0
                    light_intensity = 0
                    player2_score += 1
                    obj.PosX, obj.PosY = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2
                    event_timer = 0
                    ball_teleport_sound.play()

        # Обновление заголовка окна
        pygame.display.set_caption(f"Pin --- Pang   {player1_score}    {player2_score}")

        # Восстановление толщины ракеток
        if paddle_thickness != 10:
            paddle_thickness = paddle_thickness - int((5 * (paddle_thickness - 10) / 100))
        if paddle2_thickness != 9:
            paddle2_thickness = paddle2_thickness - int((5 * (paddle2_thickness - 10) / 100))

        # Отскок от верхней и нижней границ
        for obj in Balls_list:
            if obj.PosY > WINDOW_HEIGHT - obj.Radius:
                pong_sound.play()
                obj.SpeedY = -obj.SpeedY

            if obj.PosY < 0 + obj.Radius:
                pong_sound.play()
                obj.SpeedY = -obj.SpeedY


        # Обработка таймера событий и проверка на неиграбильные комбинации (гравитация ракеток и обратное управление не позволяет управлять!)
        if event_timer > 0:
            event_timer -= event_speed
        elif event_timer < 1:
            new_event = random.randint(0, max_events)
            current_events_list.append(new_event)
            print(current_events_list)
            print(len(current_events_list))
            if len(current_events_list) > 2:
                current_events_list.remove(current_events_list[0])
            events_list_text = str(str(events_name_list[current_events_list[0]]) + ", "
                                   + str(events_name_list[current_events_list[1]]) + ", "
                                   + str(events_name_list[current_events_list[2]]))
            text_surface = font.render(str(events_list_text), True, (255, 255, 255))
            event_timer = WINDOW_WIDTH
            event_speed += 0.05

        # Анимация размера мяча

        for obj in Balls_list:
            if obj.Radius > WINDOW_HEIGHT / 20:
                obj.Radius -= 1

        # Восстановление интенсивности света

        if light_intensity < 254:
            light_intensity += 2
        if light_intensity2 < 254:
            light_intensity2 += 2

        # Пульсация анимации

        if pulse_effect > 0:
            pulse_effect -= 5
            background_image.set_alpha(pulse_effect + 50)

        # Обработка специальных событий

        for obj in Balls_list:
            if 1 in current_events_list:
                if delay_counter < 1:
                    obj.SpeedY = random.randint(-8, 8)
                    obj.SpeedX = -obj.SpeedX

        if 2 in current_events_list:
            paddle_size = 30
        else:
            paddle_size = min(WINDOW_HEIGHT / 5, 250)

        if 3 in current_events_list and 6 not in current_events_list:
            if paddle1_y < WINDOW_HEIGHT - paddle_size:
                paddle1_y += 5
            if paddle2_y < WINDOW_HEIGHT - paddle_size:
                paddle2_y += 5

        for obj in Balls_list:
            if 4 in current_events_list:
                obj.SpeedY -= 0.5
                if obj.PosY < 0 + ball_radius:
                    obj.SpeedY = random.randint(1, 20)
                if obj.PosY > WINDOW_HEIGHT / 2:
                    current_event = 5

        for obj in Balls_list:
            if 5 in current_events_list:
                obj.SpeedY += 0.5
                if obj.PosY > WINDOW_HEIGHT - ball_radius:
                    obj.SpeedY = random.randint(-20, -1)
                if obj.PosY < WINDOW_HEIGHT / 2:
                    current_event = 4

        if 6 in current_events_list:
            paddle_speed = -10
        else:
            paddle_speed = 10

        if 7 in current_events_list:
            WHITE = [0, 0, 0]
        else:
            WHITE = [255, 255, 255]

        # Обновление счетчика задержки

        if delay_counter > 0:
            delay_counter -= 1
        else:
            delay_counter = random.randint(50, 250)

        # Управление ракетками

        if keys[pygame.K_w] and paddle2_y > 0 + paddle_size:
            paddle2_y -= paddle_speed
        if keys[pygame.K_s] and paddle2_y < WINDOW_HEIGHT - paddle_size:
            paddle2_y += paddle_speed
        if keys[pygame.K_UP] and paddle1_y > 0 + paddle_size:
            paddle1_y -= paddle_speed
        if keys[pygame.K_DOWN] and paddle1_y < WINDOW_HEIGHT - paddle_size:
            paddle1_y += paddle_speed

        # Ограничение движения ракеток

        paddle1_y = max(0 + paddle_size + 1, min(WINDOW_HEIGHT - paddle_size - 1, paddle1_y))
        paddle2_y = max(0 + paddle_size + 1, min(WINDOW_HEIGHT - paddle_size - 1, paddle2_y))



    # Отрисовка игры

    background_color = (background_brightness, background_brightness, background_brightness)
    screen.fill(BLACK)
    screen_buffer.fill(BLACK)

    # Фон с анимацией

    bg_x = 0
    bg_y = 0
    image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(image, (bg_x, bg_y))

    # Центральная линия
    line_color = (255 - middle_line_radius / 5, 255 - middle_line_radius / 5, 255 - middle_line_radius / 5)
    # pygame.draw.line(screen, line_color, [WINDOW_WIDTH / 2, 0],
    # [WINDOW_WIDTH / 2, WINDOW_HEIGHT], middle_line_radius)

    # Ракетки
    pygame.draw.line(screen, white_effect_color2,
                     [WINDOW_WIDTH - 2, (paddle1_y - paddle_size) + (pulse_effect / 10)],
                     [WINDOW_WIDTH - 2, paddle1_y + paddle_size - (pulse_effect / 10)],
                     paddle_thickness)

    pygame.draw.line(screen, white_effect_color,
                     [0, paddle2_y - paddle_size + (pulse_effect / 10)],
                     [0, paddle2_y + paddle_size - (pulse_effect / 10)],
                     paddle2_thickness)



    # Мяч
    for obj in Balls_list:
        obj.Color = WHITE
        pygame.draw.circle(screen, obj.Color, (obj.PosX, obj.PosY), obj.Radius)

    # Анимированное изображение мяча
    ball_img_x = (WINDOW_WIDTH / 2 - ball_radius * 3)
    ball_img_y = (WINDOW_HEIGHT / 2 - ball_radius * 3) + (math.cos(animation_step / 50) * 100)
    #screen.blit(ball_image, (ball_img_x, ball_img_y))

    # Таймер событий
    pygame.draw.line(screen, WHITE, [0, WINDOW_HEIGHT - 1],
                     [0 + event_timer, WINDOW_HEIGHT - 1], 20)
    pygame.draw.line(screen_buffer, WHITE, [0, WINDOW_HEIGHT - 1],
                     [0 + event_timer, WINDOW_HEIGHT - 1], 20)

    # Текст с названиями событий
    text_pos = ((WINDOW_WIDTH / 2) - ((len(events_list_text) / 2) * 10), WINDOW_HEIGHT - 40)
    screen.blit(text_surface, text_pos)

    # Экран паузы
    if pause_state > 0:
        paused_bg = pygame.transform.scale(pause_background, (
            paused_bg.get_width() + (50 * (WINDOW_WIDTH - paused_bg.get_width()) / 100),
            paused_bg.get_height() + (50 * (WINDOW_WIDTH / 2 - paused_bg.get_height()) / 100)))
        screen.blit(paused_bg, (bg_x, bg_y))

    # Обновление экрана
    #pygame.display.update()
    pygame.display.flip()
    game_clock.tick(TICK)


# Завершение игры
pygame.quit()
