import pygame
import math

# Inicializa o pygame
pygame.init()

# Configurações da janela (aumentei largura e altura)
WIDTH, HEIGHT = 600, 700
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tempo de Queda Livre")

# Cores
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (200, 50, 50)
GRAY = (180, 180, 180)

# Objeto (círculo)
radius = 25
x = WIDTH // 2
y = 150
dragging = False

# Constante da gravidade
g = 9.8  # m/s²
scale = 1  # 1 pixel = 1 metro (simplificação)

font = pygame.font.SysFont(None, 32)

# Controle de simulação
simulando = False
t_inicio = 0
altura_inicial = 0

running = True
clock = pygame.time.Clock()

# Função para desenhar botão
def draw_button(surface, rect, text, active=True):
    color = RED if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=8)
    txt = font.render(text, True, WHITE)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)

# Retângulo do botão
button_rect = pygame.Rect(WIDTH//2 - 70, HEIGHT - 50, 140, 35)

while running:
    dt = clock.tick(60) / 1000  # segundos por frame
    window.fill(WHITE)

    # Linha do "chão"
    pygame.draw.line(window, GREEN, (0, HEIGHT - 80), (WIDTH, HEIGHT - 80), 6)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Se clicar dentro do círculo, começa arrastar (somente se não estiver simulando)
            if not simulando and (mx - x) ** 2 + (my - y) ** 2 <= radius ** 2:
                dragging = True
            # Clique no botão
            elif button_rect.collidepoint(mx, my) and not simulando:
                simulando = True
                t_inicio = pygame.time.get_ticks() / 1000  # tempo em segundos
                altura_inicial = HEIGHT - 80 - y - radius

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging and not simulando:
            # Atualiza posição do círculo apenas no eixo Y
            _, my = pygame.mouse.get_pos()
            if my < HEIGHT - 80 - radius:
                y = my

    # Durante simulação
    tempo_decorrido = 0
    velocidade_instantanea = 0
    if simulando:
        tempo_decorrido = pygame.time.get_ticks() / 1000 - t_inicio
        # Fórmula do movimento uniformemente acelerado: s = 0.5*g*t²
        deslocamento = 0.5 * g * tempo_decorrido ** 2
        y = (HEIGHT - 80 - radius) - (altura_inicial - deslocamento)

        # Velocidade instantânea: v = g * t
        velocidade_instantanea = g * tempo_decorrido

        # Se tocar no chão, para
        if y >= HEIGHT - 80 - radius:
            y = HEIGHT - 80 - radius
            simulando = False

    # Desenha o círculo
    pygame.draw.circle(window, BLUE, (x, int(y)), radius)

    # Calcula altura até o chão
    altura_metros = (HEIGHT - 80 - y - radius) * scale

    # Exibição de dados físicos (sempre mostra tudo)
    if altura_metros > 0:
        if simulando:
            tempo = tempo_decorrido
            v_atual = velocidade_instantanea
        else:
            tempo = math.sqrt(2 * altura_metros / g)
            v_atual = math.sqrt(2 * g * altura_metros)
        texto = font.render(f"Altura: {altura_metros:.1f} m | Tempo: {tempo:.2f} s | Velocidade: {v_atual:.2f} m/s", True, BLACK)
    else:
        texto = font.render("Altura: 0 m | Tempo: 0 s | Velocidade: 0 m/s", True, BLACK)

    window.blit(texto, (20, 20))

    # Desenha o botão
    draw_button(window, button_rect, "Simular", not simulando)

    pygame.display.flip()

pygame.quit()
