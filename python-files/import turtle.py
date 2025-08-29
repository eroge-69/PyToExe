# Imports
import turtle
import random
import time
import json
import os

# Variable Definitions
SIZE = 4
TILE_SIZE = 100
WINDOW_SIZE = 600
EMPTY_TILE = 0
#Save Files
CHECKPOINT_FILE = "checkpoint.json"
LEADERBOARD_FILE = "leaderboard.txt"

# Game Variables
grid = [[(i * SIZE + j + 1) % (SIZE * SIZE) for j in range(SIZE)] for i in range(SIZE)]
empty_pos = (SIZE - 1, SIZE - 1)
moves_list = []
start_time = None
move_count = 0
player_name = ""
difficulty_level = ""

#Turtle Setup
screen = turtle.Screen()
screen.title("Sliding Puzzle Game")
screen.bgcolor("white")
screen.setup(width=WINDOW_SIZE, height=WINDOW_SIZE)
screen.tracer(0)

pen = turtle.Turtle()
pen.penup()
pen.hideturtle()

msg_pen = turtle.Turtle()   # Pen for error and info messages
msg_pen.penup()
msg_pen.hideturtle()

# Drawing Function
def draw_board():
    pen.clear()
    for i in range(SIZE):
        for j in range(SIZE):
            x = -200 + j * TILE_SIZE
            y = 200 - i * TILE_SIZE
            draw_tile(x, y, grid[i][j])
    screen.update()

def draw_tile(x, y, num):
    pen.goto(x, y)
    pen.fillcolor("lightblue" if num != 0 else "white")
    pen.begin_fill()
    for _ in range(4):
        pen.forward(TILE_SIZE)
        pen.right(90)
    pen.end_fill()
    if num != 0:
        pen.goto(x + TILE_SIZE/2, y - TILE_SIZE + 30)
        pen.color("black")
        pen.write(chr(64+num), align="center", font=("Arial", 24, "bold"))

# Move Function
def move_tile(direction, flag=False):
    global empty_pos, move_count
    r, c = empty_pos
    moved = False

    # Move blank tile if possible
    if direction == "Up" and r < SIZE - 1:
        swap(r, c, r + 1, c)
        empty_pos = (r + 1, c)
        moved = True
    elif direction == "Down" and r > 0:
        swap(r, c, r - 1, c)
        empty_pos = (r - 1, c)
        moved = True
    elif direction == "Left" and c < SIZE - 1:
        swap(r, c, r, c + 1)
        empty_pos = (r, c + 1)
        moved = True
    elif direction == "Right" and c > 0:
        swap(r, c, r, c - 1)
        empty_pos = (r, c - 1)
        moved = True

    if moved:
        if not flag:  # Only update stats for player moves
            move_count += 1
            moves_list.append(direction)
            draw_board()
            if check_win():
                handle_win()
    else:
        if not flag:
            show_error("Invalid move!")

def swap(r1, c1, r2, c2):
    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]

# Invalid Move
def show_error(msg):
    msg_pen.clear()
    msg_pen.goto(0, -260)
    msg_pen.color("red")
    msg_pen.write(msg, align="center", font=("Arial", 14, "bold"))
    screen.update()
    screen.ontimer(lambda: msg_pen.clear(), 1000)  # Clear message after 1 second

# Initial Suffled Board 
def shuffle_board():
    global empty_pos, grid

    # Start from solved state
    grid = [[(r * SIZE + c + 1) % (SIZE * SIZE) for c in range(SIZE)] for r in range(SIZE)]
    empty_pos = (SIZE - 1, SIZE - 1)

    moves = ["Up", "Down", "Left", "Right"]

    # Shuffle by making random valid moves
    for _ in range(200):
        move_tile(random.choice(moves), flag=True)

    # Ensure not already solved
    while check_win():
        for _ in range(20):
            move_tile(random.choice(moves), flag=True)

    # Move blank to bottom-right
    while empty_pos != (SIZE - 1, SIZE - 1):
        er, ec = empty_pos
        if er < SIZE - 1:
            move_tile("Up", flag=True)
        elif er > SIZE - 1:
            move_tile("Down", flag=True)
        elif ec < SIZE - 1:
            move_tile("Left", flag=True)
        elif ec > SIZE - 1:
            move_tile("Right", flag=True)

    draw_board()

# Check Win Condition and Handle Win
def check_win():
    expected = 1
    for i in range(SIZE):
        for j in range(SIZE):
            if i == SIZE - 1 and j == SIZE - 1:
                return grid[i][j] == 0
            if grid[i][j] != expected:
                return False
            expected += 1
    return True

def handle_win():
    end_time = time.time()
    elapsed = end_time - start_time
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    pen.goto(0, -250)
    pen.color("green")
    pen.write(f"You Win! Moves: {move_count}, Time: {mins:02}:{secs:02}", align="center", font=("Arial", 18, "bold"))
    screen.update()
    pen.clear()
    update_leaderboard(player_name, move_count, elapsed, difficulty_level)

    leaderboard = load_leaderboard()
    if any(player_name in entry for entry in leaderboard[:3]):
        pen.goto(0, -300)
        pen.color("blue")
        pen.write(f"🏆 Congratulations {player_name}! You are in the top 3!", align="center", font=("Arial", 16, "bold"))

    display_top_3_leaderboard()
    msg_pen.goto(0, -290)
    msg_pen.color("blue")
    msg_pen.write(f"Moves Stored in file {player_name}_moves_list.json", align="center", font=("Arial", 10, "normal"))
    with open(f"{player_name}_moves_list.json", "w") as f:
        json.dump(moves_list, f)

# Save and Load Checkpoint
def save_checkpoint():
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({
            "grid": grid,
            "empty_pos": empty_pos,
            "moves": moves_list,
            "move_count": move_count,
            "start_time": time.time(),
        }, f)
    show_error("Checkpoint Saved!")

def load_checkpoint():
    global grid, empty_pos, moves_list, move_count, start_time
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
            grid[:] = data["grid"]
            empty_pos = tuple(data["empty_pos"])
            moves_list[:] = data["moves"]
            move_count = data["move_count"]
            start_time = time.time()
        draw_board()
        show_error("Checkpoint Loaded!")
    except:
        show_error("No valid checkpoint!")


# Measure Difficulty
def manhattan_distance():
    total = 0
    for i in range(SIZE):
        for j in range(SIZE):
            val = grid[i][j]
            if val == 0:
                continue
            goal_i = (val - 1) // SIZE
            goal_j = (val - 1) % SIZE
            total += abs(i - goal_i) + abs(j - goal_j)
    return total

def classify_difficulty():
    dist = manhattan_distance()
    if dist < 20:
        return "Easy"
    elif dist < 40:
        return "Medium"
    else:
        return "Hard"

# LeaderBoard
def update_leaderboard(name, moves, time_taken, difficulty):
    entry = f"{name} - Moves: {moves}, Time: {int(time_taken)}s, Difficulty: {difficulty}\n"
    leaderboard = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = f.readlines()
    leaderboard.append(entry)
    leaderboard = sorted(leaderboard, key=lambda x: int(x.split()[3][:-1]))[:3]  # sort by moves
    with open(LEADERBOARD_FILE, "w") as f:
        f.writelines(leaderboard)
    print("Leaderboard updated.")
    print("Top 3 Players:")
    for line in leaderboard:
        print(line.strip())

def load_leaderboard():
    leaderboard = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = f.readlines()
    return leaderboard

def display_leaderboard():
    leaderboard = load_leaderboard()
    pen.goto(0, 200)
    pen.color("black")
    pen.write("Current Top 3 Leaderboard:", align="center", font=("Arial", 16, "bold"))
    y_position = 160
    if leaderboard:
        for idx, entry in enumerate(leaderboard[:3]):
            pen.goto(0, y_position - idx * 30)
            pen.write(f"{idx+1}. {entry.strip()}", align="center", font=("Arial", 14, "normal"))
    else:
        pen.goto(0, 160)
        pen.write("No leaderboard data yet.", align="center", font=("Arial", 14, "normal"))
    screen.update()

def display_top_3_leaderboard():
    leaderboard = load_leaderboard()
    pen.goto(0, 100)
    pen.color("black")
    pen.write("Top 3 Leaderboard:", align="center", font=("Arial", 16, "bold"))
    y_position = 70
    if leaderboard:
        for idx, entry in enumerate(leaderboard[:3]):
            pen.goto(0, y_position - idx * 30)
            pen.write(f"{idx+1}. {entry.strip()}", align="center", font=("Arial", 14, "normal"))
    else:
        pen.goto(0, 70)
        pen.write("No leaderboard data yet.", align="center", font=("Arial", 14, "normal"))
    screen.update()

# Info Panel Drawing
def show_info(difficulty):
    msg_pen.clear()
    msg_pen.color("black")

    # Top-left: difficulty
    msg_pen.goto(-280, 260)
    msg_pen.write(f"Difficulty: {difficulty}", align="left", font=("Arial", 14, "bold"))

    # Bottom-left: controls
    msg_pen.goto(-280, -280)
    msg_pen.write("S = Save | L = Load", align="left", font=("Arial", 12, "normal"))
    screen.update()

# Key Bindings
def setup_controls():
    screen.listen()
    screen.onkey(lambda: move_tile("Up"), "Up")
    screen.onkey(lambda: move_tile("Down"), "Down")
    screen.onkey(lambda: move_tile("Left"), "Left")
    screen.onkey(lambda: move_tile("Right"), "Right")
    screen.onkey(save_checkpoint, "s")
    screen.onkey(load_checkpoint, "l")

# Main Game Loop
def main():
    global start_time, player_name, difficulty_level

    display_leaderboard()
    player_name_input = turtle.textinput("Player Name", "Enter your name:")
    player_name = player_name_input if player_name_input else "Player"
    shuffle_board()
    difficulty_level = classify_difficulty()

    show_info(difficulty_level)  # show difficulty + controls
    start_time = time.time()
    setup_controls()
    draw_board()
    screen.mainloop()

main()
