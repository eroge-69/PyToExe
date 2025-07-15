import pygame
import sys
import datetime
import random
import math

# --- Константы ---
WIDTH, HEIGHT = 1200, 600
FPS = 60

# --- Инициализация ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GTA Berlin")
clock = pygame.time.Clock()

# --- Шрифты ---
title_font = pygame.font.SysFont(None, 44)
menu_font = pygame.font.SysFont(None, 40)
info_font = pygame.font.SysFont(None, 28)

# --- Погода ---
WEATHER_LIST = [
    "Солнечно",
    "Облачно",
    "Дождь",
    "Туман",
    "Гроза",
    "Ветрено",
]
current_weather = random.choice(WEATHER_LIST)

# --- Для отслеживания клика по иконке ---
market_icon_last_click = False
nav_icon_last_click = False
pharmacy_icon_last_click = False
craft_icon_last_click = False
dealer_point_last_click = False
bank_point_last_click = False
lombard_point_last_click = False
supermarket_point_last_click = False
pharmacy_point_last_click = False
clothes_point_last_click = False
apt_btn_last_click = False
car_btn_last_click = False

# --- Товары черного рынка ---
MARKET_ITEMS = [
    ("Glock-17", 400),
    ("Бита", 80),
    ("Швейцарский нож", 120),
    ("Отмычки (5 шт.)", 60),
    ("Электрошокер", 200),
    ("USP", 350),
    ("Перцовый баллончик", 50),
    ("Взрывчатка", 1000),
    ("Кастет", 90),
    ("Пакетики для наркотиков", 30)
]

# --- Товары аптеки ---
PHARMACY_ITEMS = [
    ("Парацетамол", 40),
    ("Йод", 25),
    ("Шприцы (5 шт.)", 30),
    ("Перекись водорода", 20),
    ("Ацетон", 50),
    ("Марганцовка", 60),
    ("Медицинский спирт", 70),
    ("Пустые капсулы (10 шт.)", 35),
    ("Маска", 45),
    ("Перчатки", 20),
]

# --- Рецепты крафта наркотиков ---
CRAFT_RECIPES = [
    {
        'name': 'Наркотик',
        'ingredients': ['Шприцы (5 шт.)', 'Марганцовка'],
        'result': 'Наркотик',
        'price': 0,  # не продаётся, только крафт
    },
    {
        'name': 'Капсулы с наркотиком',
        'ingredients': ['Пустые капсулы (10 шт.)', 'Парацетамол', 'Медицинский спирт'],
        'result': 'Капсулы с наркотиком',
        'price': 0,
    },
    # Новые рецепты с пакетиками для наркотиков
    {
        'name': 'Порошок в пакетике',
        'ingredients': ['Пакетики для наркотиков', 'Марганцовка', 'Парацетамол'],
        'result': 'Порошок в пакетике',
        'price': 0,
    },
    {
        'name': 'Трава в пакетике',
        'ingredients': ['Пакетики для наркотиков', 'Медицинский спирт', 'Йод'],
        'result': 'Трава в пакетике',
        'price': 0,
    },
    {
        'name': 'Экстракт в пакетике',
        'ingredients': ['Пакетики для наркотиков', 'Ацетон', 'Шприцы (5 шт.)'],
        'result': 'Экстракт в пакетике',
        'price': 0,
    },
]

# --- Глобальные переменные ---
money = 200
health = 85
wanted = 0
inventory = []
has_apartment = False  # Есть ли квартира
has_car = False        # Есть ли машина
apartment_info = None  # dict: district, area, ...
car_info = None        # dict: brand, model, ...

# --- В начало файла, после глобальных переменных ---
game_over = False
heist_jewelry_data = None

# --- Основной цикл ---
def draw_button(rect, text, font, screen, color, border_color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, border_color, rect, 2)
    text_surf = font.render(text, True, (255, 255, 255))
    screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

def draw_stats_panel(screen, money, health, wanted, inventory, hunger):
    panel_rect = pygame.Rect(20, 20, 480, 360)
    pygame.draw.rect(screen, (20, 20, 30), panel_rect)
    pygame.draw.rect(screen, (60, 60, 80), panel_rect, 2)
    font = pygame.font.SysFont(None, 28)
    inv_font = pygame.font.SysFont(None, 14)
    # Деньги
    money_text = font.render(f"Деньги: {money}€", True, (255, 255, 80))
    screen.blit(money_text, (panel_rect.x + 12, panel_rect.y + 12))
    # Здоровье
    health_text = font.render(f"Здоровье: {health}", True, (200, 80, 80))
    screen.blit(health_text, (panel_rect.x + 12, panel_rect.y + 44))
    # Голод
    hunger_text = font.render(f"Голод: {hunger}", True, (255, 200, 80))
    screen.blit(hunger_text, (panel_rect.x + 12, panel_rect.y + 76))
    # Розыск
    wanted_text = font.render(f"Розыск: {wanted}", True, (255, 80, 80))
    screen.blit(wanted_text, (panel_rect.x + 12, panel_rect.y + 108))
    # Инвентарь
    inv_label = font.render("Инвентарь:", True, (255, 255, 255))
    screen.blit(inv_label, (panel_rect.x + 12, panel_rect.y + 142))
    # Ячейки инвентаря (6x2)
    cell_size = 48
    cell_margin = 8
    cells_x = 6
    cells_y = 2
    for i in range(cells_x * cells_y):
        cx = panel_rect.x + 12 + (i % cells_x) * (cell_size + cell_margin)
        cy = panel_rect.y + 172 + (i // cells_x) * (cell_size + cell_margin)
        cell_rect = pygame.Rect(cx, cy, cell_size, cell_size)
        pygame.draw.rect(screen, (30, 30, 40), cell_rect)
        pygame.draw.rect(screen, (100, 100, 140), cell_rect, 2)
        # Если есть предмет — выводим текст, обрезая если не помещается
        if i < len(inventory):
            item = inventory[i]
            # Обрезаем текст если не помещается
            max_width = cell_size - 8
            item_text = item
            while inv_font.size(item_text)[0] > max_width and len(item_text) > 1:
                item_text = item_text[:-1]
            if item_text != item:
                item_text = item_text[:-1] + '…'
            text_surf = inv_font.render(item_text, True, (200, 200, 200))
            screen.blit(text_surf, (cell_rect.x + 4, cell_rect.y + cell_size // 2 - text_surf.get_height() // 2))
    # Новый прямоугольник — квартира и машина
    global has_apartment, has_car, apartment_info, car_info
    info_rect = pygame.Rect(panel_rect.right + 20, panel_rect.y, 260, 110)
    pygame.draw.rect(screen, (30, 30, 40), info_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 140), info_rect, 2, border_radius=10)
    info_font = pygame.font.SysFont(None, 24)
    # Квартира
    if has_apartment and apartment_info:
        apt_text1 = info_font.render(f"Квартира: {apartment_info['district']}", True, (200,255,200))
        apt_text2 = info_font.render(f"Адрес: ул. {apartment_info['district']}, {random.randint(1, 99)}", True, (200,255,200))
        apt_text3 = info_font.render(f"Площадь: {apartment_info['area']} м²", True, (200,255,200))
    else:
        apt_text1 = info_font.render("Квартира: нет", True, (200,200,200))
        apt_text2 = info_font.render("Адрес: —", True, (200,200,200))
        apt_text3 = info_font.render("Площадь: —", True, (200,200,200))
    screen.blit(apt_text1, (info_rect.x + 16, info_rect.y + 10))
    screen.blit(apt_text2, (info_rect.x + 16, info_rect.y + 36))
    screen.blit(apt_text3, (info_rect.x + 16, info_rect.y + 62))
    # Машина
    if has_car and car_info:
        car_text = info_font.render(f"Машина: {car_info['brand']} {car_info['model']}", True, (200,255,200))
    else:
        car_text = info_font.render("Машина: нет", True, (200,200,200))
    screen.blit(car_text, (info_rect.x + 16, info_rect.y + 88))

def main_menu():
    global money, health, wanted, inventory, game_over, info_font, hunger
    global has_apartment, has_car
    if 'hunger' not in globals():
        hunger = 100
    running = True
    state = 'menu'
    while running:
        clock.tick(FPS)
        if wanted >= 5:
            game_over = True
            state = 'wanted_game_over'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Фон
        screen.fill((10, 10, 15))

        # Надпись GTA Berlin
        title_text = title_font.render("Gefährlich Berlin", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 60))

        # --- Дата, время, погода ---
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")
        # Смена погоды
        # Рисуем прямоугольник
        info_rect = pygame.Rect(20, 20, 210, 90)
        pygame.draw.rect(screen, (20, 20, 30), info_rect)
        pygame.draw.rect(screen, (60, 60, 80), info_rect, 2)
        date_text = info_font.render(f"Дата: {date_str}", True, (255, 255, 255))
        time_text = info_font.render(f"Время: {time_str}", True, (255, 255, 255))
        weather_text = info_font.render(f"Погода: {current_weather}", True, (255, 255, 255))
        screen.blit(date_text, (info_rect.x + 10, info_rect.y + 8))
        screen.blit(time_text, (info_rect.x + 10, info_rect.y + 36))
        screen.blit(weather_text, (info_rect.x + 10, info_rect.y + 64))

        if state == 'menu':
            # Кнопки меню
            btn_w, btn_h = 260, 60
            btn_color = (20, 20, 30)
            btn_border = (60, 60, 80)
            start_btn_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 - 50, btn_w, btn_h)
            exit_btn_rect = pygame.Rect(WIDTH // 2 - btn_w // 2, HEIGHT // 2 + 30, btn_w, btn_h)
            draw_button(start_btn_rect, "Начать игру", menu_font, screen, btn_color, btn_border)
            draw_button(exit_btn_rect, "Выход", menu_font, screen, btn_color, btn_border)

            # Обработка кликов по кнопкам
            mouse = pygame.mouse.get_pressed()
            if mouse[0]:
                mx, my = pygame.mouse.get_pos()
                if start_btn_rect.collidepoint(mx, my):
                    state = 'game'
                if exit_btn_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        elif state == 'game':
            # Игровое поле — такой же фон, как в меню
            screen.fill((10, 10, 15))

            # Внешний вид телефона справа (увеличенный)
            phone_rect = pygame.Rect(WIDTH - 180, 20, 140, 280)
            pygame.draw.rect(screen, (30, 30, 40), phone_rect, border_radius=28)
            pygame.draw.rect(screen, (100, 100, 140), phone_rect, 4, border_radius=28)
            # Экран телефона
            screen_rect = pygame.Rect(phone_rect.x + 18, phone_rect.y + 32, 104, 190)
            pygame.draw.rect(screen, (15, 15, 25), screen_rect, border_radius=16)
            # Кнопка home
            pygame.draw.circle(screen, (80, 80, 120), (phone_rect.centerx, phone_rect.bottom - 26), 13)
            # Иконки приложений
            app_font = pygame.font.SysFont(None, 26)
            # Черный рынок
            market_icon = pygame.Rect(screen_rect.x + 14, screen_rect.y + 22, 32, 32)
            pygame.draw.rect(screen, (40, 40, 40), market_icon, border_radius=8)
            market_text = app_font.render("Ч.рынок", True, (255, 255, 255))
            screen.blit(market_text, (market_icon.x + market_icon.width // 2 - market_text.get_width() // 2, market_icon.bottom + 4))
            # Обработка клика по иконке черного рынка
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            global market_icon_last_click
            if mouse[0] and market_icon.collidepoint(mx, my):
                if not market_icon_last_click:
                    state = 'market'
                market_icon_last_click = True
            else:
                market_icon_last_click = False
            # Навигатор
            nav_icon = pygame.Rect(screen_rect.x + 58, screen_rect.y + 22, 32, 32)
            pygame.draw.polygon(screen, (80, 160, 220), [
                (nav_icon.centerx, nav_icon.y),
                (nav_icon.x, nav_icon.bottom),
                (nav_icon.right, nav_icon.bottom)
            ])
            nav_text = app_font.render("Навиг.", True, (255, 255, 255))
            screen.blit(nav_text, (nav_icon.x + nav_icon.width // 2 - nav_text.get_width() // 2, nav_icon.bottom + 4))
            # Телефон
            tel_icon = pygame.Rect(screen_rect.x + 30, screen_rect.y + 80, 44, 44)
            pygame.draw.rect(screen, (200, 200, 255), tel_icon, border_radius=12)
            tel_text = app_font.render("Телефон", True, (255, 255, 255))
            screen.blit(tel_text, (tel_icon.x + tel_icon.width // 2 - tel_text.get_width() // 2, tel_icon.bottom + 4))
            # Кнопка Крафт — отдельно на экране, не в телефоне
            craft_btn_rect = pygame.Rect(40, 480, 180, 54)
            pygame.draw.rect(screen, (180, 120, 60), craft_btn_rect, border_radius=14)
            pygame.draw.rect(screen, (120, 80, 30), craft_btn_rect, 4, border_radius=14)
            craft_btn_font = pygame.font.SysFont(None, 36)
            craft_btn_text = craft_btn_font.render("Крафт наркотиков", True, (255, 255, 255))
            screen.blit(craft_btn_text, (craft_btn_rect.centerx - craft_btn_text.get_width() // 2, craft_btn_rect.centery - craft_btn_text.get_height() // 2))
            # Новые кнопки: Покупка квартиры и машины
            apt_btn_rect = pygame.Rect(240, 480, 180, 54)
            car_btn_rect = pygame.Rect(440, 480, 180, 54)
            # Квартира
            pygame.draw.rect(screen, (80, 120, 200) if not has_apartment else (120, 120, 120), apt_btn_rect, border_radius=14)
            pygame.draw.rect(screen, (40, 80, 160), apt_btn_rect, 4, border_radius=14)
            apt_btn_font = pygame.font.SysFont(None, 32)
            apt_btn_text = apt_btn_font.render("Покупка квартиры", True, (255, 255, 255))
            screen.blit(apt_btn_text, (apt_btn_rect.centerx - apt_btn_text.get_width() // 2, apt_btn_rect.centery - apt_btn_text.get_height() // 2))
            if has_apartment:
                bought_text = apt_btn_font.render("Куплено", True, (200,255,200))
                screen.blit(bought_text, (apt_btn_rect.centerx - bought_text.get_width() // 2, apt_btn_rect.bottom - 24))
            # Машина
            pygame.draw.rect(screen, (200, 120, 80) if not has_car else (120, 120, 120), car_btn_rect, border_radius=14)
            pygame.draw.rect(screen, (160, 80, 40), car_btn_rect, 4, border_radius=14)
            car_btn_font = pygame.font.SysFont(None, 32)
            car_btn_text = car_btn_font.render("Покупка машины", True, (255, 255, 255))
            screen.blit(car_btn_text, (car_btn_rect.centerx - car_btn_text.get_width() // 2, car_btn_rect.centery - car_btn_text.get_height() // 2))
            if has_car:
                bought_text = car_btn_font.render("Куплено", True, (200,255,200))
                screen.blit(bought_text, (car_btn_rect.centerx - bought_text.get_width() // 2, car_btn_rect.bottom - 24))
            global craft_icon_last_click
            if mouse[0] and craft_btn_rect.collidepoint(mx, my):
                if not craft_icon_last_click:
                    state = 'craft'
                craft_icon_last_click = True
            else:
                craft_icon_last_click = False
            # Обработка кликов по новым кнопкам
            global apt_btn_last_click, car_btn_last_click
            if 'apt_btn_last_click' not in globals():
                apt_btn_last_click = False
            if 'car_btn_last_click' not in globals():
                car_btn_last_click = False
            # Квартира
            if mouse[0] and apt_btn_rect.collidepoint(mx, my):
                if not apt_btn_last_click and not has_apartment:
                    state = 'apartment_shop'
                apt_btn_last_click = True
            else:
                apt_btn_last_click = False
            # Машина
            if mouse[0] and car_btn_rect.collidepoint(mx, my):
                if not car_btn_last_click and not has_car:
                    state = 'car_shop'
                car_btn_last_click = True
            else:
                car_btn_last_click = False
            # Голод уменьшается каждые 5 секунд
            if 'last_hunger_tick' not in globals():
                last_hunger_tick = pygame.time.get_ticks()
            if pygame.time.get_ticks() - last_hunger_tick > 5000:
                hunger -= 1
                last_hunger_tick = pygame.time.get_ticks()
            if hunger <= 0:
                game_over = True
                state = 'wanted_game_over'
            draw_stats_panel(screen, money, health, wanted, inventory, hunger)

            # Обработка клика по иконке навигатора
            global nav_icon_last_click
            if mouse[0] and nav_icon.collidepoint(mx, my):
                if not nav_icon_last_click:
                    state = 'navigator'
                nav_icon_last_click = True
            else:
                nav_icon_last_click = False

            # Кнопка ESC возвращает в меню
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = 'menu'
            pygame.display.flip()
            continue

        elif state == 'market':
            # Центрируем и расширяем окно черного рынка
            market_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), market_rect, border_radius=18)
            pygame.draw.rect(screen, (100, 100, 140), market_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Черный рынок", True, (255, 255, 255))
            screen.blit(title, (market_rect.centerx - title.get_width() // 2, market_rect.y + 18))
            # Список товаров
            item_font = pygame.font.SysFont(None, 28)
            btn_font = pygame.font.SysFont(None, 24)
            buy_btns = []
            for i, (item, price) in enumerate(MARKET_ITEMS):
                y = market_rect.y + 70 + i * 34
                item_text = item_font.render(item, True, (220, 220, 220))
                price_text = item_font.render(f"{price}€", True, (255, 255, 80))
                screen.blit(item_text, (market_rect.x + 30, y))
                screen.blit(price_text, (market_rect.x + 320, y))
                btn_rect = pygame.Rect(market_rect.right - 120, y - 4, 90, 28)
                pygame.draw.rect(screen, (20, 20, 30), btn_rect, border_radius=8)
                pygame.draw.rect(screen, (60, 60, 80), btn_rect, 2, border_radius=8)
                btn_text = btn_font.render("Купить", True, (255, 255, 255))
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))
                buy_btns.append((btn_rect, item, price))
            # Кнопка назад
            back_rect = pygame.Rect(market_rect.x + 20, market_rect.bottom - 50, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (60, 60, 80), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                # Купить
                for btn_rect, item, price in buy_btns:
                    if btn_rect.collidepoint(mx, my):
                        if len(inventory) < 12 and item not in inventory and money >= price:
                            inventory.append(item)
                            money -= price
                # Назад
                if back_rect.collidepoint(mx, my):
                    state = 'game'

            pygame.display.flip()
            continue

        elif state == 'pharmacy':
            # Окно аптеки
            pharmacy_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 40, 40), pharmacy_rect, border_radius=18)
            pygame.draw.rect(screen, (60, 180, 180), pharmacy_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Аптека — ингредиенты и средства", True, (255, 255, 255))
            screen.blit(title, (pharmacy_rect.centerx - title.get_width() // 2, pharmacy_rect.y + 18))
            item_font = pygame.font.SysFont(None, 28)
            btn_font = pygame.font.SysFont(None, 24)
            buy_btns = []
            for i, (item, price) in enumerate(PHARMACY_ITEMS):
                y = pharmacy_rect.y + 70 + i * 34
                item_text = item_font.render(item, True, (220, 220, 220))
                price_text = item_font.render(f"{price}€", True, (60, 255, 255))
                screen.blit(item_text, (pharmacy_rect.x + 30, y))
                screen.blit(price_text, (pharmacy_rect.x + 320, y))
                btn_rect = pygame.Rect(pharmacy_rect.right - 120, y - 4, 90, 28)
                pygame.draw.rect(screen, (20, 30, 30), btn_rect, border_radius=8)
                pygame.draw.rect(screen, (60, 180, 180), btn_rect, 2, border_radius=8)
                btn_text = btn_font.render("Купить", True, (255, 255, 255))
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))
                buy_btns.append((btn_rect, item, price))
            # Кнопка назад
            back_rect = pygame.Rect(pharmacy_rect.x + 20, pharmacy_rect.bottom - 50, 120, 36)
            pygame.draw.rect(screen, (20, 30, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (60, 180, 180), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                # Купить
                for btn_rect, item, price in buy_btns:
                    if btn_rect.collidepoint(mx, my):
                        if len(inventory) < 12 and item not in inventory and money >= price:
                            inventory.append(item)
                            money -= price
                # Назад
                if back_rect.collidepoint(mx, my):
                    state = 'game'
            pygame.display.flip()
            continue

        elif state == 'navigator':
            # Окно навигатора
            nav_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (25, 30, 40), nav_rect, border_radius=18)
            pygame.draw.rect(screen, (100, 100, 140), nav_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Навигатор города", True, (255, 255, 255))
            screen.blit(title, (nav_rect.centerx - title.get_width() // 2, nav_rect.y + 18))
            # Схематичная карта (прямоугольник)
            map_rect = pygame.Rect(nav_rect.x + 40, nav_rect.y + 70, 560, 300)
            pygame.draw.rect(screen, (40, 50, 70), map_rect, border_radius=12)
            pygame.draw.rect(screen, (80, 100, 140), map_rect, 2, border_radius=12)
            # Дороги (линии)
            road_color = (120, 120, 120)
            road_width = 6
            # Примерные координаты точек для соединения дорогами
            road_points = [
                (map_rect.x + 80, map_rect.y + 60),    # Банк
                (map_rect.x + 320, map_rect.y + 60),   # Магазин
                (map_rect.x + 400, map_rect.y + 80),   # Заправка
                (map_rect.x + 480, map_rect.y + 120),  # Ювелирка
                (map_rect.x + 500, map_rect.y + 250),  # Дилер
                (map_rect.x + 420, map_rect.y + 270),  # Касса метро
                (map_rect.x + 350, map_rect.y + 200),  # Супермаркет
                (map_rect.x + 300, map_rect.y + 250),  # Пекарня
                (map_rect.x + 250, map_rect.y + 120),  # Ломбард
                (map_rect.x + 200, map_rect.y + 220),  # Аптека
                (map_rect.x + 120, map_rect.y + 180),  # Минимаркет
                (map_rect.x + 60, map_rect.y + 260),   # Тюрьма
                (map_rect.x + 100, map_rect.y + 100),  # Кафе
                (map_rect.x + 180, map_rect.y + 80),   # Магазин техники
                (map_rect.x + 380, map_rect.y + 150),  # Магазин одежды
            ]
            # Основные улицы (цепочки точек)
            main_roads = [
                [0, 1, 2, 3, 4, 5, 6, 7],  # Центральная улица
                [0, 8, 9, 10, 11],         # Южная улица
                [1, 13, 14, 6],            # Северная улица
                [12, 10, 7],               # Кафе — Минимаркет — Пекарня
            ]
            for road in main_roads:
                pygame.draw.lines(screen, road_color, False, [road_points[i] for i in road], road_width)
            # Точки интереса
            nav_points = [
                ("Банк", (map_rect.x + 80, map_rect.y + 60)),
                ("Заправка", (map_rect.x + 400, map_rect.y + 80)),
                ("Аптека", (map_rect.x + 200, map_rect.y + 220)),
                ("Дилер", (map_rect.x + 500, map_rect.y + 250)),
                ("Тюрьма", (map_rect.x + 60, map_rect.y + 260)),
                ("Магазин", (map_rect.x + 320, map_rect.y + 60)),
                ("Ломбард", (map_rect.x + 480, map_rect.y + 120)),
                ("Минимаркет", (map_rect.x + 120, map_rect.y + 180)),
                ("Супермаркет", (map_rect.x + 350, map_rect.y + 200)),
                ("Ювелирка", (map_rect.x + 250, map_rect.y + 120)),
                ("Касса метро", (map_rect.x + 420, map_rect.y + 270)),
                ("Магазин техники", (map_rect.x + 180, map_rect.y + 80)),
                ("Магазин одежды", (map_rect.x + 380, map_rect.y + 150)),
                ("Кафе", (map_rect.x + 100, map_rect.y + 100)),
                ("Пекарня", (map_rect.x + 300, map_rect.y + 250)),
                ("Ограбление: банк", (map_rect.x + 80, map_rect.y + 40)),
                ("Ограбление: ювелирка", (map_rect.x + 250, map_rect.y + 100)),
                ("Ограбление: ломбард", (map_rect.x + 480, map_rect.y + 100)),
                ("Ограбление: супермаркет", (map_rect.x + 350, map_rect.y + 180)),
                ("Ограбление: магазин техники", (map_rect.x + 180, map_rect.y + 40)),
            ]
            point_font = pygame.font.SysFont(None, 16)
            for name, (px, py) in nav_points:
                pygame.draw.circle(screen, (220, 180, 60), (px, py), 10)
                pygame.draw.circle(screen, (120, 100, 40), (px, py), 10, 2)
                label = point_font.render(name, True, (255, 255, 255))
                screen.blit(label, (px + 12, py - 8))
            # Обработка клика по точке 'Дилер'
            dealer_idx = 3  # индекс точки 'Дилер'
            mx, my = pygame.mouse.get_pos()
            dealer_point = nav_points[dealer_idx][1]
            global dealer_point_last_click
            if mouse[0] and (mx - dealer_point[0]) ** 2 + (my - dealer_point[1]) ** 2 < 14 ** 2:
                if not dealer_point_last_click:
                    globals()['travel_price'] = 0  # Бесплатно!
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Дилер'
                    globals()['travel_next_state'] = 'dealer'
                    state = 'travel_payment'
                dealer_point_last_click = True
            else:
                dealer_point_last_click = False
            # Обработка клика по точке 'Ограбление: банк'
            bank_idx = 15
            bank_point = nav_points[bank_idx][1]
            global bank_point_last_click
            if mouse[0] and (mx - bank_point[0]) ** 2 + (my - bank_point[1]) ** 2 < 14 ** 2:
                if not bank_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Ограбление: банк'
                    globals()['travel_next_state'] = 'heist_bank'
                    state = 'travel_payment'
                bank_point_last_click = True
            else:
                bank_point_last_click = False
            # Обработка клика по точке 'Ограбление: ломбард'
            lombard_idx = 17
            lombard_point = nav_points[lombard_idx][1]
            global lombard_point_last_click
            if mouse[0] and (mx - lombard_point[0]) ** 2 + (my - lombard_point[1]) ** 2 < 14 ** 2:
                if not lombard_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Ограбление: ломбард'
                    globals()['travel_next_state'] = 'heist_lombard'
                    state = 'travel_payment'
                lombard_point_last_click = True
            else:
                lombard_point_last_click = False
            # Обработка клика по точке 'Ограбление: супермаркет'
            supermarket_idx = 18
            supermarket_point = nav_points[supermarket_idx][1]
            global supermarket_point_last_click
            if mouse[0] and (mx - supermarket_point[0]) ** 2 + (my - supermarket_point[1]) ** 2 < 14 ** 2:
                if not supermarket_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Ограбление: супермаркет'
                    globals()['travel_next_state'] = 'heist_supermarket'
                    state = 'travel_payment'
                supermarket_point_last_click = True
            else:
                supermarket_point_last_click = False
            # Обработка клика по точке 'Аптека'
            pharmacy_idx = 2  # индекс точки 'Аптека' в nav_points
            pharmacy_point = nav_points[pharmacy_idx][1]
            global pharmacy_point_last_click
            if mouse[0] and (mx - pharmacy_point[0]) ** 2 + (my - pharmacy_point[1]) ** 2 < 14 ** 2:
                if not pharmacy_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Аптека'
                    globals()['travel_next_state'] = 'pharmacy'
                    state = 'travel_payment'
                pharmacy_point_last_click = True
            else:
                pharmacy_point_last_click = False
            # Обработка клика по точке 'Магазин одежды'
            clothes_idx = 12  # индекс точки 'Магазин одежды' в nav_points
            clothes_point = nav_points[clothes_idx][1]
            global clothes_point_last_click
            if mouse[0] and (mx - clothes_point[0]) ** 2 + (my - clothes_point[1]) ** 2 < 14 ** 2:
                if not clothes_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Магазин одежды'
                    globals()['travel_next_state'] = 'clothes_shop'
                    state = 'travel_payment'
                clothes_point_last_click = True
            else:
                clothes_point_last_click = False
            # Добавляю точку 'Ограбление: заправка' на карту
            nav_points.append(("Ограбление: заправка", (map_rect.x + 400, map_rect.y + 60)))
            # Обработка клика по точке 'Ограбление: заправка'
            gas_heist_idx = len(nav_points) - 1
            gas_heist_point = nav_points[gas_heist_idx][1]
            global gas_heist_point_last_click
            if mouse[0] and (mx - gas_heist_point[0]) ** 2 + (my - gas_heist_point[1]) ** 2 < 14 ** 2:
                if not gas_heist_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Ограбление: заправка'
                    globals()['travel_next_state'] = 'heist_gas_station'
                    state = 'travel_payment'
                gas_heist_point_last_click = True
            else:
                gas_heist_point_last_click = False
            # Кнопка назад
            btn_font = pygame.font.SysFont(None, 24)
            back_rect = pygame.Rect(nav_rect.x + 20, nav_rect.bottom - 50, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (60, 60, 80), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            # Обработка клика по кнопке 'Назад' с анти-автокликом
            global back_btn_last_click
            if 'back_btn_last_click' not in globals():
                back_btn_last_click = False
            if mouse[0] and back_rect.collidepoint(mx, my):
                if not back_btn_last_click:
                    state = 'game'
                back_btn_last_click = True
            else:
                back_btn_last_click = False
            # Обработка клика по точке 'Ограбление: магазин техники'
            electronics_heist_idx = 19  # индекс новой точки
            electronics_heist_point = nav_points[electronics_heist_idx][1]
            global electronics_heist_point_last_click
            if mouse[0] and (mx - electronics_heist_point[0]) ** 2 + (my - electronics_heist_point[1]) ** 2 < 14 ** 2:
                if not electronics_heist_point_last_click:
                    globals()['travel_price'] = random.randint(0, 300)
                    globals()['travel_method'] = random.choice(['Такси', 'Метро'])
                    globals()['travel_dest'] = 'Ограбление: магазин техники'
                    globals()['travel_next_state'] = 'heist_electronics'
                    state = 'travel_payment'
                electronics_heist_point_last_click = True
            else:
                electronics_heist_point_last_click = False

        elif state == 'craft':
            # Новый красивый интерфейс крафта
            craft_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (40, 30, 20), craft_rect, border_radius=18)
            pygame.draw.rect(screen, (180, 120, 60), craft_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Крафт — изготовление наркотиков", True, (255, 255, 255))
            screen.blit(title, (craft_rect.centerx - title.get_width() // 2, craft_rect.y + 18))
            item_font = pygame.font.SysFont(None, 26)
            btn_font = pygame.font.SysFont(None, 24)
            recipe_h = 70
            recipe_margin = 18
            start_y = craft_rect.y + 70
            craft_btns = []
            for i, recipe in enumerate(CRAFT_RECIPES):
                y = start_y + i * (recipe_h + recipe_margin)
                # Блок рецепта
                recipe_block = pygame.Rect(craft_rect.x + 24, y, craft_rect.width - 48, recipe_h)
                pygame.draw.rect(screen, (60, 45, 30), recipe_block, border_radius=12)
                pygame.draw.rect(screen, (180, 120, 60), recipe_block, 2, border_radius=12)
                # Ингредиенты
                ing_x = recipe_block.x + 12
                for ing in recipe['ingredients']:
                    have = inventory.count(ing) > 0
                    color = (80, 200, 80) if have else (200, 60, 60)
                    ing_rect = pygame.Rect(ing_x, y + 12, 120, 32)
                    pygame.draw.rect(screen, color, ing_rect, border_radius=8)
                    pygame.draw.rect(screen, (255, 255, 255), ing_rect, 2, border_radius=8)
                    # Текст ингредиента
                    ing_text = item_font.render(ing, True, (30, 30, 30))
                    # Обрезка текста если не помещается
                    max_ing_w = ing_rect.width - 10
                    while ing_text.get_width() > max_ing_w and len(ing) > 2:
                        ing = ing[:-1]
                        ing_text = item_font.render(ing + '…', True, (30, 30, 30))
                    screen.blit(ing_text, (ing_rect.x + 5, ing_rect.y + ing_rect.height // 2 - ing_text.get_height() // 2))
                    ing_x += ing_rect.width + 8
                # Стрелка
                arrow_font = pygame.font.SysFont(None, 36)
                arrow = arrow_font.render("→", True, (255, 255, 255))
                screen.blit(arrow, (ing_x + 2, y + 20 - arrow.get_height() // 2))
                # Результат
                res_rect = pygame.Rect(ing_x + 40, y + 12, 140, 32)
                pygame.draw.rect(screen, (80, 120, 200), res_rect, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), res_rect, 2, border_radius=8)
                res_text = item_font.render(recipe['result'], True, (30, 30, 30))
                # Обрезка текста если не помещается
                max_res_w = res_rect.width - 10
                res_disp = recipe['result']
                while res_text.get_width() > max_res_w and len(res_disp) > 2:
                    res_disp = res_disp[:-1]
                    res_text = item_font.render(res_disp + '…', True, (30, 30, 30))
                screen.blit(res_text, (res_rect.x + 5, res_rect.y + res_rect.height // 2 - res_text.get_height() // 2))
                # Кнопка крафта
                can_craft = all(inventory.count(ing) > 0 for ing in recipe['ingredients'])
                btn_rect = pygame.Rect(recipe_block.right - 130, y + recipe_h - 44, 110, 36)
                pygame.draw.rect(screen, (80, 180, 80) if can_craft else (120, 120, 120), btn_rect, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2, border_radius=8)
                btn_text = btn_font.render("Сделать" if can_craft else "Нет ингредиентов", True, (255, 255, 255))
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))
                craft_btns.append((btn_rect, recipe, can_craft))
            # Подсказка
            hint_font = pygame.font.SysFont(None, 22)
            hint = hint_font.render("Кликните 'Сделать', чтобы скрафтить. Ингредиенты подсвечены зелёным, если есть, и красным, если нет.", True, (200, 200, 200))
            screen.blit(hint, (craft_rect.x + 30, craft_rect.bottom - 80))
            # Кнопка назад
            back_rect = pygame.Rect(craft_rect.x + 20, craft_rect.bottom - 50, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (180, 120, 60), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                # Крафт
                for btn_rect, recipe, can_craft in craft_btns:
                    if btn_rect.collidepoint(mx, my) and can_craft:
                        for ing in recipe['ingredients']:
                            inventory.remove(ing)
                        if len(inventory) < 12:
                            inventory.append(recipe['result'])
                # Назад
                if back_rect.collidepoint(mx, my):
                    state = 'game'
            pygame.display.flip()
            continue

        elif state == 'dealer':
            # Окно дилера
            dealer_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), dealer_rect, border_radius=18)
            pygame.draw.rect(screen, (80, 180, 80), dealer_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Дилер — скупка краденого", True, (255, 255, 255))
            screen.blit(title, (dealer_rect.centerx - title.get_width() // 2, dealer_rect.y + 18))
            # Список краденых предметов
            item_font = pygame.font.SysFont(None, 28)
            btn_font = pygame.font.SysFont(None, 24)
            sell_btns = []
            # Только предметы, которые можно продать дилеру
            stolen_items = [
                ("Кольцо", 120),
                ("Ожерелье", 200),
                ("Часы", 160),
                ("Слиток", 300),
                ("Деньги", 180),
                ("Сейф", 400),
                ("Тележка", 60),
                ("Касса", 90),
                ("Колбаса", 30),
                ("Телевизор", 150),
                ("Камера", 110),
                ("Ноутбук", 220),
                ("Наркотик", 250),
                ("Капсулы с наркотиком", 320),
                ("Компьютер", 200),
                ("Стиральная машина", 180),
                ("Золотые часы", 180),
                ("Украшения", 220),
                # Новые наркотики в пакетиках
                ("Порошок в пакетике", 325),
                ("Трава в пакетике", 325),
                ("Экстракт в пакетике", 415),
                ("Машинное масло", 60),
                ("Бензин в канистрах", 90),
                ("Деньги из кассы", 120),
            ]
            y_offset = 0
            for item_name, price in stolen_items:
                if item_name in inventory:
                    y = dealer_rect.y + 70 + y_offset * 40
                    y_offset += 1
                    item_text = item_font.render(item_name, True, (220, 220, 220))
                    price_text = item_font.render(f"{price}€", True, (80, 255, 80))
                    screen.blit(item_text, (dealer_rect.x + 30, y))
                    screen.blit(price_text, (dealer_rect.x + 320, y))
                    btn_rect = pygame.Rect(dealer_rect.right - 120, y - 4, 90, 28)
                    pygame.draw.rect(screen, (20, 30, 20), btn_rect, border_radius=8)
                    pygame.draw.rect(screen, (80, 180, 80), btn_rect, 2, border_radius=8)
                    btn_text = btn_font.render("Продать", True, (255, 255, 255))
                    screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))
                    sell_btns.append((btn_rect, item_name, price))
            # Кнопка назад
            back_rect = pygame.Rect(dealer_rect.x + 20, dealer_rect.bottom - 50, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (80, 180, 80), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                # Продать
                for btn_rect, item_name, price in sell_btns:
                    if btn_rect.collidepoint(mx, my):
                        if item_name in inventory:
                            inventory.remove(item_name)
                            money += price
                # Назад
                if back_rect.collidepoint(mx, my):
                    state = 'game'
            pygame.display.flip()
            continue

        elif state == 'heist_jewelry':
            global heist_jewelry_data
            import time
            # --- Мини-игра: ограбление ювелирки ---
            heist_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), heist_rect, border_radius=18)
            pygame.draw.rect(screen, (180, 180, 220), heist_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 38).render("Ограбление ювелирки", True, (255, 255, 255))
            screen.blit(title, (heist_rect.centerx - title.get_width() // 2, heist_rect.y + 12))
            # Игровое поле
            field_rect = pygame.Rect(heist_rect.x + 40, heist_rect.y + 60, 560, 320)
            pygame.draw.rect(screen, (50, 50, 70), field_rect, border_radius=10)
            # --- Инициализация мини-игры ---
            if heist_jewelry_data is None:
                random.seed(time.time())
                # Рандомные предметы
                item_names = ["Кольцо", "Ожерелье", "Часы"]
                items = []
                for name in item_names:
                    while True:
                        x = random.randint(field_rect.x + 30, field_rect.right - 50)
                        y = random.randint(field_rect.y + 30, field_rect.bottom - 50)
                        overlap = False
                        for it in items:
                            if abs(x - it['x']) < 40 and abs(y - it['y']) < 40:
                                overlap = True
                                break
                        if not overlap:
                            break
                    items.append({'x': x, 'y': y, 'w': 22, 'h': 22, 'taken': False, 'name': name})
                heist_jewelry_data = {
                    'player': {'x': field_rect.x + 20, 'y': field_rect.y + field_rect.height - 40, 'w': 28, 'h': 28, 'vx': 0, 'vy': 0},
                    'items': items,
                    'fail': False,
                    'win': False,
                    'bullets': [],
                    'bullet_timer': 0
                }
            player = heist_jewelry_data['player']
            items = heist_jewelry_data['items']
            bullets = heist_jewelry_data['bullets']
            # Управление: плавное движение при удержании WASD
            keys = pygame.key.get_pressed()
            speed = 4
            player['vx'] = 0
            player['vy'] = 0
            if keys[pygame.K_a]:
                player['vx'] = -speed
            if keys[pygame.K_d]:
                player['vx'] = speed
            if keys[pygame.K_w]:
                player['vy'] = -speed
            if keys[pygame.K_s]:
                player['vy'] = speed
            player['x'] += player['vx']
            player['y'] += player['vy']
            # Границы поля
            player['x'] = max(field_rect.x, min(field_rect.x + field_rect.width - player['w'], player['x']))
            player['y'] = max(field_rect.y, min(field_rect.y + field_rect.height - player['h'], player['y']))
            # --- Пули ---
            heist_jewelry_data['bullet_timer'] += 1
            if heist_jewelry_data['bullet_timer'] >= 60:  # Каждую секунду
                heist_jewelry_data['bullet_timer'] = 0
                for _ in range(random.randint(3, 5)):
                    corner = random.choice([0, 1, 2, 3])
                    if corner == 0:
                        x, y = field_rect.x, field_rect.y
                    elif corner == 1:
                        x, y = field_rect.right, field_rect.y
                    elif corner == 2:
                        x, y = field_rect.x, field_rect.bottom
                    else:
                        x, y = field_rect.right, field_rect.bottom
                    # Центр поля
                    cx = field_rect.x + field_rect.width // 2
                    cy = field_rect.y + field_rect.height // 2
                    # Немного рандома в цель
                    cx += random.randint(-40, 40)
                    cy += random.randint(-40, 40)
                    dx = cx - x
                    dy = cy - y
                    length = math.hypot(dx, dy)
                    if length == 0:
                        length = 1
                    speed = random.uniform(4, 7)
                    dx = dx / length * speed
                    dy = dy / length * speed
                    bullets.append({'x': x, 'y': y, 'dx': dx, 'dy': dy, 'lifetime': 120})
            # Обновление и отрисовка пуль
            new_bullets = []
            for b in bullets:
                # Хаотичное движение: немного меняем направление каждый кадр
                b['dx'] += random.uniform(-0.5, 0.5)
                b['dy'] += random.uniform(-0.5, 0.5)
                # Ограничим максимальную скорость
                speed = math.hypot(b['dx'], b['dy'])
                max_speed = 7
                if speed > max_speed:
                    b['dx'] = b['dx'] / speed * max_speed
                    b['dy'] = b['dy'] / speed * max_speed
                b['x'] += b['dx']
                b['y'] += b['dy']
                b['lifetime'] -= 1
                if field_rect.x - 20 < b['x'] < field_rect.right + 20 and field_rect.y - 20 < b['y'] < field_rect.bottom + 20 and b['lifetime'] > 0:
                    new_bullets.append(b)
                # Рисуем пулю как красную палочку
                pygame.draw.rect(screen, (255, 40, 40), (int(b['x']), int(b['y']), 12, 4))
            heist_jewelry_data['bullets'] = new_bullets
            # Проверка столкновения с пулей
            player_rect = pygame.Rect(int(player['x']), int(player['y']), player['w'], player['h'])
            # Рисуем игрока поверх пуль
            pygame.draw.rect(screen, (0, 0, 0), player_rect)
            for b in new_bullets:
                bullet_rect = pygame.Rect(int(b['x']), int(b['y']), 12, 4)
                if player_rect.colliderect(bullet_rect):
                    heist_jewelry_data['fail'] = True
            # Предметы
            for item in items:
                if not item['taken']:
                    item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])
                    pygame.draw.rect(screen, (255, 215, 80), item_rect, border_radius=6)
                    icon = pygame.font.SysFont(None, 18).render(item['name'][0], True, (80, 60, 0))
                    screen.blit(icon, (item['x'] + 5, item['y'] + 2))
                    if player_rect.colliderect(item_rect):
                        item['taken'] = True
            # Победа
            if all(item['taken'] for item in items):
                heist_jewelry_data['win'] = True
            # Сообщения о победе/проигрыше
            msg_font = pygame.font.SysFont(None, 32)
            if heist_jewelry_data['fail']:
                msg = msg_font.render("Поймали! Нажмите ESC", True, (255, 80, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            elif heist_jewelry_data['win']:
                msg = msg_font.render("Успех! Нажмите ESC", True, (80, 255, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            # Кнопка ESC — выход
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if heist_jewelry_data is not None and heist_jewelry_data['win']:
                        # Добавить предметы в инвентарь
                        for item in heist_jewelry_data['items']:
                            if item['name'] not in inventory and len(inventory) < 12:
                                inventory.append(item['name'])
                    elif heist_jewelry_data is not None and heist_jewelry_data['fail']:
                        wanted += 1
                    heist_jewelry_data = None
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'heist_bank':
            global heist_bank_data
            import time
            heist_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), heist_rect, border_radius=18)
            pygame.draw.rect(screen, (180, 220, 180), heist_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 38).render("Ограбление банка", True, (255, 255, 255))
            screen.blit(title, (heist_rect.centerx - title.get_width() // 2, heist_rect.y + 12))
            field_rect = pygame.Rect(heist_rect.x + 40, heist_rect.y + 60, 560, 320)
            pygame.draw.rect(screen, (50, 50, 70), field_rect, border_radius=10)
            if 'heist_bank_data' not in globals() or heist_bank_data is None:
                random.seed(time.time())
                items = []
                for name in ["Слиток", "Деньги", "Сейф"]:
                    while True:
                        x = random.randint(field_rect.x + 30, field_rect.right - 50)
                        y = random.randint(field_rect.y + 30, field_rect.bottom - 50)
                        overlap = False
                        for it in items:
                            if abs(x - it['x']) < 40 and abs(y - it['y']) < 40:
                                overlap = True
                                break
                        if not overlap:
                            break
                    items.append({'x': x, 'y': y, 'w': 22, 'h': 22, 'taken': False, 'name': name})
                # Лазеры мигают
                lasers = []
                for _ in range(3):
                    y = random.randint(field_rect.y + 60, field_rect.bottom - 60)
                    lasers.append({'x1': field_rect.x + 40, 'y1': y, 'x2': field_rect.right - 40, 'y2': y, 'on': True, 'timer': random.randint(30, 90)})
                heist_bank_data = {
                    'player': {'x': field_rect.x + 20, 'y': field_rect.y + field_rect.height - 40, 'w': 28, 'h': 28, 'vx': 0, 'vy': 0},
                    'items': items,
                    'lasers': lasers,
                    'fail': False,
                    'win': False
                }
            player = heist_bank_data['player']
            items = heist_bank_data['items']
            lasers = heist_bank_data['lasers']
            # Управление
            keys = pygame.key.get_pressed()
            speed = 4
            player['vx'] = 0
            player['vy'] = 0
            if keys[pygame.K_a]:
                player['vx'] = -speed
            if keys[pygame.K_d]:
                player['vx'] = speed
            if keys[pygame.K_w]:
                player['vy'] = -speed
            if keys[pygame.K_s]:
                player['vy'] = speed
            player['x'] += player['vx']
            player['y'] += player['vy']
            player['x'] = max(field_rect.x, min(field_rect.x + field_rect.width - player['w'], player['x']))
            player['y'] = max(field_rect.y, min(field_rect.y + field_rect.height - player['h'], player['y']))
            # Лазеры мигают
            for laser in lasers:
                laser['timer'] -= 1
                if laser['timer'] <= 0:
                    laser['on'] = not laser['on']
                    laser['timer'] = random.randint(30, 90)
                if laser['on']:
                    pygame.draw.line(screen, (255, 40, 40), (laser['x1'], laser['y1']), (laser['x2'], laser['y2']), 6)
            player_rect = pygame.Rect(int(player['x']), int(player['y']), player['w'], player['h'])
            pygame.draw.rect(screen, (0, 0, 0), player_rect)
            for laser in lasers:
                if laser['on']:
                    laser_rect = pygame.Rect(min(laser['x1'], laser['x2']), int(laser['y1']) - 3, abs(laser['x2'] - laser['x1']), 6)
                    if player_rect.colliderect(laser_rect):
                        heist_bank_data['fail'] = True
            for item in items:
                if not item['taken']:
                    item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])
                    pygame.draw.rect(screen, (255, 215, 80), item_rect, border_radius=6)
                    icon = pygame.font.SysFont(None, 18).render(item['name'][0], True, (80, 60, 0))
                    screen.blit(icon, (item['x'] + 5, item['y'] + 2))
                    if player_rect.colliderect(item_rect):
                        item['taken'] = True
            if all(item['taken'] for item in items):
                heist_bank_data['win'] = True
            msg_font = pygame.font.SysFont(None, 32)
            if heist_bank_data['fail']:
                msg = msg_font.render("Поймали! Нажмите ESC", True, (255, 80, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            elif heist_bank_data['win']:
                msg = msg_font.render("Успех! Нажмите ESC", True, (80, 255, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if heist_bank_data is not None and heist_bank_data['win']:
                        for item in heist_bank_data['items']:
                            if item['name'] not in inventory and len(inventory) < 12:
                                inventory.append(item['name'])
                    elif heist_bank_data is not None and heist_bank_data['fail']:
                        wanted += 1
                    heist_bank_data = None
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'heist_supermarket':
            global heist_supermarket_data
            import time
            heist_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), heist_rect, border_radius=18)
            pygame.draw.rect(screen, (80, 180, 220), heist_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 38).render("Ограбление супермаркета", True, (255, 255, 255))
            screen.blit(title, (heist_rect.centerx - title.get_width() // 2, heist_rect.y + 12))
            field_rect = pygame.Rect(heist_rect.x + 40, heist_rect.y + 60, 560, 320)
            pygame.draw.rect(screen, (50, 50, 70), field_rect, border_radius=10)
            if 'heist_supermarket_data' not in globals() or heist_supermarket_data is None:
                random.seed(time.time())
                items = []
                for name in ["Тележка", "Касса", "Колбаса"]:
                    while True:
                        x = random.randint(field_rect.x + 30, field_rect.right - 50)
                        y = random.randint(field_rect.y + 30, field_rect.bottom - 50)
                        overlap = False
                        for it in items:
                            if abs(x - it['x']) < 40 and abs(y - it['y']) < 40:
                                overlap = True
                                break
                        if not overlap:
                            break
                    items.append({'x': x, 'y': y, 'w': 22, 'h': 22, 'taken': False, 'name': name})
                # Охранники с треугольным полем зрения
                guards = []
                for _ in range(2):
                    gx = random.randint(field_rect.x + 60, field_rect.right - 60)
                    gy = random.randint(field_rect.y + 60, field_rect.bottom - 60)
                    angle = random.uniform(0, 2 * math.pi)
                    guards.append({'x': gx, 'y': gy, 'w': 32, 'h': 32, 'angle': angle, 'turn_timer': random.randint(30, 90), 'move_timer': random.randint(20, 60), 'dx': 0, 'dy': 0})
                heist_supermarket_data = {
                    'player': {'x': field_rect.x + 20, 'y': field_rect.y + field_rect.height - 40, 'w': 28, 'h': 28, 'vx': 0, 'vy': 0},
                    'items': items,
                    'guards': guards,
                    'fail': False,
                    'win': False
                }
            player = heist_supermarket_data['player']
            items = heist_supermarket_data['items']
            guards = heist_supermarket_data['guards']
            keys = pygame.key.get_pressed()
            speed = 4
            player['vx'] = 0
            player['vy'] = 0
            if keys[pygame.K_a]:
                player['vx'] = -speed
            if keys[pygame.K_d]:
                player['vx'] = speed
            if keys[pygame.K_w]:
                player['vy'] = -speed
            if keys[pygame.K_s]:
                player['vy'] = speed
            player['x'] += player['vx']
            player['y'] += player['vy']
            player['x'] = max(field_rect.x, min(field_rect.x + field_rect.width - player['w'], player['x']))
            player['y'] = max(field_rect.y, min(field_rect.y + field_rect.height - player['h'], player['y']))
            # Охранники: движение и хаотичное поведение
            for guard in guards:
                guard['move_timer'] -= 1
                guard['turn_timer'] -= 1
                if guard['move_timer'] <= 0:
                    angle = random.uniform(0, 2 * math.pi)
                    guard['dx'] = math.cos(angle) * random.uniform(1, 2)
                    guard['dy'] = math.sin(angle) * random.uniform(1, 2)
                    guard['move_timer'] = random.randint(20, 60)
                guard['x'] += guard['dx']
                guard['y'] += guard['dy']
                # Границы
                if guard['x'] < field_rect.x + 20 or guard['x'] > field_rect.right - guard['w'] - 20:
                    guard['dx'] *= -1
                    guard['x'] = max(field_rect.x + 20, min(field_rect.right - guard['w'] - 20, guard['x']))
                if guard['y'] < field_rect.y + 20 or guard['y'] > field_rect.bottom - guard['h'] - 20:
                    guard['dy'] *= -1
                    guard['y'] = max(field_rect.y + 20, min(field_rect.bottom - guard['h'] - 20, guard['y']))
                if guard['turn_timer'] <= 0:
                    guard['angle'] = random.uniform(0, 2 * math.pi)
                    guard['turn_timer'] = random.randint(30, 90)
                # Рисуем охранника
                guard_rect = pygame.Rect(int(guard['x']), int(guard['y']), guard['w'], guard['h'])
                pygame.draw.rect(screen, (80, 180, 80), guard_rect)
                # Рисуем треугольное поле зрения
                vision_len = 120
                vision_angle = math.radians(40)
                a = guard['angle']
                p1 = (guard['x'] + guard['w']//2, guard['y'] + guard['h']//2)
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                pygame.draw.polygon(screen, (255, 255, 80, 80), [p1, p2, p3])
            player_rect = pygame.Rect(int(player['x']), int(player['y']), player['w'], player['h'])
            pygame.draw.rect(screen, (0, 0, 0), player_rect)
            # Проверка попадания в поле зрения охранников
            for guard in guards:
                a = guard['angle']
                p1 = (guard['x'] + guard['w']//2, guard['y'] + guard['h']//2)
                vision_len = 120
                vision_angle = math.radians(40)
                # Проверяем, попал ли центр игрока в треугольник зрения
                px, py = player_rect.centerx, player_rect.centery
                def point_in_triangle(pt, v1, v2, v3):
                    def sign(p1, p2, p3):
                        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
                    b1 = sign(pt, v1, v2) < 0.0
                    b2 = sign(pt, v2, v3) < 0.0
                    b3 = sign(pt, v3, v1) < 0.0
                    return ((b1 == b2) and (b2 == b3))
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                if point_in_triangle((px, py), p1, p2, p3):
                    heist_supermarket_data['fail'] = True
            for item in items:
                if not item['taken']:
                    item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])
                    pygame.draw.rect(screen, (255, 215, 80), item_rect, border_radius=6)
                    icon = pygame.font.SysFont(None, 18).render(item['name'][0], True, (80, 60, 0))
                    screen.blit(icon, (item['x'] + 5, item['y'] + 2))
                    if player_rect.colliderect(item_rect):
                        item['taken'] = True
            if all(item['taken'] for item in items):
                heist_supermarket_data['win'] = True
            msg_font = pygame.font.SysFont(None, 32)
            if heist_supermarket_data['fail']:
                msg = msg_font.render("Поймали! Нажмите ESC", True, (255, 80, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            elif heist_supermarket_data['win']:
                msg = msg_font.render("Успех! Нажмите ESC", True, (80, 255, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if heist_supermarket_data is not None and heist_supermarket_data['win']:
                        for item in heist_supermarket_data['items']:
                            if item['name'] not in inventory and len(inventory) < 12:
                                inventory.append(item['name'])
                    elif heist_supermarket_data is not None and heist_supermarket_data['fail']:
                        wanted += 1
                    heist_supermarket_data = None
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'heist_lombard':
            global heist_lombard_data
            import time
            heist_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), heist_rect, border_radius=18)
            pygame.draw.rect(screen, (220, 180, 80), heist_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 38).render("Ограбление ломбарда", True, (255, 255, 255))
            screen.blit(title, (heist_rect.centerx - title.get_width() // 2, heist_rect.y + 12))
            field_rect = pygame.Rect(heist_rect.x + 40, heist_rect.y + 60, 560, 320)
            pygame.draw.rect(screen, (50, 50, 70), field_rect, border_radius=10)
            if 'heist_lombard_data' not in globals() or heist_lombard_data is None:
                random.seed(time.time())
                items = []
                for name in ["Золотые часы", "Украшения", "Сейф"]:
                    while True:
                        x = random.randint(field_rect.x + 30, field_rect.right - 50)
                        y = random.randint(field_rect.y + 30, field_rect.bottom - 50)
                        overlap = False
                        for it in items:
                            if abs(x - it['x']) < 40 and abs(y - it['y']) < 40:
                                overlap = True
                                break
                        if not overlap:
                            break
                    items.append({'x': x, 'y': y, 'w': 22, 'h': 22, 'taken': False, 'name': name})
                # Охранники с треугольным полем зрения
                guards = []
                for _ in range(2):
                    gx = random.randint(field_rect.x + 60, field_rect.right - 60)
                    gy = random.randint(field_rect.y + 60, field_rect.bottom - 60)
                    angle = random.uniform(0, 2 * math.pi)
                    guards.append({'x': gx, 'y': gy, 'w': 32, 'h': 32, 'angle': angle, 'turn_timer': random.randint(30, 90), 'move_timer': random.randint(20, 60), 'dx': 0, 'dy': 0})
                heist_lombard_data = {
                    'player': {'x': field_rect.x + 20, 'y': field_rect.y + field_rect.height - 40, 'w': 28, 'h': 28, 'vx': 0, 'vy': 0},
                    'items': items,
                    'guards': guards,
                    'fail': False,
                    'win': False
                }
            player = heist_lombard_data['player']
            items = heist_lombard_data['items']
            guards = heist_lombard_data['guards']
            keys = pygame.key.get_pressed()
            speed = 4
            player['vx'] = 0
            player['vy'] = 0
            if keys[pygame.K_a]:
                player['vx'] = -speed
            if keys[pygame.K_d]:
                player['vx'] = speed
            if keys[pygame.K_w]:
                player['vy'] = -speed
            if keys[pygame.K_s]:
                player['vy'] = speed
            player['x'] += player['vx']
            player['y'] += player['vy']
            # Границы поля
            player['x'] = max(field_rect.x, min(field_rect.x + field_rect.width - player['w'], player['x']))
            player['y'] = max(field_rect.y, min(field_rect.y + field_rect.height - player['h'], player['y']))
            # Охранники двигаются и поворачиваются
            for guard in guards:
                guard['move_timer'] -= 1
                if guard['move_timer'] <= 0:
                    guard['dx'] = random.choice([-1, 0, 1]) * 2
                    guard['dy'] = random.choice([-1, 0, 1]) * 2
                    guard['move_timer'] = random.randint(20, 60)
                guard['x'] += guard['dx']
                guard['y'] += guard['dy']
                guard['x'] = max(field_rect.x, min(field_rect.right - guard['w'], guard['x']))
                guard['y'] = max(field_rect.y, min(field_rect.bottom - guard['h'], guard['y']))
                guard['turn_timer'] -= 1
                if guard['turn_timer'] <= 0:
                    guard['angle'] = random.uniform(0, 2 * math.pi)
                    guard['turn_timer'] = random.randint(30, 90)
            # Рисуем охранников и их поле зрения
            for guard in guards:
                guard_rect = pygame.Rect(int(guard['x']), int(guard['y']), guard['w'], guard['h'])
                pygame.draw.rect(screen, (180, 180, 80), guard_rect)
                # Треугольное поле зрения
                vision_len = 120
                vision_angle = math.radians(40)
                a = guard['angle']
                p1 = (guard['x'] + guard['w']//2, guard['y'] + guard['h']//2)
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                pygame.draw.polygon(screen, (255, 255, 80, 80), [p1, p2, p3])
            player_rect = pygame.Rect(int(player['x']), int(player['y']), player['w'], player['h'])
            pygame.draw.rect(screen, (0, 0, 0), player_rect)
            # Проверка попадания в поле зрения охранников
            for guard in guards:
                a = guard['angle']
                p1 = (guard['x'] + guard['w']//2, guard['y'] + guard['h']//2)
                vision_len = 120
                vision_angle = math.radians(40)
                px, py = player_rect.centerx, player_rect.centery
                def point_in_triangle(pt, v1, v2, v3):
                    def sign(p1, p2, p3):
                        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
                    b1 = sign(pt, v1, v2) < 0.0
                    b2 = sign(pt, v2, v3) < 0.0
                    b3 = sign(pt, v3, v1) < 0.0
                    return ((b1 == b2) and (b2 == b3))
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                if point_in_triangle((px, py), p1, p2, p3):
                    heist_lombard_data['fail'] = True
            # Предметы
            for item in items:
                if not item['taken']:
                    item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])
                    pygame.draw.rect(screen, (255, 215, 80), item_rect, border_radius=6)
                    icon = pygame.font.SysFont(None, 18).render(item['name'][0], True, (80, 60, 0))
                    screen.blit(icon, (item['x'] + 5, item['y'] + 2))
                    if player_rect.colliderect(item_rect):
                        item['taken'] = True
            if all(item['taken'] for item in items):
                heist_lombard_data['win'] = True
            msg_font = pygame.font.SysFont(None, 32)
            if heist_lombard_data['fail']:
                msg = msg_font.render("Поймали! Нажмите ESC", True, (255, 80, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            elif heist_lombard_data['win']:
                msg = msg_font.render("Успех! Нажмите ESC", True, (80, 255, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if heist_lombard_data is not None and heist_lombard_data['win']:
                        for item in heist_lombard_data['items']:
                            if item['name'] not in inventory and len(inventory) < 12:
                                inventory.append(item['name'])
                    elif heist_lombard_data is not None and heist_lombard_data['fail']:
                        wanted += 1
                    heist_lombard_data = None
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'clothes_shop':
            # Новый устойчивый магазин одежды без использования global и локальных money/wanted
            shop_rect = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 120, 520, 240)
            pygame.draw.rect(screen, (40, 40, 60), shop_rect, border_radius=18)
            pygame.draw.rect(screen, (120, 120, 180), shop_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Магазин одежды", True, (255, 255, 255))
            screen.blit(title, (shop_rect.centerx - title.get_width() // 2, shop_rect.y + 18))
            info_font = pygame.font.SysFont(None, 28)
            info = info_font.render("Смена имиджа поможет снизить розыск!", True, (200, 200, 255))
            screen.blit(info, (shop_rect.centerx - info.get_width() // 2, shop_rect.y + 70))
            btn_font = pygame.font.SysFont(None, 32)
            btn_rect = pygame.Rect(shop_rect.centerx - 120, shop_rect.y + 120, 240, 54)
            can_change = globals()['wanted'] > 0 and globals()['money'] >= 1500
            pygame.draw.rect(screen, (80, 180, 80) if can_change else (120, 120, 120), btn_rect, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2, border_radius=12)
            btn_text = btn_font.render("Сменить имидж (1500€)", True, (255, 255, 255))
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))
            # Кнопка назад
            back_rect = pygame.Rect(shop_rect.x + 20, shop_rect.bottom - 50, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 120, 180), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                if can_change and btn_rect.collidepoint(mx, my):
                    globals()['money'] -= 1500
                    globals()['wanted'] -= 1
                if back_rect.collidepoint(mx, my):
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'wanted_game_over':
            screen.fill((30, 10, 10))
            over_font = pygame.font.SysFont(None, 60)
            msg_font = pygame.font.SysFont(None, 36)
            over_text = over_font.render("Вас поймали!", True, (255, 80, 80))
            info_text = msg_font.render("Игра окончена. Нажмите любую клавишу для выхода в меню.", True, (255, 255, 255))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 10))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    # Сбросить розыск и вернуться в меню
                    globals()['wanted'] = 0
                    globals()['game_over'] = False
                    state = 'menu'
            pygame.display.flip()
            continue

        elif state == 'travel_payment':
            # Окно оплаты поездки
            travel_rect = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 120, 520, 240)
            pygame.draw.rect(screen, (30, 30, 50), travel_rect, border_radius=18)
            pygame.draw.rect(screen, (80, 180, 220), travel_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Оплата поездки", True, (255, 255, 255))
            screen.blit(title, (travel_rect.centerx - title.get_width() // 2, travel_rect.y + 18))
            # Текст: способ и цена
            pay_font = pygame.font.SysFont(None, 32)
            method = globals().get('travel_method', 'Такси')
            price = globals().get('travel_price', 0)
            dest = globals().get('travel_dest', '???')
            info_text = pay_font.render(f"{method} до '{dest}' — {price}€", True, (255, 255, 255))
            screen.blit(info_text, (travel_rect.centerx - info_text.get_width() // 2, travel_rect.y + 70))
            # Кнопки
            btn_font = pygame.font.SysFont(None, 28)
            pay_btn = pygame.Rect(travel_rect.centerx - 110, travel_rect.bottom - 60, 100, 40)
            cancel_btn = pygame.Rect(travel_rect.centerx + 10, travel_rect.bottom - 60, 100, 40)
            can_pay = money >= price
            pygame.draw.rect(screen, (80, 180, 80) if can_pay else (120, 120, 120), pay_btn, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), pay_btn, 2, border_radius=10)
            pay_text = btn_font.render("Оплатить", True, (255, 255, 255))
            screen.blit(pay_text, (pay_btn.centerx - pay_text.get_width() // 2, pay_btn.centery - pay_text.get_height() // 2))
            pygame.draw.rect(screen, (180, 80, 80), cancel_btn, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), cancel_btn, 2, border_radius=10)
            cancel_text = btn_font.render("Отмена", True, (255, 255, 255))
            screen.blit(cancel_text, (cancel_btn.centerx - cancel_text.get_width() // 2, cancel_btn.centery - cancel_text.get_height() // 2))
            # Сообщение если не хватает денег
            if not can_pay:
                warn_font = pygame.font.SysFont(None, 26)
                warn = warn_font.render("Недостаточно денег!", True, (255, 80, 80))
                screen.blit(warn, (travel_rect.centerx - warn.get_width() // 2, travel_rect.y + 120))
            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            global travel_btn_last_click
            if 'travel_btn_last_click' not in globals():
                travel_btn_last_click = False
            if mouse[0]:
                if pay_btn.collidepoint(mx, my) and can_pay:
                    globals()['money'] -= price
                    # Переход на выбранную локацию
                    state = globals().get('travel_next_state', 'game')
                    # Сбросить параметры
                    globals()['travel_price'] = 0
                    globals()['travel_dest'] = ''
                    globals()['travel_next_state'] = 'game'
                elif cancel_btn.collidepoint(mx, my):
                    state = 'navigator'
                    globals()['travel_price'] = 0
                    globals()['travel_dest'] = ''
                    globals()['travel_next_state'] = 'game'
            pygame.display.flip()
            continue

        # Голод уменьшается каждые 5 секунд
        if 'last_hunger_tick' not in globals():
            last_hunger_tick = pygame.time.get_ticks()
        if pygame.time.get_ticks() - last_hunger_tick > 5000:
            hunger -= 1
            last_hunger_tick = pygame.time.get_ticks()
        if hunger <= 0:
            game_over = True
            state = 'wanted_game_over'

        elif state == 'heist_electronics':
            global heist_electronics_data
            import time
            heist_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), heist_rect, border_radius=18)
            pygame.draw.rect(screen, (80, 180, 220), heist_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 38).render("Ограбление магазина техники", True, (255, 255, 255))
            screen.blit(title, (heist_rect.centerx - title.get_width() // 2, heist_rect.y + 12))
            field_rect = pygame.Rect(heist_rect.x + 40, heist_rect.y + 60, 560, 320)
            pygame.draw.rect(screen, (50, 50, 70), field_rect, border_radius=10)
            if 'heist_electronics_data' not in globals() or heist_electronics_data is None:
                random.seed(time.time())
                items = []
                for name in ["Телевизор", "Компьютер", "Стиральная машина"]:
                    while True:
                        x = random.randint(field_rect.x + 30, field_rect.right - 50)
                        y = random.randint(field_rect.y + 30, field_rect.bottom - 50)
                        overlap = False
                        for it in items:
                            if abs(x - it['x']) < 40 and abs(y - it['y']) < 40:
                                overlap = True
                                break
                        if not overlap:
                            break
                    items.append({'x': x, 'y': y, 'w': 28, 'h': 28, 'taken': False, 'name': name})
                # Охранники с треугольным полем зрения
                guards = []
                for _ in range(2):
                    gx = random.randint(field_rect.x + 60, field_rect.right - 60)
                    gy = random.randint(field_rect.y + 60, field_rect.bottom - 60)
                    angle = random.uniform(0, 2 * math.pi)
                    guards.append({'x': gx, 'y': gy, 'w': 32, 'h': 32, 'angle': angle, 'turn_timer': random.randint(30, 90), 'move_timer': random.randint(20, 60), 'dx': 0, 'dy': 0})
                heist_electronics_data = {
                    'player': {'x': field_rect.x + 20, 'y': field_rect.y + field_rect.height - 40, 'w': 28, 'h': 28, 'vx': 0, 'vy': 0},
                    'items': items,
                    'guards': guards,
                    'fail': False,
                    'win': False
                }
            player = heist_electronics_data['player']
            items = heist_electronics_data['items']
            guards = heist_electronics_data['guards']
            keys = pygame.key.get_pressed()
            speed = 4
            player['vx'] = 0
            player['vy'] = 0
            if keys[pygame.K_a]:
                player['vx'] = -speed
            if keys[pygame.K_d]:
                player['vx'] = speed
            if keys[pygame.K_w]:
                player['vy'] = -speed
            if keys[pygame.K_s]:
                player['vy'] = speed
            player['x'] += player['vx']
            player['y'] += player['vy']
            # Границы поля
            player['x'] = max(field_rect.x, min(field_rect.x + field_rect.width - player['w'], player['x']))
            player['y'] = max(field_rect.y, min(field_rect.y + field_rect.height - player['h'], player['y']))
            # Охранники двигаются и поворачиваются
            for guard in guards:
                guard['move_timer'] -= 1
                if guard['move_timer'] <= 0:
                    guard['dx'] = random.choice([-1, 0, 1]) * 2
                    guard['dy'] = random.choice([-1, 0, 1]) * 2
                    guard['move_timer'] = random.randint(20, 60)
                guard['x'] += guard['dx']
                guard['y'] += guard['dy']
                guard['x'] = max(field_rect.x, min(field_rect.right - guard['w'], guard['x']))
                guard['y'] = max(field_rect.y, min(field_rect.bottom - guard['h'], guard['y']))
                guard['turn_timer'] -= 1
                if guard['turn_timer'] <= 0:
                    guard['angle'] = random.uniform(0, 2 * math.pi)
                    guard['turn_timer'] = random.randint(30, 90)
            # Рисуем охранников и их поле зрения
            for guard in guards:
                guard_rect = pygame.Rect(int(guard['x']), int(guard['y']), guard['w'], guard['h'])
                pygame.draw.rect(screen, (80, 180, 220), guard_rect)
                # Треугольное поле зрения
                vision_len = 120
                vision_angle = math.radians(40)
                a = guard['angle']
                p1 = (guard['x'] + guard['w']//2, guard['y'] + guard['h']//2)
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                pygame.draw.polygon(screen, (255, 255, 80, 80), [p1, p2, p3])
            player_rect = pygame.Rect(int(player['x']), int(player['y']), player['w'], player['h'])
            pygame.draw.rect(screen, (0, 0, 0), player_rect)
            # Проверка попадания в поле зрения охранников
            for guard in guards:
                a = guard['angle']
                p1 = (guard['x'] + guard['w']//2, guard['y'] + guard['h']//2)
                vision_len = 120
                vision_angle = math.radians(40)
                px, py = player_rect.centerx, player_rect.centery
                def point_in_triangle(pt, v1, v2, v3):
                    def sign(p1, p2, p3):
                        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
                    b1 = sign(pt, v1, v2) < 0.0
                    b2 = sign(pt, v2, v3) < 0.0
                    b3 = sign(pt, v3, v1) < 0.0
                    return ((b1 == b2) and (b2 == b3))
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                if point_in_triangle((px, py), p1, p2, p3):
                    heist_electronics_data['fail'] = True
            # Предметы
            for item in items:
                if not item['taken']:
                    item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])
                    pygame.draw.rect(screen, (255, 215, 80), item_rect, border_radius=6)
                    icon = pygame.font.SysFont(None, 18).render(item['name'][0], True, (80, 60, 0))
                    screen.blit(icon, (item['x'] + 5, item['y'] + 2))
                    if player_rect.colliderect(item_rect):
                        item['taken'] = True
            if all(item['taken'] for item in items):
                heist_electronics_data['win'] = True
            msg_font = pygame.font.SysFont(None, 32)
            if heist_electronics_data['fail']:
                msg = msg_font.render("Поймали! Нажмите ESC", True, (255, 80, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            elif heist_electronics_data['win']:
                msg = msg_font.render("Успех! Нажмите ESC", True, (80, 255, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if heist_electronics_data is not None and heist_electronics_data['win']:
                        for item in heist_electronics_data['items']:
                            if item['name'] not in inventory and len(inventory) < 12:
                                inventory.append(item['name'])
                    elif heist_electronics_data is not None and heist_electronics_data['fail']:
                        wanted += 1
                    heist_electronics_data = None
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'heist_gas_station':
            global heist_gas_station_data
            import time
            heist_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 220, 640, 440)
            pygame.draw.rect(screen, (30, 30, 40), heist_rect, border_radius=18)
            pygame.draw.rect(screen, (220, 220, 80), heist_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 38).render("Ограбление заправки", True, (255, 255, 255))
            screen.blit(title, (heist_rect.centerx - title.get_width() // 2, heist_rect.y + 12))
            field_rect = pygame.Rect(heist_rect.x + 40, heist_rect.y + 60, 560, 320)
            pygame.draw.rect(screen, (50, 50, 70), field_rect, border_radius=10)
            if 'heist_gas_station_data' not in globals() or heist_gas_station_data is None:
                random.seed(time.time())
                items = []
                for name in ["Машинное масло", "Бензин в канистрах", "Деньги из кассы"]:
                    while True:
                        x = random.randint(field_rect.x + 30, field_rect.right - 50)
                        y = random.randint(field_rect.y + 30, field_rect.bottom - 50)
                        overlap = False
                        for it in items:
                            if abs(x - it['x']) < 40 and abs(y - it['y']) < 40:
                                overlap = True
                                break
                        if not overlap:
                            break
                    items.append({'x': x, 'y': y, 'w': 28, 'h': 28, 'taken': False, 'name': name})
                # Камеры: вращаются влево-вправо треугольниками
                cameras = []
                for _ in range(3):
                    cx = random.randint(field_rect.x + 60, field_rect.right - 60)
                    cy = random.randint(field_rect.y + 60, field_rect.bottom - 60)
                    angle = random.uniform(-math.pi/3, math.pi/3)
                    direction = random.choice([-1, 1])
                    cameras.append({'x': cx, 'y': cy, 'angle': angle, 'dir': direction, 'timer': random.randint(40, 80)})
                heist_gas_station_data = {
                    'player': {'x': field_rect.x + 20, 'y': field_rect.y + field_rect.height - 40, 'w': 28, 'h': 28, 'vx': 0, 'vy': 0},
                    'items': items,
                    'cameras': cameras,
                    'fail': False,
                    'win': False
                }
            player = heist_gas_station_data['player']
            items = heist_gas_station_data['items']
            cameras = heist_gas_station_data['cameras']
            keys = pygame.key.get_pressed()
            speed = 4
            player['vx'] = 0
            player['vy'] = 0
            if keys[pygame.K_a]:
                player['vx'] = -speed
            if keys[pygame.K_d]:
                player['vx'] = speed
            if keys[pygame.K_w]:
                player['vy'] = -speed
            if keys[pygame.K_s]:
                player['vy'] = speed
            player['x'] += player['vx']
            player['y'] += player['vy']
            # Границы поля
            player['x'] = max(field_rect.x, min(field_rect.x + field_rect.width - player['w'], player['x']))
            player['y'] = max(field_rect.y, min(field_rect.y + field_rect.height - player['h'], player['y']))
            # Камеры вращаются
            for cam in cameras:
                cam['angle'] += cam['dir'] * 0.025
                if cam['angle'] > math.pi/3:
                    cam['angle'] = math.pi/3
                    cam['dir'] *= -1
                if cam['angle'] < -math.pi/3:
                    cam['angle'] = -math.pi/3
                    cam['dir'] *= -1
                # Рисуем камеру
                pygame.draw.circle(screen, (200, 200, 80), (int(cam['x']), int(cam['y'])), 12)
                # Рисуем треугольное поле зрения
                vision_len = 120
                vision_angle = math.radians(40)
                a = cam['angle']
                p1 = (cam['x'], cam['y'])
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                pygame.draw.polygon(screen, (255, 255, 80, 80), [p1, p2, p3])
            player_rect = pygame.Rect(int(player['x']), int(player['y']), player['w'], player['h'])
            pygame.draw.rect(screen, (0, 0, 0), player_rect)
            # Проверка попадания в поле зрения камер
            for cam in cameras:
                a = cam['angle']
                p1 = (cam['x'], cam['y'])
                vision_len = 120
                vision_angle = math.radians(40)
                px, py = player_rect.centerx, player_rect.centery
                def point_in_triangle(pt, v1, v2, v3):
                    def sign(p1, p2, p3):
                        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
                    b1 = sign(pt, v1, v2) < 0.0
                    b2 = sign(pt, v2, v3) < 0.0
                    b3 = sign(pt, v3, v1) < 0.0
                    return ((b1 == b2) and (b2 == b3))
                p2 = (p1[0] + vision_len * math.cos(a - vision_angle/2), p1[1] + vision_len * math.sin(a - vision_angle/2))
                p3 = (p1[0] + vision_len * math.cos(a + vision_angle/2), p1[1] + vision_len * math.sin(a + vision_angle/2))
                if point_in_triangle((px, py), p1, p2, p3):
                    heist_gas_station_data['fail'] = True
            # Предметы
            for item in items:
                if not item['taken']:
                    item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])
                    pygame.draw.rect(screen, (255, 215, 80), item_rect, border_radius=6)
                    icon = pygame.font.SysFont(None, 18).render(item['name'][0], True, (80, 60, 0))
                    screen.blit(icon, (item['x'] + 5, item['y'] + 2))
                    if player_rect.colliderect(item_rect):
                        item['taken'] = True
            if all(item['taken'] for item in items):
                heist_gas_station_data['win'] = True
            msg_font = pygame.font.SysFont(None, 32)
            if heist_gas_station_data['fail']:
                msg = msg_font.render("Поймали камерой! Нажмите ESC", True, (255, 80, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            elif heist_gas_station_data['win']:
                msg = msg_font.render("Успех! Нажмите ESC", True, (80, 255, 80))
                screen.blit(msg, (heist_rect.centerx - msg.get_width() // 2, heist_rect.bottom - 60))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if heist_gas_station_data is not None and heist_gas_station_data['win']:
                        for item in heist_gas_station_data['items']:
                            if item['name'] not in inventory and len(inventory) < 12:
                                inventory.append(item['name'])
                    elif heist_gas_station_data is not None and heist_gas_station_data['fail']:
                        wanted += 1
                    heist_gas_station_data = None
                    state = 'navigator'
            pygame.display.flip()
            continue

        elif state == 'apartment_shop':
            # Генерируем новые квартиры при каждом открытии окна
            if 'apartment_shop_offers' not in globals() or globals().get('apartment_shop_refresh', True):
                districts = ["Пренцлауэр-Берг", "Фридрихсхайн", "Шарлоттенбург", "Кройцберг", "Митте", "Шёнеберг", "Веддинг", "Трептов", "Лихтенберг"]
                apartments = []
                for _ in range(5):
                    district = random.choice(districts)
                    rooms = random.randint(1, 4)
                    area = random.randint(28 + rooms*10, 40 + rooms*30)
                    price = area * random.randint(180, 350) + rooms * random.randint(1000, 4000)
                    apartments.append({"district": district, "rooms": rooms, "area": area, "price": price})
                globals()['apartment_shop_offers'] = apartments
                globals()['apartment_selected'] = 0
                globals()['apartment_shop_refresh'] = False
            apartments = globals()['apartment_shop_offers']
            apartment_selected = globals()['apartment_selected']
            apt_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 180, 640, 360)
            pygame.draw.rect(screen, (40, 40, 60), apt_rect, border_radius=18)
            pygame.draw.rect(screen, (120, 120, 180), apt_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Покупка квартиры", True, (255, 255, 255))
            screen.blit(title, (apt_rect.centerx - title.get_width() // 2, apt_rect.y + 18))
            info_font = pygame.font.SysFont(None, 28)
            btn_font = pygame.font.SysFont(None, 28)
            # Список квартир
            apt_btns = []
            for i, apt in enumerate(apartments):
                y = apt_rect.y + 70 + i * 54
                block_rect = pygame.Rect(apt_rect.x + 24, y, apt_rect.width - 48, 44)
                pygame.draw.rect(screen, (60, 60, 90) if i != apartment_selected else (80, 120, 200), block_rect, border_radius=10)
                pygame.draw.rect(screen, (120, 120, 180), block_rect, 2, border_radius=10)
                txt = f"{apt['district']} | Комнат: {apt['rooms']} | {apt['area']} м² | {apt['price']}€"
                txt_surf = info_font.render(txt, True, (255,255,255))
                screen.blit(txt_surf, (block_rect.x + 12, block_rect.y + 8))
                apt_btns.append(block_rect)
            # Кнопки купить/назад/обновить
            selected_apt = apartments[apartment_selected]
            can_buy = not has_apartment and money >= selected_apt['price']
            buy_rect = pygame.Rect(apt_rect.right - 160, apt_rect.bottom - 60, 120, 36)
            pygame.draw.rect(screen, (80, 180, 80) if can_buy else (120, 120, 120), buy_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 120, 180), buy_rect, 2, border_radius=8)
            buy_text = btn_font.render("Купить" if can_buy else ("Куплено" if has_apartment else "Нет денег"), True, (255,255,255))
            screen.blit(buy_text, (buy_rect.centerx - buy_text.get_width() // 2, buy_rect.centery - buy_text.get_height() // 2))
            back_rect = pygame.Rect(apt_rect.x + 10, apt_rect.y + 20, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 120, 180), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            refresh_rect = pygame.Rect(apt_rect.right - 160, apt_rect.y + 20, 120, 36)
            pygame.draw.rect(screen, (40, 80, 160), refresh_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 120, 180), refresh_rect, 2, border_radius=8)
            refresh_text = btn_font.render("Обновить", True, (255,255,255))
            screen.blit(refresh_text, (refresh_rect.centerx - refresh_text.get_width() // 2, refresh_rect.centery - refresh_text.get_height() // 2))
            # Обработка кликов
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                # Выбор квартиры
                for i, rect in enumerate(apt_btns):
                    if rect.collidepoint(mx, my):
                        apartment_selected = i
                # Купить
                if can_buy and buy_rect.collidepoint(mx, my):
                    has_apartment = True
                    money -= selected_apt['price']
                    apartment_info = selected_apt.copy()
                # Назад
                if back_rect.collidepoint(mx, my):
                    state = 'game'
                    globals()['apartment_shop_refresh'] = True
                # Обновить предложения
                if refresh_rect.collidepoint(mx, my):
                    globals()['apartment_shop_refresh'] = True
            # Сохраняем выбранную квартиру между кадрами
            globals()['apartment_selected'] = apartment_selected
            pygame.display.flip()
            continue

        elif state == 'car_shop':
            # Большая база автомобилей
            car_db = [
                ("BMW", "3 Series"), ("BMW", "5 Series"), ("BMW", "X5"), ("BMW", "M3"),
                ("Mercedes-Benz", "C-Class"), ("Mercedes-Benz", "E-Class"), ("Mercedes-Benz", "GLA"), ("Mercedes-Benz", "S-Class"),
                ("Audi", "A3"), ("Audi", "A4"), ("Audi", "A6"), ("Audi", "Q5"), ("Audi", "Q7"),
                ("Volkswagen", "Golf"), ("Volkswagen", "Passat"), ("Volkswagen", "Tiguan"), ("Volkswagen", "Polo"),
                ("Opel", "Astra"), ("Opel", "Insignia"), ("Opel", "Corsa"),
                ("Ford", "Focus"), ("Ford", "Mondeo"), ("Ford", "Kuga"), ("Ford", "Fiesta"),
                ("Toyota", "Camry"), ("Toyota", "Corolla"), ("Toyota", "RAV4"), ("Toyota", "Yaris"),
                ("Nissan", "Qashqai"), ("Nissan", "X-Trail"), ("Nissan", "Juke"),
                ("Hyundai", "Solaris"), ("Hyundai", "Tucson"), ("Hyundai", "Elantra"),
                ("Kia", "Rio"), ("Kia", "Sportage"), ("Kia", "Ceed"),
                ("Mazda", "3"), ("Mazda", "6"), ("Mazda", "CX-5"),
                ("Renault", "Logan"), ("Renault", "Duster"), ("Renault", "Kaptur"),
                ("Lada", "Vesta"), ("Lada", "Granta"), ("Lada", "Niva"),
                ("Skoda", "Octavia"), ("Skoda", "Rapid"), ("Skoda", "Kodiaq"),
                ("Peugeot", "308"), ("Peugeot", "3008"), ("Peugeot", "408"),
                ("Honda", "Civic"), ("Honda", "CR-V"), ("Honda", "Accord"),
                ("Subaru", "Forester"), ("Subaru", "Outback"), ("Subaru", "Impreza"),
                ("Chevrolet", "Cruze"), ("Chevrolet", "Niva"), ("Chevrolet", "Aveo"),
                ("Mitsubishi", "Lancer"), ("Mitsubishi", "Outlander"), ("Mitsubishi", "ASX"),
                ("Volvo", "XC60"), ("Volvo", "S60"), ("Volvo", "V40"),
                ("Fiat", "500"), ("Fiat", "Panda"), ("Fiat", "Tipo"),
                ("Mini", "Cooper"), ("Mini", "Countryman"),
                ("Jeep", "Renegade"), ("Jeep", "Compass"),
                ("Suzuki", "Vitara"), ("Suzuki", "SX4"),
                ("Citroen", "C4"), ("Citroen", "C3"),
                ("Seat", "Leon"), ("Seat", "Ibiza"),
                ("Dacia", "Duster"), ("Dacia", "Sandero"),
                ("Chery", "Tiggo"), ("Chery", "Arrizo"),
                ("Geely", "Atlas"), ("Geely", "Coolray"),
                ("Great Wall", "Hover"), ("Great Wall", "Haval H6"),
                ("UAZ", "Patriot"), ("UAZ", "Hunter"),
                ("GAZ", "Volga"), ("GAZ", "Sobol"),
                ("Moskwitch", "2141"), ("Moskwitch", "408"),
                ("Tesla", "Model S"), ("Tesla", "Model 3"), ("Tesla", "Model X"), ("Tesla", "Model Y"),
            ]
            if 'car_shop_offers' not in globals() or globals().get('car_shop_refresh', True):
                offers = []
                for _ in range(5):
                    brand, model = random.choice(car_db)
                    year = random.randint(2005, 2023)
                    mileage = random.randint(20000, 220000)
                    price = int((25000 + (2023 - year) * -1200 + (220000 - mileage) * 0.07 + random.randint(-3000, 3000)) * random.uniform(0.8, 1.2))
                    price = max(3500, price)
                    offers.append({"brand": brand, "model": model, "year": year, "mileage": mileage, "price": price})
                globals()['car_shop_offers'] = offers
                globals()['car_selected'] = 0
                globals()['car_shop_refresh'] = False
            offers = globals()['car_shop_offers']
            car_selected = globals()['car_selected']
            car_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 180, 640, 360)
            pygame.draw.rect(screen, (40, 40, 60), car_rect, border_radius=18)
            pygame.draw.rect(screen, (200, 120, 80), car_rect, 4, border_radius=18)
            title = pygame.font.SysFont(None, 40).render("Покупка машины", True, (255, 255, 255))
            screen.blit(title, (car_rect.centerx - title.get_width() // 2, car_rect.y + 18))
            info_font = pygame.font.SysFont(None, 28)
            btn_font = pygame.font.SysFont(None, 28)
            car_btns = []
            for i, car in enumerate(offers):
                y = car_rect.y + 70 + i * 54
                block_rect = pygame.Rect(car_rect.x + 24, y, car_rect.width - 48, 44)
                pygame.draw.rect(screen, (120, 80, 40) if i != car_selected else (200, 120, 80), block_rect, border_radius=10)
                pygame.draw.rect(screen, (200, 120, 80), block_rect, 2, border_radius=10)
                txt = f"{car['brand']} {car['model']} | {car['year']} | {car['mileage']} км | {car['price']}€"
                txt_surf = info_font.render(txt, True, (255,255,255))
                screen.blit(txt_surf, (block_rect.x + 12, block_rect.y + 8))
                car_btns.append(block_rect)
            selected_car = offers[car_selected]
            can_buy = not has_car and money >= selected_car['price']
            buy_rect = pygame.Rect(car_rect.right - 160, car_rect.bottom - 60, 120, 36)
            pygame.draw.rect(screen, (80, 180, 80) if can_buy else (120, 120, 120), buy_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 120, 80), buy_rect, 2, border_radius=8)
            buy_text = btn_font.render("Купить" if can_buy else ("Куплено" if has_car else "Нет денег"), True, (255,255,255))
            screen.blit(buy_text, (buy_rect.centerx - buy_text.get_width() // 2, buy_rect.centery - buy_text.get_height() // 2))
            back_rect = pygame.Rect(car_rect.x + 10, car_rect.y + 20, 120, 36)
            pygame.draw.rect(screen, (20, 20, 30), back_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 120, 80), back_rect, 2, border_radius=8)
            back_text = btn_font.render("Назад", True, (255,255,255))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
            refresh_rect = pygame.Rect(car_rect.right - 160, car_rect.y + 20, 120, 36)
            pygame.draw.rect(screen, (160, 80, 40), refresh_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 120, 80), refresh_rect, 2, border_radius=8)
            refresh_text = btn_font.render("Обновить", True, (255,255,255))
            screen.blit(refresh_text, (refresh_rect.centerx - refresh_text.get_width() // 2, refresh_rect.centery - refresh_text.get_height() // 2))
            mouse = pygame.mouse.get_pressed()
            mx, my = pygame.mouse.get_pos()
            if mouse[0]:
                for i, rect in enumerate(car_btns):
                    if rect.collidepoint(mx, my):
                        car_selected = i
                if can_buy and buy_rect.collidepoint(mx, my):
                    has_car = True
                    money -= selected_car['price']
                    car_info = selected_car.copy()
                if back_rect.collidepoint(mx, my):
                    state = 'game'
                    globals()['car_shop_refresh'] = True
                if refresh_rect.collidepoint(mx, my):
                    globals()['car_shop_refresh'] = True
            globals()['car_selected'] = car_selected
            pygame.display.flip()
            continue

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        main_menu()
