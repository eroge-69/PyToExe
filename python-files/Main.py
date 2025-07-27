import pygame
import random

# Init
pygame.init()
WIDTH, HEIGHT = 160, 160
SCALE = 4
screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
pygame.display.set_caption("PixelFrount – Capital Edition - Fixed Removal")

# Colors
COLORS = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'green': (0, 200, 0),
    'neutral': (20, 20, 20),
    'capital': (255, 255, 0),
}

ALL_TEAMS = ['red', 'blue', 'yellow', 'green']
active_teams = ALL_TEAMS.copy()
grid = [['neutral' for _ in range(WIDTH)] for _ in range(HEIGHT)]
wars = {team: set() for team in ALL_TEAMS}
capitals = {}
selected_team = None
territory_count = {}

def place_starting_positions():
    for team in ALL_TEAMS:
        placed = False
        while not placed:
            if team == 'red':
                x, y = random.randint(0, WIDTH // 4), random.randint(0, HEIGHT - 1)
            elif team == 'blue':
                x, y = random.randint(WIDTH * 3 // 4, WIDTH - 1), random.randint(0, HEIGHT - 1)
            elif team == 'yellow':
                x, y = random.randint(0, WIDTH - 1), random.randint(0, HEIGHT // 4)
            elif team == 'green':
                x, y = random.randint(0, WIDTH - 1), random.randint(HEIGHT * 3 // 4, HEIGHT - 1)
            if grid[y][x] == 'neutral':
                grid[y][x] = team
                capitals[team] = (x, y)
                placed = True
        for _ in range(14):
            nx = max(0, min(WIDTH - 1, x + random.randint(-3, 3)))
            ny = max(0, min(HEIGHT - 1, y + random.randint(-3, 3)))
            grid[ny][nx] = team

def recalc_territory_count():
    global territory_count
    territory_count = {team: 0 for team in active_teams}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t = grid[y][x]
            if t in territory_count:
                territory_count[t] += 1

def remove_team(team):
    global active_teams, wars, capitals, grid
    if team not in active_teams:
        return
    print(f"⚠️ {team.upper()} has been eliminated!")
    active_teams.remove(team)
    wars.pop(team, None)
    capitals.pop(team, None)
    for t in wars:
        wars[t].discard(team)
    # Clear tiles in grid
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == team:
                grid[y][x] = 'neutral'
    recalc_territory_count()

def spread():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            team = grid[y][x]
            if team in active_teams:
                strength_attacker = territory_count.get(team, 0)
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                        neighbor = grid[ny][nx]
                        if neighbor == 'neutral':
                            if random.random() < 0.25:
                                grid[ny][nx] = team
                                territory_count[team] += 1
                        elif neighbor in active_teams and neighbor != team:
                            if neighbor in wars[team]:
                                strength_defender = territory_count.get(neighbor, 0)
                                total_strength = strength_attacker + strength_defender
                                if total_strength == 0:
                                    chance = 0.05
                                else:
                                    base_chance = 0.05
                                    strength_ratio = strength_attacker / total_strength
                                    chance = base_chance + strength_ratio * 0.25
                                if random.random() < chance:
                                    grid[ny][nx] = team
                                    territory_count[team] += 1
                                    territory_count[neighbor] -= 1
                                    if capitals.get(neighbor) == (nx, ny):
                                        print(f"⚠️ {team.upper()} captured {neighbor.upper()}'s capital!")
                                        remove_team(neighbor)

def draw():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = grid[y][x]
            color = COLORS[tile] if tile in COLORS else COLORS['neutral']
            pygame.draw.rect(screen, color, (x * SCALE, y * SCALE, SCALE, SCALE))

    for team in active_teams:
        cx, cy = capitals[team]
        if team == 'yellow':
            pygame.draw.rect(screen, COLORS['green'], (cx * SCALE, cy * SCALE, SCALE, SCALE))
        else:
            pygame.draw.rect(screen, COLORS['capital'], (cx * SCALE, cy * SCALE, SCALE, SCALE))

    if selected_team:
        pygame.display.set_caption(f"Selected: {selected_team.upper()}")

def get_team_at_pos(mx, my):
    gx = mx // SCALE
    gy = my // SCALE
    if 0 <= gx < WIDTH and 0 <= gy < HEIGHT:
        return grid[gy][gx]
    return None

place_starting_positions()
recalc_territory_count()

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(COLORS['neutral'])
    spread()
    draw()
    pygame.display.flip()
    clock.tick(15)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                selected_team = get_team_at_pos(*event.pos)
                if selected_team not in active_teams:
                    selected_team = None
            elif event.button == 1 and selected_team:
                target_team = get_team_at_pos(*event.pos)
                if target_team in active_teams and target_team != selected_team:
                    print(f"{selected_team.upper()} declared war on {target_team.upper()}")
                    wars[selected_team].add(target_team)
                    wars[target_team].add(selected_team)

pygame.quit()

