import random

# Функции для отображения игрового поля
def print_board(board):
    print("\n")
    print("┌─────┬───────┬─────┐")
    for i in range(2, -1, -1):  # Перебираем строки от 2 до 0 (снизу вверх)
        row = "  │  ".join([f" {board[i][j]} " if board[i][j] != ' ' else f" {i * 3 + j + 1} " for j in range(3)])
        print(f"│{row}│")
        if i > 0:
            print("├─────┼───────┼─────┤")
    print("└─────┴───────┴─────┘")
    print("\n")

# Функция для проверки победы
def check_win(board, player):
    for row in board:
        if all([cell == player for cell in row]):
            return True
    for col in range(3):
        if all([board[row][col] == player for row in range(3)]):
            return True
    if all([board[i][i] == player for i in range(3)]) or all([board[i][2 - i] == player for i in range(3)]):
        return True
    return False

# Функция для проверки наличия свободных клеток
def is_board_full(board):
    return all(cell != ' ' for row in board for cell in row)

# Функция для получения доступных клеток
def available_moves(board):
    return [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']

# Функция для хода игрока
def player_move(board):
    while True:
        try:
            move = input('Введите координаты для вашего хода (от 1 до 9, например 1 - нижний левый угол, 5 - центральная клетка): ')
            move = int(move)
            if move < 1 or move > 9:
                print('Повторите, введите число от 1 до 9.')
                continue

            # Преобразование numpad-позиций в координаты
            if move == 1:
                row, col = 0, 0
            elif move == 2:
                row, col = 0, 1
            elif move == 3:
                row, col = 0, 2
            elif move == 4:
                row, col = 1, 0
            elif move == 5:
                row, col = 1, 1
            elif move == 6:
                row, col = 1, 2
            elif move == 7:
                row, col = 2, 0
            elif move == 8:
                row, col = 2, 1
            elif move == 9:
                row, col = 2, 2

            if board[row][col] == ' ':
                board[row][col] = 'X'
                break
            else:
                print('Клетка занята. Попробуйте ещё раз.')
        except ValueError:
            print('Некорректные данные. Пожалуйста, введите число от 1 до 9.')

# Функция для хода AI
def ai_move(board):
    best_score = -float('inf')
    best_move = None
    for (row, col) in available_moves(board):
        board[row][col] = 'O'
        score = minimax(board, 0, False)
        board[row][col] = ' '
        if score > best_score:
            best_score = score
            best_move = (row, col)
    board[best_move[0]][best_move[1]] = 'O'
    print(f"AI ходит: {best_move[0] * 3 + best_move[1] + 1}")

# Функция для оценки хода с использованием minimax
def minimax(board, depth, is_maximizing):
    if check_win(board, 'X'):
        return -10 + depth
    if check_win(board, 'O'):
        return 10 - depth
    if is_board_full(board):
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for (row, col) in available_moves(board):
            board[row][col] = 'O'
            score = minimax(board, depth + 1, False)
            board[row][col] = ' '
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for (row, col) in available_moves(board):
            board[row][col] = 'X'
            score = minimax(board, depth + 1, True)
            board[row][col] = ' '
            best_score = min(score, best_score)
        return best_score

# Главная функция игры
def play_game():
    print("Добро пожаловать в игру 'Крестики-Нолики'!")
    
    while True:
        board = [[' ' for _ in range(3)] for _ in range(3)]
        print_board(board)
        
        while True:
            # Ход игрока
            player_move(board)
            print_board(board)
            if check_win(board, 'X'):
                print('Вы победили!')
                break
            if is_board_full(board):
                print('Ничья!')
                break
            
            # Ход AI
            ai_move(board)
            print_board(board)
            if check_win(board, 'O'):
                print('AI победило!')
                break
            if is_board_full(board):
                print('Ничья!')
                break
        
        # Запросить у игрока, хочет ли он сыграть еще раз
        if not play_again():
            print("Спасибо за игру! До свидания.")
            break

#Перезапуск игры
def play_again():
    while True:
        play_again_choice = input('Хотите сыграть еще раз? (y/n): ').lower()
        if play_again_choice == 'y':
            return True
        elif play_again_choice == 'n':
            return False
        else:
            print("Пожалуйста, введите 'y' для продолжения или 'n' для завершения.")



# Запуск игры
if __name__ == "__main__":
    play_game()
