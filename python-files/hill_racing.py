import pygame
import math
import random

# --- Константы игры ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
LIGHT_GREEN = (50, 255, 50)
DARK_GREEN = (0, 150, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
GREY = (100, 100, 100)
LIGHT_GREY = (180, 180, 180)

# Физика
GRAVITY = 0.5
FRICTION = 0.98  # Применяется к скорости при движении по земле
AIR_RESISTANCE = 0.99  # Применяется к скорости в воздухе
ANGULAR_FRICTION = 0.95 # Трение для вращения в воздухе
BOUNCE_FACTOR = 0.3 # Насколько сильно отскакивает при приземлении

# Параметры игрока (машины)
CAR_WIDTH = 60
CAR_HEIGHT = 20
WHEEL_RADIUS = 8
WHEEL_OFFSET_X = CAR_WIDTH // 3
WHEEL_OFFSET_Y = CAR_HEIGHT // 2 + WHEEL_RADIUS // 2

CAR_MAX_SPEED = 10
CAR_ACCELERATION = 0.2
CAR_BRAKE_FORCE = 0.3
CAR_ROTATION_SPEED = 3 # Скорость вращения в воздухе

HILL_SEGMENT_LENGTH = 50 # Длина сегмента при генерации холмов
HILL_AMPLITUDE_RANGE = (50, 150) # Диапазон высот холмов
HILL_FREQUENCY_RANGE = (0.01, 0.03) # Диапазон частот холмов (для волнистости)
TOTAL_HILL_LENGTH = SCREEN_WIDTH * 5 # Общая длина трассы (в 5 раз больше экрана)

# --- Инициализация Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hill Racing Simulator")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # Шрифт для текста

# --- Класс Car (Машина) ---
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.angle = 0  # Угол в градусах (0 - горизонтально, положительный - по часовой стрелке)
        self.angular_velocity = 0 # Скорость вращения в воздухе
        self.in_air = False

        self.color = RED

    def update(self, keys, ground_points):
        # Применение управления
        if keys[pygame.K_UP]:
            self.speed += CAR_ACCELERATION
        if keys[pygame.K_DOWN]:
            self.speed -= CAR_BRAKE_FORCE
        
        # Ограничение скорости
        self.speed = max(-CAR_MAX_SPEED, min(CAR_MAX_SPEED, self.speed))
        
        # Применение вращения в воздухе
        if self.in_air:
            if keys[pygame.K_LEFT]:
                self.angular_velocity += CAR_ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                self.angular_velocity -= CAR_ROTATION_SPEED
            
            self.angle += self.angular_velocity
            self.angular_velocity *= ANGULAR_FRICTION # Затухание вращения
            self.angle %= 360 # Ограничение угла от 0 до 360

        # Применение движения
        # Движение машины зависит от ее скорости и угла.
        # Однако, для упрощения, мы сначала обновим X, Y, а затем скорректируем Y под землю.
        self.x += self.speed * math.cos(math.radians(self.angle)) # Горизонтальное движение
        self.y += self.speed * math.sin(math.radians(self.angle)) # Вертикальное движение (не используется для гравитации)

        # Применение гравитации
        self.y += GRAVITY

        # Поиск точки на земле под машиной
        ground_y, ground_angle_rad = get_ground_y_and_slope(self.x, ground_points)
        
        # Проверка столкновения с землей
        car_bottom_y = self.y + CAR_HEIGHT / 2 # Центр машины
        
        if car_bottom_y >= ground_y:
            # Машина на земле
            self.y = ground_y - CAR_HEIGHT / 2 # Поднять машину на уровень земли
            
            if self.in_air: # Если только что приземлились
                # Отскок при приземлении
                self.speed *= BOUNCE_FACTOR
                self.in_air = False
                self.angular_velocity = 0 # Обнулить вращение при приземлении

            # Привязать угол машины к углу земли
            self.angle = -math.degrees(ground_angle_rad) # Pygame вращает против часовой стрелки, поэтому минус

            # Применение трения
            self.speed *= FRICTION
            
            # Изменение скорости в зависимости от уклона
            # На крутом подъеме замедляемся, на спуске ускоряемся
            slope_factor = math.sin(ground_angle_rad) # Положительный для спуска, отрицательный для подъема
            self.speed += slope_factor * 0.5 # Регулируйте это значение для изменения "скольжения"

        else:
            # Машина в воздухе
            self.in_air = True
            # Применение сопротивления воздуха
            self.speed *= AIR_RESISTANCE

    def draw(self, screen, camera_offset_x):
        # Позиция машины относительно камеры
        draw_x = self.x - camera_offset_x
        draw_y = self.y

        # Рисуем корпус машины (поворачиваем)
        car_surf = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        car_surf.fill(self.color)
        
        # Рисуем кабину/верх машины
        cab_width = CAR_WIDTH * 0.6
        cab_height = CAR_HEIGHT * 0.8
        cab_x = (CAR_WIDTH - cab_width) / 2
        cab_y = -cab_height / 2
        pygame.draw.rect(car_surf, GREY, (cab_x, cab_y, cab_width, cab_height), border_radius=3)
        pygame.draw.rect(car_surf, LIGHT_GREY, (cab_x + 5, cab_y + 5, cab_width - 10, cab_height - 10), border_radius=2)


        rotated_car = pygame.transform.rotate(car_surf, self.angle)
        rotated_rect = rotated_car.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated_car, rotated_rect)

        # Рисуем колеса
        # Колеса должны быть привязаны к корпусу, но вращаться независимо (визуально)
        # Для простоты, пока просто рисуем их без вращения
        wheel1_offset_x = -WHEEL_OFFSET_X
        wheel2_offset_x = WHEEL_OFFSET_X
        
        # Поворачиваем смещения колес
        angle_rad = math.radians(self.angle)
        
        # Переднее колесо
        wx1 = draw_x + wheel1_offset_x * math.cos(angle_rad) - WHEEL_OFFSET_Y * math.sin(angle_rad)
        wy1 = draw_y + wheel1_offset_x * math.sin(angle_rad) + WHEEL_OFFSET_Y * math.cos(angle_rad)
        pygame.draw.circle(screen, BLACK, (int(wx1), int(wy1)), WHEEL_RADIUS)
        pygame.draw.circle(screen, WHITE, (int(wx1), int(wy1)), WHEEL_RADIUS // 2, 1)

        # Заднее колесо
        wx2 = draw_x + wheel2_offset_x * math.cos(angle_rad) - WHEEL_OFFSET_Y * math.sin(angle_rad)
        wy2 = draw_y + wheel2_offset_x * math.sin(angle_rad) + WHEEL_OFFSET_Y * math.cos(angle_rad)
        pygame.draw.circle(screen, BLACK, (int(wx2), int(wy2)), WHEEL_RADIUS)
        pygame.draw.circle(screen, WHITE, (int(wx2), int(wy2)), WHEEL_RADIUS // 2, 1)


# --- Генерация ландшафта (холмов) ---
def generate_ground(length, segment_len, screen_height_offset):
    points = []
    current_x = 0
    current_y = screen_height_offset # Начальная высота земли

    while current_x < length:
        points.append((current_x, current_y))

        # Генерация следующей точки
        next_x = current_x + segment_len
        
        # Случайное изменение высоты для создания холмов
        # Используем sin/cos для более плавных холмов
        amplitude = random.uniform(*HILL_AMPLITUDE_RANGE)
        frequency = random.uniform(*HILL_FREQUENCY_RANGE)
        
        # Создаем волну для следующего участка
        next_y = screen_height_offset + amplitude * math.sin(frequency * current_x) \
                 + random.randint(-20, 20) # Немного случайного шума

        # Убедимся, что земля не уходит за пределы экрана слишком сильно
        next_y = max(screen_height_offset - SCREEN_HEIGHT / 4, min(screen_height_offset + SCREEN_HEIGHT / 4, next_y))

        current_x = next_x
        current_y = next_y
    
    # Добавить последнюю точку
    points.append((length, current_y))
    return points

def get_ground_y_and_slope(x, ground_points):
    """
    Возвращает высоту земли и угол уклона в заданной X-координате.
    Использует линейную интерполяцию между точками земли.
    """
    for i in range(len(ground_points) - 1):
        x1, y1 = ground_points[i]
        x2, y2 = ground_points[i+1]

        if x1 <= x <= x2:
            # Найдена правильная пара точек
            if x2 == x1: # Избегаем деления на ноль
                return y1, 0.0
            
            # Линейная интерполяция для Y
            ratio = (x - x1) / (x2 - x1)
            interpolated_y = y1 + ratio * (y2 - y1)
            
            # Угол наклона
            angle_rad = math.atan2(y2 - y1, x2 - x1)
            return interpolated_y, angle_rad
    
    # Если X вне сгенерированного диапазона земли (например, в конце трассы),
    # используем последнюю точку или плоскую линию
    if x < ground_points[0][0]:
        return ground_points[0][1], 0.0
    return ground_points[-1][1], 0.0 # В конце трассы - плоская линия


# --- Главная игровая функция ---
def main():
    running = True

    # Игрок (машина)
    player_car = Car(x=SCREEN_WIDTH // 4, y=SCREEN_HEIGHT // 2)

    # Генерация земли
    ground_points = generate_ground(TOTAL_HILL_LENGTH, HILL_SEGMENT_LENGTH, SCREEN_HEIGHT * 0.7)

    # Смещение камеры
    camera_offset_x = 0

    # Время (для подсчета)
    start_time = pygame.time.get_ticks() # Время в миллисекундах
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Обновление машины
        player_car.update(keys, ground_points)

        # Обновление смещения камеры (следует за машиной)
        camera_offset_x = player_car.x - SCREEN_WIDTH // 4 # Машина находится на четверти экрана
        
        # Ограничение камеры, чтобы не выходить за границы сгенерированной земли
        max_camera_offset_x = TOTAL_HILL_LENGTH - SCREEN_WIDTH
        camera_offset_x = max(0, min(camera_offset_x, max_camera_offset_x))


        # --- Отрисовка ---
        screen.fill(SKY_BLUE) # Фон - небо

        # Рисуем дальние горы (декорации)
        for i in range(3):
            mountain_x = (i * 400 + 50 - camera_offset_x * 0.5) % (TOTAL_HILL_LENGTH + 400) # Параллакс
            pygame.draw.polygon(screen, DARK_GREEN, [
                (mountain_x, SCREEN_HEIGHT * 0.8), 
                (mountain_x + 200, SCREEN_HEIGHT * 0.4), 
                (mountain_x + 400, SCREEN_HEIGHT * 0.8)
            ])
            pygame.draw.polygon(screen, GREEN, [
                (mountain_x + 100, SCREEN_HEIGHT * 0.75), 
                (mountain_x + 300, SCREEN_HEIGHT * 0.3), 
                (mountain_x + 500, SCREEN_HEIGHT * 0.75)
            ])

        # Рисуем землю
        ground_display_points = []
        for x, y in ground_points:
            ground_display_points.append((x - camera_offset_x, y))
        
        if len(ground_display_points) > 1:
            pygame.draw.lines(screen, DARK_GREEN, False, ground_display_points, 5) # Верхний контур земли
            
            # Заполняем область под землей
            # Создаем многоугольник из точек земли и нижних углов экрана
            ground_polygon_points = ground_display_points + [
                (ground_display_points[-1][0], SCREEN_HEIGHT),
                (ground_display_points[0][0], SCREEN_HEIGHT)
            ]
            pygame.draw.polygon(screen, BROWN, ground_polygon_points)


        # Рисуем машину
        player_car.draw(screen, camera_offset_x)

        # Вывод информации на экран
        speed_text = font.render(f"Скорость: {player_car.speed:.1f} м/с", True, BLACK)
        screen.blit(speed_text, (10, 10))

        distance_text = font.render(f"Дистанция: {player_car.x:.0f} м", True, BLACK)
        screen.blit(distance_text, (10, 40))

        # Вывод таймера
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000 # В секундах
        timer_text = font.render(f"Время: {elapsed_time:.1f} с", True, BLACK)
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, 10))

        # Проверка на окончание трассы
        if player_car.x >= TOTAL_HILL_LENGTH - 100: # Завершение трассы
            end_game_text = font.render("Трасса завершена! Поздравляем!", True, BLACK)
            text_rect = end_game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(end_game_text, text_rect)
            running = False # Остановка игры

        pygame.display.flip() # Обновление экрана
        clock.tick(FPS) # Ограничение FPS

    pygame.quit()

if __name__ == "__main__":
    main()