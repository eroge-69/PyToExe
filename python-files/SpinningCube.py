import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Vertices of the cube
vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

# Edges connecting the vertices
edges = (
    (0,1),
    (1,2),
    (2,3),
    (3,0),
    (4,5),
    (5,7),
    (7,6),
    (6,4),
    (0,4),
    (1,5),
    (2,7),
    (3,6)
)

def draw_cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption("Spinning Cube")

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)

    clock = pygame.time.Clock()
    rotation = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glRotatef(1, 3, 1, 1)  # Rotate cube a little every frame
        draw_cube()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
