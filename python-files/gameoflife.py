import pygame

# =========================
#        HILFSFUNKTIONEN
# =========================

def draw_grid(screen, cell_size, width, height, grid, offset_x, offset_y):
    """
    Zeichnet das Spielfeldgitter und die lebenden Zellen.

    Parameter:
    - screen: Das pygame-Fenster, auf das gezeichnet wird.
    - cell_size: Größe einer Zelle in Pixeln.
    - width, height: Größe des Fensters.
    - grid: Dictionary mit Zell-Koordinaten als Schlüssel und 1/0 für lebend/tot.
    - offset_x, offset_y: Verschiebung des sichtbaren Bereichs (Scrolling).
    """
    # Gitterlinien
    for x in range(-offset_x % cell_size, width, cell_size):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, height))
    for y in range(-offset_y % cell_size, height, cell_size):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (width, y))
    # Zellen
    for (gx, gy), alive in grid.items():
        if alive:
            sx = gx * cell_size - offset_x
            sy = gy * cell_size - offset_y
            if 0 <= sx < width and 0 <= sy < height:
                pygame.draw.rect(screen, (255, 255, 255), (sx, sy, cell_size, cell_size))
                pygame.draw.rect(screen, (40, 40, 40), (sx, sy, cell_size, cell_size), 1)

def draw_status(screen, running, width, speed):
    """
    Zeigt den Simulationsstatus und die Geschwindigkeit an.

    Parameter:
    - screen: Das pygame-Fenster.
    - running: Bool, ob die Simulation läuft.
    - width: Fensterbreite (für Positionierung).
    - speed: Simulationsgeschwindigkeit in Millisekunden.
    """
    font = pygame.font.SysFont(None, 36)
    status = "Running" if running else "Paused"
    color = (0, 255, 0) if running else (255, 0, 0)
    text_status = font.render(status, True, color)
    text_speed = font.render(f"Speed: {speed}ms", True, (255, 255, 255))
    screen.blit(text_status, (width - text_status.get_width() - 10, 10))
    screen.blit(text_speed, (width - text_speed.get_width() - 10, 50))

def draw_help_icon(screen):
    """
    Zeichnet ein Fragezeichen-Icon oben links.

    Parameter:
    - screen: Das pygame-Fenster.
    """
    font = pygame.font.SysFont(None, 28)
    text = font.render("?", True, (200, 200, 200))
    text_rect = text.get_rect(center=(30, 30))
    pygame.draw.circle(screen, (50, 50, 50), (30, 30), 20)
    screen.blit(text, text_rect)

def draw_instructions(screen, width, height):
    """
    Zeigt ein Overlay mit Steuerungsanweisungen.

    Parameter:
    - screen: Das pygame-Fenster.
    - width, height: Fenstergröße (für zentrierte Anzeige).
    """
    font = pygame.font.SysFont("Arial", 24)
    lines = [
        "Steuerung:",
        "W/A/S/D: Bewegen auf dem Feld",
        "\u2191/\u2193: Vergroessern/Verkleinern",
        "\u2190/\u2192: Geschwindigkeit anpassen",
        "SPACE: Start/Pause",
        "N: Gitter leeren",
        "Linksklick: Zelle setzen/entfernen",
    ]
    box_w, box_h = 500, 250
    box_x, box_y = (width - box_w) // 2, (height - box_h) // 2
    overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay.fill((50, 50, 50, 200))
    screen.blit(overlay, (box_x, box_y))
    pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_w, box_h), 2, border_radius=15)
    for i, line in enumerate(lines):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (box_x + 20, box_y + 20 + i * 30))

# =========================
#        SPIELLOGIK
# =========================

def update_logic(grid):
    """
    Berechnet den nächsten Zustand des Spielfelds.

    Parameter:
    - grid: Dictionary mit Zell-Koordinaten als Schlüssel und 1/0 für lebend/tot.

    Rückgabe:
    - new_grid: Neues Dictionary mit aktualisiertem Zustand.
    """
    from collections import defaultdict
    neighbor_offsets = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    neighbor_counts = defaultdict(int)
    # Nachbarn zählen
    for (x, y), alive in grid.items():
        if alive:
            for dx, dy in neighbor_offsets:
                neighbor_counts[(x+dx, y+dy)] += 1
    new_grid = {}
    for cell, count in neighbor_counts.items():
        if grid.get(cell, 0):
            if count in (2, 3):
                new_grid[cell] = 1
        else:
            if count == 3:
                new_grid[cell] = 1
    return new_grid

# =========================
#        HAUPTPROGRAMM
# =========================

def main():
    """
    Hauptfunktion: Initialisiert Fenster, Variablen und startet die Hauptschleife.
    Steuert Eingaben, Spiellogik und Darstellung.
    """
    # Initialisierung
    pygame.init()
    pygame.display.set_caption("Conway's Game of Life")
    screen = pygame.display.set_mode((1200, 720))
    clock = pygame.time.Clock()
    width, height = 1200, 720

    # Spielfeld-Parameter
    cell_size = 20
    min_cell_size, max_cell_size = 5, 60
    offset_x, offset_y = 0, 0
    move_speed = 20

    # Simulations-Parameter
    logic_running = False
    logic_speed = 250  # in ms
    min_speed, max_speed = 50, 2000  # 50ms ist jetzt das Minimum!
    last_update_time = pygame.time.get_ticks()

    # Sonstiges
    grid = {}
    show_instructions = False
    mouse_down = False
    draw_mode = None  # <--- NEU: Merkt sich, ob wir setzen oder entfernen
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Spielfeld verschieben
        if keys[pygame.K_w]:
            offset_y = max(offset_y - move_speed, 0)
        if keys[pygame.K_s]:
            offset_y += move_speed
        if keys[pygame.K_a]:
            offset_x = max(offset_x - move_speed, 0)
        if keys[pygame.K_d]:
            offset_x += move_speed

        # Zoom
        if keys[pygame.K_UP]:
            old = cell_size
            cell_size = min(cell_size + 1, max_cell_size)
            if cell_size != old:
                mx, my = pygame.mouse.get_pos()
                scale = cell_size / old
                offset_x = int(mx + (offset_x - mx) * scale)
                offset_y = int(my + (offset_y - my) * scale)
        if keys[pygame.K_DOWN]:
            old = cell_size
            cell_size = max(cell_size - 1, min_cell_size)
            if cell_size != old:
                mx, my = pygame.mouse.get_pos()
                scale = cell_size / old
                offset_x = int(mx + (offset_x - mx) * scale)
                offset_y = int(my + (offset_y - my) * scale)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    logic_running = not logic_running
                elif event.key == pygame.K_RIGHT:
                    logic_speed = max(min_speed, logic_speed - 50)  # Schneller, aber nicht unter 50ms
                elif event.key == pygame.K_LEFT:
                    logic_speed = min(max_speed, logic_speed + 50)  # Langsamer, max 2000ms
                elif event.key == pygame.K_n:
                    grid = {}

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    mx, my = pygame.mouse.get_pos()
                    # Hilfe-Icon
                    if 10 <= mx <= 50 and 10 <= my <= 50:
                        show_instructions = not show_instructions
                    else:
                        gx = (mx + offset_x) // cell_size
                        gy = (my + offset_y) // cell_size
                        current = grid.get((gx, gy), 0)
                        grid[(gx, gy)] = 1 - current
                        draw_mode = 0 if current else 1  # <--- Merke, was gemacht wurde

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
                    draw_mode = None  # <--- Reset

        # Zellen setzen oder entfernen beim Ziehen
        if mouse_down and draw_mode is not None:
            mx, my = pygame.mouse.get_pos()
            gx = (mx + offset_x) // cell_size
            gy = (my + offset_y) // cell_size
            grid[(gx, gy)] = draw_mode

        # Begrenzung der Geschwindigkeit auf mindestens 50ms
        if logic_speed < min_speed:
            logic_speed = min_speed

        # Spiellogik aktualisieren
        if logic_running and current_time - last_update_time >= logic_speed:
            grid = update_logic(grid)
            last_update_time = current_time

        # Zeichnen
        clock.tick(30)
        screen.fill((0, 0, 0))
        draw_grid(screen, cell_size, width, height, grid, offset_x, offset_y)
        draw_status(screen, logic_running, width, logic_speed)
        draw_help_icon(screen)
        if show_instructions:
            draw_instructions(screen, width, height)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()