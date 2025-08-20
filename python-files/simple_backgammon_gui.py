import pygame
import random

# --- تنظیمات اولیه ---
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 2, 12  # ۲ ردیف، ۱۲ ستون
SQUARE_SIZE = WIDTH // COLS
FPS = 30

# رنگ‌ها
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (150, 75, 0)
BEIGE = (245, 245, 220)
RED = (200, 0, 0)

# --- کلاس مهره ---
class Piece:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

    def draw(self, win):
        radius = SQUARE_SIZE//2 - 5
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)

# --- ایجاد تخته و مهره‌ها ---
def create_pieces():
    pieces = []
    # سفید‌ها روی سمت پایین
    for i in range(15):
        row = 1
        col = i % COLS
        pieces.append(Piece(WHITE, row, col))
    # مشکی‌ها روی سمت بالا
    for i in range(15):
        row = 0
        col = i % COLS
        pieces.append(Piece(BLACK, row, col))
    return pieces

# --- رسم تخته ---
def draw_board(win):
    win.fill(BEIGE)
    for row in range(ROWS):
        for col in range(COLS):
            rect = (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            if (row+col) % 2 == 0:
                pygame.draw.rect(win, BROWN, rect)
            else:
                pygame.draw.rect(win, BEIGE, rect)

# --- برنامه اصلی ---
def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('تخته‌نرد ساده')
    clock = pygame.time.Clock()

    pieces = create_pieces()
    selected = None

    font = pygame.font.SysFont(None, 40)
    roll = (0,0)

    run = True
    while run:
        clock.tick(FPS)
        draw_board(win)

        # رسم مهره‌ها
        for piece in pieces:
            piece.draw(win)

        # متن تاس
        text = font.render(f'Toss: {roll[0]}, {roll[1]}', True, RED)
        win.blit(text, (10, HEIGHT-50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                # انتخاب مهره
                for piece in pieces:
                    if piece.row == row and piece.col == col:
                        selected = piece
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    selected.row = row
                    selected.col = col
                    selected.calc_pos()
                    selected = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    roll = (random.randint(1,6), random.randint(1,6))

    pygame.quit()

if __name__ == '__main__':
    main()
