import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game with Perfect Tail Fit")

# Colors
LIGHT_GREEN = (170, 215, 81)
DARK_GREEN = (162, 209, 73)
GREEN_HEAD = (0, 255, 0)
GREEN_TAIL = (0, 155, 0)
RED = (220, 0, 0)
DARK_RED = (180, 0, 0)
WHITE = (255, 255, 255)
BLACK_EYE = (0, 0, 0)

FPS = 7

font_style = pygame.font.SysFont(None, 30)
score_font = pygame.font.SysFont(None, 35)

def draw_chessboard_background():
    rows = SCREEN_HEIGHT // CELL_SIZE
    cols = SCREEN_WIDTH // CELL_SIZE
    for row in range(rows):
        for col in range(cols):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(SCREEN, color, rect)

def draw_score(score):
    score_text = score_font.render("Score: " + str(score), True, WHITE)
    SCREEN.blit(score_text, (10, 10))

def draw_snake(snake_segments, x_change, y_change):
    tail_width = 14
    tail_height = 14

    for segment in snake_segments[:-1]:
        seg_x, seg_y = segment

        # Tail rectangle size smaller than CELL_SIZE
        # Position shift depends on movement direction to avoid gap

        if x_change > 0:  # Moving right
            tail_rect = pygame.Rect(seg_x, seg_y + (CELL_SIZE - tail_height)//2, tail_width, tail_height)
        elif x_change < 0:  # Moving left
            tail_rect = pygame.Rect(seg_x + (CELL_SIZE - tail_width), seg_y + (CELL_SIZE - tail_height)//2, tail_width, tail_height)
        elif y_change > 0:  # Moving down
            tail_rect = pygame.Rect(seg_x + (CELL_SIZE - tail_width)//2, seg_y, tail_width, tail_height)
        elif y_change < 0:  # Moving up
            tail_rect = pygame.Rect(seg_x + (CELL_SIZE - tail_width)//2, seg_y + (CELL_SIZE - tail_height), tail_width, tail_height)
        else:
            # Default center tail segment if no movement yet
            tail_rect = pygame.Rect(seg_x + (CELL_SIZE - tail_width)//2, seg_y + (CELL_SIZE - tail_height)//2, tail_width, tail_height)

        pygame.draw.rect(SCREEN, GREEN_TAIL, tail_rect)

    # Draw head full square
    head_x, head_y = snake_segments[-1]
    head_rect = pygame.Rect(head_x, head_y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(SCREEN, GREEN_HEAD, head_rect)

    # Eyes on head
    eye_radius = 3
    eye_offset = 5

    if x_change > 0:  # right
        left_eye_pos = (head_x + CELL_SIZE - eye_offset, head_y + eye_offset)
        right_eye_pos = (head_x + CELL_SIZE - eye_offset, head_y + CELL_SIZE - eye_offset)
    elif x_change < 0:  # left
        left_eye_pos = (head_x + eye_offset, head_y + eye_offset)
        right_eye_pos = (head_x + eye_offset, head_y + CELL_SIZE - eye_offset)
    elif y_change > 0:  # down
        left_eye_pos = (head_x + eye_offset, head_y + CELL_SIZE - eye_offset)
        right_eye_pos = (head_x + CELL_SIZE - eye_offset, head_y + CELL_SIZE - eye_offset)
    elif y_change < 0:  # up
        left_eye_pos = (head_x + eye_offset, head_y + eye_offset)
        right_eye_pos = (head_x + CELL_SIZE - eye_offset, head_y + eye_offset)
    else:
        left_eye_pos = (head_x + CELL_SIZE - eye_offset, head_y + eye_offset)
        right_eye_pos = (head_x + CELL_SIZE - eye_offset, head_y + CELL_SIZE - eye_offset)

    pygame.draw.circle(SCREEN, WHITE, left_eye_pos, eye_radius)
    pygame.draw.circle(SCREEN, WHITE, right_eye_pos, eye_radius)
    pygame.draw.circle(SCREEN, BLACK_EYE, left_eye_pos, 1)
    pygame.draw.circle(SCREEN, BLACK_EYE, right_eye_pos, 1)

def draw_food(food_position):
    center_x = food_position[0] + CELL_SIZE // 2
    center_y = food_position[1] + CELL_SIZE // 2
    radius = CELL_SIZE // 2

    pygame.draw.circle(SCREEN, RED, (center_x, center_y), radius)
    pygame.draw.circle(SCREEN, DARK_RED, (center_x + 4, center_y + 4), radius - 4)

    shine_rect = pygame.Rect(center_x - radius//2, center_y - radius//1.5, radius//2, radius//3)
    pygame.draw.ellipse(SCREEN, WHITE, shine_rect)

def message(msg, color, y_displace=0):
    mesg = font_style.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_displace))
    SCREEN.blit(mesg, mesg_rect)

def game_loop():
    snake_pos_x = SCREEN_WIDTH // 2
    snake_pos_y = SCREEN_HEIGHT // 2

    x_change = 0
    y_change = 0

    snake_segments = []
    snake_length = 1

    food_x = random.randrange(0, SCREEN_WIDTH - CELL_SIZE, CELL_SIZE)
    food_y = random.randrange(0, SCREEN_HEIGHT - CELL_SIZE, CELL_SIZE)

    score = 0
    game_over = False
    clock = pygame.time.Clock()

    while True:
        while game_over:
            draw_chessboard_background()
            message("Game Over!", RED, -30)
            message("Final Score: " + str(score), WHITE, 10)
            message("Press Enter to Restart or ESC to Quit", WHITE, 50)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_loop()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and x_change == 0:
                    x_change = -CELL_SIZE
                    y_change = 0
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and x_change == 0:
                    x_change = CELL_SIZE
                    y_change = 0
                elif (event.key == pygame.K_UP or event.key == pygame.K_w) and y_change == 0:
                    x_change = 0
                    y_change = -CELL_SIZE
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and y_change == 0:
                    x_change = 0
                    y_change = CELL_SIZE

        snake_pos_x += x_change
        snake_pos_y += y_change

        # Wrap-around edges
        if snake_pos_x < 0:
            snake_pos_x = SCREEN_WIDTH - CELL_SIZE
        elif snake_pos_x >= SCREEN_WIDTH:
            snake_pos_x = 0
        if snake_pos_y < 0:
            snake_pos_y = SCREEN_HEIGHT - CELL_SIZE
        elif snake_pos_y >= SCREEN_HEIGHT:
            snake_pos_y = 0

        snake_head = [snake_pos_x, snake_pos_y]
        snake_segments.append(snake_head)

        if len(snake_segments) > snake_length:
            del snake_segments[0]

        # Check self collision
        for segment in snake_segments[:-1]:
            if segment == snake_head:
                game_over = True
                break

        # Check food eaten
        if snake_pos_x == food_x and snake_pos_y == food_y:
            score += 1
            snake_length += 1
            while True:
                food_x = random.randrange(0, SCREEN_WIDTH - CELL_SIZE, CELL_SIZE)
                food_y = random.randrange(0, SCREEN_HEIGHT - CELL_SIZE, CELL_SIZE)
                if [food_x, food_y] not in snake_segments:
                    break

        draw_chessboard_background()
        draw_snake(snake_segments, x_change, y_change)
        draw_food([food_x, food_y])
        draw_score(score)

        pygame.display.update()
        clock.tick(FPS)

def draw_chessboard_background():
    rows = SCREEN_HEIGHT // CELL_SIZE
    cols = SCREEN_WIDTH // CELL_SIZE
    for row in range(rows):
        for col in range(cols):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(SCREEN, color, rect)

if __name__ == "__main__":
    game_loop()
