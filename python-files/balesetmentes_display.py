
import pygame
import sys
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

# Ask user for last accident date
root = tk.Tk()
root.withdraw()
user_input = simpledialog.askstring("Utolsó baleset", "Add meg az utolsó baleset dátumát (ÉÉÉÉ-HH-NN):")
if not user_input:
    sys.exit()

try:
    last_accident_date = datetime.strptime(user_input, "%Y-%m-%d")
except ValueError:
    sys.exit("Hibás dátumformátum.")

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Balesetmentes napok száma")
font_large = pygame.font.SysFont("arial", 120)
font_medium = pygame.font.SysFont("arial", 60)
font_small = pygame.font.SysFont("arial", 40)
white = (255, 255, 255)
black = (0, 0, 0)

running = True
while running:
    screen.fill(black)

    now = datetime.now()
    delta = now - last_accident_date
    total_days = delta.days
    total_minutes = delta.total_seconds() // 60
    total_hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)

    title_hu = font_large.render("Balesetmentes napok száma", True, white)
    title_en = font_large.render("Accident free days", True, white)
    count_text = font_medium.render(f"{total_days} nap / {total_hours} óra {minutes} perc", True, white)
    date_text = font_small.render(f"Mai dátum: {now.strftime('%Y-%m-%d %H:%M')}", True, white)

    screen.blit(title_hu, (screen.get_width() // 2 - title_hu.get_width() // 2, 100))
    screen.blit(title_en, (screen.get_width() // 2 - title_en.get_width() // 2, 230))
    screen.blit(count_text, (screen.get_width() // 2 - count_text.get_width() // 2, 400))
    screen.blit(date_text, (screen.get_width() // 2 - date_text.get_width() // 2, 500))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

pygame.quit()
