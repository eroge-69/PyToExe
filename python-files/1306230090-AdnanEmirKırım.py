# 1306230090-Adnan Emir Kırım
# Bilgisayar Mühendisliği 2. Sınıf Bahar Dönemi
# File Organization dersi Lab Projesi
# Ship Game

# 10x10 board
def create_board():
    return [['.' for _ in range(10)] for _ in range(10)]

# write board
def write_to_board(board, filename):
    with open(filename, 'w') as file:
        file.write(" " + " ".join(str(i) for i in range(1, 11)) + "\n")
        for i, row in enumerate(board):
            file.write(chr(ord('A') + i) + " " + " " .join(row) + "\n")
# print
def print_board(board):
    print("  " + " ".join(str(i) for i in range(1, 11)))
    for i,row in enumerate(board):
        print(chr(ord('A') + i) + " " + " ".join(row))
# coordinate -> board
def coordinate(coord):
    row=ord(coord[0].upper()) - ord('A')
    col=int(coord[1:]) - 1
    return row,col
def valid_coordinate(coord):
    if len(coord)<2 or len(coord) > 3:
        return False
    row_char = coord[0].upper()
    if row_char<'A' or row_char>'J':
        return False
    try:
        col_num=int(coord[1:])
        return 1<=col_num<=10
    except ValueError:
        return False
# ship coordinate
def place_ships(board):
    info=[
        ('A', 5, 1),
        ('B', 4, 1),
        ('C', 3, 2),
        ('D', 2, 2),
        ('E', 1, 3)
    ]
    for ship_char,length, count in info:
        for _ in range(count):
            while True:
                print_board(board)
                print(f"Place ship '{ship_char}' in {length} cells length")
                coords=input(f"Enter {length} coordinates for ship {ship_char}: ").split()

                if len(coords)!=length or any(not valid_coordinate(c) for c in coords):
                    print(f"Please enter {length} valid coordinates...")
                    continue

                position=[coordinate(c) for c in coords]

                if any(board[r][c]!='.' for r, c in position):
                    print("Try again, it is not available!")
                    continue
                row=[r for r, _ in position]
                col=[c for _, c in position]
                if all(r==row[0] for r in row):
                    if sorted(col)!=list(range(min(col),min(col)+length)):
                        print("Not consecutive horizontally.")
                        continue
                elif all(c==col[0] for c in col):
                    if sorted(row)!=list(range(min(row),min(row)+length)):
                        print("Not consecutive vertically.")
                        continue
                else:
                    print("The ship must be placed in a straight line.")
                    continue
                for r,c in position:
                    board[r][c]=ship_char
                break
# shoot
def shoot(board):
    while True:
        print_board(board)
        shot=input("Enter the coordinate you want to shoot: ").strip().upper()
        if not valid_coordinate(shot):
            print("Invalid coordinate. Try again.")
            continue
        row,col=coordinate(shot)
        if board[row][col] in ('X', 'O'):
            print("You already shot at this point. Try somewhere else.")
            continue
        if board[row][col]!='.':
            print("Hit!")
            board[row][col]='X'
        else:
            print("Miss.")
            board[row][col]='O'
            break
# shooting cycle
def play_game(board):
    while True:
        shoot(board)
        write_to_board(board,"aim.txt")
        if end_game_check(board):
            print("Congratulations, game over!")
            break
        while True:
            next=input("Wanna Continue?(Y/N): ").strip().upper()
            if next in ('Y','N'):
                break
            print("Please enter only 'Y' or 'N'")
        if next=='N':
            print("GAME OVER!..")
            break
# end game check
def end_game_check(board):
    return all(cell not in ['A','B','C','D','E'] for row in board for cell in row)
def main():
    board=create_board()
    place_ships(board)
    write_to_board(board,"ships.txt")

    play_game(board)
    print("Thanks")

if __name__=="__main__":
    main()
