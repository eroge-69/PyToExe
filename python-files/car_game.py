import os
import time
import random
import msvcrt
import sys

# --- ������������ ���� �� ������� ---
WIDTH = 25
HEIGHT = 20
CAR_SYMBOL = 'A'
OBSTACLE_SYMBOL = 'X'
EMPTY_SYMBOL = ' '

# --- �������� ������� ---
car_x = WIDTH // 2
car_y = HEIGHT - 2
obstacles = []
score = 0
game_speed = 0.1 

# --- ������� ��� ---

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def generate_obstacle():
    if random.randint(0, 4) == 0: 
        obs_x = random.randint(1, WIDTH - 2)
        obstacles.append([obs_x, 0])

def move_objects():
    global score
    new_obstacles = []
    for obs_x, obs_y in obstacles:
        if obs_y < HEIGHT - 1:
            new_obstacles.append([obs_x, obs_y + 1])
        else:
            score += 1 
    obstacles.clear()
    obstacles.extend(new_obstacles)

def check_collision():
    for obs_x, obs_y in obstacles:
        if obs_x == car_x and obs_y == car_y:
            return True
    return False

def draw_game():
    clear_screen()
    game_map = [[EMPTY_SYMBOL] * WIDTH for _ in range(HEIGHT)]
    
    if 0 <= car_y < HEIGHT and 0 <= car_x < WIDTH:
        game_map[car_y][car_x] = CAR_SYMBOL
    
    for obs_x, obs_y in obstacles:
        if 0 <= obs_y < HEIGHT and 0 <= obs_x < WIDTH:
            game_map[obs_y][obs_x] = OBSTACLE_SYMBOL

    border = '#' * WIDTH
    print(border)
    for row in game_map:
        print("#" + "".join(row[1:-1]) + "#")
    print(border)
    
    print(f"����: {score}")
    print("���������: A (���), D (�����). Q ��� ������.")

def get_input():
    if msvcrt.kbhit():
        return msvcrt.getch().decode('utf-8', errors='ignore').lower()
    return None

# --- �������� ������� ���� ---

print("������� ���! ��������� ����-��� ������.")
msvcrt.getch()

while True:
    draw_game()
    
    key = get_input()
    
    if key == 'q':
        break

    if key == 'a' and car_x > 1:
        car_x -= 1
    elif key == 'd' and car_x < WIDTH - 2:
        car_x += 1
    
    move_objects()
    generate_obstacle()

    if check_collision():
        draw_game()
        print("\n*** ǲ�������! ��� ��ʲ�����! ***")
        break
        
    time.sleep(game_speed)

print(f"��� ��������� �������: {score}")