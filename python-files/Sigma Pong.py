import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong 2D z wyborem trybu i trudności")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 33, 23)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
PADDLE_SPEED = 6
BALL_SIZE = 40

font = pygame.font.SysFont("Arial", 28)
large_font = pygame.font.SysFont("Arial", 72)
logo_font = pygame.font.SysFont("Arial", 40, bold=True)

clock = pygame.time.Clock()

def draw_gradient(surface, color1, color2):
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

def create_ball_texture(size):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 100, 100), (size//2, size//2), size//2)
    pygame.draw.line(surface, (200, 50, 50), (size//2, 0), (size//2, size), 3)
    pygame.draw.line(surface, (200, 50, 50), (0, size//2), (size, size//2), 3)
    return surface

def draw_logo(surface, x, y):
    logo_width, logo_height = 60, 40
    pygame.draw.rect(surface, RED, (x, y, logo_width, logo_height), border_radius=8)
    tri_points = [
        (x + logo_width * 0.4, y + logo_height * 0.3),
        (x + logo_width * 0.75, y + logo_height * 0.5),
        (x + logo_width * 0.4, y + logo_height * 0.7)
    ]
    pygame.draw.polygon(surface, WHITE, tri_points)
    text = logo_font.render("Dytron", True, WHITE)
    surface.blit(text, (x + logo_width + 10, y + logo_height // 2 - text.get_height() // 2))

def draw_menu(surface, selected_option, selected_difficulty, menu_stage):
    surface.fill(BLACK)
    title = large_font.render("MENU PAUZY", True, WHITE)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 8))

    if menu_stage == 0:
        text = font.render("Wybierz tryb gry:", True, WHITE)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

        modes = ["Singleplayer", "Multiplayer"]
        for i, mode in enumerate(modes):
            color = (255, 255, 0) if i == selected_option else WHITE
            prefix = "→ " if i == selected_option else "  "
            mode_text = font.render(prefix + mode, True, color)
            surface.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, HEIGHT // 3 + 40 + i * 30))

    elif menu_stage == 1:
        text = font.render("Wybierz poziom trudności:", True, WHITE)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

        difficulties = ["Łatwy", "Średni", "Trudny"]
        for i, diff in enumerate(difficulties):
            color = (255, 255, 0) if i == selected_difficulty else WHITE
            prefix = "→ " if i == selected_difficulty else "  "
            diff_text = font.render(prefix + diff, True, color)
            surface.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, HEIGHT // 3 + 40 + i * 30))

    elif menu_stage == 2:
        text = font.render("MENU", True, WHITE)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

        options = ["Wznów", "Wyjdź"]
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else WHITE
            prefix = "→ " if i == selected_option else "  "
            option_text = font.render(prefix + option, True, color)
            surface.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, HEIGHT // 3 + 40 + i * 30))

    draw_logo(surface, WIDTH // 2 - 100, HEIGHT - 100)
    pygame.display.update()

def draw_game_over(surface, score1, score2):
    surface.fill(BLACK)
    text1 = large_font.render("GAME OVER", True, (255, 50, 50))
    text2 = font.render(f"Wynik gracz 1: {score1}   Wynik gracz 2: {score2}", True, WHITE)
    text3 = font.render("Naciśnij SPACJĘ, aby zacząć nową grę", True, WHITE)
    surface.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 4))
    surface.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2))
    surface.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 60))
    draw_logo(surface, WIDTH // 2 - 100, HEIGHT // 2 + 150)
    pygame.display.update()

def ai_move(paddle, ball, difficulty):
    if difficulty == 0:
        ai_speed = 2
        margin = 40
    elif difficulty == 1:
        ai_speed = 4
        margin = 20
    else:
        ai_speed = 6
        margin = 5

    if paddle.centery < ball.centery - margin:
        paddle.y += ai_speed
    elif paddle.centery > ball.centery + margin:
        paddle.y -= ai_speed

    if paddle.top < 0:
        paddle.top = 0
    if paddle.bottom > HEIGHT:
        paddle.bottom = HEIGHT

def main():
    paddle1 = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_speed = [random.choice([-4, 4]), random.choice([-4, 4])]

    ball_texture = create_ball_texture(BALL_SIZE)

    score1 = 0
    score2 = 0
    max_score = 10

    paused = True
    in_game_over = False

    menu_stage = 0
    selected_mode = 0
    selected_difficulty = 1
    selected_menu_option = 0

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not in_game_over:
                    if event.key == pygame.K_ESCAPE:
                        if menu_stage == 2:
                            paused = not paused
                            if paused:
                                menu_stage = 2
                            else:
                                menu_stage = None
                        else:
                            paused = True
                            menu_stage = 0
                            selected_mode = 0
                            selected_difficulty = 1
                            selected_menu_option = 0

                    if paused:
                        if event.key == pygame.K_UP:
                            if menu_stage == 0:
                                selected_mode = (selected_mode - 1) % 2
                            elif menu_stage == 1:
                                selected_difficulty = (selected_difficulty - 1) % 3
                            elif menu_stage == 2:
                                selected_menu_option = (selected_menu_option - 1) % 2

                        elif event.key == pygame.K_DOWN:
                            if menu_stage == 0:
                                selected_mode = (selected_mode + 1) % 2
                            elif menu_stage == 1:
                                selected_difficulty = (selected_difficulty + 1) % 3
                            elif menu_stage == 2:
                                selected_menu_option = (selected_menu_option + 1) % 2

                        elif event.key == pygame.K_RETURN:
                            if menu_stage == 0:
                                if selected_mode == 0:
                                    menu_stage = 1
                                else:
                                    menu_stage = 2
                                selected_menu_option = 0

                            elif menu_stage == 1:
                                paused = False
                                menu_stage = None
                                in_game_over = False
                                score1 = 0
                                score2 = 0
                                paddle1.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
                                paddle2.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
                                ball.center = (WIDTH // 2, HEIGHT // 2)
                                ball_speed = [random.choice([-4, 4]), random.choice([-4, 4])]

                            elif menu_stage == 2:
                                if selected_menu_option == 0:
                                    paused = False
                                    menu_stage = None
                                else:
                                    running = False

                else:
                    if event.key == pygame.K_SPACE:
                        in_game_over = False
                        paused = True
                        menu_stage = 0
                        score1 = 0
                        score2 = 0
                        paddle1.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
                        paddle2.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
                        ball.center = (WIDTH // 2, HEIGHT // 2)
                        ball_speed = [random.choice([-4, 4]), random.choice([-4, 4])]

        if not paused and not in_game_over:
            keys = pygame.key.get_pressed()

            # Ruch gracza 1 (WSAD)
            if keys[pygame.K_w] and paddle1.top > 0:
                paddle1.y -= PADDLE_SPEED
            if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
                paddle1.y += PADDLE_SPEED

            if menu_stage != 2:  # Jeśli multiplayer
                if selected_mode == 1:
                    # Ruch gracza 2 (Strzałki)
                    if keys[pygame.K_UP] and paddle2.top > 0:
                        paddle2.y -= PADDLE_SPEED
                    if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
                        paddle2.y += PADDLE_SPEED
                else:
                    # AI sterowanie paddle2
                    ai_move(paddle2, ball, selected_difficulty)

            # Ruch piłki
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]

            # Odbicia od góry i dołu
            if ball.top <= 0:
                ball_speed[1] = abs(ball_speed[1])
            if ball.bottom >= HEIGHT:
                ball_speed[1] = -abs(ball_speed[1])

            # Odbicia od paletek
            if ball.colliderect(paddle1):
                ball_speed[0] = abs(ball_speed[0])
            if ball.colliderect(paddle2):
                ball_speed[0] = -abs(ball_speed[0])

            # Punkt dla gracza 1 (piłka wyszła za prawą krawędź)
            if ball.left > WIDTH:
                score1 += 1
                ball.center = (WIDTH // 2, HEIGHT // 2)
                ball_speed = [random.choice([-4, 4]), random.choice([-4, 4])]

            # Punkt dla gracza 2 (piłka wyszła za lewą krawędź)
            if ball.right < 0:
                score2 += 1
                ball.center = (WIDTH // 2, HEIGHT // 2)
                ball_speed = [random.choice([-4, 4]), random.choice([-4, 4])]

            if score1 >= max_score or score2 >= max_score:
                in_game_over = True
                paused = True
                menu_stage = None

            draw_gradient(WIN, (10, 30, 50), (40, 70, 100))
            pygame.draw.rect(WIN, WHITE, paddle1)
            pygame.draw.rect(WIN, WHITE, paddle2)
            WIN.blit(ball_texture, ball.topleft)

            score_text = font.render(f"{score1} : {score2}", True, WHITE)
            WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
            draw_logo(WIN, WIDTH // 2 - 100, HEIGHT - 100)

            pygame.display.update()

        elif paused:
            if in_game_over:
                draw_game_over(WIN, score1, score2)
            else:
                draw_menu(WIN, selected_mode if menu_stage == 0 else selected_menu_option if menu_stage == 2 else None, selected_difficulty, menu_stage)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
