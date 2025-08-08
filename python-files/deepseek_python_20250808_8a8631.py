import pygame
import random
import math

# Inizializzazione di Pygame
pygame.init()

# Dimensioni della finestra di gioco
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man con Gettoni - Edizione Ciro")

# Colori
BLACK = (0, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Classe per rappresentare il labirinto
class Maze:
    def __init__(self):
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
            [1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.cell_size = 35
        self.coins = []
        self.power_pellets = []
        self.initialize_coins()
        
    def initialize_coins(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 0:  # Solo nelle celle vuote
                    if random.random() < 0.1:  # 10% di probabilità per un power pellet
                        self.power_pellets.append((x, y))
                    else:
                        self.coins.append((x, y))
    
    def draw(self, screen):
        # Disegna il labirinto
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                  self.cell_size, self.cell_size)
                if cell == 1:  # Muro
                    pygame.draw.rect(screen, BLUE, rect)
                    pygame.draw.rect(screen, (0, 0, 100), rect, 2)
        
        # Disegna i gettoni (monete)
        for coin in self.coins:
            x, y = coin
            center = (x * self.cell_size + self.cell_size // 2, 
                     y * self.cell_size + self.cell_size // 2)
            pygame.draw.circle(screen, GOLD, center, 4)
        
        # Disegna i power pellet
        for pellet in self.power_pellets:
            x, y = pellet
            center = (x * self.cell_size + self.cell_size // 2, 
                     y * self.cell_size + self.cell_size // 2)
            pygame.draw.circle(screen, WHITE, center, 8)
    
    def is_wall(self, x, y):
        # Controlla se la posizione è un muro
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        
        if 0 <= grid_y < len(self.grid) and 0 <= grid_x < len(self.grid[0]):
            return self.grid[grid_y][grid_x] == 1
        return True

# Classe per il giocatore (Pac-Man)
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 3
        self.direction = "RIGHT"
        self.next_direction = self.direction
        self.mouth_open = 0
        self.mouth_direction = 1
        self.score = 0
        self.power_mode = False
        self.power_timer = 0
    
    def update(self, maze):
        # Prova a cambiare direzione se possibile
        self.try_change_direction(maze)
        
        # Muovi nella direzione corrente
        old_x, old_y = self.x, self.y
        
        if self.direction == "RIGHT":
            self.x += self.speed
        elif self.direction == "LEFT":
            self.x -= self.speed
        elif self.direction == "UP":
            self.y -= self.speed
        elif self.direction == "DOWN":
            self.y += self.speed
        
        # Controlla collisioni con i muri
        if maze.is_wall(self.x, self.y):
            self.x, self.y = old_x, old_y
        
        # Animazione della bocca
        self.mouth_open += 0.2 * self.mouth_direction
        if self.mouth_open > 45 or self.mouth_open < 0:
            self.mouth_direction *= -1
        
        # Gestione del power mode
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
    
    def try_change_direction(self, maze):
        # Prova a cambiare direzione se possibile
        test_x, test_y = self.x, self.y
        
        if self.next_direction == "RIGHT":
            test_x += self.speed
        elif self.next_direction == "LEFT":
            test_x -= self.speed
        elif self.next_direction == "UP":
            test_y -= self.speed
        elif self.next_direction == "DOWN":
            test_y += self.speed
        
        if not maze.is_wall(test_x, test_y):
            self.direction = self.next_direction
    
    def draw(self, screen):
        # Disegna Pac-Man
        color = YELLOW
        
        # Angoli per la bocca in base alla direzione
        if self.direction == "RIGHT":
            start_angle = 30 + self.mouth_open
            end_angle = 330 - self.mouth_open
        elif self.direction == "LEFT":
            start_angle = 210 + self.mouth_open
            end_angle = 150 - self.mouth_open
        elif self.direction == "UP":
            start_angle = 120 + self.mouth_open
            end_angle = 60 - self.mouth_open
        else:  # DOWN
            start_angle = 300 + self.mouth_open
            end_angle = 240 - self.mouth_open
        
        # Disegna Pac-Man come un cerchio con una fetta mancante
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Disegna la bocca
        points = [(self.x, self.y)]
        for angle in range(int(start_angle), int(end_angle) - 1, -1):
            rad = math.radians(angle)
            points.append((
                self.x + self.radius * math.cos(rad),
                self.y - self.radius * math.sin(rad)
            ))
        pygame.draw.polygon(screen, BLACK, points)
        
        # Disegna l'occhio
        eye_offset_x = 0
        eye_offset_y = 0
        if self.direction == "RIGHT":
            eye_offset_x = 5
        elif self.direction == "LEFT":
            eye_offset_x = -5
        elif self.direction == "UP":
            eye_offset_y = -5
        else:  # DOWN
            eye_offset_y = 5
        
        pygame.draw.circle(screen, BLACK, 
                          (int(self.x + eye_offset_x), int(self.y + eye_offset_y)), 
                          self.radius // 4)

# Classe per i fantasmi
class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 14
        self.speed = 2
        self.direction = random.choice(["RIGHT", "LEFT", "UP", "DOWN"])
        self.target_x = x
        self.target_y = y
        self.frightened = False
        self.frightened_timer = 0
    
    def update(self, maze, player):
        # Comportamento in base allo stato
        if player.power_mode:
            if not self.frightened:
                self.frightened = True
                self.frightened_timer = 300
            # Comportamento di fuga
            self.flee(player)
        else:
            self.frightened = False
            # Comportamento normale: inseguimento
            self.chase(player)
        
        # Muovi nella direzione corrente
        old_x, old_y = self.x, self.y
        
        if self.direction == "RIGHT":
            self.x += self.speed
        elif self.direction == "LEFT":
            self.x -= self.speed
        elif self.direction == "UP":
            self.y -= self.speed
        elif self.direction == "DOWN":
            self.y += self.speed
        
        # Controlla collisioni con i muri
        if maze.is_wall(self.x, self.y):
            self.x, self.y = old_x, old_y
            # Scegli una nuova direzione casuale
            possible_dirs = ["RIGHT", "LEFT", "UP", "DOWN"]
            possible_dirs.remove(self.direction)  # Evita di tornare indietro
            self.direction = random.choice(possible_dirs)
        
        # Aggiorna il timer per lo stato spaventato
        if self.frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened = False
    
    def chase(self, player):
        # Semplice algoritmo di inseguimento
        if random.random() < 0.02:  # Aggiorna la direzione casualmente
            if self.x < player.x:
                self.direction = "RIGHT"
            elif self.x > player.x:
                self.direction = "LEFT"
            elif self.y < player.y:
                self.direction = "DOWN"
            elif self.y > player.y:
                self.direction = "UP"
    
    def flee(self, player):
        # Comportamento di fuga (opposto a inseguimento)
        if random.random() < 0.03:  # Aggiorna la direzione casualmente
            if self.x < player.x:
                self.direction = "LEFT"
            elif self.x > player.x:
                self.direction = "RIGHT"
            elif self.y < player.y:
                self.direction = "UP"
            elif self.y > player.y:
                self.direction = "DOWN"
    
    def draw(self, screen):
        # Disegna il fantasma
        color = self.color
        if self.frightened:
            color = (0, 0, 255)  # Blu quando spaventato
        
        # Corpo del fantasma
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.rect(screen, color, 
                        (self.x - self.radius, self.y, 
                         self.radius * 2, self.radius))
        
        # Disegna la parte ondulata del fantasma
        wave_points = []
        for i in range(5):
            wave_points.append((self.x - self.radius + i * (self.radius * 2) // 4, 
                              self.y + self.radius))
            wave_points.append((self.x - self.radius + (i + 0.5) * (self.radius * 2) // 4, 
                              self.y + self.radius - 5))
        pygame.draw.lines(screen, color, False, wave_points, 2)
        
        # Disegna gli occhi
        eye_offset = 4
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x - eye_offset), int(self.y - 2)), 5)
        pygame.draw.circle(screen, WHITE, 
                          (int(self.x + eye_offset), int(self.y - 2)), 5)
        
        # Disegna le pupille
        pupil_offset_x = 0
        if self.direction == "RIGHT":
            pupil_offset_x = 2
        elif self.direction == "LEFT":
            pupil_offset_x = -2
        
        pupil_color = BLACK if not self.frightened else WHITE
        pygame.draw.circle(screen, pupil_color, 
                          (int(self.x - eye_offset + pupil_offset_x), 
                           int(self.y - 2)), 2)
        pygame.draw.circle(screen, pupil_color, 
                          (int(self.x + eye_offset + pupil_offset_x), 
                           int(self.y - 2)), 2)

# Classe per i gettoni speciali
class Token:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.color = SILVER
        self.value = 100
    
    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, GOLD, (self.x, self.y), self.radius - 4)
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius - 6)
            # Disegna la "C" per Ciro
            font = pygame.font.SysFont(None, 20)
            text = font.render("C", True, WHITE)
            screen.blit(text, (self.x - 5, self.y - 7))

# Creazione degli oggetti di gioco
maze = Maze()
player = Player(35 * 1.5, 35 * 1.5)
ghosts = [
    Ghost(35 * 14, 35 * 1.5, RED),     # Rosso
    Ghost(35 * 1.5, 35 * 14, PINK),    # Rosa
    Ghost(35 * 14, 35 * 14, CYAN),     # Ciano
    Ghost(35 * 8, 35 * 8, ORANGE)      # Arancione
]

# Crea gettoni speciali
tokens = [
    Token(35 * 4, 35 * 4),
    Token(35 * 12, 35 * 4),
    Token(35 * 4, 35 * 12),
    Token(35 * 12, 35 * 12)
]

# Variabili di gioco
running = True
game_over = False
game_won = False
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Funzione per disegnare l'interfaccia
def draw_ui(screen, player):
    # Barra superiore
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, 40))
    
    # Punteggio
    score_text = font.render(f"Punteggio: {player.score}", True, WHITE)
    screen.blit(score_text, (20, 10))
    
    # Gettoni speciali
    tokens_text = font.render("Gettoni Speciali:", True, WHITE)
    screen.blit(tokens_text, (250, 10))
    
    # Disegna i gettoni speciali raccolti
    token_x = 450
    for token in tokens:
        if token.collected:
            pygame.draw.circle(screen, token.color, (token_x, 20), 10)
            pygame.draw.circle(screen, GOLD, (token_x, 20), 6)
            pygame.draw.circle(screen, token.color, (token_x, 20), 2)
            token_x += 25

# Loop principale del gioco
while running:
    # Gestione degli eventi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.next_direction = "UP"
            elif event.key == pygame.K_DOWN:
                player.next_direction = "DOWN"
            elif event.key == pygame.K_LEFT:
                player.next_direction = "LEFT"
            elif event.key == pygame.K_RIGHT:
                player.next_direction = "RIGHT"
            elif event.key == pygame.K_r and (game_over or game_won):
                # Reset del gioco
                maze = Maze()
                player = Player(35 * 1.5, 35 * 1.5)
                ghosts = [
                    Ghost(35 * 14, 35 * 1.5, RED),
                    Ghost(35 * 1.5, 35 * 14, PINK),
                    Ghost(35 * 14, 35 * 14, CYAN),
                    Ghost(35 * 8, 35 * 8, ORANGE)
                ]
                tokens = [
                    Token(35 * 4, 35 * 4),
                    Token(35 * 12, 35 * 4),
                    Token(35 * 4, 35 * 12),
                    Token(35 * 12, 35 * 12)
                ]
                game_over = False
                game_won = False
    
    if not game_over and not game_won:
        # Aggiornamento degli oggetti di gioco
        player.update(maze)
        
        # Controlla la raccolta dei gettoni
        for coin in maze.coins[:]:
            coin_x = coin[0] * maze.cell_size + maze.cell_size // 2
            coin_y = coin[1] * maze.cell_size + maze.cell_size // 2
            distance = math.sqrt((player.x - coin_x)**2 + (player.y - coin_y)**2)
            if distance < player.radius + 5:
                maze.coins.remove(coin)
                player.score += 10
        
        # Controlla la raccolta dei power pellet
        for pellet in maze.power_pellets[:]:
            pellet_x = pellet[0] * maze.cell_size + maze.cell_size // 2
            pellet_y = pellet[1] * maze.cell_size + maze.cell_size // 2
            distance = math.sqrt((player.x - pellet_x)**2 + (player.y - pellet_y)**2)
            if distance < player.radius + 8:
                maze.power_pellets.remove(pellet)
                player.power_mode = True
                player.power_timer = 300
                player.score += 50
        
        # Controlla la raccolta dei gettoni speciali
        for token in tokens:
            distance = math.sqrt((player.x - token.x)**2 + (player.y - token.y)**2)
            if distance < player.radius + token.radius and not token.collected:
                token.collected = True
                player.score += token.value
        
        # Aggiornamento dei fantasmi
        for ghost in ghosts:
            ghost.update(maze, player)
            
            # Controlla collisione con il giocatore
            distance = math.sqrt((player.x - ghost.x)**2 + (player.y - ghost.y)**2)
            if distance < player.radius + ghost.radius:
                if ghost.frightened:
                    # Il giocatore mangia il fantasma
                    ghost.x = maze.cell_size * 14
                    ghost.y = maze.cell_size * 1.5
                    ghost.frightened = False
                    player.score += 200
                else:
                    game_over = True
        
        # Controlla se il giocatore ha vinto
        if len(maze.coins) == 0 and len(maze.power_pellets) == 0:
            game_won = True
    
    # Disegno
    screen.fill(BLACK)
    maze.draw(screen)
    
    # Disegna i gettoni speciali
    for token in tokens:
        token.draw(screen)
    
    # Disegna il giocatore
    player.draw(screen)
    
    # Disegna i fantasmi
    for ghost in ghosts:
        ghost.draw(screen)
    
    # Disegna l'interfaccia utente
    draw_ui(screen, player)
    
    # Messaggio di game over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font.render("GAME OVER!", True, RED)
        restart_text = font.render("Premi R per riavviare", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
    
    # Messaggio di vittoria
    if game_won:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        win_text = font.render("HAI VINTO!", True, GOLD)
        score_text = font.render(f"Punteggio Finale: {player.score}", True, WHITE)
        restart_text = font.render("Premi R per giocare di nuovo", True, WHITE)
        
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()