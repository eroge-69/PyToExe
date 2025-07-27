import pygame, sys
import Obstacle
from Player import player
from Alien import alien

# Global constants (must be defined before use)
WIDTH = 800
HEIGHT = 600

class game:
    def __init__(self):
        playerSprite = player((WIDTH / 2, HEIGHT - 30), WIDTH, 5)
        self.player = pygame.sprite.GroupSingle(playerSprite)

        self.shape = Obstacle.shape
        self.blockSize = 6
        self.blocks = pygame.sprite.Group()
        self.obstacleAmount = 4
        self.obstacleXPos = [num * (WIDTH / self.obstacleAmount) for num in range(self.obstacleAmount)]
        self.createMultipleObstacles(WIDTH / 15, 480, *self.obstacleXPos)
        self.aliens = pygame.sprite.Group()
        self.alienSetup(rows=6, cols=8)


    def createObstacle(self, xStart, yStart, offsetX):
        for rowIndex, row in enumerate(self.shape):
            for colIndex, col in enumerate(row):
                if col == 'x':
                    x = xStart + colIndex * self.blockSize + offsetX
                    y = yStart + rowIndex * self.blockSize
                    block = Obstacle.Block(self.blockSize, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def createMultipleObstacles(self, xStart, yStart, *offset):
        for x in offset:
            self.createObstacle(xStart, yStart, x)

    def alienSetup(self, rows, cols, xDistance=60, yDistance=48, xOffset=70, yOffset=100):
      for rowIndex, row in enumerate(range(rows)):
        for colIndex, col in enumerate(range(cols)):
            x = colIndex * xDistance + xOffset
            y = rowIndex * yDistance + yOffset

            if rowIndex == 0:
              alienSprite = alien("red", x, y)
            elif 1 <= rowIndex <= 2:
              alienSprite = alien("green", x, y)
            else:
              alienSprite = alien("yellow", x, y)
              
            self.aliens.add(alienSprite)

    def run(self, screen):
        self.player.update()
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)

# Main game loop
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PyInvaders")
    clock = pygame.time.Clock()

    g = game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((30, 30, 30))
        g.run(screen)
        pygame.display.flip()
        clock.tick(60)
