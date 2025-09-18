# snake_f11_r.py
import pygame
import random
import sys

pygame.init()
pygame.display.set_caption("Snake - F11: Fullscreen, R: Yeniden Başla, ESC: Çık")

# Ayarlar
CELL_SIZE = 20
WINDOWED_SIZE = (640, 480)
BG_COLOR = (10, 10, 10)
SNAKE_COLOR = (0, 200, 0)
FOOD_COLOR = (200, 50, 50)
TEXT_COLOR = (220, 220, 220)
FPS = 60  # oyun hızı (yüksek yaparsanız yılan hızlanır)

# Global durumlar (başlangıçta pencere modu)
is_fullscreen = False
screen = pygame.display.set_mode(WINDOWED_SIZE)
width, height = WINDOWED_SIZE
cols = width // CELL_SIZE
rows = height // CELL_SIZE

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)
clock = pygame.time.Clock()

def new_food(snake):
    while True:
        pos = (random.randint(0, cols - 1), random.randint(0, rows - 1))
        if pos not in snake:
            return pos

def reset_game():
    global snake, direction, food, score, game_over, cols, rows
    cols = width // CELL_SIZE
    rows = height // CELL_SIZE
    start_x = cols // 2
    start_y = rows // 2
    snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
    direction = (1, 0)  # sağ
    food = new_food(snake)
    score = 0
    game_over = False

def toggle_fullscreen():
    global is_fullscreen, screen, width, height, cols, rows
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    else:
        width, height = WINDOWED_SIZE
        screen = pygame.display.set_mode(WINDOWED_SIZE)
    cols = width // CELL_SIZE
    rows = height // CELL_SIZE
    # oyunu yeniden hesapla
    reset_game()

def draw_rect_grid(pos, color):
    x, y = pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

def draw_text_center(text, font_obj, y):
    surf = font_obj.render(text, True, TEXT_COLOR)
    rect = surf.get_rect(center=(width // 2, y))
    screen.blit(surf, rect)

# Başlangıç
toggle_fullscreen()  # fullscreen değişikliği reset_game çağırdığı için oyunu başlatır
# Ama başlangıçta is_fullscreen default False, toggle ile önce fullscreen True oluyor.
# Kullanıcı isterse F11'le değiştirebilir. Eğer otomatik fullscreen istenmezse
# yukarıdaki satırı `reset_game()` ile değiştirin. Burada daha stabil başlatmak için:
# reset_game()

# (Eğer otomatik fullscreen istemezseniz, aşağıdaki satırı aktif edin ve toggle_fullscreen() satırını silin)
# reset_game()

# Ancak kullanıcı genelde pencere modunda başlatmak ister; o yüzden düz reset yapalım:
is_fullscreen = False
screen = pygame.display.set_mode(WINDOWED_SIZE)
width, height = WINDOWED_SIZE
cols = width // CELL_SIZE
rows = height // CELL_SIZE
reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_F11:
                toggle_fullscreen()
            if event.key == pygame.K_r:  # her durumda yeniden başlat
                reset_game()
            # yön tuşları (yeni yön, tersine dönmeyi engelle)
            if not game_over:
                if event.key == pygame.K_UP:
                    if direction != (0, 1):
                        direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    if direction != (0, -1):
                        direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    if direction != (1, 0):
                        direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if direction != (-1, 0):
                        direction = (1, 0)

    if not game_over:
        # Yeni baş
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Duvara çarpma kontrolü (oyunu bitir)
        if not (0 <= new_head[0] < cols and 0 <= new_head[1] < rows):
            game_over = True
        else:
            # kendi üzerine çarpma
            if new_head in snake:
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    food = new_food(snake)
                else:
                    snake.pop()

    # Çizimler
    screen.fill(BG_COLOR)

    # Yem
    draw_rect_grid(food, FOOD_COLOR)

    # Yılan
    for segment in snake:
        draw_rect_grid(segment, SNAKE_COLOR)

    # Skor
    score_surf = font.render(f"Skor: {score}", True, TEXT_COLOR)
    screen.blit(score_surf, (10, 10))

    # Yardım bilgisi
    help_surf = font.render("F11: Tam Ekran  R: Yeniden  ESC: Çık", True, TEXT_COLOR)
    screen.blit(help_surf, (10, height - 30))

    if game_over:
        draw_text_center("Oyun Bitti!", big_font, height // 2 - 30)
        draw_text_center("R ile yeniden başla", font, height // 2 + 30)

    pygame.display.flip()
    clock.tick(FPS)
