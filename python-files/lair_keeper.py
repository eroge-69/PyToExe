import curses
import random
import time

# Инициализация curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.curs_set(0)

# Константы
MAP_WIDTH = 40
MAP_HEIGHT = 20
HERO_SPAWN_CHANCE = 0.05
TRAP_SPAWN_CHANCE = 0.1
MAX_HEROES = 3

# Символы для отображения
WALL_CHAR = "#"
FLOOR_CHAR = "."
PLAYER_CHAR = "M"  # Монстр!
HERO_CHAR = "H"
TRAP_CHAR = "T"
TREASURE_CHAR = "$"
EXIT_CHAR = ">"

# Цветовые пары
COLOR_PLAYER = 1
COLOR_HERO = 2
COLOR_TRAP = 3
COLOR_TREASURE = 4
COLOR_EXIT = 5

class GameObject:
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.health = 100
        self.attack = 10

    def move(self, dx, dy, game_map):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
            if game_map[new_y][new_x] != WALL_CHAR:
                self.x, self.y = new_x, new_y
                return True
        return False

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_CHAR, COLOR_PLAYER)
        self.health = 150
        self.attack = 15

class Hero(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, HERO_CHAR, COLOR_HERO)
        self.health = 80
        self.attack = 12
        self.target = None

    def update(self, player, game_map):
        # Простой ИИ: если герой видит игрока, он идет на него
        dx = player.x - self.x
        dy = player.y - self.y
        if abs(dx) > abs(dy):
            if dx > 0:
                self.move(1, 0, game_map)
            else:
                self.move(-1, 0, game_map)
        else:
            if dy > 0:
                self.move(0, 1, game_map)
            else:
                self.move(0, -1, game_map)

class Trap(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, TRAP_CHAR, COLOR_TRAP)
        self.health = 1
        self.attack = 20

class Treasure(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, TREASURE_CHAR, COLOR_TREASURE)
        self.health = 1

class Exit(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, EXIT_CHAR, COLOR_EXIT)
        self.health = 1000

def generate_map():
    # Простая генерация карты: комната со стенами
    game_map = [[FLOOR_CHAR for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if y == 0 or y == MAP_HEIGHT - 1 or x == 0 or x == MAP_WIDTH - 1:
                game_map[y][x] = WALL_CHAR
    return game_map

def main(stdscr):
    # Инициализация цветов
    curses.start_color()
    curses.init_pair(COLOR_PLAYER, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_HERO, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOR_TRAP, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_TREASURE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_EXIT, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    # Генерация карты
    game_map = generate_map()
    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    heroes = []
    traps = []
    treasures = [Treasure(random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2))]
    exit = Exit(random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2))

    # Основной игровой цикл
    running = True
    turns = 0
    score = 0

    stdscr.nodelay(True)
    stdscr.timeout(100)

    while running:
        stdscr.clear()

        # Отрисовка карты и всех объектов
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                stdscr.addch(y, x, game_map[y][x])
        for trap in traps:
            stdscr.addch(trap.y, trap.x, trap.char, curses.color_pair(trap.color))
        for treasure in treasures:
            stdscr.addch(treasure.y, treasure.x, treasure.char, curses.color_pair(treasure.color))
        stdscr.addch(exit.y, exit.x, exit.char, curses.color_pair(exit.color))
        for hero in heroes:
            stdscr.addch(hero.y, hero.x, hero.char, curses.color_pair(hero.color))
        stdscr.addch(player.y, player.x, player.char, curses.color_pair(player.color))

        # Отображение статистики
        stdscr.addstr(MAP_HEIGHT + 1, 0, f"Здоровье: {player.health} | Счет: {score} | Ходов: {turns}")
        stdscr.addstr(MAP_HEIGHT + 2, 0, "Управление: Стрелки - движение, 't' - поставить ловушку, 'q' - выход")

        # Обработка ввода
        key = stdscr.getch()
        if key == ord('q'):
            running = False
        elif key == curses.KEY_UP:
            player.move(0, -1, game_map)
            turns += 1
        elif key == curses.KEY_DOWN:
            player.move(0, 1, game_map)
            turns += 1
        elif key == curses.KEY_LEFT:
            player.move(-1, 0, game_map)
            turns += 1
        elif key == curses.KEY_RIGHT:
            player.move(1, 0, game_map)
            turns += 1
        elif key == ord('t'):
            # Попытка поставить ловушку
            if random.random() < TRAP_SPAWN_CHANCE:
                traps.append(Trap(player.x, player.y))

        # Спавн героев
        if len(heroes) < MAX_HEROES and random.random() < HERO_SPAWN_CHANCE:
            spawn_x, spawn_y = 0, 0
            side = random.randint(0, 3)
            if side == 0:  # Верхняя стена
                spawn_x, spawn_y = random.randint(1, MAP_WIDTH - 2), 1
            elif side == 1:  # Правая стена
                spawn_x, spawn_y = MAP_WIDTH - 2, random.randint(1, MAP_HEIGHT - 2)
            elif side == 2:  # Нижняя стена
                spawn_x, spawn_y = random.randint(1, MAP_WIDTH - 2), MAP_HEIGHT - 2
            elif side == 3:  # Левая стена
                spawn_x, spawn_y = 1, random.randint(1, MAP_HEIGHT - 2)
            heroes.append(Hero(spawn_x, spawn_y))

        # Обновление героев
        for hero in heroes[:]:
            hero.update(player, game_map)
            # Проверка столкновения с ловушками
            for trap in traps[:]:
                if hero.x == trap.x and hero.y == trap.y:
                    hero.health -= trap.attack
                    traps.remove(trap)
                    if hero.health <= 0:
                        heroes.remove(hero)
                        score += 10
            # Проверка столкновения с игроком
            if hero.x == player.x and hero.y == player.y:
                player.health -= hero.attack
                if player.health <= 0:
                    running = False

        # Проверка условий победы/поражения
        if player.health <= 0:
            stdscr.addstr(MAP_HEIGHT + 3, 0, "Вы погибли! Ваше логово разграблено.")
            stdscr.refresh()
            time.sleep(2)
            running = False

        stdscr.refresh()

    # Завершение игры
    curses.endwin()
    print(f"Игра окончена! Ваш счет: {score}")

if __name__ == "__main__":
    curses.wrapper(main)