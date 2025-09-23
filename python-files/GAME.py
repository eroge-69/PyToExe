import random
import time

ROOM_WIDTH = 30
ROOM_HEIGHT = 15
NUM_WALLS = 15
NUM_MONSTERS = 7
current_floor = 1

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = "K"
        
    def move(self):
        directions = [
            (0, -1),  # вверх
            (0, 1),   # вниз
            (-1, 0),  # влево
            (1, 0)     # вправо
        ]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        
        if (0 <= new_x < ROOM_WIDTH and 
            0 <= new_y < ROOM_HEIGHT and 
            (new_x, new_y) not in walls and 
            (new_x, new_y) != (stairs_x, stairs_y)):
            self.x = new_x
            self.y = new_y

def generate_level():
    global player_x, player_y, stairs_x, stairs_y, walls, monsters
    
    player_x, player_y = 1, 1
    
    walls = []
    for _ in range(NUM_WALLS):
        while True:
            x = random.randint(0, ROOM_WIDTH-1)
            y = random.randint(0, ROOM_HEIGHT-1)
            if (x, y) != (player_x, player_y):
                walls.append((x, y))
                break
                
    while True:
        stairs_x = random.randint(ROOM_WIDTH-3, ROOM_WIDTH-1)
        stairs_y = random.randint(ROOM_HEIGHT-3, ROOM_HEIGHT-1)
        if (stairs_x, stairs_y) != (player_x, player_y) and (stairs_x, stairs_y) not in walls:
            break
    
    monsters = []
    for _ in range(NUM_MONSTERS):
        while True:
            x = random.randint(2, ROOM_WIDTH-2)
            y = random.randint(2, ROOM_HEIGHT-2)
            if (x, y) not in walls and (x, y) != (stairs_x, stairs_y):
                monsters.append(Monster(x, y))
                break

generate_level()

while True:
    print("\n" * 5)
    print(f"FL00R: {current_floor}")
    for y in range(ROOM_HEIGHT):
        for x in range(ROOM_WIDTH):
            char = "."
            if any(m.x == x and m.y == y for m in monsters):
                char = "K"
            if (x, y) == (player_x, player_y):
                char = "@"
            elif (x, y) == (stairs_x, stairs_y):
                char = ">"
            elif (x, y) in walls:
                char = "#"
            print(char, end="")
        print()

    if (player_x, player_y) == (stairs_x, stairs_y):
        current_floor += 1
        generate_level()
        continue

    for monster in monsters:
        monster.move()

    move = input("ДВИГАЙ НОГАМИ МИХАИЛ!").lower()

    new_x, new_y = player_x, player_y
    if move == "w":
        new_y -= 1
    elif move == "s":
        new_y += 1
    elif move == "a":
        new_x -= 1
    elif move == "d":
        new_x += 1
    else:
        print("БЛЯЯЯЯЯ")
        continue

    if (0 <= new_x < ROOM_WIDTH and 
        0 <= new_y < ROOM_HEIGHT and 
        (new_x, new_y) not in walls and 
        not any(m.x == new_x and m.y == new_y for m in monsters)):
        player_x, player_y = new_x, new_y
    else:
        print("'Э БЛЭТ КУДА ПРЕШЬ!")
