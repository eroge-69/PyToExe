import pygame
import math
import random
import time

# =========================
# КОНСТАНТЫ ИНАЧАЛИЗАЦИИ
# =========================

pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")

FPS = 60
CLOCK = pygame.time.Clock()

# Цвета
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GRAY       = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED        = (255,   0,   0)
GREEN      = (  0, 255,   0)
BLUE       = (  0,   0, 255)
YELLOW     = (255, 255,   0)
PURPLE     = (150,   0, 150)
CYAN       = (  0, 255, 255)
ORANGE     = (255, 165,   0)

# Шрифты
FONT_SMALL  = pygame.font.SysFont("arial", 16)
FONT_MEDIUM = pygame.font.SysFont("arial", 24)
FONT_LARGE  = pygame.font.SysFont("arial", 36)

# =========================
# ПУТЬ ВРАГОВ
# =========================

# Путь — список контрольных точек, по которым движутся враги.
PATH = [
    (0, 250), (150, 250), (150, 100),
    (350, 100), (350, 400), (600, 400),
    (600, 200), (800, 200)
]

# Предварительно рассчитываем сегменты пути (радиусы угла, длины сегментов)
def build_path_segments(path):
    segments = []
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        segments.append({
            "start": (x1, y1),
            "end": (x2, y2),
            "dx": dx, "dy": dy,
            "length": length,
            "angle": angle
        })
    return segments

PATH_SEGMENTS = build_path_segments(PATH)

# =========================
# МЕСТА ПОД БАШНИ (FIXED)
# =========================

TOWER_SPOTS = [
    (100, 200), (200, 150), (300, 300), (450, 150),
    (500, 350), (700, 300), (250, 450), (550, 100)
]
TOWER_SPOT_RADIUS = 20

# =========================
# ГЛОБАЛЬНАЯ ИГРОВАЯ СТАТИСТИКА
# =========================

player_money = 200
player_lives = 20
current_wave = 0
wave_in_progress = False
enemies = []
towers = []
bullets = []
abilities = {
    "bomb": {"cooldown": 15, "last_cast": -999},
    "slow": {"cooldown": 20, "last_cast": -999}
}

# =========================
# КЛАССЫ ВРАГОВ
# =========================

class Enemy:
    def __init__(self, path_segments):
        self.path_segments = path_segments
        self.curr_seg = 0
        self.pos = list(path_segments[0]["start"])
        self.speed = 1.0
        self.max_health = 10
        self.health = self.max_health
        self.value = 5
        self.radius = 10
        self.shield = 0  # урон поглощается до исчерпания щита
        self.is_flying = False
        self.color = RED
        self.alive = True

    def update(self, dt, global_slow=False):
        # Если замедление активно, снижаем скорость
        speed = self.speed * (0.5 if global_slow else 1.0)
        # Движение вдоль сегмента
        seg = self.path_segments[self.curr_seg]
        dist_to_travel = speed * dt
        remaining = seg["length"] - math.hypot(self.pos[0] - seg["start"][0], self.pos[1] - seg["start"][1])
        if dist_to_travel < remaining:
            # Продвигаемся вдоль сегмента
            self.pos[0] += math.cos(seg["angle"]) * dist_to_travel
            self.pos[1] += math.sin(seg["angle"]) * dist_to_travel
        else:
            # Переходим на следующий сегмент
            self.curr_seg += 1
            if self.curr_seg >= len(self.path_segments):
                # Добрались до конца — отнимаем жизнь
                global player_lives
                player_lives -= 1
                self.alive = False
                return
            overflow = dist_to_travel - remaining
            next_seg = self.path_segments[self.curr_seg]
            self.pos = list(next_seg["start"])
            self.pos[0] += math.cos(next_seg["angle"]) * overflow
            self.pos[1] += math.sin(next_seg["angle"]) * overflow

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        # Полоска здоровья
        hp_bar_width = 30
        hp_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.pos[0] - hp_bar_width // 2, self.pos[1] - self.radius - 10, hp_bar_width, 5))
        pygame.draw.rect(screen, GREEN, (self.pos[0] - hp_bar_width // 2, self.pos[1] - self.radius - 10, hp_bar_width * hp_ratio, 5))

    def take_damage(self, dmg):
        if self.shield > 0:
            # Щит поглощает 50% урона, остальные идут по здоровью
            absorbed = dmg * 0.5
            self.shield -= absorbed
            remaining = dmg - absorbed
            if self.shield < 0:
                # Остаток щита переходит в урон по HP
                remaining += -self.shield
                self.shield = 0
            self.health -= remaining
        else:
            self.health -= dmg
        if self.health <= 0:
            self.alive = False
            return self.value
        return 0

# Подклассы врагов

class SlowStrongEnemy(Enemy):
    def __init__(self, path_segments):
        super().__init__(path_segments)
        self.speed = 0.5
        self.max_health = 30
        self.health = self.max_health
        self.value = 20
        self.radius = 14
        self.color = (139, 0, 0)  # темно-красный

class FastWeakEnemy(Enemy):
    def __init__(self, path_segments):
        super().__init__(path_segments)
        self.speed = 2.0
        self.max_health = 8
        self.health = self.max_health
        self.value = 8
        self.radius = 8
        self.color = ORANGE

class ShieldedEnemy(Enemy):
    def __init__(self, path_segments):
        super().__init__(path_segments)
        self.speed = 1.0
        self.max_health = 20
        self.health = self.max_health
        self.value = 15
        self.radius = 12
        self.shield = 10
        self.color = BLUE

class FlyingEnemy(Enemy):
    def __init__(self, path_segments):
        super().__init__(path_segments)
        self.speed = 1.5
        self.max_health = 12
        self.health = self.max_health
        self.value = 12
        self.radius = 10
        self.is_flying = True
        self.color = PURPLE

class BossEnemy(Enemy):
    def __init__(self, path_segments):
        super().__init__(path_segments)
        self.speed = 0.8
        self.max_health = 200
        self.health = self.max_health
        self.value = 100
        self.radius = 20
        self.shield = 50
        self.color = (128, 0, 128)  # насыщенный фиолетовый

# =========================
# КЛАССЫ БАШЕН
# =========================

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.range = 100
        self.damage = 10
        self.fire_rate = 1.0  # выстрелов в секунду
        self.last_shot = 0
        self.price = 50
        self.upgrade_cost = 40
        self.radius_draw = 5 + self.range // 10
        self.bullet_speed = 4.0
        self.type = "standard"  # стандартная башня
        self.color = GREEN

    def can_shoot(self, curr_time):
        return (curr_time - self.last_shot) >= 1 / self.fire_rate

    def shoot(self, target, bullets, curr_time):
        # Создаём пулю от центра башни к врагу
        dx = target.pos[0] - self.x
        dy = target.pos[1] - self.y
        angle = math.atan2(dy, dx)
        bullets.append(Bullet(self.x, self.y, angle, self.damage, self.bullet_speed, self.type))
        self.last_shot = curr_time

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.5)
        self.fire_rate *= 1.2
        self.range = int(self.range * 1.1)
        self.radius_draw = 5 + self.range // 10
        self.upgrade_cost = int(self.upgrade_cost * 1.5)

    def sell_value(self):
        total_spent = self.price + (self.upgrade_cost / 1.5)  # грубо считаем затраты
        return int(total_spent * 0.5)

    def draw(self, screen, selected=False):
        color = YELLOW if selected else self.color
        pygame.draw.circle(screen, color, (self.x, self.y), 15)
        # Радиус стрельбы
        #pygame.draw.circle(screen, LIGHT_GRAY, (self.x, self.y), self.range, 1)

class AoeTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 120
        self.damage = 15
        self.fire_rate = 0.7
        self.price = 80
        self.upgrade_cost = 60
        self.type = "aoe"
        self.color = CYAN

class FastTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 90
        self.damage = 6
        self.fire_rate = 2.5
        self.price = 70
        self.upgrade_cost = 50
        self.type = "fast"
        self.color = YELLOW

class PiercingTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 110
        self.damage = 12
        self.fire_rate = 1.0
        self.price = 100
        self.upgrade_cost = 80
        self.type = "piercing"
        self.color = ORANGE

# =========================
# КЛАСС ПУЛИ (БУЛЛЕТ)
# =========================

class Bullet:
    def __init__(self, x, y, angle, damage, speed, btype):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.type = btype  # стандартный, aoe, piercing
        self.radius = 5 if btype == "standard" else (8 if btype == "aoe" else 4)
        self.color = WHITE if btype == "standard" else (RED if btype == "aoe" else YELLOW)
        self.alive = True

    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        # Уничтожаем пулю, если она вышла за границы
        if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# =========================
# ФУНКЦИИ ДЛЯ ВОЛН
# =========================

def spawn_wave(wave_num):
    group = []
    # Простая формула: в каждой волне по 5 + wave_num врагов, типы разложены по рандому
    count = 5 + wave_num * 2
    for i in range(count):
        r = random.random()
        if wave_num % 5 == 0 and i == count - 1:
            # Каждый 5-й — босс
            group.append(BossEnemy(PATH_SEGMENTS))
        elif r < 0.3:
            group.append(SlowStrongEnemy(PATH_SEGMENTS))
        elif r < 0.6:
            group.append(FastWeakEnemy(PATH_SEGMENTS))
        elif r < 0.8:
            group.append(ShieldedEnemy(PATH_SEGMENTS))
        else:
            group.append(FlyingEnemy(PATH_SEGMENTS))
    # Делаем задержку спауна: каждый следующий через 1 секунду
    return [{"enemy": e, "spawn_time": i * 1000} for i, e in enumerate(group)]

wave_queue = []  # очередь «врагов с таймингом»

# =========================
# ФУНКЦИИ ОТРИСОВКИ UI
# =========================

def draw_path(screen, path):
    # Рисуем серые полосы как дорогу
    for i in range(len(path) - 1):
        pygame.draw.line(screen, LIGHT_GRAY, path[i], path[i + 1], 40)

def draw_tower_spots(screen, spots):
    for (x, y) in spots:
        pygame.draw.circle(screen, GRAY, (x, y), TOWER_SPOT_RADIUS, 2)

def draw_hud(screen):
    # Отрисовка денег, жизней, волны, способностей и их кулдауна
    money_surf = FONT_MEDIUM.render(f"Деньги: {player_money}", True, WHITE)
    lives_surf = FONT_MEDIUM.render(f"Жизни: {player_lives}", True, WHITE)
    wave_surf = FONT_MEDIUM.render(f"Волна: {current_wave}", True, WHITE)
    screen.blit(money_surf, (10, 10))
    screen.blit(lives_surf, (10, 40))
    screen.blit(wave_surf, (10, 70))

    # Способности
    now = time.time()
    # Бомба
    bomb_cd = max(0, abilities["bomb"]["cooldown"] - (now - abilities["bomb"]["last_cast"]))
    bomb_text = FONT_SMALL.render(f"[1] Бомба ({bomb_cd:.1f}s)", True, CYAN if bomb_cd <= 0 else GRAY)
    screen.blit(bomb_text, (10, 110))
    # Замедление
    slow_cd = max(0, abilities["slow"]["cooldown"] - (now - abilities["slow"]["last_cast"]))
    slow_text = FONT_SMALL.render(f"[2] Замедление ({slow_cd:.1f}s)", True, CYAN if slow_cd <= 0 else GRAY)
    screen.blit(slow_text, (10, 130))

# =========================
# ОСНОВНОЙ ЦИКЛ ИГРЫ
# =========================

def main():
    global player_money, player_lives, current_wave, wave_in_progress, wave_queue

    selected_tower = None
    next_wave_timer = 0
    wave_delay = 3000  # 3 секунды перед началом следующей волны
    running = True

    while running:
        dt = CLOCK.tick(FPS) / 1000.0  # dt в секундах
        curr_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Клик мыши — установка/выбор/апгрейд/продажа башни
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Проверим, кликнули ли на уже установленную башню
                clicked_tower = None
                for t in towers:
                    if math.hypot(mx - t.x, my - t.y) <= 15:
                        clicked_tower = t
                        break

                if clicked_tower:
                    # Выбираем башню (для апгрейда/продажи)
                    if selected_tower == clicked_tower:
                        # Если она уже выбрана, нажали ещё раз — продаём
                        player_money += clicked_tower.sell_value()
                        towers.remove(clicked_tower)
                        selected_tower = None
                    else:
                        selected_tower = clicked_tower
                else:
                    # Если кликнули вне башни — пытаемся поставить башню на свободное место
                    selected_tower = None
                    for spot in TOWER_SPOTS:
                        sx, sy = spot
                        if math.hypot(mx - sx, my - sy) <= TOWER_SPOT_RADIUS:
                            # Проверяем, свободно ли
                            occupied = any(math.hypot(sx - t.x, sy - t.y) < 1 for t in towers)
                            if not occupied:
                                # Открыть меню выбора типа башни
                                tower_type = show_tower_menu()
                                if tower_type:
                                    if tower_type == "standard" and player_money >= Tower(sx, sy).price:
                                        player_money -= Tower(sx, sy).price
                                        towers.append(Tower(sx, sy))
                                    elif tower_type == "aoe" and player_money >= AoeTower(sx, sy).price:
                                        player_money -= AoeTower(sx, sy).price
                                        towers.append(AoeTower(sx, sy))
                                    elif tower_type == "fast" and player_money >= FastTower(sx, sy).price:
                                        player_money -= FastTower(sx, sy).price
                                        towers.append(FastTower(sx, sy))
                                    elif tower_type == "piercing" and player_money >= PiercingTower(sx, sy).price:
                                        player_money -= PiercingTower(sx, sy).price
                                        towers.append(PiercingTower(sx, sy))
                            break

            # Клавиши для умений
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # Бомба
                    if curr_time - abilities["bomb"]["last_cast"] >= abilities["bomb"]["cooldown"]:
                        cast_bomb()
                        abilities["bomb"]["last_cast"] = curr_time
                if event.key == pygame.K_2:
                    # Замедление
                    if curr_time - abilities["slow"]["last_cast"] >= abilities["slow"]["cooldown"]:
                        abilities["slow"]["last_cast"] = curr_time

        # Запуск следующей волны, если нет текущей
        if not wave_in_progress and len(enemies) == 0 and len(wave_queue) == 0:
            next_wave_timer += CLOCK.get_time()
            if next_wave_timer >= wave_delay:
                current_wave += 1
                wave_in_progress = True
                wave_queue = spawn_wave(current_wave)
                next_wave_timer = 0

        # Спавн врагов по таймингу
        if wave_in_progress and len(wave_queue) > 0:
            if pygame.time.get_ticks() >= wave_queue[0]["spawn_time"]:
                enemies.append(wave_queue[0]["enemy"])
                wave_queue.pop(0)
            if len(wave_queue) == 0:
                wave_in_progress = False

        # Обновление врагов
        global_slow = (curr_time - abilities["slow"]["last_cast"]) < 3  # Замедление действует 3 секунды
        for enemy in enemies:
            enemy.update(dt * 60, global_slow)  # умножаем dt для компенсации fps

        # Удаляем погибших врагов, начисляем деньги
        for enemy in enemies[:]:
            if not enemy.alive:
                if enemy.health <= 0:
                    player_money += enemy.value
                enemies.remove(enemy)

        # Обновление башен: стрельба
        for tower in towers:
            # Находим ближайшего врага в радиусе
            target = None
            min_dist = float("inf")
            for enemy in enemies:
                dist = math.hypot(enemy.pos[0] - tower.x, enemy.pos[1] - tower.y)
                if dist <= tower.range and dist < min_dist:
                    min_dist = dist
                    target = enemy
            if target and tower.can_shoot(curr_time):
                tower.shoot(target, bullets, curr_time)

        # Обновление пуль: движение и попадание
        for bullet in bullets:
            bullet.update(dt * 60)
            # Проверяем попадание по врагам
            for enemy in enemies:
                if math.hypot(enemy.pos[0] - bullet.x, enemy.pos[1] - bullet.y) <= enemy.radius + bullet.radius:
                    # Попадание!
                    if bullet.type == "standard":
                        enemy.take_damage(bullet.damage)
                    elif bullet.type == "aoe":
                        # Наносим урон всем врагам в радиус 30
                        for e in enemies:
                            if math.hypot(e.pos[0] - bullet.x, e.pos[1] - bullet.y) <= 30:
                                e.take_damage(bullet.damage)
                    elif bullet.type == "piercing":
                        # Урон сразу 3 ближайшим врагам
                        # Сортируем врагов по дистанции до точки попадания
                        sorted_enemies = sorted(enemies, key=lambda e: math.hypot(e.pos[0] - bullet.x, e.pos[1] - bullet.y))
                        for i, e in enumerate(sorted_enemies[:3]):
                            if math.hypot(e.pos[0] - bullet.x, e.pos[1] - bullet.y) <= e.radius + bullet.radius:
                                e.take_damage(bullet.damage)
                    bullet.alive = False
                    break
            if not bullet.alive:
                continue

        # Удаляем пули за границами или по попаданию
        bullets[:] = [b for b in bullets if b.alive]

        # Отрисовка всего
        SCREEN.fill(BLACK)
        draw_path(SCREEN, PATH)
        draw_tower_spots(SCREEN, TOWER_SPOTS)

        # Нарисуем врагов
        for enemy in enemies:
            enemy.draw(SCREEN)

        # Нарисуем башни
        for tower in towers:
            tower.draw(SCREEN, selected=(tower == selected_tower))

        # Нарисуем пули
        for bullet in bullets:
            bullet.draw(SCREEN)

        # Если башня выбрана, показываем информацию и возможность апгрейда
        if selected_tower:
            info_x, info_y = 600, 10
            info_surf = FONT_MEDIUM.render(f"Уровень: {selected_tower.level}", True, WHITE)
            SCREEN.blit(info_surf, (info_x, info_y))
            dmg_surf = FONT_SMALL.render(f"Урон: {selected_tower.damage}", True, WHITE)
            SCREEN.blit(dmg_surf, (info_x, info_y + 30))
            fr_surf = FONT_SMALL.render(f"Скорость: {selected_tower.fire_rate:.1f} в/с", True, WHITE)
            SCREEN.blit(fr_surf, (info_x, info_y + 50))
            range_surf = FONT_SMALL.render(f"Радиус: {selected_tower.range}", True, WHITE)
            SCREEN.blit(range_surf, (info_x, info_y + 70))
            upg_surf = FONT_SMALL.render(f"[ПКМ] Улучшить за {selected_tower.upgrade_cost}", True, CYAN)
            SCREEN.blit(upg_surf, (info_x, info_y + 100))
            sell_surf = FONT_SMALL.render(f"[ЛКМ на башню] Продать за {selected_tower.sell_value()}", True, ORANGE)
            SCREEN.blit(sell_surf, (info_x, info_y + 130))

        draw_hud(SCREEN)
        pygame.display.flip()

        # Обработка обновления/апгрейда башни правой кнопкой мыши
        if pygame.mouse.get_pressed()[2] and selected_tower:
            if player_money >= selected_tower.upgrade_cost:
                player_money -= selected_tower.upgrade_cost
                selected_tower.upgrade()

        # Проверка на проигрыш
        if player_lives <= 0:
            running = False

    # Конец игры
    game_over()

# =========================
# ФУНКЦИИ МЕНЮ ИГРОКА
# =========================

def show_tower_menu():
    """
    Показывает простое меню выбора типа башни.
    Вернёт один из: "standard", "aoe", "fast", "piercing" или None.
    """
    menu_open = True
    selection = None

    # Поверх игрового экрана рисуем полупрозрачный прямоугольник
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((50, 50, 50))

    while menu_open:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_open = False
                # Клавиши 1-4 — выбор типа башни
                if event.key == pygame.K_1:
                    selection = "standard"
                    menu_open = False
                if event.key == pygame.K_2:
                    selection = "aoe"
                    menu_open = False
                if event.key == pygame.K_3:
                    selection = "fast"
                    menu_open = False
                if event.key == pygame.K_4:
                    selection = "piercing"
                    menu_open = False
        # Отрисуем оверлей и текст
        SCREEN.blit(overlay, (0, 0))
        text1 = FONT_LARGE.render("Выберите тип башни:", True, WHITE)
        text2 = FONT_MEDIUM.render("[1] Стандартная (50)", True, GREEN)
        text3 = FONT_MEDIUM.render("[2] Площадная (80)", True, CYAN)
        text4 = FONT_MEDIUM.render("[3] Скорострельная (70)", True, YELLOW)
        text5 = FONT_MEDIUM.render("[4] Пробивающая (100)", True, ORANGE)
        text6 = FONT_SMALL.render("[ESC] Отмена", True, RED)
        SCREEN.blit(text1, (200, 150))
        SCREEN.blit(text2, (200, 220))
        SCREEN.blit(text3, (200, 260))
        SCREEN.blit(text4, (200, 300))
        SCREEN.blit(text5, (200, 340))
        SCREEN.blit(text6, (200, 400))
        pygame.display.flip()

    return selection

def cast_bomb():
    """
    Уменьшает здоровье всех врагов на 30%
    """
    for e in enemies:
        e.take_damage(int(e.max_health * 0.3))

def game_over():
    """
    Простая заставка «Game Over» и выход.
    """
    over = True
    while over:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                over = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                over = False
        SCREEN.fill(BLACK)
        text = FONT_LARGE.render("Игра окончена!", True, RED)
        instr = FONT_MEDIUM.render("Нажмите любую клавишу, чтобы выйти", True, WHITE)
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
        SCREEN.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.flip()
    pygame.quit()
    exit()

if __name__ == "__main__":
    main()
