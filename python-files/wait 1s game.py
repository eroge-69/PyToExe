import pygame
pygame.init()
screen = pygame.display.set_mode((1028, 512))
clock = pygame.time.Clock()

counter, text = 1, '1'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.USEREVENT:
            counter -= 0.0001
            text = str(counter).rjust(3) if counter > 0 else 'hell nah is just 1s'
        if e.type == pygame.QUIT:
            run = False

    screen.fill((255, 255, 255))
    screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
    pygame.display.flip()
    clock.tick(60)
