#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pygame
import random
import time
import matplotlib.pyplot as plt
import os
from datetime import datetime

score_history = [0]

# Initialiseer pygame
pygame.init()

# Constantes
GRID_SIZE = 16  # 16x16 bord
CELL_SIZE = 30  # Grootte van een vakje
# Driehoekige doelgebieden
BLUE_GOAL = [
    (0,0), (0,1), (0,2), (0,3), (0,4),
    (1,0), (1,1), (1,2), (1,3), (1,4),
    (2,0), (2,1), (2,2), (2,3),
    (3,0), (3,1), (3,2),
    (4,0), (4,1)
]

RED_GOAL = [(15 - x, 15 - y) for (x, y) in BLUE_GOAL]



WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE + 100  # Extra ruimte voor knop en beurtindicator
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (200, 200, 200)
BUTTON_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 255, 0)  # Kleur voor geselecteerd stuk
START_COLOR = (0, 220, 50)
MIDDLE_COLOR = (255, 230, 60)
END_COLOR = (255, 120, 20)
status_text = "Just aan de beurt"
max_time = 5  # tijd in seconden om na te denken
current_phase = "begin"
move_counter = 0
score_saved = False

# Maak het scherm
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Halma")

# Knop coördinaten
BUTTON_RECT = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 40, 150, 30)
NEW_GAME_RECT = pygame.Rect(20, HEIGHT - 60, 70, 20)


# In[2]:


def is_winner(pieces, player_color, goal_area):
    for pos, color in pieces.items():
        if color == player_color and pos not in goal_area:
            return False
    return True


# In[3]:


def draw_board(move_made):
    # Kleuren
    WHITE = (255, 255, 255)
    START_COLOR = (0, 220, 50)         # Groen voor startpad
    MIDDLE_COLOR = (255, 230, 60)      # Geel voor tussenstappen
    END_COLOR = (255, 120, 20)         # Oranje voor eindpunt
    SELECTED_PIECE_COLOR = (255, 255, 0)  # Felle gele selectie
    BLUE_GOAL_COLOR = (210, 230, 255)
    RED_GOAL_COLOR = (255, 235, 235)
    BLUE_BORDER = (0, 102, 204)
    RED_BORDER = (204, 30, 30)
    THICKNESS = 4

    screen.fill(WHITE)

    # Grid en vakjeskleur
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (x, y) in BLUE_GOAL:
                pygame.draw.rect(screen, BLUE_GOAL_COLOR, rect)
            elif (x, y) in RED_GOAL:
                pygame.draw.rect(screen, RED_GOAL_COLOR, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)

    # Dikke buitenrand van doelgebied
    def draw_thick_border(goalset, color):
        for (x, y) in goalset:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            for side, (dx, dy) in zip(
                ["top", "bottom", "left", "right"],
                [(0, -1), (0, 1), (-1, 0), (1, 0)]
            ):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) in goalset):
                    if side == "top":
                        pygame.draw.line(screen, color,
                            (x*CELL_SIZE, y*CELL_SIZE),
                            ((x+1)*CELL_SIZE, y*CELL_SIZE), THICKNESS)
                    if side == "bottom":
                        pygame.draw.line(screen, color,
                            (x*CELL_SIZE, (y+1)*CELL_SIZE),
                            ((x+1)*CELL_SIZE, (y+1)*CELL_SIZE), THICKNESS)
                    if side == "left":
                        pygame.draw.line(screen, color,
                            (x*CELL_SIZE, y*CELL_SIZE),
                            (x*CELL_SIZE, (y+1)*CELL_SIZE), THICKNESS)
                    if side == "right":
                        pygame.draw.line(screen, color,
                            ((x+1)*CELL_SIZE, y*CELL_SIZE),
                            ((x+1)*CELL_SIZE, (y+1)*CELL_SIZE), THICKNESS)
    draw_thick_border(BLUE_GOAL, BLUE_BORDER)
    draw_thick_border(RED_GOAL, RED_BORDER)

    # Highlight het complete pad (slide of multijump)
    font = pygame.font.Font(None, int(CELL_SIZE * 0.5))
    if last_move and len(last_move) >= 2:
        # Start
        rect = pygame.Rect(last_move[0][0]*CELL_SIZE, last_move[0][1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, START_COLOR, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 1)

        # Tussenstappen (met nummer)
        for idx, pos in enumerate(last_move[1:-1], 1):
            rect = pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, MIDDLE_COLOR, rect)
            pygame.draw.rect(screen, (0,0,0), rect, 1)
            label = font.render(str(idx), True, (0,0,0))
            text_rect = label.get_rect(center=(pos[0]*CELL_SIZE + CELL_SIZE//2, pos[1]*CELL_SIZE + CELL_SIZE//2))
            screen.blit(label, text_rect)

        # Eind
        rect = pygame.Rect(last_move[-1][0]*CELL_SIZE, last_move[-1][1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, END_COLOR, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 1)

    # Highlight het geselecteerde stuk van de speler felgeel (mits niet dubbel met pad)
    if selected_piece and (not last_move or selected_piece not in last_move):
        rect = pygame.Rect(selected_piece[0]*CELL_SIZE, selected_piece[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, SELECTED_PIECE_COLOR, rect, 0)
        pygame.draw.rect(screen, (80,80,80), rect, 2)

    # Teken de knop
    if move_made:
        pygame.draw.rect(screen, BUTTON_COLOR, BUTTON_RECT)
        font_btn = pygame.font.Font(None, 24)
        text = font_btn.render("Beurt beëindigen", True, BUTTON_TEXT_COLOR)
        screen.blit(text, (BUTTON_RECT.x + 15, BUTTON_RECT.y + 10))

    #Knop New Game
    pygame.draw.rect(screen, GRAY, NEW_GAME_RECT)
    text = font.render("Nieuw spel", True, BLACK)
    screen.blit(text, (NEW_GAME_RECT.x + 10, NEW_GAME_RECT.y + 10))

    # Beurtindicator
    draw_turn_indicator()


# In[4]:


def draw_turn_indicator():
    font = pygame.font.Font(None, 36)
    text_surface = font.render(status_text, True, BLACK)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT - 80))


# In[5]:


# Functie om stukken te tekenen
def draw_pieces(pieces):
    for (x, y), color in pieces.items():
        pygame.draw.circle(screen, color, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)



# In[6]:


pieces = {}
# BLAUW linksboven
for item in BLUE_GOAL:
            pieces[(item)] = BLUE

for item in RED_GOAL:
            pieces[(item)] = RED


# In[7]:


def distance_to_goal(pos, color):
    x, y = pos
    if color == BLUE:
        return (GRID_SIZE - 1 - x) + (GRID_SIZE - 1 - y)
    else:
        return x + y

def total_distance(pieces, color, goal_area):
    total = 0
    for pos in pieces:
        if pieces[pos] == color:
            if pos in goal_area:
                total += BONUS   # Beloon stukken in doelgebied
            else:
                total += distance_to_goal(pos, color)
    return total


def board_score(pieces, player_color):
    goal_area = RED_GOAL if player_color == BLUE else BLUE_GOAL
    opp_goal_area = BLUE_GOAL if player_color == BLUE else RED_GOAL
    my_distance_sum = 0
    opp_distance_sum = 0

    for pos, color in pieces.items():
        dist = distance_to_goal(pos, color)
        if color == player_color:
            my_distance_sum += dist
        else:
            opp_distance_sum += dist

        score = opp_distance_sum - my_distance_sum

    return score     


# In[8]:


def game_over(pieces):
    # Controleer of er geen stukken meer over zijn voor een speler
    red_pieces = [pos for pos, color in pieces.items() if color == RED]
    blue_pieces = [pos for pos, color in pieces.items() if color == BLUE]

    # Als een van de spelers geen stukken meer heeft, is het spel voorbij
    if not red_pieces or not blue_pieces:
        return True

    # Controleer of er geen geldige zetten meer zijn voor een speler
    for piece in pieces:
        if pieces[piece] == BLUE:  # Voor de bot
            if any(is_valid_jump(piece, (piece[0] + dx, piece[1] + dy), pieces) for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]):
                return False  # Er zijn nog geldige zetten, spel is niet voorbij

        if pieces[piece] == RED:  # Voor de speler
            if any(is_valid_jump(piece, (piece[0] + dx, piece[1] + dy), pieces) for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]):
                return False  # Er zijn nog geldige zetten, spel is niet voorbij

    return True  # Als er geen geldige zetten meer zijn, is het spel voorbij


# In[9]:


from functools import lru_cache
import time

# Evalueer met transposition key (caching alleen voor evaluatie, niet voor hele minimax)
def board_to_key_simple(pieces):
    return tuple(sorted(pieces.items()))

from itertools import combinations

def manhattan_dist(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def evaluate_board(pieces, player_color):
    opponent = RED if player_color == BLUE else BLUE

    # Parameters
    board_size = 16  
    axis_deviation_weight = 0.75
    splinter_weight = 0.75

    # Verzamel eigen afstanden en posities
    own_distances_pos = sorted(
        [(distance_to_goal(pos, player_color), pos) for pos, color in pieces.items() if color == player_color],
        reverse=True
    )
    own_distances = [x[0] for x in own_distances_pos]

    # Straf voor afwijking van de diagonaal-as (x == y)
    axis_deviation = sum(
        abs(pos[0] - pos[1]) for _, pos in own_distances_pos
    )

    # Straf voor spreiding van de achterblijvende stenen
    ntop = min(3, len(own_distances_pos))
    backwards = [pos for _, pos in own_distances_pos[:ntop]]
    splinter_penalty = 0
    if len(backwards) > 1:
        total = 0
        n = 0
        for p1, p2 in combinations(backwards, 2):
            total += manhattan_dist(p1, p2)
            n += 1
        avg_splinter = total / n
        splinter_penalty = splinter_weight * avg_splinter

    # Rest van je bestaande evaluatie
    opponent_distance = evaluate_own_distance(pieces, opponent)
    sum_own_distance = sum(own_distances)

    weights = [5.0, 3.0, 1.0]
    penalty = 0
    for i in range(min(3, len(own_distances))):
        penalty += weights[i] * own_distances[i]

    score = (1.5 * opponent_distance - sum_own_distance) - penalty

    # Toevoegen nieuwe straffen
    score -= axis_deviation_weight * axis_deviation
    score -= splinter_penalty

    return score


def estimate_move_value(pieces, move, player_color):
    new_pieces = simulate_move(pieces, move)
    return evaluate_board(new_pieces, player_color)

# De transposition table als globale dict
ttable = {}

def minimax(pieces, depth, alpha, beta, maximizing_player, player_color, time_limit, max_width):
    alpha_orig = alpha
    key = (board_to_key_simple(pieces), depth, maximizing_player)

    if time.time() > time_limit or depth == 0:
        return evaluate_board(pieces, player_color), None

    if key in ttable:
        stored_score, bound_type, stored_move = ttable[key]
        if bound_type == "exact":
            return stored_score, stored_move
        elif bound_type == "lower" and stored_score >= beta:
            return stored_score, stored_move
        elif bound_type == "upper" and stored_score <= alpha:
            return stored_score, stored_move

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        moves = generate_moves(pieces, player_color)
        moves.sort(key=lambda move: -estimate_move_value(pieces, move, player_color))
        moves = moves[:max_width]

        for move in moves:
            new_pieces = simulate_move(pieces, move)
            eval_score, _ = minimax(new_pieces, depth - 1, alpha, beta, False, player_color, time_limit, max_width)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        if max_eval <= alpha_orig:
            bound_type = "upper"
        elif max_eval >= beta:
            bound_type = "lower"
        else:
            bound_type = "exact"

        ttable[key] = (max_eval, bound_type, best_move)
        return max_eval, best_move

    else:
        min_eval = float('inf')
        opponent = RED if player_color == BLUE else BLUE
        moves = generate_moves(pieces, opponent)
        moves.sort(key=lambda move: estimate_move_value(pieces, move, opponent))
        moves = moves[:max_width]

        for move in moves:
            new_pieces = simulate_move(pieces, move)
            eval_score, _ = minimax(new_pieces, depth - 1, alpha, beta, True, player_color, time_limit, max_width)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        if min_eval <= alpha_orig:
            bound_type = "upper"
        elif min_eval >= beta:
            bound_type = "lower"
        else:
            bound_type = "exact"

        ttable[key] = (min_eval, bound_type, best_move)
        return min_eval, best_move


def minimax_iterative_deepening(pieces, player_color, max_time, max_width):
    m_time = time.time() + max_time
    best_move = None
    depth = 1
    previous_root_scores = None

    while time.time() < m_time:
        try:
            # Genereer root-moves, eventueel geordend op vorige scores
            if previous_root_scores:
                root_moves = [move for move, scr in previous_root_scores]
            else:
                root_moves = generate_moves(pieces, player_color)

            # Beperk tot max_width moves (optioneel)
            root_moves = root_moves[:max_width]

            root_scores = []
            best_score_this_depth = float('-inf')
            best_move_this_depth = None

            for move in root_moves:
                new_pieces = simulate_move(pieces, move)
                # Diepte-1, want deze move is de eerste laag
                eval_score, _ = minimax(
                    new_pieces, depth-1,
                    float('-inf'), float('inf'),
                    False, player_color, m_time, max_width
                )
                root_scores.append((move, eval_score))
                if eval_score > best_score_this_depth:
                    best_score_this_depth = eval_score
                    best_move_this_depth = move
                if time.time() > m_time:
                    raise TimeoutError

            # Sorteer moves op hun score voor volgende diepte
            previous_root_scores = sorted(root_scores, key=lambda t: -t[1])

            print(f"✅ Zet gevonden op diepte {depth}: {best_move_this_depth} (score {best_score_this_depth})")
            best_move = best_move_this_depth
            depth += 1
        except TimeoutError:
            print("⏱️ Tijdslimiet overschreden tijdens minimax")
            break

    if best_move is None:
        print("⚠️ Geen zet gevonden via iterative deepening — fallback naar depth=1")
        root_moves = generate_moves(pieces, player_color)[:max_width]
        best_score = float('-inf')
        for move in root_moves:
            new_pieces = simulate_move(pieces, move)
            eval_score = evaluate_board(new_pieces, player_color)
            if eval_score > best_score:
                best_score = eval_score
                best_move = move

    return best_move


# In[10]:


def find_multijumps(pieces, start, current, visited=None):
    if visited is None:
        visited = {start}
    else:
        visited = set(visited)

    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1),  (1, 0), (1, 1)]

    found_jump = False
    for dx, dy in DIRECTIONS:
        mx, my = current[0] + dx, current[1] + dy
        nx, ny = current[0] + 2*dx, current[1] + 2*dy

        if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and
            (nx, ny) not in pieces and (mx, my) in pieces and (nx, ny) not in visited):

            visited.add((nx, ny))
            temp_pieces = pieces.copy()
            temp_pieces[(nx, ny)] = temp_pieces.pop(current)

            further = list(find_multijumps(temp_pieces, start, (nx, ny), visited))
            if further:
                for path in further:
                    yield [current] + path
            else:
                yield [current, (nx, ny)]

            visited.remove((nx, ny))
            found_jump = True

    if not found_jump:
        return


# In[11]:


def generate_moves(pieces, color):
    moves = []
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1),  (1, 0), (1, 1)]
    for pos, piece_color in pieces.items():
        if piece_color == color:
            # SLIDES
            for dx, dy in DIRECTIONS:
                nx, ny = pos[0] + dx, pos[1] + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in pieces:
                    moves.append( ( [pos, (nx, ny)], 'slide' ) )
            # MULTIJUMPS
            multijump_routes = find_multijumps(pieces, pos, pos)
            for route in multijump_routes:
                # route is bijv. [pos, a, b, c]
                if len(route) > 1:
                    moves.append( (route, 'jump') )
    return moves


# In[12]:


def simulate_move(pieces, move):
    route, move_type = move
    start = route[0]
    end = route[-1]

    # In-place mutatie met kopie van enkel gewijzigde delen
    new_pieces = pieces.copy()
    new_pieces[end] = new_pieces.pop(start)

    return new_pieces


# In[13]:


def compute_multijumps(piece, simulated_pieces, current_distance):
            current_position = piece
            total_distance_after_jump = current_distance
            visited_positions = {piece}  # Houd bij waar de steen al geweest is
            all_jump_sequences = []  # Lijst om alle mogelijke multijumps bij te houden

            while True:
                valid_jump_found = False
                best_jump = None
                best_distance = total_distance_after_jump  # Huidige afstand als referentie

                for dx, dy in [(i * 2, j * 2) for i in [-1, 0, 1] for j in [-1, 0, 1] if (i, j) != (0, 0)]:
                        mid_x, mid_y = current_position[0] + dx // 2, current_position[1] + dy // 2
                        end_x, end_y = current_position[0] + dx, current_position[1] + dy

                        if (end_x, end_y) in visited_positions:
                            continue  # Niet terug naar een eerder bezochte plek!

                        if is_valid_jump(current_position, (end_x, end_y), simulated_pieces):
                            # Simuleer de sprong
                            temp_pieces = simulated_pieces.copy()
                            temp_pieces[(end_x, end_y)] = temp_pieces[current_position]  # voeg het stuk toe op de nieuwe eindplek
                            del temp_pieces[current_position] #verwijder oorspronkelijke plek van het stuk
                            # Bereken de nieuwe afstand
                            new_distance = total_distance(temp_pieces, BLUE)

                            if new_distance < best_distance:  # Sprong moet de afstand verkleinen!
                                best_distance = new_distance
                                best_jump = (end_x, end_y)

                if best_jump:
                    # Voer de beste sprong uit
                    simulated_pieces[best_jump] = simulated_pieces[current_position]
                    del simulated_pieces[current_position]

                    # Voeg deze sprong toe aan het pad van de multijump
                    visited_positions.add(best_jump)
                    current_position = best_jump
                    total_distance_after_jump = best_distance
                    valid_jump_found = True
                else:
                    break  # Stop als er geen sprongen meer mogelijk zijn

                # Voeg de huidige sprong en de bijbehorende afstand toe aan de lijst van alle multijumps
                all_jump_sequences.append((current_position, total_distance_after_jump))

            return all_jump_sequences  # Geef de lijst van alle multijumps en hun afstanden terug


# In[14]:


def bot_move():
    global last_move, pieces
    score = board_score(pieces, BLUE)
    print('Score na zet Just: ', score)
    score_history.append(board_score(pieces, BLUE))

    phase = get_game_phase(pieces, BLUE)
    print(f"🤖 Bot denkt... ({phase})")

    #TODO afstemmen op maxtime
    if phase == 'begin':
        depth_limit = max(7-move_counter,3)
        if depth_limit > 4:
            beam_width = max_time*15000//depth_limit
        else:
            beam_width = max_time*1000000//depth_limit
        best_move = beam_search(pieces, BLUE, depth_limit, beam_width, max_time)

    elif phase == 'midden':
           best_move = minimax_iterative_deepening(pieces, BLUE, max_time, 75*max_time)
    elif phase == 'einde':
        depth_limit = 20
        best_move = beam_search(pieces, BLUE, depth_limit, max_time*500//depth_limit, max_time)
    else:
        best_move = None

    if best_move:
        route, move_type = best_move
        last_move = route
        pieces = simulate_move(pieces, best_move)
        print("Bot zet:", route)
    else:
        print("❌ Geen mogelijke zetten voor de bot!")
    score_history.append(board_score(pieces, BLUE))
    print('Score na zet Sam: ', board_score(pieces, BLUE))


# In[15]:


def save_score_graph():
    # Genereer timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"halma_score_graph_{timestamp}.png"

    # Pad naar bureaublad
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filepath = os.path.join(desktop_path, filename)

    # Fallback als bureaublad niet bestaat
    if not os.path.exists(desktop_path):
        print("⚠️ Bureaublad niet gevonden, opslaan in huidige map...")
        filepath = filename

    # Plot en opslaan
    plt.figure(figsize=(10, 5))
    plt.plot(score_history, marker='o')
    plt.title("Scoreverloop Halma")
    plt.xlabel("Zetnummer")
    plt.ylabel("Score (voor BLUE)")
    plt.grid(True)
    plt.savefig(filepath)
    plt.close()

    print(f"📊 Scoregrafiek opgeslagen als: {os.path.abspath(filepath)}")


# In[16]:


# Controleer of een sprong geldig is
def is_valid_jump(start, end, pieces):
    sx, sy = start
    ex, ey = end

    # Controleer of de start- en eindposities binnen de grenzen van het bord vallen
    if not (0 <= sx < GRID_SIZE and 0 <= sy < GRID_SIZE):
        return False
    if not (0 <= ex < GRID_SIZE and 0 <= ey < GRID_SIZE):
        return False

    # Controleer of de sprongafstand correct is (2 in een richting)
    if (abs(ex - sx) == 2 and sy == ey) or (abs(ey - sy) == 2 and sx == ex) or (abs(ex - sx) == 2 and abs(ey - sy) == 2):
        mid_x, mid_y = (sx + ex) // 2, (sy + ey) // 2

        # Controleer of er een stuk in het midden zit
        if (mid_x, mid_y) in pieces and (ex, ey) not in pieces:
            return True

    return False


# In[17]:


def board_to_key(pieces):
    return tuple(sorted((pos, color) for pos, color in pieces.items()))

@lru_cache(maxsize=10000)
def evaluate_board_cached(pieces_key, player_color):
    pieces = {pos: color for pos, color in pieces_key}
    return evaluate_board(pieces, player_color)


# In[18]:


# Functie om te controleren of een schuif geldig is
def is_valid_slide(start, end):
    sx, sy = start
    ex, ey = end

    # Controleer of de start- en eindposities binnen de grenzen van het bord vallen
    if not (0 <= sx < GRID_SIZE and 0 <= sy < GRID_SIZE):
        return False
    if not (0 <= ex < GRID_SIZE and 0 <= ey < GRID_SIZE):
        return False

    # Controleer of de schuifafstand correct is (1 in elke richting)
    if abs(ex - sx) <= 1 and abs(ey - sy) <= 1:
        # Controleer of de eindpositie leeg is
        if (ex, ey) not in pieces:
            return True

    return False


# In[19]:


def get_game_phase(pieces, player_color):
    global current_phase

    if move_counter < 4:
        return 'begin'
    elif move_counter < 40:
        return 'midden'
    else:
        return 'einde'

    opponent_color = RED if player_color == BLUE else BLUE

    # Detecteer of er sprongen over vijandelijke stukken mogelijk zijn
    for pos, color in pieces.items():
        if color != player_color:
            continue

        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx == 0 and dy == 0:
                    continue

                mid_x, mid_y = pos[0] + dx // 2, pos[1] + dy // 2
                end_x, end_y = pos[0] + dx, pos[1] + dy

                if (0 <= end_x < GRID_SIZE and 0 <= end_y < GRID_SIZE and
                    (mid_x, mid_y) in pieces and pieces[(mid_x, mid_y)] == opponent_color and
                    (end_x, end_y) not in pieces):

                    if current_phase != "einde":
                        current_phase = "midden"
                    return current_phase

    # Geen sprongen mogelijk → kijk naar afstand om 'einde' te bepalen
    my_positions = [pos for pos, color in pieces.items() if color == player_color]
    avg_dist = sum(distance_to_goal(pos, player_color) for pos in my_positions) / len(my_positions)

    if avg_dist < 10 and current_phase != "einde":
        current_phase = "einde"

    return current_phase


# In[20]:


import heapq
from functools import lru_cache

def evaluate_own_distance(pieces, player_color):
    return sum(distance_to_goal(pos, player_color) for pos, color in pieces.items() if color == player_color)


@lru_cache(maxsize=10000)
def cached_distance_sum(pieces_key, player_color):
    pieces = {pos: color for pos, color in pieces_key}
    return evaluate_own_distance(pieces, player_color)

def board_to_key_simple(pieces):
    return tuple(sorted(pieces.items()))

def beam_search(pieces, player_color, depth_limit, beam_width, max_time):
    start_time = time.time()
    time_limit = start_time + max_time
    goal = RED_GOAL if player_color == BLUE else BLUE_GOAL

    queue = [(
        evaluate_own_distance(pieces, player_color),
        [],
        pieces
    )]

    best_path = None
    best_score = float('inf')
    seen = set()

    for depth in range(depth_limit):
        if time.time() > time_limit:
            print("⏱️ Tijdslimiet bereikt vóór diepteniveau", depth + 1)
            break

        next_queue = []

        for score, path, board in queue:
            if time.time() > time_limit:
                break  # Tussentijdse controle

            moves = generate_moves(board, player_color)
            moves = sorted(
                moves,
                key=lambda move: distance_to_goal(move[0][-1], player_color)
            )

            for move in moves:
                if time.time() > time_limit:
                    break  # Tijdslimiet controle binnen inner-loop

                new_board = simulate_move(board, move)
                key = board_to_key_simple(new_board)
                if key in seen:
                    continue
                seen.add(key)

                new_score = cached_distance_sum(key, player_color)
                heapq.heappush(next_queue, (new_score, path + [move], new_board))

                if is_winner(new_board, player_color, goal):
                    print(f"🟢 Early exit op diepte {depth + 1}")
                    return (path + [move])[0]  # ✅ alleen de eerste zet


        queue = heapq.nsmallest(beam_width, next_queue)
        if queue:
            best_score, best_path, _ = queue[0]


        if time.time() > time_limit:
            print("⏱️ Beam search tijdslimiet bereikt na diepte", depth + 1)
            break
    print(f"🔍 Diepte {depth + 1}: {len(queue)} kandidaten, beste score: {best_score:.2f}")
    return best_path[0] if best_path else None


# In[ ]:


running = True
player_turn = True
selected_piece = None
jump_made = False
shove_made = False
current_move_path = []
last_move = None

while running:

    move_made = jump_made or shove_made

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE

            if NEW_GAME_RECT.collidepoint(mouse_x, mouse_y):
                print("🔄 Nieuw spel gestart")
                pieces = {}
                # BLAUW linksboven
                for item in BLUE_GOAL:
                            pieces[(item)] = BLUE
                # ROOD Rechtonder
                for item in RED_GOAL:
                            pieces[(item)] = RED

                player_turn = True
                selected_piece = None
                current_move_path.clear()
                last_move = None
                score_history.clear()
                move_counter = 0
                score_saved = False

            # --- Beurt beëindigen
            if BUTTON_RECT.collidepoint(mouse_x, mouse_y) and move_made:
                selected_piece = None
                jump_made = False
                shove_made = False
                player_turn = False

                if current_move_path and len(current_move_path) >= 2:
                    last_move = current_move_path.copy()
                else:
                    last_move = None
                current_move_path = []

            # --- Speler selecteert veld
            elif selected_piece:
                if (grid_x, grid_y) not in pieces:
                    # SPRONG toegestaan alleen als er nog niet geschoven is
                    if is_valid_jump(selected_piece, (grid_x, grid_y), pieces) and not shove_made:
                        pieces[(grid_x, grid_y)] = pieces[selected_piece]
                        del pieces[selected_piece]
                        if not current_move_path:
                            current_move_path = [selected_piece]
                        current_move_path.append((grid_x, grid_y))
                        selected_piece = (grid_x, grid_y)
                        jump_made = True

                    # SCHUIF toegestaan alleen als er nog niet gesprongen of geschoven is
                    elif is_valid_slide(selected_piece, (grid_x, grid_y)) and not move_made:
                        pieces[(grid_x, grid_y)] = pieces[selected_piece]
                        del pieces[selected_piece]
                        current_move_path = [selected_piece, (grid_x, grid_y)]
                        shove_made = True
                        selected_piece = None
            else:
                # Stuk selecteren
                if (grid_x, grid_y) in pieces and pieces[(grid_x, grid_y)] == RED:
                    selected_piece = (grid_x, grid_y)
                    current_move_path = [selected_piece]

    if not player_turn:
        start = time.time()
        status_text = "Sam aan de beurt"
        move_made = jump_made or shove_made
        draw_board(move_made)
        draw_pieces(pieces)
        draw_turn_indicator()
        pygame.display.flip()

        bot_move()
        move_counter += 1

        status_text = "Just aan de beurt"
        pygame.display.update()
        end = time.time()
        print('bottime', end - start)
        player_turn = True

    # WINCONDITIE
    if is_winner(pieces, RED, BLUE_GOAL):
        status_text = "Just heeft gewonnen"
        if not score_saved:
            save_score_graph()
            score_saved = True

    elif is_winner(pieces, BLUE, RED_GOAL):
        status_text = "Sam heeft gewonnen"
        if not score_saved:
            save_score_graph()
            score_saved = True


    draw_board(move_made)
    draw_pieces(pieces)
    pygame.display.flip()
pygame.quit()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




