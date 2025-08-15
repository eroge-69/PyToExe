
import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# Constantes
ANCHO, ALTO = 800, 600
FPS = 60
TIEMPO_SPAWN = 2000  # ms
TIEMPO_COMIDA = 3000  # ms

# Colores
NEGRO = (0, 0, 0)
GRIS = (50, 50, 50)
VERDE = (0, 255, 0)

# Inicializar pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulador de Colmena")
clock = pygame.time.Clock()

# Entidades
class Reina:
    def __init__(self):
        self.x = ANCHO // 2
        self.y = ALTO // 2
        self.radio = 40

    def crecer(self, cantidad):
        self.radio += cantidad

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, NEGRO, (self.x, self.y), self.radio)

class Bolita:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = 10
        self.vel_x = random.choice([-2, 2])
        self.vel_y = random.choice([-2, 2])
        self.tiene_comida = False
        self.objetivo = None

    def mover(self):
        if self.tiene_comida and self.objetivo:
            dx = self.objetivo[0] - self.x
            dy = self.objetivo[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                self.x += dx / dist * 2
                self.y += dy / dist * 2
        else:
            self.x += self.vel_x
            self.y += self.vel_y
            if self.x - self.radio < 0 or self.x + self.radio > ANCHO:
                self.vel_x *= -1
            if self.y - self.radio < 0 or self.y + self.radio > ALTO:
                self.vel_y *= -1

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, GRIS, (int(self.x), int(self.y)), self.radio)

class Comida:
    def __init__(self):
        self.x = random.randint(20, ANCHO - 20)
        self.y = random.randint(20, ALTO - 20)
        self.radio = 6
        self.recogida = False

    def dibujar(self, pantalla):
        if not self.recogida:
            pygame.draw.circle(pantalla, VERDE, (self.x, self.y), self.radio)

# Inicialización
reina = Reina()
bolitas = []
comidas = []

# Timers
pygame.time.set_timer(pygame.USEREVENT + 1, TIEMPO_SPAWN)  # Spawn bolitas
pygame.time.set_timer(pygame.USEREVENT + 2, TIEMPO_COMIDA)  # Spawn comida

# Bucle principal
ejecutando = True
while ejecutando:
    clock.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.USEREVENT + 1:
            bolitas.append(Bolita(reina.x, reina.y))
        elif evento.type == pygame.USEREVENT + 2:
            comidas.append(Comida())

    pantalla.fill((200, 200, 200))

    # Mover y dibujar bolitas
    for bolita in bolitas:
        bolita.mover()
        bolita.dibujar(pantalla)

    # Dibujar y comprobar comida
    for comida in comidas:
        if comida.recogida:
            continue
        comida.dibujar(pantalla)
        for bolita in bolitas:
            dx = bolita.x - comida.x
            dy = bolita.y - comida.y
            distancia = math.hypot(dx, dy)
            if distancia < bolita.radio + comida.radio:
                comida.recogida = True
                bolita.tiene_comida = True
                bolita.objetivo = (reina.x, reina.y)

    # Comprobar si alguna bolita entrega comida
    for bolita in bolitas:
        if bolita.tiene_comida:
            dx = bolita.x - reina.x
            dy = bolita.y - reina.y
            if math.hypot(dx, dy) < reina.radio:
                reina.crecer(1)
                bolita.tiene_comida = False
                bolita.objetivo = None

    reina.dibujar(pantalla)
    pygame.display.flip()

pygame.quit()
