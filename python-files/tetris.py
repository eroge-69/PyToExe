import tkinter as tk
import random

CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
DELAY = 500  # Initial delay in ms

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

COLORS = {
    'I': 'cyan', 'O': 'yellow', 'T': 'purple',
    'S': 'green', 'Z': 'red', 'J': 'blue', 'L': 'orange'
}

class Tetris:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLUMNS*CELL_SIZE+150, height=ROWS*CELL_SIZE, bg='black')
        self.canvas.pack()
        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.delay = DELAY
        self.running = True

        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.draw_score()
        self.draw_next_piece()
        self.root.bind("<Key>", self.key_pressed)
        self.drop()

    def new_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        return {
            'shape': SHAPES[shape],
            'color': COLORS[shape],
            'x': COLUMNS // 2 - len(SHAPES[shape][0]) // 2,
            'y': 0,
            'type': shape
        }

    def draw_score(self):
        self.canvas.delete("score")
        self.canvas.create_text(COLUMNS*CELL_SIZE + 75, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 14), tags="score")
        self.canvas.create_text(COLUMNS*CELL_SIZE + 75, 50, text=f"Level: {self.level}", fill="white", font=("Arial", 14), tags="score")

    def draw_next_piece(self):
        self.canvas.delete("next")
        self.canvas.create_text(COLUMNS*CELL_SIZE + 75, 100, text="Next:", fill="white", font=("Arial", 14), tags="next")
        shape = self.next_piece['shape']
        color = self.next_piece['color']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.canvas.create_rectangle(
                        COLUMNS*CELL_SIZE + 50 + x*CELL_SIZE//2,
                        120 + y*CELL_SIZE//2,
                        COLUMNS*CELL_SIZE + 50 + (x+1)*CELL_SIZE//2,
                        120 + (y+1)*CELL_SIZE//2,
                        fill=color, tags="next"
                    )

    def draw_board(self):
        self.canvas.delete("block")
        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.board[y][x]:
                    self.canvas.create_rectangle(
                        x*CELL_SIZE, y*CELL_SIZE,
                        (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                        fill=self.board[y][x], tags="block"
                    )
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.canvas.create_rectangle(
                        (self.current_piece['x'] + x)*CELL_SIZE,
                        (self.current_piece['y'] + y)*CELL_SIZE,
                        (self.current_piece['x'] + x + 1)*CELL_SIZE,
                        (self.current_piece['y'] + y + 1)*CELL_SIZE,
                        fill=color, tags="block"
                    )

    def key_pressed(self, event):
        if not self.running:
            return
        if event.keysym == 'Left':
            self.move(-1)
        elif event.keysym == 'Right':
            self.move(1)
        elif event.keysym == 'Down':
            self.drop_piece()
        elif event.keysym == 'Up':
            self.rotate()

    def move(self, dx):
        self.current_piece['x'] += dx
        if self.collision():
            self.current_piece['x'] -= dx
        self.draw_board()

    def rotate(self):
        shape = self.current_piece['shape']
        rotated = [list(row) for row in zip(*shape[::-1])]
        old = self.current_piece['shape']
        self.current_piece['shape'] = rotated
        if self.collision():
            self.current_piece['shape'] = old
        self.draw_board()

    def drop_piece(self):
        self.current_piece['y'] += 1
        if self.collision():
            self.current_piece['y'] -= 1
            self.lock_piece()
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            self.draw_next_piece()
            if self.collision():
                self.running = False
                self.canvas.create_text(COLUMNS*CELL_SIZE//2, ROWS*CELL_SIZE//2, text="GAME OVER", fill="white", font=("Arial", 24))
        self.draw_board()

    def drop(self):
        if self.running:
            self.drop_piece()
            self.root.after(self.delay, self.drop)

    def collision(self):
        shape = self.current_piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece['x'] + x
                    py = self.current_piece['y'] + y
                    if px < 0 or px >= COLUMNS or py >= ROWS or (py >= 0 and self.board[py][px]):
                        return True
        return False

    def lock_piece(self):
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece['x'] + x
                    py = self.current_piece['y'] + y
                    if 0 <= py < ROWS and 0 <= px < COLUMNS:
                        self.board[py][px] = color

    def clear_lines(self):
        new_board = []
        lines = 0
        for row in self.board:
            if all(row):
                lines += 1
            else:
                new_board.append(row)
        for _ in range(lines):
            new_board.insert(0, [None for _ in range(COLUMNS)])
        self.board = new_board
        self.score += lines * 100
        if lines:
            self.level = 1 + self.score // 500
            self.delay = max(100, DELAY - (self.level - 1) * 30)
        self.draw_score()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tetris (tkinter edition)")
    game = Tetris(root)
    root.mainloop()
