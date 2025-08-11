import pygame
import sys
import random
import time

# ---------- Configuration ----------
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
GAME_WIDTH = CELL_SIZE * GRID_WIDTH
GAME_HEIGHT = CELL_SIZE * GRID_HEIGHT

HUD_HEIGHT = 120
BORDER = 5
WINDOW_WIDTH = GAME_WIDTH + BORDER * 2
WINDOW_HEIGHT = GAME_HEIGHT + BORDER * 2 + HUD_HEIGHT

FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREEN = (10, 100, 10)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (60, 60, 60)
BORDER_COLOR = (230, 230, 230)
HUD_BG = (230, 230, 230)

# ---------- Utilities ----------


def random_food_position(snake):
    positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]
    available = list(set(positions) - set(snake))
    return random.choice(available) if available else None


def draw_rect(surface, color, pos):
    x, y = pos
    rect = pygame.Rect(
        BORDER + x * CELL_SIZE,
        HUD_HEIGHT + BORDER + y * CELL_SIZE,
        CELL_SIZE, CELL_SIZE
    )
    pygame.draw.rect(surface, color, rect)

# ---------- Game ----------


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    big_font = pygame.font.SysFont("consolas", 48)

    def reset_game():
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        snake = [(start_x, start_y), (start_x - 1, start_y),
                 (start_x - 2, start_y)]
        direction = (1, 0)
        food = random_food_position(snake)
        score = 0
        start_time = time.time()
        return snake, direction, food, score, start_time

    def show_start_screen():
        waiting = True
        while waiting:
            screen.fill(BLACK)
            title_text = big_font.render("SNAKE GAME", True, WHITE)
            title_rect = title_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
            screen.blit(title_text, title_rect)

            start_text = font.render("Press any key to start", True, WHITE)
            start_rect = start_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            screen.blit(start_text, start_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    show_start_screen()

    snake, direction, food, score, start_time = reset_game()
    running = True
    paused = False
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if event.key == pygame.K_p:
                    paused = not paused
                if not game_over and not paused:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                        direction = (1, 0)
                if game_over and event.key == pygame.K_r:
                    snake, direction, food, score, start_time = reset_game()
                    game_over = False
                    paused = False

        if not running:
            break

        if not paused and not game_over:
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                    new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                if food and new_head == food:
                    score += 1
                    food = random_food_position(snake)
                    if food is None:
                        game_over = True
                else:
                    snake.pop()

        # ---------- Drawing ----------
        screen.fill(BORDER_COLOR)

        # HUD background
        pygame.draw.rect(screen, HUD_BG, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))

        # Draw HUD info
        elapsed_time = int(
            time.time() - start_time) if not game_over else int(start_time - start_time)
        score_surf = font.render(f"Score: {score}", True, BLACK)
        time_surf = font.render(f"Time: {elapsed_time}s", True, BLACK)
        screen.blit(score_surf, (30, 30))
        screen.blit(time_surf, (WINDOW_WIDTH - time_surf.get_width() - 30, 30))

        # Draw game background
        pygame.draw.rect(screen, BLACK, (BORDER, HUD_HEIGHT +
                         BORDER, GAME_WIDTH, GAME_HEIGHT))

        # Grid lines inside game area
        for x in range(GRID_WIDTH):
            pygame.draw.line(screen, GRAY,
                             (BORDER + x * CELL_SIZE, HUD_HEIGHT + BORDER),
                             (BORDER + x * CELL_SIZE, HUD_HEIGHT + BORDER + GAME_HEIGHT))
        for y in range(GRID_HEIGHT):
            pygame.draw.line(screen, GRAY,
                             (BORDER, HUD_HEIGHT + BORDER + y * CELL_SIZE),
                             (BORDER + GAME_WIDTH, HUD_HEIGHT + BORDER + y * CELL_SIZE))

        # Food
        if food:
            draw_rect(screen, RED, food)
        # Snake
        if snake:
            draw_rect(screen, DARK_GREEN, snake[0])
            for seg in snake[1:]:
                draw_rect(screen, GREEN, seg)

        # Messages
        if paused:
            pause_surf = big_font.render("PAUSED", True, WHITE)
            rect = pause_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(pause_surf, rect)
        if game_over:
            over_surf = big_font.render("GAME OVER", True, WHITE)
            rect = over_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            screen.blit(over_surf, rect)
            hint = font.render(
                "Press R to restart or ESC to quit", True, WHITE)
            screen.blit(
                hint, (rect.centerx - hint.get_width() // 2, rect.bottom + 8))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
