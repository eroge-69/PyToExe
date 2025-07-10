# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN
# DO NOT RUN




















import pygame, pygame_gui, os, ctypes

print(os.path.exists(f"C:\\Users\\{os.getlogin()}\\Desktop\\scary.png"))
cmd = '''powershell -Command "Start-Process "taskkill" -ArgumentList '/FI "WINDOWTITLE eq Untitled - Notepad" /T /F'"'''
cmd2 = '''powershell -Command "shutdown /l"'''

downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
count = 0

print("Hello World!")
pygame.time.wait(2000)
print(f"Is \"{os.getlogin()}\" familiar to you?")
pygame.time.wait(2000)
print('But it should be: dead')
pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(f'{os.getlogin()}.exe')
pygame.display.set_icon(pygame.transform.scale(pygame.image.load("scary.png").convert(), (50, 50)))
screen.fill((0, 0, 0))
center_rect = pygame.Rect((250, 250), (300, 100))
pygame.draw.rect(screen, (0, 0, 0), center_rect)

manager = pygame_gui.UIManager((screen_width, screen_height))
text = pygame_gui.elements.UITextBox(
    html_text='I SEE YOU',
    relative_rect=center_rect,
    manager=manager
)

clock = pygame.time.Clock()
is_running = True

while is_running:
    try:
        time_delta = clock.tick(60)/1000.0
    except KeyboardInterrupt:
        count += 1
        if count == 10:
            with open(os.path.join(downloads_path, "EXE.txt"), "w") as file:
                file.write("YOUR FREE TRIAL OF LIVING HAS ENDED.")
            ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred.", "System Alert", 0x10)
            ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred.", "System Alert", 0x10)
            ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred.", "System Alert", 0x10)
            os.startfile(os.path.join(downloads_path, "EXE.txt"))
            ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred. Check Notepad.", "System Alert", 0x10)
            pygame.time.wait(5000)
            os.system(cmd)
            os.startfile(os.path.join(downloads_path, "EXE.txt"))
            with open(os.path.join(downloads_path, "EXE.txt"), "w") as file:
                file.write("WHY ARE YOU HERE?")
            pygame.time.wait(3000)
            os.system(cmd)
            os.startfile(os.path.join(downloads_path, "EXE.txt"))
            with open(os.path.join(downloads_path, "EXE.txt"), "w") as file:
                file.write("YOU ARE NOT SUPPOESED TO BE HERE.")
            pygame.time.wait(5000)
            with open(os.path.join(downloads_path, f"WELCOME_BACK_{os.getlogin().upper()}.txt"), "w") as file:
                file.write(f"HEY {os.getlogin().upper()}")
            os.system(cmd2)
        pygame.display.set_caption('N̸̛̛̙̙̹͉̯͖̯̜̗̓̀͋̽͗̈́̉̂͑̎̆͋̈́̓̋̀͘͜Ǫ̶̨̧̖̦̞̖͇͍̤̪̱̤͎͕͉̹̹̤̱̬̗̰̐̀͌̓̓̿̾̉̄̈́̂̆͝ ̶̩̪̲͔̼̫̏̓̇͐̏́͐̈́͝͝Ë̶̛̠̫̫̠̼͔̱̩͎̳̠͉̬͈̣́͂͆͐̒̅̉̽́͒̒̎͑̓̿̚̚͠͝͠͝S̸̡̀͛ͅC̷̞̬̼͕̻̤͖̬̥͉͔̬̤̮̱̯͓͉̬͖̱̜̖̿̍͗͑͛̄̕̚Ą̴̳̜͚͖̺͖̞̈́̑͆̈́̏͗̌̄̆̎͘͝P̶̠͉̰͖̳̹͖̠͈͔̭̜͂̓̽͐̍ͅĔ̵̢̢̗͇͓̠͚̠͇̮͈̭͔̌́̀̇̉͊̈́̈̽͐̆̿͆͘̚͜͜͠͠͝')
        pygame.time.wait(1000)
        pygame.display.set_caption(f'{os.getlogin()}.exe')
        continue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            count += 1
            if count == 10:
                with open(os.path.join(downloads_path, "EXE.txt"), "w") as file:
                    file.write("YOUR FREE TRIAL OF LIVING HAS ENDED.")
                ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred.", "System Alert", 0x10)
                ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred.", "System Alert", 0x10)
                ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred.", "System Alert", 0x10)
                os.startfile(downloads_path)
                pygame.time.wait(3000)
                os.startfile(os.path.join(downloads_path, "EXE.txt"))
                ctypes.windll.user32.MessageBoxW(0, "An unexpected error occurred. Check Notepad.", "System Alert", 0x10)
                pygame.time.wait(5000)
                os.system(cmd)
                os.startfile(os.path.join(downloads_path, "EXE.txt"))
                with open(os.path.join(downloads_path, "EXE.txt"), "w") as file:
                    file.write("WHY ARE YOU HERE?")
                pygame.time.wait(3000)
                os.system(cmd)
                os.startfile(os.path.join(downloads_path, "EXE.txt"))
                with open(os.path.join(downloads_path, "EXE.txt"), "w") as file:
                    file.write("YOU ARE NOT SUPPOESED TO BE HERE.")
                pygame.time.wait(5000)
                with open(os.path.join(downloads_path, f"WELCOME_BACK_{os.getlogin().upper()}.txt"), "w") as file:
                    file.write(f"HEY {os.getlogin().upper()}")
                os.system(cmd2)
            pygame.display.set_caption('N̸̛̛̙̙̹͉̯͖̯̜̗̓̀͋̽͗̈́̉̂͑̎̆͋̈́̓̋̀͘͜Ǫ̶̨̧̖̦̞̖͇͍̤̪̱̤͎͕͉̹̹̤̱̬̗̰̐̀͌̓̓̿̾̉̄̈́̂̆͝ ̶̩̪̲͔̼̫̏̓̇͐̏́͐̈́͝͝Ë̶̛̠̫̫̠̼͔̱̩͎̳̠͉̬͈̣́͂͆͐̒̅̉̽́͒̒̎͑̓̿̚̚͠͝͠͝S̸̡̀͛ͅC̷̞̬̼͕̻̤͖̬̥͉͔̬̤̮̱̯͓͉̬͖̱̜̖̿̍͗͑͛̄̕̚Ą̴̳̜͚͖̺͖̞̈́̑͆̈́̏͗̌̄̆̎͘͝P̶̠͉̰͖̳̹͖̠͈͔̭̜͂̓̽͐̍ͅĔ̵̢̢̗͇͓̠͚̠͇̮͈̭͔̌́̀̇̉͊̈́̈̽͐̆̿͆͘̚͜͜͠͠͝')
            pygame.time.wait(250)
            pygame.display.set_caption(f'{os.getlogin()}.exe')
        manager.process_events(event)

    manager.update(time_delta)
    screen.fill((0, 0, 0))
    manager.draw_ui(screen)

    pygame.display.update()
