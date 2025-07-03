
import pygame
import sys
import random
import time

pygame.init()

# Configuración
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Battle: ¡Suma, Resta y Multiplica!")
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 30, bold=True)
clock = pygame.time.Clock()

WHITE, BLACK, RED, GREEN, BLUE, GRAY = (255,255,255), (0,0,0), (255,0,0), (0,255,0), (50,150,255), (200,200,200)

# Funciones básicas
def draw_text(text, font, color, surface, x, y):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        textobj = font.render(line, True, color)
        surface.blit(textobj, (x, y + i * 30))

def generate_matrix():
    return [[random.randint(0, 9) for _ in range(2)] for _ in range(2)]

def add_matrices(a, b):
    return [[a[i][j] + b[i][j] for j in range(2)] for i in range(2)]

def subtract_matrices(a, b):
    return [[a[i][j] - b[i][j] for j in range(2)] for i in range(2)]

def multiply_matrices(a, b):
    return [
        [a[0][0]*b[0][0] + a[0][1]*b[1][0], a[0][0]*b[0][1] + a[0][1]*b[1][1]],
        [a[1][0]*b[0][0] + a[1][1]*b[1][0], a[1][0]*b[0][1] + a[1][1]*b[1][1]]
    ]

def matrix_to_string(matrix):
    return f"[{matrix[0][0]} {matrix[0][1]}]\n[{matrix[1][0]} {matrix[1][1]}]"

def game_loop(operation):
    start_time = time.time()
    score = 0
    attempts = 0
    while time.time() - start_time < 300:  # 5 minutos
        A, B = generate_matrix(), generate_matrix()
        correct = operations[operation](A, B)

        user_input = [[None, None], [None, None]]
        input_index = [0, 0]
        input_text = ""

        running = True
        while running:
            screen.fill(WHITE)
            draw_text(f"Operación: {operation}", font, BLACK, screen, 30, 30)
            draw_text(f"A =\n{matrix_to_string(A)}", font, BLUE, screen, 30, 100)
            draw_text(f"B =\n{matrix_to_string(B)}", font, GREEN, screen, 300, 100)
            draw_text("Escribe el valor en la posición [" + str(input_index[0]) + "][" + str(input_index[1]) + "]:", font, BLACK, screen, 30, 300)
            draw_text("Entrada: " + input_text, font, BLACK, screen, 30, 340)
            draw_text(f"Puntaje: {score}", font, BLACK, screen, 650, 30)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            val = int(input_text)
                            user_input[input_index[0]][input_index[1]] = val
                            input_text = ""
                            if input_index == [1, 1]:
                                running = False
                            else:
                                if input_index[1] == 1:
                                    input_index[0] += 1
                                    input_index[1] = 0
                                else:
                                    input_index[1] += 1
                        except:
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            clock.tick(30)

        correct_count = sum(user_input[i][j] == correct[i][j] for i in range(2) for j in range(2))
        if correct_count == 4:
            score += 10
        else:
            score -= 5
        attempts += 1

    show_final_screen(score, attempts)

def show_final_screen(score, attempts):
    screen.fill(WHITE)
    draw_text("¡Tiempo terminado!", title_font, RED, screen, 250, 200)
    draw_text(f"Puntaje final: {score}", font, BLACK, screen, 300, 260)
    draw_text(f"Preguntas respondidas: {attempts}", font, BLACK, screen, 300, 300)
    draw_text("Presiona cualquier tecla para volver al menú.", font, GRAY, screen, 200, 360)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

operations = {"Suma": add_matrices, "Resta": subtract_matrices, "Multiplicación": multiply_matrices}

def show_intro():
    screen.fill(WHITE)
    draw_text("Matrix Battle: ¡Suma, Resta y Multiplica!", title_font, BLACK, screen, 130, 30)
    draw_text("Objetivos Procedimentales:\n- Resolver suma, resta y multiplicación de matrices 2x2.\n- Aplicar reglas de álgebra matricial.\n- Desarrollar agilidad mental.\n", font, BLACK, screen, 60, 100)
    draw_text("Reglas:\n- Selecciona una operación.\n- Ingresa los valores de la matriz resultado.\n- 10 puntos por acierto, -5 por error.\n- Tienes 5 minutos.", font, BLACK, screen, 60, 300)
    draw_text("Presiona S para Suma, R para Resta, M para Multiplicación o ESC para salir.", font, RED, screen, 60, 500)
    pygame.display.flip()

def main_menu():
    while True:
        show_intro()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    game_loop("Suma")
                elif event.key == pygame.K_r:
                    game_loop("Resta")
                elif event.key == pygame.K_m:
                    game_loop("Multiplicación")
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

main_menu()
