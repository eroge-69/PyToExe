# -*- coding: utf-8 -*-
"""
Created on Wed May 14 09:23:38 2025

@author: A143VU08
"""

import random
import pgzrun

# === Fenster- und Spielfeld-Konfiguration ===
TILE_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = TILE_SIZE * COLS
HEIGHT = TILE_SIZE * ROWS
TITLE = "Tetris"

# === Farben: Pastelltöne für die Steine ===
PASTEL_COLORS = [
    (255, 179, 186),  # Rosa
    (255, 223, 186),  # Pfirsich
    (255, 255, 186),  # Hellgelb
    (186, 255, 201),  # Minz
    (186, 225, 255),  # Hellblau
    (218, 186, 255),  # Flieder
    (255, 186, 247),  # Pink
    ]

ROSA = (255, 179, 186)  # Fester Rosaton für Startseite (enter)

# === Tetris-Formen ===
SHAPES = {
    'I': [[1, 1, 1, 1]],
    
    'J': [[1, 0, 0],
          [1, 1, 1]],
    
    'L': [[0, 0, 1],
          [1, 1, 1]],
    
    'O': [[1, 1],
          [1, 1]],
    
    'S': [[0, 1, 1],
          [1, 1, 0]],
    
    'T': [[0, 1, 0],
          [1, 1, 1]],
    
    'Z': [[1, 1, 0],
          [0, 1, 1]]
}

# === Spielstatus-Variablen === bevor stein fällt
grid = [[None for _ in range(COLS)] for _ in range(ROWS)] #feld ist leer
current_piece = None
current_color = None
piece_x = 0
piece_y = 0
fall_time = 0
fall_speed = 30
game_state = "start"  # 'start', 'playing', 'gameover'
score = 0  # Punktestand

# === Neuer Tetris-Stein ===
def new_piece():
    global current_piece, current_color, piece_x, piece_y, game_state
    current_piece = random.choice(list(SHAPES.values()))  #random form
    current_color = random.choice(PASTEL_COLORS)             #random farbe
    piece_x = COLS // 2 - len(current_piece[0]) // 2 #stein fällt mittig
    piece_y = 0 # oberer rand des feldes
    if check_collision(current_piece, piece_x, piece_y):  #wenn neuer stein einen in der obersten reihe berührt
        game_state = "gameover"  # wenn kollision, dass gameover

# === Kollision prüfen ===
def check_collision(piece, x, y):
    for i, row in enumerate(piece): #jede zeile wird durchlaufen um zu prüfen wo steine sind
        for j, val in enumerate(row):
            if val:
                px = x + j #horizontal berechnung der position des blocks
                py = y + i # vertikal
                if px < 0 or px >= COLS or py >= ROWS: #prüft dassder block nicht aus spielfeld geht
                    return True # wenn auserhalb, gibt kollision-> platz besetzt
                if py >= 0 and grid[py][px]:
                    return True # gleiche nur mit block
    return False # wenn es keine kollision gibt, dann kann sich der block frei bewegen

# === Stein festsetzen ===
def place_piece():
    global score
    for i, row in enumerate(current_piece): # reihen werden durchgegangen
        for j, val in enumerate(row):
            if val:
                px = piece_x + j
                py = piece_y + i
                if 0 <= px < COLS and 0 <= py < ROWS: #wenn innerhalb des feldes (stellt fest dass es nicht raus geht)
                    grid[py][px] = current_color # farbe wird festgesetzt
    lines_cleared = clear_lines()  # Gibt die Anzahl der gelöschten Linien zurück
    score += lines_cleared * 100  # Für jede gelöschte Linie gibt es 100 Punkte
    new_piece()

# === Ganze Linien löschen ===
def clear_lines():
    global grid
    new_grid = [row for row in grid if any(cell is None for cell in row)] #neue linie, nur wenn alle zellen einer linie besetzt sind
    lines_cleared = ROWS - len(new_grid) # new grid= wieviele zeilen leer sind/ (lines cleared)-> neue zeilen, da volle gelöscht werden
    for _ in range(lines_cleared):
        new_grid.insert(0, [None for _ in range(COLS)]) # neue zeile(aktuell)
    grid = new_grid
    return lines_cleared  # Anzahl der gelöschten Linien zurückgeben

# === Stein drehen ===
def rotate_piece():
    global current_piece
    rotated = list(zip(*current_piece[::-1])) #kehrt die Reihenfolge der Zeilen um,
   # sodass die Zeilen von unten nach oben statt von oben nach unten gelesen werden.
   #zip ::-1 =zeilen werden zu spalten

    rotated = [list(row) for row in rotated]
    if not check_collision(rotated, piece_x, piece_y): #kollision wird überprüft
        current_piece = rotated

# === Spiel zurücksetzen ===
def reset_game():
    global grid, score
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)] #neues feld ohne steine drinne
    score = 0  # Punktestand zurücksetzen
    new_piece()

# === Spielablauf (Tick) ===
def update():
    global fall_time, piece_y
    if game_state != "playing":#Code nur dann ausgeführt wird, wenn das Spiel wirklich läuft.
        return

    fall_time += 1 #wie lange der block gefallen ist
    if fall_time >= fall_speed:
        fall_time = 0
        if not check_collision(current_piece, piece_x, piece_y + 1): #kann stein noch weiter nach unten
            piece_y += 1 #wenn keine kollision= stein 1 nach unten
        else:
            place_piece()

# === Darstellung ===
def draw():
    screen.clear()
    screen.fill((250, 250, 250))  # Hintergrund

    if game_state == "start":
        draw_start_screen()
    elif game_state == "gameover":
        draw_gameover_screen()
    else:
        # Gitter und gesetzte Steine
        for y in range(ROWS):
            for x in range(COLS):
                color = grid[y][x]
                if color:
                    draw_tile(x, y, color)
                else:
                    draw_tile(x, y, (230, 230, 230))  # Gitterfarbe

        # Aktueller fallender Stein
        for i, row in enumerate(current_piece):
            for j, val in enumerate(row):
                if val:
                    draw_tile(piece_x + j, piece_y + i, current_color)

        # Punktestand anzeigen
        screen.draw.text(f"Punkte: {score}", (10, 10), fontsize=24, color=(0, 0, 0))

# === Einzelne Kachel zeichnen ===
def draw_tile(x, y, color):
    rect = Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE - 1, TILE_SIZE - 1))
    screen.draw.filled_rect(rect, color)
    screen.draw.rect(rect, (200, 200, 200))  # Umrandung

# === Startbildschirm zeichnen  ===
def draw_start_screen():
    screen.draw.text("TETRIS", center=(WIDTH // 2, HEIGHT // 4),
                     fontsize=80, color=(219, 112, 147), owidth=0.5, ocolor=(180, 180, 180))

    screen.draw.text("Drücke ENTER um zu starten", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=30, color=ROSA)

    screen.draw.text("PFEILTASTEN : Bewegen   SPACE : Drehen", center=(WIDTH // 2, HEIGHT * 3 // 4),
                     fontsize=21, color=(160, 160, 160))

# === Game Over Bildschirm ===
def draw_gameover_screen():
    screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 3),
                     fontsize=50, color=(200, 100, 100), owidth=0.5, ocolor=(100, 100, 100))

    screen.draw.text(f"Punkte: {score}", center=(WIDTH // 2, HEIGHT // 2),
                     fontsize=30, color=(120, 120, 120))

    screen.draw.text("Drücke R zum Neustart", center=(WIDTH // 2, HEIGHT * 2 // 3),
                     fontsize=30, color=(120, 120, 120))

# === Tasteneingaben ===
def on_key_down(key):
    global piece_x, piece_y, game_state

    if game_state == "start":
        if key == keys.RETURN:
            game_state = "playing"
            reset_game()
    elif game_state == "gameover":
        if key == keys.R:
            game_state = "start"
    elif game_state == "playing":
        if key == keys.LEFT:
            if not check_collision(current_piece, piece_x - 1, piece_y):
                piece_x -= 1
        elif key == keys.RIGHT:
            if not check_collision(current_piece, piece_x + 1, piece_y):
                piece_x += 1
        elif key == keys.DOWN:
            if not check_collision(current_piece, piece_x, piece_y + 1):
                piece_y += 1
        elif key == keys.SPACE:
            rotate_piece()

# === Spiel initial starten ===
new_piece()
pgzrun.go()
