import random
import time
import os
import math

# Константы игры
WIDTH = 20
HEIGHT = 10
EMPTY = '.'
PATH = '#'
ENEMY = 'O'
FROZEN = '*'
RANGE = '~'

# Структуры данных
class Enemy:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        self.frozen = False
        self.freeze_time = 0

class Tower:
    def __init__(self, x, y, damage, range_, fire_rate):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_
        self.fire_rate = fire_rate
        self.last_fire_time = 0

# Глобальные переменные
grid = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
enemies = []
towers = []
player_health = 100
coins = 100
wave = 1
game_over = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def spawn_enemy():
    if random.randint(0, 100) < min(50 + wave * 5, 95):
        enemy = Enemy(0, HEIGHT // 2, 50 + wave * 10)
        enemies.append(enemy)

def move_enemies():
    for enemy in enemies:
        if enemy.frozen:
            enemy.freeze_time -= 1
            if enemy.freeze_time <= 0:
                enemy.frozen = False
            continue

        if enemy.x < WIDTH - 1:
            enemy.x += 1
        else:
            global player_health
            player_health -= 10
            enemy.health = 0

    # Удаляем мертвых врагов
    enemies[:] = [e for e in enemies if e.health > 0]

def fire_towers():
    current_time = time.time() * 1000  # текущее время в миллисекундах

    for tower in towers:
        if current_time - tower.last_fire_time >= tower.fire_rate:
            closest_enemy = None
            closest_dist = tower.range + 1

            for enemy in enemies:
                dist = distance(tower.x, tower.y, enemy.x, enemy.y)
                if dist <= tower.range and dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = enemy

            if closest_enemy is not None:
                closest_enemy.health -= tower.damage
                if closest_enemy.health <= 0:
                    coins += 10
                tower.last_fire_time = current_time

def draw_game():
    display_grid = [row[:] for row in grid]

    for enemy in enemies:
        if enemy.y < HEIGHT and enemy.x < WIDTH:
            display_grid[enemy.y][enemy.x] = enemy.frozen and FROZEN or ENEMY

    clear_screen()
    for row in display_grid:
        print(''.join(row))

    print(f"\nHealth: {player_health} | Coins: {coins} | Wave: {wave} | Enemies: {len(enemies)}")

def update_game():
    spawn_enemy()
    move_enemies()
    fire_towers()

    if player_health <= 0:
        global game_over
        game_over = True

def main():
    global game_over
    while not game_over:
        draw_game()
        update_game()
        time.sleep(0.1)

    print("Game Over!")

if __name__ == "__main__":
    main()
