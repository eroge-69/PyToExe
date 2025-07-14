import pygame
import random

WIDTH, HEIGHT = 630, 630
ROWS, COLS = 9, 9
CELL_SIZE = WIDTH // COLS
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
RED = (255, 0, 0)
DARK_BLUE = (0, 0, 139)
GREEN = (0, 200, 0)
LIGHT_GRAY = (220, 220, 220)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Судоку-киллер")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 60)


def generate_full_sudoku():
    def is_valid(num, row, col, board):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        sr, sc = 3 * (row // 3), 3 * (col // 3)
        for r in range(sr, sr + 3):
            for c in range(sc, sc + 3):
                if board[r][c] == num:
                    return False
        return True

    def solve(board):
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(num, r, c, board):
                            board[r][c] = num
                            if solve(board):
                                return True
                            board[r][c] = 0
                    return False
        return True

    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    return board


def generate_random_cages(grid):
    all_cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(all_cells)
    visited = set()
    cages = []

    while all_cells:
        cell = all_cells.pop()
        if cell in visited:
            continue
        cage_size = random.choice([2, 3])
        cage = [cell]
        visited.add(cell)

        r, c = cell
        neighbors = [(r + dr, c + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                     if 0 <= r + dr < 9 and 0 <= c + dc < 9 and (r + dr, c + dc) not in visited]

        random.shuffle(neighbors)
        for n in neighbors:
            if len(cage) >= cage_size:
                break
            cage.append(n)
            visited.add(n)

        if len(cage) >= 2:
            total = sum(grid[r][c] for r, c in cage)
            cages.append((total, cage))
    return cages


def draw_grid():
    for i in range(ROWS + 1):
        width = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), width)
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), width)


def draw_dotted_line(x1, y1, x2, y2, color, length=5, gap=3):
    dx, dy = x2 - x1, y2 - y1
    dist = max(abs(dx), abs(dy))
    for i in range(0, dist, length + gap):
        start_x = x1 + dx * i // dist
        start_y = y1 + dy * i // dist
        end_x = x1 + dx * min(i + length, dist) // dist
        end_y = y1 + dy * min(i + length, dist) // dist
        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 1)


def draw_cages(cages):
    for total, cells in cages:
        r, c = cells[0]
        text = font.render(str(total), True, RED)
        screen.blit(text, (c * CELL_SIZE + 3, r * CELL_SIZE + 3))

        for i in range(len(cells)):
            for j in range(i + 1, len(cells)):
                r1, c1 = cells[i]
                r2, c2 = cells[j]
                if abs(r1 - r2) + abs(c1 - c2) == 1:
                    x1 = c1 * CELL_SIZE + CELL_SIZE // 2
                    y1 = r1 * CELL_SIZE + CELL_SIZE // 2
                    x2 = c2 * CELL_SIZE + CELL_SIZE // 2
                    y2 = r2 * CELL_SIZE + CELL_SIZE // 2
                    draw_dotted_line(x1, y1, x2, y2, GRAY)


def draw_numbers(user_grid, fixed_cells, cell_feedback):
    for r in range(ROWS):
        for c in range(COLS):
            num = user_grid[r][c]
            if num != 0:
                if (r, c) in fixed_cells:
                    color = BLACK
                else:
                    status = cell_feedback.get((r, c))
                    color = RED if status == "incorrect" else DARK_BLUE
                text = big_font.render(str(num), True, color)
                rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, rect)


def draw_success_message():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(WHITE)
    screen.blit(overlay, (0, 0))

    text = title_font.render("Победа!", True, GREEN)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(text, rect)

    restart_text = big_font.render("Нажмите ENTER для новой игры", True, BLACK)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(restart_text, restart_rect)


def is_grid_full(grid):
    return all(all(cell != 0 for cell in row) for row in grid)


def check_cage_sums(cages, user_grid):
    for total, cells in cages:
        values = [user_grid[r][c] for r, c in cells]
        if 0 in values or sum(values) != total or len(set(values)) != len(values):
            return False
    return True


def check_full_grid_validity(user_grid):
    for i in range(9):
        row = user_grid[i]
        col = [user_grid[r][i] for r in range(9)]
        if len(set(row)) != 9 or len(set(col)) != 9:
            return False
    for br in range(3):
        for bc in range(3):
            block = [user_grid[3*br + r][3*bc + c] for r in range(3) for c in range(3)]
            if len(set(block)) != 9:
                return False
    return True


def main():
    running = True
    game_won = False
    selected_cell = None
    input_mode = True
    input_text = ""
    user_grid = [[0 for _ in range(9)] for _ in range(9)]
    fixed_cells = set()
    cell_feedback = {}
    grid = generate_full_sudoku()
    cages = generate_random_cages(grid)

    while running:
        screen.fill(WHITE)

        if input_mode:
            title = title_font.render("Судоку-киллер", True, DARK_BLUE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4 - 30))
            screen.blit(title, title_rect)
            prompt = big_font.render("Введите количество заполненных ячеек (1-80):", True, BLACK)
            screen.blit(prompt, (20, HEIGHT // 2 - 60))
            input_render = title_font.render(input_text, True, DARK_BLUE)
            screen.blit(input_render, (WIDTH // 2 - 40, HEIGHT // 2))

        else:
            draw_grid()
            draw_cages(cages)
            draw_numbers(user_grid, fixed_cells, cell_feedback)

            if selected_cell:
                r, c = selected_cell
                pygame.draw.rect(screen, (200, 200, 255), (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

            if not game_won:
                if is_grid_full(user_grid) and check_cage_sums(cages, user_grid) and check_full_grid_validity(user_grid):
                    game_won = True

            if game_won:
                draw_success_message()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if input_mode:
                    if event.key == pygame.K_RETURN:
                        if input_text.isdigit():
                            count = max(1, min(80, int(input_text)))
                            fixed_cells = set(random.sample([(r, c) for r in range(9) for c in range(9)], count))
                            for r, c in fixed_cells:
                                user_grid[r][c] = grid[r][c]
                            input_mode = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode
                elif game_won and event.key == pygame.K_RETURN:
                    return main()
                elif selected_cell and not game_won:
                    r, c = selected_cell
                    if (r, c) not in fixed_cells:
                        if pygame.K_0 <= event.key <= pygame.K_9:
                            num = event.key - pygame.K_0
                            user_grid[r][c] = num
                            if num == 0:
                                cell_feedback[(r, c)] = None
                            elif num == grid[r][c]:
                                cell_feedback[(r, c)] = "correct"
                            else:
                                cell_feedback[(r, c)] = "incorrect"
                            if is_grid_full(user_grid) and check_cage_sums(cages,
                                                                           user_grid) and check_full_grid_validity(
                                    user_grid):
                                game_won = True

            elif event.type == pygame.MOUSEBUTTONDOWN and not input_mode and not game_won:
                x, y = pygame.mouse.get_pos()
                if y < WIDTH:
                    selected_cell = (y // CELL_SIZE, x // CELL_SIZE)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
