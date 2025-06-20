import pygame
import datetime

pygame.init()

width, height = 600, 300
screen = pygame.display.set_mode((width, height))

pink = (255, 230, 240)
dark_purple = (209, 29, 83)

font = pygame.font.SysFont("Arial", 34)

running = True
clock = pygame.time.Clock()

def get_time_until_sept2():
    today = datetime.datetime.now()
    target = datetime.datetime(today.year, 9, 2)
    if today > target:
        target = datetime.datetime(today.year + 1, 9, 2)
    return target - today

while running:
    screen.fill(pink)

    diff = get_time_until_sept2()

    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    title_text = font.render("till we see eachother", True, dark_purple)
    countdown_text = font.render(
        f"{days} days, {hours:02}h {minutes:02}m {seconds:02}s", True, dark_purple
    )

    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 80))
    screen.blit(countdown_text, (width // 2 - countdown_text.get_width() // 2, 140))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(1)  

pygame.quit()
