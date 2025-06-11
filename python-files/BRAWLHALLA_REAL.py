import pygame
import random
import sys

# Inicializar pygame
pygame.init()

# Definir colores
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 0, 255)

# Configurar pantalla
ANCHO = 800
ALTO = 600
TAMAÑO_CELDA = 20

# Configurar ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Snake Game')
reloj = pygame.time.Clock()

# Configurar fuente
fuente = pygame.font.Font(None, 36)

class Snake:
    def __init__(self):  # <-- corregido
        self.longitud = 1
        self.posiciones = [((ANCHO // 2), (ALTO // 2))]
        self.direccion = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.color = VERDE
        self.puntos = 0
        
    def obtener_cabeza(self):
        return self.posiciones[0]
    
    def girar(self, punto):
        if self.longitud > 1 and (punto[0] * -1, punto[1] * -1) == self.direccion:
            return
        else:
            self.direccion = punto
    
    def mover(self):
        cur = self.obtener_cabeza()
        x, y = self.direccion
        nueva = (((cur[0] + (x * TAMAÑO_CELDA)) % ANCHO), (cur[1] + (y * TAMAÑO_CELDA)) % ALTO)
        if len(self.posiciones) > 2 and nueva in self.posiciones[2:]:
            self.reiniciar()
        else:
            self.posiciones.insert(0, nueva)
            if len(self.posiciones) > self.longitud:
                self.posiciones.pop()
    
    def reiniciar(self):
        self.longitud = 1
        self.posiciones = [((ANCHO // 2), (ALTO // 2))]
        self.direccion = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.puntos = 0
    
    def dibujar(self, superficie):
        for p in self.posiciones:
            r = pygame.Rect((p[0], p[1]), (TAMAÑO_CELDA, TAMAÑO_CELDA))
            pygame.draw.rect(superficie, self.color, r)
            pygame.draw.rect(superficie, BLANCO, r, 1)
    
    def manejar_teclas(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    self.girar((0, -1))
                elif evento.key == pygame.K_DOWN:
                    self.girar((0, 1))
                elif evento.key == pygame.K_LEFT:
                    self.girar((-1, 0))
                elif evento.key == pygame.K_RIGHT:
                    self.girar((1, 0))

class Comida:
    def __init__(self):  # <-- corregido
        self.posicion = (0, 0)
        self.color = ROJO
        self.randomizar_posicion()
    
    def randomizar_posicion(self):
        self.posicion = (random.randint(0, (ANCHO // TAMAÑO_CELDA) - 1) * TAMAÑO_CELDA,
                        random.randint(0, (ALTO // TAMAÑO_CELDA) - 1) * TAMAÑO_CELDA)
    
    def dibujar(self, superficie):
        r = pygame.Rect((self.posicion[0], self.posicion[1]), (TAMAÑO_CELDA, TAMAÑO_CELDA))
        pygame.draw.rect(superficie, self.color, r)
        pygame.draw.rect(superficie, BLANCO, r, 1)

def mostrar_puntuacion(superficie, puntos):
    texto = fuente.render(f"Puntos: {puntos}", True, BLANCO)
    superficie.blit(texto, (10, 10))

def main():
    snake = Snake()
    comida = Comida()
    
    # Mapeo de direcciones
    direcciones = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0)
    }
    
    # Establecer dirección inicial
    snake.direccion = direcciones[snake.direccion]
    
    while True:
        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key in direcciones:
                    snake.girar(direcciones[evento.key])
        
        # Mover snake
        snake.mover()
        
        # Verificar si comió
        if snake.obtener_cabeza() == comida.posicion:
            snake.longitud += 1
            snake.puntos += 10
            comida.randomizar_posicion()
            
            # Evitar que la comida aparezca en el cuerpo de la serpiente
            while comida.posicion in snake.posiciones:
                comida.randomizar_posicion()
        
        # Dibujar todo
        pantalla.fill(NEGRO)
        snake.dibujar(pantalla)
        comida.dibujar(pantalla)
        mostrar_puntuacion(pantalla, snake.puntos)
        
        pygame.display.update()
        reloj.tick(10)  # Velocidad del juego

if __name__ == '__main__':
    main()