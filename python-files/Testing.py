# from tkinter import *
# from PIL import ImageTk, Image
# import os

# root = Tk()
# img = ImageTk.PhotoImage(Image.open("game/images/bg Birds.png"))
# panel = Label(root, image = img)
# panel.pack(side = "bottom", fill = "both", expand = "yes")
# root.mainloop()

# import pygame
# from pygame.locals import*
# img = pygame.image.load('game/images/bg Birds.png')

# white = (255, 64, 64)
# w = 640
# h = 480
# screen = pygame.display.set_mode((w, h))
# screen.fill((white))
# running = 1

# while running:
#     screen.fill((white))
#     screen.blit(img,(0,0))
#     pygame.display.flip()

import tkinter as tk
root = tk.Tk()
root.mainloop()
window = tk.Tk()
window.title('Hello Python')
window.geometry("500x800+10+20")
window.mainloop()