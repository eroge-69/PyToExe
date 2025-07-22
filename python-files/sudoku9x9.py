import random

# Board sizeunits
SIZE = 9
BOX = 3
ALL_DIGITS = (1  SIZE) - 1  # Bitmask with bits 0..8 set 0b111111111 = 511

def bit_to_digits(bits)
    Convert bitmask to list of digits.
    return [d+1 for d in range(SIZE) if bits & (1  d)]

def digit_to_bit(d)
    Digit (1-9) to bitmask bit.
    return 1  (d - 1)

def count_bits(bits)
    Count number of 1 bits in bits (candidates count).
    return bin(bits).count('1')

def lowest_bit(bits)
    Return lowest bit's digit (only call if count_bits == 1).
    return (bits & -bits).bit_length()  # bit_length returns 1-based index of highest set bit
                                          # but we want digit where 1 (digit-1) set
                                          # So digit = bit_length(bits & -bits)
                                          # Since digit = position of lowest set bit
                                          # E.g. bits=0b000001000, bits & -bits = 0b000001000
                                          # bit_length=4 means digit=4
                                          # We want digit = bit_length(bits & -bits)
                                          # So safe

def peers_of_cell(row, col)
    Return set of peer coordinates for given cell.
    peers = set()
    for i in range(SIZE)
        if i != col
            peers.add((row, i))
        if i != row
            peers.add((i, col))
    # 3x3 box peers
    box_row_start = (row  BOX)  BOX
    box_col_start = (col  BOX)  BOX
    for r in range(box_row_start, box_row_start + BOX)
        for c in range(box_col_start, box_col_start + BOX)
            if (r, c) != (row, col)
                peers.add((r, c))
    return peers

PEERS = [[peers_of_cell(r, c) for c in range(SIZE)] for r in range(SIZE)]

def units_of_cell(row, col)
    Return units (row, col, box) of cell.
    units = []
    # Row unit
    units.append({(row, c) for c in range(SIZE)})
    # Col unit
    units.append({(r, col) for r in range(SIZE)})
    # Box unit
    box_row_start = (row  BOX)  BOX
    box_col_start = (col  BOX)  BOX
    units.append({(r, c) for r in range(box_row_start, box_row_start + BOX)
                          for c in range(box_col_start, box_col_start + BOX)})
    return units

UNITS = [[units_of_cell(r, c) for c in range(SIZE)] for r in range(SIZE)]

class Sudoku
    def __init__(self, board=None)
        # For each cell, store candidate bits (initially all digits possible for empty)
        # If board given, set assigned digits and propagate constraints
        self.candidates = [[ALL_DIGITS for _ in range(SIZE)] for _ in range(SIZE)]
        if board
            for r in range(SIZE)
                for c in range(SIZE)
                    val = board[r][c]
                    if val != 0
                        if not self.assign(r, c, val)
                            raise ValueError(Invalid board with conflicts)

    def assign(self, row, col, digit)
        Assign digit to cell and propagate constraints.
        Return False if contradiction found.
        other_bits = self.candidates[row][col] & ~digit_to_bit(digit)
        # Eliminate all other digits except assigned one
        for d in bit_to_digits(other_bits)
            if not self.eliminate(row, col, d)
                return False
        return True

    def eliminate(self, row, col, digit)
        Eliminate digit from candidates of cell.
        If contradiction found, return False.
        bit = digit_to_bit(digit)
        if (self.candidates[row][col] & bit) == 0
            # Already eliminated
            return True

        self.candidates[row][col] &= ~bit
        n = count_bits(self.candidates[row][col])
        if n == 0
            # No candidates left contradiction
            return False
        elif n == 1
            # Only one candidate left, assign it and propagate to peers
            last_digit = bit_to_digits(self.candidates[row][col])[0]
            for (pr, pc) in PEERS[row][col]
                if not self.eliminate(pr, pc, last_digit)
                    return False

        # Check units for unit constraint propagation
        for unit in UNITS[row][col]
            places = [ (r,c) for (r,c) in unit if (self.candidates[r][c] & bit) != 0 ]
            if len(places) == 0
                # Digit cannot be placed anywhere in unit failure
                return False
            elif len(places) == 1
                r, c = places[0]
                # If digit not yet assigned in this cell, assign it now
                if count_bits(self.candidates[r][c])  1
                    if not self.assign(r, c, digit)
                        return False
        return True

    def is_solved(self)
        Check if fully solved.
        return all(count_bits(self.candidates[r][c]) == 1 for r in range(SIZE) for c in range(SIZE))

    def find_min_candidate_cell(self)
        Find cell with smallest candidate count  1 to branch on.
        min_count = 10
        target = None
        for r in range(SIZE)
            for c in range(SIZE)
                n = count_bits(self.candidates[r][c])
                if 1  n  min_count
                    min_count = n
                    target = (r, c)
        return target

    def to_board(self)
        Return current board as 2D list with digits or 0.
        board = [[0]SIZE for _ in range(SIZE)]
        for r in range(SIZE)
            for c in range(SIZE)
                if count_bits(self.candidates[r][c]) == 1
                    board[r][c] = bit_to_digits(self.candidates[r][c])[0]
        return board

    def solve(self)
        Solve with constraint propagation and backtracking.

        if self.is_solved()
            return True

        pos = self.find_min_candidate_cell()
        if not pos
            # No place to assign but not solved Contradiction.
            return False
        r, c = pos
        bits = self.candidates[r][c]
        digits = bit_to_digits(bits)
        for d in digits
            # Create a copy to try assignment
            snapshot = [row[] for row in self.candidates]
            if self.assign(r, c, d)
                if self.solve()
                    return True
            # Restore on failure
            self.candidates = [row[] for row in snapshot]
        return False

def generate_full_board()
    Generate a completely filled valid Sudoku board using Sudoku class.
    sudoku = Sudoku()
    # Fill cells randomly by assigning on empty
    def fill()
        pos = sudoku.find_min_candidate_cell()
        if not pos
            return True
        r, c = pos
        candidates = bit_to_digits(sudoku.candidates[r][c])
        random.shuffle(candidates)
        for d in candidates
            snapshot = [row[] for row in sudoku.candidates]
            if sudoku.assign(r, c, d)
                if fill()
                    return True
            sudoku.candidates = [row[] for row in snapshot]
        return False
    fill()
    return sudoku.to_board()

def count_solutions(board, max_count=2)
    Count number of solutions using Sudoku solver with early exit.
    sudoku = Sudoku(board)
    count = 0

    def helper()
        nonlocal count
        if count = max_count
            return
        if sudoku.is_solved()
            count += 1
            return
        pos = sudoku.find_min_candidate_cell()
        if not pos
            return
        r, c = pos
        for d in bit_to_digits(sudoku.candidates[r][c])
            snapshot = [row[] for row in sudoku.candidates]
            if sudoku.assign(r, c, d)
                helper()
            sudoku.candidates = [row[] for row in snapshot]

    helper()
    return count

def generate_sudoku(clues)
    board = generate_full_board()
    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(positions)
    removed = 0
    max_removed = 81 - clues
    for r, c in positions
        if removed = max_removed
            break
        backup = board[r][c]
        board[r][c] = 0
        # Ensure uniqueness
        if count_solutions(board, max_count=2) != 1
            board[r][c] = backup
        else
            removed += 1
    return board

def print_board(board)
    for row in board
        print( .join(str(cell) if cell != 0 else . for cell in row))

def create_sudoku(level='easy')
    if level == 'easy'
        clues = random.randint(36, 49)
    elif level == 'hard'
        clues = random.randint(27, 31)
    elif level == 'difficult'
        clues = random.randint(17, 26)
    else
        clues = 36
    puzzle = generate_sudoku(clues)
    print(fSudoku ({level}, {clues} clues))
    print_board(puzzle)

if __name__ == __main__
    create_sudoku('easy')
    create_sudoku('hard')
    create_sudoku('difficult')