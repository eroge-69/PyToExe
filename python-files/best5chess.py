import random
import time
import shutil
from collections import defaultdict
from datetime import datetime
import os
import pygame
import sys

# Initialize pygame, let's get started~
pygame.init()

# Game constants, don't mix them up~
BOARD_SIZE = 15
CELL_SIZE = 40
BOARD_PADDING = 50
WINDOW_SIZE = BOARD_PADDING * 2 + CELL_SIZE * (BOARD_SIZE - 1)
BUTTON_HEIGHT = 40
INFO_HEIGHT = 80
TOTAL_HEIGHT = WINDOW_SIZE + BUTTON_HEIGHT + INFO_HEIGHT

# Color definitions, easy on the eyes~
BACKGROUND = (220, 179, 92)
LINE_COLOR = (0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
GREEN = (0, 150, 0)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 149, 237)
INFO_BG = (50, 50, 50)

# Create window, let's work~
screen = pygame.display.set_mode((WINDOW_SIZE, TOTAL_HEIGHT))
pygame.display.set_caption("Gomoku Game")

# Fonts, clarity is important~
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 36)

# Piece scoring rules, very important~
PATTERN_SCORES = {
    'FIVE': 1000000,
    'LIVE_FOUR': 100000,
    'FOUR': 10000,
    'LIVE_THREE': 1000,
    'THREE': 100,
    'LIVE_TWO': 10,
    'TWO': 5,
    'ONE': 1
}

class Game:
    def __init__(self):
        self.board = self.reset_board()
        self.current_player = 'X'  # Player moves first, fair game~
        self.history = []  # Move history, don't forget~
        self.win_probability = {'X': 0, 'O': 0}  # Win probability for both sides
        self.move_history = []  # Game record moves
        self.start_time = None  # Game start time
        self.game_record = {
            'metadata': {
                'date': '',
                'players': {'X': 'Player', 'O': 'Computer'},
                'result': 'Unfinished'
            },
            'moves': []
        }
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.message = "Welcome to play Gomoku!"
        self.hover_pos = None
        self.buttons = {
            'undo': {'rect': pygame.Rect(20, WINDOW_SIZE + 10, 80, BUTTON_HEIGHT), 'text': 'Undo'},
            'save': {'rect': pygame.Rect(120, WINDOW_SIZE + 10, 80, BUTTON_HEIGHT), 'text': 'Save'},
            'replay': {'rect': pygame.Rect(220, WINDOW_SIZE + 10, 80, BUTTON_HEIGHT), 'text': 'Restart'},
            'exit': {'rect': pygame.Rect(320, WINDOW_SIZE + 10, 80, BUTTON_HEIGHT), 'text': 'Exit'}
        }

    def reset_board(self):
        # Reset the board to empty state
        return [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def draw_board(self):
        # Draw board background, pretty~
        screen.fill(BACKGROUND)
        
        # Draw grid lines carefully~
        for i in range(BOARD_SIZE):
            # Horizontal lines
            pygame.draw.line(screen, LINE_COLOR, 
                            (BOARD_PADDING, BOARD_PADDING + i * CELL_SIZE), 
                            (BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE), 
                            2)
            # Vertical lines
            pygame.draw.line(screen, LINE_COLOR, 
                            (BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING), 
                            (BOARD_PADDING + i * CELL_SIZE, BOARD_PADDING + (BOARD_SIZE - 1) * CELL_SIZE), 
                            2)
        
        # Draw five special points on the board
        points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for point in points:
            x, y = point
            pygame.draw.circle(screen, BLACK, 
                             (BOARD_PADDING + x * CELL_SIZE, BOARD_PADDING + y * CELL_SIZE), 
                             5)
        
        # Draw pieces on the board
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 'X':
                    pygame.draw.circle(screen, BLACK, 
                                     (BOARD_PADDING + j * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE), 
                                     CELL_SIZE // 2 - 2)
                elif self.board[i][j] == 'O':
                    pygame.draw.circle(screen, WHITE, 
                                     (BOARD_PADDING + j * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE), 
                                     CELL_SIZE // 2 - 2)
                    pygame.draw.circle(screen, BLACK, 
                                     (BOARD_PADDING + j * CELL_SIZE, BOARD_PADDING + i * CELL_SIZE), 
                                     CELL_SIZE // 2 - 2, 1)
        
        # Highlight the last move with a red or blue dot
        if self.last_move:
            row, col, player = self.last_move
            pygame.draw.circle(screen, RED if player == 'X' else BLUE, 
                             (BOARD_PADDING + col * CELL_SIZE, BOARD_PADDING + row * CELL_SIZE), 
                             5)
        
        # Show hover position with a green dot if valid
        if self.hover_pos and not self.game_over:
            row, col = self.hover_pos
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.board[row][col] == '.':
                pygame.draw.circle(screen, GREEN, 
                                 (BOARD_PADDING + col * CELL_SIZE, BOARD_PADDING + row * CELL_SIZE), 
                                 5)
    
    def draw_info_panel(self):
        # Draw info panel background
        pygame.draw.rect(screen, INFO_BG, (0, WINDOW_SIZE, WINDOW_SIZE, BUTTON_HEIGHT + INFO_HEIGHT))
        
        # Draw buttons for user interaction
        for name, button in self.buttons.items():
            color = BUTTON_HOVER if button['rect'].collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
            pygame.draw.rect(screen, color, button['rect'], border_radius=5)
            text = font.render(button['text'], True, WHITE)
            screen.blit(text, (button['rect'].centerx - text.get_width() // 2, 
                             button['rect'].centery - text.get_height() // 2))
        
        # Draw current game status
        status_text = f"Current Player: {'Player (X)' if self.current_player == 'X' else 'Computer (O)'}"
        if self.game_over:
            if self.winner == 'X':
                status_text = "Player wins!"
            elif self.winner == 'O':
                status_text = "Computer wins!"
            else:
                status_text = "Game Over!"
        
        status_surf = font.render(status_text, True, WHITE)
        screen.blit(status_surf, (420, WINDOW_SIZE + 15))
        
        # Draw win probability info
        prob_text = f"Win Probability: Player {self.win_probability['X']}% - Computer {self.win_probability['O']}%"
        prob_surf = font.render(prob_text, True, WHITE)
        screen.blit(prob_surf, (420, WINDOW_SIZE + 45))
        
        # Draw messages to user
        msg_surf = font.render(self.message, True, GREEN)
        screen.blit(msg_surf, (20, WINDOW_SIZE + BUTTON_HEIGHT + 20))
    
    def check_win(self, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Check forward direction
            for i in range(1, 5):
                r, c = row + i * dr, col + i * dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                    count += 1
                else:
                    break
            # Check backward direction
            for i in range(1, 5):
                r, c = row - i * dr, col - i * dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def evaluate_pattern(self, count, open_ends):
        # Simple evaluation scoring
        if count >= 5:
            return PATTERN_SCORES['FIVE']
        if count == 4:
            if open_ends == 2:
                return PATTERN_SCORES['LIVE_FOUR']
            elif open_ends == 1:
                return PATTERN_SCORES['FOUR']
        if count == 3:
            if open_ends == 2:
                return PATTERN_SCORES['LIVE_THREE']
            elif open_ends == 1:
                return PATTERN_SCORES['THREE']
        if count == 2:
            if open_ends == 2:
                return PATTERN_SCORES['LIVE_TWO']
            elif open_ends == 1:
                return PATTERN_SCORES['TWO']
        if count == 1:
            return PATTERN_SCORES['ONE']
        return 0

    def evaluate_position(self, row, col, player):
        total_score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 0
            open_ends = 0
            
            # Forward count
            i = 1
            while True:
                r, c = row + i * dr, col + i * dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if self.board[r][c] == player:
                        count += 1
                        i += 1
                    elif self.board[r][c] == '.':
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break
            
            # Backward count
            i = 1
            while True:
                r, c = row - i * dr, col - i * dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if self.board[r][c] == player:
                        count += 1
                        i += 1
                    elif self.board[r][c] == '.':
                        open_ends += 1
                        break
                    else:
                        break
                else:
                    break

            total_score += self.evaluate_pattern(count + 1, open_ends)  # +1 for this position
        return total_score

    def get_valid_moves(self):
        valid_moves = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == '.':
                    valid_moves.append((i, j))
        return valid_moves

    def get_best_move(self):
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            # No moves, pick center
            return (BOARD_SIZE // 2, BOARD_SIZE // 2)

        best_score = -float('inf')
        best_move = random.choice(valid_moves)

        for (row, col) in valid_moves:
            attack_score = self.evaluate_position(row, col, 'O')
            defense_score = self.evaluate_position(row, col, 'X')

            # If can win or must block, do it
            if attack_score >= PATTERN_SCORES['FIVE']:
                return (row, col)
            if defense_score >= PATTERN_SCORES['FIVE']:
                return (row, col)

            total_score = attack_score * 1.3 + defense_score * 1.0
            if total_score > best_score:
                best_score = total_score
                best_move = (row, col)

        return best_move

    def make_move(self, row, col, player):
        if self.board[row][col] == '.' and not self.game_over:
            self.board[row][col] = player
            self.history.append((row, col, player))
            self.last_move = (row, col, player)
            self.move_history.append({'player': player, 'row': row, 'col': col})
            self.game_record['moves'].append({'player': player, 'row': row, 'col': col})
            self.message = f"{'Player' if player == 'X' else 'Computer'} placed at ({row}, {col})"

            if self.check_win(row, col, player):
                self.game_over = True
                self.winner = player
                self.message = f"{'Player' if player == 'X' else 'Computer'} wins! Congratulations!"
                self.game_record['metadata']['result'] = f"{player} wins"
            else:
                total_moves = len(self.history)
                win_rate_x = max(0, 50 - total_moves)
                win_rate_o = max(0, 50 - win_rate_x)
                self.win_probability = {'X': win_rate_x, 'O': win_rate_o}

                self.current_player = 'O' if player == 'X' else 'X'
                if self.current_player == 'O':
                    self.message = "Computer's turn, please wait..."

    def undo_move(self):
        if self.history and not self.game_over:
            last_move = self.history.pop()
            row, col, player = last_move
            self.board[row][col] = '.'
            self.move_history.pop()
            self.game_record['moves'].pop()
            self.current_player = player
            self.message = f"Undo successful, it's {'Player' if player == 'X' else 'Computer'}'s turn!"
            self.last_move = self.history[-1] if self.history else None

    def save_game_record(self):
        if not os.path.exists('records'):
            os.mkdir('records')
        now = datetime.now()
        filename = now.strftime("records/gomoku_%Y%m%d_%H%M%S.json")
        import json
        self.game_record['metadata']['date'] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.game_record['metadata']['players']['X'] = 'Player'
        self.game_record['metadata']['players']['O'] = 'Computer'
        if self.winner:
            self.game_record['metadata']['result'] = f"{self.winner} wins"
        else:
            self.game_record['metadata']['result'] = "Unfinished"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.game_record, f, ensure_ascii=False, indent=2)
        self.message = f"Game record saved to {filename}!"

    def replay_game(self):
        self.board = self.reset_board()
        self.current_player = 'X'
        self.history = []
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.message = "Game restarted, get ready!"

    def handle_click(self, pos):
        if self.game_over:
            self.message = "Game over, please restart to play again."
            return

        x, y = pos
        # Check if clicked a button first
        for name, button in self.buttons.items():
            if button['rect'].collidepoint(pos):
                if name == 'undo':
                    self.undo_move()
                elif name == 'save':
                    self.save_game_record()
                elif name == 'replay':
                    self.replay_game()
                elif name == 'exit':
                    pygame.quit()
                    sys.exit()
                return

        # Handle placing piece on board
        col = round((x - BOARD_PADDING) / CELL_SIZE)
        row = round((y - BOARD_PADDING) / CELL_SIZE)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.board[row][col] == '.' and self.current_player == 'X':
                self.make_move(row, col, 'X')

    def ai_move(self):
        if self.game_over or self.current_player != 'O':
            return
        time.sleep(0.5)  # Fake thinking time
        row, col = self.get_best_move()
        self.make_move(row, col, 'O')

    def update_hover(self):
        if self.game_over or self.current_player != 'X':
            self.hover_pos = None
            return
        x, y = pygame.mouse.get_pos()
        col = round((x - BOARD_PADDING) / CELL_SIZE)
        row = round((y - BOARD_PADDING) / CELL_SIZE)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.board[row][col] == '.':
                self.hover_pos = (row, col)
            else:
                self.hover_pos = None
        else:
            self.hover_pos = None

def main():
    game = Game()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
        
        game.update_hover()
        game.ai_move()
        game.draw_board()
        game.draw_info_panel()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
