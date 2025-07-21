import pygame
import random
import sys

# Inisialisasi PyGame
pygame.init()

# Konstanta permainan
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 7  # Diperlambat dari 10 menjadi 7

# Warna
BACKGROUND = (15, 15, 25)
GRID_COLOR = (30, 30, 40)
SNAKE_COLOR = (100, 230, 100)
FOOD_COLOR = (230, 100, 100)
TEXT_COLOR = (220, 220, 220)

# Arah
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        
        # Buat tubuh ular awal
        for i in range(1, self.length):
            self.positions.append(
                (self.positions[0][0] - self.direction[0] * i, 
                 self.positions[0][1] - self.direction[1] * i)
            )
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = (((head[0] + x) % GRID_WIDTH), (head[1] + y) % GRID_HEIGHT)
        
        if new_position in self.positions[1:]:
            self.reset()
        else:
            self.positions.insert(0, new_position)
            if len(self.positions) > self.length:
                self.positions.pop()
    
    def grow(self):
        self.length += 1
        self.score += 10
    
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            color = SNAKE_COLOR if i == 0 else (SNAKE_COLOR[0] - 20, SNAKE_COLOR[1] - 20, SNAKE_COLOR[2])
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (30, 30, 30), rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
    
    def draw(self, surface):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(surface, FOOD_COLOR, rect)
        pygame.draw.rect(surface, (150, 50, 50), rect, 1)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Permainan Ular by SYIHAB TEKNIK")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)
    
    snake = Snake()
    food = Food()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == pygame.K_r:
                    snake.reset()
                    food.randomize_position()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Tombol + untuk percepat
                    global FPS
                    FPS = min(20, FPS + 1)  # Batas maksimum 20
                elif event.key == pygame.K_MINUS:  # Tombol - untuk perlambat
                    FPS = max(3, FPS - 1)  # Batas minimum 3
        
        snake.update()
        
        # Cek apakah ular makan makanan
        if snake.get_head_position() == food.position:
            snake.grow()
            food.randomize_position()
            # Pastikan makanan tidak muncul di tubuh ular
            while food.position in snake.positions:
                food.randomize_position()
        
        # Gambar latar belakang
        screen.fill(BACKGROUND)
        draw_grid(screen)
        
        # Gambar objek
        snake.draw(screen)
        food.draw(screen)
        
        # Gambar skor
        score_text = font.render(f'Skor: {snake.score}', True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        
        # Instruksi
        instructions = font.render('Tekan R: reset | +: cepat | -: lambat', True, TEXT_COLOR)
        screen.blit(instructions, (WIDTH - instructions.get_width() - 10, 10))
        
        # Tampilkan kecepatan saat ini
        speed_text = font.render(f'Kecepatan: {FPS}', True, TEXT_COLOR)
        screen.blit(speed_text, (10, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()