import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 1200, 800
FPS = 60
TARGET_RADIUS = 23
LEVELS = [5, 10, 15, 20, 25]


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

main_menu_background = pygame.image.load('037.jpg')
game_background = pygame.image.load('max.jpg')

main_menu_background = pygame.transform.scale(main_menu_background, (WIDTH, HEIGHT))
game_background = pygame.transform.scale(game_background, (WIDTH, HEIGHT))


class Target:
    def __init__(self, speed):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.speed_x = speed * random.choice([-1, 1])
        self.speed_y = speed * random.choice([-1, 1])

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), TARGET_RADIUS)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Отскок от стен
        if self.x <= TARGET_RADIUS or self.x >= WIDTH - TARGET_RADIUS:
            self.speed_x *= -1
        if self.y <= TARGET_RADIUS or self.y >= HEIGHT - TARGET_RADIUS:
            self.speed_y *= -1

    def is_hit(self, pos):
        return (pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2 <= TARGET_RADIUS ** 2


# Класс луча
class Beam:
    def __init__(self):
        self.angle = 0
        self.length = 75

    def draw(self, screen, start_pos):
        end_x = int(start_pos[0] + self.length * math.cos(math.radians(self.angle)))
        end_y = int(start_pos[1] + self.length * math.sin(math.radians(self.angle)))
        pygame.draw.line(screen, RED, start_pos, (end_x, end_y), 5)

    def rotate(self):
        self.angle += 5


def draw_button(screen, text, x, y, width, height):
    font = pygame.font.Font(None, 24)
    pygame.draw.rect(screen, WHITE, (x, y, width, height))
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def select_level():
    while True:
        screen.blit(main_menu_background, (0, 0))
        font = pygame.font.Font(None, 90)
        title_text = font.render("Выберите уровень:", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 5))

        for i in range(len(LEVELS)):
            draw_button(screen,
                        f"Уровень {i + 1}: {LEVELS[i]} попаданий",
                        WIDTH // 2 - 100,
                        HEIGHT // 4 + (i + 1) * 60,
                        200,
                        40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    for i in range(len(LEVELS)):
                        if HEIGHT // 4 + (i + 1) * 60 <= mouse_pos[1] <= HEIGHT // 4 + (i + 1) * 60 + 30:
                            return LEVELS[i]


def display_level_completed_message():
    font = pygame.font.Font(None, 85)
    message_surface = font.render('WIN!', True, WHITE)
    message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    for scale in range(50, 500):
        screen.blit(game_background, (0, 0))
        scaled_surface = pygame.transform.scale(message_surface, (scale, scale // 3))
        scaled_rect = scaled_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        outline_surface = font.render("Уровень пройден", True, BLACK)
        outline_rect = outline_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        screen.blit(outline_surface, outline_rect)
        screen.blit(scaled_surface, scaled_rect)

        pygame.display.flip()
        pygame.time.delay(1)

    pygame.time.delay(1000)


def main():
    global screen
    total_hits = 0

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ART GUN")
    clock = pygame.time.Clock()

    while True:
        target_count = select_level()
        targets_hit = 0
        speed = target_count // 5 + 1

        targets = [Target(speed) for _ in range(target_count)]
        beam = None

        beam_start_pos = None

        while targets_hit < target_count:
            screen.blit(game_background, (0, 0))

            for target in targets:
                target.move()
                target.draw(screen)

            font = pygame.font.Font(None, 36)
            hits_text = font.render(f"Попадания: {targets_hit}/{target_count}", True, WHITE)
            screen.blit(hits_text, (WIDTH // 2 - hits_text.get_width() // 2, HEIGHT - 50))

            draw_button(screen,
                        "Выйти в меню",
                        WIDTH - 150,
                        HEIGHT - 50,
                        140,
                        30)

            if beam:
                beam.rotate()
                beam.draw(screen, beam_start_pos)

                for target in targets[:]:
                    if beam_start_pos and target.is_hit(beam_start_pos):
                        targets_hit += 1
                        total_hits += 1
                        targets.remove(target)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos

                        if WIDTH - 150 <= mouse_pos[0] <= WIDTH - 10 and HEIGHT - 50 <= mouse_pos[1] <= HEIGHT - 20:
                            break

                        beam_start_pos = event.pos
                        beam = Beam()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        beam_start_pos = None
                        beam = None

            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                break

            clock.tick(FPS)

        display_level_completed_message()


if __name__ == "__main__":
    main()
