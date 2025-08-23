import pygame
import random
import itertools
import time

# ---------------- CONFIGURACIÓN ----------------
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basquet Manager LUB 24-25")
FPS = 60

# Colores básicos
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Jugador
PLAYER_SIZE = 30
PLAYER_SPEED = 5

# Canchas
HOOP_A_X, HOOP_A_Y = WIDTH - 50, HEIGHT // 2
HOOP_B_X, HOOP_B_Y = 50, HEIGHT // 2
THREE_POINT_DIST = 200

# Tipografía
pygame.font.init()
FONT_BOLD = pygame.font.SysFont("Cambria", 14, bold=True)
FONT_REGULAR = pygame.font.SysFont("Cambria", 14)
FONT_TITLE_BOLD = pygame.font.SysFont("Cambria", 50, bold=True)
FONT_MENU_BOLD = pygame.font.SysFont("Cambria", 30, bold=True)
FONT_SUBTITLE_BOLD = pygame.font.SysFont("Cambria", 25, bold=True)

# Equipos y colores para camiseta/short
equipos = {
    "Nacional": {"camiseta": (255, 255, 255), "short": (0, 0, 255)},
    "Aguada": {"camiseta": (200, 0, 0), "short": (200, 0, 0)},
    "Malvín": {"camiseta": (0, 0, 200), "short": (0, 0, 200)},
    "Peñarol": {"camiseta": (255, 255, 0), "short": (0, 0, 0)},
    "Defensor Sporting": {"camiseta": (128, 0, 128), "short": (200, 0, 0)},
    "Cordón": {"camiseta": (135, 206, 250), "short": (200, 0, 0)},
    "Biguá": {"camiseta": (0, 0, 255), "short": (200, 0, 0)},
    "Hebraica Macabi": {"camiseta": (255, 255, 0), "short": (200, 0, 0)},
    "Urunday Universitario": {"camiseta": (0, 128, 0), "short": (255, 255, 255)},
    "Urupan": {"camiseta": (0, 128, 0), "short": (255, 255, 255)},
    "Welcome": {"camiseta": (200, 0, 0), "short": (255, 255, 255)},
    "Trouville": {"camiseta": (200, 0, 0), "short": (255, 255, 255)}
}

# Rosters completos de jugadores por equipo
full_rosters = {
    "Aguada": ["Santiago Vidal", "Juan Santiso", "Federico Pereiras", "Joaquín Osimani", "Agustín Zuvich", "Donald Sims", "Emmitt Holt", "Frank Hassell", "Ignacio Stoll", "Agustín Gentile", "Matías Benítez"],
    "Biguá": ["Federico Bavosi", "Álex López", "Leandro Cerminato", "Juan Ignacio Ducasse", "Nicolás Catalá", "Isaac Hamilton", "Joshua Cunningham", "Maique Tavares","Vinicius Malachias", "Matías Espinosa", "Thiago Rodríguez", "Guillermo Jones", "Maximiliano Greiver"],
    "Cordón": ["Mateo Giano", "Emiliano Bonet", "Xavier Cousté", "Diego Pena García", "Fernando Verrone", "Deshone Hicks", "Victor Andrade", "Massine Fall", "Nicolás Lema", "Michael Viazzo", "Matías Schell", "Santiago García", "Lautaro Echevarría"],
    "Defensor Sporting": ["Facundo Terra", "Juan Andrés Galletto", "Mauro Zubiaurre", "Federico Soto", "Theo Metzger", "Malik Curry", "Andriy Grytsak", "James Montgomery", "Mateo Mac Mullen", "Charlie García", "Mateo Bianchi"],
    "Hebraica Macabi": ["Manuel Mayora", "Manuel Saavedra", "Brian García", "Santiago Massa", "Federico Haller", "Skyler Hogan", "Daviyon Draper", "Kingsley Okanu", "Joaquín Aszyn", "Martín Fazio", "Martín Astramskas", "Lautaro Viatri"],
    "Malvín": ["Lucas Capalbo", "Manuel Romero", "Marcel Souberbielle", "Kiril Wachsmann", "Mauricio Arregui", "Carlton Guyton", "Anthony Hilliard", "Nicolás Martínez", "Felipe Serdio", "Pedro Mendive", "Nahuel Rodríguez", "Franco Brun", "Marcelo Rosas"],
    "Nacional": ["Mateo Sarni", "Gastón Semiglia", "Bernardo Barrera", "Gianfranco Espíndola", "Sebastián Ottonello", "James Feldeine", "Néstor Colemanares", "Manny Suárez", "Patricio Prieto", "Agustín Méndez", "Lucas Fernández"],
    "Peñarol": ["Luciano Parodi", "Salvador Zanotta", "Ignacio Xavier", "Emiliano Serres", "Martín Rojas", "Brandon Robinson", "Josué Erazo", "Luis Santos", "Santiago Calimares", "Edu Medina", "Roodvan Osores", "Ignacio Wener"],
    "Trouville": ["Santiago Fernández", "Guillermo Curbelo", "Guillermo Souza", "Martín Tessadri", "Mateo Bolívar", "Felipe Queiros", "Marlon Díaz", "Nicolás Bessio", "Santiago Tucuna", "Pablo Gómez"],
    "Urunday Universitario": ["Alejandro Acosta", "Fernando Martínez", "Iván Loriente", "Rodrigo Brause", "Nicolás Delgado", "Robert Whitfield", "Ivan Aska", "Gerard DeVaughn", "Giovanni Corbisiero", "Bruno Curadossi", "Felipe Satut"],
    "Urupan": ["Pierino Rüsch", "Facundo Medina", "Octavio Medina", "Nahuel Amichetti", "Jonathan Sacco", "Abel Agarbado", "Tony Wroten", "Anthony Peacock", "Rafael Previatti", "Tiago Leites", "Rodrigo Iriarte"],
    "Welcome": ["Juan Martín Ortíz", "Sebastián Álvarez", "Ángel Arévalo", "Rodrigo Cardozo", "Marcos Geller", "Gustavo Barrera", "Santiago Moglia", "Justin Sylver", "Gerónimo Viera", "Lucas Silva", "Emanuel Gramajo", "Matías Núñez", "Juan Terra", "Gabriel Silveira"]
}

# Dificultad (1-12, siendo 1 el más difícil y 12 el más fácil)
dificultad = {
    "Nacional": 1, "Aguada": 2, "Malvín": 3, "Peñarol": 4, "Defensor Sporting": 5,
    "Cordón": 6, "Biguá": 7, "Hebraica Macabi": 8, "Urunday Universitario": 9,
    "Urupan": 10, "Welcome": 11, "Trouville": 12
}

# Tabla de posiciones
tabla_posiciones = {eq: {"PJ": 0, "G": 0, "P": 0, "Pts": 0} for eq in equipos.keys()}

# Presupuestos de los equipos en Pesos Uruguayos
team_budgets = {
    "Aguada": 2_000_000,
    "Biguá": 1_000_000,
    "Cordón": 1_000_000,
    "Defensor Sporting": 1_000_000,
    "Hebraica Macabi": 1_000_000,
    "Malvín": 1_000_000,
    "Nacional": 2_500_000,
    "Peñarol": 2_500_000,
    "Trouville": 1_000_000,
    "Urunday Universitario": 1_000_000,
    "Urupan": 1_000_000,
    "Welcome": 1_000_000
}

# Costo fijo de cada jugador
PLAYER_PRICE = 150_000

# Global para la alineación del usuario
current_user_lineup_names = []

# Listas de jugadores para el mercado de transferencias
players_for_sale_ai = []  # Jugadores de la IA que puedes comprar
players_for_sale_user = []  # Jugadores que tú pones a la venta

# ---------------- CLASES ----------------
class Player:
    def __init__(self, x, y, camiseta_color, short_color, team, name=""):
        self.x = x
        self.y = y
        self.camiseta_color = camiseta_color
        self.short_color = short_color
        self.team = team
        self.name = name
        self.has_ball = False
        self.fouls = 0
        
        self.ethnicity = random.choice(["caucásica"] * 3 + ["africana"] * 2)
        if self.ethnicity == "caucásica":
            self.skin_color = (255, 224, 189)
        else:
            self.skin_color = (139, 69, 19)

    def draw(self):
        pygame.draw.circle(WIN, self.skin_color, (self.x, self.y - 30), 10)
        pygame.draw.rect(WIN, self.camiseta_color, (self.x - 15, self.y - 20, 30, 20))
        pygame.draw.rect(WIN, self.short_color, (self.x - 15, self.y, 30, 15))
        pygame.draw.rect(WIN, WHITE, (self.x - 10, self.y + 15, 8, 10))
        pygame.draw.rect(WIN, WHITE, (self.x + 2, self.y + 15, 8, 10))
        pygame.draw.rect(WIN, BLACK, (self.x - 10, self.y + 25, 8, 5))
        pygame.draw.rect(WIN, BLACK, (self.x + 2, self.y + 25, 8, 5))

        if self.has_ball:
            pygame.draw.circle(WIN, ORANGE, (self.x, self.y - 10), 10)

    def move(self, keys, up, down, left, right):
        if keys[up] and self.y - PLAYER_SPEED > 0:
            self.y -= PLAYER_SPEED
        if keys[down] and self.y + PLAYER_SPEED < HEIGHT:
            self.y += PLAYER_SPEED
        if keys[left] and self.x - PLAYER_SPEED > 0:
            self.x -= PLAYER_SPEED
        if keys[right] and self.x + PLAYER_SPEED < WIDTH:
            self.x += PLAYER_SPEED

    def move_to(self, target_x, target_y, speed):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist != 0:
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
        
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

# ---------------- FUNCIONES ----------------
def generar_calendario(equipos_list):
    partidos = []
    for ida, vuelta in itertools.combinations(equipos_list, 2):
        partidos.append((ida, vuelta))
        partidos.append((vuelta, ida))
    return partidos

def mostrar_tabla_pantalla():
    run = True
    while run:
        WIN.fill(WHITE)
        title_text = FONT_TITLE_BOLD.render("Tabla de Posiciones", True, BLACK)
        WIN.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 50)))

        header_text = FONT_REGULAR.render("Equipo      | PJ | G | P | Pts", True, BLACK)
        WIN.blit(header_text, (50, 120))

        orden = sorted(tabla_posiciones.items(), key=lambda x: x[1]["Pts"], reverse=True)
        
        for i, (eq, stats) in enumerate(orden):
            y_pos = 160 + i * 30
            eq_text = FONT_REGULAR.render(f"{eq:<20} {stats['PJ']:<4} {stats['G']:<4} {stats['P']:<4} {stats['Pts']:<4}", True, BLACK)
            WIN.blit(eq_text, (50, y_pos))

        back_text = FONT_REGULAR.render("Volver", True, BLACK)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        WIN.blit(back_text, back_rect)
        if back_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, back_rect.inflate(10, 5), 3)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and back_rect.collidepoint(event.pos):
                    run = False

def simular_partido(eq1, eq2):
    nivel1 = 13 - dificultad[eq1]
    nivel2 = 13 - dificultad[eq2]
    total_nivel = nivel1 + nivel2
    
    if total_nivel == 0:
        prob_eq1 = 0.5
    else:
        prob_eq1 = nivel1 / total_nivel
    
    score_base = random.uniform(70, 100)
    score1 = int(score_base * (prob_eq1 + random.uniform(-0.1, 0.1)))
    score2 = int(score_base * ((1 - prob_eq1) + random.uniform(-0.1, 0.1)))
    
    score1 = max(60, min(110, score1))
    score2 = max(60, min(110, score2))

    tabla_posiciones[eq1]["PJ"] += 1
    tabla_posiciones[eq2]["PJ"] += 1
    if score1 > score2:
        tabla_posiciones[eq1]["G"] += 1
        tabla_posiciones[eq1]["Pts"] += 2
        tabla_posiciones[eq2]["P"] += 1
        ganador = eq1
    else:
        tabla_posiciones[eq2]["G"] += 1
        tabla_posiciones[eq2]["Pts"] += 2
        tabla_posiciones[eq1]["P"] += 1
        ganador = eq2
    print(f"{eq1} {score1} - {score2} {eq2} | Ganador: {ganador}")
    return score1, score2

def dibujar_cancha():
    WIN.fill(BROWN)
    pygame.draw.rect(WIN, BLACK, (5, 5, WIDTH - 10, HEIGHT - 10), 5)
    pygame.draw.line(WIN, BLACK, (WIDTH // 2, 5), (WIDTH // 2, HEIGHT - 5), 3)
    pygame.draw.circle(WIN, BLACK, (WIDTH // 2, HEIGHT // 2), 60, 3)
    
    pygame.draw.rect(WIN, BLACK, (WIDTH - 150, HEIGHT // 2 - 60, 145, 120), 3)
    pygame.draw.circle(WIN, BLACK, (WIDTH - 150, HEIGHT // 2), 60, 3)
    
    pygame.draw.rect(WIN, BLACK, (5, HEIGHT // 2 - 60, 145, 120), 3)
    pygame.draw.circle(WIN, BLACK, (150, HEIGHT // 2), 60, 3)
    
    pygame.draw.arc(WIN, BLACK, (WIDTH - THREE_POINT_DIST - 50, HEIGHT // 2 - THREE_POINT_DIST, 2 * THREE_POINT_DIST, 2 * THREE_POINT_DIST), 1.57, 4.71, 3)
    pygame.draw.arc(WIN, BLACK, (50 - THREE_POINT_DIST, HEIGHT // 2 - THREE_POINT_DIST, 2 * THREE_POINT_DIST, 2 * THREE_POINT_DIST), -1.57, 1.57, 3)
    
    pygame.draw.rect(WIN, BLACK, (50 - 5, HOOP_B_Y - 30, 5, 60))
    pygame.draw.rect(WIN, ORANGE, (HOOP_B_X - 15, HOOP_B_Y - 15, 30, 30), 5)
    pygame.draw.line(WIN, ORANGE, (HOOP_B_X - 15, HOOP_B_Y), (HOOP_B_X, HOOP_B_Y), 3)

    pygame.draw.rect(WIN, BLACK, (HOOP_A_X, HOOP_A_Y - 30, 5, 60))
    pygame.draw.rect(WIN, ORANGE, (HOOP_A_X - 15, HOOP_A_Y - 15, 30, 30), 5)
    pygame.draw.line(WIN, ORANGE, (HOOP_A_X + 15, HOOP_A_Y), (HOOP_A_X, HOOP_A_Y), 3)

    pygame.draw.line(WIN, BLACK, (HOOP_A_X - 5, HOOP_A_Y - 15), (HOOP_A_X - 5, HOOP_A_Y + 15), 3)
    pygame.draw.line(WIN, BLACK, (HOOP_B_X + 5, HOOP_B_Y - 15), (HOOP_B_X + 5, HOOP_B_Y + 15), 3)

def tiro_libre(shooter, num_tiros, marcador, is_player_team):
    tiros_anotados = 0
    for i in range(num_tiros):
        run_free_throw = True
        while run_free_throw:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if random.random() < 0.7:
                            tiros_anotados += 1
                            if is_player_team:
                                marcador["A"] += 1
                            else:
                                marcador["B"] += 1
                        run_free_throw = False
            
            dibujar_cancha()
            
            if is_player_team:
                shooter.x, shooter.y = HOOP_A_X - 150, HOOP_A_Y
            else:
                shooter.x, shooter.y = HOOP_B_X + 150, HOOP_B_Y
            shooter.draw()

            if is_player_team:
                text = FONT_REGULAR.render(f"¡Falta! Tiros Libres: {i+1} de {num_tiros}", True, BLACK)
            else:
                text = FONT_REGULAR.render(f"¡Falta! Tiro Libre rival: {i+1} de {num_tiros}", True, BLACK)
            
            WIN.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            pygame.display.update()
            
            time.sleep(1)

    return tiros_anotados

def jugar_partido_usuario(equipo_usuario, equipo_rival):
    color_user = equipos[equipo_usuario]["camiseta"]
    short_user = equipos[equipo_usuario]["short"]
    color_rival = equipos[equipo_rival]["camiseta"]
    short_rival = equipos[equipo_rival]["short"]

    player_team = []
    roster_base = full_rosters.get(equipo_usuario, [])
    # Revisa si la alineación del usuario ha sido modificada por transferencias
    lineup_to_use = current_user_lineup_names if len(current_user_lineup_names) == 5 else roster_base[:5]

    for i, player_name in enumerate(lineup_to_use):
        player_team.append(Player(100, i * 100 + 50, color_user, short_user, "A", name=player_name))

    enemy_team = []
    enemy_roster_base = full_rosters.get(equipo_rival, [])
    for i, player_name in enumerate(enemy_roster_base[:5]):
        enemy_team.append(Player(WIDTH - 150, i * 100 + 50, color_rival, short_rival, "B", name=player_name))

    ball_owner = player_team[0]
    ball_owner.has_ball = True
    controlled_player = player_team[0]

    marcador = {"A": 0, "B": 0}
    clock = pygame.time.Clock()
    enemy_speed = 2 + (13 - dificultad[equipo_rival]) * 0.2
    
    faltas_equipo = {"A": 0, "B": 0}
    
    for cuarto in range(1, 5):
        tiempo_inicio = time.time()
        run = True
        while run:
            clock.tick(FPS)
            keys = pygame.key.get_pressed()
            tiempo_transcurrido = int(time.time() - tiempo_inicio)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and ball_owner == controlled_player:
                        dist_to_hoop_user = ((ball_owner.x - HOOP_A_X)**2 + (ball_owner.y - HOOP_A_Y)**2)**0.5
                        points = 2
                        if dist_to_hoop_user > THREE_POINT_DIST:
                            points = 3
                        
                        if random.random() < 0.6:
                            marcador["A"] += points
                        
                        ball_owner.has_ball = False
                        ball_owner = enemy_team[0]
                        ball_owner.has_ball = True
                            
                    if event.key == pygame.K_RETURN and ball_owner == controlled_player:
                        team = player_team
                        closest = min([p for p in team if p != ball_owner],
                                      key=lambda p: (p.x - ball_owner.x) ** 2 + (p.y - ball_owner.y) ** 2)
                        ball_owner.has_ball = False
                        ball_owner = closest
                        ball_owner.has_ball = True
                    
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        controlled_player = ball_owner

            controlled_player.move(keys, pygame.K_f, pygame.K_v, pygame.K_o, pygame.K_p)

            for e in enemy_team:
                if e.has_ball:
                    if abs(e.x - HOOP_B_X) < 50 and abs(e.y - HOOP_B_Y) < 50:
                        dist_to_hoop_rival = ((e.x - HOOP_B_X)**2 + (e.y - HOOP_B_Y)**2)**0.5
                        points_rival = 2
                        if dist_to_hoop_rival > THREE_POINT_DIST:
                            points_rival = 3
                        
                        if random.random() < (13 - dificultad[equipo_rival]) * 0.05:
                            marcador["B"] += points_rival
                            e.has_ball = False
                            ball_owner = player_team[0]
                            ball_owner.has_ball = True
                        else:
                            closest_teammate = min([p for p in enemy_team if p != e],
                                                    key=lambda p: (p.x - e.x) ** 2 + (p.y - e.y) ** 2)
                            e.has_ball = False
                            ball_owner = closest_teammate
                            ball_owner.has_ball = True
                    else:
                        e.move_to(HOOP_B_X, HOOP_B_Y, enemy_speed)
                else:
                    e.move_to(ball_owner.x, ball_owner.y, enemy_speed)
                    if ball_owner == controlled_player and abs(e.x - ball_owner.x) < 20 and abs(e.y - ball_owner.y) < 20:
                        if random.random() < 0.1:
                            e.fouls += 1
                            faltas_equipo["B"] += 1
                            print(f"Falta del equipo {equipo_rival} sobre {equipo_usuario}!")
                            ball_owner.has_ball = False
                            
                            num_tiros = 0
                            if ((controlled_player.x - HOOP_A_X)**2 + (controlled_player.y - HOOP_A_Y)**2)**0.5 < THREE_POINT_DIST:
                                num_tiros = 2
                            else:
                                num_tiros = 3
                            
                            tiro_libre(controlled_player, num_tiros, marcador, True)
                            ball_owner = enemy_team[0]
                            ball_owner.has_ball = True
                        else:
                            ball_owner.has_ball = False
                            e.has_ball = True
                            ball_owner = e
            
            for p in player_team:
                if p != controlled_player:
                    if ball_owner == p:
                        if abs(p.x - HOOP_A_X) < 50 and abs(p.y - HOOP_A_Y) < 50:
                            if random.random() < 0.6:
                                p.has_ball = False
                                ball_owner = controlled_player
                                ball_owner.has_ball = True
                            else:
                                dist_to_hoop_ai_user = ((p.x - HOOP_A_X)**2 + (p.y - HOOP_A_Y)**2)**0.5
                                points_ai_user = 2
                                if dist_to_hoop_ai_user > THREE_POINT_DIST:
                                    points_ai_user = 3
                                if random.random() < 0.7:
                                    marcador["A"] += points_ai_user
                                p.has_ball = False
                                ball_owner = enemy_team[0]
                                ball_owner.has_ball = True
                        else:
                            p.move_to(HOOP_A_X, HOOP_A_Y, PLAYER_SPEED * 0.8)
                    else:
                        p.move_to(controlled_player.x + random.randint(-50, 50), controlled_player.y + random.randint(-50, 50), PLAYER_SPEED * 0.8)

            dibujar_cancha()
            for p in player_team + enemy_team:
                p.draw()
            
            score_text = FONT_REGULAR.render(f"{equipo_usuario}:{marcador['A']}  {equipo_rival}:{marcador['B']}", True, BLACK)
            WIN.blit(score_text, (WIDTH // 2 - 100, 20))
            tiempo_text = FONT_REGULAR.render(f"Tiempo cuarto {cuarto}: {tiempo_transcurrido}s", True, BLACK)
            WIN.blit(tiempo_text, (WIDTH // 2 - 130, 60))
            
            faltas_text = FONT_REGULAR.render(f"Faltas: {faltas_equipo['A']} - {faltas_equipo['B']}", True, BLACK)
            WIN.blit(faltas_text, (WIDTH // 2 - 60, 90))
            
            pygame.display.update()

            if tiempo_transcurrido >= 60:
                run = False

        print(f"Fin del cuarto {cuarto}: {equipo_usuario} {marcador['A']} - {marcador['B']} {equipo_rival}")

    tabla_posiciones[equipo_usuario]["PJ"] += 1
    tabla_posiciones[equipo_rival]["PJ"] += 1
    if marcador["A"] > marcador["B"]:
        tabla_posiciones[equipo_usuario]["G"] += 1
        tabla_posiciones[equipo_usuario]["Pts"] += 2
        tabla_posiciones[equipo_rival]["P"] += 1
        print(f"Ganaste {equipo_usuario} {marcador['A']}-{marcador['B']} {equipo_rival}")
    else:
        tabla_posiciones[equipo_rival]["G"] += 1
        tabla_posiciones[equipo_rival]["Pts"] += 2
        tabla_posiciones[equipo_usuario]["P"] += 1
        print(f"Perdiste {equipo_usuario} {marcador['A']}-{marcador['B']} {equipo_rival}")

# ---------------- MENÚS ----------------
def alineacion_menu(equipo_usuario, initial_lineup):
    global current_user_lineup_names
    selected_lineup = list(initial_lineup)
    full_roster = full_rosters.get(equipo_usuario, [])
    selected_player_name = None
    
    run = True
    while run:
        WIN.fill(WHITE)

        title_text = FONT_MENU_BOLD.render(f"Alineación de {equipo_usuario}", True, BLACK)
        WIN.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 30)))
        
        roster_y = 100
        player_rects = []
        for i, player_name in enumerate(full_roster):
            text_color = BLACK
            if player_name in selected_lineup:
                text_color = ORANGE if player_name == selected_player_name else BLACK
            
            text = FONT_REGULAR.render(player_name, True, text_color)
            rect = text.get_rect(topleft=(50, roster_y + i * 20))
            player_rects.append((rect, player_name))
            WIN.blit(text, rect)
            
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(WIN, LIGHT_GRAY, rect.inflate(10, 5), 1)

        lineup_x = WIDTH // 2 + 50
        lineup_y = 100
        lineup_rects = []
        for i in range(5):
            rect = pygame.Rect(lineup_x, lineup_y + i * 40, 200, 30)
            lineup_rects.append(rect)
            
            if i < len(selected_lineup):
                player_name = selected_lineup[i]
                text_color = BLACK
                if player_name == selected_player_name:
                    pygame.draw.rect(WIN, ORANGE, rect, 3)
                else:
                    pygame.draw.rect(WIN, BLACK, rect, 2)
                
                player_text = FONT_REGULAR.render(player_name, True, BLACK)
                WIN.blit(player_text, (lineup_x + 5, lineup_y + i * 40 + 5))
            else:
                pygame.draw.rect(WIN, BLACK, rect, 2)
                placeholder_text = FONT_REGULAR.render("Vacío", True, GRAY)
                WIN.blit(placeholder_text, (lineup_x + 5, lineup_y + i * 40 + 5))
        
        save_text = FONT_MENU_BOLD.render("Guardar", True, BLACK)
        save_rect = save_text.get_rect(center=(WIDTH // 2 - 100, HEIGHT - 50))
        WIN.blit(save_text, save_rect)
        if save_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, save_rect.inflate(10, 5), 3)

        back_text = FONT_MENU_BOLD.render("Volver", True, BLACK)
        back_rect = back_text.get_rect(center=(WIDTH // 2 + 100, HEIGHT - 50))
        WIN.blit(back_text, back_rect)
        if back_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, back_rect.inflate(10, 5), 3)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked_player = None
                    for rect, player_name in player_rects:
                        if rect.collidepoint(event.pos):
                            clicked_player = player_name
                            break
                    
                    if not clicked_player:
                        for i, rect in enumerate(lineup_rects):
                            if rect.collidepoint(event.pos) and i < len(selected_lineup):
                                clicked_player = selected_lineup[i]
                                break

                    if clicked_player:
                        if selected_player_name is None:
                            if clicked_player in selected_lineup:
                                selected_player_name = clicked_player
                            elif len(selected_lineup) < 5:
                                selected_lineup.append(clicked_player)
                        else:
                            if clicked_player == selected_player_name:
                                selected_player_name = None
                            else:
                                player_to_swap_out = selected_player_name
                                player_to_swap_in = clicked_player
                                
                                if player_to_swap_in in selected_lineup:
                                    idx1 = selected_lineup.index(player_to_swap_out)
                                    idx2 = selected_lineup.index(player_to_swap_in)
                                    selected_lineup[idx1], selected_lineup[idx2] = selected_lineup[idx2], selected_lineup[idx1]
                                else:
                                    idx1 = selected_lineup.index(player_to_swap_out)
                                    selected_lineup[idx1] = player_to_swap_in
                                
                                selected_player_name = None
                    
                    if save_rect.collidepoint(event.pos):
                        if len(selected_lineup) == 5:
                            current_user_lineup_names = selected_lineup
                            run = False
                        else:
                            error_text = FONT_REGULAR.render("Debes seleccionar 5 jugadores.", True, RED)
                            WIN.blit(error_text, error_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
                            pygame.display.update()
                            time.sleep(1)
                    
                    if back_rect.collidepoint(event.pos):
                        run = False
                        
    return current_user_lineup_names

def transfer_menu(equipo_usuario):
    global team_budgets, players_for_sale_user, current_user_lineup_names, full_rosters
    
    run = True
    message = ""

    # Generar lista de jugadores transferibles de la IA (solo si está vacía)
    if not players_for_sale_ai:
        for eq_name, roster in full_rosters.items():
            if eq_name != equipo_usuario and len(roster) > 5:
                # La IA pone a la venta un jugador aleatorio de su plantel que no esté en su quinteto inicial
                ai_player_to_sell = random.choice(roster[5:]) 
                players_for_sale_ai.append({"equipo": eq_name, "jugador": ai_player_to_sell})

    while run:
        WIN.fill(WHITE)

        title_text = FONT_MENU_BOLD.render("Mercado de Transferencias", True, BLACK)
        WIN.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 30)))

        # Mostrar presupuesto del usuario
        budget_text = FONT_REGULAR.render(f"Presupuesto: ${team_budgets[equipo_usuario]:,}", True, BLACK)
        WIN.blit(budget_text, (WIDTH // 2 - 150, 80))

        # Sección de jugadores a la venta (IA)
        list_ai_title = FONT_SUBTITLE_BOLD.render("Jugadores Transferibles", True, BLACK)
        WIN.blit(list_ai_title, (50, 120))
        
        ai_player_rects = []
        for i, player_data in enumerate(players_for_sale_ai):
            player_name = player_data["jugador"]
            equipo_origen = player_data["equipo"]
            text = FONT_REGULAR.render(f"{player_name} ({equipo_origen}) - ${PLAYER_PRICE:,}", True, BLACK)
            rect = text.get_rect(topleft=(50, 150 + i * 20))
            ai_player_rects.append((rect, player_data))
            WIN.blit(text, rect)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(WIN, ORANGE, rect.inflate(10, 5), 1)

        # Sección de mi plantel
        list_user_title = FONT_SUBTITLE_BOLD.render("Mi Plantel", True, BLACK)
        WIN.blit(list_user_title, (WIDTH // 2 + 50, 120))
        
        user_player_rects = []
        for i, player_name in enumerate(full_rosters[equipo_usuario]):
            text_color = BLACK
            # Indicar si el jugador ya está a la venta
            if player_name in [p['jugador'] for p in players_for_sale_user]:
                text_color = RED
            
            text = FONT_REGULAR.render(player_name, True, text_color)
            rect = text.get_rect(topleft=(WIDTH // 2 + 50, 150 + i * 20))
            user_player_rects.append((rect, player_name))
            WIN.blit(text, rect)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(WIN, ORANGE, rect.inflate(10, 5), 1)

        # Jugadores a la venta por el usuario
        if players_for_sale_user:
            selling_title = FONT_REGULAR.render("A la Venta:", True, BLACK)
            WIN.blit(selling_title, (WIDTH // 2 + 50, 150 + len(full_rosters[equipo_usuario]) * 20 + 20))
            for i, p_data in enumerate(players_for_sale_user):
                player_name = p_data['jugador']
                text = FONT_REGULAR.render(f"{player_name} - ${PLAYER_PRICE:,}", True, RED)
                WIN.blit(text, (WIDTH // 2 + 50, 150 + len(full_rosters[equipo_usuario]) * 20 + 40 + i * 20))


        # Botones de menú
        back_text = FONT_MENU_BOLD.render("Volver", True, BLACK)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        WIN.blit(back_text, back_rect)
        if back_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, back_rect.inflate(10, 5), 3)

        # Mensajes de estado
        if message:
            msg_text = FONT_REGULAR.render(message, True, BLACK)
            WIN.blit(msg_text, msg_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Lógica para comprar
                    for rect, player_data in ai_player_rects:
                        if rect.collidepoint(event.pos):
                            player_name = player_data['jugador']
                            equipo_origen = player_data['equipo']
                            
                            if team_budgets[equipo_usuario] >= PLAYER_PRICE:
                                team_budgets[equipo_usuario] -= PLAYER_PRICE
                                full_rosters[equipo_usuario].append(player_name)
                                full_rosters[equipo_origen].remove(player_name)
                                players_for_sale_ai.remove(player_data)
                                message = f"¡Has comprado a {player_name} de {equipo_origen}!"
                                print(message)
                            else:
                                message = "¡Presupuesto insuficiente!"
                                print(message)
                            break
                    
                    # Lógica para poner a la venta
                    for rect, player_name in user_player_rects:
                        if rect.collidepoint(event.pos):
                            # Evitar poner a la venta un jugador ya a la venta o en la alineación
                            if player_name not in [p['jugador'] for p in players_for_sale_user] and player_name not in current_user_lineup_names:
                                players_for_sale_user.append({"equipo": equipo_usuario, "jugador": player_name})
                                message = f"¡{player_name} ha sido puesto a la venta!"
                                print(message)
                            elif player_name in [p['jugador'] for p in players_for_sale_user]:
                                message = "Ese jugador ya está a la venta."
                                print(message)
                            elif player_name in current_user_lineup_names:
                                message = "No puedes vender a un jugador de tu quinteto inicial."
                                print(message)
                            break
                    
                    if back_rect.collidepoint(event.pos):
                        run = False
    
    # AI de compra/venta al salir del menú
    ai_transfers(equipo_usuario)

def ai_transfers(equipo_usuario):
    global team_budgets, players_for_sale_ai, players_for_sale_user, full_rosters

    # Lógica para que la IA compre jugadores del usuario
    comprador_list = [eq for eq in equipos.keys() if eq != equipo_usuario and team_budgets[eq] >= PLAYER_PRICE]
    if comprador_list:
        for player_data in players_for_sale_user[:]: # Copia para evitar problemas al modificar
            # Los equipos de la IA tienen una pequeña probabilidad de comprar
            if random.random() < 0.3:
                comprador = random.choice(comprador_list)
                if comprador:
                    player_name = player_data['jugador']
                    team_budgets[comprador] -= PLAYER_PRICE
                    team_budgets[equipo_usuario] += PLAYER_PRICE
                    
                    # Actualizar rosters
                    full_rosters[comprador].append(player_name)
                    full_rosters[equipo_usuario].remove(player_name)
                    
                    players_for_sale_user.remove(player_data)
                    
                    print(f"¡{comprador} ha comprado a {player_name} por ${PLAYER_PRICE:,}! Tu presupuesto es ahora: ${team_budgets[equipo_usuario]:,}")

def main_menu():
    run = True
    while run:
        WIN.fill(WHITE)
        
        title_text = FONT_TITLE_BOLD.render("Basquet Manager LUB 24-25", True, BLACK)
        subtitle_text = FONT_SUBTITLE_BOLD.render("Selecciona tu equipo", True, BLACK)
        WIN.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 50)))
        WIN.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, 120)))

        equipo_buttons = []
        start_y = 200
        for i, equipo in enumerate(equipos.keys()):
            text = FONT_REGULAR.render(equipo, True, BLACK)
            rect = text.get_rect(center=(WIDTH // 2, start_y + i * 40))
            equipo_buttons.append((rect, equipo))
            WIN.blit(text, rect)
            
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(WIN, ORANGE, rect.inflate(10, 5), 3)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for rect, equipo in equipo_buttons:
                        if rect.collidepoint(event.pos):
                            return equipo
    return None

def game_menu(equipo_usuario, jornada, partido_actual):
    global current_user_lineup_names
    run = True
    while run:
        WIN.fill(WHITE)

        title_text = FONT_REGULAR.render(f"Jornada {jornada}", True, BLACK)
        WIN.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 50)))
        
        partido_text = FONT_REGULAR.render(f"Próximo Partido: {partido_actual[0]} vs {partido_actual[1]}", True, BLACK)
        WIN.blit(partido_text, partido_text.get_rect(center=(WIDTH // 2, 120)))

        play_text = FONT_REGULAR.render("Jugar Partido", True, BLACK)
        simulate_text = FONT_REGULAR.render("Simular Jornada", True, BLACK)
        table_text = FONT_REGULAR.render("Ver Tabla de Posiciones", True, BLACK)
        lineup_text = FONT_REGULAR.render("Alineación", True, BLACK)
        transfer_text = FONT_REGULAR.render("Transferencias", True, BLACK) 

        play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        simulate_rect = simulate_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        table_rect = table_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        lineup_rect = lineup_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        transfer_rect = transfer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180)) 

        WIN.blit(play_text, play_rect)
        WIN.blit(simulate_text, simulate_rect)
        WIN.blit(table_text, table_rect)
        WIN.blit(lineup_text, lineup_rect)
        WIN.blit(transfer_text, transfer_rect)

        if play_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, play_rect.inflate(10, 5), 3)
        if simulate_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, simulate_rect.inflate(10, 5), 3)
        if table_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, table_rect.inflate(10, 5), 3)
        if lineup_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, ORANGE, lineup_rect.inflate(10, 5), 3)
        if transfer_rect.collidepoint(pygame.mouse.get_pos()): 
            pygame.draw.rect(WIN, ORANGE, transfer_rect.inflate(10, 5), 3)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_rect.collidepoint(event.pos):
                        return "play"
                    if simulate_rect.collidepoint(event.pos):
                        return "simulate"
                    if table_rect.collidepoint(event.pos):
                        mostrar_tabla_pantalla()
                        break
                    if lineup_rect.collidepoint(event.pos):
                        current_user_lineup_names = alineacion_menu(equipo_usuario, current_user_lineup_names)
                        break
                    if transfer_rect.collidepoint(event.pos):
                        transfer_menu(equipo_usuario)
                        break
    return None

def main_liga():
    global current_user_lineup_names, players_for_sale_ai, players_for_sale_user
    
    equipo_usuario = main_menu()
    if equipo_usuario is None:
        return
    
    current_user_lineup_names = full_rosters.get(equipo_usuario, [])[:5]
    
    equipos_list = list(equipos.keys())
    calendario = generar_calendario(equipos_list)
    partidos_por_jornada = len(equipos_list) // 2
    
    jornada_actual = 1
    for i in range(0, len(calendario), partidos_por_jornada):
        # Reiniciar listas de transferibles para la nueva jornada
        players_for_sale_ai = []
        players_for_sale_user = []

        partidos_jornada = calendario[i:i + partidos_por_jornada]
        
        partido_usuario = None
        for partido in partidos_jornada:
            if equipo_usuario in partido:
                partido_usuario = partido
                break
        
        action = game_menu(equipo_usuario, jornada_actual, partido_usuario)
        
        if action == "quit":
            break
        
        if action == "play":
            jugar_partido_usuario(equipo_usuario, partido_usuario[1] if partido_usuario[0] == equipo_usuario else partido_usuario[0])
            partidos_jornada.remove(partido_usuario)
        
        for p in partidos_jornada:
            if p == partido_usuario and action == "play":
                continue 
            simular_partido(p[0], p[1])
        
        jornada_actual += 1

    print("\n¡LIGA FINALIZADA!")
    print("Tabla de posiciones final:")
    mostrar_tabla_pantalla()
    time.sleep(5)
    
if __name__ == "__main__":
    main_liga()