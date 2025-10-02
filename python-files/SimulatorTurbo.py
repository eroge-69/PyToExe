import pygame
import sys
import os
import json
import math

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SimulatorTurbo: Симулятор Планеты")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)   # Вода
RED = (255, 50, 0)     # Огонь
GREEN = (0, 200, 0)    # Земля
YELLOW = (255, 255, 0) # Воздух

# Папка для сохранения на рабочем столе
save_folder = os.path.join(os.path.expanduser("~"), "Desktop", "SimulatorTurbo")
if not os.path.exists(save_folder):
    os.makedirs(save_folder)
save_file = os.path.join(save_folder, "save.json")

# Загрузка состояния
def load_game():
    if os.path.exists(save_file):
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"water": 0, "fire": 0, "earth": 0, "air": 0}
    return {"water": 0, "fire": 0, "earth": 0, "air": 0}

# Сохранение состояния
def save_game(state):
    with open(save_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

# Анимация стихии
def animate_element(element, color):
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    for i in range(20):  # 20 кадров анимации
        screen.fill(BLACK)
        # Рисуем планету как круг
        radius = 100 + i * 2
        pygame.draw.circle(screen, color, (center_x, center_y), radius, 5)
        # Добавляем текст стихии
        font = pygame.font.Font(None, 48)
        text = font.render(element, True, color)
        screen.blit(text, (center_x - 20, center_y - 20))
        pygame.display.flip()
        clock.tick(15)  # Скорость анимации
    # Финальный кадр
    pygame.draw.circle(screen, WHITE, (center_x, center_y), 100, 2)

# Рисование кнопок
def draw_button(screen, text, x, y, color, text_color=WHITE):
    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(x, y, 150, 50)
    pygame.draw.rect(screen, color, button_rect)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

# Главный цикл
def main():
    game_state = load_game()
    running = True
    animation_active = False
    anim_element = ""
    anim_color = WHITE

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(game_state)
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Вода
                    game_state["water"] += 1
                    if game_state["fire"] > 0:
                        game_state["fire"] -= 1
                    animation_active = True
                    anim_element = "Вода"
                    anim_color = BLUE
                elif event.key == pygame.K_2:  # Огонь
                    game_state["fire"] += 1
                    if game_state["water"] > 0:
                        game_state["water"] -= 1
                    animation_active = True
                    anim_element = "Огонь"
                    anim_color = RED
                elif event.key == pygame.K_3:  # Земля
                    game_state["earth"] += 1
                    if game_state["air"] > 0:
                        game_state["air"] -= 1
                    animation_active = True
                    anim_element = "Земля"
                    anim_color = GREEN
                elif event.key == pygame.K_4:  # Воздух
                    game_state["air"] += 1
                    if game_state["earth"] > 0:
                        game_state["earth"] -= 1
                    animation_active = True
                    anim_element = "Воздух"
                    anim_color = YELLOW
                elif event.key == pygame.K_5:  # Сброс
                    game_state = {"water": 0, "fire": 0, "earth": 0, "air": 0}
                elif event.key == pygame.K_0:  # Выход
                    save_game(game_state)
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Кнопки (примерные координаты)
                if 50 <= mouse_pos[0] <= 200 and 400 <= mouse_pos[1] <= 450:  # Кнопка 1
                    # То же, что K_1
                    game_state["water"] += 1
                    if game_state["fire"] > 0:
                        game_state["fire"] -= 1
                    animation_active = True
                    anim_element = "Вода"
                    anim_color = BLUE
                # Добавь аналогично для других кнопок...

        # Анимация
        if animation_active:
            animate_element(anim_element, anim_color)
            animation_active = False

        # Отрисовка
        screen.fill(BLACK)
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)

        # Заголовок
        title = font_large.render("SimulatorTurbo", True, WHITE)
        screen.blit(title, (WIDTH//2 - 150, 20))

        # Состояние
        state_text = font_small.render(
            f"Вода: {game_state['water']} | Огонь: {game_state['fire']} | Земля: {game_state['earth']} | Воздух: {game_state['air']}",
            True, WHITE
        )
        screen.blit(state_text, (50, 100))

        # Планета (статичная, с элементами)
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        pygame.draw.circle(screen, WHITE, (center_x, center_y), 100, 2)
        if game_state["water"] > 0:
            pygame.draw.circle(screen, BLUE, (center_x - 30, center_y - 30), 20)
        if game_state["fire"] > 0:
            pygame.draw.circle(screen, RED, (center_x + 30, center_y - 30), 20)
        if game_state["earth"] > 0:
            pygame.draw.circle(screen, GREEN, (center_x - 30, center_y + 30), 20)
        if game_state["air"] > 0:
            pygame.draw.circle(screen, YELLOW, (center_x + 30, center_y + 30), 20)

        # Кнопки
        draw_button(screen, "Вода (1)", 50, 400, BLUE)
        draw_button(screen, "Огонь (2)", 250, 400, RED)
        draw_button(screen, "Земля (3)", 450, 400, GREEN)
        draw_button(screen, "Воздух (4)", 50, 500, YELLOW)
        draw_button(screen, "Сброс (5)", 250, 500, WHITE)
        draw_button(screen, "Выход (0)", 450, 500, (128, 128, 128))

        # Проверка баланса
        total = sum(game_state.values())
        if total > 10:
            lose_text = font_large.render("Перегрузка! Проигрыш!", True, RED)
            screen.blit(lose_text, (WIDTH//2 - 150, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            game_state = {"water": 0, "fire": 0, "earth": 0, "air": 0}
        elif all(v >= 3 for v in game_state.values()):
            win_text = font_large.render("Гармония! Победа!", True, GREEN)
            screen.blit(win_text, (WIDTH//2 - 150, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            game_state = {"water": 0, "fire": 0, "earth": 0, "air": 0}

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()