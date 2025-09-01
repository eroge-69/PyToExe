import pygame
import numpy 

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("floor_test")
    pygame.display.set_icon(pygame.image.load("icon.png"))
    clock = pygame.time.Clock()
    running = True

    hres = 400
    halfvres = 300

    mod = hres/60
    posx, posy, rot = 0, 0, 0
    frame = numpy.random.uniform(0, 1, (hres, halfvres*2, 3)).astype(numpy.uint8)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        for i in range(hres):
            rot_i = rot + numpy.deg2rad(i/mod - 30)
            sin, cos = numpy.sin(rot_i), numpy.cos(rot_i)
            
            for j in range(halfvres):
                n = halfvres/(halfvres - j)
                x, y = posx + cos*n, posy + sin*n

                if int(x) %2 == int(y) %2:
                    frame[i] [halfvres*2-j-1] = [0, 0, 0]
                else:
                    frame[i] [halfvres*2-j-1] = [1, 1, 1]

        surf = pygame.surfarray.make_surface(frame*255)
        surf = pygame.transform.scale(surf, (400, 300))

        screen.blit(surf, (0, 0))
        pygame.display.update()

        posx, posy, rot = movement(posx, posy, rot, pygame.key.get_pressed())

def movement(posx, posy, rot, keys):
    if keys[pygame.K_LEFT] or keys[ord('a')]:
        rot = rot - 0.1
    if keys[pygame.K_RIGHT] or keys[ord('d')]:
        rot = rot + 0.1
    if keys[pygame.K_UP] or keys[ord('w')]:
        posx, posy = posx + numpy.cos(rot)*0.5, posy + numpy.sin(rot)*0.5
    if keys[pygame.K_DOWN] or keys[ord('s')]:
        posx, posy = posx - numpy.cos(rot)*0.5, posy - numpy.sin(rot)*0.5
    return posx, posy, rot
if __name__ == "__main__":
    main()
    pygame.quit()
            
