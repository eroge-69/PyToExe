import pygame as pg


pg.init()


WIDTH = 400
HEIGHT = 400
sc = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Krestiki-Noliki')

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (64,64,64)
clock = pg.time.Clock()
x = 4
rect_w = 125
rect_h = 125

button_1 = pg.draw.rect(sc, BLACK, (4, 5, rect_w, rect_h), False, 5)
button_2 = pg.draw.rect(sc, BLACK, (140, 5, rect_w, rect_h), False, 5)
button_3 = pg.draw.rect(sc, BLACK, (275, 5, rect_w, rect_h), False, 5)
button_4 = pg.draw.rect(sc, BLACK, (4, 140, rect_w, rect_h), False, 5)
button_5 = pg.draw.rect(sc, BLACK, (140, 140, rect_w, rect_h), False, 5)
button_6 = pg.draw.rect(sc, BLACK, (275, 140, rect_w, rect_h), False, 5)
button_7 = pg.draw.rect(sc, BLACK, (4, 275, rect_w, rect_h), False, 5)
button_8 = pg.draw.rect(sc, BLACK, (140, 275, rect_w, rect_h), False, 5)
button_9 = pg.draw.rect(sc, BLACK, (275, 275, rect_w, rect_h), False, 5)
pg.display.update()

def Zero(x1, y1):
    x_font = pg.font.SysFont(None, 150)
    x_render = x_font.render('0', True, WHITE)
    sc.blit(x_render, [x1, y1])
    pg.display.update()
def Iks(x2, y2):
    iks_font = pg.font.SysFont(None, 145)
    iks_render = iks_font.render('X', True, WHITE)
    sc.blit(iks_render, [x2, y2])
    pg.display.update()
def win(sign):
    win_font = pg.font.SysFont(None, 35)
    win_render = win_font.render(f'Победили: {sign}', True, WHITE)

    sc.blit(win_render, [90, 75])

def Game_Loop():
    sign = ''
    o = 1
    x = 2
    game_over = False
    game_close = False
    line_change = 135
    mat = [[0 for _ in range(3)] for _ in range(3)]

    while not game_over:
        while game_close == True:

            sc.fill(GRAY)
            win(sign)
            button_again = pg.draw.rect(sc, WHITE, (75, 220, 250, 75), False,5)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if button_again.collidepoint(event.pos):
                            sc.fill(BLACK)
                            Game_Loop()
        for _ in range(3):
            pg.draw.line(sc, WHITE, (line_change, 0), (line_change, 400), 1)
            pg.draw.line(sc, WHITE, (0, line_change), (400, line_change), 1)
            line_change += 135
            pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                game_over = True
                game_close = False
            if event.type == pg.MOUSEBUTTONDOWN:

                if event.button == 1:
                    if button_1.collidepoint(event.pos):
                        Zero(37, 27)
                        mat[0][0] = 1
                    elif button_2.collidepoint(event.pos):
                        Zero(172, 27)
                        mat[0][1] = 1
                    elif button_3.collidepoint(event.pos):
                        Zero(307, 27)
                        mat[0][2] = 1
                    elif button_4.collidepoint(event.pos):
                        Zero(37, 162)
                        mat[1][0] = 1
                    elif button_5.collidepoint(event.pos):
                        Zero(172, 162)
                        mat[1][1] = 1
                    elif button_6.collidepoint(event.pos):
                        Zero(307, 162)
                        mat[1][2] = 1
                    elif button_7.collidepoint(event.pos):
                        Zero(37, 297)
                        mat[2][0] = 1
                    elif button_8.collidepoint(event.pos):
                        Zero(172, 297)
                        mat[2][1] = 1
                    elif button_9.collidepoint(event.pos):
                        Zero(307, 297)
                        mat[2][2] = 1

                if event.button == 3:
                    if button_1.collidepoint(event.pos):
                        Iks(37, 27)
                        mat[0][0] = 2
                    elif button_2.collidepoint(event.pos):
                        Iks(172, 27)
                        mat[0][1] = 2
                    elif button_3.collidepoint(event.pos):
                        Iks(307, 27)
                        mat[0][2] = 2
                    elif button_4.collidepoint(event.pos):
                        Iks(37, 162)
                        mat[1][0] = 2
                    elif button_5.collidepoint(event.pos):
                        Iks(172, 162)
                        mat[1][1] = 2
                    elif button_6.collidepoint(event.pos):
                        Iks(307, 162)
                        mat[1][2] = 2
                    elif button_7.collidepoint(event.pos):
                        Iks(37, 297)
                        mat[2][0] = 2
                    elif button_8.collidepoint(event.pos):
                        Iks(172, 297)
                        mat[2][1] = 2
                    elif button_9.collidepoint(event.pos):
                        Iks(307, 297)
                        mat[2][2] = 2
        if mat[0] == [o, o, o]:
            game_close = True
            sign = 'Нолики'
        elif mat[1] == [o, o, o]:
            game_close = True
            sign = 'Нолики'

        elif mat[2] == [o, o, o]:
            game_over = True
            sign = 'Нолики'

        elif mat[0][0] == o and mat[1][1] == o and mat[2][2] == o:
            game_close = True
            sign = 'Нолики'

        elif mat[0][2] == o and mat[1][1] == o and mat[2][0] == o:
            game_close = True
            sign = 'Нолики'

        elif mat[1][0] == o and mat[1][1] == o and mat[1][2] == o:
            game_close = True
            sign = 'Нолики'

        elif mat[0][0] == o and mat[1][0] == o and mat[2][0] == o:
            game_close = True
            sign = 'Нолики'

        elif mat[0][1] == o and mat[1][1] == o and mat[2][1] == o:
            game_close = True
            sign = 'Нолики'

        elif mat[0][2] == o and mat[1][2] == o and mat[2][2] == o:
            game_close = True
            sign = 'Нолики'


        if mat[0] == [x, x, x]:
            game_close = True
            sign = 'Крестики'

        elif mat[1] == [x, x, x]:
            game_close = True
            sign = 'Крестики'

        elif mat[2] == [x, x, x]:
            game_close = True
            sign = 'Крестики'

        elif mat[0][0] == x and mat[1][1] == x and mat[2][2] == x:
            game_close = True
            sign = 'Крестики'

        elif mat[0][2] == x and mat[1][1] == x and mat[2][0] == x:
            game_close = True
            sign = 'Крестики'


        elif mat[1][0] == x and mat[1][1] == x and mat[1][2] == x:
            game_close = True
            sign = 'Крестики'

        elif mat[0][0] == x and mat[1][0] == x and mat[2][0] == x:
            game_close = True
            sign = 'Крестики'


        elif mat[0][1] == x and mat[1][1] == x and mat[2][1] == x:
            game_close = True
            sign = 'Крестики'

        elif mat[0][2] == x and mat[1][2] == x and mat[2][2] == x:
            game_close = True
            sign = 'Крестики'




    clock.tick(15)

Game_Loop()
