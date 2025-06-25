import random
import os
import time


def clear_screen():
    # Clears the terminal screen for a cleaner game display.
    os.system('cls' if os.name == 'nt' else 'clear')


def print_game(snake, food, score):
    # Renders the game board, snake, food, and score.
    clear_screen()
    width = 20
    height = 10
    game_board = [['.' for _ in range(width)] for _ in range(height)]

    # Place the snake on the board
    for x, y in snake:
        # Ensures that snake segments are within bounds before placing
        if 0 <= x < width and 0 <= y < height:
            game_board[y][x] = 'O'

    # Place the food on the board
    # Ensures food is within bounds before placing
    if 0 <= food[0] < width and 0 <= food[1] < height:
        game_board[food[1]][food[0]] = '*'

    # Print the game board
    for row in game_board:
        print(''.join(row))
    print(f"Счет: {score}")


def get_move():
    # Gets valid movement input from the player.
    while True:
        move = input("Введите направление (w/a/s/d): ").lower()
        if move in ('w', 'a', 's', 'd'):
            return move


def move_snake(snake, move, food_eaten):
    # Calculates the new position of the snake's head based on the move.
    head_x, head_y = snake[0]
    if move == 'w':
        new_head = (head_x, head_y - 1)
    elif move == 's':
        new_head = (head_x, head_y + 1)
    elif move == 'a':
        new_head = (head_x - 1, head_y)
    elif move == 'd':
        new_head = (head_x + 1, head_y)

    # Add the new head to the beginning of the snake list
    snake.insert(0, new_head)

    # If food was not eaten, remove the tail segment
    if not food_eaten:
        snake.pop()

    return snake


def check_collision(snake, width, height):
    # Checks for collisions with walls or the snake's own body.
    head_x, head_y = snake[0]
    # Check wall collision
    if not (0 <= head_x < width and 0 <= head_y < height):
        return True
    # Check self-collision (head with any part of the body except itself)
    if snake[0] in snake[1:]:
        return True
    return False


def generate_food(snake, width, height):
    # Generates a new food position that is not on the snake's body.
    while True:
        food = (random.randint(0, width - 1), random.randint(0, height - 1))
        if food not in snake:
            return food


def play_snake_game():
    # Main function to run the Snake game.
    width = 20
    height = 10
    snake = [(width // 2, height // 2)]  # Initial snake position
    food = generate_food(snake, width, height)
    direction = 'd'  # Initial direction
    score = 0
    game_over = False

    while not game_over:
        print_game(snake, food, score)

        # Get player input for the next move
        try:
            move = get_move()
            direction = move  # Update the current direction
        except (KeyboardInterrupt, EOFError):
            print("Игра прервана")
            return

        # Determine if food is eaten BEFORE moving the snake
        food_eaten_this_turn = False
        # Calculate the potential new head position to check for food collision
        head_x, head_y = snake[0]
        if direction == 'w':
            potential_new_head = (head_x, head_y - 1)
        elif direction == 's':
            potential_new_head = (head_x, head_y + 1)
        elif direction == 'a':
            potential_new_head = (head_x - 1, head_y)
        elif direction == 'd':
            potential_new_head = (head_x + 1, head_y)

        if potential_new_head == food:
            food_eaten_this_turn = True
            score += 1
            food = generate_food(snake, width, height)

        # Move the snake based on whether food was eaten
        snake = move_snake(snake, direction, food_eaten_this_turn)

        # Check for collisions after the snake has moved
        if check_collision(snake, width, height):
            game_over = True
            print_game(snake, food, score)  # Display final state
            print("Игра окончена!")
            break

        time.sleep(0.2)  # Control game speed


if __name__ == "__main__":
    play_snake_game()