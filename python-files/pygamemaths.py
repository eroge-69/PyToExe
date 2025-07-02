import sys
from random import randint
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Have fun!")

test_font = pygame.font.SysFont("None", 50)
clock = pygame.time.Clock()


def new_question():
    a = randint(1, 12)
    b = randint(1, 12)
    return a, b, a * b


number_1, number_2, correct_answer = new_question()
user_input = ''
feedback = ''
feedback_color = (255, 255, 255)

input_rect = pygame.Rect(0, 0, 800, 400)
input_color = pygame.Color('white')

while True:
    screen.fill((0, 0, 0))  # Backup fill (just in case)

    # Fullscreen indigo box
    pygame.draw.rect(screen, (75, 0, 130), input_rect)
    pygame.draw.rect(screen, input_color, input_rect, 4)

    # Render question
    question_surface = test_font.render(f"What is {number_1} × {number_2}?", True, (255, 255, 255))
    screen.blit(question_surface, (20, 20))

    # Render input text
    input_surface = test_font.render(user_input, True, (255, 255, 255))
    screen.blit(input_surface, (20, 100))

    # Render feedback
    if feedback:
        feedback_surface = test_font.render(feedback, True, feedback_color)
        screen.blit(feedback_surface, (20, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    if int(user_input) == correct_answer:
                        feedback = "Correct!"
                        feedback_color = (0, 255, 0)
                    else:
                        feedback = f"Nope, it was {correct_answer}"
                        feedback_color = (255, 0, 0)
                except ValueError:
                    feedback = "Numbers only!"
                    feedback_color = (255, 255, 0)

                # Load new question
                number_1, number_2, correct_answer = new_question()
                user_input = ''
            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                user_input += event.unicode

    pygame.display.update()
    clock.tick(60)