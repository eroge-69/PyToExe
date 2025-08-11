import pygame
import random
import sys

# -----------------------------
# Настройки игры
# -----------------------------
GRID_W, GRID_H = 10, 20
BLOCK = 30
PLAY_W, PLAY_H = GRID_W * BLOCK, GRID_H * BLOCK
SIDE_W = 220

WIN_W = PLAY_W + SIDE_W + 40  # + поля
WIN_H = PLAY_H + 40

TOP_LEFT_X = 20
TOP_LEFT_Y = 20

TITLE = "Tetris"

# Цвета
BLACK = (0, 0, 0)
GRAY = (30, 30, 30)
LIGHT_GRAY = (80, 80, 80)
WHITE = (230, 230, 230)

# Цвета для фигур
SHAPE_COLORS = [
    (48, 201, 74),   # S
    (233, 68, 55),   # Z
    (51, 181, 229),  # I
    (240, 194, 57),  # O
    (63, 81, 181),   # J
    (255, 152, 0),   # L
    (156, 39, 176),  # T
]

# Определения фигур (каждая ротация — 4x5 сетка символьных строк)
S = [
    [
        ".....",
        ".....",
        "..00.",
        ".00..",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..00.",
        "...0.",
        ".....",
    ],
]

Z = [
    [
        ".....",
        ".....",
        ".00..",
        "..00.",
        ".....",
    ],
    [
        ".....",
        "..0..",
        ".00..",
        ".0...",
        ".....",
    ],
]

I = [
    [
        "..0..",
        "..0..",
        "..0..",
        "..0..",
        ".....",
    ],
    [
        ".....",
        "0000.",
        ".....",
        ".....",
        ".....",
    ],
]

O = [
    [
        ".....",
        ".....",
        ".00..",
        ".00..",
        ".....",
    ],
]

J = [
    [
        ".....",
        ".0...",
        ".000.",
        ".....",
        ".....",
    ],
    [
        ".....",
        "..00.",
        "..0..",
        "..0..",
        ".....",
    ],
    [
        ".....",
        ".....",
        ".000.",
        "...0.",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..0..",
        ".00..",
        ".....",
    ],
]

L = [
    [
        ".....",
        "...0.",
        ".000.",
        ".....",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..0..",
        "..00.",
        ".....",
    ],
    [
        ".....",
        ".....",
        ".000.",
        ".0...",
        ".....",
    ],
    [
        ".....",
        ".00..",
        "..0..",
        "..0..",
        ".....",
    ],
]

T = [
    [
        ".....",
        "..0..",
        ".000.",
        ".....",
        ".....",
    ],
    [
        ".....",
        "..0..",
        "..00.",
        "..0..",
        ".....",
    ],
    [
        ".....",
        ".....",
        ".000.",
        "..0..",
        ".....",
    ],
    [
        ".....",
        "..0..",
        ".00..",
        "..0..",
        ".....",
    ],
]

SHAPES = [S, Z, I, O, J, L, T]


class Piece:
    def __init__(self, x, y, shape, color):
        self.x = x  # в клетках
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0  # индекс ротации

    @property
    def pattern(self):
        return self.shape[self.rotation % len(self.shape)]


def create_grid(locked):
    grid = [[BLACK for _ in range(GRID_W)] for _ in range(GRID_H)]
    for (x, y), color in locked.items():
        if 0 <= y < GRID_H and 0 <= x < GRID_W:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    pattern = piece.pattern
    for i, line in enumerate(pattern):
        for j, char in enumerate(line):
            if char == "0":
                # смещение: сетка 5x5, центрируем относительно фигуры
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    accepted = {(x, y) for y in range(GRID_H) for x in range(GRID_W) if grid[y][x] == BLACK}
    for (x, y) in convert_shape_format(piece):
        if y < 0:
            continue
        if (x, y) not in accepted:
            return False
    return True


def check_lost(locked):
    # проигрыш — если какая-либо заблокированная клетка выше поля
    for (_, y) in locked.keys():
        if y < 1:
            return True
    return False


def get_shape(bag):
    # 7-bag: используем мешок фигур для равномерности
    if not bag:
        indices = list(range(len(SHAPES)))
        random.shuffle(indices)
        for idx in indices:
            bag.append(idx)
    idx = bag.pop()
    shape = SHAPES[idx]
    color = SHAPE_COLORS[idx]
    return Piece(GRID_W // 2, 0, shape, color)


def draw_grid_lines(surf):
    # сетка
    for i in range(GRID_H + 1):
        y = TOP_LEFT_Y + i * BLOCK
        pygame.draw.line(surf, GRAY, (TOP_LEFT_X, y), (TOP_LEFT_X + PLAY_W, y), 1)
    for j in range(GRID_W + 1):
        x = TOP_LEFT_X + j * BLOCK
        pygame.draw.line(surf, GRAY, (x, TOP_LEFT_Y), (x, TOP_LEFT_Y + PLAY_H), 1)


def draw_window(surf, grid, score, level, lines, next_piece):
    surf.fill((12, 12, 16))
    # рамка поля
    pygame.draw.rect(surf, LIGHT_GRAY, (TOP_LEFT_X - 2, TOP_LEFT_Y - 2, PLAY_W + 4, PLAY_H + 4), 2)

    # клетки
    for y in range(GRID_H):
        for x in range(GRID_W):
            color = grid[y][x]
            rect = pygame.Rect(TOP_LEFT_X + x * BLOCK, TOP_LEFT_Y + y * BLOCK, BLOCK, BLOCK)
            if color != BLACK:
                pygame.draw.rect(surf, color, rect)
                pygame.draw.rect(surf, (20, 20, 20), rect, 1)

    draw_grid_lines(surf)

    # боковая панель
    panel_x = TOP_LEFT_X + PLAY_W + 20
    title = FONT_BIG.render(TITLE, True, WHITE)
    surf.blit(title, (panel_x, TOP_LEFT_Y))

    # Счёт/уровень/линии
    y_info = TOP_LEFT_Y + 70
    info_lines = [
        ("Score", str(score)),
        ("Level", str(level)),
        ("Lines", str(lines)),
    ]
    for label, val in info_lines:
        text = FONT_MED.render(f"{label}: {val}", True, WHITE)
        surf.blit(text, (panel_x, y_info))
        y_info += 30

    # Предпросмотр
    preview_lbl = FONT_MED.render("Next:", True, WHITE)
    surf.blit(preview_lbl, (panel_x, y_info + 10))
    draw_next_shape(surf, next_piece, panel_x, y_info + 40)

    # Низ: подсказки
    hints = [
        "Arrows: move/rotate",
        "Space: hard drop",
        "P: pause",
        "Esc: quit",
    ]
    yh = WIN_H - 120
    for h in hints:
        surf.blit(FONT_SMALL.render(h, True, (190, 190, 190)), (panel_x, yh))
        yh += 22


def draw_next_shape(surf, piece, ox, oy):
    # рисуем в мини-сетке
    pattern = piece.shape[0]  # показываем первую ориентацию
    for i, line in enumerate(pattern):
        for j, ch in enumerate(line):
            if ch == "0":
                rect = pygame.Rect(ox + j * (BLOCK // 1.2), oy + i * (BLOCK // 1.2), BLOCK // 1.2, BLOCK // 1.2)
                pygame.draw.rect(surf, piece.color, rect)
                pygame.draw.rect(surf, (30, 30, 30), rect, 1)


def clear_rows(grid, locked):
    removed = 0
    for y in range(GRID_H - 1, -1, -1):
        if BLACK not in grid[y]:
            removed += 1
            # удаляем все клетки этой строки из locked
            for x in range(GRID_W):
                try:
                    del locked[(x, y)]
                except KeyError:
                    pass
    if removed > 0:
        # смещаем вниз всё, что выше
        # сортировка по y (вниз)
        for y in sorted({py for (_, py) in locked.keys()}, reverse=True):
            for x in range(GRID_W):
                if (x, y) in locked:
                    color = locked[(x, y)]
                    # сколько строчек под y удалено?
                    shift = sum(1 for ry in range(y + 1, GRID_H) if all(grid[ry][cx] != BLACK for cx in range(GRID_W)))
                    # Это неверно: после зачистки grid уже неактуален. Сделаем проще:
        # Правильный перенос: пройти по копии и сдвинуть вниз на количество удалённых строк ниже
        rows_removed_set = set()
        # восстановим по новой проверке какие строки были полными
        # (так как grid уже не соответствует locked, пересчитаем по индексу)
        full_rows = []
        # Мы уже знаем количество removed, но для сдвига нужен список индексов
        # Пересоберём временную сетку из locked до удаления (поэтому пересчитаем заново):
        # Упростим: вычислим "сколько полных строк ниже каждой y" через скан вниз.
        # Для этого нам нужны индексы полных строк до удаления. Считаем их сначала.
    return removed


def clear_rows_safe(locked):
    # Пересчёт удаления строк, корректный и независимый от grid
    removed = 0
    rows = {}
    for (x, y) in locked:
        rows.setdefault(y, 0)
        rows[y] += 1
    full_rows = sorted([y for y, count in rows.items() if count == GRID_W])
    if not full_rows:
        return 0

    removed = len(full_rows)
    # Удаляем полные строки
    for y in full_rows:
        for x in range(GRID_W):
            locked.pop((x, y), None)

    # Сдвигаем всё, что выше, вниз на количество полных строк ниже
    # Для каждого блока вычисляем, сколько полных строк строго ниже его y
    new_locked = {}
    full_rows_set = set(full_rows)
    for (x, y), color in locked.items():
        # считаем, сколько y' из full_rows меньше y
        shift = sum(1 for fy in full_rows if fy > y)
        new_locked[(x, y + shift)] = color

    locked.clear()
    locked.update(new_locked)
    return removed


def score_for_lines(n, level):
    # Классика Tetris Guideline (упрощённый множитель)
    table = {1: 100, 2: 300, 3: 500, 4: 800}
    base = table.get(n, 0)
    return base * max(1, level)


def draw_text_center(surf, text, size=48, color=WHITE, dy=0):
    font = pygame.font.SysFont("consolas", size, bold=True)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(TOP_LEFT_X + PLAY_W // 2, TOP_LEFT_Y + PLAY_H // 2 + dy))
    surf.blit(label, rect.topleft)


def hard_drop(piece, grid):
    # опустить максимально вниз
    while True:
        piece.y += 1
        if not valid_space(piece, grid):
            piece.y -= 1
            break


def pause_loop(surf):
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    paused = False
        draw_text_center(surf, "PAUSED", 56, (180, 220, 255), dy=-20)
        draw_text_center(surf, "Press P to resume", 28, (200, 200, 200), dy=30)
        pygame.display.flip()


def game_loop(screen):
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    bag = []
    current_piece = get_shape(bag)
    next_piece = get_shape(bag)

    fall_time = 0
    fall_interval = 0.6  # сек на шаг падения
    level = 1
    score = 0
    lines_cleared = 0

    running = True
    game_over = False

    while running:
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        grid = create_grid(locked_positions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if game_over:
                    if event.key == pygame.K_r:
                        # рестарт
                        return "restart"
                    continue

                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    prev = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    # wall kick простейший
                    kicked = False
                    for dx in [0, -1, 1, -2, 2]:
                        current_piece.x += dx
                        if valid_space(current_piece, grid):
                            kicked = True
                            break
                        current_piece.x -= dx
                    if not kicked:
                        current_piece.rotation = prev
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid)
                elif event.key == pygame.K_p:
                    pause_loop(screen)

        if game_over:
            draw_window(screen, grid, score, level, lines_cleared, next_piece)
            draw_text_center(screen, "GAME OVER", 56, (255, 120, 120), dy=-20)
            draw_text_center(screen, "Press R to restart or ESC to quit", 24, (220, 220, 220), dy=30)
            pygame.display.flip()
            continue

        # Падение
        if fall_time >= fall_interval:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                # блокируем фигуру
                for (x, y) in convert_shape_format(current_piece):
                    if y < 0:
                        game_over = True
                        break
                    locked_positions[(x, y)] = current_piece.color

                # очистка линий
                removed = clear_rows_safe(locked_positions)
                if removed > 0:
                    lines_cleared += removed
                    score += score_for_lines(removed, level)
                    # ап левел по прогрессии
                    new_level = 1 + lines_cleared // 10
                    if new_level != level:
                        level = new_level
                        # ускоряем падение (нижняя граница)
                        fall_interval = max(0.08, 0.6 - 0.05 * (level - 1))

                # следующая фигура
                current_piece = next_piece
                next_piece = get_shape(bag)

                if check_lost(locked_positions):
                    game_over = True

        # Рисуем текущую фигуру на grid (временно)
        for (x, y) in convert_shape_format(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.color

        draw_window(screen, grid, score, level, lines_cleared, next_piece)
        pygame.display.flip()

    return "quit"


def main():
    pygame.init()
    pygame.font.init()
    global FONT_BIG, FONT_MED, FONT_SMALL
    FONT_BIG = pygame.font.SysFont("consolas", 36, bold=True)
    FONT_MED = pygame.font.SysFont("consolas", 22)
    FONT_SMALL = pygame.font.SysFont("consolas", 18)

    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption(TITLE)

    # Основной цикл с возможностью рестарта
    while True:
        result = game_loop(screen)
        if result == "restart":
            continue
        break

    pygame.quit()


if __name__ == "__main__":
    main()
