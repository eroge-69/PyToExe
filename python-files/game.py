import pygame, sys, random, math
from PIL.ImageStat import Global

pygame.init()
WIDTH, HEIGHT = 1060, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sigma Drop")
clock = pygame.time.Clock()
balance = 10
winning = 0
PANEL_COLOR = (175, 25, 25)
PANEL_COLOR2 = (125, 15, 15)
SCREEN_FILL_COLOR = (60, 60, 65)
font = pygame.font.SysFont(None, 36)
FPS = 60
game_mode = 0
offsets = [0, 0, 0]
COLUMN_SPEED = 2
STEP = 150
start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 145, 200, 60)
cashout_button_rect = start_button_rect
game = False
gamee = True
BACKWARD_DURATION = 100
backward_timer = 0
SLOWDOWN_STAGE = False
COLUMN_SPEEDS = [0, 0, 0]
DECEL_FACTORS = [0, 0, 0]
NUM_ELEMENTS = 5
SQUARE_PADDING = 15
SQUARE_COLOR = (80, 80, 80)
button_color = (50, 150, 50)
hover_color = (70, 200, 70)
GRID_COLS = 8
GRID_ROWS = 5
NUM_MINES = 8
CELL_SIZE = 70
CELL_SPACING = 5
mines = set()
revealed = set()
game2_reset_timer = 0
game2_active = False
game2_lost = False
game3_active = False
game3_exploded = False
coef3 = 1.0
CRASH_ZERO_CHANCE = 5
CRASH_POWER = 1.4
CRASH_LIMIT = 999
CRASH_DIVIDER = 1000
initial_radius = 30
max_radius = 150
SCREEN_FILL_COLOR = (60, 60, 65)
BUTTON_COLOR = (50, 150, 50)
HOVER_COLOR = (70, 200, 70)
YELLOW = (255, 230, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
rect_width, rect_height = 450, 300
rect_x = 305
rect_y = 140
button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 145, 200, 60)
selected_y = None
animating = False
win = False
anim_rect_y = 0
anim_height = 0
anim_coef = None
PEG_COLOR = (200, 200, 200)
BALL_COLOR = (255, 100, 100)
SLOT_COLORS = [(255, 0, 0), (255, 100, 0), (255, 200, 0), (100, 255, 100), (100, 255, 255), (100, 150, 255), (100, 150, 255), (100, 255, 255), (100, 255, 100), (255, 200, 0), (255, 100, 0), (255, 0, 0)] #[(255, 0, 0), (255, 100, 0), (255, 200, 0), (100, 255, 100), (100, 255, 255), (100, 150, 255), (200, 100, 255), (255, 0, 200)]
font5 = pygame.font.SysFont(None, 28)
GAME_LEFT, GAME_TOP = 212, 80
GAME_RIGHT, GAME_BOTTOM = 848, 520
peg_radius = 5
peg_spacing_x = 60
peg_spacing_y = 60
peg_rows = 7
peg_offset = peg_spacing_x // 2
ball_radius = 8
ball = None
ball_x, ball_y, ball_vx, ball_vy = 0, 0, 0, 2
pegs = []
peg_cols = 12
for row in range(peg_rows):
    offset = peg_offset if row % 2 else 0
    for col in range(peg_cols):
        x = GAME_LEFT + col * peg_spacing_x + offset + 20
        y = GAME_TOP + (row + 1) * peg_spacing_y
        if x + peg_radius < GAME_RIGHT:
            pegs.append((x, y))
slot_count = peg_cols
slot_width = 53
slots = [(GAME_LEFT + i * slot_width, GAME_BOTTOM - 40, slot_width, 40) for i in range(slot_count)]
slot_coefficients = [2, 1.5, 1.2, 1, 0.5, 0.1, 0.1, 0.5, 1, 1.2, 1.5, 2]
highlighted_slot = None
highlight_time = 0
circle_pos = (55, 55)
circle_radius = 50
def draw_background():
    global balance
    font = pygame.font.SysFont(None, 40)
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, 132, 600))
    pygame.draw.rect(screen, PANEL_COLOR, (928, 0, 132, 600))
    pygame.draw.polygon(screen, PANEL_COLOR, [(132, 0), (928, 0), (848, 80), (212, 80)])
    pygame.draw.polygon(screen, PANEL_COLOR, [(212, 520), (848, 520), (928, 600), (132, 600)])
    pygame.draw.polygon(screen, PANEL_COLOR2, [(132, 0), (212, 80), (212, 520), (132, 600)])
    pygame.draw.polygon(screen, PANEL_COLOR2, [(928, 0), (848, 80), (848, 520), (928, 600)])
    RECT8 = pygame.Rect(610, 85, 234, 41)
    mouse_pos = pygame.mouse.get_pos()  # Получаем позицию мыши
    color = (
        (255, 0, 0) if balance < 1 and start_button_rect.collidepoint(mouse_pos) and game_mode != 0
        else (button_color if balance >= 1 else (150, 0, 0))
    )
    pygame.draw.rect(screen, color, RECT8, 0, 15)
    text = font.render(str(balance), True, (0, 0, 0))
    text_rect = text.get_rect(center=RECT8.center)
    screen.blit(text, text_rect)
def draw_buttons():
    button_color = (100, 100, 100)
    button_hover_color = (150, 150, 150)
    button_width = 150
    button_height = 80
    margin_x = (796 - 2 * button_width) // 3
    margin_y = (440 - 3 * button_height) // 4
    start_x = 132
    start_y = 80
    buttons = []
    for row in range(2):
        for col in range(2):
            x = start_x + margin_x + col * (button_width + margin_x)
            y = start_y + margin_y + row * (button_height + margin_y)
            rect = pygame.Rect(x, y, button_width, button_height)
            buttons.append(rect)
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, button_hover_color, rect, 0, 5)
            else:
                pygame.draw.rect(screen, button_color, rect)
            text = font.render(f"Игpa {row*2 + col + 1}", True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
    rect5 = pygame.Rect((WIDTH - button_width) // 2, start_y + 3 * margin_y + 2 * button_height, button_width, button_height)
    buttons.append(rect5)
    if rect5.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, rect5, 0, 5)
    else:
        pygame.draw.rect(screen, button_color, rect5, 0, 0)
    text5 = font.render("Игpa 5", True, (255, 255, 255))
    screen.blit(text5, text5.get_rect(center=rect5.center))
    return buttons
def snap_column_to_center(index):
    center_y = HEIGHT // 2
    closest_distance = float('inf')
    closest_j = 0
    for j in range(NUM_ELEMENTS):
        y_pos = (offsets[index] + j * STEP) % (NUM_ELEMENTS * STEP) - STEP
        if 0 <= y_pos < HEIGHT:
            distance = abs(y_pos - center_y)
            if distance < closest_distance:
                closest_distance = distance
                closest_j = j
    target_y = HEIGHT // 2
    current_y = (offsets[index] + closest_j * STEP) % (NUM_ELEMENTS * STEP) - STEP
    correction = current_y - target_y
    offsets[index] = (offsets[index] - correction) % (NUM_ELEMENTS * STEP)
    return closest_j
def draw_game_one(COLUMN_SPEED):
    for i in range(3):
        offsets[i] += COLUMN_SPEED
        offsets[i] %= NUM_ELEMENTS * STEP
        for j in range(NUM_ELEMENTS):
            y_pos = (offsets[i] + j * STEP) % (NUM_ELEMENTS * STEP) - STEP
            x_pos = i * 212 + 310
            if 0 <= y_pos < HEIGHT:
                number = str(j)
                text = font.render(number, True, (255, 255, 255))
                text_width, text_height = text.get_size()
                square_size = max(text_width, text_height) + 2 * SQUARE_PADDING
                square_x = x_pos - (square_size - text_width) // 2
                square_y = y_pos - (square_size - text_height) // 2
                pygame.draw.rect(screen, SQUARE_COLOR, (square_x, square_y, square_size, square_size), 0, 4)
                screen.blit(text, (x_pos, y_pos))
def generate_mines():
    global mines
    mines = set()
    while len(mines) < NUM_MINES:
        i = random.randint(0, GRID_ROWS - 1)
        j = random.randint(0, GRID_COLS - 1)
        mines.add((i, j))
def reset_game_two():
    global revealed, game2_active, game2_lost
    revealed = set()
    generate_mines()
    game2_active = True
    game2_lost = False
def draw_game_two():
    font = pygame.font.SysFont(None, 52)
    grid_pixel_width = GRID_COLS * CELL_SIZE + (GRID_COLS - 1) * CELL_SPACING
    grid_pixel_height = GRID_ROWS * CELL_SIZE + (GRID_ROWS - 1) * CELL_SPACING
    start_x = WIDTH // 2 - grid_pixel_width // 2
    start_y = HEIGHT // 2 - grid_pixel_height // 2
    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            x = start_x + j * (CELL_SIZE + CELL_SPACING)
            y = start_y + i * (CELL_SIZE + CELL_SPACING)
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if (i, j) in revealed:
                color = (200, 0, 0) if (i, j) in mines else (0, 200, 0)
            else:
                color = (100, 100, 100)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10)
    if not game2_active:
        if start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, start_button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, button_color, start_button_rect, border_radius=10)
        button_text = font.render("START", True, (255, 255, 255))
        screen.blit(button_text, button_text.get_rect(center=start_button_rect.center))
    if game2_active and not game2_lost:
        cashout_button_rect = start_button_rect
        if cashout_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (255, 255, 100), cashout_button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, (200, 200, 0), cashout_button_rect, border_radius=10)
        text = font.render("ЗАБРАТЬ", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=cashout_button_rect.center))
        rect9 = pygame.Rect(217, 85, 234, 41)
        pygame.draw.rect(screen, BALL_COLOR, rect9, 0, 15)
        print(len(revealed))
        text = font.render(f'+{str((round(1.2 ** len(revealed) - 1, 2)))}', True, (0, 0, 0))
        text_rect = text.get_rect(center=rect9.center)
        screen.blit(text, text_rect)
def death_coef():
    if random.randint(1, 100) <= CRASH_ZERO_CHANCE:
        return 1.00
    r = random.randint(0, CRASH_LIMIT) / CRASH_DIVIDER
    val = 1.0 / (1.0 - (r ** CRASH_POWER))
    return round(max(1.01, val), 2)
def draw_game_three():
    global coef3, chance_of_explosion, game3_active, game3_exploded
    font_big = pygame.font.SysFont(None, 60)
    intensity = min(255, int(coef3 * 20))
    circle_color = (intensity, intensity, intensity)
    if game3_exploded:
        circle_color = (200, 0, 0)
    elif not game3_active:
        circle_color = (0, 0, 0)
    radius = min(int(initial_radius * coef3), max_radius)
    pygame.draw.circle(screen, circle_color, (WIDTH//2, HEIGHT//2), radius)
    if not game3_active:
        coef3 = 1.0
        if start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, start_button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, button_color, start_button_rect, border_radius=10)
        start_text = font_big.render("START", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))
    elif game3_active and not game3_exploded:
        if cashout_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (255, 255, 100), cashout_button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, (200, 200, 0), cashout_button_rect, border_radius=10)
        cash_text = font_big.render("ЗАБРАТЬ", True, (0, 0, 0))
        screen.blit(cash_text, cash_text.get_rect(center=cashout_button_rect.center))

    coef_text = font_big.render(f"{round(coef3, 2)}x", True, (255, 255, 255))
    screen.blit(coef_text, coef_text.get_rect(center=(WIDTH//2, 120)))
    if game3_active and not game3_exploded:
        coef3 *= 1.001
        if coef3 >= dead_coef:
            game3_exploded = True
            print(f"Вы проиграли! Коэффициент: {round(coef3, 2)}")
            print(f"Ваш баланс {round(balance, 2)} монет")
def get_chance_and_coef(mouse_y):
    relative_y = rect_y + rect_height - mouse_y
    chance = min(max(relative_y / 3, 1), 99)
    coef = round(100 / chance, 2)
    return round(chance, 2), coef
def reset_game():
    global selected_y, animating, anim_height, win, anim_coef
    selected_y = None
    animating = False
    anim_height = 0
    win = False
    anim_coef = None
def draw_game_four():
    global anim_rect_y, anim_height, button_rect
    font_big = pygame.font.SysFont(None, 60)
    pygame.draw.rect(screen, (80, 80, 80), (rect_x, rect_y, rect_width, rect_height))
    if selected_y and not animating:
        pygame.draw.rect(screen, YELLOW, (rect_x, selected_y, rect_width, rect_y + rect_height - selected_y))
    if animating:
        if win:
            if anim_rect_y > rect_y:
                anim_rect_y -= 1
                anim_height += 1
            else:
                reset_game()
            pygame.draw.rect(screen, GREEN, (rect_x, anim_rect_y, rect_width, anim_height))
        else:
            if anim_height > 0:
                anim_rect_y += 1
                anim_height -= 1
                pygame.draw.rect(screen, RED, (rect_x, anim_rect_y, rect_width, anim_height))
            else:
                reset_game()
    if (selected_y and not animating) or (animating and anim_coef != None):
        if animating:
            if win:
                label = font.render(f"{anim_coef}x", True, WHITE)
            else:
                label = font.render("0x", True, WHITE)
        else:
            chance, coef = get_chance_and_coef(selected_y)
            label = font.render(f"{coef}x  {chance}%", True, WHITE)
        screen.blit(label, (rect_x + (rect_width - label.get_width()) // 2, rect_y - 30))
    if not animating:
        color = HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        button_text = font_big.render("START", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
def draw_game_five():
    global highlighted_slot, highlight_time, ball, ball_y, ball_x, ball_vx, ball_vy, balance
    for peg_x, peg_y in pegs:
        pygame.draw.circle(screen, PEG_COLOR, (peg_x, peg_y), peg_radius)
    current_time = pygame.time.get_ticks()
    for i, slot in enumerate(slots):
        if highlighted_slot == i and current_time - highlight_time < 1000:
            color = (255, 255, 255)
        else:
            color = SLOT_COLORS[i % len(SLOT_COLORS)]
        pygame.draw.rect(screen, color, slot)
        coeff_text = font5.render(f"{slot_coefficients[i]}x", True, (0, 0, 0))
        text_rect = coeff_text.get_rect(center=(slot[0] + slot[2] // 2, slot[1] + 20))
        screen.blit(coeff_text, text_rect)
    if ball:
        ball_y += ball_vy
        ball_x += ball_vx
        for peg_x, peg_y in pegs:
            dx = ball_x - peg_x
            dy = ball_y - peg_y
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= peg_radius + ball_radius:
                angle = math.atan2(dy, dx)
                ball_vx += math.cos(angle)
                ball_vx = max(-5, min(5, ball_vx))
        if ball_x < GAME_LEFT + ball_radius:
            ball_x = GAME_LEFT + ball_radius
            ball_vx *= -1
        elif ball_x > GAME_RIGHT - ball_radius:
            ball_x = GAME_RIGHT - ball_radius
            ball_vx *= -1
        pygame.draw.circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)), ball_radius)
        if ball_y > GAME_BOTTOM - 50:
            for i, slot in enumerate(slots):
                if slot[0] <= ball_x < slot[0] + slot[2]:
                    highlighted_slot = i
                    highlight_time = pygame.time.get_ticks()
                    print(f"Шар попал в слот {i + 1} — коэффициент: x{slot_coefficients[i]}")
                    if slot_coefficients[i] > 1:
                        print(f"Победа! Ваш выигрыш составил {slot_coefficients[i] - 1} монет")
                    elif slot_coefficients[i] == 1:
                        print(f"Нейтральный коэффицент")
                    elif slot_coefficients[i] < 1:
                        print(f"Частичное поражение. Ваш выигрыш составил {slot_coefficients[i] - 1} монет")
                    balance += slot_coefficients[i]
                    print(f"Ваш баланс {round(balance, 2)} монет")
            ball = None
    screen.set_clip(None)
    if not ball:
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, hover_color if start_button_rect.collidepoint(mouse_pos) else button_color, start_button_rect, border_radius=10)
        button_text = font5.render("START", True, (255, 255, 255))
        screen.blit(button_text, button_text.get_rect(center=start_button_rect.center))
keys = pygame.key.get_pressed()
mouse_pos = (0, 0)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_mode == 0:
                buttons = draw_buttons()
                for idx, rect in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        game_mode = idx + 1
            elif game_mode == 1:
                if not game:
                    if start_button_rect.collidepoint(event.pos) and balance >= 1:
                        balance -= 1
                        game = True
                        backward_timer = BACKWARD_DURATION
            elif game_mode == 2:
                if not game2_active:
                    if start_button_rect.collidepoint(event.pos) and balance >= 1:
                        balance -= 1
                        reset_game_two()
                elif game2_active and not game2_lost:
                    if cashout_button_rect.collidepoint(event.pos):
                        print(f"Забрано! Открыто клеток: {len(revealed)}, ваш выигрыш составил {round((1.2**len(revealed))-1, 2)} монет")
                        balance += round((1.2**len(revealed)), 2)
                        print(f"Ваш баланс {round(balance, 2)} монет")
                        game2_active = False
                        revealed.clear()
                    else:
                        grid_pixel_width = GRID_COLS * CELL_SIZE + (GRID_COLS - 1) * CELL_SPACING
                        grid_pixel_height = GRID_ROWS * CELL_SIZE + (GRID_ROWS - 1) * CELL_SPACING
                        start_x = WIDTH // 2 - grid_pixel_width // 2
                        start_y = HEIGHT // 2 - grid_pixel_height // 2
                        for i in range(GRID_ROWS):
                            for j in range(GRID_COLS):
                                x = start_x + j * (CELL_SIZE + CELL_SPACING)
                                y = start_y + i * (CELL_SIZE + CELL_SPACING)
                                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                                if rect.collidepoint(event.pos) and (i, j) not in revealed:
                                    revealed.add((i, j))
                                    if (i, j) in mines:
                                        game2_lost = True
                                        print(f"Вы проиграли! Ваш баланс {round(balance, 2)} монет")
                                    else:
                                        print(
                                            f"Открыто клеток: {len(revealed)}, можете забрать {round((1.2 ** len(revealed)), 2)} монет или играть дальше.")
            elif game_mode == 3:
                if not game3_active:
                    if start_button_rect.collidepoint(event.pos) and balance >= 1:
                        balance -= 1
                        game3_active = True
                        game3_exploded = False
                        coef3 = 1.0
                        dead_coef = death_coef()
                elif game3_active and not game3_exploded:
                    if cashout_button_rect.collidepoint(event.pos):
                        print(f"Забрано! Коэффициент: {round(coef3, 2)}, ваш выигрыш составил {round(coef3 - 1, 2)} монет")
                        balance += round(coef3, 2)
                        print(f"Ваш баланс {round(balance, 2)} монет")
                        game3_active = False
                        game3_exploded = False
                        coef = 1.0
                        dead_coef = death_coef()
            elif game_mode == 4:
                if not animating and event.type == pygame.MOUSEBUTTONDOWN:
                    if rect_x <= mouse_pos[0] <= rect_x + rect_width and rect_y <= mouse_pos[1] <= rect_y + rect_height:
                        selected_y = mouse_pos[1]
                    elif button_rect.collidepoint(mouse_pos) and balance >= 1:
                        if selected_y is None:
                            print("Выберите коэффициент перед началом!")
                        else:
                            balance -= 1
                            chance, coef = get_chance_and_coef(selected_y)
                            roll = random.randint(0, 100)
                            win = roll < chance
                            if win:
                                print(f"Победа! Коэф: {round(coef, 2)}x, ваш выигрыш составил {round(coef-1, 2)} монет")
                                balance += round(coef, 2)
                            else:
                                print(f"Поражение!")
                            print(f"Ваш баланс {round(balance, 2)} монет")
                            animating = True
                            anim_height = rect_y + rect_height - selected_y
                            anim_rect_y = selected_y
                            anim_coef = coef
            elif game_mode == 5:
                if event.type == pygame.MOUSEBUTTONDOWN and not ball and start_button_rect.collidepoint(event.pos) and balance >= 1:
                    balance -= 1
                    ball = True
                    ball_x = random.randint(GAME_LEFT + ball_radius, GAME_RIGHT - ball_radius)
                    ball_y = GAME_TOP + 10
                    ball_vx = random.uniform(-2, 2)
                    ball_vy = 2
            if start_button_rect.collidepoint(event.pos) and balance < 1 and game_mode:
                print(f"Игра невозможна! Баланс меньше 1 монеты - {round(balance, 2)}")
            if game_mode != 0:
                mouse_pos = pygame.mouse.get_pos()
                distance = ((mouse_pos[0] - circle_pos[0]) ** 2 + (mouse_pos[1] - circle_pos[1]) ** 2) ** 0.5
                if distance <= circle_radius:
                    game_mode = 0
    screen.fill(SCREEN_FILL_COLOR)
    if game_mode == 0:
        draw_buttons()
    elif game_mode == 1:
        font = pygame.font.SysFont(None, 52)
        if not gamee:
            COLUMN_SPEED = 0
        else:
            COLUMN_SPEED = 2
        if not game:
            draw_game_one(COLUMN_SPEED)
            start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 145, 200, 60)
            if start_button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, start_button_rect, border_radius=10)
            else:
                pygame.draw.rect(screen, button_color, start_button_rect, border_radius=10)
            button_text = font.render("START", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=start_button_rect.center)
            screen.blit(button_text, text_rect)
        if game:
            if backward_timer > 60:
                COLUMN_SPEED = -5
                draw_game_one(COLUMN_SPEED)
                backward_timer -= 1
            elif backward_timer > 0:
                COLUMN_SPEED = 40
                draw_game_one(COLUMN_SPEED)
                backward_timer -= 1
            else:
                if not SLOWDOWN_STAGE:
                    COLUMN_SPEEDS = [30.0, 30.0, 30.0]
                    DECEL_FACTORS = [random.uniform(0.9, 0.99), random.uniform(0.9, 0.99), random.uniform(0.9, 0.99)]
                    SLOWDOWN_STAGE = True
                all_stopped = True
                for i in range(3):
                    if COLUMN_SPEEDS[i] > 0:
                        COLUMN_SPEEDS[i] *= DECEL_FACTORS[i]
                        if COLUMN_SPEEDS[i] < 0.1:
                            COLUMN_SPEEDS[i] = 0
                        else:
                            all_stopped = False
                    offsets[i] += COLUMN_SPEEDS[i]
                    offsets[i] %= NUM_ELEMENTS * STEP
                    for j in range(NUM_ELEMENTS):
                        y_pos = (offsets[i] + j * STEP) % (NUM_ELEMENTS * STEP) - STEP
                        x_pos = i * 212 + 310
                        if 0 <= y_pos < HEIGHT:
                            number = str(j)
                            text = font.render(number, True, (255, 255, 255))
                            text_width, text_height = text.get_size()
                            square_size = max(text_width, text_height) + 2 * SQUARE_PADDING
                            square_x = x_pos - (square_size - text_width) // 2
                            square_y = y_pos - (square_size - text_height) // 2
                            pygame.draw.rect(screen, SQUARE_COLOR, (square_x, square_y, square_size, square_size), 0, 4)
                            screen.blit(text, (x_pos, y_pos))
                if all_stopped:
                    result = []
                    for i in range(3):
                        digit = snap_column_to_center(i)
                        result.append(digit)
                    print("Выпали числа:", result)
                    if result[0] == result[1] == result[2]:
                        print("Победа! Вы выиграли 25 монет")
                        balance += 26
                    print(f"Ваш баланс {round(balance, 2)} монет")
                    game = False
                    SLOWDOWN_STAGE = False
                    COLUMN_SPEEDS = [0, 0, 0]
                    DECEL_FACTORS = [0, 0, 0]
                    gamee = False
    elif game_mode == 2:
        draw_game_two()
        if game2_lost and game2_reset_timer == 0:
            game2_reset_timer = pygame.time.get_ticks() + 1000
        if pygame.time.get_ticks() >= game2_reset_timer > 0:
            game2_active = False
            game2_lost = False
            revealed.clear()
            game2_reset_timer = 0
    elif game_mode == 3:
        draw_game_three()
        if game3_exploded:
            if pygame.time.get_ticks() % 2000 < 50:
                game3_active = False
                game3_exploded = False
                coef3 = 1.0
                chance_of_explosion = 0.04
    elif game_mode == 4:
        draw_game_four()
    elif game_mode == 5:
        draw_game_five()
    balance = round(balance, 2)
    draw_background()
    if game_mode != 0:
        points = [(70, 35), (50, 55), (70, 75), (60, 85), (30, 55), (60, 25)]
        pygame.draw.circle(screen, (100, 100, 100), (55, 55), 50)
        pygame.draw.polygon(screen, (255, 255, 255), points)
    pygame.display.flip()
    clock.tick(FPS)
    if keys[pygame.K_ESCAPE]:
        game_mode = 0