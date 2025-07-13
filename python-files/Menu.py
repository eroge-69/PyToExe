import os
from pygame import KEYDOWN
import pygame

from Animatronic import AnimatronicAI
from CAMERASYS import CAMERA
from Drawer import drawer
from Scrappy import ScrappyAi
from office import officec


class MenuClass:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.MENUANDDRAWER = True
        self.Level = 0
        self.w = True
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.SIZE = (self.width,self.height)
        print(self.SIZE)
        self.Indeks = 0
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.background = pygame.image.load("image/office/0001.png")
        self.Sounds = [pygame.mixer.Sound("Sounds/environment.mp3"),pygame.mixer.Sound("Sounds/CameraSwitch.wav")]
        self.BackGround = pygame.mixer.Sound("Sounds/storm.wav").play(-1)
        self.Menu =[
            [pygame.transform.scale(pygame.image.load("Menu/MenuButton/1.png"),(self.width,self.height)),
            pygame.transform.scale(pygame.image.load("Menu/MenuButton/2.png"),(self.width,self.height)),
            pygame.transform.scale(pygame.image.load("Menu/MenuButton/3.png"),(self.width,self.height))],
            [pygame.transform.scale(pygame.image.load("Menu/Guide/Guide.png"),(self.width,self.height))]]
        self.Etap = 0

    def NewPlay(self):
        with open("Save.txt","w")as w:
            w.write("0")
        self.Level = 0
        self.w = False

    def Continue(self):
        if os.path.isfile("Save.txt"):
            with open("Save.txt", "r") as s:
                self.Level = s.read()
                self.w = False

        else:
            with open("Save.txt","w") as w:
                w.write("0")
                self.Level = 0
                self.w = False

    def MENU(self):
        while self.w:
            self.menuImages()
            self.Controll()
            pygame.display.flip()

    def menuImages(self):
        self.screen.blit(self.background,(0,0))
        self.screen.blit(self.Menu[self.Etap][self.Indeks],(0,0))

    def Controll(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.MENUANDDRAWER = False
            if event.type == KEYDOWN:
                key = event.key
                if key == pygame.K_w and self.Etap == 0:
                    self.Indeks -= 1
                    self.Sounds[1].play()
                    print(self.Indeks)
                    if self.Indeks == -1:
                        self.Indeks = 2
                if key == pygame.K_s and self.Etap == 0:
                    self.Indeks += 1
                    self.Sounds[1].play()
                    print(self.Indeks)
                    if self.Indeks >= 3:
                        self.Indeks = 0
                if key == pygame.K_SPACE:
                    self.Indeks = 0
                    self.Etap = (self.Etap + 1) % len(self.Menu)
                if key == pygame.K_e:
                    if self.Indeks == 0:
                        print("Play")
                        self.NewPlay()
                    elif self.Indeks == 1:
                        print("Continue")
                        self.Continue()
                    elif self.Indeks == 2:
                        print("Exit")
                        self.w = False
                        self.MENUANDDRAWER = False
                    self.BackGround.stop()
class GameEyes:
    def __init__(self,MenuClass):
        self.MenuClass = MenuClass
        self.Scrappy = ScrappyAi(self.MenuClass.SIZE,self.MenuClass.Level)
        self.Scrappy.load_assets()
        self.animatronic= AnimatronicAI(self.MenuClass.SIZE)
        self.C = CAMERA(0,0,0,self.MenuClass.SIZE)
        self.OFFICE = officec(self.MenuClass.SIZE)
class Game:
    def __init__(self):

        self.MenuClass = MenuClass()
        self.GameEyes = GameEyes(self.MenuClass)
        while self.MenuClass.MENUANDDRAWER:
            if self.MenuClass.w:
                self.MenuClass.MENU()
            else:
                self.Drawer = drawer(self.MenuClass.SIZE,self.MenuClass.Level,self,self.MenuClass)
                self.Drawer.anim()

M = Game()
while M.GameEyes.C.LoaderWork < 10:
    print("Not lOADED")
M.MenuClass.MENU()


