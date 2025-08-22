# game_dark.py
import pygame # type: ignore
import random
import sys
import winsound
import threading
import os

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Поймай шарик! — Тёмная версия")

# === ЦВЕТА (тёмная тема) ===
BG_COLOR = (20, 20, 30)        # Глубокий тёмно-синий фон
TEXT_COLOR = (220, 220, 240)   # Светлый текст
BALL_OUTLINE = (180, 180, 200) # Обводка шариков
RED = (255, 80, 80)
BLUE = (80, 120, 255)
GOLD = (255, 215, 0)
GREEN = (80, 200, 100)
PURPLE = (200, 100, 255)
GRAY = (60, 60, 80)
BUTTON_COLOR = (50, 100, 180)

# === ШРИФТЫ ===
font_large = pygame.font.SysFont(None, 64)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 32)
font_tiny = pygame.font.SysFont(None, 24)

# === ЗВУКИ ЧЕРЕЗ WINSOUND (для Windows) ===
def play_click():
    threading.Thread(target=lambda: winsound.Beep(800, 100), daemon=True).start()

def play_miss():
    threading.Thread(target=lambda: winsound.Beep(400, 200), daemon=True).start()

def play_level_up():
    def sequence():
        winsound.Beep(600, 100)
        pygame.time.wait(50)
        winsound.Beep(800, 150)
    threading.Thread(target=sequence, daemon=True).start()

def play_alert():
    threading.Thread(target=lambda: winsound.Beep(500, 300), daemon=True).start()

# === КЛАСС ШАРИКА ===
class Ball:
    def __init__(self, level):
        self.radius = random.randint(15, 40 - level)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.lifetime = 120 - level * 5
        self.level = level

        self.type = random.choices(['normal', 'fast', 'rare'], weights=[70, 20, 10])[0]

        if self.type == 'normal':
            self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            self.points = 1
            self.speed_mult = 1
        elif self.type == 'fast':
            self.color = RED
            self.points = 2
            self.speed_mult = 1.5
            self.lifetime = max(30, self.lifetime - 20)
        elif self.type == 'rare':
            self.color = GOLD
            self.points = 5
            self.speed_mult = 0.8
            self.radius = random.randint(25, 50)

    def draw(self, surface):
        # Основной круг
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        # Обводка
        pygame.draw.circle(surface, BALL_OUTLINE, (self.x, self.y), self.radius, width=3)
        # Звезда для редких
        if self.type == 'rare':
            star = font_small.render("★", True, (255, 255, 200))
            rect = star.get_rect(center=(self.x, self.y - 2))
            surface.blit(star, rect)

    def is_clicked(self, pos):
        distance = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
        return distance <= self.radius

    def update(self):
        self.lifetime -= self.speed_mult
        return self.lifetime > 0

# === ОТВЛЕКАЮЩИЕ КАРТИНКИ ===
class Distraction:
    def __init__(self):
        self.side = random.choice(['left', 'right', 'top', 'bottom'])
        self.duration = random.randint(40, 100)
        self.lifetime = 0

        self.width = 180
        self.height = 120

        padding = 20
        if self.side == 'left':
            self.rect = pygame.Rect(padding, random.randint(50, HEIGHT - 50 - self.height), self.width, self.height)
        elif self.side == 'right':
            self.rect = pygame.Rect(WIDTH - self.width - padding, random.randint(50, HEIGHT - 50 - self.height), self.width, self.height)
        elif self.side == 'top':
            self.rect = pygame.Rect(random.randint(50, WIDTH - 50 - self.width), padding, self.width, self.height)
        elif self.side == 'bottom':
            self.rect = pygame.Rect(random.randint(50, WIDTH - 50 - self.width), HEIGHT - self.height - padding, self.width, self.height)

        # Загрузка случайной картинки из папки
        images = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        self.image = None
        if images:
            try:
                img_path = random.choice(images)
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (self.width, self.height))
                self.image = img
            except Exception as e:
                print(f"Не удалось загрузить {img_path}: {e}")

        # Заглушка, если нет картинок
        if not self.image:
            self.image = pygame.Surface((self.width, self.height))
            color = random.choice([RED, BLUE, GREEN, GOLD, PURPLE, (100, 100, 150)])
            self.image.fill(color)
            warning = font_tiny.render("НЕ КЛИКАЙ!", True, (255, 255, 200))
            text_rect = warning.get_rect(center=(self.width//2, self.height//2))
            self.image.blit(warning, text_rect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Стрелка
        if self.side == 'left':
            pygame.draw.polygon(surface, TEXT_COLOR, [
                (self.rect.left - 10, self.rect.centery),
                (self.rect.left, self.rect.top),
                (self.rect.left, self.rect.bottom)
            ])
        elif self.side == 'right':
            pygame.draw.polygon(surface, TEXT_COLOR, [
                (self.rect.right + 10, self.rect.centery),
                (self.rect.right, self.rect.top),
                (self.rect.right, self.rect.bottom)
            ])
        elif self.side == 'top':
            pygame.draw.polygon(surface, TEXT_COLOR, [
                (self.rect.centerx, self.rect.top - 10),
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.top)
            ])
        elif self.side == 'bottom':
            pygame.draw.polygon(surface, TEXT_COLOR, [
                (self.rect.centerx, self.rect.bottom + 10),
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.bottom)
            ])

    def update(self):
        self.lifetime += 1
        return self.lifetime < self.duration

# === КНОПКА ===
class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 3, border_radius=12)
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# === МЕНЮ ===
def main_menu():
    button_play = Button(WIDTH//2 - 150, HEIGHT//2, 300, 80, "Играть")
    button_quit = Button(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 80, "Выйти", color=RED)

    while True:
        screen.fill(BG_COLOR)

        title = font_large.render("Поймай шарик!", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(title, title_rect)

        button_play.draw(screen)
        button_quit.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.is_clicked(event.pos):
                    return
                if button_quit.is_clicked(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

# === ОСНОВНАЯ ИГРА ===
def main():
    clock = pygame.time.Clock()
    balls = []
    distractions = []
    score = 0
    level = 1
    time_left = 90  # 90 секунд
    spawn_timer = 0
    distraction_timer = 0
    level_up_score = 10

    main_menu()

    running = True
    game_over = False
    start_ticks = pygame.time.get_ticks()

    while running:
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = max(0, 90 - seconds_passed)

        if time_left <= 0 and not game_over:
            game_over = True

        screen.fill(BG_COLOR)  # Тёмный фон

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    clicked = False
                    for ball in balls[:]:
                        if ball.is_clicked(event.pos):
                            score += ball.points
                            balls.remove(ball)
                            play_click()
                            clicked = True
                            break
                    if not clicked:
                        pass  # Промах — ничего

        if game_over:
            over_text = font_large.render("Игра окончена!", True, GOLD)
            score_text = font_medium.render(f"Очки: {score}", True, TEXT_COLOR)
            level_text = font_medium.render(f"Уровень: {level}", True, GREEN)
            restart_text = font_small.render("Нажмите R, чтобы начать заново", True, TEXT_COLOR)
            menu_text = font_small.render("Нажмите ESC, чтобы в меню", True, TEXT_COLOR)

            screen.blit(over_text, over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
            screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
            screen.blit(level_text, level_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 110)))
            screen.blit(menu_text, menu_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 150)))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()
            if keys[pygame.K_ESCAPE]:
                main_menu()

        else:
            # Повышение уровня
            if score >= level * level_up_score:
                new_level = score // level_up_score + 1
                if new_level > level:
                    level = new_level
                    play_level_up()

            # Спавн шариков
            spawn_timer += 1
            spawn_rate = max(10, 60 - level * 5)
            if spawn_timer >= spawn_rate:
                balls.append(Ball(level))
                spawn_timer = 0

            # Спавн отвлечений
            distraction_timer += 1
            if distraction_timer >= random.randint(180, 300):
                distractions.append(Distraction())
                play_alert()
                distraction_timer = 0

            # Обновление шариков
            for ball in balls[:]:
                if not ball.update():
                    balls.remove(ball)
                    play_miss()
                else:
                    ball.draw(screen)

            # Обновление отвлечений
            for d in distractions[:]:
                if not d.update():
                    distractions.remove(d)
                else:
                    d.draw(screen)

            # UI
            timer_text = font_small.render(f"Время: {time_left}", True, TEXT_COLOR)
            score_text = font_small.render(f"Очки: {score}", True, TEXT_COLOR)
            level_text = font_small.render(f"Уровень: {level}", True, GREEN)

            screen.blit(timer_text, (10, 10))
            screen.blit(score_text, (10, 50))
            screen.blit(level_text, (10, 90))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# === ЗАПУСК ===
if __name__ == "__main__":
    main()