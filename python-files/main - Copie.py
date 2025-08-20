import pygame
from game import Game
from musique import Musique


if __name__ == '__main__':
    pygame.init()
    game = Game()
    musique = Musique()
    game.run()