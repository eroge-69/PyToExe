import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 500, 500
CELL_SIZE = WIDTH // 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BASE_FONT_SIZE = 36

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schulte Tables by Olga Hlebko")

sequence = list(range(1, 26))
current_number = 1
table_count = 0
start_time = None
times = []
table = None


def generate_table():
    random.shuffle(sequence)
    return [(i % 5 * CELL_SIZE, i // 5 * CELL_SIZE, sequence[i]) for i in range(25)]


def draw_table(table, highlight=None):
    screen.fill(WHITE)
    font = pygame.font.Font(None, BASE_FONT_SIZE)
    for x, y, num in table:
        color = GREEN if highlight == num else RED if highlight == -num else WHITE
        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
        text = font.render(str(num), True, BLACK)
        screen.blit(text, (x + CELL_SIZE // 2 - text.get_width() // 2,
                           y + CELL_SIZE // 2 - text.get_height() // 2))
    pygame.display.flip()
    if highlight:
        pygame.time.delay(200)


def draw_adaptive_text_block(lines):
    font_size = BASE_FONT_SIZE
    spacing = 12
    while font_size >= 14:
        font = pygame.font.Font(None, font_size)
        surfaces = [font.render(line, True, BLACK) for line in lines]
        total_height = sum(s.get_height() for s in surfaces) + spacing * (len(surfaces) - 1)
        max_width = max(s.get_width() for s in surfaces)
        if total_height < HEIGHT - 40 and max_width < WIDTH - 40:
            screen.fill(WHITE)
            y = HEIGHT // 2 - total_height // 2
            for surface in surfaces:
                x = WIDTH // 2 - surface.get_width() // 2
                screen.blit(surface, (x, y))
                y += surface.get_height() + spacing
            return
        font_size -= 2
    screen.fill(WHITE)
    fallback = pygame.font.Font(None, 20).render("Слишком много текста для отображения", True, RED)
    screen.blit(fallback, (WIDTH // 2 - fallback.get_width() // 2, HEIGHT // 2))


def show_transition_screen():
    font = pygame.font.Font(None, BASE_FONT_SIZE)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(WHITE)
    for alpha in range(0, 255, 15):
        overlay.set_alpha(alpha)
        screen.fill(WHITE)
        text = font.render("Следующая таблица", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2,
                           HEIGHT // 2 - text.get_height() // 2))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(50)
    pygame.time.delay(1500)


def show_final_result():
    lines = []
    if times:
        avg_time = round(sum(times) / len(times), 2)

        if avg_time <= 30:
            result = "Норма"
        elif avg_time <= 35:
            result = "Лёгкое ослабление внимания"
        elif avg_time <= 45:
            result = "Внимание умеренно ослаблено"
        elif avg_time <= 55:
            result = "Выраженное ослабление внимания"
        else:
            result = "Резкое ослабление внимания"

        lines.append(f"Среднее время: {avg_time} сек")
        lines.append(result)

        if len(times) >= 2:
            t2_ratio = times[1] / avg_time
            lines.append("Вы можете сходу начать работу без предварительной подготовки."
                         if t2_ratio <= 1 else "Чаще вам нужно время, чтобы влиться в работу.")
        else:
            lines.append("Недостаточно данных по таблице 2.")

        if len(times) >= 4:
            t4_ratio = times[3] / avg_time
            lines.append("Внимание может быть устойчиво достаточно долгое время."
                         if t4_ratio <= 1 else "Вы не удерживаете внимание долгое время, выполняя интеллектуальные задачи.")
        else:
            lines.append("Недостаточно данных по таблице 4.")
    else:
        lines.append("Нет данных")

    draw_adaptive_text_block(lines)
    pygame.display.flip()
    pygame.time.delay(6000)


def draw_instruction_text(lines):
    font_size = BASE_FONT_SIZE
    while True:
        font = pygame.font.Font(None, font_size)
        text_surfaces = [font.render(line, True, BLACK) for line in lines]
        total_height = sum(s.get_height() for s in text_surfaces) + (len(text_surfaces) - 1) * 15
        max_width = max(s.get_width() for s in text_surfaces)
        if total_height < HEIGHT - 40 and max_width < WIDTH - 40:
            break
        font_size -= 2
        if font_size < 16:
            break
    start_y = HEIGHT // 2 - total_height // 2
    for surface in text_surfaces:
        x = WIDTH // 2 - surface.get_width() // 2
        screen.blit(surface, (x, start_y))
        start_y += surface.get_height() + 15


def check_click(table, pos):
    global current_number, table_count, start_time, times
    for x, y, num in table:
        if x < pos[0] < x + CELL_SIZE and y < pos[1] < y + CELL_SIZE:
            if num == current_number:
                draw_table(table, highlight=num)
                current_number += 1
                if current_number > 25:
                    times.append(round(time.time() - start_time, 2))
                    table_count += 1
                    if table_count < 5:
                        show_transition_screen()
                        current_number = 1
                        start_time = time.time()
                        return generate_table()
                    else:
                        show_final_result()
                        return None
            else:
                draw_table(table, highlight=-num)
    return table


# Главный игровой цикл
running = True
start_screen = True

while running:
    screen.fill(WHITE)
    if start_screen:
        instructions = [
            "Перед вами будут появляться таблицы с цифрами.",
            "Нажимайте на числа от 1 до 25 по порядку как можно быстрее!.",
            "Для начала нажмите любую клавишу."
        ]
        draw_instruction_text(instructions)
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and start_screen:
            start_screen = False
            start_time = time.time()
            table_count = 0
            times = []
            current_number = 1
            table = generate_table()

        elif event.type == pygame.MOUSEBUTTONDOWN and table:
            table = check_click(table, pygame.mouse.get_pos())

    if table:
        draw_table(table)

pygame.quit()
