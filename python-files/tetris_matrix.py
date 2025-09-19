import pygame
import random
import asyncio
import platform
import time

# Initialize Pygame with error handling
try:
    pygame.init()
    pygame.mixer.init()  # For sound effects
except Exception as e:
    print(f"Pygame initialization failed: {e}")
    exit(1)

# Constants
GRID_WIDTH, GRID_HEIGHT = 10, 20
BLOCK_SIZE = 30
SCREEN_WIDTH = 800  # Adjusted for fullscreen layout
SCREEN_HEIGHT = 900
GRID_OFFSET_X = 100
GRID_OFFSET_Y = 50
PREVIEW_OFFSET_X = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 40
PREVIEW_OFFSET_Y = GRID_OFFSET_Y + 50
HOLD_OFFSET_X = GRID_OFFSET_X - 180
HOLD_OFFSET_Y = GRID_OFFSET_Y + 50

# Colors (Matrix theme: neon green, black)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BRIGHT_GREEN = (100, 255, 100)
WHITE = (255, 255, 255)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]
SHAPE_COLORS = [GREEN for _ in SHAPES]

# Font
try:
    FONT = pygame.font.SysFont('consolas', 24)
    LARGE_FONT = pygame.font.SysFont('consolas', 48)
except:
    FONT = pygame.font.SysFont('monospace', 24)
    LARGE_FONT = pygame.font.SysFont('monospace', 48)

# Digital rain effect (optimized)
class DigitalRain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.columns = width // 15  # Fewer columns for performance
        self.drops = [random.randint(-height, 0) for _ in range(self.columns)]
        self.chars = [random.choice('01') for _ in range(self.columns)]  # Binary rain for Matrix feel
        self.speeds = [random.randint(5, 15) for _ in range(self.columns)]
        self.brightness = [random.randint(50, 255) for _ in range(self.columns)]

    def update(self):
        for i in range(self.columns):
            self.drops[i] += self.speeds[i]
            if self.drops[i] > self.height:
                self.drops[i] = random.randint(-100, 0)
                self.chars[i] = random.choice('01')
                self.speeds[i] = random.randint(5, 15)
                self.brightness[i] = random.randint(50, 255)
            # Randomly change brightness
            if random.random() < 0.05:
                self.brightness[i] = max(50, min(255, self.brightness[i] + random.randint(-20, 20)))

    def draw(self, screen):
        for i in range(self.columns):
            color = (0, self.brightness[i], 0)
            text = FONT.render(self.chars[i], True, color)
            screen.blit(text, (i * 15, self.drops[i]))

class Tetris:
    def __init__(self):
        try:
            # Try to create a fullscreen display first
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True
            self.actual_width, self.actual_height = self.screen.get_size()
            
            # Adjust positions based on actual screen size
            global GRID_OFFSET_X, GRID_OFFSET_Y, PREVIEW_OFFSET_X, PREVIEW_OFFSET_Y, HOLD_OFFSET_X, HOLD_OFFSET_Y
            GRID_OFFSET_X = self.actual_width // 2 - (GRID_WIDTH * BLOCK_SIZE) // 2
            GRID_OFFSET_Y = 50
            PREVIEW_OFFSET_X = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 40
            PREVIEW_OFFSET_Y = GRID_OFFSET_Y + 50
            HOLD_OFFSET_X = GRID_OFFSET_X - 180
            HOLD_OFFSET_Y = GRID_OFFSET_Y + 50
            
        except:
            # Fallback to windowed mode if fullscreen fails
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fullscreen = False
            self.actual_width, self.actual_height = SCREEN_WIDTH, SCREEN_HEIGHT
            
        pygame.display.set_caption("Matrix Tetris")
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.digital_rain = DigitalRain(self.actual_width, self.actual_height)
        self.reset_game()
        
        # Enable key repeat
        pygame.key.set_repeat(200, 50)  # 200ms delay, 50ms interval
        
        # Load sounds
        self.sounds = {
            'rotate': None,
            'move': None,
            'drop': None,
            'clear': None,
            'gameover': None
        }
        self.load_sounds()

    def load_sounds(self):
        # Create simple sound effects programmatically
        try:
            # Rotate sound
            rotate_sound = pygame.mixer.Sound(buffer=bytearray([random.randint(0, 255) for _ in range(1024)]))
            rotate_sound.set_volume(0.3)
            self.sounds['rotate'] = rotate_sound
            
            # Move sound
            move_sound = pygame.mixer.Sound(buffer=bytearray([random.randint(0, 100) for _ in range(512)]))
            move_sound.set_volume(0.2)
            self.sounds['move'] = move_sound
            
            # Drop sound
            drop_sound = pygame.mixer.Sound(buffer=bytearray([random.randint(150, 255) for _ in range(2048)]))
            drop_sound.set_volume(0.4)
            self.sounds['drop'] = drop_sound
            
            # Line clear sound
            clear_sound = pygame.mixer.Sound(buffer=bytearray([min(255, i*10) for i in range(256)] + [max(0, 255-i*10) for i in range(256)]))
            clear_sound.set_volume(0.5)
            self.sounds['clear'] = clear_sound
            
            # Game over sound
            gameover_sound = pygame.mixer.Sound(buffer=bytearray([255 - i for i in range(512)]))
            gameover_sound.set_volume(0.6)
            self.sounds['gameover'] = gameover_sound
        except:
            # Sound initialization failed, continue without sound
            self.sounds = {k: None for k in self.sounds}

    def play_sound(self, sound_name):
        if self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass

    def reset_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_pieces = [self.new_piece() for _ in range(3)]
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = 1000  # Start at 1000ms per row
        self.last_move_down_time = 0
        self.last_rotate_time = 0
        self.last_side_move_time = 0

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        return {
            'shape': [row[:] for row in shape],  # Copy to avoid modifying original
            'color': SHAPE_COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': -len(shape)  # Start above grid to avoid overlap
        }

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = y + i
                    grid_x = x + j
                    if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                        return False
                    if grid_y >= 0 and self.grid[grid_y][grid_x] != BLACK:
                        return False
        return True

    def merge_piece(self):
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece['y'] + i
                    if grid_y < 0:  # Piece is above grid and can't move down
                        self.game_over = True
                        self.play_sound('gameover')
                        return
                    self.grid[grid_y][self.current_piece['x'] + j] = self.current_piece['color']
        self.clear_lines()
        self.current_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.new_piece())
        self.can_hold = True
        if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
            self.game_over = True
            self.play_sound('gameover')

    def clear_lines(self):
        lines = 0
        new_grid = [row for row in self.grid if any(cell == BLACK for cell in row)]
        lines = GRID_HEIGHT - len(new_grid)
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(lines)] + new_grid
        if lines > 0:
            # Scoring: 100/300/500/800 for 1/2/3/4 lines
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += line_scores.get(lines, 100) * self.level
            self.lines_cleared += lines
            self.level = 1 + self.lines_cleared // 10
            self.fall_speed = max(100, 1000 - (self.level - 1) * 100)  # Linear speed increase
            self.play_sound('clear')

    def rotate_piece(self):
        current_time = time.time()
        if current_time - self.last_rotate_time < 0.1:  # 100ms cooldown
            return
            
        piece = self.current_piece
        new_shape = list(zip(*piece['shape'][::-1]))
        temp_shape = piece['shape']
        piece['shape'] = [list(row) for row in new_shape]  # Convert tuples to lists
        if not self.valid_move(piece, piece['x'], piece['y']):
            # Try wall kicks
            for offset in [-1, 1, -2, 2]:
                if self.valid_move(piece, piece['x'] + offset, piece['y']):
                    piece['x'] += offset
                    break
            else:
                piece['shape'] = temp_shape
                return
                
        self.last_rotate_time = current_time
        self.play_sound('rotate')

    def hold_piece(self):
        if not self.can_hold:
            return
            
        # Find the index of the current shape in SHAPES
        current_shape = self.current_piece['shape']
        shape_idx = -1
        for i, shape in enumerate(SHAPES):
            if len(shape) == len(current_shape) and len(shape[0]) == len(current_shape[0]):
                match = True
                for row in range(len(shape)):
                    for col in range(len(shape[0])):
                        if (shape[row][col] == 1) != (current_shape[row][col] == 1):
                            match = False
                            break
                    if not match:
                        break
                if match:
                    shape_idx = i
                    break
        
        if shape_idx == -1:  # Shouldn't happen normally
            return

        if self.held_piece is None:
            self.held_piece = {
                'shape': [row[:] for row in SHAPES[shape_idx]],  # Reset to original shape
                'color': self.current_piece['color'],
                'x': 0,
                'y': 0
            }
            self.current_piece = self.next_pieces.pop(0)
            self.next_pieces.append(self.new_piece())
        else:
            self.held_piece, self.current_piece = self.current_piece, self.held_piece
            # Reset position and rotation of swapped piece
            self.current_piece['x'] = GRID_WIDTH // 2 - len(self.current_piece['shape'][0]) // 2
            self.current_piece['y'] = -len(self.current_piece['shape'])
            # Reset held piece to original shape
            self.held_piece['shape'] = [row[:] for row in SHAPES[shape_idx]]
            
        self.can_hold = False
        self.play_sound('rotate')

    def get_ghost_y(self):
        ghost_y = self.current_piece['y']
        while self.valid_move(self.current_piece, self.current_piece['x'], ghost_y + 1):
            ghost_y += 1
        return ghost_y

    def draw_grid_border(self):
        # Draw a glowing border around the grid
        border_rect = pygame.Rect(
            GRID_OFFSET_X - 5, 
            GRID_OFFSET_Y - 5, 
            GRID_WIDTH * BLOCK_SIZE + 10, 
            GRID_HEIGHT * BLOCK_SIZE + 10
        )
        
        # Draw multiple rectangles with increasing alpha for glow effect
        for i in range(1, 4):
            alpha = 100 - i * 25
            if alpha <= 0:
                continue
            s = pygame.Surface((border_rect.width + i*2, border_rect.height + i*2), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 255, 0, alpha), (0, 0, s.get_width(), s.get_height()), 2)
            self.screen.blit(s, (border_rect.x - i, border_rect.y - i))

    def draw(self):
        self.screen.fill(BLACK)
        self.digital_rain.update()
        self.digital_rain.draw(self.screen)

        # Draw grid border with glow effect
        self.draw_grid_border()

        # Draw grid
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.grid[i][j],
                               (GRID_OFFSET_X + j * BLOCK_SIZE, GRID_OFFSET_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.screen, DARK_GREEN,
                               (GRID_OFFSET_X + j * BLOCK_SIZE, GRID_OFFSET_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw ghost piece
        ghost_y = self.get_ghost_y()
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    # Create a semi-transparent surface for the ghost piece
                    s = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(s, (0, 100, 0, 150), (0, 0, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(s, (0, 200, 0, 200), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 1)
                    self.screen.blit(s, 
                                   (GRID_OFFSET_X + (self.current_piece['x'] + j) * BLOCK_SIZE,
                                    GRID_OFFSET_Y + (ghost_y + i) * BLOCK_SIZE))

        # Draw current piece
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_piece['color'],
                                   (GRID_OFFSET_X + (self.current_piece['x'] + j) * BLOCK_SIZE,
                                    GRID_OFFSET_Y + (self.current_piece['y'] + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    
                    # Add highlight to the piece
                    highlight_color = BRIGHT_GREEN
                    highlight_rect = pygame.Rect(
                        GRID_OFFSET_X + (self.current_piece['x'] + j) * BLOCK_SIZE + 2,
                        GRID_OFFSET_Y + (self.current_piece['y'] + i) * BLOCK_SIZE + 2,
                        BLOCK_SIZE - 4, 3
                    )
                    pygame.draw.rect(self.screen, highlight_color, highlight_rect)
                    
                    pygame.draw.rect(self.screen, DARK_GREEN,
                                   (GRID_OFFSET_X + (self.current_piece['x'] + j) * BLOCK_SIZE,
                                    GRID_OFFSET_Y + (self.current_piece['y'] + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw next pieces with a border
        next_border = pygame.Rect(
            PREVIEW_OFFSET_X - 10,
            PREVIEW_OFFSET_Y - 40,
            120,
            200
        )
        pygame.draw.rect(self.screen, DARK_GREEN, next_border, 2)
        
        for idx, piece in enumerate(self.next_pieces):
            for i, row in enumerate(piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, piece['color'],
                                       (PREVIEW_OFFSET_X + j * BLOCK_SIZE,
                                        PREVIEW_OFFSET_Y + (idx * 4 + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, DARK_GREEN,
                                       (PREVIEW_OFFSET_X + j * BLOCK_SIZE,
                                        PREVIEW_OFFSET_Y + (idx * 4 + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw held piece with a border
        hold_border = pygame.Rect(
            HOLD_OFFSET_X - 10,
            HOLD_OFFSET_Y - 40,
            120,
            80
        )
        pygame.draw.rect(self.screen, DARK_GREEN, hold_border, 2)
        
        if self.held_piece:
            for i, row in enumerate(self.held_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.held_piece['color'],
                                       (HOLD_OFFSET_X + j * BLOCK_SIZE,
                                        HOLD_OFFSET_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(self.screen, DARK_GREEN,
                                       (HOLD_OFFSET_X + j * BLOCK_SIZE,
                                        HOLD_OFFSET_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw UI with better formatting
        score_text = FONT.render(f"SCORE: {self.score:06d}", True, GREEN)
        level_text = FONT.render(f"LEVEL: {self.level:02d}", True, GREEN)
        lines_text = FONT.render(f"LINES: {self.lines_cleared:04d}", True, GREEN)
        next_text = FONT.render("NEXT:", True, BRIGHT_GREEN)
        hold_text = FONT.render("HOLD:", True, BRIGHT_GREEN)
        
        # Draw UI background panels
        pygame.draw.rect(self.screen, (0, 20, 0), (GRID_OFFSET_X - 5, GRID_OFFSET_Y - 40, GRID_WIDTH * BLOCK_SIZE + 10, 30))
        pygame.draw.rect(self.screen, (0, 20, 0), (PREVIEW_OFFSET_X - 10, PREVIEW_OFFSET_Y - 40, 120, 30))
        pygame.draw.rect(self.screen, (0, 20, 0), (HOLD_OFFSET_X - 10, HOLD_OFFSET_Y - 40, 120, 30))
        
        self.screen.blit(score_text, (GRID_OFFSET_X, GRID_OFFSET_Y - 35))
        self.screen.blit(level_text, (GRID_OFFSET_X + 200, GRID_OFFSET_Y - 35))
        self.screen.blit(lines_text, (GRID_OFFSET_X + 400, GRID_OFFSET_Y - 35))
        self.screen.blit(next_text, (PREVIEW_OFFSET_X, PREVIEW_OFFSET_Y - 35))
        self.screen.blit(hold_text, (HOLD_OFFSET_X, HOLD_OFFSET_Y - 35))

        if self.paused:
            # Darken the screen when paused
            s = pygame.Surface((self.actual_width, self.actual_height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (0, 0))
            
            pause_text = LARGE_FONT.render("PAUSED", True, BRIGHT_GREEN)
            resume_text = FONT.render("Press P to Resume", True, GREEN)
            self.screen.blit(pause_text, (self.actual_width // 2 - pause_text.get_width() // 2, self.actual_height // 2 - 50))
            self.screen.blit(resume_text, (self.actual_width // 2 - resume_text.get_width() // 2, self.actual_height // 2 + 20))

        if self.game_over:
            # Darken the screen when game over
            s = pygame.Surface((self.actual_width, self.actual_height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (0, 0))
            
            game_over_text = LARGE_FONT.render("GAME OVER", True, BRIGHT_GREEN)
            restart_text = FONT.render("Press R to Restart", True, GREEN)
            score_text = FONT.render(f"Final Score: {self.score}", True, GREEN)
            self.screen.blit(game_over_text, (self.actual_width // 2 - game_over_text.get_width() // 2, self.actual_height // 2 - 80))
            self.screen.blit(score_text, (self.actual_width // 2 - score_text.get_width() // 2, self.actual_height // 2 - 20))
            self.screen.blit(restart_text, (self.actual_width // 2 - restart_text.get_width() // 2, self.actual_height // 2 + 30))

        pygame.display.flip()

    async def update_loop(self):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not self.paused and not self.game_over:
                    if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                        self.current_piece['x'] -= 1
                        self.play_sound('move')
                elif event.key == pygame.K_RIGHT and not self.paused and not self.game_over:
                    if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                        self.current_piece['x'] += 1
                        self.play_sound('move')
                elif event.key == pygame.K_DOWN and not self.paused and not self.game_over:
                    if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                        self.current_piece['y'] += 1
                        self.score += 1
                        self.play_sound('move')
                elif event.key == pygame.K_UP and not self.paused and not self.game_over:
                    self.rotate_piece()
                elif event.key == pygame.K_SPACE and not self.paused and not self.game_over:
                    while self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                        self.current_piece['y'] += 1
                        self.score += 2
                    self.merge_piece()
                    self.play_sound('drop')
                elif event.key == pygame.K_c and not self.paused and not self.game_over:
                    self.hold_piece()
                elif event.key == pygame.K_p:
                    if not self.game_over:
                        self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_f:  # Toggle fullscreen
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:  # Exit fullscreen or quit
                    if self.fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.game_over = True

        if not self.paused and not self.game_over:
            self.fall_time += delta_time * 1000  # Convert to ms
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                else:
                    self.merge_piece()

        self.draw()
        self.clock.tick(60)  # Cap at 60 FPS

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fullscreen = False
            self.actual_width, self.actual_height = SCREEN_WIDTH, SCREEN_HEIGHT
        else:
            try:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.fullscreen = True
                self.actual_width, self.actual_height = self.screen.get_size()
                
                # Reinitialize digital rain with new dimensions
                self.digital_rain = DigitalRain(self.actual_width, self.actual_height)
            except:
                # If fullscreen fails, revert to windowed
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.fullscreen = False
                self.actual_width, self.actual_height = SCREEN_WIDTH, SCREEN_HEIGHT

async def main():
    game = Tetris()
    while not game.game_over:
        await game.update_loop()
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())