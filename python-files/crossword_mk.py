# -*- coding: utf-8 -*-
# crossword_mk.py

GRID_SIZE = 20
EMPTY = "."

class WordPlacement:
    def __init__(self, word, row, col, direction):
        self.word = word
        self.row = row
        self.col = col
        self.direction = direction  # 'H' or 'V'

def create_empty_grid(size):
    return [[EMPTY for _ in range(size)] for _ in range(size)]

def place_word(grid, word, row, col, direction):
    for i, char in enumerate(word):
        r = row + (i if direction == 'V' else 0)
        c = col + (i if direction == 'H' else 0)
        grid[r][c] = char

def can_place(grid, word, row, col, direction):
    for i, char in enumerate(word):
        r = row + (i if direction == 'V' else 0)
        c = col + (i if direction == 'H' else 0)
        if r >= GRID_SIZE or c >= GRID_SIZE:
            return False
        if grid[r][c] not in (EMPTY, char):
            return False
    return True

def try_place_words(words):
    grid = create_empty_grid(GRID_SIZE)
    placements = []

    first_word = words[0]
    mid = GRID_SIZE // 2
    col = mid - len(first_word) // 2
    place_word(grid, first_word, mid, col, 'H')
    placements.append(WordPlacement(first_word, mid, col, 'H'))

    for word in words[1:]:
        placed = False
        for placed_word in placements:
            for i, c1 in enumerate(word):
                for j, c2 in enumerate(placed_word.word):
                    if c1 == c2:
                        if placed_word.direction == 'H':
                            row = placed_word.row - i
                            col = placed_word.col + j
                            if can_place(grid, word, row, col, 'V'):
                                place_word(grid, word, row, col, 'V')
                                placements.append(WordPlacement(word, row, col, 'V'))
                                placed = True
                                break
                        else:
                            row = placed_word.row + j
                            col = placed_word.col - i
                            if can_place(grid, word, row, col, 'H'):
                                place_word(grid, word, row, col, 'H')
                                placements.append(WordPlacement(word, row, col, 'H'))
                                placed = True
                                break
                if placed:
                    break
            if placed:
                break
        if not placed:
            print(f"Не може да се смести: {word}")
    return grid

def print_grid(grid):
    for row in grid:
        print(" ".join(row))

if __name__ == "__main__":
    with open("words.txt", "r", encoding="utf-8") as file:
        words = [line.strip() for line in file if line.strip()]
    grid = try_place_words(words)
    print_grid(grid)
